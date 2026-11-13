/* Exhaustive power-cut check of floor-advance / slot-replace over the journal.
   Flash model: write-once-to-0 (prog = AND), word-granular API, torn at every byte,
   arbitrary bit subsets of the interrupted byte, random bit subsets of interrupted word,
   torn erases. Usage: test_powerfail pf_vectors.txt [quick] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../c/sha256.h"
#include "../c/fs_journal.h"

#define PS 592u                      /* 4 records per page: forces frequent rollover */
enum { CUT_NONE, CUT_PROG_BYTE, CUT_PROG_WORD, CUT_ERASE };
typedef struct {
    uint8_t mem[2 * PS];
    unsigned opcount, cut_op; int kind; unsigned cut_pos; uint8_t mask; uint32_t wmask_seed;
    int dead; unsigned reprog; unsigned nprog, nerase;
    unsigned rec_n[64]; unsigned rec_kind[64];  /* recorded ops in dry run */
} sim;

static int s_read(void *c, uint32_t a, uint8_t *d, uint32_t n) { sim *s = c; if (s->dead || a + n > sizeof s->mem) return -1; memcpy(d, s->mem + a, n); return 0; }
static uint32_t rng(uint32_t *x) { *x ^= *x << 13; *x ^= *x >> 17; *x ^= *x << 5; return *x; }
static int s_prog(void *c, uint32_t a, const uint8_t *src, uint32_t n)
{
    sim *s = c; uint32_t i; unsigned op;
    if (s->dead) return -1;
    if ((a | n) & 3u || a + n > sizeof s->mem) return -2;
    op = s->opcount++; if (op < 64) { s->rec_n[op] = n; s->rec_kind[op] = 0; }
    s->nprog++;
    for (i = 0; i < n; i++) if (s->mem[a + i] != 0xff) { s->reprog++; break; }
    if (s->kind != CUT_NONE && op == s->cut_op && s->kind != CUT_ERASE) {
        if (s->kind == CUT_PROG_BYTE) {
            for (i = 0; i < s->cut_pos; i++) s->mem[a + i] &= src[i];
            { uint8_t d = (uint8_t)(s->mem[a + s->cut_pos] & ~src[s->cut_pos]);   /* bits to clear */
              s->mem[a + s->cut_pos] &= (uint8_t)~(d & s->mask); }                  /* any subset */
        } else {  /* word tear: words before complete, word cut_pos/4 gets random subset */
            uint32_t w = s->cut_pos & ~3u, seed = s->wmask_seed | 1u;
            for (i = 0; i < w; i++) s->mem[a + i] &= src[i];
            for (i = 0; i < 4; i++) { uint8_t d = (uint8_t)(s->mem[a + w + i] & ~src[w + i]);
                s->mem[a + w + i] &= (uint8_t)~(d & (uint8_t)rng(&seed)); }
        }
        s->dead = 1; return -1;
    }
    for (i = 0; i < n; i++) s->mem[a + i] &= src[i];
    return 0;
}
static int s_erase(void *c, uint32_t a)
{
    sim *s = c; unsigned op, i;
    if (s->dead) return -1;
    if (a != 0 && a != PS) return -2;
    op = s->opcount++; if (op < 64) { s->rec_n[op] = PS; s->rec_kind[op] = 1; }
    s->nerase++;
    if (s->kind == CUT_ERASE && op == s->cut_op) {
        for (i = 0; i < s->cut_pos; i++) s->mem[a + i] = 0xff;
        s->mem[a + s->cut_pos] |= s->mask;           /* cells raised to 1: any subset */
        s->dead = 1; return -1;
    }
    memset(s->mem + a, 0xff, PS); return 0;
}
static fs_flash mk(sim *s) { fs_flash f; f.ctx = s; f.page_size = PS; f.read = s_read; f.prog = s_prog; f.erase = s_erase; return f; }

static int hx(const char *s, uint8_t *o) { int n = 0; while (s[0] && s[1] && s[0] != '\n') { unsigned v; sscanf(s, "%2x", &v); o[n++] = (uint8_t)v; s += 2; } return n; }
static int eq(const fs_state *a, const fs_state *b)
{
    unsigned i; if (a->epoch != b->epoch || a->floor != b->floor) return 0;
    for (i = 0; i < 3; i++) if (a->state[i] != b->state[i] || a->cls[i] != b->cls[i] || a->last_q[i] != b->last_q[i] ||
        a->qseen[i] != b->qseen[i] || memcmp(a->hash[i], b->hash[i], 32)) return 0;
    return 1;
}

typedef struct { uint8_t cmd[FS_CMD_LEN]; uint8_t bun[8192]; size_t bl; } cmdv;
static cmdv CA[16], CB[16], CF[16];
typedef struct { uint32_t ver; uint8_t dg[32]; uint8_t bun[8192]; size_t bl; } imgv;
static imgv IM[2];
static uint8_t pubs[3][56]; static uint16_t cls[3];

static unsigned long ncuts, nfail, nfloor_dec, nbootfail, nreprog;
#define FAIL(...) do { nfail++; if (nfail < 10) { printf("  FAIL: " __VA_ARGS__); printf("\n"); } } while (0)

static int boot_pick(const fs_state *st, int *which)
{   /* highest-version candidate that verifies under st */
    int i;
    for (i = 1; i >= 0; i--) if (fs_image_check(st, IM[i].ver, IM[i].dg, IM[i].bun, IM[i].bl) == FS_OK) { *which = i; return 1; }
    return 0;
}

/* after a cut: reboot, validate, retry, follow-up */
static void post_cut(sim *s, const fs_state *oldst, const fs_state *newst, const cmdv *c, const cmdv *fol, const char *tag)
{
    sim t = *s; fs_flash fl; fs_journal j; fs_state st; fs_err e; int w;
    ncuts++;
    t.dead = 0; t.kind = CUT_NONE; t.opcount = 0; t.reprog = 0; fl = mk(&t);
    e = fs_journal_open(&j, &fl, 0, PS, &st);
    if (e != FS_OK) { FAIL("%s: boot: no valid record (%d)", tag, e); nbootfail++; return; }
    if (st.floor < oldst->floor) { nfloor_dec++; FAIL("%s: floor decreased %u -> %u", tag, oldst->floor, st.floor); }
    if (!eq(&st, oldst) && !eq(&st, newst)) { FAIL("%s: recovered state is neither old nor new (epoch %u)", tag, st.epoch); return; }
    { /* boot-image result depends only on the recovered state (old or new): memoised */
      static fs_state ms[2]; static int mr[2], mv[2];
      int k = eq(&st, oldst) ? 0 : 1;
      if (!mv[k] || !eq(&ms[k], &st)) { ms[k] = st; mr[k] = boot_pick(&st, &w); mv[k] = 1; }
      if (!mr[k]) { FAIL("%s: no bootable image", tag); nbootfail++; } }
    e = fs_apply_command(&j, &st, c->cmd, c->bun, c->bl);       /* retry the interrupted operation */
    if (e != FS_OK && e != FS_E_REPLAY) { FAIL("%s: retry gave %d", tag, e); return; }
    if (!eq(&st, newst)) { FAIL("%s: after retry state != new", tag); return; }
    e = fs_journal_open(&j, &fl, 0, PS, &st);                   /* durability of the retry */
    if (e != FS_OK || !eq(&st, newst)) { FAIL("%s: reopen after retry != new", tag); return; }
    e = fs_apply_command(&j, &st, fol->cmd, fol->bun, fol->bl); /* journal not wedged */
    if (e != FS_OK || st.floor != (newst->floor > 3 ? newst->floor : 3)) { FAIL("%s: follow-up failed (%d)", tag, e); return; }
    if (t.reprog) { nreprog++; FAIL("%s: reprogrammed non-blank flash", tag); }
}

static void scenario(const cmdv *tab, unsigned pre, const char *nm, int quick)
{
    sim base; fs_flash fl; fs_journal j; fs_state st, oldst, newst, g; unsigned i; fs_err e; unsigned nops, op;
    char tag[64];
    memset(&base, 0, sizeof base); memset(base.mem, 0xff, sizeof base.mem);
    fl = mk(&base);
    memset(&g, 0, sizeof g); g.epoch = 1; g.floor = 1;
    for (i = 0; i < 3; i++) { g.state[i] = SLOT_ACTIVE; g.cls[i] = cls[i]; sha256(pubs[i], 56, g.hash[i]); }
    if (fs_journal_format(&j, &fl, 0, PS, &g)) { puts("format failed"); exit(2); }
    st = g;
    for (i = 0; i < pre; i++) { fs_state n2 = st; n2.epoch++; if (fs_journal_commit(&j, &n2)) exit(2); st = n2; }
    oldst = st;
    { sim d = base; fs_flash f2 = mk(&d); fs_journal j2 = j; fs_state s2 = st; j2.fl = &f2;      /* dry run */
      d.opcount = 0; d.kind = CUT_NONE;
      e = fs_apply_command(&j2, &s2, tab[st.epoch].cmd, tab[st.epoch].bun, tab[st.epoch].bl);
      (void)f2; if (e != FS_OK) { printf("dry run failed %d (%s pre=%u)\n", e, nm, pre); exit(2); }
      newst = s2; nops = d.opcount; memcpy(base.rec_n, d.rec_n, sizeof d.rec_n); memcpy(base.rec_kind, d.rec_kind, sizeof d.rec_kind); }
    for (op = 0; op < nops; op++) {
        unsigned n = base.rec_n[op], pos;
        int is_erase = base.rec_kind[op];
        for (pos = 0; pos <= n && pos < (is_erase ? PS : n); pos++) {
            unsigned m, mmax = is_erase ? 16 : 255;
            for (m = 0; m <= mmax; m++) {
                sim s = base; fs_flash f = mk(&s); fs_journal jj; fs_state ss;
                uint8_t mask;
                if (is_erase) { static const uint8_t pat[16] = {0,0xff,1,2,4,8,16,32,64,128,0x55,0xaa,0x0f,0xf0,0x3c,0xc3}; mask = pat[m]; }
                else { /* iterate submasks lazily: m is 0..255 and used only if it is a submask of the cleared bits */
                    mask = (uint8_t)m;
                    if (quick && (m & (m - 1)) && m != 255) continue;
                }
                s.kind = is_erase ? CUT_ERASE : CUT_PROG_BYTE; s.cut_op = op; s.cut_pos = pos; s.mask = mask; s.opcount = 0;
                if (fs_journal_open(&jj, &f, 0, PS, &ss)) exit(2);
                e = fs_apply_command(&jj, &ss, tab[oldst.epoch].cmd, tab[oldst.epoch].bun, tab[oldst.epoch].bl);
                if (!s.dead) { if (m == 0 && pos == 0) {} continue; }
                snprintf(tag, sizeof tag, "%s pre=%u op=%u pos=%u mask=%02x", nm, pre, op, pos, mask);
                post_cut(&s, &oldst, &newst, &tab[oldst.epoch], &CF[newst.epoch], tag);
            }
        }
        if (!is_erase) {   /* random word tears */
            for (pos = 0; pos < n; pos += 4) { unsigned r;
                for (r = 0; r < (quick ? 4u : 32u); r++) {
                    sim s = base; fs_flash f = mk(&s); fs_journal jj; fs_state ss;
                    s.kind = CUT_PROG_WORD; s.cut_op = op; s.cut_pos = pos; s.wmask_seed = 0x9e3779b9u * (r + 1) + pos; s.opcount = 0;
                    if (fs_journal_open(&jj, &f, 0, PS, &ss)) exit(2);
                    fs_apply_command(&jj, &ss, tab[oldst.epoch].cmd, tab[oldst.epoch].bun, tab[oldst.epoch].bl);
                    snprintf(tag, sizeof tag, "%s pre=%u op=%u wordtear@%u r=%u", nm, pre, op, pos, r);
                    if (s.dead) post_cut(&s, &oldst, &newst, &tab[oldst.epoch], &CF[newst.epoch], tag);
                }
            }
        }
    }
    /* uncut run also counts: no cut => new state, no reprogram */
}

int main(int argc, char **argv)
{
    static char ln[1 << 17]; FILE *f; int quick = argc > 2; unsigned pre, ng = 0;
    if (argc < 2 || !(f = fopen(argv[1], "r"))) return 2;
    while (fgets(ln, sizeof ln, f)) {
        char *t[5]; unsigned k = 0; char *p = ln;
        while (k < 4 && (t[k] = strtok(k ? NULL : p, " \n"))) k++;
        if (!k) continue;
        if (t[0][0] == 'K') { hx(t[3], pubs[atoi(t[1])]); cls[atoi(t[1])] = (uint16_t)atoi(t[2]); }
        else if (t[0][0] == 'G') { imgv *m = &IM[ng++]; m->ver = (uint32_t)atoi(t[1]); hx(t[2], m->dg); m->bl = (size_t)hx(t[3], m->bun); }
        else { int e = atoi(t[1]); cmdv *c = t[0][0] == 'A' ? &CA[e] : t[0][0] == 'B' ? &CB[e] : &CF[e];
               hx(t[2], c->cmd); c->bl = (size_t)hx(t[3], c->bun); }
    }
    for (pre = 0; pre <= 9; pre++) {
        unsigned long c0 = ncuts;
        scenario(CA, pre, "ADVANCE_FLOOR(retire s0)", quick);
        printf("pre=%u ADVANCE: %lu cuts, cumulative fail=%lu\n", pre, ncuts - c0, nfail); fflush(stdout);
        c0 = ncuts;
        scenario(CB, pre, "REPLACE_SLOT(s2)", quick);
        printf("pre=%u REPLACE: %lu cuts, cumulative fail=%lu\n", pre, ncuts - c0, nfail); fflush(stdout);
    }
    printf("TOTAL cuts=%lu failures=%lu (floor decreases=%lu, no-valid-image/record=%lu, reprogram=%lu)\n",
           ncuts, nfail, nfloor_dec, nbootfail, nreprog);
    return nfail != 0;
}

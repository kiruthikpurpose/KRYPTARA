/* Harness for src/ac_step.c.
 *   step_test self   built-in checks (purity, fail-closed, busy rule, corruption, status codes)
 *   step_test run    reads scenario lines on stdin, prints one result line per input line.
 * `run` is driven by models/step_check.py (differential against models/step_model.py) and by
 * tests/vectors/waist-v1.txt (golden vectors any implementation of waist v1 must reproduce).
 * Scenario lines (all numbers hex):
 *   G present k0..k7 keymask h  then, for each of the 4 tiers: t s nfc nfl xca xcb xla xlb fc0..fc15 fl0..fl15
 *     then a0..a7 (action tiers) and tbl0..tbl3. Class masks and exclusions are 0xff when unused.
 *   D ...                               as G, then 8 key fill bytes (slot i's hash = 32 copies; G uses 0x10+i)
 *   H S atom bundle                     HALT message
 *   P action S atom bundle tier D T     PROPOSE_TX; D = 32-byte digest hex or -, T = 32-byte table hex or -
 *   B D                                 BOOT message
 *   A seq                               acknowledge a snapshot
 * Tables are 64 hex digits, most significant word first. */
#include <stdio.h>
#include <string.h>
#include "../src/ac_step.c"
#include "../src/prototypes/c/sha256.c"

static int unhex(const char *s, uint8_t *o, size_t n) {
    if (s[0] == '-' && s[1] == 0) { memset(o, 0, n); return 0; }
    for (size_t i = 0; i < n; i++) { unsigned v; if (sscanf(s + 2 * i, "%2x", &v) != 1) return -1; o[i] = (uint8_t)v; }
    return 0;
}
static int read_table(ac_tbl_t *t) {
    char s[80]; if (scanf("%79s", s) != 1 || strlen(s) != 64) return -1;
    for (int w = 7; w >= 0; w--) { unsigned x; if (sscanf(s + 8 * (7 - w), "%8x", &x) != 1) return -1; t->w[w] = x; }
    return 0;
}
static void hex32(const uint8_t *b) { for (int i = 0; i < 32; i++) printf("%02x", b[i]); }

static void print_state(char tag, ac_status_t st, const ac_effects_t *fx, const ac_ctx_t *c) {
    uint8_t d[32];
    printf("%c st=%d n=%u", tag, (int)st, fx ? fx->n : 0u);
    for (unsigned i = 0; i < AC_MAX_INTENTS; i++)
        if (fx && i < fx->n) printf(" i%u=%u:%u:%d", i, fx->it[i].kind, (unsigned)fx->it[i].seq, (int)fx->it[i].code);
    printf(" seq=%u acked=%u dig=", (unsigned)c->seq, (unsigned)c->acked);
    if (ac_ctx_digest(c, d) == AC_OK) hex32(d); else printf("-");
    printf(" head="); hex32(c->head); printf("\n");
}

static int run(void) {
    ac_ctx_t c; memset(&c, 0, sizeof c);
    char tag[4];
    while (scanf("%3s", tag) == 1) {
        ac_effects_t fx; size_t need; ac_msg_t m; memset(&m, 0, sizeof m); ac_status_t st;
        if (tag[0] == 'G' || tag[0] == 'D') {
            ac_genesis_t g; memset(&g, 0, sizeof g); unsigned x;
            #define RD(f) do { if (scanf("%x", &x) != 1) return 2; (f) = (uint8_t)x; } while (0)
            RD(g.present); for (int i = 0; i < 8; i++) RD(g.kinds[i]); RD(g.key_present); RD(g.halt_budget);
            for (int t = 0; t < AC_TIER_N; t++) {
                ac_budget_t *b = &g.bud[t];
                RD(b->t); RD(b->s); RD(b->nfc); RD(b->nfl); RD(b->xc_a); RD(b->xc_b); RD(b->xl_a); RD(b->xl_b);
                for (unsigned i = 0; i < AC_MAX_CLASSES; i++) RD(b->fc[i]);
                for (unsigned i = 0; i < AC_MAX_CLASSES; i++) RD(b->fl[i]);
            }
            for (int i = 0; i < AC_ACT_N; i++) RD(g.action_tier[i]);
            for (int t = 0; t < AC_TIER_N; t++) if (read_table(&g.table[t])) return 2;
            for (int i = 0; i < 8; i++) memset(g.key[i].h, 0x10 + i, 32);
            if (tag[0] == 'D') for (int i = 0; i < 8; i++) { RD(x); memset(g.key[i].h, (int)x, 32); }
            st = ac_genesis(&c, &g);
            print_state('G', st, 0, &c);
            continue;
        }
        if (tag[0] == 'A') { unsigned s; if (scanf("%x", &s) != 1) return 2; st = ac_ack(&c, s); print_state('A', st, 0, &c); continue; }
        char dh[80], th[80];
        if (tag[0] == 'H') {
            unsigned S, a, b; if (scanf("%x %x %x", &S, &a, &b) != 3) return 2;
            m.kind = AC_MSG_HALT; m.evidence = (uint8_t)S; m.atom = (uint8_t)a; m.bundle = (uint8_t)b;
        } else if (tag[0] == 'P') {
            unsigned act, S, a, b, t; if (scanf("%x %x %x %x %x %79s %79s", &act, &S, &a, &b, &t, dh, th) != 7) return 2;
            m.kind = AC_MSG_PROPOSE_TX; m.action = (uint8_t)act; m.evidence = (uint8_t)S; m.atom = (uint8_t)a;
            m.bundle = (uint8_t)b; m.tier = (uint8_t)t;
            if (unhex(dh, m.digest, 32)) return 2;
            if (th[0] != '-') {
                uint8_t tb8[32]; if (unhex(th, tb8, 32)) return 2;
                for (int w = 0; w < 8; w++) m.table.w[w] = (uint32_t)tb8[4*(7-w)] << 24 | (uint32_t)tb8[4*(7-w)+1] << 16 | (uint32_t)tb8[4*(7-w)+2] << 8 | tb8[4*(7-w)+3];
            }
        } else if (tag[0] == 'B') {
            if (scanf("%79s", dh) != 1 || unhex(dh, m.digest, 32)) return 2;
            m.kind = AC_MSG_BOOT;
        } else return 2;
        st = ac_step(&c, &m, &fx, &need);
        print_state(tag[0], st, &fx, &c);
    }
    return 0;
}

/* The reference terrestrial layout (atoms 0..5 = OEM1 OEM2 OWN1 OWN2 ESC1 ESC2, 6 = PRES, 7 = WIT)
 * with the same tiers, fault classes and budgets as models/lint.py. `fortress` puts re-keying in
 * the 2-safe CONST tier, otherwise in the recoverable RECOVERY tier (REQ-TIER-02). */
static unsigned grp(unsigned S) { return !!(S & 3) + !!(S & 12) + !!(S & 48); }
static unsigned fam(unsigned S) { return !!(S & 0x15) + !!(S & 0x2A); }
static void ref_genesis(ac_genesis_t *g, int fortress) {
    static const uint8_t base[12] = { 1, 2, 4, 8, 16, 32, 64, 3, 12, 48, 0x15, 0x2A };
    static const uint8_t loss_const[9] = { 1, 2, 4, 8, 16, 32, 3, 12, 48 };
    static const uint8_t loss_rec[11] = { 1, 2, 4, 8, 16, 32, 3, 12, 48, 0x15, 0x2A };
    memset(g, 0, sizeof *g);
    g->present = 0xff; g->key_present = 0x3f; g->halt_budget = 2;
    for (int i = 0; i < 6; i++) g->kinds[i] = 1;
    g->kinds[6] = 2; g->kinds[7] = 3;
    for (int t = 0; t < AC_TIER_N; t++) {
        ac_budget_t *b = &g->bud[t];
        b->xc_a = b->xc_b = b->xl_a = b->xl_b = 0xff;
        b->nfc = 12; memcpy(b->fc, base, 12); b->t = 1;
        b->nfl = 12; memcpy(b->fl, base, 12); b->s = 1;
    }
    g->bud[AC_T2_CONST].t = 2; g->bud[AC_T2_CONST].nfl = 9; memcpy(g->bud[AC_T2_CONST].fl, loss_const, 9);
    g->bud[AC_T2_RECOVERY].s = 2; g->bud[AC_T2_RECOVERY].nfl = 11; memcpy(g->bud[AC_T2_RECOVERY].fl, loss_rec, 11);
    g->bud[AC_T2_RECOVERY].xl_a = 9; g->bud[AC_T2_RECOVERY].xl_b = 10;
    uint8_t at[AC_ACT_N] = { 0, 1, 1, 1, 1, 1, 3, 3 };
    if (fortress) at[AC_ACT_INSTALL_TABLE] = at[AC_ACT_KEY_INSTALL] = 2;
    memcpy(g->action_tier, at, AC_ACT_N);
    for (int i = 0; i < 8; i++) memset(g->key[i].h, 0x10 + i, 32);
    for (unsigned S = 0; S < 256; S++) {
        unsigned K = (unsigned)__builtin_popcount(S & 0x3f), C = grp(S), F = fam(S), p = !!(S & 0x40), w = !!(S & 0x80);
        if (K >= 1) ts(&g->table[AC_T0_HALT], S);
        if ((w && C >= 2 && (F >= 2 || p)) || (p && C >= 2 && F >= 2)) ts(&g->table[AC_T1_OPERATE], S);
        if (p && F >= 2 && ((C >= 2 && w) || C >= 3)) ts(&g->table[AC_T2_CONST], S);
        if (p && K >= 2 && (w || C >= 2)) ts(&g->table[AC_T2_RECOVERY], S);
    }
}

static int self(void) {
    int bad = 0;
    ac_genesis_t g; ac_ctx_t c; ac_effects_t fx; size_t need; ac_msg_t m;
    ref_genesis(&g, 1); bad += ac_genesis(&c, &g) != AC_OK;               /* A: both reference profiles are admitted */
    ref_genesis(&g, 0); bad += ac_genesis(&c, &g) != AC_OK;

    /* B: before genesis every step is refused with AC_E_STATE */
    ac_ctx_t z; memset(&z, 0, sizeof z); memset(&m, 0, sizeof m); m.kind = AC_MSG_BOOT;
    bad += ac_step(&z, &m, &fx, &need) != AC_E_STATE;

    /* C: a rejected message changes nothing, byte for byte */
    ac_ctx_t before; memcpy(&before, &c, sizeof c); memset(&m, 0, sizeof m);
    m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_ADVANCE_EPOCH; m.evidence = 0x01;   /* too little evidence */
    bad += ac_step(&c, &m, &fx, &need) != AC_E_AUTH || memcmp(&before, &c, sizeof c) != 0 || fx.n != 1 || fx.it[0].kind != AC_INT_REJECT;

    /* D: an accepted message advances the chain and issues one snapshot; the next is BUSY until acked */
    m.evidence = 0x89;                                                    /* atoms 0 and 3 (two groups, two families) and the log */
    uint8_t h0[32]; memcpy(h0, c.head, 32);
    bad += ac_step(&c, &m, &fx, &need) != AC_OK || fx.n != 1 || fx.it[0].kind != AC_INT_NV_WRITE_SNAPSHOT || fx.it[0].seq != 1;
    bad += memcmp(h0, c.head, 32) == 0 || c.epoch != 1;
    memcpy(&before, &c, sizeof c);
    bad += ac_step(&c, &m, &fx, &need) != AC_E_BUSY || memcmp(&before, &c, sizeof c) != 0;
    bad += ac_ack(&c, 2) != AC_E_BADMSG || ac_ack(&c, 1) != AC_OK || ac_ack(&c, 1) != AC_E_BADMSG;
    bad += ac_step(&c, &m, &fx, &need) != AC_OK;                         /* E: not busy after the ack */
    ac_ack(&c, 2);

    /* F: image commit. BOOT refuses until a digest is committed, then only that digest. */
    memset(&m, 0, sizeof m); m.kind = AC_MSG_BOOT; memset(m.digest, 0x77, 32);
    bad += ac_step(&c, &m, &fx, &need) != AC_E_IMAGE;
    m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_ACTIVATE_IMAGE; m.evidence = 0x89; m.bundle = 3;
    bad += ac_step(&c, &m, &fx, &need) != AC_OK; ac_ack(&c, c.seq);
    m.kind = AC_MSG_BOOT; bad += ac_step(&c, &m, &fx, &need) != AC_OK || fx.it[0].kind != AC_INT_BOOT_IMAGE;
    m.digest[5] ^= 1; bad += ac_step(&c, &m, &fx, &need) != AC_E_IMAGE;

    /* G: halt, halted bundles cannot be activated, resume, and the per-epoch halt budget */
    memset(&m, 0, sizeof m); m.kind = AC_MSG_HALT; m.evidence = 0x01; m.atom = 0; m.bundle = 3;
    bad += ac_step(&c, &m, &fx, &need) != AC_OK; ac_ack(&c, c.seq);
    memset(&m, 0, sizeof m); m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_ACTIVATE_IMAGE; m.evidence = 0x89; m.bundle = 3;
    bad += ac_step(&c, &m, &fx, &need) != AC_E_HALTED;
    m.action = AC_ACT_RESUME; bad += ac_step(&c, &m, &fx, &need) != AC_OK; ac_ack(&c, c.seq);
    memset(&m, 0, sizeof m); m.kind = AC_MSG_HALT; m.evidence = 0x01; m.atom = 0; m.bundle = 4;
    bad += ac_step(&c, &m, &fx, &need) != AC_OK; ac_ack(&c, c.seq);       /* second halt by atom 0 this epoch */
    m.bundle = 5; bad += ac_step(&c, &m, &fx, &need) != AC_E_BUDGET;      /* third: budget h = 2 used */

    /* H: key install into an ACTIVE slot needs the holder's own atom; an empty slot does not (ADR-040).
     * The recoverable profile authorises KEY_INSTALL at T3: presence plus at least two keys. */
    memset(&m, 0, sizeof m); m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_KEY_INSTALL; m.atom = 1;
    m.evidence = 0x45;                                                    /* atoms 0 and 2, presence */
    memset(m.digest, 0xAA, 32);
    bad += ac_step(&c, &m, &fx, &need) != AC_E_HOLDER;                   /* slot 1 is active and atom 1 did not sign */
    m.evidence = 0x47; bad += ac_step(&c, &m, &fx, &need) != AC_OK; ac_ack(&c, c.seq);
    memset(m.digest, 0x12, 32);
    bad += ac_step(&c, &m, &fx, &need) != AC_E_DUPKEY;                   /* the hash installed in slot 2 */
    memset(&m, 0, sizeof m); m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_RETIRE_SLOT; m.atom = 5; m.evidence = 0x89;
    bad += ac_step(&c, &m, &fx, &need) != AC_OK; ac_ack(&c, c.seq);       /* retire slot 5 at T1 */
    memset(&m, 0, sizeof m); m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_KEY_INSTALL; m.atom = 5; m.evidence = 0x45;
    memset(m.digest, 0xBB, 32);
    bad += ac_step(&c, &m, &fx, &need) != AC_OK;                         /* the empty slot has no holder to co-sign */
    ac_ack(&c, c.seq);

    /* I: a widening proposal is rejected as a tightening, accepted as an install only if admissible */
    memset(&m, 0, sizeof m); m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_TIGHTEN_TABLE; m.tier = 1; m.evidence = 0x89;
    for (int i = 0; i < 8; i++) m.table.w[i] = 0xffffffffu;               /* authorise everything: widening, and not safe */
    bad += ac_step(&c, &m, &fx, &need) != AC_E_ADMIT;
    m.action = AC_ACT_INSTALL_TABLE; m.evidence = 0x4f;
    bad += ac_step(&c, &m, &fx, &need) != AC_E_ADMIT;

    /* J: corruption. A flipped bit in a stored table copy is detected by the digest and by authorise */
    ac_ctx_t bad_c = c; bad_c.eng.tier[1].c.w[0] ^= 1u;
    uint8_t dg[32]; bad += ac_ctx_digest(&bad_c, dg) != AC_E_STATE;

    /* L: fail closed on a corrupted budget in memory. Genesis validates t, s and the class counts, so
     * these cannot arise through ac_genesis; the admission must still refuse them rather than guess. */
    ref_genesis(&g, 0); ac_ctx_t cl; bad += ac_genesis(&cl, &g) != AC_OK;
    memset(&m, 0, sizeof m); m.kind = AC_MSG_PROPOSE_TX; m.action = AC_ACT_INSTALL_TABLE; m.tier = 1; m.evidence = 0x47;
    m.table = cl.eng.tier[1].t;                                           /* re-installing the current table is admissible */
    ac_ctx_t cm = cl; bad += ac_step(&cm, &m, &fx, &need) != AC_OK;
    cm = cl; cm.bud[1].t = 3; bad += ac_step(&cm, &m, &fx, &need) != AC_E_ADMIT;
    cm = cl; cm.bud[1].nfc = 33; bad += ac_step(&cm, &m, &fx, &need) != AC_E_ADMIT;
    cm = cl; cm.bud[1].s = 3; bad += ac_step(&cm, &m, &fx, &need) != AC_E_ADMIT;
    cm = cl; cm.bud[1].nfl = 33; bad += ac_step(&cm, &m, &fx, &need) != AC_E_ADMIT;

    /* K: status codes are negative and distinct */
    const int codes[] = { AC_E_BADMSG, AC_E_AUTH, AC_E_ADMIT, AC_E_HOLDER, AC_E_DUPKEY, AC_E_HALTED, AC_E_BUDGET,
                          AC_E_BUSY, AC_E_NOCLASS, AC_E_STATE, AC_E_IMAGE };
    for (unsigned i = 0; i < sizeof codes / sizeof *codes; i++) {
        bad += codes[i] >= 0;
        for (unsigned j = i + 1; j < sizeof codes / sizeof *codes; j++) bad += codes[i] == codes[j];
    }
    printf("step self failures=%d\n", bad);
    return bad;
}

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "self")) return self();
    if (!strcmp(argv[1], "run")) return run();
    return 2;
}

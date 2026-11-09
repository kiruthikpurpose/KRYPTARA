#include "fs_journal.h"
#include "sha256.h"
#include <string.h>

static void w32(uint8_t *p, uint32_t v) { p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8); p[2]=(uint8_t)(v>>16); p[3]=(uint8_t)(v>>24); }
static uint32_t r32(const uint8_t *p) { return p[0] | ((uint32_t)p[1]<<8) | ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24); }

static void ser(const fs_state *s, uint8_t r[FS_REC_LEN])
{
    unsigned i; uint8_t d[32];
    memset(r, 0, FS_REC_LEN);
    w32(r, s->epoch); w32(r + 4, s->floor);
    for (i = 0; i < FS_NSLOTS; i++) {
        r[8 + i] = s->state[i]; r[11 + i] = s->qseen[i];
        r[16 + 2*i] = (uint8_t)s->cls[i]; r[17 + 2*i] = (uint8_t)(s->cls[i] >> 8);
        w32(r + 24 + 4*i, s->last_q[i]);
        memcpy(r + 36 + 32*i, s->hash[i], 32);
    }
    sha256(r, FS_REC_PAYLOAD, d);
    memcpy(r + FS_REC_PAYLOAD, d, FS_REC_DIGEST);
}

/* 1 = valid record parsed into *s; 0 = not valid */
static int deser(const uint8_t r[FS_REC_LEN], fs_state *s)
{
    uint8_t d[32]; unsigned i;
    sha256(r, FS_REC_PAYLOAD, d);
    if (memcmp(d, r + FS_REC_PAYLOAD, FS_REC_DIGEST) != 0) return 0;
    s->epoch = r32(r);
    if (s->epoch == 0xffffffffu) return 0;
    s->floor = r32(r + 4);
    for (i = 0; i < FS_NSLOTS; i++) {
        s->state[i] = r[8 + i]; s->qseen[i] = r[11 + i];
        if (s->state[i] > SLOT_RETIRED || s->qseen[i] > 1) return 0;
        s->cls[i] = (uint16_t)(r[16 + 2*i] | (r[17 + 2*i] << 8));
        s->last_q[i] = r32(r + 24 + 4*i);
        memcpy(s->hash[i], r + 36 + 32*i, 32);
    }
    return 1;
}

static int is_blank(const uint8_t *r)
{
    unsigned i; uint8_t a = 0xff;
    for (i = 0; i < FS_REC_LEN; i++) a &= r[i];
    return a == 0xff;       /* all bytes 0xFF  <=>  AND of all bytes is 0xFF */
}

fs_err fs_journal_format(fs_journal *j, const fs_flash *fl, uint32_t b0, uint32_t b1, const fs_state *g)
{
    uint8_t rec[FS_REC_LEN];
    if (fl->erase(fl->ctx, b0) || fl->erase(fl->ctx, b1)) return FS_E_FLASH;
    ser(g, rec);
    if (fl->prog(fl->ctx, b0, rec, FS_REC_LEN)) return FS_E_FLASH;
    j->fl = fl; j->base[0] = b0; j->base[1] = b1;
    j->nslots = (uint16_t)(fl->page_size / FS_REC_LEN);
    j->cur = 0; j->next = 1; j->last_epoch = g->epoch;
    return FS_OK;
}

fs_err fs_journal_open(fs_journal *j, const fs_flash *fl, uint32_t b0, uint32_t b1, fs_state *out)
{
#ifdef FS_BUG_NO_DIGEST_CHECK
    (void)0;
#endif
    uint8_t rec[FS_REC_LEN]; fs_state s; int found = 0; unsigned p, k;
    uint16_t lastnb[2] = {0, 0};       /* 1 + index of last non-blank record, per page */
    j->fl = fl; j->base[0] = b0; j->base[1] = b1;
    j->nslots = (uint16_t)(fl->page_size / FS_REC_LEN);
    for (p = 0; p < 2; p++) {
        for (k = 0; k < j->nslots; k++) {
            if (fl->read(fl->ctx, j->base[p] + k * FS_REC_LEN, rec, FS_REC_LEN)) return FS_E_FLASH;
            if (is_blank(rec)) continue;
            lastnb[p] = (uint16_t)(k + 1);
#ifdef FS_BUG_NO_DIGEST_CHECK
            { /* mutant: trust any non-blank record whose epoch field looks plausible */
              fs_state t; unsigned i; t.epoch = r32(rec);
              if (t.epoch == 0xffffffffu) continue;
              t.floor = r32(rec + 4);
              for (i = 0; i < FS_NSLOTS; i++) { t.state[i] = rec[8+i]; t.qseen[i] = rec[11+i];
                  t.cls[i] = (uint16_t)(rec[16+2*i] | (rec[17+2*i] << 8)); t.last_q[i] = r32(rec+24+4*i);
                  memcpy(t.hash[i], rec + 36 + 32*i, 32); }
              if (!found || t.epoch > j->last_epoch) { s = t; found = 1; j->last_epoch = t.epoch; j->cur = (uint8_t)p; }
              continue; }
#else
            if (!deser(rec, &s)) continue;     /* torn or garbage: skip but count as used */
            if (!found || s.epoch > j->last_epoch) { *out = s; found = 1; j->last_epoch = s.epoch; j->cur = (uint8_t)p; }
#endif
        }
    }
#ifdef FS_BUG_NO_DIGEST_CHECK
    if (found) *out = s;
#endif
    if (!found) return FS_E_PARSE;
    j->next = lastnb[j->cur];
    return FS_OK;
}

fs_err fs_journal_commit(fs_journal *j, const fs_state *next)
{
    uint8_t rec[FS_REC_LEN]; uint8_t dst; uint16_t slot; uint32_t addr;
    if (next->epoch <= j->last_epoch || next->epoch == 0xffffffffu) return FS_E_REPLAY;
    ser(next, rec);
    if (j->next < j->nslots) { dst = j->cur; slot = j->next; }
    else {
#ifdef FS_BUG_ERASE_CURRENT_FIRST
        dst = j->cur;                               /* mutant: no ping-pong */
#else
        dst = (uint8_t)(j->cur ^ 1u);               /* erase the page that is NOT current */
#endif
        if (j->fl->erase(j->fl->ctx, j->base[dst])) return FS_E_FLASH;
        slot = 0;
    }
    addr = j->base[dst] + (uint32_t)slot * FS_REC_LEN;
    if (j->fl->prog(j->fl->ctx, addr, rec, FS_REC_LEN)) return FS_E_FLASH;
    j->cur = dst; j->next = (uint16_t)(slot + 1); j->last_epoch = next->epoch;
    return FS_OK;
}

fs_err fs_apply_command(fs_journal *j, fs_state *st, const uint8_t msg[FS_CMD_LEN],
                        const uint8_t *bundle, size_t bundle_len)
{
    fs_state nx; fs_err e = fs_command_eval(st, msg, bundle, bundle_len, &nx);
    if (e != FS_OK) return e;
    e = fs_journal_commit(j, &nx);
    if (e != FS_OK) return e;
    *st = nx;
    return FS_OK;
}

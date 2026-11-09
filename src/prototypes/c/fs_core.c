#include "fs_core.h"
#include "sha256.h"
#include <string.h>

static uint32_t rb32(const uint8_t *p) { return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3]; }
static void wb32(uint8_t *p, uint32_t v) { p[0]=(uint8_t)(v>>24); p[1]=(uint8_t)(v>>16); p[2]=(uint8_t)(v>>8); p[3]=(uint8_t)v; }

fs_err fs_parse_bundle(const uint8_t *buf, size_t len, fs_sigref out[FS_MAX_SIGS], unsigned *n)
{
    size_t off = 1; unsigned cnt, i; size_t sl;
    if (buf == NULL || len < 1) return FS_E_PARSE;
    cnt = buf[0];
    if (cnt == 0 || cnt > FS_MAX_SIGS) return FS_E_PARSE;
    for (i = 0; i < cnt; i++) {
        if (len - off < 1u + LMS_PUB_LEN + 2u) return FS_E_PARSE;   /* no overflow: off <= len */
        out[i].slot = buf[off];
        out[i].pub  = buf + off + 1;
        sl = ((size_t)buf[off + 1 + LMS_PUB_LEN] << 8) | buf[off + 2 + LMS_PUB_LEN];
        off += 1u + LMS_PUB_LEN + 2u;
        if (len - off < sl) return FS_E_PARSE;
        out[i].sig = buf + off; out[i].siglen = (uint16_t)sl;
        off += sl;
    }
    if (off != len) return FS_E_PARSE;                              /* trailing bytes */
    *n = cnt;
    return FS_OK;
}

fs_err fs_authorize(const fs_state *st, const uint8_t *msg, size_t msglen,
                    const fs_sigref *sr, unsigned n, uint8_t *mask, uint32_t qs[FS_MAX_SIGS])
{
    uint16_t sets[FS_MAX_SIGS] = {0, 0, 0}; uint8_t m = 0, h[32]; unsigned i;
    if (n == 0 || n > FS_MAX_SIGS) return FS_E_PARSE;
    /* cheap checks first: slot validity, key-hash binding, quorum shape */
    for (i = 0; i < n; i++) {
        uint8_t s = sr[i].slot;
        if (s >= FS_NSLOTS || st->state[s] != SLOT_ACTIVE || (m & (1u << s))) return FS_E_SLOT;
        sha256(sr[i].pub, LMS_PUB_LEN, h);
        if (memcmp(h, st->hash[s], 32) != 0) return FS_E_KEYHASH;
        m = (uint8_t)(m | (1u << s));
        sets[i] = st->cls[s];
    }
    if (!fs_quorum_valid(sets, n)) return FS_E_QUORUM;
    for (i = 0; i < n; i++) {
        uint32_t q = 0;
        if (lms_verify(sr[i].pub, msg, msglen, sr[i].sig, sr[i].siglen, &q) != LMS_OK) return FS_E_SIG;
        if (qs) qs[i] = q;
    }
    *mask = m;
    return FS_OK;
}

void fs_build_cmd(uint8_t o[FS_CMD_LEN], uint8_t op, uint8_t slot, uint32_t epoch,
                  uint32_t new_floor, const uint8_t new_hash[32], uint16_t new_class)
{
    memset(o, 0, FS_CMD_LEN);
    memcpy(o, "FSC1", 4); o[4] = op; o[5] = slot;
    wb32(o + 8, epoch); wb32(o + 12, new_floor);
    if (new_hash) memcpy(o + 16, new_hash, 32);
    o[48] = (uint8_t)(new_class >> 8); o[49] = (uint8_t)new_class;
}

fs_err fs_command_eval(const fs_state *st, const uint8_t m[FS_CMD_LEN],
                       const uint8_t *bundle, size_t blen, fs_state *nx)
{
    fs_sigref sr[FS_MAX_SIGS]; unsigned n, i; uint8_t mask = 0; uint32_t qs[FS_MAX_SIGS];
    fs_err e; uint8_t op, tgt; uint32_t nf; uint16_t ncls;
    static const uint8_t zero32[32] = {0};

    if (memcmp(m, "FSC1", 4) != 0) return FS_E_PARSE;
    op = m[4]; tgt = m[5];
    if (m[6] || m[7] || m[50] || m[51]) return FS_E_PARSE;
    nf = rb32(m + 12); ncls = (uint16_t)((m[48] << 8) | m[49]);
    if (op == OP_ADVANCE_FLOOR) {
        if (memcmp(m + 16, zero32, 32) != 0 || ncls != 0) return FS_E_PARSE;
        if (tgt != NO_SLOT && tgt >= FS_NSLOTS) return FS_E_POLICY;
    } else if (op == OP_REPLACE_SLOT) {
        if (tgt >= FS_NSLOTS || ncls == 0 || nf != 0) return FS_E_POLICY;
    } else return FS_E_PARSE;

    if (rb32(m + 8) != st->epoch) return FS_E_REPLAY;
    e = fs_parse_bundle(bundle, blen, sr, &n);
    if (e != FS_OK) return e;
    if (n < FS_QUORUM_MIN) return FS_E_QUORUM;
    /* the signer must not be the slot being retired / replaced */
    for (i = 0; i < n; i++) if (sr[i].slot == tgt) return FS_E_POLICY;
    e = fs_authorize(st, m, FS_CMD_LEN, sr, n, &mask, qs);
    if (e != FS_OK) return e;
    /* OTS-reuse damper: leaf index must be strictly above the slot's high-water */
    for (i = 0; i < n; i++)
        if (st->qseen[sr[i].slot] && qs[i] <= st->last_q[sr[i].slot]) return FS_E_REPLAY;

    *nx = *st;
    if (op == OP_ADVANCE_FLOOR) {
        if (nf < st->floor) return FS_E_FLOOR;
        if (tgt != NO_SLOT) {
            if (st->state[tgt] != SLOT_ACTIVE) return FS_E_POLICY;
#if FS_REQUIRE_FOREIGN_CLASS
            { int foreign = 0;
              for (i = 0; i < n; i++) if ((st->cls[sr[i].slot] & st->cls[tgt]) == 0) foreign = 1;
              if (!foreign) return FS_E_POLICY; }
#endif
            nx->state[tgt] = SLOT_RETIRED;
            /* signer != tgt and signer is ACTIVE, so >= 1 ACTIVE slot always survives */
        }
        nx->floor = nf;
    } else {
        memcpy(nx->hash[tgt], m + 16, 32); nx->cls[tgt] = ncls;
        nx->state[tgt] = SLOT_ACTIVE; nx->qseen[tgt] = 0; nx->last_q[tgt] = 0;
    }
    for (i = 0; i < n; i++) { nx->qseen[sr[i].slot] = 1; nx->last_q[sr[i].slot] = qs[i]; }
    nx->epoch = st->epoch + 1;
    return FS_OK;
}

fs_err fs_image_check(const fs_state *st, uint32_t version, const uint8_t digest[32],
                      const uint8_t *bundle, size_t blen)
{
    fs_sigref sr[FS_MAX_SIGS]; unsigned n; uint8_t mask, msg[40]; fs_err e;
    if (version < st->floor) return FS_E_FLOOR;
    e = fs_parse_bundle(bundle, blen, sr, &n);
    if (e != FS_OK) return e;
    if (n != 1) return FS_E_PARSE;
    memcpy(msg, "IMG1", 4); wb32(msg + 4, version); memcpy(msg + 8, digest, 32);
    return fs_authorize(st, msg, sizeof msg, sr, n, &mask, NULL);
}

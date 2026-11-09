#include "lms.h"
#include "sha256.h"
#include <string.h>

#define D_PBLC 0x8080u
#define D_MESG 0x8181u
#define D_LEAF 0x8282u
#define D_INTR 0x8383u

static uint32_t rd32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3];
}
static void wr32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v >> 24); p[1] = (uint8_t)(v >> 16); p[2] = (uint8_t)(v >> 8); p[3] = (uint8_t)v;
}

typedef struct { uint8_t h, w, p, ls; } lms_params;

/* returns 0 if unsupported */
static int params(const uint8_t pub[LMS_PUB_LEN], lms_params *pr)
{
    uint32_t lt = rd32(pub), ot = rd32(pub + 4);
    switch (lt) { case 5: pr->h = 5; break; case 6: pr->h = 10; break; default: return 0; }
    switch (ot) { case 3: pr->w = 4; pr->p = 67; pr->ls = 4; break;
                  case 4: pr->w = 8; pr->p = 34; pr->ls = 0; break; default: return 0; }
    return 1;
}

long lms_sig_len_for_pub(const uint8_t pub[LMS_PUB_LEN])
{
    lms_params pr;
    if (!params(pub, &pr)) return -1;
    return 4 + 4 + 32 + 32 * (long)pr.p + 4 + 32 * (long)pr.h;
}

/* coef(S,i,w) with the checksum appended: S is Q(32) || cksm(2) */
static unsigned coef(const uint8_t *S, unsigned i, unsigned w)
{
    if (w == 8) return S[i];
    return (i & 1) ? (S[i >> 1] & 0x0f) : (S[i >> 1] >> 4);
}

static uint16_t checksum(const uint8_t Q[32], unsigned w, unsigned ls)
{
    unsigned i, n = 256u / w, s = 0;
    for (i = 0; i < n; i++) s += ((1u << w) - 1u) - coef(Q, i, w);
    return (uint16_t)((s << ls) & 0xffffu);
}

#ifdef LMS_NO_FASTPATH
/* generic chain step: H(I || q || i || j || tmp) */
static void chain_step(const uint8_t *I, const uint8_t qb[4], unsigned i, unsigned j, uint8_t tmp[32])
{
    sha256_ctx c; uint8_t hdr[3];
    hdr[0] = (uint8_t)(i >> 8); hdr[1] = (uint8_t)i; hdr[2] = (uint8_t)j;
    sha256_init(&c); sha256_update(&c, I, 16); sha256_update(&c, qb, 4);
    sha256_update(&c, hdr, 3); sha256_update(&c, tmp, 32); sha256_final(&c, tmp);
}
#endif

int lms_verify(const uint8_t pub[LMS_PUB_LEN], const uint8_t *msg, size_t msglen,
               const uint8_t *sig, size_t siglen, uint32_t *q_out)
{
    lms_params pr;
    const uint8_t *I = pub + 8, *T1 = pub + 24, *C, *y, *path;
    uint8_t qb[4], Qc[34], tmp[32], diff, blk[64];
    sha256_ctx kc, hc;
    uint32_t q, node;
    unsigned i, j, top, a;
    uint16_t ck;

    if (!params(pub, &pr)) return LMS_E_TYPE;
    if (sig == NULL || siglen != (size_t)(8 + 32 + 32 * (unsigned)pr.p + 4 + 32 * (unsigned)pr.h))
        return LMS_E_LEN;
    q = rd32(sig);
    if (q >= (1u << pr.h)) return LMS_E_INDEX;
    if (rd32(sig + 4) != (pr.w == 4 ? 3u : 4u)) return LMS_E_TYPE;
    C = sig + 8; y = sig + 40; path = sig + 40 + 32u * pr.p + 4;
    if (rd32(sig + 40 + 32u * pr.p) != rd32(pub)) return LMS_E_TYPE;
    if (q_out) *q_out = q;
    wr32(qb, q);

    /* Q = H(I || q || D_MESG || C || msg) */
    sha256_init(&hc);
    sha256_update(&hc, I, 16); sha256_update(&hc, qb, 4);
    tmp[0] = D_MESG >> 8; tmp[1] = D_MESG & 0xff; sha256_update(&hc, tmp, 2);
    sha256_update(&hc, C, 32); sha256_update(&hc, msg, msglen);
    sha256_final(&hc, Qc);
    ck = checksum(Qc, pr.w, pr.ls);
    Qc[32] = (uint8_t)(ck >> 8); Qc[33] = (uint8_t)ck;

    /* Kc = H(I || q || D_PBLC || z[0] || ... ) streamed, z[i] never stored together */
    sha256_init(&kc);
    sha256_update(&kc, I, 16); sha256_update(&kc, qb, 4);
    tmp[0] = D_PBLC >> 8; tmp[1] = D_PBLC & 0xff; sha256_update(&kc, tmp, 2);
    top = (1u << pr.w) - 1u;
    for (i = 0; i < pr.p; i++) {
        memcpy(tmp, y + 32u * i, 32);
        a = coef(Qc, i, pr.w);
        for (j = a; j < top; j++) {
#ifdef LMS_NO_FASTPATH
            chain_step(I, qb, i, j, tmp);
#else
            /* single-block message: I(16) q(4) i(2) j(1) tmp(32) = 55 B, padded in place */
            memcpy(blk, I, 16); memcpy(blk + 16, qb, 4);
            blk[20] = (uint8_t)(i >> 8); blk[21] = (uint8_t)i; blk[22] = (uint8_t)j;
            memcpy(blk + 23, tmp, 32);
            blk[55] = 0x80; memset(blk + 56, 0, 6); blk[62] = 0x01; blk[63] = 0xb8; /* 440 bits */
            sha256_oneblock(blk, tmp);
#endif
        }
        sha256_update(&kc, tmp, 32);
    }
    sha256_final(&kc, tmp);                 /* tmp = Kc */

    /* leaf: H(I || node || D_LEAF || Kc) then climb */
    node = (1u << pr.h) + q;
    {
        uint8_t nb[4], dd[2];
        wr32(nb, node); dd[0] = D_LEAF >> 8; dd[1] = D_LEAF & 0xff;
        sha256_init(&hc); sha256_update(&hc, I, 16); sha256_update(&hc, nb, 4);
        sha256_update(&hc, dd, 2); sha256_update(&hc, tmp, 32); sha256_final(&hc, tmp);
        for (i = 0; i < pr.h; i++) {
            wr32(nb, node >> 1); dd[0] = D_INTR >> 8; dd[1] = D_INTR & 0xff;
            sha256_init(&hc); sha256_update(&hc, I, 16); sha256_update(&hc, nb, 4);
            sha256_update(&hc, dd, 2);
            if (node & 1) { sha256_update(&hc, path + 32u * i, 32); sha256_update(&hc, tmp, 32); }
            else          { sha256_update(&hc, tmp, 32); sha256_update(&hc, path + 32u * i, 32); }
            sha256_final(&hc, tmp);
            node >>= 1;
        }
    }
    diff = 0;
    for (i = 0; i < 32; i++) diff |= (uint8_t)(tmp[i] ^ T1[i]);
    return diff ? LMS_E_BAD : LMS_OK;
}

#include "sha256.h"
#include <string.h>

#ifdef FS_COUNT_COMPRESS
unsigned long fs_compress_count;
#endif

static const uint32_t K[64] = {
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};

static const uint32_t IV[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                               0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};

#define ROR(x,n) (((x) >> (n)) | ((x) << (32 - (n))))

/* Rolled compression with a 16-word circular schedule: smallest code, 64 B of W. */
static void compress(uint32_t h[8], const uint8_t blk[64])
{
    uint32_t w[16], v[8], t1, t2;
    unsigned i;
#ifdef FS_COUNT_COMPRESS
    fs_compress_count++;
#endif
    for (i = 0; i < 16; i++)
        w[i] = ((uint32_t)blk[4*i] << 24) | ((uint32_t)blk[4*i+1] << 16) |
               ((uint32_t)blk[4*i+2] << 8) | blk[4*i+3];
    for (i = 0; i < 8; i++) v[i] = h[i];
    for (i = 0; i < 64; i++) {
        if (i >= 16) {
            uint32_t w15 = w[(i+1) & 15], w2 = w[(i+14) & 15];
            uint32_t s0 = ROR(w15,7) ^ ROR(w15,18) ^ (w15 >> 3);
            uint32_t s1 = ROR(w2,17) ^ ROR(w2,19) ^ (w2 >> 10);
            w[i & 15] = w[i & 15] + s0 + w[(i+9) & 15] + s1;
        }
        t1 = v[7] + (ROR(v[4],6) ^ ROR(v[4],11) ^ ROR(v[4],25)) +
             ((v[4] & v[5]) ^ (~v[4] & v[6])) + K[i] + w[i & 15];
        t2 = (ROR(v[0],2) ^ ROR(v[0],13) ^ ROR(v[0],22)) +
             ((v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]));
        v[7] = v[6]; v[6] = v[5]; v[5] = v[4]; v[4] = v[3] + t1;
        v[3] = v[2]; v[2] = v[1]; v[1] = v[0]; v[0] = t1 + t2;
    }
    for (i = 0; i < 8; i++) h[i] += v[i];
}

static void store_be(const uint32_t h[8], uint8_t out[32])
{
    unsigned i;
    for (i = 0; i < 8; i++) {
        out[4*i]   = (uint8_t)(h[i] >> 24); out[4*i+1] = (uint8_t)(h[i] >> 16);
        out[4*i+2] = (uint8_t)(h[i] >> 8);  out[4*i+3] = (uint8_t)h[i];
    }
}

void sha256_init(sha256_ctx *c)
{
    memcpy(c->h, IV, sizeof IV);
    c->len_lo = c->len_hi = 0; c->fill = 0;
}

void sha256_update(sha256_ctx *c, const uint8_t *p, size_t n)
{
    uint32_t old = c->len_lo;
    c->len_lo += (uint32_t)n;
    if (c->len_lo < old) c->len_hi++;
    while (n) {
        size_t k = 64u - c->fill;
        if (k > n) k = n;
        memcpy(c->buf + c->fill, p, k);
        c->fill = (uint8_t)(c->fill + k); p += k; n -= k;
        if (c->fill == 64) { compress(c->h, c->buf); c->fill = 0; }
    }
}

void sha256_final(sha256_ctx *c, uint8_t out[32])
{
    uint32_t hi = (c->len_hi << 3) | (c->len_lo >> 29), lo = c->len_lo << 3;
    unsigned i, f = c->fill;
    c->buf[f++] = 0x80;
    if (f > 56) { memset(c->buf + f, 0, 64 - f); compress(c->h, c->buf); f = 0; }
    memset(c->buf + f, 0, 56 - f);
    for (i = 0; i < 4; i++) { c->buf[56+i] = (uint8_t)(hi >> (24 - 8*i)); c->buf[60+i] = (uint8_t)(lo >> (24 - 8*i)); }
    compress(c->h, c->buf);
    store_be(c->h, out);
}

void sha256(const uint8_t *p, size_t n, uint8_t out[32])
{
    sha256_ctx c; sha256_init(&c); sha256_update(&c, p, n); sha256_final(&c, out);
}

void sha256_oneblock(const uint8_t blk[64], uint8_t out[32])
{
    uint32_t h[8];
    memcpy(h, IV, sizeof IV);
    compress(h, blk);
    store_be(h, out);
}

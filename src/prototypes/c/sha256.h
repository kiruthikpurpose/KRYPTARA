/* Minimal SHA-256 (FIPS 180-4). C99, no heap, no recursion. */
#ifndef FS_SHA256_H
#define FS_SHA256_H
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t h[8];
    uint8_t  buf[64];
    uint32_t len_lo;      /* total bytes, low 32 bits (enough: inputs < 4 GiB) */
    uint32_t len_hi;
    uint8_t  fill;
} sha256_ctx;

void sha256_init(sha256_ctx *c);
void sha256_update(sha256_ctx *c, const uint8_t *p, size_t n);
void sha256_final(sha256_ctx *c, uint8_t out[32]);
void sha256(const uint8_t *p, size_t n, uint8_t out[32]);

/* Compress one fully padded 64-byte block starting from the IV, write digest.
   Used by the LMS fast path for single-block messages (<= 55 bytes). */
void sha256_oneblock(const uint8_t blk[64], uint8_t out[32]);

#ifdef FS_COUNT_COMPRESS
extern unsigned long fs_compress_count;   /* host-only instrumentation */
#endif
#endif

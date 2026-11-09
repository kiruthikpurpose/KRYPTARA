/* FR-ASR-10 (legacy): "All parsers SHALL be bounded and continuously fuzzed." Partial coverage: a
 * simple seeded random-input harness over the hardened admission API's parser-like entry points
 * (ac_faults_from_labels, ac_labels_valid, ac_tbl_upper/lower, ac_key_install_authorised,
 * ac_no_duplicate_keys). This is NOT coverage-guided fuzzing (no AFL/libFuzzer/honggfuzz is
 * installed or assumed) -- it is a cheap, dependency-free stand-in: random malformed input, many
 * iterations, asserting the two properties a hardened parser must have: (1) it never crashes
 * (caught indirectly -- a crash fails the whole binary, which run_all_checks.sh treats as a
 * failure) and (2) it never returns a result outside its documented contract (valid error codes,
 * or a table that is still monotone/within-bounds when input was otherwise well-formed).
 * Deterministic seed for reproducibility; run time is a few milliseconds. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../src/policy8.c"

static uint32_t rng_state = 0xC0FFEE42u;
static uint32_t xrand(void) {   /* xorshift32, no libc rand() dependency */
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 17; rng_state ^= rng_state << 5;
    return rng_state;
}

int main(void) {
    const int N = 200000;
    int bad = 0;
    for (int iter = 0; iter < N; iter++) {
        uint8_t f[8]; unsigned nf = xrand() % 9;        /* 0..8, one over cap to test the boundary */
        for (unsigned i = 0; i < 8; i++) f[i] = (uint8_t)(xrand() & 0xff);
        unsigned k = xrand() % 4;                        /* 0..3, one over the k<=2 cap */
        uint8_t expo = (uint8_t)(xrand() & 0xff);
        ac_tbl_t U, L;

        int ru = ac_tbl_upper(&U, f, nf, k, expo, NULL);
        if (ru == 0) {
            if (!ac_tbl_monotone(&U)) { bad++; printf("FAIL: ac_tbl_upper produced non-monotone U\n"); }
        } else if (ru != -1) { bad++; printf("FAIL: ac_tbl_upper returned undocumented code %d\n", ru); }

        int rl = ac_tbl_lower(&L, f, nf, k, expo, NULL);
        if (rl != 0 && rl != -1 && rl != -2) { bad++; printf("FAIL: ac_tbl_lower returned undocumented code %d\n", rl); }
        if (rl == 0 && ru == 0) {
            /* within() must itself never crash or diverge on these two freshly (possibly wild) tables */
            ac_tbl_within(&U, &U, &L);
        }

        uint8_t kind[8]; uint32_t lab[8];
        for (unsigned i = 0; i < 8; i++) { kind[i] = (uint8_t)(xrand() % 4); lab[i] = xrand(); }
        uint8_t present = (uint8_t)(xrand() & 0xff);
        int rlv = ac_labels_valid(kind, lab, present);
        if (rlv != 0 && rlv != 1) { bad++; printf("FAIL: ac_labels_valid returned non-boolean %d\n", rlv); }

        uint8_t cl[16]; uint32_t lab2[8];
        for (unsigned i = 0; i < 8; i++) lab2[i] = xrand();
        unsigned cap = xrand() % 17, singles = (uint8_t)(xrand() & 0xff);
        uint32_t filter = xrand();
        int rf = ac_faults_from_labels(cl, cap, lab2, present, singles, filter);
        if (rf < -1) { bad++; printf("FAIL: ac_faults_from_labels returned %d\n", rf); }
        if (rf >= 0 && (unsigned)rf > cap) { bad++; printf("FAIL: ac_faults_from_labels overran cap\n"); }

        ac_tbl_t t_active; for (int i = 0; i < 8; i++) t_active.w[i] = xrand();
        uint8_t S = (uint8_t)(xrand() & 0xff), holder = (uint8_t)(1u << (xrand() % 8));
        int active = xrand() & 1;
        int rk = ac_key_install_authorised(&t_active, S, holder, active);
        if (rk != 0 && rk != 1) { bad++; printf("FAIL: ac_key_install_authorised returned non-boolean %d\n", rk); }

        ac_key_hash_t kh[8]; for (int i = 0; i < 8; i++) for (int j = 0; j < 32; j++) kh[i].h[j] = (uint8_t)xrand();
        int rd = ac_no_duplicate_keys(kind, kh, present);
        if (rd != 0 && rd != 1) { bad++; printf("FAIL: ac_no_duplicate_keys returned non-boolean %d\n", rd); }
    }
    printf("fuzz_policy8: %d iterations, failures=%d\n", N, bad);
    return bad;
}

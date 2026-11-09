/* On-device policy admission for <=8 evidence atoms (256-bit monotone truth tables).
 * Admission rule: monotone(t) && Lo <= t <= U  (&& t <= t_old when tightening).
 * U  = largest policy that no admissible compromise can satisfy (safety bound)
 * Lo = smallest policy the survivors of every admissible loss still satisfy (liveness bound)
 * No allocation, no recursion, no libc beyond memset. */
#include <stdint.h>
#include <string.h>

typedef struct { uint32_t w[8]; } ac_tbl_t;

static inline unsigned tb(const ac_tbl_t *t, unsigned m) { return (t->w[m >> 5] >> (m & 31)) & 1u; }
static inline void ts(ac_tbl_t *t, unsigned m) { t->w[m >> 5] |= 1u << (m & 31); }

/* Adding an atom never removes authority. */
int ac_tbl_monotone(const ac_tbl_t *t) {
    for (unsigned m = 0; m < 256; m++)
        if (tb(t, m))
            for (unsigned i = 0; i < 8; i++)
                if (!tb(t, m | (1u << i))) return 0;
    return 1;
}

/* Fault classes from labels: one class per present atom of a "single" kind, one per label value. */
unsigned ac_faults_from_labels(uint8_t *out, unsigned cap, const uint16_t lab[8], uint8_t present,
                               uint8_t singles, uint16_t label_filter) {
    unsigned n = 0;
    for (unsigned i = 0; i < 8 && n < cap; i++)
        if ((present & singles) >> i & 1u) out[n++] = (uint8_t)(1u << i);
    for (unsigned l = 0; l < 16 && n < cap; l++) {
        if (!(label_filter >> l & 1u)) continue;
        uint8_t m = 0;
        for (unsigned i = 0; i < 8; i++)
            if ((present >> i & 1u) && (lab[i] >> l & 1u)) m |= (uint8_t)(1u << i);
        if (m) out[n++] = m;
    }
    return n;
}

/* Unions of exactly k (0,1,2) distinct fault classes; excl[a] bit b excludes the pair (a,b). */
static unsigned covered(unsigned m, const uint8_t *f, unsigned nf, unsigned k, uint8_t extra,
                        const uint16_t *excl, int want_subset) {
    /* want_subset=1: is m a subset of some union?  want_subset=0: does m contain the complement of some union? */
    if (k == 0) {
        uint8_t u = extra;
        return want_subset ? ((m & ~u & 0xffu) == 0) : ((~u & 0xffu & ~m) == 0);
    }
    for (unsigned a = 0; a < nf; a++) {
        if (k == 1) {
            uint8_t u = f[a] | extra;
            if (want_subset ? ((m & ~u & 0xffu) == 0) : ((~u & 0xffu & ~m) == 0)) return 1;
            continue;
        }
        for (unsigned b = a + 1; b < nf; b++) {
            if (excl && (excl[a] >> b & 1u)) continue;
            uint8_t u = f[a] | f[b] | extra;
            if (want_subset ? ((m & ~u & 0xffu) == 0) : ((~u & 0xffu & ~m) == 0)) return 1;
        }
    }
    return 0;
}

/* Safety bound: expo = exposure atoms (publicity), always available to an attacker. */
void ac_tbl_upper(ac_tbl_t *U, const uint8_t *f, unsigned nf, unsigned k, uint8_t expo, const uint16_t *excl) {
    memset(U, 0, sizeof *U);
    for (unsigned m = 0; m < 256; m++)
        if (!covered(m, f, nf, k, expo, excl, 1)) ts(U, m);
}

/* Liveness bound: absent = atoms that do not exist on this device (permanently lost). */
void ac_tbl_lower(ac_tbl_t *L, const uint8_t *f, unsigned nf, unsigned k, uint8_t absent, const uint16_t *excl) {
    memset(L, 0, sizeof *L);
    for (unsigned m = 0; m < 256; m++)
        if (covered(m, f, nf, k, absent, excl, 0)) ts(L, m);
}

/* Lo <= t <= U, branch-free over the words. */
int ac_tbl_within(const ac_tbl_t *t, const ac_tbl_t *U, const ac_tbl_t *L) {
    uint32_t bad = 0;
    for (unsigned i = 0; i < 8; i++) bad |= (t->w[i] & ~U->w[i]) | (L->w[i] & ~t->w[i]);
    return bad == 0;
}

int ac_tbl_tighten(const ac_tbl_t *n, const ac_tbl_t *o) {
    uint32_t bad = 0;
    for (unsigned i = 0; i < 8; i++) bad |= n->w[i] & ~o->w[i];
    return bad == 0;
}

/* Authorisation at use time: evidence set S (bit i = atom i verified for this transition). */
int ac_tbl_authorises(const ac_tbl_t *t, uint8_t S) { return (int)tb(t, S); }

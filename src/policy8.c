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
/* Returns number of classes (>=0), or -1 if cap would be exceeded (never truncates silently). */
int ac_faults_from_labels(uint8_t *out, unsigned cap, const uint32_t lab[8], uint8_t present,
                          uint8_t singles, uint32_t label_filter) {
    unsigned n = 0;
    for (unsigned i = 0; i < 8; i++)
        if ((present & singles) >> i & 1u) { if (n >= cap) return -1; out[n++] = (uint8_t)(1u << i); }
    for (unsigned l = 0; l < 32; l++) {
        if (!(label_filter >> l & 1u)) continue;
        uint8_t m = 0;
        for (unsigned i = 0; i < 8; i++)
            if ((present >> i & 1u) && (lab[i] >> l & 1u)) m |= (uint8_t)(1u << i);
        if (m) { if (n >= cap) return -1; out[n++] = m; }
    }
    return (int)n;
}
/* Exposure atoms are derived from atom kinds (kind 3 = WIT), never supplied by the caller. */
uint8_t ac_expo_from_kinds(const uint8_t kind[8], uint8_t present) {
    uint8_t e = 0;
    for (unsigned i = 0; i < 8; i++) if ((present >> i & 1u) && kind[i] == 3) e |= (uint8_t)(1u << i);
    return e;
}
/* Every present SIG atom (kind 1) must carry a custody-group label (bits 16..23), else reject. */
int ac_labels_valid(const uint8_t kind[8], const uint32_t lab[8], uint8_t present) {
    for (unsigned i = 0; i < 8; i++)
        if ((present >> i & 1u) && kind[i] == 1 && !((lab[i] >> 16) & 0xffu)) return 0;
    return 1;
}

/* Unions of exactly k (0,1,2) distinct fault classes; excl[a] bit b excludes the pair (a,b). */
static unsigned covered(unsigned m, const uint8_t *f, unsigned nf, unsigned k, uint8_t extra,
                        const uint32_t *excl, int want_subset) {
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
/* Fail-closed: k>2 unsupported (-1); k is clamped to nf so a short class list can never make U permissive. */
int ac_tbl_upper(ac_tbl_t *U, const uint8_t *f, unsigned nf, unsigned k, uint8_t expo, const uint32_t *excl) {
    memset(U, 0, sizeof *U);
    if (k > 2 || nf > 32) return -1;
    if (k > nf) k = nf;
    for (unsigned m = 0; m < 256; m++)
        if (!covered(m, f, nf, k, expo, excl, 1)) ts(U, m);
    return 0;
}

/* Liveness bound: absent = atoms that do not exist on this device (permanently lost). */
/* Liveness: if k > nf the budget is unsatisfiable by construction -> return -2 (caller must refuse the profile). */
int ac_tbl_lower(ac_tbl_t *L, const uint8_t *f, unsigned nf, unsigned k, uint8_t absent, const uint32_t *excl) {
    memset(L, 0, sizeof *L);
    if (k > 2 || nf > 32) return -1;
    if (k > nf) return -2;
    for (unsigned m = 0; m < 256; m++)
        if (covered(m, f, nf, k, absent, excl, 0)) ts(L, m);
    return 0;
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

/* Canonical form (REQ-ADM-05): f'(S) = f(S & present). Atoms that do not exist on the device are treated as
 * compromised AND lost by the bounds, so a stored table must not depend on them. */
void ac_tbl_project(ac_tbl_t *out, const ac_tbl_t *t, uint8_t present) {
    memset(out, 0, sizeof *out);
    for (unsigned m = 0; m < 256; m++) if (tb(t, m & present)) ts(out, m);
}
int ac_tbl_is_projected(const ac_tbl_t *t, uint8_t present) {
    ac_tbl_t p; ac_tbl_project(&p, t, present);
    uint32_t d = 0; for (unsigned i = 0; i < 8; i++) d |= p.w[i] ^ t->w[i];
    return d == 0;
}

/* REQ-LIFE-02: installing a key into an ACTIVE custody slot MUST also carry that slot's own
 * holder atom in the evidence set, on top of whatever the admission table authorises for the
 * KEY_INSTALL transition (F-R2-03: otherwise an outside quorum can install keys into every slot
 * without that slot's holder ever participating). "active" is false only for a slot that holds
 * no key yet, where there is no holder to co-sign. */
int ac_key_install_authorised(const ac_tbl_t *t, uint8_t S, uint8_t holder_atom, int active) {
    if (!ac_tbl_authorises(t, S)) return 0;
    if (active && !(S & holder_atom)) return 0;
    return 1;
}

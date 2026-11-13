/* On-device policy admission for <=8 evidence atoms (256-bit monotone truth tables).
 * Admission rule: monotone(t) && Lo <= t <= U  (&& t <= t_old when tightening).
 * U  = largest policy that no admissible compromise can satisfy (safety bound)
 * Lo = smallest policy the survivors of every admissible loss still satisfy (liveness bound)
 * No allocation, no recursion, no libc beyond memset. */
#include <stdint.h>
#include <string.h>
#include "ac_types.h"

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

/* REQ-EVD-02 (ADR-002): assumption labels (bits 0..7: which cryptographic assumption/hash family a
 * verifier relies on) MUST be derived by the device from the verifier descriptor, never accepted as
 * caller-supplied input; group/site/infrastructure labels (bits 16..31) MAY be declared, but only at
 * T2 (the caller's responsibility, not checked here -- that is a lifecycle/tier gate, not a label
 * format rule). PROVIDER_ASSUMPTION is a closed, fixed table: an unknown provider id derives to 0
 * (no assumption claimed), never to a caller-chosen value, so a malicious or buggy caller cannot
 * forge which hash family a key is assumed to depend on. */
#define AC_PROVIDER_COUNT 4
static const uint32_t AC_PROVIDER_ASSUMPTION[AC_PROVIDER_COUNT] = {
    0x01, /* 0: LMS/HSS over SHA-256   -> family H1 */
    0x02, /* 1: LMS/HSS over SHAKE256  -> family H2 */
    0x04, /* 2: SLH-DSA (SHA2 or SHAKE parameter set folded into the same family bit as its base hash) */
    0x08, /* 3: ML-KEM-768 (enrolment only, not a SIG atom; included for completeness) */
};
uint32_t ac_derive_assumption_label(unsigned provider_id) {
    return (provider_id < AC_PROVIDER_COUNT) ? AC_PROVIDER_ASSUMPTION[provider_id] : 0u;
}
/* Combines the device-derived assumption bits (authoritative, bits 0..7) with the caller-declared
 * group/site/infra bits (bits 16..31, passed through as-is -- their T2-only gating happens upstream)
 * into the final per-atom label. Declared bits 0..7, if any, are masked away: the caller cannot
 * inject an assumption label no matter what it passes in declared[i]. */
void ac_derive_labels(uint32_t out[8], const uint8_t provider[8], const uint32_t declared[8], uint8_t present) {
    for (unsigned i = 0; i < 8; i++) {
        if (!(present >> i & 1u)) { out[i] = 0; continue; }
        out[i] = ac_derive_assumption_label(provider[i]) | (declared[i] & 0xffff0000u);
    }
}

/* REQ-EVD-03: duplicate key hashes MUST be rejected. Two present SIG atoms carrying the same key
 * hash would defeat custody separation (one compromised physical key counts as two independent
 * atoms in the fault model). Compares full 32-byte hashes; only present SIG atoms (kind 1) are
 * checked, matching ac_labels_valid's scope. O(nf^2) over at most 8 atoms, no allocation. */

static int ac_hash_eq(const ac_key_hash_t *a, const ac_key_hash_t *b) {
    uint8_t d = 0;
    for (unsigned i = 0; i < 32; i++) d |= (uint8_t)(a->h[i] ^ b->h[i]);
    return d == 0;
}
int ac_no_duplicate_keys(const uint8_t kind[8], const ac_key_hash_t key[8], uint8_t present) {
    for (unsigned i = 0; i < 8; i++) {
        if (!((present >> i & 1u) && kind[i] == 1)) continue;
        for (unsigned j = i + 1; j < 8; j++) {
            if (!((present >> j & 1u) && kind[j] == 1)) continue;
            if (ac_hash_eq(&key[i], &key[j])) return 0;
        }
    }
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

/* REQ-NV-01: tables MUST be stored with complements and decisions MUST be evaluated twice with
 * complementary encodings. A dual-stored table detects single-word bit-flip corruption (flash wear,
 * radiation, torn write) that a single copy cannot: if the live copy and the stored complement no
 * longer agree, ac_tbl_dual_authorises refuses rather than trusting either one. */

void ac_tbl_dual_init(ac_tbl_dual_t *d, const ac_tbl_t *t) {
    d->t = *t;
    for (unsigned i = 0; i < 8; i++) d->c.w[i] = ~t->w[i];
}
/* Returns 1 iff the stored complement still bitwise-inverts the live table (no corruption detected). */
int ac_tbl_dual_consistent(const ac_tbl_dual_t *d) {
    uint32_t bad = 0;
    for (unsigned i = 0; i < 8; i++) bad |= d->t.w[i] ^ ~d->c.w[i];
    return bad == 0;
}
/* Evaluates S against BOTH encodings independently and only authorises if they agree; a
 * single-word fault that flips a bit in exactly one of the two copies is caught here, not just by
 * the (cheaper, coarser) full-table ac_tbl_dual_consistent check, because this decodes S from each
 * copy on every call rather than trusting a consistency check done once at load time. */
int ac_tbl_dual_authorises(const ac_tbl_dual_t *d, uint8_t S) {
    unsigned from_t = tb(&d->t, S);
    unsigned from_c = !tb(&d->c, S);
    if (from_t != from_c) return 0;   /* disagreement: fail closed, do not pick a winner */
    return (int)from_t;
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

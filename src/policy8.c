/* On-device policy admission for <=8 evidence atoms (256-bit monotone truth tables).
 * Admission rule: monotone(t) && Lo <= t <= U  (&& t <= t_old when tightening).
 * U  = largest policy that no admissible compromise can satisfy (safety bound)
 * Lo = smallest policy the survivors of every admissible loss still satisfy (liveness bound)
 * No allocation, no recursion, no libc beyond memset.
 * Provisioning/derivation functions (bounds, labels, duplicate keys) live in policy8_prov.c, included at
 * the end of this file unless AC_RUNTIME_ONLY is defined (locked-stage runtime object, GATE-07). */
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

#ifndef AC_RUNTIME_ONLY
#include "policy8_prov.c"
#endif

/* Governed-change kernel pieces above admission: tier engine (REQ-TIER-01, REQ-NV-01),
 * image-commit boot check (REQ-IMG-01, ADR-007) and the domain-separated chain hash
 * (REQ-CHAIN-01). Host reference in C; not yet ported to or measured on any MCU.
 * No allocation, no recursion. */
#include "policy8.c"
#include "prototypes/c/sha256.h"

typedef enum { AC_T0_HALT = 0, AC_T1_OPERATE = 1, AC_T2_CONST = 2, AC_T2_RECOVERY = 3, AC_TIER_N = 4 } ac_tier_t;

typedef enum {
    AC_ACT_HALT = 0, AC_ACT_RESUME, AC_ACT_ACTIVATE_IMAGE, AC_ACT_DECLARE_CLASS_DEAD,
    AC_ACT_KEY_INSTALL, AC_ACT_LABEL_DECLARE, AC_ACT_RECOVER, AC_ACT_N
} ac_action_t;

/* Every action has exactly one tier; an action missing from this table cannot be authorised. */
static const uint8_t AC_ACTION_TIER[AC_ACT_N] = {
    [AC_ACT_HALT] = AC_T0_HALT,
    [AC_ACT_RESUME] = AC_T1_OPERATE,
    [AC_ACT_ACTIVATE_IMAGE] = AC_T1_OPERATE,
    [AC_ACT_DECLARE_CLASS_DEAD] = AC_T1_OPERATE,
    [AC_ACT_KEY_INSTALL] = AC_T2_CONST,
    [AC_ACT_LABEL_DECLARE] = AC_T2_CONST,
    [AC_ACT_RECOVER] = AC_T2_RECOVERY,
};

typedef struct { ac_tbl_dual_t tier[AC_TIER_N]; } ac_engine_t;

void ac_engine_load(ac_engine_t *e, const ac_tbl_t tables[AC_TIER_N]) {
    for (unsigned i = 0; i < AC_TIER_N; i++) ac_tbl_dual_init(&e->tier[i], &tables[i]);
}

/* Fail closed on an unknown action, and on any disagreement between a table and its complement. */
int ac_engine_authorise(const ac_engine_t *e, unsigned action, uint8_t S) {
    if (action >= AC_ACT_N) return 0;
    return ac_tbl_dual_authorises(&e->tier[AC_ACTION_TIER[action]], S);
}

/* The locked stage boots a staged image only if its digest equals the digest committed by the
 * last authorised ACTIVATE_IMAGE. A valid OEM signature is provenance, never authority: it is
 * deliberately not an input here. Comparison does not exit early. */
int ac_image_bootable(const uint8_t committed[32], const uint8_t staged[32], int have_commit) {
    uint8_t d = 0;
    for (unsigned i = 0; i < 32; i++) d |= (uint8_t)(committed[i] ^ staged[i]);
    return have_commit && d == 0;
}

/* SHA-256(len(domain) || domain || prev || payload); the tag is length-prefixed so the
 * domain/prev boundary is unambiguous. Must match models/hash_chain.py byte for byte. */
int ac_chain_hash(uint8_t out[32], const uint8_t *domain, size_t dlen, const uint8_t prev[32],
                  const uint8_t *payload, size_t plen) {
    if (dlen > 255) return -1;
    sha256_ctx c; uint8_t l = (uint8_t)dlen;
    sha256_init(&c);
    sha256_update(&c, &l, 1);
    sha256_update(&c, domain, dlen);
    sha256_update(&c, prev, 32);
    sha256_update(&c, payload, plen);
    sha256_final(&c, out);
    return 0;
}

/* Waist v1, interface W1: the pure kernel (docs/architecture/primitives-and-waist.md section 4.5,
 * docs/decisions/ADR-041). No I/O, no allocation, no clock, no mutable globals, no recursion.
 * Everything that changes the world leaves as an intent; everything the kernel needs arrives in
 * the message or the context.
 *
 * Status: waist v1 DRAFT. The stability promise below takes effect at the T0 freeze
 * (docs/implementation/roadmap.md, Phase 3: three unrelated ports and an independent
 * re-implementation agree). Until then the layout may change, but only by updating
 * src/waist-v1.abi on purpose (scripts/arch_check.py rule R8).
 * Promise after the freeze: status codes are negative, stable for ever and never reused. A struct
 * layout or an enum value in this file changes only with a new waist major version
 * (AC_WAIST_VERSION), and tests/vectors/waist-v1.txt keeps passing for v1.
 * What this slice does NOT contain: signature verification (waist W2) and platform access (W3).
 * The kernel consumes evidence that an evidence layer has already verified; see ADR-041. */
#ifndef AC_WAIST_H
#define AC_WAIST_H
#include <stddef.h>
#include "ac_types.h"

#define AC_WAIST_VERSION 1u

typedef int32_t ac_status_t;
enum {
    AC_OK        =   0,
    AC_E_BADMSG  =  -1,   /* malformed message, or a field out of range */
    AC_E_AUTH    =  -2,   /* the verified evidence does not authorise this action at its tier */
    AC_E_ADMIT   =  -3,   /* table not admissible: not monotone, not projected, outside [Lo,U], or not a tightening */
    AC_E_HOLDER  =  -4,   /* installing into an ACTIVE slot without the slot holder's co-signature (REQ-LIFE-02) */
    AC_E_DUPKEY  =  -5,   /* the key hash is already installed in another slot (REQ-EVD-03) */
    AC_E_HALTED  =  -6,   /* the bundle is halted */
    AC_E_BUDGET  =  -7,   /* the atom has used its halt budget for this epoch (REQ-HALT-01) */
    AC_E_BUSY    =  -8,   /* the previous snapshot has not been acknowledged (single mutator) */
    AC_E_NOCLASS =  -9,   /* would leave fewer than t+s+1 live key slots (REQ-LIFE-01) */
    AC_E_STATE   = -10,   /* context not initialised, or the action does not apply in this state */
    AC_E_IMAGE   = -11    /* the staged image digest is not the committed one (REQ-IMG-01) */
};

typedef enum { AC_T0_HALT = 0, AC_T1_OPERATE = 1, AC_T2_CONST = 2, AC_T2_RECOVERY = 3, AC_TIER_N = 4 } ac_tier_t;

/* Numbering is frozen. Which tier authorises each action is part of the profile (ac_genesis_t). */
typedef enum {
    AC_ACT_HALT = 0, AC_ACT_RESUME = 1, AC_ACT_ACTIVATE_IMAGE = 2, AC_ACT_TIGHTEN_TABLE = 3,
    AC_ACT_ADVANCE_EPOCH = 4, AC_ACT_RETIRE_SLOT = 5, AC_ACT_INSTALL_TABLE = 6, AC_ACT_KEY_INSTALL = 7,
    AC_ACT_N = 8
} ac_action_t;

/* Message kinds follow docs/specifications/interfaces-and-data-models.md; this slice implements
 * BOOT, PROPOSE_TX and HALT. */
typedef enum { AC_MSG_BOOT = 1, AC_MSG_PROPOSE_TX = 2, AC_MSG_HALT = 5 } ac_msg_kind_t;

/* Fixed-size projection of a transition. The wire form (CBOR bundle) is parsed outside the
 * kernel and projected to this struct. `evidence` is the set of atoms whose evidence has been
 * verified by the evidence layer. */
typedef struct {
    uint8_t  kind;       /* ac_msg_kind_t */
    uint8_t  action;     /* ac_action_t, PROPOSE_TX only */
    uint8_t  evidence;   /* verified evidence set, bit i = atom i */
    uint8_t  atom;       /* HALT: the halting atom. KEY_INSTALL, RETIRE_SLOT: the slot */
    uint8_t  bundle;     /* HALT, RESUME, ACTIVATE_IMAGE: bundle id, 0..15 */
    uint8_t  tier;       /* TIGHTEN_TABLE, INSTALL_TABLE: the target tier */
    uint8_t  digest[32]; /* ACTIVATE_IMAGE, BOOT: image digest. KEY_INSTALL: the new key hash */
    ac_tbl_t table;      /* TIGHTEN_TABLE, INSTALL_TABLE: the proposed table */
} ac_msg_t;

typedef enum { AC_INT_NONE = 0, AC_INT_NV_WRITE_SNAPSHOT = 1, AC_INT_BOOT_IMAGE = 3, AC_INT_REJECT = 6 } ac_intent_kind_t;
typedef struct { uint8_t kind; uint32_t seq; int32_t code; } ac_intent_t;
#define AC_MAX_INTENTS 2u
typedef struct { uint8_t n; ac_intent_t it[AC_MAX_INTENTS]; } ac_effects_t;

typedef struct { ac_tbl_dual_t tier[AC_TIER_N]; } ac_engine_t;

/* The fault structure a tier's table is admitted against: compromise classes and loss classes
 * (masks over atoms), budgets t and s (at most 2, the limit of policy8.c), and at most one
 * excluded pair of classes per side (0xff = none), such as "both hash families lost". */
#define AC_MAX_CLASSES 16u
typedef struct {
    uint8_t t, s;
    uint8_t nfc, nfl;
    uint8_t xc_a, xc_b, xl_a, xl_b;       /* excluded pair of compromise / loss classes, a < b < n */
    uint8_t fc[AC_MAX_CLASSES], fl[AC_MAX_CLASSES];
} ac_budget_t;

typedef struct {
    uint32_t      version;                 /* AC_WAIST_VERSION once initialised, else 0 */
    uint8_t       present;                 /* atoms that exist on this device */
    uint8_t       kinds[8];                /* 0 none, 1 SIG, 2 PRES, 3 WIT */
    uint8_t       key_present;             /* SIG slots holding a key */
    ac_key_hash_t key[8];
    ac_engine_t   eng;                     /* tier tables with complements (REQ-NV-01) */
    ac_budget_t   bud[AC_TIER_N];          /* per-tier fault structure; tier 0 (HALT) is not admitted against it */
    uint8_t       action_tier[AC_ACT_N];   /* the profile: tier that authorises each action */
    uint16_t      halted;                  /* bundles currently halted */
    uint8_t       halt_budget;             /* h halts per atom per epoch */
    uint8_t       halt_used[8];
    uint32_t      epoch;
    uint8_t       have_commit;
    uint8_t       committed[32];           /* digest committed by the last ACTIVATE_IMAGE */
    uint8_t       head[32];                /* hash-chain head over every accepted transition */
    uint32_t      seq;                     /* snapshots issued */
    uint32_t      acked;                   /* snapshots acknowledged */
} ac_ctx_t;

typedef struct {
    uint8_t       present, kinds[8], key_present;
    ac_key_hash_t key[8];
    ac_budget_t   bud[AC_TIER_N];
    uint8_t       action_tier[AC_ACT_N];
    uint8_t       halt_budget;
    ac_tbl_t      table[AC_TIER_N];
} ac_genesis_t;

/* Initialise from a provisioning record, running the same admission the device would. On failure
 * the context stays all-zero (version 0) and every later step returns AC_E_STATE. */
ac_status_t ac_genesis(ac_ctx_t *ctx, const ac_genesis_t *g);
/* The kernel step. An accepted transition updates the context, extends the chain and issues one
 * NV_WRITE_SNAPSHOT intent. A rejected message changes nothing and issues one REJECT intent.
 * `needed` receives the number of intent slots the effects buffer must hold. */
ac_status_t ac_step(ac_ctx_t *ctx, const ac_msg_t *in, ac_effects_t *out, size_t *needed);
/* The platform confirms that snapshot `seq` is durable. */
ac_status_t ac_ack(ac_ctx_t *ctx, uint32_t seq);
/* SHA-256 over the canonical serialisation of the context (state commitment). Fails closed with
 * AC_E_STATE if the context is uninitialised or a stored table disagrees with its complement. */
ac_status_t ac_ctx_digest(const ac_ctx_t *ctx, uint8_t out[32]);

#endif

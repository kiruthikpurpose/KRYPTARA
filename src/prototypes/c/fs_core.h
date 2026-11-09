/* First-stage verifier core: 3 key-hash slots, assumption-class quorum, floor rule.
   C99, no heap, no recursion. Persistence goes through the abstract flash HAL in
   fs_journal.h. */
#ifndef FS_CORE_H
#define FS_CORE_H
#include <stdint.h>
#include <stddef.h>
#include "fs_quorum.h"
#include "lms.h"

#define FS_NSLOTS    3u
#define FS_MAX_SIGS  3u
#define FS_CMD_LEN   52u

#ifndef FS_QUORUM_MIN
#define FS_QUORUM_MIN 1u          /* policy: min distinct signers for a command */
#endif
#ifndef FS_REQUIRE_FOREIGN_CLASS
#define FS_REQUIRE_FOREIGN_CLASS 0 /* policy: some signer must share no class with the retired slot */
#endif

enum { SLOT_EMPTY = 0, SLOT_ACTIVE = 1, SLOT_RETIRED = 2 };
enum { OP_ADVANCE_FLOOR = 1, OP_REPLACE_SLOT = 2 };
#define NO_SLOT 0xffu

typedef enum {
    FS_OK = 0,
    FS_E_PARSE = -1,      /* malformed / truncated bundle or command */
    FS_E_SLOT = -2,       /* slot unusable (empty, retired, bad index, duplicate) */
    FS_E_KEYHASH = -3,    /* pubkey does not hash to the slot's committed hash */
    FS_E_SIG = -4,        /* LMS verification failed (any lms_verify error) */
    FS_E_QUORUM = -5,     /* quorum too small or assumption sets overlap */
    FS_E_POLICY = -6,     /* signer == retired slot, no foreign class, bad op args */
    FS_E_REPLAY = -7,     /* epoch mismatch or LMS index not above slot high-water */
    FS_E_FLOOR = -8,      /* new floor < current floor, or image version < floor */
    FS_E_FLASH = -9       /* HAL failure (including simulated power cut) */
} fs_err;

typedef struct {
    uint32_t epoch;                   /* == journal sequence number; bumped per commit */
    uint32_t floor;                   /* min acceptable image version, monotone */
    uint8_t  state[FS_NSLOTS];
    uint16_t cls[FS_NSLOTS];          /* assumption-class bitset of each slot */
    uint32_t last_q[FS_NSLOTS];       /* highest LMS leaf index accepted for a command */
    uint8_t  qseen[FS_NSLOTS];        /* 1 if last_q is meaningful */
    uint8_t  hash[FS_NSLOTS][32];     /* SHA-256 of the 56-byte LMS public key */
} fs_state;

/* One signature in a bundle. Pointers alias the input buffer (zero-copy). */
typedef struct {
    uint8_t        slot;
    const uint8_t *pub;      /* 56 B */
    const uint8_t *sig;
    uint16_t       siglen;
} fs_sigref;

/* Bundle wire format: n(1) { slot(1) pub(56) siglen(2,BE) sig(siglen) }*n, nothing after. */
fs_err fs_parse_bundle(const uint8_t *buf, size_t len, fs_sigref out[FS_MAX_SIGS], unsigned *n);

/* Verify every signature over msg against the state's slots, apply the quorum rule.
   On success *mask has bit s set for each signing slot. If last_q_out != NULL,
   leaf indices are returned (per signature order). Does not mutate state. */
fs_err fs_authorize(const fs_state *st, const uint8_t *msg, size_t msglen,
                    const fs_sigref *sr, unsigned n, uint8_t *mask, uint32_t qs[FS_MAX_SIGS]);

/* Command message layout (52 B, big endian):
   0 "FSC1" | 4 op | 5 slot | 6-7 zero | 8 epoch | 12 new_floor |
   16 new_hash[32] | 48 new_class(2) | 50 zero(2).
   ADVANCE_FLOOR: slot = slot to retire (or NO_SLOT), new_floor >= floor.
   REPLACE_SLOT : slot = slot to replace; new_hash/new_class supplied; slot becomes ACTIVE. */
void fs_build_cmd(uint8_t out[FS_CMD_LEN], uint8_t op, uint8_t slot, uint32_t epoch,
                  uint32_t new_floor, const uint8_t new_hash[32], uint16_t new_class);

/* Pure state transition: validate command + bundle against st, produce *next on success. */
fs_err fs_command_eval(const fs_state *st, const uint8_t msg[FS_CMD_LEN],
                       const uint8_t *bundle, size_t bundle_len, fs_state *next);

/* Image acceptance: image message = "IMG1" | version(4,BE) | digest(32). The
   signing slot must be ACTIVE and version >= floor. Images need exactly one valid
   signature (the quorum policy applies to authority commands, not to images). */
fs_err fs_image_check(const fs_state *st, uint32_t version, const uint8_t digest[32],
                      const uint8_t *bundle, size_t bundle_len);

#endif

#include <stdint.h>
#include <stddef.h>
#define AC_PACKED __attribute__((packed))
typedef struct AC_PACKED { uint16_t type; uint8_t fmt_major, fmt_minor; uint16_t len; uint16_t flags; } ac_rec_hdr_t;
typedef struct AC_PACKED { uint16_t alg_id; uint8_t role, tier; uint32_t assumption_mask;
  uint16_t pubkey_len, sig_len, flags, rsvd; } ac_alg_desc_t;
typedef struct AC_PACKED { uint16_t alg_id; uint8_t hash_alg, state; uint32_t assumption_mask;
  uint8_t key_hash[32]; uint32_t activation_floor; uint8_t group, rsvd[3]; } ac_slot_t;
typedef struct AC_PACKED { ac_rec_hdr_t h; uint32_t floor_idx, authority_epoch, journal_seq;
  uint8_t last_tx8[8]; uint32_t crc32; } ac_floor_rec_t;
typedef struct AC_PACKED { ac_rec_hdr_t h; uint8_t device_uuid[16]; uint8_t dev_class, lifecycle, slot_count, quorum_rule_id;
  uint32_t authority_epoch, floor_idx, flags; uint8_t policy_hash[32]; uint8_t slots_digest[32];
  uint8_t ledger_head[64]; uint32_t crc32, rsvd0; } ac_authority_t;
/* journal entry for the NV ledger: one per accepted transition */
typedef struct AC_PACKED { ac_rec_hdr_t h; uint32_t seq; uint8_t action, n_sigs; uint16_t rsvd;
  uint32_t new_floor, new_epoch; uint8_t tx_digest[64]; uint8_t commit_marker[8]; } ac_journal_t;
_Static_assert(sizeof(ac_rec_hdr_t)==8,"hdr");
_Static_assert(sizeof(ac_alg_desc_t)==16,"alg");
_Static_assert(sizeof(ac_slot_t)==48,"slot");
_Static_assert(sizeof(ac_floor_rec_t)==32,"floor");
_Static_assert(sizeof(ac_authority_t)==176,"auth");
_Static_assert(sizeof(ac_journal_t)==96,"journal");
typedef struct AC_PACKED { ac_rec_hdr_t h; uint8_t action, n_sigs; uint16_t rsvd; uint8_t target_hash16[16];
  uint32_t new_floor, new_epoch, expect_epoch; uint8_t manifest_digest[64]; } ac_tx_t;
_Static_assert(sizeof(ac_tx_t)==104,"tx");

/* Append-only state journal over an abstract write-once-to-0 flash HAL.
   Two erase pages used ping-pong; fixed-size records; a record is valid iff its
   trailing SHA-256-derived digest matches. See P_prototype.md for the argument. */
#ifndef FS_JOURNAL_H
#define FS_JOURNAL_H
#include "fs_core.h"

#define FS_REC_PAYLOAD 132u
#define FS_REC_DIGEST  16u
#define FS_REC_LEN     (FS_REC_PAYLOAD + FS_REC_DIGEST)   /* 148, multiple of 4 */

/* The whole HAL. prog() may only clear bits (new = old & data), addr and n are
   multiples of 4. erase() sets one page to 0xFF. Any call may fail (power loss). */
typedef struct fs_flash {
    void     *ctx;
    uint32_t  page_size;
    int (*read) (void *ctx, uint32_t addr, uint8_t *dst, uint32_t n);
    int (*prog) (void *ctx, uint32_t addr, const uint8_t *src, uint32_t n);
    int (*erase)(void *ctx, uint32_t page_addr);
} fs_flash;

typedef struct {
    const fs_flash *fl;
    uint32_t base[2];
    uint16_t nslots;      /* records per page = page_size / FS_REC_LEN */
    uint8_t  cur;         /* page holding the newest valid record */
    uint16_t next;        /* next free record index in cur (== nslots: page full) */
    uint32_t last_epoch;
} fs_journal;

fs_err fs_journal_format(fs_journal *j, const fs_flash *fl, uint32_t base0, uint32_t base1,
                         const fs_state *genesis);
fs_err fs_journal_open(fs_journal *j, const fs_flash *fl, uint32_t base0, uint32_t base1,
                       fs_state *out);
fs_err fs_journal_commit(fs_journal *j, const fs_state *next);

/* Convenience: evaluate a command against *st and, if accepted, commit it durably and
   then update *st. On any failure *st is unchanged. */
fs_err fs_apply_command(fs_journal *j, fs_state *st, const uint8_t msg[FS_CMD_LEN],
                        const uint8_t *bundle, size_t bundle_len);
#endif

/* Frozen data layouts shared by the admission code, the kernel and the waist (waist v1).
 * A layout here changes only with a new waist major version (docs/decisions/ADR-041). */
#ifndef AC_TYPES_H
#define AC_TYPES_H
#include <stdint.h>

typedef struct { uint32_t w[8]; } ac_tbl_t;           /* 256-bit monotone truth table over 8 atoms */
typedef struct { uint8_t h[32]; } ac_key_hash_t;      /* SHA-256 of a public key */
typedef struct { ac_tbl_t t; ac_tbl_t c; } ac_tbl_dual_t;   /* table and its bitwise complement (REQ-NV-01) */

#endif

#ifndef FS_QUORUM_H
#define FS_QUORUM_H
#include <stdint.h>

/* Assumption classes (bitset, 16 bits; 8 assigned). Membership means "forging a
   signature of this algorithm is believed to require breaking at least this assumption". */
#define AC_HASH_SHA2        0x0001u
#define AC_HASH_KECCAK      0x0002u
#define AC_LATTICE_STRUCT   0x0004u
#define AC_CLASSICAL_DL     0x0008u
#define AC_CLASSICAL_FACT   0x0010u
#define AC_CODE_BASED       0x0020u
#define AC_MULTIVARIATE     0x0040u
#define AC_RESERVED7        0x0080u

/* A set of signers is a valid quorum iff n >= 1, every member's assumption set is
   non-empty, and the sets are pairwise disjoint. (For n == 1 the disjointness
   condition is vacuous.) No loops over more than n elements, no allocation. */
int fs_quorum_valid(const uint16_t *sets, unsigned n);
#endif

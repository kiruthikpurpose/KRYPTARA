/* LMS signature verification, RFC 8554, SHA-256 / M32. Parameter sets built in:
   LMS H5,H10 x LM-OTS W4,W8. Verification only. Constant stack, no heap. */
#ifndef FS_LMS_H
#define FS_LMS_H
#include <stdint.h>
#include <stddef.h>

#define LMS_PUB_LEN 56u

enum { LMS_OK = 0, LMS_E_LEN = -1, LMS_E_TYPE = -2, LMS_E_INDEX = -3, LMS_E_BAD = -4 };

/* wire length of an LMS signature for the types in pub (or -1 if unsupported) */
long lms_sig_len_for_pub(const uint8_t pub[LMS_PUB_LEN]);

/* Verify sig over msg under pub. The signature length must match the parameter
   set exactly (truncated or extended input -> LMS_E_LEN). If q_out != NULL it
   receives the leaf index q once the length/type/index checks pass. */
int lms_verify(const uint8_t pub[LMS_PUB_LEN], const uint8_t *msg, size_t msglen,
               const uint8_t *sig, size_t siglen, uint32_t *q_out);
#endif

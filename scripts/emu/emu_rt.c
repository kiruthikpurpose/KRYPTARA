/* Minimal freestanding runtime for the Unicorn timing harness (scripts/emu/cycles.py).
 * memset is the only libc symbol policy8.c needs (arch_check R5). This is a plain byte loop;
 * a production libc memset (word-wise) would be faster, so memset-heavy paths (ac_tbl_upper's
 * 32-byte clear) are slightly pessimistic here. Its instructions ARE counted in the totals. */
#include <stddef.h>
void *memset(void *d, int c, size_t n) {
    unsigned char *p = d;
    while (n--) *p++ = (unsigned char)c;
    return d;
}
void *memcpy(void *d, const void *s, size_t n) {
    unsigned char *p = d; const unsigned char *q = s;
    while (n--) *p++ = *q++;
    return d;
}

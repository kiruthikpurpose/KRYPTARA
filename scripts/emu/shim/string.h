/* Freestanding shim: zig cc for thumb-freestanding has no libc headers. Declares only what the kernel core uses. */
#ifndef EMU_SHIM_STRING_H
#define EMU_SHIM_STRING_H
#include <stddef.h>
void *memset(void *, int, size_t);
void *memcpy(void *, const void *, size_t);
int memcmp(const void *, const void *, size_t);
#endif

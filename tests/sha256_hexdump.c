/* Tiny harness for the provider conformance suite (item 17, 50-things list): reads all of stdin,
 * hashes it with this repo's own sha256.c, prints the hex digest. Used by
 * scripts/provider_conformance.sh to differentially test this provider against OpenSSL and
 * Python's hashlib on the same byte-identical input. */
#include <stdio.h>
#include "../src/prototypes/c/sha256.h"
#include "../src/prototypes/c/sha256.c"
int main(void) {
    uint8_t buf[65536];
    size_t n = fread(buf, 1, sizeof buf, stdin);
    uint8_t out[32];
    sha256(buf, n, out);
    for (int i = 0; i < 32; i++) printf("%02x", out[i]);
    printf("\n");
    return 0;
}

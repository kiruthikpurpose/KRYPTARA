/* Tests for src/kernel.c. Modes:
 *   kernel_test self                      built-in checks (image commit, unknown action)
 *   kernel_test tiers  < 4 tables         prints, per tier, the 256-bit authorised set, then
 *                                         the result of the single-bit-flip injection sweep
 *   kernel_test chain  < "dom prev pay"   prints one chain digest per input line (hex fields)
 * The tiers and chain modes are driven by models/kernel_check.py, which compares against the
 * Python reference. */
#include <stdio.h>
#include <string.h>
#include "../src/kernel.c"
#include "../src/prototypes/c/sha256.c"

static int unhex(const char *s, uint8_t *o, size_t max) {
    size_t n = 0;
    if (s[0] == '-' && s[1] == 0) return 0;
    while (s[0] && s[1] && n < max) { unsigned v; if (sscanf(s, "%2x", &v) != 1) return -1; o[n++] = (uint8_t)v; s += 2; }
    return (int)n;
}

static int self(void) {
    int bad = 0;
    uint8_t a[32], b[32]; memset(a, 0x11, 32); memset(b, 0x11, 32);
    bad += ac_image_bootable(a, b, 1) != 1;          /* committed digest matches: boots */
    b[31] ^= 1;
    bad += ac_image_bootable(a, b, 1) != 0;          /* OEM-signed but not the activated digest: refused */
    b[31] ^= 1;
    bad += ac_image_bootable(a, b, 0) != 0;          /* no ACTIVATE_IMAGE recorded at all: refused */
    ac_tbl_t t[AC_TIER_N]; for (int i = 0; i < AC_TIER_N; i++) memset(&t[i], 0xff, sizeof t[i]);
    ac_engine_t e; ac_engine_load(&e, t);
    bad += ac_engine_authorise(&e, AC_TIER_N, 0xff) != 0;     /* unknown tier: refused */
    bad += ac_engine_authorise(&e, 1000, 0xff) != 0;
    uint8_t out[32], big[300] = {0};
    bad += ac_chain_hash(out, big, 256, a, big, 0) != -1;    /* over-long domain tag: refused */
    printf("kernel self failures=%d\n", bad);
    return bad;
}

static int tiers(void) {
    ac_tbl_t t[AC_TIER_N];
    for (int i = 0; i < AC_TIER_N; i++)
        for (int w = 7; w >= 0; w--) { unsigned x; if (scanf("%8x", &x) != 1) return 2; t[i].w[w] = x; }
    ac_engine_t e; ac_engine_load(&e, t);
    for (unsigned a = 0; a < AC_TIER_N; a++) {
        ac_tbl_t r; memset(&r, 0, sizeof r);
        for (unsigned S = 0; S < 256; S++) if (ac_engine_authorise(&e, a, (uint8_t)S)) ts(&r, S);
        for (int w = 7; w >= 0; w--) printf("%08x", r.w[w]);
        printf("\n");
    }
    /* Flip every single bit of every stored copy; nothing the clean engine refuses may be authorised. */
    unsigned long flips = 0, widened = 0, undetected = 0;
    for (unsigned tier = 0; tier < AC_TIER_N; tier++)
        for (unsigned copy = 0; copy < 2; copy++)
            for (unsigned bit = 0; bit < 256; bit++) {
                ac_engine_t f = e;
                ac_tbl_t *victim = copy ? &f.tier[tier].c : &f.tier[tier].t;
                victim->w[bit >> 5] ^= 1u << (bit & 31);
                flips++;
                if (ac_tbl_dual_consistent(&f.tier[tier])) undetected++;
                for (unsigned a = 0; a < AC_TIER_N; a++)
                    for (unsigned S = 0; S < 256; S++)
                        if (ac_engine_authorise(&f, a, (uint8_t)S) && !ac_engine_authorise(&e, a, (uint8_t)S)) widened++;
            }
    printf("flips=%lu widened=%lu undetected=%lu\n", flips, widened, undetected);
    return 0;
}

static int chain(void) {
    char d[600], p[80], y[4200];
    while (scanf("%599s %79s %4199s", d, p, y) == 3) {
        uint8_t dom[256], prev[32], pay[2048], out[32];
        int dl = unhex(d, dom, sizeof dom), pl = unhex(p, prev, 32), yl = unhex(y, pay, sizeof pay);
        if (dl < 0 || pl != 32 || yl < 0 || ac_chain_hash(out, dom, (size_t)dl, prev, pay, (size_t)yl)) { printf("ERR\n"); continue; }
        for (int i = 0; i < 32; i++) printf("%02x", out[i]);
        printf("\n");
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "self")) return self();
    if (!strcmp(argv[1], "tiers")) return tiers();
    if (!strcmp(argv[1], "chain")) return chain();
    return 2;
}

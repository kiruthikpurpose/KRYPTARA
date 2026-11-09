/* Vector-driven test of lms.c / fs_core.c. Usage: test_core vectors.txt */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../c/sha256.h"
#include "../c/lms.h"
#include "../c/fs_core.h"

static int fails, passes;
#define CHECK(c, ...) do { if (c) passes++; else { fails++; printf("FAIL: "); printf(__VA_ARGS__); printf("\n"); } } while (0)

static size_t unhex(const char *s, uint8_t *out, size_t max)
{
    size_t n = 0;
    if (s[0] == '-' && (s[1] == 0 || s[1] == '\n')) return 0;
    while (s[0] && s[1] && s[0] != '\n' && n < max) {
        unsigned v; sscanf(s, "%2x", &v); out[n++] = (uint8_t)v; s += 2;
    }
    return n;
}
static fs_err errname(const char *s)
{
    static const struct { const char *n; fs_err e; } t[] = {
        {"OK",FS_OK},{"PARSE",FS_E_PARSE},{"SLOT",FS_E_SLOT},{"KEYHASH",FS_E_KEYHASH},{"SIG",FS_E_SIG},
        {"QUORUM",FS_E_QUORUM},{"POLICY",FS_E_POLICY},{"REPLAY",FS_E_REPLAY},{"FLOOR",FS_E_FLOOR}};
    unsigned i; for (i = 0; i < sizeof t / sizeof t[0]; i++) if (!strcmp(s, t[i].n)) return t[i].e;
    fprintf(stderr, "bad err name %s\n", s); exit(2);
}

static uint8_t pubs[3][56]; static uint16_t cls[3];
static fs_state st;
static void reset(void)
{
    unsigned i; memset(&st, 0, sizeof st); st.epoch = 1; st.floor = 1;
    for (i = 0; i < 3; i++) { st.state[i] = SLOT_ACTIVE; st.cls[i] = cls[i]; sha256(pubs[i], 56, st.hash[i]); }
}

static uint8_t g_pub[56], g_msg[4096], g_sig[8192];

static void exhaustive_lms(const char *name, const uint8_t *msg, size_t ml)
{
    size_t n, i; int bad = 0; uint8_t t[8192]; unsigned long acc = 0;
    long full = lms_sig_len_for_pub(g_pub);
    /* every proper prefix must be rejected with LEN */
    for (n = 0; n < (size_t)full; n++) if (lms_verify(g_pub, msg, ml, g_sig, n, NULL) != LMS_E_LEN) bad++;
    /* extensions rejected */
    memcpy(t, g_sig, (size_t)full); t[full] = 0;
    if (lms_verify(g_pub, msg, ml, t, (size_t)full + 1, NULL) != LMS_E_LEN) bad++;
    CHECK(bad == 0, "%s: truncation/extension accepted (%d)", name, bad);
    /* every single-bit flip of every byte must be rejected (never OK) */
    bad = 0;
    for (i = 0; i < (size_t)full; i++) {
        unsigned b;
        for (b = 0; b < 8; b += 3) {         /* bits 0,3,6 of each byte: 3 * len flips */
            memcpy(t, g_sig, (size_t)full); t[i] ^= (uint8_t)(1u << b);
            if (lms_verify(g_pub, msg, ml, t, (size_t)full, NULL) == LMS_OK) bad++;
            acc++;
        }
    }
    CHECK(bad == 0, "%s: %d bit-flip(s) accepted of %lu", name, bad, acc);
    /* pubkey flips */
    bad = 0;
    for (i = 0; i < 56; i++) { uint8_t p[56]; memcpy(p, g_pub, 56); p[i] ^= 1;
        if (lms_verify(p, msg, ml, g_sig, (size_t)full, NULL) == LMS_OK) bad++; }
    CHECK(bad == 0, "%s: pubkey flip accepted (%d)", name, bad);
}

int main(int argc, char **argv)
{
    static char ln[1 << 17]; FILE *f; char *tok[8]; unsigned nl = 0;
    static uint8_t cmd[64], bun[1 << 14], dg[32];
    if (argc < 2) return 2;
    f = fopen(argv[1], "r"); if (!f) return 2;
    while (fgets(ln, sizeof ln, f)) {
        unsigned nt = 0; char *p = ln; nl++;
        while (nt < 7 && (tok[nt] = strtok(nt ? NULL : p, " \n"))) nt++;
        if (nt == 0) continue;
        if (tok[0][0] == 'K') { unhex(tok[3], pubs[atoi(tok[1])], 56); cls[atoi(tok[1])] = (uint16_t)atoi(tok[2]); }
        else if (tok[0][0] == 'R') reset();
        else if (tok[0][0] == 'L') {
            size_t ml, sl; int r; unhex(tok[3], g_pub, 56);
            ml = unhex(tok[4], g_msg, sizeof g_msg); sl = unhex(tok[5], g_sig, sizeof g_sig);
            r = lms_verify(g_pub, g_msg, ml, g_sig, sl, NULL);
            CHECK((r == LMS_OK) == !strcmp(tok[2], "OK"), "L %s: got %d", tok[1], r);
            if (!strcmp(tok[2], "OK")) exhaustive_lms(tok[1], g_msg, ml);
        } else if (tok[0][0] == 'C') {
            fs_state before = st, nx; fs_err r, want = errname(tok[2]); size_t bl;
            unhex(tok[3], cmd, sizeof cmd); bl = unhex(tok[4], bun, sizeof bun);
            r = fs_command_eval(&st, cmd, bun, bl, &nx);
            CHECK(r == want, "C %s: want %d got %d", tok[1], want, r);
            if (r == FS_OK) {
                CHECK(nx.epoch == before.epoch + 1 && nx.floor >= before.floor, "C %s: epoch/floor", tok[1]);
                st = nx;
            } else CHECK(memcmp(&before, &st, sizeof st) == 0, "C %s: state changed on reject", tok[1]);
        } else if (tok[0][0] == 'I') {
            size_t bl; fs_err r, want = errname(tok[2]);
            unhex(tok[4], dg, 32); bl = unhex(tok[5], bun, sizeof bun);
            r = fs_image_check(&st, (uint32_t)atoi(tok[3]), dg, bun, bl);
            CHECK(r == want, "I %s: want %d got %d", tok[1], want, r);
        }
    }
    printf("test_core: %d passed, %d failed\n", passes, fails);
    return fails != 0;
}

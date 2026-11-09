/* Host-measured timing for the admission TABLE arithmetic in src/policy8.c (monotone-table build,
 * within-bounds check, authorisation lookup, key-install check). This is NOT a measurement of
 * CLM-12 / EXP-19 ("admission takes 3-10ms on M0+ at 64MHz"): that estimate is dominated by
 * hash-based signature verification (LMS/HSS), which is not benchmarked here. This measures only
 * the O(256)-table-scan primitives, on the development host, to replace "no data at all" with a
 * real number for that specific sub-step, explicitly scoped. See docs/specifications/
 * resource-estimates.md and CLM-12 in evidence-register.md for how this fits the larger estimate. */
#include <stdio.h>
#include <time.h>
#include "../src/policy8.c"

static double now_ns(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

int main(void) {
    uint8_t f[3] = {1, 2, 4};
    ac_tbl_t U, L;
    const int N = 200000;
    volatile int sink = 0;

    double t0 = now_ns();
    for (int i = 0; i < N; i++) sink += ac_tbl_upper(&U, f, 3, 2, 0x80, 0);
    double t_upper = (now_ns() - t0) / N;

    /* nf=12 classes, k<=2: matches the "2-fault bounds, 12 classes" case in resource-estimates.md */
    uint8_t f12[12] = {1, 2, 4, 8, 16, 32, 64, 128, 1, 2, 4, 8};
    t0 = now_ns();
    for (int i = 0; i < N; i++) sink += ac_tbl_upper(&U, f12, 12, 2, 0x80, 0);
    double t_upper12 = (now_ns() - t0) / N;

    t0 = now_ns();
    for (int i = 0; i < N; i++) sink += ac_tbl_lower(&L, f, 3, 1, 0, 0);
    double t_lower = (now_ns() - t0) / N;

    t0 = now_ns();
    for (int i = 0; i < N; i++) sink += ac_tbl_within(&U, &U, &L);
    double t_within = (now_ns() - t0) / N;

    t0 = now_ns();
    for (int i = 0; i < N; i++) sink += ac_tbl_authorises(&U, (uint8_t)(i & 0xff));
    double t_auth = (now_ns() - t0) / N;

    t0 = now_ns();
    for (int i = 0; i < N; i++) sink += ac_key_install_authorised(&U, (uint8_t)(i & 0xff), 0x01, 1);
    double t_keyinst = (now_ns() - t0) / N;

    printf("Host timing (dev machine, -O2, N=%d iterations, sink=%d; NOT silicon, NOT including signature verify):\n", N, sink);
    printf("  ac_tbl_upper              (build U, k<=2, nf=3): %8.1f ns/call\n", t_upper);
    printf("  ac_tbl_upper              (build U, k<=2, nf=12):%8.1f ns/call  <- matches resource-estimates.md row\n", t_upper12);
    printf("  ac_tbl_lower              (build L, k<=1, nf=3): %8.1f ns/call\n", t_lower);
    printf("  ac_tbl_within             (bounds check):        %8.1f ns/call\n", t_within);
    printf("  ac_tbl_authorises         (single-bit lookup):   %8.1f ns/call\n", t_auth);
    printf("  ac_key_install_authorised (REQ-LIFE-02 check):   %8.1f ns/call\n", t_keyinst);
    printf("Note: ac_tbl_upper/lower run ONCE per policy provisioning, not per admission decision;\n");
    printf("per-transition cost on the hot path is ac_tbl_authorises (+ ac_key_install_authorised for\n");
    printf("key installs), both O(1) bit tests. The real per-admission wall-clock cost on-device is\n");
    printf("dominated by hash-based signature verification (LMS/HSS), not measured here.\n");
    return 0;
}

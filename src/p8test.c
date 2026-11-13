/* Harness: reads test cases on stdin, prints U, Lo, admission results for cross-checking with Python. */
#include <stdio.h>
#include "policy8.c"
static void rd(ac_tbl_t *t) { for (int i = 0; i < 8; i++) { unsigned x; if (scanf("%x", &x) != 1) x = 0; t->w[i] = x; } }
static void pr(const ac_tbl_t *t) { for (int i = 0; i < 8; i++) printf("%08x", t->w[7 - i]); }
int main(void) {
    unsigned ncase;
    if (scanf("%u", &ncase) != 1) return 1;
    for (unsigned c = 0; c < ncase; c++) {
        unsigned nf, nl, kc, kl, expo, absent; uint8_t f[24] = {0}, l[24] = {0};
        if (scanf("%u %u %u %u %x %x", &nf, &nl, &kc, &kl, &expo, &absent) != 6 || nf > 24 || nl > 24) return 1;
        for (unsigned i = 0; i < nf; i++) { unsigned x; if (scanf("%x", &x) != 1) return 1; f[i] = (uint8_t)x; }
        for (unsigned i = 0; i < nl; i++) { unsigned x; if (scanf("%x", &x) != 1) return 1; l[i] = (uint8_t)x; }
        ac_tbl_t t, U, L; rd(&t);
        int ru = ac_tbl_upper(&U, f, nf, kc, (uint8_t)expo, 0);
        int rl = ac_tbl_lower(&L, l, nl, kl, (uint8_t)absent, 0);
        if (rl) { memset(&L, 0xff, sizeof L); }  /* unsatisfiable: lower = all ones */
        (void)ru;
        pr(&U); printf(" "); pr(&L);
        printf(" %d %d\n", ac_tbl_monotone(&t), ac_tbl_within(&t, &U, &L));
    }
    return 0;
}

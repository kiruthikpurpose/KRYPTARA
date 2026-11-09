/* R2: edge-case probes of policy8.c (unchanged source, included). Each probe prints PASS/FAIL against
 * the intended semantics in THEORY.md. Build: gcc -O1 -fsanitize=undefined -I../G r2_cedge.c -o r2_cedge */
#include <stdio.h>
#include "../../src/policy8.c"

static unsigned popc(const ac_tbl_t *t) { unsigned c = 0; for (int i = 0; i < 8; i++) c += (unsigned)__builtin_popcount(t->w[i]); return c; }
static void up_closure(ac_tbl_t *t, const uint8_t *seeds, unsigned n) {
    memset(t, 0, sizeof *t);
    for (unsigned m = 0; m < 256; m++) for (unsigned s = 0; s < n; s++) if ((seeds[s] & ~m & 0xffu) == 0) { ts(t, m); break; }
}
static void report(const char *name, int ok, const char *detail) { printf("%-4s %-58s %s\n", ok ? "PASS" : "FAIL", name, detail); }

int main(void) {
    ac_tbl_t U, L, t; char buf[160];
    /* A. k = 3 silently computed as k = 2 */
    { uint8_t f[3] = {1, 2, 4}; ac_tbl_upper(&U, f, 3, 3, 0, 0);
      snprintf(buf, sizeof buf, "U({a0,a1,a2}) = %u (must be 0: all three compromised)", tb(&U, 7));
      report("A  k=3 compromise budget", tb(&U, 7) == 0, buf); }
    /* B. fewer classes than k: no union of exactly k exists -> U = everything, even the empty set */
    { uint8_t f[1] = {1}; ac_tbl_upper(&U, f, 1, 2, 0x80, 0); ac_tbl_lower(&L, f, 0, 0, 0, 0);
      memset(&t, 0xff, sizeof t);  /* table that authorises with NO evidence */
      snprintf(buf, sizeof buf, "|U|=%u, U(empty)=%u, all-ones table admitted=%d", popc(&U), tb(&U, 0),
               ac_tbl_monotone(&t) && ac_tbl_within(&t, &U, &L));
      report("B  nf=1 < k=2 (fail-open)", tb(&U, 0) == 0, buf); }
    /* C. empty fault list, k=1: exposure atoms are ignored -> {WIT} alone is 'safe' */
    { ac_tbl_upper(&U, 0, 0, 1, 0x80, 0);
      snprintf(buf, sizeof buf, "U({WIT}) = %u (attacker always has WIT; must be 0)", tb(&U, 0x80));
      report("C  nf=0, k=1, expo=WIT", tb(&U, 0x80) == 0, buf); }
    /* Labels for the reference layout. THEORY: 32-bit word; bits 0-15 assumptions, 16-23 group. */
    const uint32_t H1 = 1u << 0, H2 = 1u << 1, G_OEM = 1u << 16, G_OWN = 1u << 17, G_ESC = 1u << 18, SITE = 1u << 24;
    uint32_t lab32[8] = {H1 | G_OEM, H2 | G_OEM, H1 | G_OWN, H2 | G_OWN, H1 | G_ESC, H2 | G_ESC, SITE, 0};
    /* D. the C API takes uint16_t labels: a 32-bit THEORY word is truncated, group/site classes vanish */
    { uint16_t lab16[8]; for (int i = 0; i < 8; i++) lab16[i] = (uint16_t)lab32[i];   /* what a port would do */
      uint8_t f[24]; unsigned nf = ac_faults_from_labels(f, 24, lab16, 0xff, 0x7f, 0xffff);
      ac_tbl_upper(&U, f, nf, 1, 0x80, 0);
      uint8_t s[1] = {0x03 | 0x80}; up_closure(&t, s, 1);           /* 'OEM1+OEM2+log': ONE group */
      snprintf(buf, sizeof buf, "classes=%u; U({OEM1,OEM2,WIT})=%u -> one-group table passes safety=%d", nf, tb(&U, 0x83),
               (int)((t.w[0] & ~U.w[0]) == 0 && (t.w[4] & ~U.w[4]) == 0 && ac_tbl_within(&t, &U, &(ac_tbl_t){0})));
      report("D  32-bit label word through uint16_t API", tb(&U, 0x83) == 0, buf); }
    /* E. silent truncation at cap */
    { uint16_t lab[8] = {1, 2, 1, 2, 1, 2, 0, 0};  /* families in low bits */
      uint8_t f[24]; unsigned n_full = ac_faults_from_labels(f, 24, lab, 0xff, 0x7f, 0xffff);
      ac_tbl_upper(&U, f, n_full, 1, 0x80, 0); unsigned full = popc(&U);
      unsigned n_cap = ac_faults_from_labels(f, 7, lab, 0xff, 0x7f, 0xffff);
      ac_tbl_upper(&U, f, n_cap, 1, 0x80, 0);
      snprintf(buf, sizeof buf, "classes %u->%u, |U| %u->%u, U({OEM1,OWN1,ESC1,WIT})=%u (family H1 dropped)", n_full, n_cap,
               full, popc(&U), tb(&U, 0x15 | 0x80));
      report("E  cap smaller than class count (no error returned)", n_cap == n_full, buf); }
    /* F. exclusion bitmap is uint16_t: pairs with an index >= 16 cannot be excluded */
    { uint8_t f[18]; for (int i = 0; i < 16; i++) f[i] = (uint8_t)(1u << (i % 8)); f[16] = 0x15; f[17] = 0x2a;
      uint16_t excl[18] = {0}; excl[16] = (uint16_t)(1u << 17);  /* intent: exclude pair (H1,H2); truncates to 0 */
      ac_tbl_upper(&U, f, 18, 2, 0, excl);
      snprintf(buf, sizeof buf, "U(all six custody atoms)=%u (intended 1 when the H1+H2 pair is excluded)", tb(&U, 0x3f));
      report("F  exclusion of pair (16,17)", tb(&U, 0x3f) == 1, buf); }
    /* G. caller forgets the exposure mask: WIT becomes a real barrier */
    { uint16_t lab[8] = {1, 2, 1, 2, 1, 2, 0, 0}; uint8_t f[24];
      unsigned nf = ac_faults_from_labels(f, 24, lab, 0xff, 0x7f, 0xffff);
      ac_tbl_upper(&U, f, nf, 1, 0x00, 0);
      snprintf(buf, sizeof buf, "U({OEM1,WIT})=%u with expo=0 (single key + log 'safe')", tb(&U, 0x81));
      report("G  expo not derived from atom kinds", tb(&U, 0x81) == 0, buf); }
    /* H. a zero (or non-one-hot) group field yields no group class */
    { uint16_t lab[8] = {1, 2, 1, 2, 1, 2, 0, 0}; uint8_t f[24];
      unsigned nf = ac_faults_from_labels(f, 24, lab, 0xff, 0x7f, 0x0003);  /* group field empty */
      ac_tbl_upper(&U, f, nf, 1, 0x80, 0);
      snprintf(buf, sizeof buf, "U({OEM1,OEM2,WIT})=%u (both keys of one group authorise)", tb(&U, 0x83));
      report("H  custody atom without a group label accepted", tb(&U, 0x83) == 0, buf); }
    return 0;
}

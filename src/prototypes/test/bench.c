/* Host timing + SHA-256 compression counts for lms_verify. Build with -DFS_COUNT_COMPRESS. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../c/sha256.h"
#include "../c/lms.h"
static size_t hx(const char *s, uint8_t *o) { size_t n = 0; while (s[0] && s[1] && s[0] != '\n') { unsigned v; sscanf(s, "%2x", &v); o[n++] = (uint8_t)v; s += 2; } return n; }
int main(int argc, char **argv)
{
    static char ln[1 << 17]; static uint8_t pub[56], msg[64], sig[4096]; FILE *f = fopen(argv[1], "r");
    char name[16], lastn[16] = ""; unsigned cnt = 0; unsigned long cmin = 1ul << 60, cmax = 0, csum = 0; double tsum = 0;
    int reps = argc > 2 ? atoi(argv[2]) : 200;
    for (;;) {
        char *a, *b, *c, *d; int have = fgets(ln, sizeof ln, f) != NULL;
        if (have) { sscanf(ln, "%15s", name); }
        if ((!have || strcmp(name, lastn)) && cnt) {
            printf("%-6s n=%u compress/verify min=%lu mean=%.1f max=%lu  host time/verify mean=%.1f us\n", lastn, cnt, cmin, (double)csum / cnt, cmax, tsum / cnt * 1e6);
            cnt = 0; cmin = 1ul << 60; cmax = 0; csum = 0; tsum = 0;
        }
        if (!have) break;
        strcpy(lastn, name);
        a = strtok(ln, " "); b = strtok(NULL, " "); c = strtok(NULL, " "); d = strtok(NULL, " \n"); (void)a;
        hx(b, pub); size_t ml = hx(c, msg), sl = hx(d, sig);
        { struct timespec t0, t1; int r, bad = 0; unsigned long c0;
          fs_compress_count = 0; if (lms_verify(pub, msg, ml, sig, sl, NULL) != LMS_OK) { puts("verify fail"); return 1; }
          c0 = fs_compress_count;
          clock_gettime(CLOCK_MONOTONIC, &t0);
          for (r = 0; r < reps; r++) bad += lms_verify(pub, msg, ml, sig, sl, NULL);
          clock_gettime(CLOCK_MONOTONIC, &t1);
          if (bad) return 1;
          tsum += ((t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9) / reps;
          if (c0 < cmin) cmin = c0; if (c0 > cmax) cmax = c0; csum += c0; cnt++; }
    }
    return 0;
}

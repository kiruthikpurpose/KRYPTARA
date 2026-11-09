#include "fs_quorum.h"

int fs_quorum_valid(const uint16_t *sets, unsigned n)
{
    uint16_t acc = 0;
    unsigned i;
    if (n == 0 || sets == 0) return 0;
    for (i = 0; i < n; i++) {
        if (sets[i] == 0) return 0;
        if (acc & sets[i]) return 0;
        acc = (uint16_t)(acc | sets[i]);
    }
    return 1;
}

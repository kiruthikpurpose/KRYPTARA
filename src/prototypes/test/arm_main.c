/* Link harness only: pulls in the verify path + journal so a linked size can be measured. */
#include "../c/fs_journal.h"
volatile int sink;
static fs_state st; static fs_journal jr; static const fs_flash *flp;
int main(void)
{
    uint8_t dg[32] = {0}, buf[64] = {0};
    sink = fs_image_check(&st, 1, dg, buf, sizeof buf);
    sink += fs_apply_command(&jr, &st, buf, buf, sizeof buf);
    sink += fs_journal_open(&jr, flp, 0, 4096, &st);
    return sink;
}

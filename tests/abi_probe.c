/* Prints every frozen constant and struct layout of waist v1 as name=value lines.
 * scripts/arch_check.py compares the output with src/waist-v1.abi. Needs only the headers. */
#include <stdio.h>
#include <stddef.h>
#include "../src/ac_waist.h"

#define V(x) printf(#x "=%ld\n", (long)(x))
#define SZ(t) printf("sizeof(" #t ")=%zu\n", sizeof(t))
#define OFF(t, f) printf("offsetof(" #t "," #f ")=%zu\n", offsetof(t, f))

int main(void) {
    V(AC_WAIST_VERSION); V(AC_MAX_INTENTS); V(AC_MAX_CLASSES);
    V(AC_OK); V(AC_E_BADMSG); V(AC_E_AUTH); V(AC_E_ADMIT); V(AC_E_HOLDER); V(AC_E_DUPKEY); V(AC_E_HALTED);
    V(AC_E_BUDGET); V(AC_E_BUSY); V(AC_E_NOCLASS); V(AC_E_STATE); V(AC_E_IMAGE);
    V(AC_T0_HALT); V(AC_T1_OPERATE); V(AC_T2_CONST); V(AC_T2_RECOVERY); V(AC_TIER_N);
    V(AC_ACT_HALT); V(AC_ACT_RESUME); V(AC_ACT_ACTIVATE_IMAGE); V(AC_ACT_TIGHTEN_TABLE); V(AC_ACT_ADVANCE_EPOCH);
    V(AC_ACT_RETIRE_SLOT); V(AC_ACT_INSTALL_TABLE); V(AC_ACT_KEY_INSTALL); V(AC_ACT_N);
    V(AC_MSG_BOOT); V(AC_MSG_PROPOSE_TX); V(AC_MSG_HALT);
    V(AC_INT_NONE); V(AC_INT_NV_WRITE_SNAPSHOT); V(AC_INT_BOOT_IMAGE); V(AC_INT_REJECT);
    SZ(ac_tbl_t); SZ(ac_key_hash_t); SZ(ac_tbl_dual_t); SZ(ac_budget_t); SZ(ac_msg_t); SZ(ac_intent_t);
    SZ(ac_effects_t); SZ(ac_engine_t); SZ(ac_ctx_t); SZ(ac_genesis_t);
    OFF(ac_msg_t, kind); OFF(ac_msg_t, action); OFF(ac_msg_t, evidence); OFF(ac_msg_t, atom); OFF(ac_msg_t, bundle);
    OFF(ac_msg_t, tier); OFF(ac_msg_t, digest); OFF(ac_msg_t, table);
    OFF(ac_intent_t, kind); OFF(ac_intent_t, seq); OFF(ac_intent_t, code);
    OFF(ac_effects_t, n); OFF(ac_effects_t, it);
    OFF(ac_budget_t, t); OFF(ac_budget_t, s); OFF(ac_budget_t, nfc); OFF(ac_budget_t, nfl); OFF(ac_budget_t, xc_a);
    OFF(ac_budget_t, xl_b); OFF(ac_budget_t, fc); OFF(ac_budget_t, fl);
    OFF(ac_ctx_t, version); OFF(ac_ctx_t, present); OFF(ac_ctx_t, kinds); OFF(ac_ctx_t, key_present); OFF(ac_ctx_t, key);
    OFF(ac_ctx_t, eng); OFF(ac_ctx_t, bud); OFF(ac_ctx_t, action_tier); OFF(ac_ctx_t, halted); OFF(ac_ctx_t, halt_budget);
    OFF(ac_ctx_t, halt_used); OFF(ac_ctx_t, epoch); OFF(ac_ctx_t, have_commit); OFF(ac_ctx_t, committed);
    OFF(ac_ctx_t, head); OFF(ac_ctx_t, seq); OFF(ac_ctx_t, acked);
    return 0;
}

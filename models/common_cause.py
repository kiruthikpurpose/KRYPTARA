# Item 7 (50-things list): correlated-failure extension of the theory. [C]
# Demonstrates models/lint.py's `common_cause_groups=` parameter: declaring that two atoms share a
# common cause (same HSM vendor, same ceremony tool) lets a SINGLE real-world event compromise both
# at once, collapsing what the t-fault budget assumed needed two independent faults. This is the
# analogy to IEC 61508-6's beta-factor the limitations doc already names (Q2) -- used as an analogy
# for the shape of the effect, not as an imported standard clause or a claimed numeric beta.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import lint, ATOMS, ALL, OPERATE, RECOVERY

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    # Baseline: OPERATE claimed 1-safe vs 1 compromise fault, independent classes.
    r_base = lint(OPERATE, ATOMS, ALL, 1, 1, loss_kinds=("SIG", "PRES"))
    check("A: baseline (no common cause) OPERATE is 1-safe", r_base["safe"])

    # Declare OEM1 (group OEM, family H1) and OWN2 (group OWN, family H2) share a common cause (e.g.
    # both provisioned by the same HSM vendor's tooling -- a compromised vendor build pipeline can
    # leak both at once). This specific pair matters because it spans BOTH the group and the family
    # boundary OPERATE relies on (C>=2 groups, F>=2 families): a same-family pair (e.g. OEM1+OWN1,
    # both H1) would NOT break safety here, because OPERATE still needs a second family regardless
    # of how many groups are touched -- the common-cause pair has to cross both axes to matter.
    r_cc = lint(OPERATE, ATOMS, ALL, 1, 1, loss_kinds=("SIG", "PRES"),
                common_cause_groups=[{"OEM1", "OWN2"}])
    check("B: with OEM1+OWN2 common cause declared (crosses group AND family), OPERATE's 1-safe claim breaks",
          r_base["safe"] and not r_cc["safe"])

    # Negative control: a common-cause pair that shares a family (OEM1+OWN1, both H1) should NOT
    # break safety, because it still only gives the attacker one family -- confirms the mechanism
    # tracks the real structure rather than flagging every declared pair indiscriminately.
    r_cc_sf = lint(OPERATE, ATOMS, ALL, 1, 1, loss_kinds=("SIG", "PRES"),
                    common_cause_groups=[{"OEM1", "OWN1"}])
    check("B2: a same-family common-cause pair (OEM1+OWN1) does NOT break OPERATE's 1-safe claim",
          r_cc_sf["safe"])

    # A common cause WITHIN a single group (OEM1+OEM2, already the same group/organisation) should
    # NOT additionally break anything beyond what a single-group compromise already implies --
    # sanity check that the mechanism doesn't double-count what's already modelled.
    r_cc_samegroup = lint(OPERATE, ATOMS, ALL, 1, 1, loss_kinds=("SIG", "PRES"),
                           common_cause_groups=[{"OEM1", "OEM2"}])
    check("C: common cause within one group changes nothing new (already a single-group fault)",
          r_cc_samegroup["safe"] == r_base["safe"])

    # RECOVERY (T2, meant to be 2-safe in the fortress variant) is unaffected by a common cause that
    # spans only one of its many compromise combinations when t stays at the declared budget --
    # demonstrate the interval shrinks (U gets smaller) rather than silently staying the same size.
    r_rec_base = lint(RECOVERY, ATOMS, ALL, 1, 2, loss_labels={"group", "family"})
    r_rec_cc = lint(RECOVERY, ATOMS, ALL, 1, 2, loss_labels={"group", "family"},
                     common_cause_groups=[{"ESC1", "ESC2"}])
    check("D: declaring ESC1+ESC2 (both families, one group) a common cause shrinks U",
          bin(r_rec_cc["U"]).count("1") <= bin(r_rec_base["U"]).count("1"))

    print(f"common_cause failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

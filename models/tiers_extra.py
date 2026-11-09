# Extra tier checks used in the blueprint. [C]
from lint import *
NANO_T2 = tbl(lambda m: p(m) and K(m) >= 1 and w(m))
r = lint(NANO_T2, ATOMS, NANO, 1, 2, loss_labels={"group"}, loss_kinds=("SIG",))
print("nano T2 = p & K>=1 & w : 1-safe incl. hash break:", r['safe'], "| live vs any 2 key/group losses:", r['live'])
r = lint(NANO_T2, ATOMS, NANO, 2, 0)
print("nano T2 double-fault safe?:", r['safe'], "(expected False: site insider + any custodian)")
HALT2 = tbl(lambda m: K(m) >= 1 or p(m))
print("HALT = K>=1 or p : monotone", all(not (HALT2>>m)&1 or all((HALT2>>(m|1<<i))&1 for i in range(8)) for m in range(256)),
      "popcount", bin(HALT2).count('1'))
# Full-control paths: if T1 may re-key a group without its participation, the effective safety of full control is T1's.
# Fortress option only helps if re-keying requires the 2-safe constitution table.
for name, t1, t2 in [("recoverable", OPERATE, RECOVERY), ("fortress", OPERATE, CONST)]:
    r1 = lint(t1, ATOMS, ALL, 2, 0); r2 = lint(t2, ATOMS, ALL, 2, 0)
    print(f"{name:11s}: T1 2-safe={r1['safe']}  T2 2-safe={r2['safe']}  -> full-control 2-safe only if re-key lives in T2 and T2 is 2-safe: {r2['safe']}")
# terrestrial T1 after sovereign exit (OEM atoms retired): what budget remains?
AFTER_EXIT = ALL - {"OEM1", "OEM2"}
for title, s_kw in [("live vs key loss", dict(loss_labels=set())), ("live vs group loss", dict(loss_labels={"group"}))]:
    r = lint(OPERATE, ATOMS, AFTER_EXIT, 1, 1, **s_kw)
    print(f"after sovereign exit, T1 OPERATE: 1-safe={r['safe']} {title}={r['live']}")

# REQ-TIER-02 (D-24): "re-keying a group lives in exactly one tier per profile." Operationalised as
# two conjuncts, both must hold for every profile below, else the design lets T1 re-key a group on
# its own authority -- the exact failure mode F-R2-03/REQ-LIFE-02 exists to close:
#   (a) T1 alone is never 2-safe (cannot itself be a site of full control: if it were, "the tier
#       where re-key lives" would be ambiguous between T1 and T2);
#   (b) T1 cannot be escalated to T2's authority by rotating a key inside T1's own labels without
#       the slot holder's co-signature (tests/redteam_r2/r2_paths.py's `rotate` flag, closed by
#       REQ-LIFE-02's ac_key_install_authorised / Repl3OK).
print("\nREQ-TIER-02 check (re-keying lives in exactly one tier per profile):")
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tests", "redteam_r2"))
import r2_paths as rp
req_tier_02_failures = 0
for name, t1, t2 in [("recoverable", OPERATE, RECOVERY), ("fortress", OPERATE, CONST)]:
    r1 = lint(t1, ATOMS, ALL, 2, 0)
    a_ok = not r1["safe"]   # (a): T1 is never itself a site of full control
    cuts_with_rotate, _ = rp.min_cuts(rp.BASE, t1, t2, rp.CUST, rotate=True)
    cuts_without_rotate, _ = rp.min_cuts(rp.BASE, t1, t2, rp.CUST, rotate=False)
    # (b): enforcing REQ-LIFE-02 (rotate=False) must never make full control EASIER to reach than
    # allowing unco-signed rotation did (fewer fault classes needed), and ideally makes it harder
    # or impossible (cuts_without_rotate is None, or strictly larger).
    b_ok = (cuts_without_rotate is None) or (cuts_with_rotate is not None and cuts_without_rotate >= cuts_with_rotate)
    print(f"  {name:11s}: T1 2-safe={r1['safe']} (want False) | min-cut to full control WITH rotation={cuts_with_rotate}, "
          f"WITHOUT (REQ-LIFE-02 enforced)={cuts_without_rotate}")
    if not (a_ok and b_ok):
        req_tier_02_failures += 1
print(f"REQ-TIER-02 failures={req_tier_02_failures}")
if req_tier_02_failures:
    sys.exit(1)

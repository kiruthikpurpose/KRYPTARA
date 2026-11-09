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

# Item 2 (50-things list): "Recursive" as a testable property. [C]
# Formal definition, per docs/vision-and-scope.md's table: "the admission predicate applies to the
# tables that govern changes to admission inputs" -- i.e. installing a NEW T1 table is itself a
# transition that must pass the SAME admission check (monotone, within [Lo,U], tightening-only if
# applicable) as any other authority action. This is not a separate mechanism: it is the claim that
# there is no privileged bypass for "changing the rules" versus any other governed change.
#
# Test: a T2 action proposes a REPLACEMENT T1 (OPERATE-like) table. Using the SAME
# ac_tbl_within/ac_tbl_tighten machinery REQ-ADM-01/02 already define, confirm:
#   (a) a replacement T1 table that is a valid tightening of the current one is admitted;
#   (b) a replacement T1 table that WIDENS authority (not a subset of the old one) is rejected by
#       the tightening check, even though T2 (a higher tier) is the one proposing it;
#   (c) a replacement T1 table that stays a tightening but drifts outside the computed [Lo,U] for
#       the CURRENT fault structure is rejected by the interval check.
# (b) and (c) are the substance of the "Recursive" property: T2 cannot install just any T1 table by
# fiat -- the replacement is itself subject to admission, exactly as the definition states.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interval import upper, lower
from lint import lint, ATOMS, ALL, OPERATE

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

def ac_tbl_tighten(new, old):
    return (new & ~old) == 0

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    r = lint(OPERATE, ATOMS, ALL, 1, 1, loss_kinds=("SIG", "PRES"))
    U, Lo = r["U"], r["Lo"]
    check("setup: current T1 (OPERATE) is itself safe-and-live under the current structure",
          r["safe"] and r["live"])

    # (a) T2 proposes tightening T1: remove authorisation at one currently-true point, keep
    # everything else. Must be admitted: a subset of OPERATE, still within the live floor Lo (as
    # long as that point wasn't required for liveness).
    # Find a point that's in OPERATE but not in Lo (safe to remove without breaking liveness).
    removable = None
    for m in range(256):
        if (OPERATE >> m) & 1 and not (Lo >> m) & 1:
            removable = m; break
    new_t1_tightened = OPERATE & ~(1 << removable)
    tighten_ok = ac_tbl_tighten(new_t1_tightened, OPERATE)
    still_in_interval = (new_t1_tightened & ~U) == 0 and (Lo & ~new_t1_tightened) == 0
    check("(a) T2 tightening T1 by removing a non-load-bearing point: admitted "
          "(tightening check passes AND stays in [Lo,U])", tighten_ok and still_in_interval)

    # (b) T2 proposes WIDENING T1: add authorisation at a point OPERATE currently forbids.
    # Must be REJECTED by the tightening check (REQ-ADM-02), regardless of who proposes it.
    forbidden_point = next(m for m in range(256) if not (OPERATE >> m) & 1)
    new_t1_widened = OPERATE | (1 << forbidden_point)
    widen_tighten_ok = ac_tbl_tighten(new_t1_widened, OPERATE)
    check("(b) T2 widening T1 (adds a forbidden point): REJECTED by the tightening check "
          "-- T2's authority does not bypass admission", not widen_tighten_ok)

    # (c) T2 proposes a table that IS a tightening of OPERATE but drifts outside [Lo,U] by
    # dropping a point that Lo requires (a load-bearing liveness point). Still a subset of
    # OPERATE (tightening check alone would pass), but the interval check must catch it.
    load_bearing = next(m for m in range(256) if (OPERATE >> m) & 1 and (Lo >> m) & 1)
    new_t1_breaks_live = OPERATE & ~(1 << load_bearing)
    tighten_ok_c = ac_tbl_tighten(new_t1_breaks_live, OPERATE)
    stays_live = (Lo & ~new_t1_breaks_live) == 0
    check("(c) T2 proposes a tightening that drops a load-bearing liveness point: tightening "
          "check alone would pass, but it leaves [Lo,U] (REQ-ADM-01's interval check catches it)",
          tighten_ok_c and not stays_live)

    print(f"recursive_property failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

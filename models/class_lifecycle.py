# REQ-LIFE-01 (ADR-011, D-31), second half: "DECLARE_CLASS_DEAD MUST be a T1 tightening; >= t+s+1
# live classes MUST be kept per tier." [C]
# The class-count law itself (>= t+s+1) is already exhaustively verified in models/interval.py [3]
# (0 disagreements over brute-force search). This closes the remaining, previously-"partial" half:
# that retiring a class is (a) only ever a tightening (new table a subset of old, via the existing
# project()/tighten machinery) and (b) refused outright if it would drop live classes below t+s+1,
# rather than silently producing an unsafe table.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import project, present_mask, ATOMS, OPERATE

def tighten_ok(new_table, old_table):
    """f_new <= f_old, bitwise (REQ-ADM-02's rule, reused here for DECLARE_CLASS_DEAD)."""
    return (new_table & ~old_table) == 0

def declare_class_dead(table, atoms, present, dying_class_atoms, t, s):
    """Models DECLARE_CLASS_DEAD: remove dying_class_atoms from `present`, project the table onto
    the smaller atom set (REQ-ADM-05's canonical form), and check both halves of REQ-LIFE-01.
    Returns (authorised, new_table_or_None, reason)."""
    new_present = present - dying_class_atoms
    live_classes = len(new_present)   # one class == one atom in this reference layout
    if live_classes < t + s + 1:
        return False, None, f"would leave {live_classes} live classes, need >= {t+s+1}"
    new_table = project(table, present_mask(atoms, new_present))
    if not tighten_ok(new_table, table):
        return False, None, "not a tightening (should be structurally impossible via project(), checked anyway)"
    return True, new_table, "ok"

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    ALL = {a.name for a in ATOMS}
    # A: declaring one class dead when plenty remain (t=1,s=1 -> need >=3; ALL has 8) is authorised
    # and the result is a genuine tightening of OPERATE.
    ok, new_t, reason = declare_class_dead(OPERATE, ATOMS, ALL, {"OEM1"}, 1, 1)
    check("A: plenty of classes remain -> authorised", ok)
    check("A: result is a tightening of the original table", ok and tighten_ok(new_t, OPERATE))
    check("A: result equals the canonical projection (REQ-ADM-05 compatible)",
          ok and new_t == project(OPERATE, present_mask(ATOMS, ALL - {"OEM1"})))

    # B: declaring classes dead until only t+s live classes remain (one short) must be refused
    t, s = 1, 1
    present = set(list(ALL)[: t + s])   # exactly t+s classes, one short of t+s+1
    ok2, new_t2, reason2 = declare_class_dead(OPERATE, ATOMS, present, {next(iter(present))}, t, s)
    check("B: dropping below t+s+1 is refused", not ok2)
    check("B: refusal leaves no table installed", new_t2 is None)

    # C: declaring a class dead that keeps exactly t+s+1 live classes is the boundary -- authorised
    present3 = set(list(ALL)[: t + s + 2])  # t+s+2 classes present, drop one -> t+s+1 remain
    dying = {list(present3)[0]}
    ok3, new_t3, reason3 = declare_class_dead(OPERATE, ATOMS, present3, dying, t, s)
    check("C: boundary case (exactly t+s+1 remain) is authorised", ok3)

    print(f"REQ-LIFE-01 (DECLARE_CLASS_DEAD half) failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

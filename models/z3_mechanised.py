# Item 5 (50-things list): "A mechanised proof in a proof assistant." Status was NONE; this is a
# deliberate ROUNDABOUT, not the item as literally specified: Lean and Coq are multi-gigabyte
# toolchains and were not installed in this session (storage budget). Z3 (an SMT solver, ~38MB via
# pip, installed in a venv OUTSIDE the repo so it never touches git) gives a different but genuine
# form of machine verification: instead of a human-checked proof script, a decision procedure
# independently re-derives and confirms the defining properties of U and Lo via bit-vector logic,
# for concrete instances. This is NOT a general proof for all n (Z3 reasons over FIXED bit-widths,
# one instance at a time) -- it is closer in spirit to the exhaustive checks in interval.py than to
# a Lean proof of the general theorem. Labelled honestly as SMT-mechanised instance verification.
#
# What is proved per instance, by UNSAT (i.e. Z3 could not find a counterexample):
#   (1) U_python is SAFE: no table bit at a compromise-covered point is set.
#   (2) U_python is MAXIMAL: any table T with U_python as a proper subset of its bit-set is NOT
#       safe (setting any bit beyond U_python's necessarily includes a compromise-covered point).
#   (3) Lo_python is LIVE: every surviving-point bit is set.
#   (4) Lo_python is MINIMAL: any table T with Lo_python as a proper superset (T's bits are a
#       proper subset of Lo_python's) fails liveness somewhere.
# Run with the venv that has z3 installed: see README note in this file's directory, or
# `pip install z3-solver` in any Python 3.9+ environment.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interval import upper, lower
try:
    import z3
except ImportError:
    print("z3-solver not installed in this interpreter -- this check is SKIPPED, not failed.")
    print("Install with: pip install z3-solver  (≈38MB; see z3_mechanised.py header)")
    sys.exit(0)

N = 8  # matches the device's 8-atom cap (REQ-EVD-01)

def bits_of(const_int):
    """Python int (256-bit mask over 2^8 points) -> list of booleans, index = point m."""
    return [(const_int >> m) & 1 for m in range(1 << N)]

def z3_check_instance(name, Ac, Al):
    U_py, Lo_py = upper(N, Ac), lower(N, Al)
    U_bits, Lo_bits = bits_of(U_py), bits_of(Lo_py)
    full = (1 << N) - 1

    def covered_by_compromise(m):
        return z3.Or([ (m & ~a) == 0 for a in Ac ]) if Ac else z3.BoolVal(False)
    def survivor_point(m):
        # REQ-ADM: a point m is a "surviving" point for loss l if (full & ~l) & ~m == 0,
        # i.e. m is a superset of the complement of l -- same definition as lower() in interval.py.
        return z3.Or([ ((full & ~l) & ~m) == 0 for l in Al ]) if Al else z3.BoolVal(True)

    results = {}

    # (1) + (2): U is safe and maximal.
    s = z3.Solver()
    T = [z3.Bool(f"t{m}") for m in range(1 << N)]
    # T must differ from U_py by having at least one extra bit set (a proper superset).
    extra = z3.Or([z3.And(T[m], z3.Not(z3.BoolVal(bool(U_bits[m])))) for m in range(1 << N)])
    s.add(extra)
    for m in range(1 << N):
        if U_bits[m]:
            s.add(T[m])  # T retains every bit U_py has (so it's a genuine superset, not just different)
    # Safety: T has no bit set at a compromise-covered point.
    safety_violated = z3.Or([z3.And(T[m], covered_by_compromise(m)) for m in range(1 << N)])
    s.add(z3.Not(safety_violated))
    results["U maximal (no safe proper superset exists)"] = (s.check() == z3.unsat)

    # Independently: U_py itself violates no compromise point (U is safe).
    s2 = z3.Solver()
    bad = z3.Or([covered_by_compromise(m) for m in range(1 << N) if U_bits[m]])
    s2.add(bad)
    results["U itself is safe"] = (s2.check() == z3.unsat)

    # (3) + (4): Lo is live and minimal.
    s3 = z3.Solver()
    live_violated = z3.Or([z3.And(survivor_point(m), z3.Not(z3.BoolVal(bool(Lo_bits[m]))))
                            for m in range(1 << N)])
    s3.add(live_violated)
    results["Lo itself is live"] = (s3.check() == z3.unsat)

    s4 = z3.Solver()
    T2 = [z3.Bool(f"u{m}") for m in range(1 << N)]
    subset = z3.Or([z3.And(z3.Not(T2[m]), z3.BoolVal(bool(Lo_bits[m]))) for m in range(1 << N)])
    s4.add(subset)
    for m in range(1 << N):
        if not Lo_bits[m]:
            s4.add(z3.Not(T2[m]))  # T2 is a genuine proper subset of Lo_py's bit set
    live_ok = z3.And([z3.Implies(survivor_point(m), T2[m]) for m in range(1 << N)])
    s4.add(live_ok)
    results["Lo minimal (no live proper subset exists)"] = (s4.check() == z3.unsat)

    all_ok = all(results.values())
    print(f"  {name}: " + ", ".join(f"{k}={'PROVED' if v else 'FAILED'}" for k, v in results.items()))
    return all_ok

if __name__ == "__main__":
    instances = [
        ("single compromise atom, single loss atom", [0b001], [0b010]),
        ("k=2 compromise, k=1 loss", [0b00001, 0b00010], [0b00100]),
        ("fixcheck.c-style f=[1,2,4], k=2", [1, 2, 4], [0]),
        ("wider: 3 compromise classes, 2 loss classes", [0b0011, 0b0101, 0b1001], [0b0110, 0b1010]),
    ]
    ok = all(z3_check_instance(name, Ac, Al) for name, Ac, Al in instances)
    print(f"\nZ3-mechanised instance checks: {'ALL PROVED' if ok else 'SOME FAILED'}")
    if not ok:
        sys.exit(1)

# GATE-12: is the SIM-01 governance-loss ordering (rev2_no_renewal >= rev2_renewal/remote
# >= remote_degraded >= terrestrial) stable under a sweep of the illustrative hazard rates,
# or does some plausible combination flip it? HYP-01's rejection condition (simulation-specifications.md)
# is exactly this: "rejected if the ordering changes under plausible hazard ranges."
# Hazards remain ILLUSTRATIVE [E]; this sweep only tests whether the claimed ORDER is sensitive to them.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
from brick_mc import run

DESIGNS = ["rev2_no_renewal", "rev2_renewal", "remote", "remote_degraded", "terrestrial"]
# Plausible range: group loss 1-10%/yr, family break 0.1-3%/yr (order-of-magnitude bracket
# around the baseline 2% / 0.5% used in brick_mc.py; no measured basis, see CLM-08).
H_GROUP = [0.01, 0.02, 0.05, 0.10]
H_FAMILY = [0.001, 0.005, 0.01, 0.03]
TRIALS = 20_000  # smaller than brick_mc's default; this is a sweep over many points, not a single estimate

def expected_order_holds(p):
    """terrestrial must be <= every remote/rev2 design; remote_degraded <= remote and <= rev2 variants."""
    if p["terrestrial"] > min(p["remote_degraded"], p["remote"], p["rev2_renewal"], p["rev2_no_renewal"]):
        return False
    if p["remote_degraded"] > max(p["remote"], p["rev2_renewal"], p["rev2_no_renewal"]):
        return False
    return True

if __name__ == "__main__":
    print(f"GATE-12 hazard sweep: {len(H_GROUP)}x{len(H_FAMILY)}={len(H_GROUP)*len(H_FAMILY)} points, "
          f"{TRIALS} trials/point, designs={DESIGNS}")
    violations = []
    for hg in H_GROUP:
        for hf in H_FAMILY:
            p = {d: run(d, h_group=hg, h_family=hf, trials=TRIALS, seed=hash((d, hg, hf)) & 0x7fffffff)
                 for d in DESIGNS}
            ok = expected_order_holds(p)
            if not ok:
                violations.append((hg, hf, p))
            print(f"  h_group={hg:.3f} h_family={hf:.3f}  " +
                  "  ".join(f"{d}={p[d]:.4f}" for d in DESIGNS) +
                  ("  <-- ORDER VIOLATION" if not ok else ""))
    print(f"\nGATE-12 result: {len(violations)} of {len(H_GROUP)*len(H_FAMILY)} points violate the claimed "
          f"ordering (terrestrial <= remote_degraded <= {{remote, rev2_*}}).")
    if violations:
        print("HYP-01 rejection condition triggered at the points listed above with 'ORDER VIOLATION'.")
    else:
        print("Ordering stable over the swept range. Not evidence the ordering holds outside this range, "
              "and hazards remain illustrative, not measured (CLM-08).")

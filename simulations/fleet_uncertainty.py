# CLM-08 extension: the single-point Monte Carlo in models/brick_mc.py answers "what is P(loss) at
# ONE guessed hazard rate". It says nothing about how much that answer moves if the guess is wrong.
# This propagates PARAMETER uncertainty: draw (h_group, h_family) from a distribution around the
# illustrative baseline, run a small Monte Carlo at each draw, and report the resulting distribution
# of P(loss) per design -- a confidence interval on the claim, not a single number.
# Hazards remain ILLUSTRATIVE [E]; this only quantifies sensitivity to that illustrative choice.
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
from brick_mc import run

DESIGNS = ["rev2_no_renewal", "rev2_renewal", "remote", "remote_degraded", "terrestrial"]
QUICK = "--quick" in sys.argv
N_DRAWS = 20 if QUICK else 200          # parameter-uncertainty draws
TRIALS_PER_DRAW = 300 if QUICK else 1500  # full run: 200*1500*5=1.5M device-trials (~5 min); quick: ~15s
BASE_GROUP, BASE_FAMILY = 0.02, 0.005   # same baseline as brick_mc.py's headline numbers

def draw_hazards(rng):
    """Log-normal jitter around baseline: models 'we guessed the rate within a factor of ~2-3x',
    not a fixed point value. Rejected if negative/absurd (log-normal can't go negative anyway)."""
    hg = BASE_GROUP * rng.lognormal(mean=0.0, sigma=0.5)
    hf = BASE_FAMILY * rng.lognormal(mean=0.0, sigma=0.5)
    return float(hg), float(hf)

def main(out_csv):
    rng = np.random.default_rng(20261109)
    rows = []
    for draw_id in range(N_DRAWS):
        hg, hf = draw_hazards(rng)
        seed = int(rng.integers(0, 2**31 - 1))
        for d in DESIGNS:
            p = run(d, h_group=hg, h_family=hf, trials=TRIALS_PER_DRAW, seed=seed)
            rows.append(dict(draw_id=draw_id, design=d, h_group=hg, h_family=hf, p_loss=p))
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["draw_id", "design", "h_group", "h_family", "p_loss"])
        w.writeheader(); w.writerows(rows)
    return rows

def summarize(rows):
    print(f"{'design':18s} {'mean':>8s} {'p5':>8s} {'p50':>8s} {'p95':>8s}  (over {N_DRAWS} hazard draws, "
          f"h_group~lognormal({BASE_GROUP}), h_family~lognormal({BASE_FAMILY}), sigma=0.5)")
    for d in DESIGNS:
        vals = np.array([r["p_loss"] for r in rows if r["design"] == d])
        print(f"  {d:16s} {vals.mean():8.4f} {np.percentile(vals,5):8.4f} "
              f"{np.percentile(vals,50):8.4f} {np.percentile(vals,95):8.4f}")
    # does the ordering (terrestrial best, rev2_no_renewal worst) hold in EVERY draw, not just on average?
    by_draw = {}
    for r in rows: by_draw.setdefault(r["draw_id"], {})[r["design"]] = r["p_loss"]
    order_violations = sum(1 for d in by_draw.values()
                            if not (d["terrestrial"] <= d["remote_degraded"] <= min(d["remote"], d["rev2_renewal"], d["rev2_no_renewal"]) + 1e-12))
    print(f"\nOrdering holds in {N_DRAWS - order_violations}/{N_DRAWS} individual hazard draws "
          f"(not just on average) -- {'CLM-08 ordering is robust to parameter uncertainty' if order_violations == 0 else 'ordering is NOT fully robust, see violating draws'}.")

if __name__ == "__main__":
    name = "fleet_uncertainty_quick.csv" if QUICK else "fleet_uncertainty.csv"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", name)
    rows = main(out)
    summarize(rows)
    print(f"\nDataset written: {out} ({len(rows)} rows, {os.path.getsize(out)/1024:.1f} KiB)")

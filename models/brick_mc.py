# X-E5: probability that a device's governance becomes permanently unusable over its life,
# under custody-group loss and hash-family breaks, for several governance designs. [C]
# Hazards are ILLUSTRATIVE [E]; the comparison between designs is the result, not the absolute numbers.
import random

def caps(design, g, f):
    """(can_act, can_renew_group, can_renew_family) for g live groups (of 3) and f live families (of 2)."""
    atoms = g * f
    if design == "rev2_no_renewal":   ok = g >= 2 and f >= 2; return ok, False, False
    if design == "rev2_renewal":      ok = g >= 2 and f >= 2; return ok, ok, ok
    if design == "remote":            ok = g >= 2 and f >= 2; return ok, ok, False
    if design == "remote_degraded":   ok = g >= 2;            return ok, ok, ok
    if design == "terrestrial":       ok = atoms >= 2;        return ok, ok, ok   # T2: presence + 2 custody atoms
    raise ValueError(design)

def run(design, years=40, h_group=0.02, h_family=0.005, d_group=1.0, d_family=3.0, trials=200_000, seed=1):
    rng = random.Random(seed); dead = 0; dt = 0.25; steps = int(years / dt)
    for _ in range(trials):
        g, f = 3, 2; pg, pf = [], []
        for s in range(steps):
            t = s * dt
            lost_g = sum(rng.random() < h_group * dt for _ in range(g)); g -= lost_g; pg += [t + d_group] * lost_g
            lost_f = sum(rng.random() < h_family * dt for _ in range(f)); f -= lost_f; pf += [t + d_family] * lost_f
            if g <= 0 or f <= 0: dead += 1; break
            can_act, rg, rf = caps(design, g, f)
            if not can_act: dead += 1; break
            due = [x for x in pg if x <= t]; pg = [x for x in pg if x > t]
            if rg: g = min(3, g + len(due))
            else:  pg += [x + dt for x in due]
            due = [x for x in pf if x <= t]; pf = [x for x in pf if x > t]
            if rf: f = min(2, f + len(due))
            else:  pf += [x + dt for x in due]
    return dead / trials

if __name__ == "__main__":
    designs = ["rev2_no_renewal", "rev2_renewal", "remote", "remote_degraded", "terrestrial"]
    print("P(governance permanently lost within 40 years) [group loss 2%/yr each, family break 0.5%/yr each; renewal 1 yr / 3 yr]")
    for d in designs: print(f"  {d:18s} {run(d):.4f}")
    print("Group loss 5%/yr:")
    for d in designs: print(f"  {d:18s} {run(d, h_group=0.05, trials=100_000):.4f}")
    print("Family break 2%/yr:")
    for d in designs: print(f"  {d:18s} {run(d, h_family=0.02, trials=100_000):.4f}")

# Theorem 3 cross-check (closes the gap docs/theory/proofs.md names at its own end): brute-force
# verification that for ANY set of authority paths g, each individually satisfying Theorem 2's
# bound t(g)+s(g) <= k-1 over the same k classes, the derived t_eff=min t(g), s_max=max s(g)
# satisfy t_eff + s_max <= k-1, exactly as Theorem 3 claims -- and that this is TIGHT (there exist
# path sets achieving equality), confirming the bound is not merely true but exact.
import itertools

def check(k, max_paths=4):
    # Enumerate every (t,s) pair individually satisfying Theorem 2's existence bound for this k.
    valid_pairs = [(t, s) for t in range(0, k) for s in range(0, k) if t + s <= k - 1]
    violations = 0
    tight_examples = 0
    checked = 0
    for n_paths in range(1, max_paths + 1):
        for paths in itertools.combinations_with_replacement(valid_pairs, n_paths):
            t_eff = min(t for t, s in paths)
            s_max = max(s for t, s in paths)
            checked += 1
            if t_eff + s_max > k - 1:
                violations += 1
                print(f"  VIOLATION at k={k}: paths={paths} -> t_eff={t_eff}, s_max={s_max}, "
                      f"sum={t_eff+s_max} > k-1={k-1}")
            elif t_eff + s_max == k - 1:
                tight_examples += 1
    return checked, violations, tight_examples

if __name__ == "__main__":
    total_checked = total_violations = total_tight = 0
    for k in range(1, 7):
        checked, violations, tight = check(k)
        total_checked += checked
        total_violations += violations
        total_tight += tight
        print(f"k={k}: {checked} path-set combinations checked, {violations} violations, "
              f"{tight} achieve equality (bound is tight)")
    print(f"\nTotal: {total_checked} combinations, {total_violations} violations, "
          f"{total_tight} tight (equality) examples across k=1..6")
    if total_violations:
        raise SystemExit(1)
    if total_tight == 0:
        print("WARNING: bound was never tight in this sweep -- cannot confirm it's exact, only an upper bound")
        raise SystemExit(1)

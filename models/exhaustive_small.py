# Item 4 (50-things list): exhaustive, not random, verification for small structures.
# models/interval.py already enumerates ALL monotone Boolean functions exactly for n<=6
# (all_monotone(), a known Dedekind-number construction -- not sampled). What WAS still sampled
# (400 random draws) was the fault structures (Ac, Al) tested against them. This closes that gap:
# for n=3 and n=4, enumerate EVERY (Ac, Al) pair with |Ac|,|Al| in {0,1,2} -- matching the real
# system's k<=2 cap in src/policy8.c's ac_tbl_upper/lower, so this isn't an arbitrary restriction,
# it's exhaustive over exactly what the implementation supports -- and check brute-force admission
# against the interval formula for every one, over every monotone function.
import sys, os, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from policy_study import all_monotone
from interval import upper, lower, brute, interval_mask, q2_mixed

def all_fault_structures(n, maxk=2):
    """Every Ac (or Al): a list of 0, 1, or 2 nonempty subsets of n atoms."""
    subsets = list(range(1, 1 << n))  # nonempty subsets only (empty fault class is meaningless)
    structures = [[0]]  # k=0: no fault classes (upper()/lower() treat this as the free/absent bits)
    structures += [[s] for s in subsets]
    structures += [[s1, s2] for s1, s2 in itertools.combinations(subsets, 2)]
    return structures

def run(n):
    T = all_monotone(n)
    structures = all_fault_structures(n)
    total = 0
    mismatches = 0
    for Ac in structures:
        U = upper(n, Ac)
        for Al in structures:
            Lo = lower(n, Al)
            ok = brute(T, n, Ac, Al)
            iv = interval_mask(T, U, Lo)
            exists_claim = q2_mixed(n, Ac, Al)
            exists_actual = bool(ok.any())
            total += 1
            if (ok != iv).any() or exists_claim != exists_actual:
                mismatches += 1
    return total, mismatches, len(T)

if __name__ == "__main__":
    grand_total = 0
    grand_bad = 0
    for n in (3, 4):
        total, mismatches, num_monotone = run(n)
        print(f"n={n}: {num_monotone} monotone functions (exhaustive) x {total} fault-structure pairs "
              f"(exhaustive, |Ac|,|Al| in {{0,1,2}}, matching policy8.c's k<=2 cap) "
              f"= {total * num_monotone:,} (table, Ac, Al) checks; mismatches={mismatches}")
        grand_total += total
        grand_bad += mismatches
    print(f"\nTotal structure-pairs checked exhaustively: {grand_total:,}; mismatches={grand_bad}")
    if grand_bad:
        raise SystemExit(1)

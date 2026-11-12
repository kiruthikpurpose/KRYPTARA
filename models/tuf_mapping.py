# Item 36 (50-things list): mapping TUF roles onto evidence atoms, and where the kernel is stricter. [C]
# TUF (The Update Framework) authorises each role (root, targets, snapshot, timestamp) by a
# threshold: any k of n listed keys. A threshold is a monotone policy, so it can be expressed as a
# kernel table exactly. What TUF does not do is say which faults the keys share. Feeding the same
# threshold to the label-aware lint shows when "2 of 3" is really "1 of 1".
# This is an interoperability check of the policy shape only; no TUF metadata is parsed here.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import Atom, lint, tbl

def threshold(k, n):
    return tbl(lambda m: bin(m & ((1 << n) - 1)).count("1") >= k)

def root_keys(families, groups):
    return [Atom(f"ROOT{i}", "SIG", [f"group:{g}", f"family:{f}"])
            for i, (f, g) in enumerate(zip(families, groups))]

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    T = threshold(2, 3)
    names = {"ROOT0", "ROOT1", "ROOT2"}

    # A: what TUF assumes -- three independent keys. 2-of-3 is safe vs 1 compromise, live vs 1 loss.
    a = root_keys(["F1", "F2", "F3"], ["A", "B", "C"])
    r = lint(T, a, names, 1, 1, loss_labels={"group"})
    check("A: 2-of-3 over keys with distinct groups and algorithms is 1-safe and 1-loss-live", r["safe"] and r["live"])

    # B: common deployment -- three keys, one organisation, one algorithm. The group label makes
    # all three one fault class: one organisational compromise yields all three keys.
    b = root_keys(["F1", "F1", "F1"], ["A", "A", "A"])
    r = lint(T, b, names, 1, 1, loss_labels={"group"})
    check("B: 2-of-3 with all keys in one organisation is NOT 1-safe", not r["safe"])

    # C: three organisations but one signature algorithm: an algorithm break yields all three.
    c = root_keys(["F1", "F1", "F1"], ["A", "B", "C"])
    r = lint(T, c, names, 1, 1, loss_labels={"group"})
    check("C: 2-of-3 across three organisations but one algorithm is NOT 1-safe (algorithm break)", not r["safe"])

    # D: the interval check says no threshold over three keys can be both 2-safe and 1-loss-live,
    # which is Theorem 2 (k >= t+s+1) applied to TUF's root role.
    r = lint(T, a, names, 2, 1, loss_labels={"group"})
    check("D: no policy over three independent keys is 2-safe and 1-loss-live (Theorem 2)", not r["exists"])

    print(f"tuf_mapping failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

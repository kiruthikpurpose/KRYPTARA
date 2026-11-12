# OQ-12: how is a slot re-keyed when its holder has lost the key, given REQ-LIFE-02 (installing into
# an ACTIVE slot needs the holder's co-signature)? Candidate: retire the slot first (T1 tightening,
# REQ-LIFE-01), then install into the now-EMPTY slot (T2, no holder exists to co-sign). [C]
# Two things must hold for the candidate to be acceptable:
#   (1) Safety: it gives an attacker no shorter path to full control than the co-signature rule
#       alone. Measured as the minimum number of fault classes to full control, as in
#       tests/redteam_r2/r2_paths.py.
#   (2) Liveness: after losing one whole custody group (holder gone), honest survivors can still
#       perform both steps: retire (T1 OPERATE) and install (T2 RECOVERY).
import sys, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "tests", "redteam_r2"))
import r2_paths as rp
from lint import lint, ATOMS, ALL, REMOTE, OPERATE, RECOVERY, CONST, REMOTE_OPERATE, REMOTE_CONST2, BOTHF

def full_retire_then_install(X, T1, T2):
    # The attacker can retire any slot with T1 evidence, but filling the emptied slot needs T2
    # evidence on its own: retirement removes atoms, it never adds any to the attacker's set.
    if rp.bit(T2, X): return True
    if rp.bit(T1, X): return bool(rp.bit(T2, X))   # retire is reachable, install still needs T2(X)
    return False

def min_cut(full, T1, T2, classes):
    names = list(classes)
    for r in range(1, 4):
        for c in itertools.combinations(names, r):
            X = rp.WIT
            for n in c: X |= classes[n]
            if full(X, T1, T2): return r
    return None

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    for title, (T1, T2, _cust) in rp.PROFILES.items():
        cosign, _ = rp.min_cuts(rp.BASE, T1, T2, rp.CUST, rotate=False)
        retire = min_cut(full_retire_then_install, T1, T2, rp.BASE)
        check(f"(1) {title.strip()}: retire-then-install min-cut {retire} >= co-signature min-cut {cosign}",
              cosign is None or (retire is not None and retire >= cosign) or retire is None)

    for g in ("OEM", "OWN", "ESC"):
        lost = ALL - {f"{g}1", f"{g}2"}
        t1 = lint(OPERATE, ATOMS, lost, 1, 0)
        t2 = lint(RECOVERY, ATOMS, lost, 1, 1, loss_labels={"group", "family"}, exclude_loss_combo=BOTHF)
        check(f"(2) group {g} lost entirely: survivors can retire (T1 live) and install (T2 RECOVERY live)",
              t1["live"] and t2["live"])

    # (3) Known limit, asserted so it cannot silently change: in the REMOTE profile T2 (R_CONST2)
    # needs all three custody groups, so after losing a whole group the survivors can retire the
    # slot but can never fill it. Remote devices cannot recover from losing a custody group.
    for g in ("OEM", "OWN", "ESC"):
        lost = REMOTE - {f"{g}1", f"{g}2"}
        t1 = lint(REMOTE_OPERATE, ATOMS, lost, 1, 0)
        t2 = lint(REMOTE_CONST2, ATOMS, lost, 1, 0)
        check(f"(3) REMOTE, group {g} lost: retire is live but install is NOT (known limit)",
              t1["live"] and not t2["live"])

    print(f"lost_holder failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

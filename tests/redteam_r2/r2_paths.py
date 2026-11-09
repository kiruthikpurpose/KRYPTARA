# R2 red-team: end-to-end "all paths to full control" analysis of the tier design. [C]
# Atoms: 0 OEM1(H1) 1 OEM2(H2) 2 OWN1(H1) 3 OWN2(H2) 4 ESC1(H1) 5 ESC2(H2) 6 PRES 7 WIT
# Model: attacker evidence X = union of compromised classes | WIT (exposure is free).
#  * If T2(X): full control (re-key + re-label).
#  * If T1(X) and T1 may "rotate a key inside its labels" / "owner transfer" WITHOUT the slot holder's
#    signature (THEORY.md 4 does not require it), the attacker installs own keys in every ACTIVE custody
#    slot (labels unchanged; the attacker simply generates fresh H1/H2 keys): X |= custody atoms.
#  * Variant FIX: rotation/transfer of slot i also needs slot i's current key -> no closure gain.
#    REQ-LIFE-02 now enforces this FIX: `ac_key_install_authorised` (src/policy8.c) and `Repl3OK`
#    (simulations/tla/FirstStage.tla) both require the slot's own holder atom/signature for an ACTIVE
#    slot. `rotate=True` below is kept only to show the vulnerability the fix closes, not a live option.
import itertools, sys
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),"..","..","models"))
from lint import OPERATE, CONST, RECOVERY, REMOTE_OPERATE, REMOTE_CONST2, NANO_PRES_OPERATE

OEM, OWN, ESC = 0b11, 0b1100, 0b110000
H1, H2 = 0b010101, 0b101010
PRES, WIT, CUST = 1 << 6, 1 << 7, 0b111111
def bit(t, m): return (t >> m) & 1

BASE = {f"key:{n}": 1 << i for i, n in enumerate(["OEM1", "OEM2", "OWN1", "OWN2", "ESC1", "ESC2"])}
BASE.update({"grp:OEM": OEM, "grp:OWN": OWN, "grp:ESC": ESC, "fam:H1": H1, "fam:H2": H2, "PRES": PRES})
CORR = {"OWNER-runs-site(OWN+PRES)": OWN | PRES,      # owner insider: owner keys + site access
        "OEM-board(OEM+PRES)": OEM | PRES}             # OEM/CM-level presence assertion (test mode, implant)

PROFILES = {
    "TERR recoverable (T1=OPERATE,T2=RECOVERY)": (OPERATE, RECOVERY, CUST),
    "TERR fortress    (T1=OPERATE,T2=CONST)": (OPERATE, CONST, CUST),
    "REMOTE           (T1=R_OPERATE,T2=R_CONST2)": (REMOTE_OPERATE, REMOTE_CONST2, CUST),
}

def full(X, T1, T2, cust, rotate):
    if bit(T2, X): return True
    if rotate and bit(T1, X): return bool(bit(T2, X | cust))
    return False

def min_cuts(classes, T1, T2, cust, rotate, maxr=3):
    names = list(classes)
    found = []
    for r in range(1, maxr + 1):
        for c in itertools.combinations(names, r):
            if any(set(f) <= set(c) for f in found): continue
            X = WIT
            for n in c: X |= classes[n]
            if full(X, T1, T2, cust, rotate): found.append(c)
        if found: return r, found
    return None, []

if __name__ == "__main__":
    print("Minimum number of fault classes giving FULL CONTROL (T2 directly, or T1 -> rotate -> T2)")
    for title, (T1, T2, cust) in PROFILES.items():
        for model, cl in [("declared classes", BASE), ("+ correlated presence", {**BASE, **CORR})]:
            for rotate in (True, False):
                r, cuts = min_cuts(cl, T1, T2, cust, rotate)
                tag = "rotation w/o holder" if rotate else "FIX: holder co-signs"
                ex = "; ".join("+".join(c) for c in cuts[:4])
                print(f"  {title:44s} {model:22s} {tag:20s} min={r}  e.g. {ex}")
    # T2 alone (what the per-tier lint certifies) vs end-to-end
    print("\nREMOTE: T2 table alone vs end-to-end (claimed 'safe vs any 2 except both families')")
    cl = BASE
    for c in itertools.combinations(cl, 2):
        if set(c) == {"fam:H1", "fam:H2"}: continue
        X = WIT
        for n in c: X |= cl[n]
        if not bit(REMOTE_CONST2, X) and full(X, REMOTE_OPERATE, REMOTE_CONST2, CUST, True):
            print("  2-fault break via T1 rotation:", " + ".join(c)); break
    # Covert (no WIT) minimal authorised sets per table
    print("\nMinimal authorised sets WITHOUT the publicity atom (acts that need not be public):")
    names = ["OEM1", "OEM2", "OWN1", "OWN2", "ESC1", "ESC2", "PRES", "WIT"]
    def minimal(t):
        ms = [m for m in range(256) if bit(t, m)]
        return [m for m in ms if not any(bit(t, m & ~(1 << i)) for i in range(8) if m >> i & 1)]
    for n, t in [("OPERATE", OPERATE), ("RECOVERY", RECOVERY), ("CONST", CONST),
                 ("R_OPERATE", REMOTE_OPERATE), ("R_CONST2", REMOTE_CONST2)]:
        cov = [m for m in minimal(t) if not m & WIT]
        print(f"  {n:9s} covert minimal sets: {len(cov):3d}" +
              (f"  e.g. {{{','.join(names[i] for i in range(8) if cov[0] >> i & 1)}}}" if cov else ""))
    # After a hash-family break: what stands between the attacker and T2?
    print("\nAfter a family break (attacker holds all H1 keys + WIT):")
    for title, (T1, T2, cust) in PROFILES.items():
        X = H1 | WIT
        print(f"  {title:44s} T1={bool(bit(T1, X))} T2={bool(bit(T2, X))} T2 with +PRES={bool(bit(T2, X | PRES))}"
              f"  T1 with +PRES={bool(bit(T1, X | PRES))}")
    X = 0b010101 | WIT  # nano: all custody atoms are H1
    print(f"  NANO+P (T1=p&C>=2) family break: T1={bool(bit(NANO_PRES_OPERATE, X))} with +PRES={bool(bit(NANO_PRES_OPERATE, X | PRES))}")

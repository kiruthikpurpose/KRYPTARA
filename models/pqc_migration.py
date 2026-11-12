# PQC migration as class retirement: a worked schedule checked against the tier budgets. [C]
# Starting point: three custody groups, each holding one classical (ECC) key and one hash-based
# (H1) key. Target: each group's ECC key replaced by a second hash family (H2) before the classical
# family's retirement date. NIST IR 8547 (final 2026-10-27, per secondary sources; re-verify against
# the NIST page before citing) deprecates quantum-vulnerable public-key algorithms after 2030 and
# disallows them after 2035; those two years are used as the label-retirement dates.
# Two orders are compared at every step with the reference tables and budgets from lint.py:
#   swap-in-place : replace one group's ECC key by an H2 key per step (holder co-signs, REQ-LIFE-02)
#   retire-first  : declare the ECC class dead, then install H2 keys afterwards
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import Atom, lint, OPERATE, CONST, RECOVERY

DEPRECATED_AFTER, DISALLOWED_AFTER = 2030, 2035
GROUPS = ["OEM", "OWN", "ESC"]

def layout(second_family):
    """second_family: dict group -> 'ECC' | 'H2' | None (slot empty)."""
    atoms, present = [], set()
    for g in GROUPS:
        atoms.append(Atom(f"{g}1", "SIG", [f"group:{g}", "family:H1"])); present.add(f"{g}1")
        fam = second_family[g]
        atoms.append(Atom(f"{g}2", "SIG", [f"group:{g}", f"family:{fam or 'NONE'}"]))
        if fam: present.add(f"{g}2")
    atoms += [Atom("PRES", "PRES", ["site:S"]), Atom("WIT", "WIT", ["log:L"])]
    return atoms, present | {"PRES", "WIT"}

def budgets(atoms, present):
    fams = sorted({l for a in atoms if a.name in present for l in a.labels if l.startswith("family:")})
    # The reference RECOVERY budget excludes the loss of both families. While three families
    # coexist mid-swap, the same exclusion is applied to every pair of whole families; losing H1
    # together with one second-slot family leaves a single key (reported below as a finding).
    both = list(itertools.combinations(fams, 2))
    return {
        "T1 OPERATE (1,1)": lint(OPERATE, atoms, present, 1, 1, loss_kinds=("SIG", "PRES")),
        "T2 CONST (2,1)": lint(CONST, atoms, present, 2, 1, loss_labels={"group"}),
        "T2 RECOVERY (1,2)": lint(RECOVERY, atoms, present, 1, 2, loss_labels={"group", "family"},
                                  exclude_loss_combo=both),
    }

def ok(r): return r["safe"] and r["live"]

SWAP = [(2026, "start: ECC + H1 in every group", dict(OEM="ECC", OWN="ECC", ESC="ECC")),
        (2027, "OEM swaps ECC -> H2", dict(OEM="H2", OWN="ECC", ESC="ECC")),
        (2028, "OWN swaps ECC -> H2", dict(OEM="H2", OWN="H2", ESC="ECC")),
        (2029, "ESC swaps ECC -> H2", dict(OEM="H2", OWN="H2", ESC="H2"))]
RETIRE_FIRST = [(2026, "start: ECC + H1 in every group", dict(OEM="ECC", OWN="ECC", ESC="ECC")),
                (2027, "ECC class declared dead, slots empty", dict(OEM=None, OWN=None, ESC=None)),
                (2028, "OEM installs H2", dict(OEM="H2", OWN=None, ESC=None)),
                (2029, "OWN installs H2", dict(OEM="H2", OWN="H2", ESC=None)),
                (2030, "ESC installs H2", dict(OEM="H2", OWN="H2", ESC="H2"))]

def run(name, schedule):
    print(f"{name}:")
    below = []
    for year, what, fams in schedule:
        atoms, present = layout(fams)
        res = budgets(atoms, present)
        status = "  ".join(f"{k}: {'ok' if ok(r) else 'BELOW BUDGET'}" for k, r in res.items())
        print(f"  {year} {what:40s} {status}")
        if not all(ok(r) for r in res.values()): below.append(year)
        if len({f for f in fams.values() if f}) == 2:
            print(f"       note: three families coexist; recovery is not live if H1 and a second-slot family are both lost")
    last_ecc = max((y for y, _, f in schedule if "ECC" in f.values()), default=None)
    return below, last_ecc

if __name__ == "__main__":
    swap_below, swap_last = run("swap-in-place", SWAP)
    ret_below, ret_last = run("retire-first", RETIRE_FIRST)
    failures = 0
    def check(name, cond):
        global failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        failures += not cond
    print("checks:")
    check("swap-in-place keeps every tier within budget at every step (two-whole-family losses excluded, as in the steady state)", not swap_below)
    check("retire-first drops below budget during the gap", bool(ret_below))
    check(f"swap-in-place uses no ECC key after {DEPRECATED_AFTER} (last year with ECC: {swap_last})",
          swap_last <= DEPRECATED_AFTER < DISALLOWED_AFTER)
    print(f"pqc_migration failures={failures}; retire-first below budget in {ret_below}")
    sys.exit(1 if failures else 0)

# Item 46 (50-things list): a second, non-PQC application domain, to test HYP-07 ("the kernel
# generalises beyond update/authority governance"). [C]
# Domain chosen: WebPKI-style root Certificate Authority key governance -- a real, well-documented
# long-lived governance problem (root CA ceremonies already use multi-party physical quorums,
# Certificate Transparency already uses public logs) that is NOT a device/update problem at all,
# unlike every other worked example in this repo. If the SAME admission math (models/lint.py,
# models/interval.py) produces sensible tiers for this domain without new theory, that is evidence
# for HYP-07; if it has to be stretched or doesn't fit, that is evidence against, and is reported
# honestly either way below.
#
# Mapping:
#   Atoms   -> root-key custodians (e.g. 3 independent HSM-key holders: the CA operator, an
#              auditor/trustee, and an independent root-program representative), each in two
#              "families" (two independent root-signing algorithms held by each party, the CA
#              equivalent of two hash families) -- mirrors the OEM/OWN/ESC x H1/H2 layout exactly.
#   PRES    -> physical ceremony attendance (real root CA ceremonies ARE conducted in a physical,
#              witnessed, audited room -- this is not a stretch, it is how WebPKI root ceremonies
#              already work).
#   WIT     -> publication to a Certificate Transparency log (a real, existing, independent log
#              network -- arguably a BETTER fit for the WIT atom than this repo's own target
#              domain, where witness log infrastructure does not exist yet).
#   T1 (OPERATE) -> routine intermediate CA cross-signing / policy-constrained issuance.
#   T2 (CONST/RECOVERY) -> root re-key or root policy change (the rare, ceremony-gated action).
#
# Where it STRAINS (reported honestly, not hidden): there is no "image" or "boot" concept in CA
# governance at all -- REQ-IMG-01 and the staged-effect halt machinery (REQ-HALT-01) have no
# analogue here. The chain/record model (REQ-CHAIN-01) maps well (CT logs already ARE a hash
# chain with inclusion proofs). DECLARE_CLASS_DEAD maps awkwardly: a CA "retiring" an algorithm
# class looks more like deprecating a root than retiring a custodian, a different lifecycle shape
# than this repo's "a custody group's key died" framing.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import Atom, lint, tbl

CA_ATOMS = [
    Atom("OPERATOR1", "SIG", ["group:OPERATOR", "family:RSA"]),
    Atom("OPERATOR2", "SIG", ["group:OPERATOR", "family:ECDSA"]),
    Atom("AUDITOR1",  "SIG", ["group:AUDITOR",  "family:RSA"]),
    Atom("AUDITOR2",  "SIG", ["group:AUDITOR",  "family:ECDSA"]),
    Atom("ROOTPROG1", "SIG", ["group:ROOTPROG", "family:RSA"]),
    Atom("ROOTPROG2", "SIG", ["group:ROOTPROG", "family:ECDSA"]),
    Atom("CEREMONY",  "PRES", ["site:ceremony-room"]),
    Atom("CTLOG",     "WIT",  ["log:certificate-transparency"]),
]
GROUPS = [0b11, 0b1100, 0b110000]; FAMS = [0b010101, 0b101010]; SITE = 1 << 6; LOG = 1 << 7
def C(m): return sum(1 for g in GROUPS if m & g)
def F(m): return sum(1 for f in FAMS if m & f)
def K(m): return bin(m & 0b111111).count("1")
def p(m): return bool(m & SITE)
def w(m): return bool(m & LOG)

# T1: routine cross-signing/issuance within policy -- 2 custodian groups + CT log publication.
CA_OPERATE = tbl(lambda m: w(m) and C(m) >= 2 and F(m) >= 2)
# T2: root re-key / root policy change -- same shape as the device domain's RECOVERY (lint.py):
# ceremony presence + at least 2 surviving custodian KEYS (not necessarily 2 distinct GROUPS --
# that is exactly what makes it tolerate losing a whole group, same as the device domain), backed
# by either the CT log or a second surviving group.
CA_ROOT_CEREMONY = tbl(lambda m: p(m) and K(m) >= 2 and (w(m) or C(m) >= 2))

ALL = {a.name for a in CA_ATOMS}

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    r1 = lint(CA_OPERATE, CA_ATOMS, ALL, 1, 1, loss_labels={"group"})
    check("A: routine issuance is 1-safe, live vs 1 custodian loss", r1["safe"] and r1["live"])

    r2 = lint(CA_ROOT_CEREMONY, CA_ATOMS, ALL, 1, 2, loss_labels={"group", "family"},
              exclude_loss_combo=[("family:RSA", "family:ECDSA")])
    check("B: root ceremony is 1-safe, live vs any 2 losses except both algorithm families", r2["safe"] and r2["live"])

    # The exact same impossibility the device domain has: 2-safe AND live vs any single loss is
    # unreachable -- same Theorem-2-driven ceiling, different domain, same arithmetic.
    r3 = lint(CA_ROOT_CEREMONY, CA_ATOMS, ALL, 2, 1, loss_labels={"group"})
    check("C: 2-safe root ceremony is NOT simultaneously live vs 1 loss (same impossibility as the device domain)",
          not (r3["safe"] and r3["live"] and r3["exists"]))

    print(f"second_domain (CA root governance) failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

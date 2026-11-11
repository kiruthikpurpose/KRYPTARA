# Gateway pattern reference lint (item 33, 50-things completion list; see
# docs/architecture/gateway-pattern.md for the prose this file backs). [C]
#
# Question this file answers formally, reusing the EXISTING admission math (models/lint.py,
# models/interval.py) with no new theory: when a device cannot host the kernel and sits behind a
# gateway (docs/architecture/mechanisms.md §6.16, ADR-035), what evidence can the fleet actually
# rely on for claims ABOUT that fronted device, and what is lost relative to the device running the
# kernel natively?
#
# Two atom roles, used throughout docs/architecture/gateway-pattern.md:
#   HOLD  -- the gateway itself holds the key/secret and asserts on the fronted device's behalf.
#            Modelled as a SIG atom labelled "group:GATEWAY", using the SAME group-label convention
#            models/lint.py already uses for OEM1/OEM2 etc: atoms sharing a group label are treated
#            as compromised TOGETHER by a single fault against that label, because they live in one
#            administrative/physical entity. For a gateway that entity is the gateway process
#            itself, so gateway-process compromise is a direct, unmediated compromise of every HOLD
#            atom's evidence -- no new mechanism needed, just an honest label.
#   RELAY -- the device holds its own key or signal and the gateway only carries it through
#            unmodified (it cannot forge what it cannot compute). Modelled as an atom in a group
#            the gateway's own common-cause declaration does NOT cover.
# A signal that LOOKS like presence (a technician report, a relayed contact-closure state) but is
# not sampled by a locked stage per REQ-PRES-01 (firmware-independent input, sampled at reset, before
# any second-stage code runs) MUST NOT be declared as a PRES-kind atom. It is modelled here as WIT:
# exposure only, per the existing rule that WIT atoms are always available to the attacker for free
# (mathematical-foundations.md §3.8, "Exposure(f) <=> f <= x_WIT"). That is not a weaker version of
# presence; it is a different evidence kind with none of PRES's independence property (CLM-09), and
# the tests below show the gap concretely rather than asserting it in prose.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import Atom, lint, tbl

GATEWAY_ATOMS = [
    Atom("GW_HOLD1",       "SIG", ["group:GATEWAY", "family:H1"]),   # held BY the gateway
    Atom("GW_HOLD2",       "SIG", ["group:GATEWAY", "family:H2"]),   # held BY the gateway
    Atom("DEV_OWN",        "SIG", ["group:DEVICE"]),                 # held by the device; gateway only relays
    Atom("GW_RELAY_SIGNAL","WIT", ["log:relay-presence"]),           # relayed presence-LIKE signal: WIT, not PRES
    Atom("GW_WIT",         "WIT", ["log:fleet"]),                    # genuine witnessed-receipt publication
]
GWGROUP = 0b11            # bits 0-1: the two gateway-held key shares
DEVBIT  = 1 << 2          # device-held key, independent of the gateway process
RELAYBIT = 1 << 3         # relayed presence-like signal (WIT kind -- see module docstring)
WITBIT  = 1 << 4          # genuine witness receipt

def gw_keys(m): return bin(m & GWGROUP).count("1")
def dev_present(m): return bool(m & DEVBIT)
def relay(m): return bool(m & RELAYBIT)
def wit(m): return bool(m & WITBIT)

# Claim about the fronted device, evidenced only by what the gateway itself holds.
FRONTED_ASSERT = tbl(lambda m: wit(m) and gw_keys(m) >= 2)
# Same claim, strengthened by one genuine device-rooted key the gateway cannot forge.
FRONTED_ASSERT_WITH_DEVKEY = tbl(lambda m: wit(m) and gw_keys(m) >= 1 and dev_present(m))
# A table that mistakes a relayed presence-like signal for real presence (the error this file
# exists to make impossible to miss: see test D).
BAD_TABLE_TREATING_RELAY_AS_PRESENCE = tbl(lambda m: relay(m) and wit(m))

ALL = {a.name for a in GATEWAY_ATOMS}


def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    # A. Naive (WRONG) analysis: treat the gateway's two key shares as independent singleton
    #    faults only, by excluding the shared "group:GATEWAY" label from the fault set
    #    (comp_labels=set() -- no group-level fault generated, atom-level only). FRONTED_ASSERT
    #    requires both keys, so under this (incorrect) independence assumption a single
    #    compromised key is not enough -- it looks 1-safe.
    rA = lint(FRONTED_ASSERT, GATEWAY_ATOMS, ALL, 1, 0, loss_labels=set(), comp_labels=set())
    check("A: FRONTED_ASSERT looks 1-safe if the gateway's two keys are (wrongly) treated as independent",
          rA["safe"])

    # B. Honest analysis, using the framework's OWN existing convention: both key shares carry the
    #    label "group:GATEWAY" (exactly how OEM1/OEM2 carry "group:OEM" in the reference 8-atom
    #    layout, models/lint.py), so by DEFAULT (comp_labels=None, nothing special requested) a
    #    single compromise of that one label already yields both bits at once -- because both keys
    #    live in the one gateway process, same as any other single administrative/physical entity
    #    in this framework. Re-run the SAME table, SAME t=1: it is now UNSAFE. This is the formal
    #    content of "a compromised gateway can lie about every device behind it" -- one fault, not
    #    two, and the framework already says so once the labels are honest about what the gateway is.
    rB = lint(FRONTED_ASSERT, GATEWAY_ATOMS, ALL, 1, 0, loss_labels=set())
    check("B: the SAME table is unsafe under the framework's own default (honest) group-label semantics",
          not rB["safe"])

    # C. Restoring one independent, device-rooted key (DEV_OWN, a different label group that the
    #    gateway never holds) is enough to make the honest analysis safe again. This is the formal
    #    case for "relay what the device itself can still assert; do not let the gateway stand in
    #    for it" -- the central recommendation of docs/architecture/gateway-pattern.md.
    rC = lint(FRONTED_ASSERT_WITH_DEVKEY, GATEWAY_ATOMS, ALL, 1, 0, loss_labels=set())
    check("C: adding one gateway-independent device-held key restores safety under the same honest analysis",
          rC["safe"])

    # D. The sharpest check: a table that mistakes a relayed presence-like signal for real
    #    presence is not merely weaker than one that uses a real PRES atom -- it is unsafe even
    #    against a ZERO-fault attacker (t=0, s=0), because WIT-kind atoms are always free to the
    #    attacker (exposure only, mathematical-foundations.md §3.8). "Safe" must hold even with no
    #    compromise at all; it does not.
    rD = lint(BAD_TABLE_TREATING_RELAY_AS_PRESENCE, GATEWAY_ATOMS, ALL, 0, 0, loss_labels=set())
    check("D: treating a relayed signal as presence is unsafe even with zero faults assumed",
          not rD["safe"])

    print(f"gateway_lint failures={failures}")
    return failures


if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

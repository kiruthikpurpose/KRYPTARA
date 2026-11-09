# REQ-PUB-01 (ADR-006): "Authorising evidence sets without presence MUST include a witnessed
# receipt (>=2 independent logs)." [C]
# This is a reference check on receipt STRUCTURE (log diversity), not a real C2SP/Tessera
# cosignature verifier -- no real log-signing keys exist in this repo, and the actual verifier is a
# Phase 1 deliverable (`ac-wit`, docs/architecture/system-architecture.md). "Signature" below is a
# placeholder opaque token, not a cryptographic check; this only verifies the counting/independence
# rule the requirement states, which is the part expressible without a real log network.

def receipt_satisfies_pub_01(log_entries, operator_of):
    """log_entries: list of (log_id, signature) pairs on the same receipt.
    operator_of: dict log_id -> operator name. 'Independent' = run by different operators
    (D-15/project-principles.md: logs/witnesses run by >=2 unaffiliated organisations)."""
    seen_logs = set()
    seen_ops = set()
    for log_id, sig in log_entries:
        if not sig:
            continue                      # an empty/missing signature doesn't count
        if log_id in seen_logs:
            continue                      # REQ-EVD-03-style: don't let one log double-count itself
        seen_logs.add(log_id)
        seen_ops.add(operator_of.get(log_id, log_id))   # unknown operator: treat log_id as its own operator
    return len(seen_logs) >= 2 and len(seen_ops) >= 2

def authorised_without_presence(presence, log_entries, operator_of):
    """REQ-PUB-01's actual gate: without presence, a witnessed receipt satisfying the >=2-independent-
    logs rule is REQUIRED; with presence, this rule does not apply (presence is its own evidence)."""
    if presence:
        return True
    return receipt_satisfies_pub_01(log_entries, operator_of)

if __name__ == "__main__":
    OPS = {"logA": "OperatorX", "logB": "OperatorY", "logC": "OperatorX"}  # logC shares an operator with logA
    cases = [
        # (presence, entries, expected)
        (True,  [],                                              True),   # presence alone suffices
        (False, [("logA", "sigA"), ("logB", "sigB")],              True),   # 2 distinct logs, 2 distinct operators
        (False, [("logA", "sigA")],                                False),  # only 1 log
        (False, [("logA", "sigA"), ("logA", "sigA2")],             False),  # same log counted twice: still 1
        (False, [("logA", "sigA"), ("logC", "sigC")],              False),  # 2 logs but same operator: not independent
        (False, [("logA", "sigA"), ("logB", "")],                  False),  # second signature missing/empty
        (False, [("logA", "sigA"), ("logB", "sigB"), ("logC", "sigC")], True),  # 3 logs, >=2 independent operators present
    ]
    failures = 0
    for presence, entries, expect in cases:
        got = authorised_without_presence(presence, entries, OPS)
        ok = got == expect
        failures += (not ok)
        print(f"  presence={presence!s:5s} entries={entries!r:60s} -> authorised={got!s:5s} "
              f"(expected {expect!s:5s}) {'OK' if ok else 'FAIL'}")
    print(f"REQ-PUB-01 failures={failures}")
    if failures:
        raise SystemExit(1)

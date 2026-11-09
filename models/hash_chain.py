# REQ-CHAIN-01 (ADR-008): "History MUST be a per-device hash chain verified under the policy in
# force at each link, with domain separation." [C]
# Reference implementation + tests, stdlib-only (hashlib). This is a model of the RECORD FORMAT and
# chain-verification algorithm; it does not implement NV storage, torn-write recovery, or signature
# verification (those are the C prototypes under src/prototypes/c/ and the locked-stage spec).
# "Domain separation" here means: the hash of a link always includes a domain tag naming what KIND
# of record it is, so a CHAIN_COMMIT record and an IMAGE_COMMIT record with identical payload bytes
# never collide to the same digest -- a structural guard against cross-protocol confusion attacks.
import hashlib

GENESIS = b"\x00" * 32

def domain_hash(domain: bytes, prev: bytes, payload: bytes) -> bytes:
    return hashlib.sha256(domain + prev + payload).digest()

class Link:
    def __init__(self, domain, payload, policy_table_id):
        self.domain = domain              # e.g. b"CHAIN_COMMIT", b"IMAGE_COMMIT", b"KEY_INSTALL"
        self.payload = payload
        self.policy_table_id = policy_table_id   # which admission table was in force when this link was appended

class Chain:
    """Per-device hash chain. append() computes the next digest from (domain, prev, payload);
    verify() replays the whole chain and checks EACH link under its own recorded policy_table_id,
    not the device's current table -- REQ-CHAIN-01's "policy in force at each link"."""
    def __init__(self):
        self.links = []
        self.digests = [GENESIS]

    def append(self, link: Link):
        prev = self.digests[-1]
        d = domain_hash(link.domain, prev, link.payload)
        self.links.append(link)
        self.digests.append(d)
        return d

    def verify(self, policy_check):
        """policy_check(table_id, domain, payload) -> bool. Returns (ok, first_bad_index_or_None)."""
        prev = GENESIS
        for i, link in enumerate(self.links):
            expected = domain_hash(link.domain, prev, link.payload)
            if expected != self.digests[i + 1]:
                return False, i                      # tamper/corruption: digest doesn't match recomputation
            if not policy_check(link.policy_table_id, link.domain, link.payload):
                return False, i                      # this link wasn't authorised under its OWN recorded policy
            prev = expected
        return True, None

def _tests():
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    c = Chain()
    c.append(Link(b"CHAIN_COMMIT", b"record-0", policy_table_id=1))
    c.append(Link(b"CHAIN_COMMIT", b"record-1", policy_table_id=1))
    c.append(Link(b"KEY_INSTALL", b"record-2", policy_table_id=2))
    always_ok = lambda *_: True
    ok, bad = c.verify(always_ok)
    check("A: untampered chain verifies", ok and bad is None)

    # B: tamper with a middle payload -> every digest from that point changes, caught at that link
    c2 = Chain()
    c2.append(Link(b"CHAIN_COMMIT", b"record-0", 1))
    c2.append(Link(b"CHAIN_COMMIT", b"record-1", 1))
    c2.links[1].payload = b"TAMPERED"   # digest in self.digests[2] now stale vs recomputation
    ok, bad = c2.verify(always_ok)
    check("B: tampered payload detected at the right link", not ok and bad == 1)

    # C: domain separation -- same prev+payload bytes, different domain tag, must NOT collide
    prev = GENESIS
    d1 = domain_hash(b"CHAIN_COMMIT", prev, b"same-bytes")
    d2 = domain_hash(b"IMAGE_COMMIT", prev, b"same-bytes")
    check("C: different domains on identical payload give different digests", d1 != d2)

    # D: a link rejected under ITS OWN recorded policy fails verification, even if later links are fine
    c3 = Chain()
    c3.append(Link(b"CHAIN_COMMIT", b"record-0", policy_table_id=1))
    c3.append(Link(b"KEY_INSTALL", b"record-1", policy_table_id=99))  # table 99 "didn't authorise this"
    reject_99 = lambda table_id, *_: table_id != 99
    ok, bad = c3.verify(reject_99)
    check("D: link rejected under its own recorded policy halts verification there", not ok and bad == 1)

    # E: same policy_check must use the policy recorded AT EACH LINK, not a single current one --
    # verify that changing an EARLIER link's recorded table_id (simulating "verified under current
    # policy" instead of "policy in force at that link") can flip the verdict, proving the function
    # actually consults per-link state rather than a closed-over current table.
    c4 = Chain()
    c4.append(Link(b"CHAIN_COMMIT", b"record-0", policy_table_id=99))   # historically rejected table
    c4.append(Link(b"CHAIN_COMMIT", b"record-1", policy_table_id=1))     # later table, fine
    ok, bad = c4.verify(reject_99)
    check("E: an old link's own (now-superseded) policy is still the one it's checked against", not ok and bad == 0)

    print(f"REQ-CHAIN-01 failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

# Item 39 (50-things list): complete CDDL wire format, canonical encoding, two independent
# encoders producing byte-identical output. [C]
# Encoder A (`encode_canonical`): hand-written, stdlib-only, deterministic CBOR (RFC 8949 ss4.2
# canonical form: definite-length only, map keys sorted by encoded byte string, shortest-form
# integers) -- matches this repo's existing convention that core logic has no dependency surface.
# Encoder B: the independently-written `cbor2` library (canonical_cbor=True). Agreement between an
# encoder built from this file's own understanding of the spec and a library built by someone else
# from the same public spec is exactly the differential-testing property REQ-LINT-01/CLM-06 already
# apply to the admission code, extended to the wire format.
#
# See docs/specifications/interfaces-and-data-models.md ss8.3 for the CDDL this implements
# (transition-bundle, evidence, receipt), and docs/specifications/wire-format-vectors.md for the
# published test vectors this script generates.
import struct, sys, os

def _encode_uint(n, major):
    if n < 24: return bytes([major << 5 | n])
    if n < 256: return bytes([major << 5 | 24, n])
    if n < 65536: return bytes([major << 5 | 25]) + struct.pack(">H", n)
    if n < 2**32: return bytes([major << 5 | 26]) + struct.pack(">I", n)
    return bytes([major << 5 | 27]) + struct.pack(">Q", n)

def encode_canonical(obj):
    """Minimal deterministic CBOR encoder: int, bytes, str, list, dict (sorted by encoded key), bool, None."""
    if isinstance(obj, bool):
        return bytes([0xf5 if obj else 0xf4])
    if isinstance(obj, int):
        if obj >= 0: return _encode_uint(obj, 0)
        return _encode_uint(-1 - obj, 1)
    if isinstance(obj, bytes):
        return _encode_uint(len(obj), 2) + obj
    if isinstance(obj, str):
        b = obj.encode("utf-8")
        return _encode_uint(len(b), 3) + b
    if isinstance(obj, list):
        out = _encode_uint(len(obj), 4)
        for item in obj: out += encode_canonical(item)
        return out
    if isinstance(obj, dict):
        encoded_pairs = [(encode_canonical(k), encode_canonical(v)) for k, v in obj.items()]
        encoded_pairs.sort(key=lambda kv: kv[0])  # RFC 8949 canonical: sort by encoded key bytes
        out = _encode_uint(len(encoded_pairs), 5)
        for k, v in encoded_pairs: out += k + v
        return out
    if obj is None:
        return bytes([0xf6])
    raise TypeError(f"unsupported type for canonical CBOR: {type(obj)}")

# ---- the wire objects from interfaces-and-data-models.md ss8.3 ------------------------------

def evidence(atom, alg, sig):
    return [atom, alg, sig]

def receipt(origin, checkpoint, cosigs, inclusion_path, leaf_index):
    return {1: origin, 2: checkpoint, 3: cosigs, 4: inclusion_path, 5: leaf_index}

def transition_bundle(tx_bytes, action_payload, evidences, rcpt, rationale=None, ceremony_ref=None):
    d = {1: 2, 2: tx_bytes, 3: action_payload, 4: evidences, 5: rcpt}
    if rationale is not None: d[6] = rationale
    if ceremony_ref is not None: d[7] = ceremony_ref
    return d

# Domain-separation strings, reused from models/hash_chain.py's convention (one string per record
# kind, hashed/included alongside the payload so no two record kinds can be confused even with
# byte-identical payloads).
DOMAIN_TAGS = {
    "CHAIN_COMMIT": b"CHAIN_COMMIT",
    "IMAGE_COMMIT": b"IMAGE_COMMIT",
    "KEY_INSTALL": b"KEY_INSTALL",
    "LABEL_DECLARATION": b"LABEL_DECLARATION",
}

def _vectors():
    return [
        ("minimal bundle, no optional fields",
         transition_bundle(b"\x00" * 112, b"", [], receipt("log-a", b"\x01" * 32, [], [], 0))),
        ("one evidence atom, rationale present",
         transition_bundle(b"\xAB" * 112, b"payload", [evidence(3, 1, b"\xCC" * 8)],
                            receipt("log-b", b"\x02" * 32, [b"cosig1"], [b"\x03" * 32], 5),
                            rationale="operator note")),
        ("two evidence atoms, ceremony ref, nested receipt arrays",
         transition_bundle(b"\xFF" * 112, b"\x10\x20\x30",
                            [evidence(0, 1, b"\x01" * 8), evidence(7, 2, b"\x02" * 8)],
                            receipt("log-c", b"\x04" * 32, [b"cs1", b"cs2"],
                                    [b"\x05" * 32, b"\x06" * 32], 99),
                            ceremony_ref=b"\x07" * 32)),
    ]

def _tests():
    failures = 0
    try:
        import cbor2
    except ImportError:
        print("cbor2 not installed in this interpreter -- SKIPPED, not failed. "
              "Install with: pip install cbor2 (see requirements-dev.txt)")
        return 0
    for name, obj in _vectors():
        a = encode_canonical(obj)
        b = cbor2.dumps(obj, canonical=True)
        ok = a == b
        print(f"  {name}: {'MATCH' if ok else 'MISMATCH'} ({len(a)} bytes)" +
              ("" if ok else f"\n    A={a.hex()}\n    B={b.hex()}"))
        if not ok: failures += 1
        # round-trip: cbor2 can decode what our encoder produced, and get the same structure back
        decoded = cbor2.loads(a)
        if decoded != obj:
            print(f"  {name}: ROUND-TRIP MISMATCH"); failures += 1
    print(f"wire_format failures={failures}")
    return failures

if __name__ == "__main__":
    if _tests():
        sys.exit(1)

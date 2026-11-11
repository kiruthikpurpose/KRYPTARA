#!/usr/bin/env python3
"""ac-ceremony (item 32, 50-things list; ADR-017/D-33): a small, real, runnable tool that captures
a custody graph (who holds which key, in which HSM, wrapped by what) and emits the T2
label-declaration record that ADR-017 says labels must come from, instead of hand-written labels.

What this is: a working reference tool matching the CDDL `label-declaration` object already
specified in docs/specifications/wire-format-vectors.md, built on the SAME canonical CBOR encoder
as models/wire_format.py (so a ceremony record and a transition-bundle are byte-compatible, not two
incompatible formats). "Signing" here is a placeholder HMAC-SHA256 under a ceremony key, clearly
labelled as such -- this tool does not implement or claim a real multi-party signature scheme; the
real `ac-ceremony` (roadmap, Phase 1/2) would use the project's actual LMS/ML-DSA providers, not a
tool built by this session. What IS real: the custody-graph digest, the canonical encoding, and the
replay property (item 32's "done when").

Usage:
    python3 ac_ceremony.py capture custody_graph.json ceremony_key.hex > ceremony_record.cbor.hex
    python3 ac_ceremony.py replay ceremony_record.cbor.hex ceremony_key.hex
"""
import sys, os, json, hmac, hashlib, binascii

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))
from wire_format import encode_canonical

LOCKED_LABEL_BITS = {"group": 16, "site": 24}   # matches ac_labels_valid's bits 16..23 convention

def custody_graph_digest(graph):
    """graph: list of {holder, key_id, hsm, wrapped_by, labels: {kind: value}}. Canonical CBOR
    encode, then SHA-256 -- this IS the "evidence-backed" part: the digest is reproducible by
    anyone given the same graph, not asserted out of band."""
    canon = encode_canonical(graph)
    return hashlib.sha256(canon).digest(), canon

def derive_label_declaration(graph, digest):
    """Builds the label-declaration object per docs/specifications/wire-format-vectors.md's CDDL:
    {1: [atom-decl...], 2: {label_name: bit}, 3: [out-of-scope pairs], 4: custody-graph-digest}."""
    atom_decls = []
    label_names = {}
    next_bit = 0
    for i, entry in enumerate(graph):
        kind = 1  # SIG, matching ac_labels_valid's convention (kind 1 = SIG)
        declared_bits = 0
        for label_kind, value in sorted(entry.get("labels", {}).items()):
            name = f"{label_kind}:{value}"
            if name not in label_names:
                label_names[name] = next_bit
                next_bit += 1
            declared_bits |= (label_names[name] & 0xff) << LOCKED_LABEL_BITS.get(label_kind, 16)
        atom_decls.append({1: kind, 2: i, 3: declared_bits, 4: digest})
    return {1: atom_decls, 2: label_names, 3: [], 4: digest}

def sign_placeholder(data, key):
    """NOT a real signature scheme -- HMAC-SHA256 placeholder, explicitly labelled. The real tool
    would use this project's own LMS/ML-DSA verify-only providers (see models/pqc_conformance.py
    for maintained implementations already integrated elsewhere in this repo)."""
    return hmac.new(key, data, hashlib.sha256).digest()

def capture(graph_path, key_path):
    graph = json.load(open(graph_path))
    key = binascii.unhexlify(open(key_path).read().strip())
    digest, canon_graph = custody_graph_digest(graph)
    decl = derive_label_declaration(graph, digest)
    decl_bytes = encode_canonical(decl)
    sig = sign_placeholder(decl_bytes, key)
    record = {1: decl, 2: sig, 3: canon_graph}   # {declaration, placeholder-sig, raw graph for replay}
    return encode_canonical(record)

def replay(record_hex, key_path):
    import cbor2  # only needed for replay's decode step; capture doesn't need it
    key = binascii.unhexlify(open(key_path).read().strip())
    record = cbor2.loads(binascii.unhexlify(record_hex))
    decl, sig, canon_graph = record[1], record[2], record[3]
    graph = cbor2.loads(canon_graph)
    digest, recomputed_canon = custody_graph_digest(graph)
    recomputed_decl = derive_label_declaration(graph, digest)
    decl_bytes = encode_canonical(recomputed_decl)
    sig_ok = hmac.compare_digest(sign_placeholder(decl_bytes, key), sig)
    labels_match = (recomputed_decl == decl)
    return sig_ok, labels_match, recomputed_decl

def _tests():
    import tempfile
    failures = 0
    def check(name, cond):
        nonlocal failures
        print(f"  {name}: {'OK' if cond else 'FAIL'}")
        if not cond: failures += 1

    graph = [
        {"holder": "OEM-HSM-1", "key_id": "oem1", "hsm": "Thales-nShield", "wrapped_by": "KEK-A",
         "labels": {"group": "OEM", "family": "H1"}},
        {"holder": "OWN-HSM-1", "key_id": "own1", "hsm": "AWS-CloudHSM", "wrapped_by": "KEK-B",
         "labels": {"group": "OWN", "family": "H2"}},
    ]
    key = os.urandom(32)
    with tempfile.TemporaryDirectory() as d:
        gpath, kpath = os.path.join(d, "g.json"), os.path.join(d, "k.hex")
        json.dump(graph, open(gpath, "w"))
        open(kpath, "w").write(key.hex())

        record_bytes = capture(gpath, kpath)
        check("A: capture produces a nonempty canonical record", len(record_bytes) > 0)

        try:
            import cbor2
            sig_ok, labels_match, decl = replay(record_bytes.hex(), kpath)
            check("B: replayed signature verifies against the same key", sig_ok)
            check("C: replayed label declaration EXACTLY matches the original (item 32's 'done when')",
                  labels_match)

            wrong_key = os.path.join(d, "wrong.hex")
            open(wrong_key, "w").write(os.urandom(32).hex())
            sig_ok2, _, _ = replay(record_bytes.hex(), wrong_key)
            check("D: replay with the WRONG key fails signature verification", not sig_ok2)

            tampered_graph = [dict(graph[0], labels={"group": "OEM", "family": "H2"}), graph[1]]
            gpath2 = os.path.join(d, "g2.json")
            json.dump(tampered_graph, open(gpath2, "w"))
            record2 = capture(gpath2, kpath)
            check("E: a different custody graph produces a different canonical record",
                  record2 != record_bytes)
        except ImportError:
            print("  cbor2 not installed -- replay-dependent checks B/C/D SKIPPED (pip install cbor2)")

    print(f"ac_ceremony failures={failures}")
    return failures

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "capture":
        sys.stdout.write(capture(sys.argv[2], sys.argv[3]).hex() + "\n")
    elif len(sys.argv) >= 2 and sys.argv[1] == "replay":
        ok, match, decl = replay(sys.argv[2], sys.argv[3])
        print(f"signature_ok={ok} labels_match={match}")
        sys.exit(0 if (ok and match) else 1)
    elif len(sys.argv) >= 2 and sys.argv[1] == "test":
        sys.exit(1 if _tests() else 0)
    else:
        print(__doc__)
        sys.exit(2)

# REQ-PUB-01 (ADR-006) support / completion-list item 15: "Witness receipt verifier (publicity) ...
# implement checkpoint and cosignature verification in the formats of the C2SP specifications and
# RFC 9162 inclusion proofs; verify the formats against the published specs, not memory."
#
# WHAT THIS FILE DOES: implements the RFC 9162 (Certificate Transparency, successor to RFC 6962)
# section 2.1 Merkle Tree Hash (MTH) and section 2.1.1 audit-path (inclusion-proof) construction and
# verification algorithm, faithfully, over SHA-256:
#   leaf hash:     MTH({d}) = SHA-256(0x00 || d)
#   interior node: SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n])),  k = largest power of two < n
# It builds a real tree, computes a real tree head, generates a real audit path for a given leaf
# index, and verifies that audit path against a tree head by *reconstructing the path*, not by
# recomputing the whole tree (see verify_inclusion_proof). It is tested on a 1-leaf tree, an exact
# power-of-two tree (8 leaves), and a non-power-of-two tree (7 leaves) -- the unbalanced case RFC
# 9162's recursive split (D[0:k], D[k:n]) is easy to get wrong -- plus tamper tests that must fail.
#
# WHAT THIS FILE DOES NOT DO: it does NOT implement real C2SP checkpoint or cosignature formats
# (https://c2sp.org/tlog-checkpoint, https://c2sp.org/signed-note) -- no checkpoint text parsing, no
# Ed25519/note-format signature verification, no witness cosignature line format. That remains a
# separate, unimplemented gap; `models/witness_receipt.py` covers only the >=2-independent-logs
# counting rule over placeholder opaque "signature" tokens, and still does not do real signature
# verification either. Nothing here should be read as closing that gap -- it is Merkle-tree math
# only. [Class: Derived (machine-checked against a hand-traced 3-leaf example in review and against
# RFC 9162 section 2.1/2.1.1's own text, not against an external reference implementation).]

import hashlib

LEAF_PREFIX = b"\x00"
NODE_PREFIX = b"\x01"


def leaf_hash(data: bytes) -> bytes:
    """RFC 9162 section 2.1: MTH of a single-entry tree containing `data`."""
    return hashlib.sha256(LEAF_PREFIX + data).digest()


def hash_children(left: bytes, right: bytes) -> bytes:
    """RFC 9162 section 2.1: the interior-node hashing rule."""
    return hashlib.sha256(NODE_PREFIX + left + right).digest()


def largest_pow2_lt(n: int) -> int:
    """Largest power of two strictly less than n (n >= 2). RFC 9162 section 2.1 defines the split
    point k for a tree of size n as the largest power of two < n, so that k < n <= 2k."""
    if n < 2:
        raise ValueError("largest_pow2_lt requires n >= 2")
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def mth_hashes(hashes):
    """RFC 9162 section 2.1 MTH(D[n]), applied to a list of already-computed leaf hashes.
    MTH({}) = SHA-256() (empty input); MTH({h}) = h; otherwise split at k = largest_pow2_lt(n)."""
    n = len(hashes)
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return hashes[0]
    k = largest_pow2_lt(n)
    left = mth_hashes(hashes[:k])
    right = mth_hashes(hashes[k:])
    return hash_children(left, right)


def tree_head(leaves):
    """Compute the Merkle Tree Hash (tree head) over a list of raw leaf byte-strings."""
    hashes = [leaf_hash(d) for d in leaves]
    return mth_hashes(hashes)


def build_audit_path(m, hashes):
    """RFC 9162 section 2.1.1 PATH(m, D[n]), over a list of already-computed leaf hashes.
    PATH(0, {d0}) = {} (empty). For n > 1, split at k = largest_pow2_lt(n):
      m < k:  PATH(m, D[n]) = PATH(m, D[0:k]) : MTH(D[k:n])
      m >= k: PATH(m, D[n]) = PATH(m-k, D[k:n]) : MTH(D[0:k])
    Returned list is ordered leaf-to-root (deepest sibling first, root-adjacent sibling last) --
    this is the order the recursion naturally produces, and the order verify_inclusion_proof below
    consumes."""
    n = len(hashes)
    if n <= 1:
        return []
    k = largest_pow2_lt(n)
    if m < k:
        return build_audit_path(m, hashes[:k]) + [mth_hashes(hashes[k:])]
    else:
        return build_audit_path(m - k, hashes[k:]) + [mth_hashes(hashes[:k])]


def inclusion_proof(leaves, m):
    """Build the audit path for leaf index m (0-based) in the tree over `leaves`.
    Returns (leaf_hash_m, tree_size, audit_path)."""
    n = len(leaves)
    if not (0 <= m < n):
        raise ValueError("leaf index out of range")
    hashes = [leaf_hash(d) for d in leaves]
    return hashes[m], n, build_audit_path(m, hashes)


def _split_decisions(m, n):
    """Replay, top-down, the same k = largest_pow2_lt(n) splits RFC 9162's PATH() definition makes
    while descending to leaf m of a tree of size n. Each entry is True if m falls in the left half
    (D[0:k]) at that level, False if it falls in the right half (D[k:n]). This lets verification
    know -- at each level of the audit path -- which side the already-computed hash is on, so it can
    combine it with the next audit-path element in the correct (left, right) order, without ever
    recomputing the whole tree."""
    decisions = []
    while n > 1:
        k = largest_pow2_lt(n)
        if m < k:
            decisions.append(True)
            n = k
        else:
            decisions.append(False)
            m = m - k
            n = n - k
    return decisions


def verify_inclusion_proof(leaf_h, m, n, audit_path, root_hash):
    """RFC 9162 section 2.1.1 audit-path verification: reconstruct the root from a leaf hash, its
    index m, the claimed tree size n, and the audit path, WITHOUT recomputing the whole tree, and
    check it equals the given tree head. Returns True/False."""
    if not (0 <= m < n):
        return False
    decisions_top_down = _split_decisions(m, n)
    if len(decisions_top_down) != len(audit_path):
        return False
    # audit_path is leaf-to-root (deepest first); decisions_top_down is root-to-leaf (shallowest
    # first), so reverse it to walk the path in the same bottom-up order as audit_path.
    decisions_bottom_up = list(reversed(decisions_top_down))
    current = leaf_h
    for was_left, sibling in zip(decisions_bottom_up, audit_path):
        if was_left:
            current = hash_children(current, sibling)
        else:
            current = hash_children(sibling, current)
    return current == root_hash


def _tests():
    failures = 0

    def check(label, cond):
        nonlocal failures
        ok = bool(cond)
        failures += not ok
        print(f"  {label}: {'OK' if ok else 'FAIL'}")

    # --- Case 1: single-leaf tree (edge case). Audit path must be empty; root is just the leaf hash.
    leaves1 = [b"only-leaf"]
    root1 = tree_head(leaves1)
    lh, n, path = inclusion_proof(leaves1, 0)
    check("1-leaf: audit path is empty", path == [])
    check("1-leaf: root equals leaf hash", root1 == leaf_hash(b"only-leaf"))
    check("1-leaf: proof verifies", verify_inclusion_proof(lh, 0, n, path, root1))

    # --- Case 2: exact power-of-two tree (8 leaves), check every index.
    leaves8 = [f"leaf-{i}".encode() for i in range(8)]
    root8 = tree_head(leaves8)
    for i in range(8):
        lh, n, path = inclusion_proof(leaves8, i)
        check(f"8-leaf idx {i}: proof verifies", verify_inclusion_proof(lh, i, n, path, root8))
    # Hand-checkable structural fact for a balanced 8-leaf tree: every audit path has depth 3.
    check("8-leaf: audit path depth is 3 for every index",
          all(len(build_audit_path(i, [leaf_hash(d) for d in leaves8])) == 3 for i in range(8)))

    # --- Case 3: non-power-of-two tree (7 leaves) -- the unbalanced RFC 9162 split, every index.
    leaves7 = [f"leaf-{i}".encode() for i in range(7)]
    root7 = tree_head(leaves7)
    for i in range(7):
        lh, n, path = inclusion_proof(leaves7, i)
        check(f"7-leaf idx {i}: proof verifies", verify_inclusion_proof(lh, i, n, path, root7))

    # --- Hand-traced 3-leaf tree, worked by hand against RFC 9162 section 2.1/2.1.1 before coding:
    #   n=3, k=2 -> left=D[0:2]={L0,L1}, right=D[2:3]={L2}
    #   H01 = hash_children(h0, h1); Root = hash_children(H01, h2)
    #   PATH(0, D[3]) = [h1, h2]; PATH(2, D[3]) = [H01]
    leaves3 = [b"L0", b"L1", b"L2"]
    h0, h1, h2 = (leaf_hash(d) for d in leaves3)
    h01 = hash_children(h0, h1)
    expected_root3 = hash_children(h01, h2)
    root3 = tree_head(leaves3)
    check("3-leaf: computed root matches hand trace", root3 == expected_root3)
    lh0, n3, path0 = inclusion_proof(leaves3, 0)
    check("3-leaf idx 0: audit path matches hand trace [h1, h2]", path0 == [h1, h2])
    check("3-leaf idx 0: proof verifies", verify_inclusion_proof(lh0, 0, n3, path0, root3))
    lh2, _, path2 = inclusion_proof(leaves3, 2)
    check("3-leaf idx 2: audit path matches hand trace [H01]", path2 == [h01])
    check("3-leaf idx 2: proof verifies", verify_inclusion_proof(lh2, 2, n3, path2, root3))

    # --- Tamper tests: a bad leaf hash, or a bad audit-path element, MUST fail verification.
    lh, n, path = inclusion_proof(leaves7, 3)
    tampered_leaf = bytes([lh[0] ^ 0xFF]) + lh[1:]
    check("7-leaf idx 3: tampered leaf hash fails", not verify_inclusion_proof(tampered_leaf, 3, n, path, root7))
    tampered_path = list(path)
    tampered_path[0] = bytes([tampered_path[0][0] ^ 0xFF]) + tampered_path[0][1:]
    check("7-leaf idx 3: tampered audit-path element fails", not verify_inclusion_proof(lh, 3, n, tampered_path, root7))
    wrong_root = bytes([root7[0] ^ 0xFF]) + root7[1:]
    check("7-leaf idx 3: tampered root fails", not verify_inclusion_proof(lh, 3, n, path, wrong_root))
    # Wrong index against a correct proof for a different index must also fail.
    check("7-leaf: proof for idx 3 rejected against idx 4",
          not verify_inclusion_proof(lh, 4, n, path, root7))

    print(f"RFC 9162 Merkle inclusion-proof failures={failures}")
    return failures


if __name__ == "__main__":
    if _tests():
        raise SystemExit(1)

"""Generate deterministic test vectors for the C core (vectors.txt). Requires lms.py."""
import sys, os, hashlib, struct, random
sys.path.insert(0, os.path.dirname(__file__))
import lms
from lms import LmsKey, u32, u16

AC_SHA2, AC_KECCAK, AC_LATT, AC_DL = 1, 2, 4, 8
def seeded(h, w, tag):
    s = hashlib.sha256(b"seed" + tag).digest()
    return LmsKey(h, w, I=hashlib.sha256(b"I" + tag).digest()[:16], seed=s)

K0 = seeded(5, 4, b"s0")    # slot 0: SHA2 class, W4 H5
K1 = seeded(5, 8, b"s1")    # slot 1: label KECCAK, W8 H5 (stand-in: an LMS key labelled as another class)
K2 = seeded(10, 4, b"s2")   # slot 2: label LATTICE, W4 H10 (sig 2508 B = atlas MV-1 size)
KN = seeded(5, 4, b"new")   # replacement key for REPLACE_SLOT
KR = seeded(5, 4, b"rogue") # key that is in no slot
keys = [K0, K1, K2]
classes = [AC_SHA2, AC_KECCAK, AC_LATT]
def h32(b): return hashlib.sha256(b).digest()
def hexs(b): return b.hex() if b else "-"

def cmd(op, slot, epoch, nf, nh=b"\0" * 32, ncls=0, magic=b"FSC1"):
    return magic + bytes([op, slot, 0, 0]) + struct.pack(">II", epoch, nf) + nh + struct.pack(">H", ncls) + b"\0\0"
def bundle(items):  # items: list of (slot, pubbytes, sig)
    out = bytes([len(items)])
    for s, p, sg in items: out += bytes([s]) + p + struct.pack(">H", len(sg)) + sg
    return out
def signed(m, key, slot, q): return (slot, key.pub(), key.sign(m, q))
def img(ver, digest): return b"IMG1" + struct.pack(">I", ver) + digest

L = []
def line(*a): L.append(" ".join(str(x) for x in a))
for i in range(3): line("K", i, classes[i], keys[i].pub().hex())

# ---- raw LMS verify cases (L name expect pub msg sig)
m = b"first-stage verifier test message"
for nm, k in [("w4h5", K0), ("w8h5", K1), ("w4h10", K2)]:
    s = k.sign(m, 3)
    line("L", nm + "_valid", "OK", k.pub().hex(), m.hex(), s.hex())
line("L", "wrong_msg", "BAD", K0.pub().hex(), (m + b"x").hex(), K0.sign(m, 5).hex())
line("L", "wrong_key", "BAD", K1.pub().hex(), m.hex(), K0.sign(m, 5).hex())

# ---- command / image sequences (R resets to genesis epoch=1 floor=1)
E = 1
M = lambda *a, **k: cmd(*a, **k)
def C(name, expect, m_, items, raw_bundle=None):
    b = raw_bundle if raw_bundle is not None else bundle(items)
    line("C", name, expect, m_.hex(), hexs(b))
def I(name, expect, ver, dg, items, raw_bundle=None):
    b = raw_bundle if raw_bundle is not None else bundle(items)
    line("I", name, expect, ver, dg.hex(), hexs(b))
dg = h32(b"image-v2")

line("R")
adv = M(1, 0, 1, 2)
good = bundle([signed(adv, K1, 1, 0)])
C("advance_retire_s0_by_s1", "OK", adv, None, good)
C("replay_same_command", "REPLAY", adv, None, good)
C("q_reuse_new_epoch", "REPLAY", M(1, NO := 255, 2, 3), [signed(M(1, 255, 2, 3), K1, 1, 0)])
C("q_next_ok", "OK", M(1, 255, 2, 3), [signed(M(1, 255, 2, 3), K1, 1, 1)])
C("floor_decrease", "FLOOR", M(1, 255, 3, 2), [signed(M(1, 255, 3, 2), K1, 1, 2)])
C("retired_slot_signs", "SLOT", M(1, 255, 3, 4), [signed(M(1, 255, 3, 4), K0, 0, 9)])
I("img_ok_v3", "OK", 3, dg, [signed(img(3, dg), K1, 1, 10)])
I("img_below_floor", "FLOOR", 2, dg, [signed(img(2, dg), K1, 1, 11)])
I("img_by_retired", "SLOT", 3, dg, [signed(img(3, dg), K0, 0, 12)])
I("img_digest_tamper", "SIG", 3, h32(b"other"), [signed(img(3, dg), K1, 1, 13)])

line("R")
C("signer_is_target", "POLICY", adv, [signed(adv, K0, 0, 0)])
C("wrong_slot_claim", "KEYHASH", adv, [(2, K1.pub(), K1.sign(adv, 0))])
C("rogue_key", "KEYHASH", adv, [(1, KR.pub(), KR.sign(adv, 0))])
C("empty_slot_index", "SLOT", adv, [(3, K1.pub(), K1.sign(adv, 0))])
tampered = M(1, 0, 1, 3)
C("msg_tampered_after_sign", "SIG", tampered, [(1, K1.pub(), K1.sign(adv, 0))])
s = bytearray(K1.sign(adv, 0))
for nm, pos in [("q_field", 3), ("ots_C", 20), ("ots_y_first", 45), ("ots_y_last", 40 + 32 * 34 - 1), ("path_last", len(s) - 1)]:
    t = bytearray(s); t[pos] ^= 0x01
    C("sig_bitflip_" + nm, "SIG", adv, [(1, K1.pub(), bytes(t))])
good1 = bundle([signed(adv, K1, 1, 1)])
for cut in [0, 1, 2, 10, 58, 59, 60, 100, len(good1) - 1]:
    C(f"bundle_trunc_{cut}", "PARSE", adv, None, good1[:cut])
C("bundle_trailing_byte", "PARSE", adv, None, good1 + b"\0")
C("bundle_zero_sigs", "PARSE", adv, None, b"\x00")
C("bundle_four_sigs", "PARSE", adv, None, b"\x04" + good1[1:])
short = K1.sign(adv, 2)[:-1]
C("sig_short_by_one_len_consistent", "SIG", adv, [(1, K1.pub(), short)])
C("cmd_bad_magic", "PARSE", cmd(1, 0, 1, 2, magic=b"XXXX"), [signed(cmd(1, 0, 1, 2, magic=b"XXXX"), K1, 1, 3)])
C("cmd_bad_op", "PARSE", cmd(9, 0, 1, 2), [signed(cmd(9, 0, 1, 2), K1, 1, 4)])
C("advance_ok_after_rejects", "OK", adv, [signed(adv, K1, 1, 5)])   # state unchanged by every reject above

line("R")
rep = M(2, 2, 1, 0, KN.pub() and h32(KN.pub()), AC_SHA2)
C("replace_s2_by_s0", "OK", rep, [signed(rep, K0, 0, 0)])
dg3 = h32(b"image-v1")
I("img_by_replaced_slot_new_key", "OK", 1, dg3, [signed(img(1, dg3), KN, 2, 0)])
I("img_by_replaced_slot_old_key", "KEYHASH", 1, dg3, [signed(img(1, dg3), K2, 2, 0)])
# s2 now SHA2 class: overlaps s0 -> 2-quorum {s0,s2} invalid
adv2 = M(1, 1, 2, 2)
C("quorum_overlap_s0_s2", "QUORUM", adv2, [signed(adv2, K0, 0, 1), signed(adv2, KN, 2, 1)])
C("quorum_duplicate_slot", "SLOT", adv2, [signed(adv2, K0, 0, 2), signed(adv2, K0, 0, 3)])
C("quorum_ok_s0_s1_retire_s2", "OK", M(1, 2, 2, 2), [signed(M(1, 2, 2, 2), K0, 0, 1), signed(M(1, 2, 2, 2), K1, 1, 0)])

line("R")
rep3 = M(2, 0, 1, 0, h32(KN.pub()), AC_LATT | AC_DL)   # replace slot 0 by class LATTICE|DL (overlaps slot 2)
C("replace_s0_overlap_lattice", "OK", rep3, [signed(rep3, K1, 1, 0)])
adv3 = M(1, 1, 2, 2)
C("quorum_overlap_s0_s2_b", "QUORUM", adv3, [signed(adv3, KN, 0, 0), signed(adv3, K2, 2, 0)])
C("replace_bad_class_zero", "POLICY", M(2, 0, 2, 0, h32(KN.pub()), 0), [signed(M(2, 0, 2, 0, h32(KN.pub()), 0), K1, 1, 1)])
open(os.path.join(os.path.dirname(__file__), "..", "test", "vectors.txt"), "w").write("\n".join(L) + "\n")
print("wrote", len(L), "lines")

# ---------------- power-fail vectors (pf_vectors.txt) ----------------
P = []
for i in range(3): P.append(f"K {i} {classes[i]} {keys[i].pub().hex()}")
for e in range(1, 15):
    a = cmd(1, 0, e, 2);            P.append(f"A {e} {a.hex()} {bundle([signed(a, K1, 1, e)]).hex()}")
    r = cmd(2, 2, e, 0, h32(KN.pub()), AC_SHA2); P.append(f"B {e} {r.hex()} {bundle([signed(r, K0, 0, e)]).hex()}")
    f_ = cmd(1, 255, e, 3);         P.append(f"F {e} {f_.hex()} {bundle([signed(f_, K1, 1, e + 16)]).hex()}")
for ver, key, slot in [(1, K0, 0), (2, K1, 1)]:
    d = h32(b"pf-image-%d" % ver)
    P.append(f"G {ver} {d.hex()} {bundle([signed(img(ver, d), key, slot, 0)]).hex()}")
open(os.path.join(os.path.dirname(__file__), "..", "test", "pf_vectors.txt"), "w").write("\n".join(P) + "\n")
print("wrote", len(P), "pf lines")

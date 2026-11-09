"""Cross-check own LMS signer/verifier against pyhsslms 2.0.0 (independent implementation)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import lms, pyhsslms as P
TC_LMS = {5: P.lms_sha256_m32_h5, 10: P.lms_sha256_m32_h10}
TC_OTS = {4: P.lmots_sha256_n32_w4, 8: P.lmots_sha256_n32_w8}
n_ok = 0
for (h, w) in [(5, 4), (5, 8)]:
    k = lms.LmsKey(h, w)
    pub = P.LmsPublicKey.deserialize(k.pub())
    for q in (0, 1, 7, (1 << h) - 1):
        msg = os.urandom(37)
        s = k.sign(msg, q)
        assert len(s) == lms.sig_len(h, w)
        assert pub.verify(msg, s), ("pyhsslms rejects ours", h, w, q)
        assert lms.verify(k.pub(), msg, s)
        bad = bytearray(s); bad[100] ^= 1
        assert not pub.verify(msg, bytes(bad))
        n_ok += 1
    # reverse direction: pyhsslms signs, we verify
    pk = P.LmsPrivateKey(TC_LMS[h], TC_OTS[w])
    pp = pk.publicKey()
    for _ in range(3):
        msg = os.urandom(20)
        s = pk.sign(msg)
        assert lms.verify(pp.serialize(), msg, s), ("ours rejects pyhsslms", h, w)
        n_ok += 1
print("xcheck ok:", n_ok, "cases (both directions, H5, W4/W8)")

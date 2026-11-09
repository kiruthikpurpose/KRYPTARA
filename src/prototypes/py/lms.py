"""LMS (RFC 8554) key generation, signing, verification. SHA-256, M32, W in {4,8}.
Written from the RFC text (from memory of the algorithms; the RFC appendix test vector
could not be fetched in this session -> cross-checked against pyhsslms, see xcheck.py).
Not constant time, not for production use: test-vector generator only."""
import hashlib, os, struct

LMOTS = {4: (3, 67, 4), 8: (4, 34, 0)}   # w -> (typecode, p, ls)
LMS_H = {5: 5, 10: 6, 15: 7}             # h -> typecode
D_PBLC, D_MESG, D_LEAF, D_INTR = 0x8080, 0x8181, 0x8282, 0x8383

def H(*parts): return hashlib.sha256(b"".join(parts)).digest()
def u32(x): return struct.pack(">I", x)
def u16(x): return struct.pack(">H", x)

def coef(S, i, w):
    return (S[(i * w) // 8] >> (8 - (w * (i % (8 // w)) + w))) & ((1 << w) - 1)

def checksum(Q, w, ls):
    s = sum(((1 << w) - 1) - coef(Q, i, w) for i in range(32 * 8 // w))
    return u16((s << ls) & 0xFFFF)

def ots_x(I, q, i, seed): return H(I, u32(q), u16(i), b"\xff", seed)

def ots_pub(I, q, seed, w):
    _, p, _ = LMOTS[w]
    top = (1 << w) - 1
    z = []
    for i in range(p):
        tmp = ots_x(I, q, i, seed)
        for j in range(top): tmp = H(I, u32(q), u16(i), bytes([j]), tmp)
        z.append(tmp)
    return H(I, u32(q), u16(D_PBLC), *z)

class LmsKey:
    def __init__(self, h=5, w=4, I=None, seed=None):
        self.h, self.w = h, w
        self.I = I or os.urandom(16); self.seed = seed or os.urandom(32)
        self.q = 0
        n = 1 << h
        # node r (1-based heap index) hashes
        self.T = [None] * (2 * n)
        for q in range(n):
            K = ots_pub(self.I, q, self.seed, w)
            self.T[n + q] = H(self.I, u32(n + q), u16(D_LEAF), K)
        for r in range(n - 1, 0, -1):
            self.T[r] = H(self.I, u32(r), u16(D_INTR), self.T[2 * r], self.T[2 * r + 1])
    def pub(self):
        return u32(LMS_H[self.h]) + u32(LMOTS[self.w][0]) + self.I + self.T[1]
    def sign(self, msg, q=None):
        """Sign with leaf q (default: next unused). Statefulness is the caller's duty."""
        if q is None: q = self.q; self.q += 1
        w = self.w; tc, p, ls = LMOTS[w]
        C = os.urandom(32)
        Q = H(self.I, u32(q), u16(D_MESG), C, msg)
        Qc = Q + checksum(Q, w, ls)
        ys = []
        for i in range(p):
            tmp = ots_x(self.I, q, i, self.seed)
            for j in range(coef(Qc, i, w)): tmp = H(self.I, u32(q), u16(i), bytes([j]), tmp)
            ys.append(tmp)
        ots_sig = u32(tc) + C + b"".join(ys)
        node = (1 << self.h) + q
        path = []
        while node > 1:
            path.append(self.T[node ^ 1]); node >>= 1
        return u32(q) + ots_sig + u32(LMS_H[self.h]) + b"".join(path)

def sig_len(h, w): 
    _, p, _ = LMOTS[w]
    return 4 + 4 + 32 + 32 * p + 4 + 32 * h

def verify(pub, msg, sig):
    """Reference verifier (RFC 8554 Alg 6a/4b). Returns bool."""
    try:
        lmstc, otstc = struct.unpack(">II", pub[:8]); I = pub[8:24]; T1 = pub[24:56]
        if len(pub) != 56: return False
        h = {v: k for k, v in LMS_H.items()}[lmstc]
        w = {v[0]: k for k, v in LMOTS.items()}[otstc]
        if len(sig) != sig_len(h, w): return False
        q = struct.unpack(">I", sig[:4])[0]
        if q >= (1 << h): return False
        tc, p, ls = LMOTS[w]
        if struct.unpack(">I", sig[4:8])[0] != tc: return False
        C = sig[8:40]; ys = [sig[40 + 32 * i: 72 + 32 * i] for i in range(p)]
        off = 40 + 32 * p
        if struct.unpack(">I", sig[off:off + 4])[0] != lmstc: return False
        path = [sig[off + 4 + 32 * i: off + 36 + 32 * i] for i in range(h)]
        Q = H(I, u32(q), u16(D_MESG), C, msg); Qc = Q + checksum(Q, w, ls)
        z = []
        for i in range(p):
            tmp = ys[i]
            for j in range(coef(Qc, i, w), (1 << w) - 1): tmp = H(I, u32(q), u16(i), bytes([j]), tmp)
            z.append(tmp)
        Kc = H(I, u32(q), u16(D_PBLC), *z)
        node = (1 << h) + q
        tmp = H(I, u32(node), u16(D_LEAF), Kc)
        for i in range(h):
            if node & 1: tmp = H(I, u32(node >> 1), u16(D_INTR), path[i], tmp)
            else: tmp = H(I, u32(node >> 1), u16(D_INTR), tmp, path[i])
            node >>= 1
        return tmp == T1
    except (KeyError, struct.error):
        return False

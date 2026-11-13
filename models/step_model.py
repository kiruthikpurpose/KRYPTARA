# Independent model of waist v1 (src/ac_step.c): ac_genesis, ac_step, ac_ack, ac_ctx_digest. [C]
# Written from docs/decisions/ADR-041 and the header comments, not by translating the C. The
# differential check (models/step_check.py) runs both on random scenarios and on the golden vectors.
# The admission arithmetic reuses models/interval.py (the project's reference for Theorem 1); the
# chain uses models/hash_chain.py. Evidence verification is out of scope, as in the C.
import hashlib, itertools, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interval import upper, lower
from lint import project
from hash_chain import domain_hash

OK, BADMSG, AUTH, ADMIT, HOLDER, DUPKEY, HALTED, BUDGET, BUSY, NOCLASS, STATE, IMAGE = 0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11
STATUS_NAMES = {OK: "OK", BADMSG: "BADMSG", AUTH: "AUTH", ADMIT: "ADMIT", HOLDER: "HOLDER", DUPKEY: "DUPKEY",
                HALTED: "HALTED", BUDGET: "BUDGET", BUSY: "BUSY", NOCLASS: "NOCLASS", STATE: "STATE", IMAGE: "IMAGE"}
HALT, RESUME, ACTIVATE, TIGHTEN, EPOCH, RETIRE, INSTALL_TABLE, KEY_INSTALL, N_ACT = range(9)
ACTION_NAMES = ["HALT", "RESUME", "ACTIVATE_IMAGE", "TIGHTEN_TABLE", "ADVANCE_EPOCH", "RETIRE_SLOT", "INSTALL_TABLE", "KEY_INSTALL"]
MSG_BOOT, MSG_PROPOSE_TX, MSG_HALT = 1, 2, 5
INT_SNAPSHOT, INT_BOOT, INT_REJECT = 1, 3, 6
MAXC = 16
NONE = 0xff
FULL = (1 << 256) - 1

def monotone(t):
    return all(not (t >> m) & 1 or all((t >> (m | (1 << i))) & 1 for i in range(8)) for m in range(256))

def popcount(x): return bin(x).count("1")

def budget(t=1, s=1, fc=(), fl=(), xc=(NONE, NONE), xl=(NONE, NONE)):
    """A per-tier fault structure. fc/fl are padded to 16 entries with zeros, as in the C layout."""
    return dict(t=t, s=s, nfc=len(fc), nfl=len(fl), xc=tuple(xc), xl=tuple(xl),
                fc=list(fc) + [0] * (MAXC - len(fc)), fl=list(fl) + [0] * (MAXC - len(fl)))

class Model:
    def __init__(self):
        self.init = False
        self.seq = self.acked = 0
        self.head = bytes(32)

    # ---- provisioning -------------------------------------------------------------------------
    def genesis(self, g):
        self.__init__()
        present, kinds, kp = g["present"], g["kinds"], g["key_present"]
        if kp & ~present & 0xff: return ADMIT
        for i in range(8):
            if kinds[i] > 3: return ADMIT
            if (kp >> i) & 1 and kinds[i] != 1: return ADMIT
        for b in g["bud"]:
            if b["t"] > 2 or b["s"] > 2 or b["nfc"] > MAXC or b["nfl"] > MAXC: return ADMIT
            if any(b["fc"][i] == 0 for i in range(b["nfc"])) or any(b["fl"][i] == 0 for i in range(b["nfl"])): return ADMIT
            xa, xb = b["xc"]
            if (xa != NONE or xb != NONE) and not (xa < xb < b["nfc"]): return ADMIT
            xa, xb = b["xl"]
            if (xa != NONE or xb != NONE) and not (xa < xb < b["nfl"]): return ADMIT
        at = g["action_tier"]
        if at[HALT] != 0: return ADMIT
        if any(at[a] != 1 for a in (RESUME, ACTIVATE, TIGHTEN, EPOCH, RETIRE)): return ADMIT
        if at[KEY_INSTALL] not in (2, 3) or at[INSTALL_TABLE] != at[KEY_INSTALL]: return ADMIT
        self.present, self.kinds, self.key_present = present, list(kinds), kp
        self.key = [bytes([0x10 + i]) * 32 if (kp >> i) & 1 else bytes(32) for i in range(8)]
        self.bud = [dict(b) for b in g["bud"]]
        self.action_tier = list(at)
        for t in range(4):
            if not self.admissible(t, g["table"][t]): self.__init__(); return ADMIT
        self.table = list(g["table"])
        self.halted = 0
        self.halt_budget = g["halt_budget"]
        self.halt_used = [0] * 8
        self.epoch = 0
        self.have_commit = False
        self.committed = bytes(32)
        self.head = bytes(32)
        self.seq = self.acked = 0
        self.init = True
        self.head = domain_hash(b"AC1_GENESIS", bytes(32), self.digest())
        return OK

    # ---- admission ----------------------------------------------------------------------------
    def interval(self, tier):
        """(Lo, U) for a tier, or None if the budget cannot be evaluated (loss budget above class count)."""
        b = self.bud[tier]
        absent = ~self.present & 0xff
        expo = sum(1 << i for i in range(8) if (self.present >> i) & 1 and self.kinds[i] == 3) | absent
        fc, fl = b["fc"][:b["nfc"]], b["fl"][:b["nfl"]]
        k = min(b["t"], len(fc))
        Ac = [expo] if k == 0 else [self._union(c) | expo for c in self._combos(fc, k, b["xc"])]
        if b["s"] > len(fl): return None
        Al = [absent] if b["s"] == 0 else [self._union(c) | absent for c in self._combos(fl, b["s"], b["xl"])]
        return lower(8, Al), upper(8, Ac)

    @staticmethod
    def _union(c):
        r = 0
        for x in c: r |= x
        return r

    @staticmethod
    def _combos(classes, k, excl):
        idx = range(len(classes))
        return [[classes[i] for i in c] for c in itertools.combinations(idx, k)
                if not (k == 2 and excl[0] != NONE and (c[0], c[1]) == tuple(excl))]

    def admissible(self, tier, t):
        if not monotone(t) or project(t, self.present) != t: return False
        if tier == 0: return True
        iv = self.interval(tier)
        if iv is None: return False
        lo, up = iv
        return (t & ~up) == 0 and (lo & ~t) == 0

    def authorises(self, tier, S): return (self.table[tier] >> S) & 1

    # ---- the step -----------------------------------------------------------------------------
    @staticmethod
    def _reject(code): return code, [(INT_REJECT, 0, code)]

    def step(self, m):
        if not self.init: return self._reject(STATE)
        if m["kind"] == MSG_BOOT:
            if self.have_commit and m["digest"] == self.committed: return OK, [(INT_BOOT, 0, 0)]
            return self._reject(IMAGE)
        if self.seq != self.acked: return self._reject(BUSY)
        if m["kind"] == MSG_HALT: action = HALT
        elif m["kind"] == MSG_PROPOSE_TX and m["action"] != HALT and m["action"] < N_ACT: action = m["action"]
        else: return self._reject(BADMSG)
        slot, bundle, tier, S = m["atom"], m["bundle"], m["tier"], m["evidence"]
        slot_action = action in (KEY_INSTALL, RETIRE)
        if action == HALT or slot_action:
            if slot >= 8 or not (self.present >> slot) & 1 or self.kinds[slot] != 1: return self._reject(BADMSG)
        if action in (HALT, RESUME, ACTIVATE) and bundle >= 16: return self._reject(BADMSG)
        if action in (TIGHTEN, INSTALL_TABLE) and tier >= 4: return self._reject(BADMSG)
        if action == TIGHTEN and tier == 0: return self._reject(BADMSG)
        if not self.authorises(self.action_tier[action], S): return self._reject(AUTH)
        if action == HALT and not (S >> slot) & 1: return self._reject(AUTH)

        bit = 1 << bundle if bundle < 16 else 0
        if action == HALT:
            if self.halted & bit: return self._reject(STATE)
            if self.halt_used[slot] >= self.halt_budget: return self._reject(BUDGET)
        elif action == RESUME:
            if not self.halted & bit: return self._reject(STATE)
        elif action == ACTIVATE:
            if self.halted & bit: return self._reject(HALTED)
        elif action == TIGHTEN:
            if not self.admissible(tier, m["table"]) or (m["table"] & ~self.table[tier]): return self._reject(ADMIT)
        elif action == INSTALL_TABLE:
            if not self.admissible(tier, m["table"]): return self._reject(ADMIT)
        elif action == KEY_INSTALL:
            if (self.key_present >> slot) & 1 and not (S >> slot) & 1: return self._reject(HOLDER)
            if any(j != slot and (self.key_present >> j) & 1 and m["digest"] == self.key[j] for j in range(8)):
                return self._reject(DUPKEY)
        elif action == RETIRE:
            if not (self.key_present >> slot) & 1: return self._reject(STATE)
            if popcount(self.key_present & ~(1 << slot) & 0xff) < self.bud[1]["t"] + self.bud[1]["s"] + 1:
                return self._reject(NOCLASS)

        tx = (bytes([m["kind"], m["action"], S, slot, bundle, tier]) + m["digest"]
              + b"".join(((m["table"] >> (32 * i)) & 0xffffffff).to_bytes(4, "little") for i in range(8)))
        if action == HALT: self.halted |= bit; self.halt_used[slot] += 1
        elif action == RESUME: self.halted &= ~bit
        elif action == ACTIVATE: self.have_commit, self.committed = True, m["digest"]
        elif action in (TIGHTEN, INSTALL_TABLE): self.table[tier] = m["table"]
        elif action == KEY_INSTALL: self.key[slot] = m["digest"]; self.key_present |= 1 << slot
        elif action == RETIRE: self.key_present &= ~(1 << slot) & 0xff; self.key[slot] = bytes(32)
        else: self.epoch += 1; self.halt_used = [0] * 8
        self.head = domain_hash(b"AC1_" + ACTION_NAMES[action].encode(), self.head, tx)
        self.seq += 1
        return OK, [(INT_SNAPSHOT, self.seq, 0)]

    def ack(self, seq):
        if not self.init: return STATE
        if seq != self.seq or self.acked == self.seq: return BADMSG
        self.acked = seq
        return OK

    def digest(self):
        if not self.init: return None
        o = struct.pack("<I", 1) + bytes([self.present]) + bytes(self.kinds) + bytes([self.key_present])
        o += b"".join(self.key[i] if (self.key_present >> i) & 1 else bytes(32) for i in range(8))
        for t in range(4):
            o += b"".join(((self.table[t] >> (32 * i)) & 0xffffffff).to_bytes(4, "little") for i in range(8))
        for b in self.bud:
            o += bytes([b["t"], b["s"], b["nfc"], b["nfl"], b["xc"][0], b["xc"][1], b["xl"][0], b["xl"][1]]) + bytes(b["fc"]) + bytes(b["fl"])
        o += bytes(self.action_tier) + struct.pack("<H", self.halted) + bytes([self.halt_budget]) + bytes(self.halt_used)
        o += struct.pack("<I", self.epoch) + bytes([int(self.have_commit)]) + self.committed + self.head
        o += struct.pack("<II", self.seq, self.acked)
        return hashlib.sha256(o).digest()

    # ---- text protocol shared with tests/step_test.c ------------------------------------------
    def line(self, tag, status, effects=None):
        s = f"{tag} st={status} n={len(effects) if effects else 0}"
        for i, (k, q, c) in enumerate(effects or []): s += f" i{i}={k}:{q}:{c}"
        d = self.digest()
        return s + f" seq={self.seq} acked={self.acked} dig={d.hex() if d else '-'} head={self.head.hex()}"

def genesis_line(g):
    x = lambda v: format(v, "x")
    out = ["G", x(g["present"])] + [x(k) for k in g["kinds"]] + [x(g["key_present"]), x(g["halt_budget"])]
    for b in g["bud"]:
        out += [x(b["t"]), x(b["s"]), x(b["nfc"]), x(b["nfl"]), x(b["xc"][0]), x(b["xc"][1]), x(b["xl"][0]), x(b["xl"][1])]
        out += [x(v) for v in b["fc"]] + [x(v) for v in b["fl"]]
    out += [x(a) for a in g["action_tier"]] + [format(t, "064x") for t in g["table"]]
    return " ".join(out)

def message_line(m):
    if m["kind"] == MSG_HALT: return f"H {m['evidence']:x} {m['atom']:x} {m['bundle']:x}"
    if m["kind"] == MSG_BOOT: return f"B {m['digest'].hex()}"
    d = m["digest"].hex() if any(m["digest"]) else "-"
    t = format(m["table"], "064x") if m["table"] else "-"
    return f"P {m['action']:x} {m['evidence']:x} {m['atom']:x} {m['bundle']:x} {m['tier']:x} {d} {t}"

def msg(kind, action=0, evidence=0, atom=0, bundle=0, tier=0, digest=bytes(32), table=0):
    return dict(kind=kind, action=action, evidence=evidence, atom=atom, bundle=bundle, tier=tier, digest=digest, table=table)

def run(lines):
    """Replay scenario lines (the text protocol) through the model; returns the result lines."""
    out, mod = [], Model()
    for ln in lines:
        f = ln.split()
        if f[0] == "G":
            v = [int(t, 16) for t in f[1:-4]]
            kinds, kp, hb = v[1:9], v[9], v[10]
            bud, pos = [], 11
            for _ in range(4):
                t, s, nfc, nfl, xca, xcb, xla, xlb = v[pos:pos + 8]
                fc, fl = v[pos + 8:pos + 8 + MAXC], v[pos + 8 + MAXC:pos + 8 + 2 * MAXC]
                bud.append(dict(t=t, s=s, nfc=nfc, nfl=nfl, xc=(xca, xcb), xl=(xla, xlb), fc=fc, fl=fl))
                pos += 8 + 2 * MAXC
            g = dict(present=v[0], kinds=kinds, key_present=kp, halt_budget=hb, bud=bud, action_tier=v[pos:pos + 8],
                     table=[int(t, 16) for t in f[-4:]])
            out.append(mod.line("G", mod.genesis(g)))
        elif f[0] == "A":
            out.append(mod.line("A", mod.ack(int(f[1], 16))))
        else:
            if f[0] == "H": m = msg(MSG_HALT, evidence=int(f[1], 16), atom=int(f[2], 16), bundle=int(f[3], 16))
            elif f[0] == "B": m = msg(MSG_BOOT, digest=bytes.fromhex(f[1]))
            else:
                dg = bytes(32) if f[6] == "-" else bytes.fromhex(f[6])
                m = msg(MSG_PROPOSE_TX, action=int(f[1], 16), evidence=int(f[2], 16), atom=int(f[3], 16),
                        bundle=int(f[4], 16), tier=int(f[5], 16), digest=dg, table=0 if f[7] == "-" else int(f[7], 16))
            st, fx = mod.step(m)
            out.append(mod.line(f[0], st, fx))
    return out

if __name__ == "__main__":
    print("models/step_model.py is a library; run models/step_check.py")

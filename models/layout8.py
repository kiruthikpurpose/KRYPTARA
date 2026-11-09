# Tiered policies on the 8-atom layout, derived from the interval theorem. [C]
# Atoms: 0 OEM-1(H1) 1 OEM-2(H2) 2 OWN-1(H1) 3 OWN-2(H2) 4 ESC-1(H1) 5 ESC-2(H2) 6 PRES(site) 7 WIT(publicity)
# H1 = SHA-2 family, H2 = Keccak family. WIT is an *exposure* atom: always obtainable by an attacker
# (logging is not consent), so it is added to every compromise set.
import itertools
from interval import upper, lower

N = 8; P = (1 << N) - 1
OEM, OWN, ESC = 0b00000011, 0b00001100, 0b00110000
H1, H2 = 0b00010101, 0b00101010
SITE, LOG = 1 << 6, 1 << 7
EXPOSURE = LOG
CUST = [1 << i for i in range(6)]
GROUPS = [OEM, OWN, ESC]; FAMS = [H1, H2]

def unions(base, k):
    if k == 0: return [0]
    return sorted({sum(set_) if False else _u(c) for c in itertools.combinations(base, k)})
def _u(c):
    r = 0
    for x in c: r |= x
    return r

comp1 = sorted({x | EXPOSURE for x in CUST + GROUPS + FAMS + [SITE]})
def comp(t): return sorted({_u(c) | EXPOSURE for c in itertools.combinations(comp1, t)}) if t else [EXPOSURE]

def table(pred):
    t = 0
    for m in range(1 << N):
        if pred(m): t |= 1 << m
    return t
def C(m): return sum(1 for g in GROUPS if m & g)
def F(m): return sum(1 for f in FAMS if m & f)
def K(m): return bin(m & 0b111111).count("1")
def p(m): return bool(m & SITE)
def w(m): return bool(m & LOG)

def monotone(t):
    for m in range(1 << N):
        if (t >> m) & 1:
            for i in range(N):
                if not (t >> (m | 1 << i)) & 1: return False
    return True
def check(name, t, Ac, Al):
    U = upper(N, Ac); Lo = lower(N, Al)
    ok_u = (t & ~U) == 0; ok_l = (Lo & ~t) == 0
    exists = (Lo & ~U) == 0
    print(f"  {name:10s} monotone={monotone(t)} safe={ok_u} live={ok_l} interval_nonempty={exists} "
          f"|f|={bin(t).count('1'):3d} |U|={bin(U).count('1'):3d} |Lo|={bin(Lo).count('1'):3d}")
    return ok_u and ok_l

print("Layout: dual + presence + publicity (8 atoms)")
loss_single = sorted(set(CUST + GROUPS + FAMS + [SITE, LOG]))
# OPERATE / AUTHORITY tier: safe vs 1 compromise, live vs 1 loss
OPERATE = table(lambda m: (w(m) and C(m) >= 2 and (F(m) >= 2 or p(m))) or (p(m) and C(m) >= 2 and F(m) >= 2))
check("OPERATE", OPERATE, comp(1), loss_single)
# CONSTITUTION tier: safe vs any 2 compromises; live vs 1 loss of a key or a group (not family/site/log)
CONST = table(lambda m: p(m) and F(m) >= 2 and ((C(m) >= 2 and w(m)) or C(m) >= 3))
check("CONST", CONST, comp(2), sorted(set(CUST + GROUPS)))
# RECOVERY tier: safe vs 1 compromise; live vs any 2 losses among keys, groups, one family, log
#                (not both families: with all cryptography gone only presence remains, which one insider has)
loss_pairs = sorted({a | b for a, b in itertools.combinations(sorted(set(CUST + GROUPS + FAMS + [LOG])), 2)
                     if (a | b) & (H1 | H2) != (H1 | H2) or not ((a | b) >= 0 and (a == H1 and b == H2 or a == H2 and b == H1))})
loss_pairs = [x for x in loss_pairs if not ((x & H1) == H1 and (x & H2) == H2)]
RECOVERY = table(lambda m: p(m) and K(m) >= 2 and (w(m) or C(m) >= 2))
check("RECOVERY", RECOVERY, comp(1), loss_pairs + loss_single)

print("\nImpossibility checks (interval empty):")
def empty(Ac, Al): return (lower(N, Al) & ~upper(N, Ac)) != 0
print("  2-safe and live vs family loss            :", empty(comp(2), loss_single) and "impossible" or "possible")
print("  1-safe and live vs loss of BOTH families  :", empty(comp(1), [H1 | H2]) and "impossible" or "possible")
print("  CONST 2-safe & live vs site loss          :", empty(comp(2), [SITE]) and "impossible" or "possible")

print("\nRemote profile (no presence atom): atoms 0..5 + WIT")
def remote_comp(t):
    base = sorted({x | EXPOSURE for x in CUST + GROUPS + FAMS})
    return sorted({_u(c) | EXPOSURE for c in itertools.combinations(base, t)})
r_loss1 = sorted(set(CUST + GROUPS + FAMS + [LOG]))
print("  1-safe & live vs key/group loss           :", "possible" if not empty(remote_comp(1), sorted(set(CUST+GROUPS))) else "impossible")
print("  1-safe & live vs family loss              :", "possible" if not empty(remote_comp(1), FAMS) else "impossible")
print("  2-safe & live vs any single group loss    :", "possible" if not empty(remote_comp(2), GROUPS) else "impossible")
print("  1-safe & live vs any two group losses     :", "possible" if not empty(remote_comp(1), [a|b for a,b in itertools.combinations(GROUPS,2)]) else "impossible")

print("\nNano profile (one family H1 for all custody atoms; + presence + publicity)")
def nano_comp(t):
    base = sorted({x | EXPOSURE for x in CUST + GROUPS + [H1 | H2, SITE]})   # one family covers all custody atoms
    return sorted({_u(c) | EXPOSURE for c in itertools.combinations(base, t)}) if t else [EXPOSURE]
print("  1-safe (incl. hash break) & live vs group loss :", "possible" if not empty(nano_comp(1), GROUPS) else "impossible")
print("  1-safe (incl. hash break) & live vs hash loss  :", "possible" if not empty(nano_comp(1), [H1 | H2]) else "impossible")

for name, t in [("OPERATE", OPERATE), ("CONST", CONST), ("RECOVERY", RECOVERY)]:
    print(f"{name} table (256-bit, little-endian 64-bit words): " + " ".join(f"{(t >> (64*i)) & ((1<<64)-1):016x}" for i in range(4)))

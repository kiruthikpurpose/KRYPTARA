# Interval theorem for safe-and-live monotone authority policies. [C]
# Claim: for compromise structure Ac and loss structure Al over atoms P,
#   Safe(f)  <=> f(A)=0 for all A in Ac      <=> f <= U  where U(S)=[S not subset of any A]
#   Live(f)  <=> f(P\L)=1 for all L in Al    <=> f >= Lo where Lo = up-closure of {P\L}
#   so the safe-and-live set is the lattice interval [Lo, U], non-empty iff A|L != P for all A,L.
import numpy as np, random, itertools, sys
from policy_study import all_monotone, bit

def upper(n, Ac):
    t = 0
    for m in range(1 << n):
        if all((m & ~a) for a in Ac): t |= 1 << m
    return t
def lower(n, Al):
    P = (1 << n) - 1; t = 0
    for m in range(1 << n):
        if any(((P & ~l) & ~m) == 0 for l in Al): t |= 1 << m
    return t
def q2_mixed(n, Ac, Al):
    P = (1 << n) - 1
    return all((a | l) != P for a in Ac for l in Al)

def brute(T, n, Ac, Al):
    P = (1 << n) - 1
    ok = np.ones(len(T), bool)
    for a in Ac: ok &= (bit(T, a) == 0)
    for l in Al: ok &= (bit(T, P & ~l) == 1)
    return ok

def interval_mask(T, U, Lo):
    U = np.uint64(U); Lo = np.uint64(Lo)
    return ((T & ~U) == 0) & ((Lo & ~T) == 0)

if __name__ == "__main__":
    # 1. random structures, exhaustive over all monotone functions, n = 3,4,5
    random.seed(7); trials = 0; mism = 0
    for n in (3, 4, 5):
        T = all_monotone(n)
        for _ in range(400 if n < 5 else 250):
            k1 = random.randint(1, 5); k2 = random.randint(1, 5)
            Ac = [random.randrange(1 << n) for _ in range(k1)]
            Al = [random.randrange(1 << n) for _ in range(k2)]
            ok = brute(T, n, Ac, Al)
            iv = interval_mask(T, upper(n, Ac), lower(n, Al))
            exists = bool(ok.any())
            trials += 1
            if (ok != iv).any() or exists != q2_mixed(n, Ac, Al): mism += 1
    print(f"[1] random structures tested={trials}, mismatches (brute vs interval, existence vs mixed-Q2)={mism}")

    # 2. reproduce earlier 6-slot counts as interval sizes
    T6 = all_monotone(6)
    n = 6; groups = [0b000011, 0b001100, 0b110000]; atoms = [0b010101, 0b101010]
    singles = [1 << i for i in range(6)]
    for name, Ac, Al in [
        ("slot+group (safe & live)", singles + groups, singles + groups),
        ("critical: safe vs slot,group,family; live vs slot,group", singles + groups + atoms, singles + groups),
        ("safe vs slot,group,family; live vs slot,group,family", singles + groups + atoms, singles + groups + atoms)]:
        U = upper(n, Ac); Lo = lower(n, Al)
        cnt = int(interval_mask(T6, U, Lo).sum()); b = int(brute(T6, n, Ac, Al).sum())
        print(f"[2] {name:58s} interval size={cnt:>9,} brute={b:>9,} Q2={q2_mixed(n,Ac,Al)}  U=0x{U:016x} Lo=0x{Lo:016x}")

    # 3. class-count law: atoms partitioned into k classes of size c; fault = whole class.
    #    safe vs any t compromised classes, live vs any s lost classes  <=>  k >= t+s+1
    print("[3] class-count law (partition into k classes; t compromise faults, s loss faults):")
    bad = 0
    for k in range(1, 7):
        for c in (1,):
            n = k * c
            cls = [sum(1 << (i * c + j) for j in range(c)) for i in range(k)]
            for t in range(0, 3):
                for s in range(0, 3):
                    Ac = [sum(x) for x in itertools.combinations(cls, t)] if t else [0]
                    Al = [sum(x) for x in itertools.combinations(cls, s)] if s else [0]
                    if t > k or s > k: continue
                    ex = q2_mixed(n, Ac, Al) and lower(n, Al) & ~upper(n, Ac) == 0
                    law = k >= t + s + 1
                    if ex != law: bad += 1
    print(f"    disagreements with k >= t+s+1 : {bad}")

import itertools
A={"H_SHA2":1,"H_KECCAK":2,"LATTICE":4,"DLOG_EC":8,"FACTOR":16}
K={"ML-DSA":A["LATTICE"]|A["H_KECCAK"],"SLH-SHAKE":A["H_KECCAK"],"LMS-SHA256":A["H_SHA2"],"SLH-SHA2":A["H_SHA2"],"ECDSA":A["DLOG_EC"]|A["H_SHA2"]}
def valid(S,d=2,t=2):
    S=list(S)
    if len(S)<t: return False
    # need >=d members pairwise disjoint
    for D in itertools.combinations(S,d):
        if all(K[a]&K[b]==0 for a,b in itertools.combinations(D,2)): return True
    return False
def single_fail_safe(slots,valid_fn):
    # attacker holds all keys depending on assumption a; may any valid S be a subset?
    for bit in A.values():
        F=[k for k in slots if K[k]&bit]
        for r in range(1,len(F)+1):
            for S in itertools.combinations(F,r):
                if valid_fn(S): return False,bit
    return True,None
slots=["ML-DSA","SLH-SHAKE","LMS-SHA256"]
for r in (2,3):
    for S in itertools.combinations(slots,r): print(S,valid(S))
print("2-of-3 plain safe?",single_fail_safe(slots,lambda S:len(S)>=2))
print("disjoint rule safe?",single_fail_safe(slots,valid))
print("liveness: valid quorums",[S for r in (2,3) for S in itertools.combinations(slots,r) if valid(S)])
# degenerate policy: all slots share keccak
print("lint bad set:",single_fail_safe(["ML-DSA","SLH-SHAKE"],valid),[S for S in [("ML-DSA","SLH-SHAKE")] if valid(S)])

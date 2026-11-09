"""B.2 disjoint-quorum checker. Key compromise condition = monotone DNF over assumption-failure atoms.
single key:   fails if ANY atom in A(k) fails   -> DNF = [{a} for a in A(k)]
AND-composite (both must verify): fails only if BOTH components fail -> cross product of component DNFs
OR-accept (either verifies): fails if EITHER component fails -> union of DNFs (never allowed for authority)."""
import itertools, sys
def single(A): return [frozenset([a]) for a in A]
def AND(*ds): # forging conj of components: need a failing set from each
    out=[frozenset().union(*c) for c in itertools.product(*ds)]
    return minimise(out)
def OR(*ds): return minimise([c for d in ds for c in d])
def minimise(d):
    d=set(d); return [c for c in d if not any(o<c for o in d)]
def broken(dnf,F): return any(c<=F for c in dnf)
def atoms(keys): return sorted({a for k in keys.values() for c in k for a in c})
def cover_number(keys,S,theft=0,amax=6):
    """min #assumption failures (given up to `theft` stolen keys, chosen adversarially) that make every key in S forgeable.
    returns (a_min). exhaustive."""
    at=atoms({k:keys[k] for k in S})
    for a in range(0,amax+1):
        for F in itertools.combinations(at,a):
            F=frozenset(F)
            rest=[k for k in S if not broken(keys[k],F)]
            if len(rest)<=theft: return a
    return 99
def accepted_sets(keys,slots,f,t=0,minsize=2):
    """all signer sets S (>=minsize) with cover_number > f  (i.e. f assumption failures + t thefts cannot forge S)"""
    res=[]
    for m in range(minsize,len(slots)+1):
        for S in itertools.combinations(slots,m):
            if cover_number(keys,S,t)>f: res.append(S)
    return res
def minimal(sets):
    sets=[frozenset(s) for s in sets]; return [tuple(sorted(s)) for s in sets if not any(o<s for o in sets)]
def is_safe(keys,sets,f,t=0): return all(cover_number(keys,S,t)>f for S in sets)
if __name__=='__main__':
    K={'ML-DSA':single({'MLWE','KECCAK'}),'LMS-SHA256':single({'SHA2'}),'SLH-DSA-SHAKE':single({'KECCAK'}),
       'SLH-DSA-SHA2':single({'SHA2'}),'ECDSA':single({'ECDLP','SHA2'}),'Ed25519':single({'ECDLP','SHA2'}),
       'LMS-SHAKE':single({'KECCAK'}),'FN-DSA':single({'NTRU','KECCAK'})}
    slots=('ML-DSA','LMS-SHA256','SLH-DSA-SHAKE')
    print('f=1 accepted sets for 3-slot set:',accepted_sets(K,slots,1))
    print('plain any-2-of-3 safe at f=1?',is_safe(K,[s for s in itertools.combinations(slots,2)],1))
    for S in itertools.combinations(slots,2): print(S,'cover number',cover_number(K,S))
    # 4-slot with LMS-SHAKE / SLH-SHA2: shows only two waists
    s4=('ML-DSA','LMS-SHA256','SLH-DSA-SHAKE','SLH-DSA-SHA2','LMS-SHAKE')
    print('5 slots, f=1 minimal accepted:',minimal(accepted_sets(K,s4,1)))
    # composite
    K['ML-DSA^Ed25519']=AND(K['ML-DSA'],K['Ed25519'])
    print('composite ML-DSA^Ed25519 min failing sets:',sorted(map(sorted,K['ML-DSA^Ed25519'])))
    print('composite alone cover number (needs one signer):',cover_number(K,('ML-DSA^Ed25519',)))
    K['ML-DSA|Ed25519']=OR(K['ML-DSA'],K['Ed25519'])
    print('OR-accept hybrid min failing sets:',sorted(map(sorted,K['ML-DSA|Ed25519'])),'cover number',cover_number(K,('ML-DSA|Ed25519',)))
    # post-CRQC epoch: ECDLP already failed -> remove atom => composite degrades to its PQ half
    def drop(dnf,atom): return minimise([c-{atom} for c in dnf])
    post=drop(K['ML-DSA^Ed25519'],'ECDLP'); print('post-CRQC composite failing sets:',sorted(map(sorted,post)))
    # (f=1,t=1): one assumption failure + one key theft
    print('2-slot disjoint pair safe at (f=1,t=1)?',is_safe(K,[('ML-DSA','LMS-SHA256')],1,1))
    trip=('ML-DSA','LMS-SHA256','SLH-DSA-SHAKE')
    print('all 3 signers (f=1,t=1) safe?',is_safe(K,[trip],1,1), ' (f=1,t=0)',is_safe(K,[trip],1,0))
    print('all 3 signers cover number',cover_number(K,trip), ' with t=1',cover_number(K,trip,1))
    print('ML-DSA+LMS+SLHSHA2? cover',cover_number(K,('ML-DSA','LMS-SHA256','SLH-DSA-SHA2')),'t=1',cover_number(K,('ML-DSA','LMS-SHA256','SLH-DSA-SHA2'),1))

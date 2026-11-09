# Policies as monotone truth tables; single-fault-tolerant (SFT) counts. [C]
import numpy as np, itertools
def all_monotone(n):
    if n<=5:
        out=[0,1]
        for k in range(1,n+1):
            half=1<<(k-1); prev=out; arr=np.array(prev,dtype=np.uint64); mask=np.uint64((1<<half)-1)
            new=[]
            for g in prev:
                sel=(np.uint64(g)&~arr&mask)==0
                new.extend((int(g)|(int(h)<<half)) for h in arr[sel])
            out=new
        return np.array(out,dtype=np.uint64)
    prev=all_monotone(5); half=32; mask=np.uint64((1<<32)-1); chunks=[]
    for g in prev:
        sel=(g&~prev&mask)==0
        chunks.append(g | (prev[sel]<<np.uint64(32)))
    return np.concatenate(chunks)
def bit(tab,m): return (tab>>np.uint64(m))&np.uint64(1)
def study(name,n,groups,atoms,tol_atoms=True):
    full=(1<<n)-1
    faults=[1<<i for i in range(n)]+[sum(1<<i for i in g) for g in groups]
    if tol_atoms: faults+= [sum(1<<i for i in a) for a in atoms]
    faults=sorted(set(faults))
    T=all_monotone(n)
    ok=np.ones(len(T),bool)
    for F in faults:
        ok&=(bit(T,F)==0)&(bit(T,full&~F)==1)
    print(f"{name}: slots={n}, monotone fns={len(T):,}, fault sets={len(faults)}, single-fault-tolerant (safe AND live)={int(ok.sum()):,}")
    return T[ok],faults

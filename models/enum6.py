# Exhaustive study of policies as monotone Boolean functions over slots. [C]
import numpy as np, itertools, sys, time
def monotone(n):
    # list of truth tables (python ints, bit m = f(mask m)) of all monotone functions on n vars
    if n==0: return [0,1]
    prev=monotone(n-1); half=1<<(n-1)
    out=[]
    arr=np.array(prev,dtype=np.uint64)
    for g in prev:      # g = f restricted to x_n=0
        ok = (arr & np.uint64(~g & ((1<<half)-1))) ==0 if False else None
    # g <= h  (g subset of h)
    res=[]
    for g in prev:
        mask=np.uint64((1<<half)-1)
        sel = (np.uint64(g) & ~arr & mask)==0
        for h in arr[sel]:
            res.append(int(g)|(int(h)<<half))
    return res
t=time.time()
F={n:monotone(n) for n in range(0,6)}
print({n:len(F[n]) for n in F}, "expected Dedekind 2,3,6,20,168,7581", time.time()-t)
# n=6 count via numpy without materialising python ints
prev=np.array(F[5],dtype=np.uint64); half=32; mask=np.uint64((1<<32)-1)
cnt=0
for g in prev:
    cnt+=int(((g & ~prev & mask)==0).sum())
print("monotone functions on 6 vars:",cnt,"(Dedekind D(6)=7828354)")

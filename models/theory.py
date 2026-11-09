# Lemmas about single-fault-tolerant authority. [C] brute force over ALL monotone functions on <=6 slots
import numpy as np, itertools
from policy_study import all_monotone, bit
def faults_of(n,groups,atoms,use_atoms=True):
    F=[1<<i for i in range(n)]+[sum(1<<i for i in g) for g in groups]
    if use_atoms: F+=[sum(1<<i for i in a) for a in atoms]
    return sorted(set(F))
def q2(n,F):
    U=(1<<n)-1
    return not any((a|b)==U for a in F for b in F)
def maximal_policy(n,F):
    # S authorised iff S not contained in any single fault set
    t=0
    for m in range(1<<n):
        if not any((m&~f)==0 for f in F): t|=1<<m
    return t
cases={
 "2 groups x2 (4 slots), slot+group":(4,[[0,1],[2,3]],[],False),
 "3 groups x1 (3 slots), slot+group":(3,[[0],[1],[2]],[],False),
 "3 groups x2 (6 slots), slot+group":(6,[[0,1],[2,3],[4,5]],[[0,2,4],[1,3,5]],False),
 "3 groups x2 (6 slots), slot+group+2 atoms":(6,[[0,1],[2,3],[4,5]],[[0,2,4],[1,3,5]],True),
 "3 slots, 3 groups, 3 distinct atoms":(3,[[0],[1],[2]],[[0],[1],[2]],True),
}
print("Q2 condition (no two fault sets cover all slots) vs. existence of a safe AND live policy:")
for k,(n,g,a,u) in cases.items():
    F=faults_of(n,g,a,u); T=all_monotone(n); U=(1<<n)-1
    ok=np.ones(len(T),bool)
    for f in F: ok&=(bit(T,f)==0)&(bit(T,U&~f)==1)
    print(f"  {k:46s} Q2={q2(n,F)!s:5s}  safe+live policies={int(ok.sum()):>9,}")
# project's dual layout: slots 0 OEM-A(SHA2) 1 OEM-B(KEC) 2 OWN-A 3 OWN-B 4 ESC-A 5 ESC-B
n=6; groups=[[0,1],[2,3],[4,5]]; atoms=[[0,2,4],[1,3,5]]
Fall=faults_of(n,groups,atoms,True); Fgs=faults_of(n,groups,atoms,False)
Tmax=maximal_policy(n,Fall)
print("maximal safe policy (auth iff not covered by ONE fault set): popcount",bin(Tmax).count('1'),"table 0x%016x"%Tmax)
# is it the same as the pair rule?
def auth_pair(m):
    s=[i for i in range(6) if m>>i&1]
    atom={0:0,1:1,2:0,3:1,4:0,5:1}; grp={0:0,1:0,2:1,3:1,4:2,5:2}
    return any(grp[i]!=grp[j] and atom[i]!=atom[j] for i in s for j in s if i<j)
print("maximal safe policy == 'one pair from two groups with different atoms':",all(((Tmax>>m)&1)==int(auth_pair(m)) for m in range(64)))
T=all_monotone(6); U=63
safe=np.ones(len(T),bool)
for f in Fall: safe&=(bit(T,f)==0)
print("safe policies (any liveness) with atom faults:",f"{int(safe.sum()):,}")
# critical policy: safe vs everything, live vs single slot/group loss
crit=safe.copy()
for f in Fgs: crit&=(bit(T,U&~f)==1)
print("CRITICAL-type policies (safe vs slot,group,atom; live vs slot,group loss):",f"{int(crit.sum()):,}", " includes maximal:",bool((T[crit]==np.uint64(Tmax)).any()))
# repair policy: safe vs slot+group; live vs any single loss incl atom
rep=np.ones(len(T),bool)
for f in Fgs: rep&=(bit(T,f)==0)
for f in Fall: rep&=(bit(T,U&~f)==1)
print("REPAIR-type policies (safe vs slot,group; live vs slot,group,ATOM loss):",f"{int(rep.sum()):,}")
# lattice: critical policies are tightenings of the maximal; show tighten-only inclusion check cost
cr=T[crit]; print("critical policies that are subsets of the maximal:",int(((cr&~np.uint64(Tmax))==0).sum()),"of",len(cr))
# smallest critical policies by popcount
pc=np.array([bin(int(x)).count('1') for x in cr[:200000]])
print("min popcount among first 200k critical policies:",pc.min(),"; maximal has",bin(Tmax).count('1'))

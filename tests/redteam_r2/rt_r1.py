import itertools, random
def monos(n):
    N=1<<n; subs=range(N)
    # enumerate monotone boolean functions as sets of accepted masks (upsets) by recursion over masks
    res=[]
    order=sorted(subs,key=lambda m:-bin(m).count('1'))
    def rec(i,acc):
        if i==len(order): res.append(frozenset(acc)); return
        m=order[i]
        # m can be accepted only if all supersets (already decided) accepted
        sup_ok=all((s in acc) for s in range(N) if s&m==m and s!=m)
        rec(i+1,acc)               # reject m
        if sup_ok: rec(i+1,acc|{m})
    rec(0,frozenset()); return res
for n in (3,4,5):
    print('Dedekind',n,len(monos(n)))
n=5
M=monos(n)
# slots 0..4. groups: OEM{0,1} OWNER{2} ESCROW{3,4}; atoms: H1{0,2,3} H2{1,4}  (slot0,2,3 under hash A; 1,4 under hash B)
groups=[{0,1},{2},{3,4}]; atoms=[{0,2,3},{1,4}]
mask=lambda s:sum(1<<i for i in s)
D=[mask({i}) for i in range(n)]+[mask(g) for g in groups]+[mask(a) for a in atoms]
def safe(A): return all(f not in A for f in D)   # table[F]=0 (monotone => subsets of F too)
def live(A,held=(1<<n)-1): return any(a&~held==0 for a in A)
def liveQ(A): return all(((1<<n)-1)&~f in A for f in D)   # survive loss of any declared fault
nonempty=[A for A in M if A]
ok=[A for A in nonempty if safe(A) and live(A)]
print('monotone nonempty',len(nonempty),'pass thesis (a)+(c)',len(ok))
# hidden event: one human controls two slots (any pair) -> single realistic event
def hidden(A): return any(mask({i,j}) in A for i,j in itertools.combinations(range(n),2))
bad=[A for A in ok if hidden(A)]
print('pass but a 2-slot single-person event authorises:',len(bad),f'{len(bad)/len(ok):.1%}')
okQ=[A for A in ok if liveQ(A)]
print('also survive loss of any declared fault (P\\F in A):',len(okQ))
# pairs-hidden-resistant tables
res=[A for A in ok if not hidden(A)]
print('pass and robust to any 2-slot person:',len(res))
# Q2 check for nano: all slots one atom
print('nano atom covers P => liveness vs hash fault impossible')
L=[mask({i}) for i in range(n)]+[mask(g) for g in groups]
liveL=lambda A: all(((1<<n)-1)&~f in A or any(a&f==0 for a in A) for f in L)
okL=[A for A in ok if liveL(A)]
print('pass (a)+(c) AND some authorised set survives loss of any slot/group:',len(okL))
# brick example: tighten-only to all-slots
full=frozenset({(1<<n)-1}); print('table requiring all 5 passes (a),(c):',safe(full) and live(full),'; survives loss of one slot:',liveL(full))
print('tighten-only chain length from max-permissive ok table to full:', 'any ok table can be tightened to full')

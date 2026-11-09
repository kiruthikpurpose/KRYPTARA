import random, itertools
crit=["Security","TCB","FlashRAM","Certif","Extens","Portab","Migr","Longev","Compreh"]
W=[18,12,8,10,10,8,8,18,8]
S={ # 1-5, higher better; judgements [H]
"A1 monolithic PQ boot+update":[3,2,4,2,2,3,4,2,4],
"A2 policy-engine-centric":[2,1,2,2,5,3,2,3,2],
"A3 authority-ledger core+adapters":[5,4,4,4,4,4,3,5,3],
"A4 hourglass @verify waist":[4,4,5,4,4,5,4,4,4],
"A5 microkernel/capability":[4,2,2,3,3,2,2,3,2],
"A6 protocol-gateway-centric":[2,3,5,3,3,4,5,2,4],
"S  synthesis (A3 core in A4 layering)":[5,4,4,5,5,5,3,5,3],
}
def score(w,s): return sum(a*b for a,b in zip(w,s))/sum(w)
print("W sum",sum(W))
for k,v in S.items(): print(f"{k:42s} {score(W,v):.2f}")
alts={"security-first":[30,15,5,10,5,5,5,20,5],"cost/migration-first":[10,8,15,6,6,10,25,10,10],
"ecosystem-first":[10,5,5,8,20,15,10,12,15],"certification-first":[15,15,8,25,5,5,5,12,10],"uniform":[1]*9}
for n,w in alts.items():
    r=sorted(S,key=lambda k:-score(w,S[k]))
    print(n,[(k[:2].strip(),round(score(w,S[k]),2)) for k in r[:4]])
# OAT +-50%
flips=0;tot=0
for i in range(9):
  for f in (0.5,1.5):
    w=W[:];w[i]*=f
    r=max(S,key=lambda k:score(w,S[k])); tot+=1
    if not r.startswith("S "): flips+=1; print("flip",crit[i],f,r)
print("OAT flips",flips,"of",tot)
# excluding S (the 'hindsight' candidate): does A3 or A4 win?
base={k:v for k,v in S.items() if not k.startswith("S ")}
random.seed(1); N=100000; win={k:0 for k in S}; win2={k:0 for k in base}
for _ in range(N):
  g=[random.gammavariate(1,1) for _ in range(9)]
  win[max(S,key=lambda k:score(g,S[k]))]+=1
  win2[max(base,key=lambda k:score(g,base[k]))]+=1
print("Dirichlet(1) all:",{k[:2]:round(v/N,3) for k,v in win.items()})
print("Dirichlet(1) w/o S:",{k[:2]:round(v/N,3) for k,v in win2.items()})
# score noise: +-1 on each cell w.p. .25
win3={k:0 for k in S}
for _ in range(20000):
  sc={k:[min(5,max(1,x+random.choice([-1,0,0,1]))) for x in v] for k,v in S.items()}
  win3[max(S,key=lambda k:score(W,sc[k]))]+=1
print("score-noise wins:",{k[:2]:round(v/20000,3) for k,v in win3.items()})
# gap if S dev-comprehension and migration scored 2 (pessimistic)
S2=dict(S); S2["S  synthesis (A3 core in A4 layering)"]=[5,4,4,5,5,5,2,5,2]
print("pessimistic S:",round(score(W,S2["S  synthesis (A3 core in A4 layering)"]),2),"vs A4",round(score(W,S["A4 hourglass @verify waist"]),2))

# Cross-check policy8.c against an independent Python reference on random structures and tables. [C]
import random, subprocess, itertools
N = 8; P = 255
def up_closure(seeds):
    t = 0
    for m in range(256):
        if any((s & ~m) == 0 for s in seeds): t |= 1 << m
    return t
def ref_upper(f, k, expo):
    k = min(k, len(f))
    unions = [expo] if k == 0 else [(sum_or(c) | expo) for c in itertools.combinations(f, k)]
    return sum(1 << m for m in range(256) if not any((m & ~u) == 0 for u in unions))
def ref_lower(l, k, absent):
    if k > len(l): return (1 << 256) - 1
    unions = [absent] if k == 0 else [(sum_or(c) | absent) for c in itertools.combinations(l, k)]
    return sum(1 << m for m in range(256) if any(((P & ~u) & ~m) == 0 for u in unions))
def sum_or(c):
    r = 0
    for x in c: r |= x
    return r
def monotone(t):
    return all(not ((t >> m) & 1) or all((t >> (m | 1 << i)) & 1 for i in range(8)) for m in range(256))
random.seed(11); cases = []; lines = []
for _ in range(3000):
    nf = random.randint(1, 12); nl = random.randint(1, 12)
    kc = random.choice([0, 1, 1, 2]); kl = random.choice([0, 1, 1, 2])
    expo = random.choice([0, 0, 0x80, 0x40]); absent = random.choice([0, 0, 0x40, 0x0c])
    f = [random.randrange(1, 256) for _ in range(nf)]; l = [random.randrange(1, 256) for _ in range(nl)]
    if random.random() < 0.7: t = up_closure([random.randrange(256) for _ in range(random.randint(1, 6))])
    else: t = random.getrandbits(256)
    cases.append((f, l, kc, kl, expo, absent, t))
    words = " ".join(f"{(t >> (32 * i)) & 0xffffffff:x}" for i in range(8))
    lines.append(f"{nf} {nl} {kc} {kl} {expo:x} {absent:x} " + " ".join(f"{x:x}" for x in f) + " " +
                 " ".join(f"{x:x}" for x in l) + " " + words)
out = subprocess.run(["./p8test"], input=f"{len(cases)}\n" + "\n".join(lines) + "\n",
                     capture_output=True, text=True).stdout.split("\n")
bad = 0; admitted = 0
for (f, l, kc, kl, expo, absent, t), row in zip(cases, out):
    U_s, L_s, mono, within = row.split()
    U = ref_upper(f, kc, expo); L = ref_lower(l, kl, absent)
    ok = int(U_s, 16) == U and int(L_s, 16) == L and int(mono) == monotone(t) and \
         int(within) == (((t & ~U) == 0) and ((L & ~t) == 0))
    bad += not ok; admitted += int(within) and int(mono)
print(f"cases={len(cases)} mismatches={bad} admitted(monotone & in interval)={admitted}")

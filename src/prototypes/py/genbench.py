import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from genvec import K0, K1, K2
random.seed(7)
out = []
for nm, k in [("w4h5", K0), ("w8h5", K1), ("w4h10", K2)]:
    for i in range(64):
        m = random.randbytes(52)
        out.append(f"{nm} {k.pub().hex()} {m.hex()} {k.sign(m, i % (1 << k.h)).hex()}")
open(os.path.join(os.path.dirname(__file__), "..", "test", "bench_vectors.txt"), "w").write("\n".join(out) + "\n")

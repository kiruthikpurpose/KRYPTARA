# Differential check of src/kernel.c against the Python reference. [C]
#  - tier engine: for every tier and all 256 evidence sets, the C engine authorises exactly the
#    sets the reference tier table does, and no single-bit flip in any stored copy widens authority
#  - chain hash: C and models/hash_chain.py agree byte for byte on random and edge-case vectors
# Expects ./kernel_test in the working directory (built by scripts/run_all_checks.sh).
import os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint import HALT, OPERATE, CONST, RECOVERY
from hash_chain import domain_hash

TIERS = [HALT, OPERATE, CONST, RECOVERY]

def main():
    failures = 0
    out = subprocess.run(["./kernel_test", "tiers"], input=" ".join(f"{t:064x}" for t in TIERS),
                         capture_output=True, text=True).stdout.split("\n")
    for tier, ref in enumerate(TIERS):
        if int(out[tier], 16) != ref:
            failures += 1; print(f"  tier {tier}: C engine differs from reference tier table")
    print(f"  tier engine: {len(TIERS)} tiers x 256 evidence sets compared")
    inj = dict(kv.split("=") for kv in out[len(TIERS)].split())
    print(f"  bit-flip injection: flips={inj['flips']} widened={inj['widened']} undetected={inj['undetected']}")
    if int(inj["flips"]) != 4 * 2 * 256 or int(inj["widened"]) or int(inj["undetected"]): failures += 1

    rng = random.Random(11)
    cases = [(b"", bytes(32), b""), (b"CHAIN_COMMIT", bytes(32), b"x"), (b"A" * 255, bytes([255]) * 32, b"\x00" * 64)]
    for _ in range(500):
        cases.append((rng.randbytes(rng.randint(0, 40)), rng.randbytes(32), rng.randbytes(rng.randint(0, 300))))
    hx = lambda b: b.hex() if b else "-"
    lines = "\n".join(f"{hx(d)} {hx(p)} {hx(y)}" for d, p, y in cases) + "\n"
    got = subprocess.run(["./kernel_test", "chain"], input=lines, capture_output=True, text=True).stdout.split()
    mism = sum(1 for (d, p, y), g in zip(cases, got) if g != domain_hash(d, p, y).hex()) + abs(len(got) - len(cases))
    print(f"  chain hash: {len(cases)} vectors, C vs Python mismatches={mism}")
    failures += mism
    print(f"kernel_check failures={failures}")
    return failures

if __name__ == "__main__":
    sys.exit(1 if main() else 0)

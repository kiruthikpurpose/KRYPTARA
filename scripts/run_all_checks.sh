#!/usr/bin/env bash
# Reproduces every computed claim in the repository that can run on a laptop. Exit non-zero on any failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"; BUILD="$ROOT/build"; mkdir -p "$BUILD"
echo "== [1] interval theorem + class-count law (models/interval.py)";      (cd models && python3 interval.py)
echo "== [1b] exhaustive (not random) check, n=3,4, all monotone functions x all k<=2 fault structures (models/exhaustive_small.py)"
(cd models && python3 exhaustive_small.py)
echo "== [1c] Z3-mechanised instance verification of U/Lo maximality/minimality (models/z3_mechanised.py)"
(cd models && python3 z3_mechanised.py)   # skips cleanly (exit 0) if z3-solver isn't installed in this interpreter
echo "== [2] tier tables, budgets, impossibility catalogue (models/lint.py)"; (cd models && python3 lint.py && python3 tiers_extra.py)
echo "== [3] C admission vs Python reference";
gcc -O2 -Wall -o "$BUILD/p8test" src/p8test.c; cp "$BUILD/p8test" models/p8test; (cd models && python3 p8check.py); rm -f models/p8test
echo "== [4] projection test (TEST-ADM-05)"; gcc -O2 -o "$BUILD/test_projection" tests/test_projection.c && "$BUILD/test_projection"
echo "== [5] hardened-API fail-closed checks (red-team R2)"; gcc -O1 -I src -o "$BUILD/fixcheck" tests/redteam_r2/fixcheck.c 2>/dev/null || gcc -O1 -o "$BUILD/fixcheck" tests/redteam_r2/fixcheck.c -I tests/redteam_r2; "$BUILD/fixcheck"
echo "== [6] red-team R2 path analysis (informational)"; (cd tests/redteam_r2 && python3 r2_absent.py | tail -8)
if command -v arm-none-eabi-gcc >/dev/null; then echo "== [7] Cortex-M0+ size"; arm-none-eabi-gcc -mcpu=cortex-m0plus -mthumb -Os -c src/policy8.c -o "$BUILD/policy8_m0.o" && arm-none-eabi-size "$BUILD/policy8_m0.o"; fi
echo "== [8] GATE-12 hazard sweep (simulations/hazard_sweep.py)"; python3 simulations/hazard_sweep.py | tail -3
echo "== [9] host timing of admission table primitives (tests/bench_policy8.c)"
gcc -O2 -o "$BUILD/bench_policy8" tests/bench_policy8.c && "$BUILD/bench_policy8"
echo "== [10] CLM-24 hazard parameter-uncertainty sweep, quick mode (simulations/fleet_uncertainty.py --quick)"
python3 simulations/fleet_uncertainty.py --quick | tail -4
echo "== [11] REQ-STALE-01 reference check (models/stale_bound.py)"; (cd models && python3 stale_bound.py | tail -3)
echo "== [12] REQ-PUB-01 reference check (models/witness_receipt.py)"; (cd models && python3 witness_receipt.py | tail -3)
echo "== [13] REQ-HALT-01 property test (models/halt_budget.py)"; (cd models && python3 halt_budget.py)
echo "== [14] REQ-CHAIN-01 hash-chain reference check (models/hash_chain.py)"; (cd models && python3 hash_chain.py | tail -3)
echo "== [15] legacy requirements reconciliation regenerates cleanly (scripts/reconcile_legacy_requirements.py)"
python3 scripts/reconcile_legacy_requirements.py
echo "== [16] FR-ASR-10 fuzz harness, 200,000 random-input iterations (tests/fuzz_policy8.c)"
gcc -O2 -o "$BUILD/fuzz_policy8" tests/fuzz_policy8.c && "$BUILD/fuzz_policy8"
if gcc -fsanitize=address,undefined -x c -c -o /dev/null tests/fuzz_policy8.c 2>/dev/null; then
  echo "== [16b] same harness under ASan+UBSan"
  gcc -O1 -fsanitize=address,undefined -o "$BUILD/fuzz_policy8_asan" tests/fuzz_policy8.c && "$BUILD/fuzz_policy8_asan"
fi
echo "== [17] REQ-LIFE-01 DECLARE_CLASS_DEAD check (models/class_lifecycle.py)"; (cd models && python3 class_lifecycle.py | tail -3)
echo "== [18] wire-format two-encoder differential check (models/wire_format.py)"; (cd models && python3 wire_format.py)
echo "== [19] correlated-failure (common-cause) extension of the theory (models/common_cause.py)"; (cd models && python3 common_cause.py)
echo "== [20] mutation testing of policy8.c against the full test suite (scripts/mutation_test.py)"
python3 scripts/mutation_test.py
echo "== [21] Theorem 3 machine cross-check (models/theorem3_check.py)"; (cd models && python3 theorem3_check.py | tail -3)
echo "== [22] reproducible build check (scripts/reproducible_build.sh)"; bash scripts/reproducible_build.sh
echo "== [23] second application domain: CA root governance (models/second_domain_ca_root.py)"; (cd models && python3 second_domain_ca_root.py)
echo "== [24] static stack analysis, host x86-64 (scripts/stack_analysis.sh)"; bash scripts/stack_analysis.sh
echo "== [25] crypto provider conformance suite: our sha256.c vs OpenSSL vs Python hashlib (scripts/provider_conformance.sh)"
bash scripts/provider_conformance.sh
echo "== [26] PQC conformance: ML-KEM/ML-DSA/SLH-DSA via maintained libraries (models/pqc_conformance.py)"
(cd models && python3 pqc_conformance.py)   # skips cleanly if mlkem/mldsa/dilithium-py/slh-dsa aren't installed
echo "== [27] RFC 9162 Merkle inclusion-proof reference check (models/merkle_inclusion.py)"; (cd models && python3 merkle_inclusion.py)
echo "== [28] ac-ceremony custody-graph capture/replay tool (scripts/ac_ceremony.py)"
python3 scripts/ac_ceremony.py test   # replay-dependent cases skip cleanly without cbor2
echo "== [29] 'Recursive' as a testable property (models/recursive_property.py)"; (cd models && python3 recursive_property.py)
echo "== [30] kernel: tier engine, bit-flip injection, image commit, chain hash C vs Python (src/kernel.c)"
gcc -O2 -o "$BUILD/kernel_test" tests/kernel_test.c && "$BUILD/kernel_test" self
cp "$BUILD/kernel_test" models/kernel_test; (cd models && python3 kernel_check.py); rm -f models/kernel_test
echo "== [31] first-stage prototype vectors (src/prototypes, test_core)"
gcc -O2 -o "$BUILD/proto_core" src/prototypes/test/test_core.c src/prototypes/c/fs_core.c src/prototypes/c/fs_quorum.c src/prototypes/c/lms.c src/prototypes/c/sha256.c
"$BUILD/proto_core" src/prototypes/test/vectors.txt | tail -1
echo "== [32] PQC migration as class retirement, two schedules (models/pqc_migration.py)"; (cd models && python3 pqc_migration.py | tail -5)
echo "== [33] TUF threshold roles under label-aware analysis (models/tuf_mapping.py)"; (cd models && python3 tuf_mapping.py)
echo "== [34] OQ-12/ADR-040: re-keying a slot whose holder is lost (models/lost_holder.py)"; (cd models && python3 lost_holder.py)
echo "ALL CHECKS COMPLETED"

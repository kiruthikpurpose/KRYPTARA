#!/usr/bin/env bash
# Reproduces every computed claim in the repository that can run on a laptop. Exit non-zero on any failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"; BUILD="$ROOT/build"; mkdir -p "$BUILD"
echo "== [1] interval theorem + class-count law (models/interval.py)";      (cd models && python3 interval.py)
echo "== [2] tier tables, budgets, impossibility catalogue (models/lint.py)"; (cd models && python3 lint.py && python3 tiers_extra.py)
echo "== [3] C admission vs Python reference";
gcc -O2 -Wall -o "$BUILD/p8test" src/p8test.c; cp "$BUILD/p8test" models/p8test; (cd models && python3 p8check.py); rm -f models/p8test
echo "== [4] projection test (TEST-ADM-05)"; gcc -O2 -o "$BUILD/test_projection" tests/test_projection.c && "$BUILD/test_projection"
echo "== [5] hardened-API fail-closed checks (red-team R2)"; gcc -O1 -I src -o "$BUILD/fixcheck" tests/redteam_r2/fixcheck.c 2>/dev/null || gcc -O1 -o "$BUILD/fixcheck" tests/redteam_r2/fixcheck.c -I tests/redteam_r2; "$BUILD/fixcheck"
echo "== [6] red-team R2 path analysis (informational)"; (cd tests/redteam_r2 && python3 r2_absent.py | tail -8)
if command -v arm-none-eabi-gcc >/dev/null; then echo "== [7] Cortex-M0+ size"; arm-none-eabi-gcc -mcpu=cortex-m0plus -mthumb -Os -c src/policy8.c -o "$BUILD/policy8_m0.o" && arm-none-eabi-size "$BUILD/policy8_m0.o"; fi
echo "== [8] GATE-12 hazard sweep (simulations/hazard_sweep.py)"; python3 simulations/hazard_sweep.py | tail -3
echo "ALL CHECKS COMPLETED"

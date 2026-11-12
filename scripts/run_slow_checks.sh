#!/usr/bin/env bash
# Checks too slow for run_all_checks.sh (minutes each). Exit non-zero on any failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"; BUILD="$ROOT/build"; mkdir -p "$BUILD"
echo "== [S1] journal power-cut sweep, quick mode (src/prototypes/test/test_powerfail.c), about 3 minutes"
P=src/prototypes
gcc -O2 -o "$BUILD/proto_pf" $P/test/test_powerfail.c $P/c/fs_journal.c $P/c/fs_core.c $P/c/fs_quorum.c $P/c/lms.c $P/c/sha256.c
"$BUILD/proto_pf" $P/test/pf_vectors.txt quick | tail -1
echo "== [S2] hazard parameter-uncertainty sweep, full (simulations/fleet_uncertainty.py), about 5 minutes"
python3 simulations/fleet_uncertainty.py | tail -4
echo "SLOW CHECKS COMPLETED"

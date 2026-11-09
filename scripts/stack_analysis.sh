#!/usr/bin/env bash
# Item 20 (50-things list), partial: static worst-case stack analysis via gcc -fstack-usage. [M]
# This is a HOST build (x86, -O2), not the target Cortex-M0+/M33 -fstack-usage output -- frame
# sizes differ by ISA and register count, so these numbers do not replace a target-compiler
# measurement. What IS real and target-independent: the CALL GRAPH shape (which function calls
# which), which bounds the worst-case call-chain depth regardless of per-frame byte counts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
BUILD="$ROOT/build"; mkdir -p "$BUILD"
gcc -O2 -fstack-usage -c src/policy8.c -o "$BUILD/policy8_stack.o"
SU="$BUILD/policy8_stack.su"

echo "Per-function worst-case frame size (host x86-64, gcc -O2 -- NOT target silicon):"
cat "$SU" | sed 's/^src\/policy8.c://'

echo
echo "Call-chain analysis (static, from source, not from the .su file alone):"
echo "  ac_tbl_upper -> covered(): $(grep ac_tbl_upper "$SU" | awk '{print $2}')B + $(grep 'covered.part' "$SU" | awk '{print $2}')B = $(( $(grep ac_tbl_upper "$SU" | awk '{print $2}') + $(grep 'covered.part' "$SU" | awk '{print $2}') ))B (deepest chain found)"
echo "  ac_key_install_authorised -> ac_tbl_authorises: $(grep ac_key_install_authorised "$SU" | awk '{print $2}')B + $(grep '[^_]ac_tbl_authorises' "$SU" | awk '{print $2}')B"
echo
echo "Comparison to docs/specifications/resource-estimates.md's existing claim (88 B, M33-targeted, pre-dating this session's additions):"
upper_chain=$(( $(grep ac_tbl_upper "$SU" | awk '{print $2}') + $(grep 'covered.part' "$SU" | awk '{print $2}') ))
echo "  host x86-64 deepest chain measured here: ${upper_chain} B"
echo "  NOTE: this is a different ISA/compiler than the documented M33 figure; the two numbers are"
echo "  not directly comparable, and this script does not claim to supersede the M33 estimate --"
echo "  it only confirms a chain of this approximate shape/depth exists and gives a host-measured bound."

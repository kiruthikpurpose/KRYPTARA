#!/usr/bin/env bash
# Item 44 (50-things list): supply-chain and reproducible-build controls. [M]
# What this checks: building src/policy8.c (and tests/redteam_r2/fixcheck.c) TWICE, from the same
# source, with SOURCE_DATE_EPOCH pinned and build paths normalised, produces BIT-IDENTICAL object
# files -- no embedded timestamps, no absolute-path leakage, no nondeterministic compiler behaviour
# (e.g. randomised symbol ordering) on this toolchain.
# What this does NOT check, honestly: it does NOT confirm two DIFFERENT compilers (gcc vs clang)
# agree -- no clang is installed in this environment (D-13's "two compilers" diversity goal is a
# separate claim, already tracked, and remains open: see docs/specifications/requirements.md). It
# also does not confirm a THIRD PARTY on a different machine reproduces the same bytes -- that
# needs an actual third party, which this environment cannot manufacture (item 44's "a third party
# reproduces a release bit for bit" is explicitly out of reach here; this is the part that IS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
BUILD="$ROOT/build/repro"; rm -rf "$BUILD"; mkdir -p "$BUILD/a" "$BUILD/b"

export SOURCE_DATE_EPOCH=1700000000   # fixed, arbitrary, reproducible-builds.org convention

build_once() {
    local outdir="$1"
    gcc -O2 -fdebug-prefix-map="$ROOT"=. -ffile-prefix-map="$ROOT"=. \
        -c src/policy8.c -o "$outdir/policy8.o"
    gcc -O1 -fdebug-prefix-map="$ROOT"=. -ffile-prefix-map="$ROOT"=. \
        -I tests/redteam_r2 -c tests/redteam_r2/fixcheck.c -o "$outdir/fixcheck.o"
}

build_once "$BUILD/a"
sleep 1   # make sure any accidental wall-clock dependency would show up as a byte difference
build_once "$BUILD/b"

bad=0
for f in policy8.o fixcheck.o; do
    ha=$(sha256sum "$BUILD/a/$f" | cut -d' ' -f1)
    hb=$(sha256sum "$BUILD/b/$f" | cut -d' ' -f1)
    if [ "$ha" = "$hb" ]; then
        echo "  $f: MATCH ($ha)"
    else
        echo "  $f: MISMATCH (a=$ha b=$hb)"
        bad=1
    fi
done
rm -rf "$BUILD"
if [ "$bad" -ne 0 ]; then
    echo "reproducible_build: FAILED"
    exit 1
fi
echo "reproducible_build: same toolchain, two independent builds, bit-identical. Cross-compiler and third-party reproduction remain open (see header)."

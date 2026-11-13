#!/bin/bash
# usage: run.sh name [seconds]   (cfg_name.cfg must exist; optional wall-clock cap)
# TLC's state files go to a temporary directory, never into the repository.
# Optional environment (all default to the previous behaviour):
#   TLC_HEAP     JVM heap, default 5g
#   TLC_WORKERS  TLC workers, default 2 (a number, or "auto")
#   TLC_META     persistent state/checkpoint directory (kept after the run); default is a temp dir
#   TLC_EXTRA    extra TLC flags, e.g. "-checkpoint 30" or "-simulate num=20000 -depth 200 -seed 1"
# Note: with -simulate the result is SAMPLED evidence (random traces), never an exhaustive check.
cd "$(dirname "$0")"
if [ -n "$TLC_META" ]; then META="$TLC_META"; mkdir -p "$META"; else META="$(mktemp -d)"; fi
( time timeout "${2:-86400}" java -XX:+UseParallelGC -Xmx${TLC_HEAP:-5g} -cp "${TLA_JAR:-tla2tools.jar}" tlc2.TLC -workers "${TLC_WORKERS:-2}" -metadir "$META" $TLC_EXTRA -config cfg_$1.cfg FirstStage.tla > out_$1.txt 2>&1 ; echo "tlc_exit=$?" >> out_$1.txt ) 2> time_$1.txt
[ -n "$TLC_META" ] || rm -rf "$META"
grep -v JAVA_TOOL out_$1.txt | grep -E "^Error: |violated|No error|states generated, .* distinct|depth of the complete|^Finished in|^tlc_exit" | tail -7

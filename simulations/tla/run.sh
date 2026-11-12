#!/bin/bash
# usage: run.sh name [seconds]   (cfg_name.cfg must exist; optional wall-clock cap)
# TLC's state files go to a temporary directory, never into the repository.
cd "$(dirname "$0")"
META="$(mktemp -d)"
( time timeout "${2:-86400}" java -XX:+UseParallelGC -Xmx${TLC_HEAP:-5g} -cp "${TLA_JAR:-tla2tools.jar}" tlc2.TLC -workers 2 -metadir "$META" -config cfg_$1.cfg FirstStage.tla > out_$1.txt 2>&1 ) 2> time_$1.txt
rm -rf "$META"
grep -v JAVA_TOOL out_$1.txt | grep -E "^Error: |violated|No error|states generated, .* distinct|depth of the complete|^Finished in" | tail -6

#!/bin/bash
# usage: run.sh name  (cfg_name.cfg must exist)
cd "$(dirname "$0")"
( time java -XX:+UseParallelGC -Xmx5g -cp "${TLA_JAR:-tla2tools.jar}" tlc2.TLC -workers 2 -config cfg_$1.cfg FirstStage.tla > out_$1.txt 2>&1 ) 2> time_$1.txt
grep -v JAVA_TOOL out_$1.txt | grep -E "^Error: (Inv|Temporal|Action|Deadlock)|violated|No error|states generated, .* distinct|depth of the complete|^Finished in" | tail -6

.PHONY: help check audit arch step mutation-step slow bench quick clean

help:  ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

check:  ## full check suite (scripts/run_all_checks.sh)
	./scripts/run_all_checks.sh

audit:  ## documentation audit
	python3 scripts/audit_docs.py

arch:  ## architecture fitness checks R1-R8 plus self-test
	python3 scripts/arch_check.py
	python3 scripts/arch_check.py --self-test

step:  ## waist: C self checks, C vs Python model, golden vectors
	mkdir -p build
	gcc -O2 -std=c99 -Wall -Wextra -o build/step_test tests/step_test.c
	./build/step_test self
	cp build/step_test models/step_test
	cd models && python3 step_check.py && python3 step_check.py --verify-golden ../tests/vectors/waist-v1.txt; rc=$$?; rm -f step_test; exit $$rc

mutation-step:  ## mutation testing of src/ac_step.c (slow)
	python3 scripts/mutation_test.py --step

slow:  ## long-running sweeps (also run in CI)
	./scripts/run_slow_checks.sh

bench:  ## host timing of admission (not silicon)
	mkdir -p build
	gcc -O2 -o build/bench_policy8 tests/bench_policy8.c
	./build/bench_policy8

quick:  ## fast loop: C admission and hardened API only
	mkdir -p build
	gcc -O2 -Wall -o build/p8test src/p8test.c
	gcc -O1 -o build/fixcheck tests/redteam_r2/fixcheck.c -I tests/redteam_r2
	gcc -O2 -o build/test_projection tests/test_projection.c
	./build/fixcheck
	./build/test_projection

clean:  ## remove build output
	rm -rf build simulations/tla/states

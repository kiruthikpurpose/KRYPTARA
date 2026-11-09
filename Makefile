.PHONY: check audit bench quick clean

# Mirrors scripts/run_all_checks.sh; `make check` is just the memorable entry point.
check:
	./scripts/run_all_checks.sh

audit:
	python3 scripts/audit_docs.py

# Fast feedback loop: C admission + hardened API only, skips the Python Monte Carlo sweeps.
quick:
	mkdir -p build
	gcc -O2 -Wall -o build/p8test src/p8test.c
	gcc -O1 -o build/fixcheck tests/redteam_r2/fixcheck.c -I tests/redteam_r2
	gcc -O2 -o build/test_projection tests/test_projection.c
	gcc -O2 -o build/bench_policy8 tests/bench_policy8.c
	./build/fixcheck
	./build/test_projection
	./build/bench_policy8

clean:
	rm -rf build simulations/tla/states

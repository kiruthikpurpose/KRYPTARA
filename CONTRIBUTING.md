# Contributing

Thank you for helping. Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [GOVERNANCE.md](GOVERNANCE.md) first.

## Rules
1. Every claim needs an evidence class and, if Derived, a runnable check.
2. Add or change a decision through an ADR (`docs/decisions/ADR-TEMPLATE.md`); do not edit accepted ADRs, supersede them.
3. Run `make check` (or `./scripts/run_all_checks.sh`) and `make audit` before opening a pull request.
4. No empty placeholder files; no claims about unimplemented or unrun work.
5. Keep hardware content defensive; no attack procedures against flash locks.
6. Do not edit `tests/vectors/waist-v1.txt` or `src/waist-v1.abi` to make a failing build pass. A
   change to either needs an ADR and a reason in the commit message.
7. IDs: HYP-, REQ-, ADR-, EXP-, TEST-, CLM-, SRC-, OQ-.

## Setup
```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt     # optional extras: z3, cbor2, PQC conformance libraries
make check
```
Needs `gcc` and `python3`. `arm-none-eabi-gcc` is optional (size gate runs in CI). TLA+ needs the TLC jar.

## Where to put a change
| Change | Update |
|---|---|
| Kernel behaviour | `src/ac_step.c`, `models/step_model.py`, golden vectors, `docs/specifications/requirements.md` |
| New claim | `docs/research/evidence-register.md`, `docs/specifications/traceability-matrix.md` |
| Decision | new ADR, `docs/index.md` |
| Anything user-visible | `CHANGELOG.md` |

## Commits and pull requests
Short imperative subject, a body that says what and why, and what was not run. Authorship is the
person who wrote the change; commits carry no tool or co-author trailers.

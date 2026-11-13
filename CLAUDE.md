# CLAUDE.md: routing for Claude Code

Project: KRYPTARA (see README). Verified core = governed-change kernel. Do not rename the project or invent a scientific meaning for its name terms.

## Rules
- Label claims Established / Derived / Proposed / Hypothesis / Speculative / Refuted; update `docs/research/evidence-register.md` with any new claim.
- Never invent equations, sources or results. Do not describe unrun work as done. Record unrun gates as "not run".
- Keep hardware discussion defensive; no attack procedures against MCU flash locks.
- Hierarchy and conflicts: `docs/document-hierarchy.md`. `research-archive/` is historical only.
- New decisions: copy `docs/decisions/ADR-TEMPLATE.md`. IDs: HYP-, REQ-, ADR-, EXP-, TEST-, CLM-, SRC-, OQ-.

## Where things are
- Theory: docs/theory. Architecture: docs/architecture. Requirements: docs/specifications.
- Code: `src/policy8.c` (admission, C), `models/lint.py` (reference model), `models/` other studies, `simulations/`, `tests/`.
- Run everything: `./scripts/run_all_checks.sh`. Docs audit: `python3 scripts/audit_docs.py`.

## Next work (in order)
0. Resolve the 24 surviving `ac_step.c` mutants (`python3 scripts/mutation_test.py --step`), CLM-68.
1. GATE-08: run the TLA+ base configuration to completion (`.github/workflows/gate-08-tla.yml`,
   manual trigger). The reduced configuration passes (GATE-08r); mutations M4 and M6 need the base
   size to be caught.
2. First CI run: GATE-07 measured 1,196 B against 1,024 B, so it FAILS as worded (OQ-13): decide to
   raise the budget by ADR or move provisioning-only code out of the locked stage. Still to read:
   the `rust-twin` workflow result (Rust vs C differential tests, never yet run).
3. ADR-040 (lost-holder re-keying) is Proposed and blocked by OQ-14: the PAM rule makes a lost
   escrow key unrecoverable in the first-stage model (CLM-63). Decide how to resolve it.
4. Human triage of the 146 gap-candidate legacy requirements
   (`docs/research/legacy-requirements-reconciliation.md`).
5. External work that cannot be done from this repository: cryptographer review (EXP-18, GATE-11),
   independent red-team round 3, silicon measurements (EXP-19, E-A1; GATE-09/10), a reference
   board, a pilot operator. Stop and report if GATE-10 fails on real silicon.
6. Owner decision: the meaning of "Yielding" (OQ-01). The licence is Apache-2.0 (LICENSE, NOTICE), chosen 2026-11-13.

`docs/*` files sliced from Rev 4 were reviewed against the R2 findings on 2026-11-12 (see CHANGELOG).

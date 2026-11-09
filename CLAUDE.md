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
1. Complete the TLA+ base run (GATE-08), add holder co-signature to the model (REQ-LIFE-02).
2. Implement REQ-LINT-03 (site-controller group mode) and REQ-LIFE-02.
3. Hazard sweep for SIM-01 (GATE-12).
4. Reconcile the 221 legacy requirements (`research-archive/streams/R_requirements`) with REQ-.
5. Migrate remaining legacy D/C/X/J decisions to ADRs.
6. Silicon measurements (EXP-19, E-A1) when hardware is available. Stop and report if GATE-10 fails.
`docs/*` files sliced from Rev 4 carry a banner; review them against the R2 findings before relying on them.

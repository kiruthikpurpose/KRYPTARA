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
1. ~~Complete the TLA+ base run (GATE-08)~~ — still **not passed**: two laptop attempts killed after
   14+ minutes without finishing (large but apparently converging state space). A `workflow_dispatch`
   CI job (`.github/workflows/gate-08-tla.yml`) exists to give it real time/memory on a GitHub
   runner; needs a human to actually trigger it. ~~add holder co-signature to the model
   (REQ-LIFE-02)~~ — done (`Repl3OK` in `simulations/tla/FirstStage.tla`), but unverified by TLC
   until GATE-08 finishes.
2. ~~Implement REQ-LINT-03~~ and ~~REQ-LIFE-02~~ — done (`models/lint.py` `site_controller=`;
   `src/policy8.c` `ac_key_install_authorised`, tested).
3. ~~Hazard sweep for SIM-01 (GATE-12)~~ — done, passed (`simulations/hazard_sweep.py`).
4. Reconcile the 221 legacy requirements (`research-archive/streams/R_requirements`) with REQ- —
   **mechanical first pass done** (`scripts/reconcile_legacy_requirements.py` →
   `docs/research/legacy-requirements-reconciliation.md`: 11 likely-covered, 62 out-of-scope,
   148 gap-candidates). The 148 gap candidates still need a human semantic triage pass — a script
   doing that unsupervised would be exactly the kind of invented judgment this file's own rules
   forbid.
5. Migrate remaining legacy D/C/X/J decisions to ADRs. **Not started.**
6. Silicon measurements (EXP-19, E-A1) when hardware is available. Stop and report if GATE-10 fails.
   **Blocked: no MCU hardware in this environment.** A host-only timing benchmark exists
   (`tests/bench_policy8.c`, CLM-23) as a sanity check, explicitly not a substitute.

Also done this pass, not in the original list: REQ-EVD-02, REQ-EVD-03, REQ-TIER-02, REQ-PRES-02,
REQ-PUB-01, REQ-STALE-01, REQ-NV-01, REQ-CHAIN-01, REQ-HALT-01 each now have a runnable, passing
reference check (GATE-15) — see `docs/specifications/requirements.md` for exactly what each one
does and doesn't cover.

`docs/*` files sliced from Rev 4 carry a banner; review them against the R2 findings before relying on them.

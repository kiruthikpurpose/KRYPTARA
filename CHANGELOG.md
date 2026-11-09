# Changelog

## 2026-11-09: initial repository
- Imported research archive S01–S11, legacy blueprints Rev 1–4, working streams.
- Sliced Rev 4 into 18 topic documents (`scripts/build_docs_from_rev4.py`).
- New: vision-and-scope, evidence register (18 claims), source inventory, requirements (24), ADR-001..015, simulation specs (4), validation gates, traceability matrix, open questions.
- Model fix: absent atoms count as compromised and lost; projection-canonical tables (F-R2-01/02).
- C: `ac_tbl_project`, `ac_tbl_is_projected`; hardened API per R2. Admission code size: 682 B (Rev 4) → 812 B (hardened) → 902 B (with projection), Cortex-M0+ -Os.
- Reconciled: Rev 4 T0 HALT popcount 254 refers to `K≥1 ∨ p` (`tiers_extra.py`); `lint.py` HALT (`K≥1`) gives 252. Both correct for their definitions.

## 2026-11-09: REQ-LIFE-02 and REQ-LINT-03 (next-work items 1–3)
- REQ-LIFE-02 (slot-holder co-signature, F-R2-03): added `ac_key_install_authorised` to `src/policy8.c`
  (tested by `tests/redteam_r2/fixcheck.c` cases I/J/K, 0 failures); `Repl3OK` in
  `simulations/tla/FirstStage.tla` now requires `ValidSig(r.sg, Esc)` whenever slot 3 is active.
  ADR-015 moved Proposed → Accepted. GATE-08 (TLA+ base run) re-run against the updated model; see
  `simulations/tla/out_base.txt` for the current run status — treat as "not yet passed" until it
  finishes with no invariant violation.
- REQ-LINT-03 (declared site-controller group mode, F-R2-04): added `site_controller=` to
  `structures()`/`lint()` in `models/lint.py`. Demonstrates that OPERATE's claimed 1-safe/live interval
  is empty when `OWN` is declared site controller, confirming F-R2-04's correlated-presence finding at
  the lint level (CLM-21). REQ-PRES-02, the matching device-side guard, remains not implemented.
- Fixed `simulations/tla/run.sh` to resolve its own directory instead of a hardcoded path, and to take
  the TLA+ tools jar from `$TLA_JAR`.
- Updated: requirements.md, traceability-matrix.md, validation-gates.md (GATE-13), red-team-r2-findings.md,
  evidence-register.md (CLM-19..21), ADR-015.
- GATE-12 (SIM-01 hazard sweep) completed: `simulations/hazard_sweep.py`, 16 points over `h_group`
  1–10%/yr × `h_family` 0.1–3%/yr, 20,000 trials/point. 0/16 points violate the claimed ordering
  terrestrial ≤ remote_degraded ≤ {remote, rev2_renewal, rev2_no_renewal}. HYP-01's rejection
  condition was not triggered over this range (CLM-22). Hazards remain illustrative (CLM-08).
- The legacy-requirements reconciliation (221 items, next-work item 4) and ADR migration (item 5) were
  not started in this pass — see `docs/research/open-questions.md`.

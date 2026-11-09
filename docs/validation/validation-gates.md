# Validation gates

**Level:** L2. A gate is passed only when its command exits zero and output is recorded. "Not run" is a valid state.

| Gate | Criterion | Command / experiment | Status |
|---|---|---|---|
| GATE-01 | Interval theorem holds on ≥1,000 random structures; zero counterexamples. | `models/interval.py` | Passed earlier (1,050); re-run in this build |
| GATE-02 | All reference tiers safe-and-live; all 8 impossibility rows IMPOSSIBLE. | `models/lint.py` | Passed 2026-11-09 |
| GATE-03 | C admission equals Python reference on 3,000 random cases. | `models/p8check.py` | Passed (mismatches=0) |
| GATE-04 | Projection test: 20,000 cases, 0 failures. | `tests/test_projection.c` | Passed |
| GATE-05 | Hardened API fail-closed checks 0 failures. | `tests/redteam_r2/fixcheck.c` | Passed |
| GATE-06 | Absent-atom fix does not change interval non-emptiness over 20,000 structures. | `r2_absent.py` [5] | Passed (0 changes) |
| GATE-07 | Admission code ≤ 1,024 B on Cortex-M0+ -Os. | `arm-none-eabi-size` | Passed (902 B) |
| GATE-08 | TLA+ base model completes with no invariant violation. | `simulations/tla/run.sh` | **Not passed: recorded run did not complete** |
| GATE-09 | Admission ≤ 10 ms at 64 MHz on M0+ silicon. | EXP-19 | **Not run; no silicon** |
| GATE-10 | Locked first stage with safe torn reads on ≥30% of sampled MCU families. | E-A1 | **Not run** |
| GATE-11 | Hash-family independence reviewed with no non-negligible shared assumption. | EXP-18 | **Not run** |
| GATE-12 | SIM-01 ordering stable under hazard sweep. | `simulations/hazard_sweep.py` | **Passed** (2026-11-09): 0 of 16 points (`h_group` 1–10%/yr × `h_family` 0.1–3%/yr, 20,000 trials/point) violate the claimed ordering terrestrial ≤ remote_degraded ≤ {remote, rev2_renewal, rev2_no_renewal}. Hazards remain illustrative (CLM-08); this only shows the *order* is insensitive to them over this range, not that the range is correct. |
| GATE-13 | REQ-LIFE-02 and REQ-LINT-03 implemented and tested. | `tests/redteam_r2/fixcheck.c` (REQ-LIFE-02 C unit tests), `models/lint.py` (REQ-LINT-03) | **Passed** for the C admission primitive and the lint mode; the TLA+ model-level check of REQ-LIFE-02 (`Repl3OK`) rides on GATE-08 and is not yet separately complete |
| GATE-14 | Documentation audit passes. | `scripts/audit_docs.py` | see CHANGELOG |

Full EXP-01..20 list: `falsification-programme.md`.

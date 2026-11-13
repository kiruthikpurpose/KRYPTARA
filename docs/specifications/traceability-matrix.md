# Traceability matrix

Chain: source evidence → principle → claim → decision → requirement → component → implementation → test → result. "—" means none exists.

| Source | Claim | ADR | Requirement | Component | Implementation | Test | Result |
|---|---|---|---|---|---|---|---|
| SRC-12 (Rev 4 §3.3) | CLM-01 | ADR-003 | REQ-ADM-01 | admission | `src/policy8.c` `ac_tbl_within` | `models/interval.py`, `p8check.py` | Passed (GATE-01, 03) |
| Rev 4 §3.3 | CLM-01 | ADR-003 | REQ-ADM-02 | admission | `ac_tbl_tighten` | `fixcheck.c` | Passed |
| R2 red-team | CLM-05 | ADR-014 | REQ-ADM-03 | admission | `ac_tbl_upper/lower` (`expo`, `absent`) | `r2_absent.py`, `fixcheck.c` | Passed (GATE-05, 06) |
| R2 red-team | — | ADR-014 | REQ-ADM-04 | admission | hardened API | `fixcheck.c` | Passed |
| R2 red-team | — | ADR-014 | REQ-ADM-05 | admission | `ac_tbl_project` | `tests/test_projection.c` | Passed (GATE-04) |
| Rev 4 §3.4 | CLM-02, CLM-34 | ADR-011 | REQ-LIFE-01 | lifecycle | `models/interval.py` (class-count law); `models/class_lifecycle.py` (DECLARE_CLASS_DEAD) | `interval.py` [3] (0 disagreements); `class_lifecycle.py` (6/6) | Passed, both halves |
| Rev 4 §3.5–3.6 | CLM-03, 04 | ADR-004 | REQ-TIER-01 | tiers | `models/lint.py` | `lint.py` | Passed (GATE-02) |
| Rev 4 §3.5–3.6 | — | ADR-004 | REQ-TIER-02 | tiers | `models/tiers_extra.py` | `tiers_extra.py` | Passed (0 failures, both profiles) |
| Rev 4 §6.4 | CLM-09 | ADR-005 | REQ-PRES-01 | locked stage | — | — | Not implemented (hardware-only; no MCU available) |
| R2 red-team | CLM-09 | ADR-005 | REQ-PRES-02 | lint | `models/lint.py` `site_controller_guard` | `lint.py` | Passed (0/6 violations: OEM/OWN/ESC × RECOVERY/CONST) |
| Rev 4 §6.5 | CLM-10 | ADR-006 | REQ-PUB-01 | witness verifier | `models/witness_receipt.py` | `witness_receipt.py` | Passed (7/7); reference counting rule only, not a real cosignature verifier |
| Rev 4 §6.11 | — | ADR-007 | REQ-IMG-01 | locked stage | `simulations/tla/FirstStage.tla` (model) | TLC | Incomplete (GATE-08) |
| Rev 4 §6.6 | — | ADR-008 | REQ-CHAIN-01 | record | `src/prototypes/`; `models/hash_chain.py` (algorithm reference) | prototype tests; `hash_chain.py` (5/5) | Prototype + reference algorithm; no NV storage or real signatures |
| Rev 4 §4.4 | — | ADR-009 | REQ-HALT-01 | effect | `models/halt_budget.py` (reference state machine) | `halt_budget.py` (2,000 random sequences, 0 violations) | Property-tested reference model; exhaustive TLA+ spec still incomplete (rides on GATE-08) |
| R2 red-team | — | ADR-015 | REQ-LIFE-02 | lifecycle | `src/policy8.c` `ac_key_install_authorised`; `Repl3OK` in `simulations/tla/FirstStage.tla` | `fixcheck.c` (I/J/K); TLC cfg_base | Passed (C unit tests); TLC run killed after 14m43s, not finished — GATE-08 not passed, model-level claim unverified |
| R2 red-team | — | ADR-015 | REQ-LINT-03 | tooling | `models/lint.py` `site_controller=` | `lint.py` | Passed |
| R2 red-team | — | ADR-002 | REQ-EVD-02 | evidence | `src/policy8.c` `ac_derive_assumption_label`/`ac_derive_labels` | `fixcheck.c` (S/T/U/V/W) | Passed; covers "device-derived not caller-supplied" only |
| R2 red-team | — | ADR-002 | REQ-EVD-03 | evidence | `src/policy8.c` `ac_no_duplicate_keys` | `fixcheck.c` (Q/R) | Passed |
| R2 red-team | — | ADR-012 | REQ-NV-01 | locked stage | `src/policy8.c` `ac_tbl_dual_*` | `fixcheck.c` (L/M/N/O/P) | Passed |
| R2 red-team | — | ADR-010 | REQ-STALE-01 | record | `models/stale_bound.py` | `stale_bound.py` (5/5) | Passed |
| Rev 4 §9 | CLM-07, 12 | ADR-003 | — | admission | `src/policy8.c` | `arm-none-eabi-size`; `tests/bench_policy8.c` (host) | Size measured; host timing measured (CLM-23); silicon time not |
| SIM-01 | CLM-08, 18 | ADR-004 | REQ-TIER-01 | tiers | `models/brick_mc.py`; `simulations/fleet_uncertainty.py` | MC run; hazard sweep (CLM-24) | Illustrative, but ordering robust to hazard-sweep/parameter uncertainty |
| ADR-041 | CLM-64..68 | ADR-041 | REQ-WAIST-01..04 | waist | `src/ac_step.c`, `src/ac_waist.h`, `src/kernel.c` | `arch_check.py`; `step_check.py`; `step_test.c`; mutation `--step` | Host checks pass; mutation 81% (24 survivors); Rust twin, ARM size not run |

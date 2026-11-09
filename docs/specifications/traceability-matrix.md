# Traceability matrix

Chain: source evidence → principle → claim → decision → requirement → component → implementation → test → result. "—" means none exists.

| Source | Claim | ADR | Requirement | Component | Implementation | Test | Result |
|---|---|---|---|---|---|---|---|
| SRC-12 (Rev 4 §3.3) | CLM-01 | ADR-003 | REQ-ADM-01 | admission | `src/policy8.c` `ac_tbl_within` | `models/interval.py`, `p8check.py` | Passed (GATE-01, 03) |
| Rev 4 §3.3 | CLM-01 | ADR-003 | REQ-ADM-02 | admission | `ac_tbl_tighten` | `fixcheck.c` | Passed |
| R2 red-team | CLM-05 | ADR-014 | REQ-ADM-03 | admission | `ac_tbl_upper/lower` (`expo`, `absent`) | `r2_absent.py`, `fixcheck.c` | Passed (GATE-05, 06) |
| R2 red-team | — | ADR-014 | REQ-ADM-04 | admission | hardened API | `fixcheck.c` | Passed |
| R2 red-team | — | ADR-014 | REQ-ADM-05 | admission | `ac_tbl_project` | `tests/test_projection.c` | Passed (GATE-04) |
| Rev 4 §3.4 | CLM-02 | ADR-011 | REQ-LIFE-01 | lifecycle | `models/lint.py` | `lint.py` | Partial |
| Rev 4 §3.5–3.6 | CLM-03, 04 | ADR-004 | REQ-TIER-01 | tiers | `models/lint.py` | `lint.py` | Passed (GATE-02) |
| Rev 4 §6.4 | CLM-09 | ADR-005 | REQ-PRES-01 | locked stage | — | — | Not implemented |
| R2 red-team | CLM-09 | ADR-005 | REQ-PRES-02 | lint | — | — | Not implemented |
| Rev 4 §6.5 | CLM-10 | ADR-006 | REQ-PUB-01 | witness verifier | — (design only) | — | Not implemented |
| Rev 4 §6.11 | — | ADR-007 | REQ-IMG-01 | locked stage | `simulations/tla/FirstStage.tla` (model) | TLC | Incomplete (GATE-08) |
| Rev 4 §6.6 | — | ADR-008 | REQ-CHAIN-01 | record | `src/prototypes/` | prototype tests | Prototype only |
| Rev 4 §4.4 | — | ADR-009 | REQ-HALT-01 | effect | TLA+ model | TLC | Incomplete |
| R2 red-team | — | ADR-015 | REQ-LIFE-02 | lifecycle | `src/policy8.c` `ac_key_install_authorised`; `Repl3OK` in `simulations/tla/FirstStage.tla` | `fixcheck.c` (I/J/K); TLC cfg_base | Passed (C unit tests); TLC run killed after 14m43s, not finished — GATE-08 not passed, model-level claim unverified |
| R2 red-team | — | ADR-015 | REQ-LINT-03 | tooling | `models/lint.py` `site_controller=` | `lint.py` | Passed |
| Rev 4 §9 | CLM-07, 12 | ADR-003 | — | admission | `src/policy8.c` | `arm-none-eabi-size` | Size measured; time not |
| SIM-01 | CLM-08, 18 | ADR-004 | REQ-TIER-01 | tiers | `models/brick_mc.py` | MC run | Illustrative |

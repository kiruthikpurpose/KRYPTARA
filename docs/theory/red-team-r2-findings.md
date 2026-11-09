# Red-team round 2 findings and their status

**Level:** L2. Source: stopped second red-team (artefacts in `tests/redteam_r2/`), reviewed and re-run 2026-11-09. Round 2 did not finish; this is a partial review, not a clean bill of health.

| ID | Finding | Evidence | Resolution | Status |
|---|---|---|---|---|
| F-R2-01 | Absent atoms (declared slots with no key) were treated as unavailable to the attacker, so bounds were too permissive. | `r2_absent.py` [1]–[4] | Absent atoms count as compromised and lost: `models/lint.py` (`free = expo \| absent`), `ac_tbl_upper/lower` take `expo`/`absent`. Fix leaves interval non-emptiness unchanged on 20,000 random structures [M]. | Fixed in model and C |
| F-R2-02 | Tables could depend on absent atoms. | `r2_absent.py` [6] | Canonical form f'(S)=f(S&present); `ac_tbl_project`, `ac_tbl_is_projected`; TEST-ADM-05 passes. | Fixed |
| F-R2-03 | Key rotation/transfer without the slot holder's co-signature lets other parties install a key into an ACTIVE slot. | `r2_paths.py` [3] | Requirement REQ-LIFE-02 (holder co-signature): `ac_key_install_authorised` (`src/policy8.c`, tested by `fixcheck.c` I/J/K) and `Repl3OK` in `simulations/tla/FirstStage.tla` (`SlotActive(Esc) => ValidSig(r.sg, Esc)`). TLC check of cfg_base killed after 14m43s without finishing (249M states, 40M distinct, queue falling from an 8.5M peak to 4.9M — converging, not diverging, but too slow for the time available); GATE-08 not passed. | Fixed in C and modelled; TLA+ model check not completed |
| F-R2-04 | Correlated presence: an owner who controls the site satisfies recoverable T2 alone. | `r2_paths.py` | Use fortress T2, or an independent presence custodian; lint mode for a declared site-controller group (REQ-LINT-03): `site_controller=` parameter in `models/lint.py` `structures()`/`lint()`. Confirms OPERATE's claimed 1-safe/live interval is empty (unsafe) when `OWN` is declared site controller — procurement must pick fortress T2 or an independent presence custodian. REQ-PRES-02 (the device-side guard rejecting this at runtime) remains **not implemented**. | Lint mode fixed; device-side guard open |
| F-R2-05 | C admission API accepted malformed inputs (cap overflow, k>nf, bad labels). | `fixcheck.c` | Hardened API returns -1/-2 and refuses; `fixcheck` failures=0. | Fixed |

`tests/redteam_r2/r2_cedge.c` prints FAIL lines because it probes the pre-hardening API semantics; it is retained as history, not as a regression test.

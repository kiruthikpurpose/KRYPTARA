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
  ADR-015 moved Proposed → Accepted. GATE-08 (TLA+ base run) re-run against the updated model: killed
  after 14m43s without finishing (249M states generated, 40M distinct; queue falling from an 8.5M peak
  to 4.9M when stopped — converging, not diverging, but too slow for the time available). No invariant
  violation was reported before termination, but a run that didn't finish proves nothing either way.
  GATE-08 remains **not passed**; the state space is too large for a laptop-class run in this time
  budget and needs either more time/memory or a reduced/abstracted config to actually complete.
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

## 2026-11-09: simulated datasets, host measurements, literature grounding
- Added `simulations/fleet_uncertainty.py` (CLM-24): propagates hazard-rate PARAMETER uncertainty
  (log-normal, σ=0.5) through the existing `models/brick_mc.py` Monte Carlo, 200 draws × 1,500
  trials/design/draw (1.5M device-trials, ~5 min, <40 MB RAM). Produces a 1,000-row dataset
  (`simulations/data/fleet_uncertainty.csv`, 72 KiB) and confirms CLM-08's governance-loss ordering
  holds in all 200/200 individual draws, not just at the single illustrative point. `--quick` mode
  (20 draws × 300 trials, ~5 s) wired into `run_all_checks.sh` step [10].
- Added `tests/bench_policy8.c` (CLM-23): real host-measured timing (gcc -O2, `clock_gettime`) of the
  admission table primitives in `src/policy8.c`. `ac_tbl_upper` at nf=12/k≤2 (the case resource-
  estimates.md's "admission, 12 classes" row describes) measures ≈21.4 µs on a 2026 x86 laptop —
  scaling by clock+throughput to a 64 MHz Cortex-M0+ lands inside the existing 3–10 ms [E] estimate,
  corroborating it. The actual per-transition hot path, `ac_tbl_authorises`, is sub-nanosecond (a
  single bit test); `ac_tbl_upper`/`lower` run once at provisioning, not per admission. No ARM
  toolchain or silicon was available in this environment, so this is a host measurement used to sanity
  check an existing estimate, not a replacement for EXP-19.
- Updated CLM-11 (hash-family independence) with a real citation for the *structural* independence of
  SHA-2 (Merkle–Damgård lineage) vs SHA-3/Keccak (sponge, chosen by public competition explicitly as
  insurance against a SHA-2 break): NIST's SHA-3 project rationale and the CRYPTREC SHA-3 security
  evaluation report. This grounds the claim that the *designs* are independent; "independent enough"
  as a cryptanalytic security property is still EXP-18, not run — searched for published quantitative
  HSM/key-custody failure-rate data for CLM-08 and found none public, confirming "illustrative, not
  measured" was the honest label rather than an oversight.
- Environment note: this machine has ~8.7 GB free disk and ~1 GB free RAM under normal desktop load
  (Brave + VS Code already using most of 8 GB). All new scripts were kept small and pure-Python/numpy
  (already installed, nothing new downloaded) or a single tiny C file; no ARM toolchain, Docker, or
  other heavy tooling was installed. The TLA+ GATE-08 run from the previous pass was identified as the
  actual risk (it had grown its on-disk state to 1.2 GB before being killed) — `simulations/tla/states/`
  is now gitignored so a future run can't silently fill the disk.

## 2026-11-09: nine requirements implemented, legacy requirements reconciled, 23 ADRs migrated
Closes out next-work items 4 and 5, and clears every remaining non-hardware "not yet verified"/
"not implemented" requirement row.

- **REQ-EVD-02, REQ-EVD-03** (`src/policy8.c`): `ac_derive_assumption_label`/`ac_derive_labels`
  (assumption bits come only from a closed provider table, never caller input) and
  `ac_no_duplicate_keys` (rejects two present SIG atoms with identical key hashes). Tested by
  `fixcheck.c` cases S–W and Q–R.
- **REQ-NV-01** (`src/policy8.c`): `ac_tbl_dual_init`/`ac_tbl_dual_consistent`/`ac_tbl_dual_authorises`
  — dual storage with complements, decisions evaluated twice, fails closed on a single-bit-flip
  disagreement between the two copies. Tested by `fixcheck.c` cases L–P.
- **REQ-TIER-02** (`models/tiers_extra.py`): T1 is never itself 2-safe, and REQ-LIFE-02 never shrinks
  the minimum-cut distance to full control relative to allowing unco-signed rotation. 0 failures,
  both reference profiles.
- **REQ-PRES-02** (`models/lint.py` `site_controller_guard`): RECOVERY and CONST both reject OEM,
  OWN, and ESC as candidate site controllers (0/6 violations) — the lint-level guard F-R2-04 asked for.
- **REQ-PUB-01** (`models/witness_receipt.py`): reference check of the ≥2-independent-logs counting
  rule, 7/7 cases. Explicitly not a real C2SP/Tessera verifier — that component doesn't exist yet.
- **REQ-STALE-01** (`models/stale_bound.py`): catch-up gate requiring presence only when staleness is
  measurable (RTC trusted, age > window), 5/5 cases.
- **REQ-CHAIN-01** (`models/hash_chain.py`): reference hash-chain algorithm — tamper detection, domain
  separation, per-link (not current-table) policy verification, 5/5 cases.
- **REQ-HALT-01** (`models/halt_budget.py`): property test of the three stated invariants over 2,000
  random action sequences, 0 violations. A Python reference state machine, not the planned exhaustive
  TLA+ spec (still incomplete, rides on GATE-08).
- All nine wired into `run_all_checks.sh` (steps [2]/[3]/[11]–[14]) as GATE-15.
- **Legacy requirements reconciliation** (next-work item 4): `scripts/reconcile_legacy_requirements.py`
  mechanically classifies all 221 `FR-`/`NFR-` rows in `research-archive/streams/R_requirements.md`
  against the 23 current `REQ-` rows → `docs/research/legacy-requirements-reconciliation.md`: 11
  likely covered, 62 out of scope for the kernel today (update/migration/enclave/ownership/
  provisioning/governance/certification — Phase 2+ features), 148 gap candidates still needing a
  human semantic triage pass. This is a classification pass, not a verification — explicitly flagged
  as such in the output.
- **Legacy decision migration** (next-work item 5): `scripts/migrate_legacy_decisions.py` generated
  ADR-016..038 directly from `legacy-decision-record.md`'s own Decision/Why/Alternatives columns for
  every remaining `D-xx` item (D-01..D-19, D-32..D-34, D-36) not already covered by ADR-001..015.
  Every "DECIDED" legacy item now has an ADR. The C-xx/X-xx/J-xx tables (~80 items, conditional/
  research/rejected) were deliberately NOT split into individual ADRs — see `docs/decisions/README.md`
  for why.
- Not done, and not claimable as done: GATE-08 (TLA+ model check, still not passed — see
  `.github/workflows/gate-08-tla.yml`), REQ-PRES-01 and silicon measurements (EXP-19, E-A1 — no MCU
  hardware available), and the 148 gap-candidate legacy requirements (need human judgment, not a
  script).

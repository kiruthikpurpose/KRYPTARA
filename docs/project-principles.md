<!-- Title: Vision, principles, objectives, non-goals (Rev 4) -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L2. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 2. Vision, philosophy, principles and objectives

### 2.1 Vision

*A machine that can be governed for its whole life by evidence, not by contact with its maker. Its rules of change are small enough to read, strict enough to prove, and renewable by whoever comes next.*

### 2.2 Architectural philosophy

1. **Authority is the asset.** A forger after a quantum computer decrypts nothing; they *sign*. The exposure of long-lived infrastructure lies in who may change it, so the foundation is a theory and kernel of authority, not an algorithm library.
2. **Small, frozen waist; everything else is data or replaceable code.** The locked stage contains no parser for rich formats, no clock dependence, no policy interpreter and no secret.
3. **Structure over trust.** Where a property can be checked by the device from public data, the device checks it. It does not trust a host tool, a gateway or a human summary.
4. **Diversity is a budget, not a slogan.** Independent classes are counted, spent per tier, and renewed when lost.
5. **Monotone history.** Authority state only moves forward. Undoing is a new, higher-epoch, more strongly authorised act, and it is public.
6. **Every power has a recovery path, and every recovery path requires presence, is delayed, and is public.**
7. **Time may only restrict authority, never grant it.**
8. **Honest degradation.** When the mathematics forbids both safety and liveness, the design says so and chooses safety by default.

### 2.3 Principles, each with its test

| # | Principle | How it is tested |
|---|---|---|
| P-1 | No single declared fault can authorise any non-halt action | Lint: each tier table ≤ U for its compromise budget; device refuses otherwise |
| P-2 | The survivors of any single declared loss can still govern | Lint: each tier table ≥ Lo for its loss budget; Monte Carlo of governance loss |
| P-3 | The device itself refuses inadmissible policies | Conformance vectors: unsafe or non-live tables rejected on all ports |
| P-4 | Every authority-bearing action routes through one admission rule (no side doors) | Code review and static check: only `ac_step` emits authority intents; debug, RMA, provisioning and configuration are actions |
| P-5 | Only the locked stage mutates authority; it verifies every atom itself | Verification-locality lint; tests in which the second stage lies |
| P-6 | Authority state is monotone and power-cut safe | TLA+ invariants; ≥ 10⁵ power cuts on real silicon |
| P-7 | Every authority act without presence is published before it is effective | Device requires a witnessed receipt for every evidence set lacking presence; on-site acts during a log outage need extra custody diversity and appear in the next witnessed report |
| P-8 | One opened device yields no fleet authority | Locked stage holds only public key hashes; reporting seed device-scoped |
| P-9 | Verification paths take public inputs only | Code audit; no secret in the verify path |
| P-10 | Time restricts, never grants | Lint over all rules; property tests with a hostile clock |
| P-11 | Every counter declares capacity, rate and life with a 2× margin | Lint on part profiles |
| P-12 | The specification is small enough to re-implement from scratch | Independent re-implementation from the spec in Phase 3; differential testing |

### 2.4 Objectives with measurable targets

| Objective | Target | Status |
|---|---|---|
| O1 Locked-stage footprint | ≤ 8 KiB code for kernel + admission + hash waist(s) + LMS verify on Cortex-M0+; ≤ 4 KiB RAM | Core 3,962 B [M, not executed]; admission 682 B (Rev 4; 902 B hardened as of the R2 fixes, **stale as of 2026-11-09** pending re-measurement in CI, see CLM-07) [M]; total ≈ 6–8 KiB [E] |
| O2 Admission cost | Bounds and admission ≤ 10 ms at 64 MHz on M0+ | ≈ 3–10 ms [E from loop counts]; to be measured (EXP-19) |
| O3 Single-fault safety, all tiers except HALT | 100% of declared single faults rejected | Proven per table by lint [M] |
| O4 Governance survivability | P(permanent governance loss in 40 yr) ≤ 2% under the reference hazard model | 1.0% [M, illustrative hazards] |
| O5 Power-cut safety | 0 unrecoverable states in ≥ 10⁵ cuts on ≥ 2 ECC-flash families | Host simulator only so far: 6,720 cases [M]; silicon pending (EXP-01) |
| O6 Publicity | 100% of authority acts without presence carry device-verified witnessed receipts | Design; EXP-19 measures cost |
| O7 Reproducibility | Every number in this document reproducible by a script in the repository | §21 |
| O8 Independent implementations | ≥ 2 implementations (C, Rust) plus a Python model agreeing on all small-universe inputs | Phase 1 gate |

### 2.5 Non-goals

Not a new signature scheme. Not a PKI replacement. Not a blockchain. Not a gateway product. Not a hardware company. Not a dashboard. Not protection of one device against a well-equipped local attacker. Not a guarantee about the plant: the kernel governs *who may change the machine*, not whether a validly changed machine is safe. That is the safety function's job, and the kernel only protects the safety envelope's custody (D-19).

---


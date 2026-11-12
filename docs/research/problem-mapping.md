<!-- Title: Problem analysis and problem-to-mechanism mapping -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Reviewed against the R2 red-team findings on 2026-11-12; conflicting passages were corrected in place (see CHANGELOG).

# 1. The deeper problem

### 1.1 One problem wearing many masks

| What practitioners call it | The governed-change question underneath |
|---|---|
| PQC migration | When a class of evidence (RSA/ECDSA signatures) is about to fail, how do we stop accepting it without losing the ability to act? |
| Hash-function weakening | Same question, for a class that every hash-based signature depends on |
| Firmware update | Who may change the code the device runs, and how does the device know? |
| Key rotation / stolen key | How does the device stop trusting one key without being able to ask anyone? |
| Vendor bankruptcy / end of support | Who holds authority when one custodian disappears for ever? |
| Resale, RMA, change of operator | How does authority move between custodians without a bearer secret? |
| Debug unlock, factory provisioning, engineering workstations | Why do these side doors have different, weaker rules from the front door? |
| Safety-limit changes | How do we stop a validly signed change from widening a physical safety envelope? |
| Device offline for 8 years | How does a device catch up without trusting a forged or stale history? |
| Supply-chain attack on a build | How is "who built it" kept separate from "who may make it effective"? |
| Covert targeted update | How do we make every authority act public before it takes effect? |
| Power cut during an authority change | How is state change atomic on non-volatile media with hazards? |
| Decommissioning and resurrection | How does a device die cleanly and come back only under strong evidence? |

### 1.2 Four things fail, not one

The industry's mental model has one failure mode: *keys are compromised.* Over a 40-year life four kinds of thing fail, and each can fail in two ways: it can be **compromised** (it now works for the adversary) or **lost** (it no longer works for anyone).

| Failing thing | Compromise | Loss |
|---|---|---|
| **Parties** (custodians, keys, HSMs, insiders) | Theft, coercion, insider abuse | Bankruptcy, lost keys, staff churn, dissolved escrow agent |
| **Assumptions** (hash families, hardness problems, implementations) | Cryptanalytic break; an implementation bug shared by many keys | A deprecated algorithm that can no longer legally or safely be used |
| **Places** (the site where a device sits) | Malicious insider or contractor with physical access | Unmanned, sealed, orbital or buried device: nobody can be there |
| **Time** (clocks, freshness, ordering) | Manipulated clock, replayed old history | No clock at all after a long sleep |

A rule that tolerates one stolen key but not a dead vendor, or that survives a dead vendor but not a broken hash family, is not a solution. It is a choice of which failure to ignore. This project's earlier passes found many such choices hidden in good designs, including our own.

### 1.3 Assumptions the industry relies on, and what is wrong with each

| Inherited assumption | Why it is incomplete | What replaces it here |
|---|---|---|
| Security is a property of algorithms | Authority fails through custody, policy and procedure long before cryptanalysis | Security is a property of *evidence structures*, of which algorithms are one label |
| A root of trust is one key or one vendor | Vendors and keys do not last 40 years | A root is a monotone policy over independent classes, with defined exits |
| Freshness comes from being online | OT devices are partitioned or offline for years | Freshness from monotone counters and witnessed checkpoints; time may only *restrict* authority |
| Host tools that produce policies are trustworthy | Humans sign what tools show them; a compromised compiler emits an unsafe policy that a valid quorum signs | The device re-derives its own safety and liveness bounds and refuses inadmissible policies |
| Recovery is an operational matter | Every recovery path is an attack path; recovery decides the real security level | Recovery is a tier with an explicit fault budget, presence and publicity |
| Logs and transparency prevent attacks | A log publishes; it does not consent | Publicity is modelled as exposure, not prevention, and is paired with delay and veto |
| More signatures means more safety | Signatures that share an assumption fail together (plain 2-of-3 lets one Keccak break forge both Keccak-based signatures) | Count *independent classes*, not signatures |
| Physical access means game over | True for one device's secrets; false for fleet authority, and presence is also a *resource* | One opened device yields no fleet authority; presence is a deliberate evidence class |

### 1.4 The problem set this foundation addresses

Each governed-change problem G1–G24 is mapped to mechanisms, components, outcomes and validation in §10. Atlas codes (R-, N-, P-) refer to the earlier atlas and blueprints.

| ID | Problem | Class |
|---|---|---|
| G1 | Signature-algorithm obsolescence or break, including a cryptographically relevant quantum computer | Assumption |
| G2 | Hash-family break or weakening | Assumption |
| G3 | Single key compromise | Party |
| G4 | Custodian (group) compromise or insider | Party |
| G5 | Custodian loss: lost keys, dissolved escrow, staff churn | Party |
| G6 | Ownership change: sale, transfer, RMA | Party |
| G7 | Vendor exit or hostility (OEM death or refusal) | Party |
| G8 | Malicious-but-authorised change, including signed harmful settings | Effect |
| G9 | Covert, targeted change (split view) | Time/publicity |
| G10 | Stale or offline device catch-up | Time |
| G11 | Rollback and replay of old authority or images | Time |
| G12 | Power loss during authority change; hazardous non-volatile memory | Record |
| G13 | Policy misconfiguration and bricking by tightening | Rule |
| G14 | Toolchain or host compromise producing an unsafe policy | Rule |
| G15 | Verifier bugs (systematic faults shared by every slot) | Implementation |
| G16 | Side-door authority chains: debug, RMA, provisioning, configuration | Rule |
| G17 | Upward evidence (state reports) without fleet-scale device keys | Evidence |
| G18 | Real-time and safety constraints; recertification cost | Deployment |
| G19 | Brownfield devices that cannot change | Deployment |
| G20 | Provenance of changes (who built it) versus authority (who may make it effective) | Evidence |
| G21 | Long-term verifiability of history after algorithms age | Record |
| G22 | Decommissioning, resale and resurrection | Lifecycle |
| G23 | Time manipulation granting authority | Time |
| G24 | Counter exhaustion and wrap | Record |

### 1.5 What no design can solve

These are stated up front so that nothing later implies otherwise.

* **A device whose immutable verifier accepts only a broken class, and which has no lock and no second path, cannot be rescued by cryptography.** It must be contained or replaced (§6.16).
* **If every class of evidence a device accepts is compromised, no policy can be both safe and live** (interval theorem, §3.6 row (a)). If all cryptography is gone, only presence remains, and one insider has it.
* **A local attacker who defeats a part's physical lock can do anything to that device.** The design bounds the blast radius to that device. It does not prevent the compromise.
* **Fault models are closed-world.** Every guarantee here holds relative to the declared classes. A common-mode fault nobody declared, such as a shared HSM firmware bug, a verifier bug or a ceremony script used by every group, is outside the proof (§17, §18).
* **Systematic faults in the verifier itself** are a single fault on every atom at once. No policy covers them; only implementation assurance does (D-13, D-14, D-20).

---


## 10. Problem → root cause → mechanism → components → outcome → validation

| ID | Problem | Root cause | Mechanism | Components | Expected outcome | Validation |
|---|---|---|---|---|---|---|
| G1 | Signature algorithm obsolete or broken (incl. a quantum computer) | Algorithms hard-coded as the root; classes not counted | Assumption labels from descriptors; `DECLARE_CLASS_DEAD`; renewal invariant; hash-based locked stage | `ac-policy`, `ac-hbs-verify`, planner | Migration is a class retirement, not a re-flash; no tier ever admits DLOG-only evidence | Lint on fleet labels; IR 8547 date tracking; conformance vectors |
| G2 | Hash-family break | Single hash under every signature | Dual families (κ ≥ 2) + presence as third class | dual profile, PRES atom | Silent break forges nothing; declared break leaves governance live with presence | Theorem 1 + lint [M]; EXP-18 independence review |
| G3 | Single key compromise | Keys treated as roots | Single fault never authorises above HALT; continuity-signed rotation | tiers, `ROTATE_KEY` | A thief can at most spend a halt budget | Lint; TLA+ invariant; red-team drills |
| G4 | Custodian compromise / insider | One organisation holds every key | Three custody groups; group as a fault class | custody groups, ceremony | One bad organisation cannot act, unless it also controls the site's presence input (F-R2-04, REQ-LINT-03) | Lint; ceremony audit |
| G5 | Custodian loss | Authority assumes permanent parties | Loss budgets; re-key at T2 (or T1 remote); renewal invariant | `REKEY_GROUP`, govsim | P(permanent governance loss, 40 yr) ≈ 1.0% vs 39% (Rev 2 rule) [M, illustrative] | `brick_mc.py`; EXP-14 calibration |
| G6 | Ownership change | Bearer secrets or vendor mediation | `TRANSFER_OWNER` with current owner + one other group | T1 | Single-hop transfer without a vendor | End-to-end test; pilot |
| G7 | Vendor exit or hostility | OEM required for every change | `SOVEREIGN_EXIT` (OWNER + ESCROW, OEM excluded); halt budget + resume | T2/T1 remote, T0 rules | Fleet survives the vendor; hostile halts are bounded | Demonstration with OEM keys destroyed (Phase 2) |
| G8 | Malicious-but-authorised change | Authority ≠ safety | Safety-envelope tier (widen = T2 with presence); device echo; staging + halt | D-08, D-19 | A remote quorum cannot widen physical limits | Pilot drills; assessor review |
| G9 | Covert targeted change | Unpublished authority | WIT atom required for every act without presence; on-site acts during log outages reported afterwards; monitors | `ac-wit`, logs, `ac-monitor` | Every remote act is public before it is effective | EXP-13 equivocation drill; monitor coverage |
| G10 | Stale-device catch-up | Snapshots trusted, or no history | Chain with per-link historical policy; fresh final receipt; RTC window → presence | `ac-core`, `ac-wit` | Safe against one class break during sleep; visible otherwise | EXP-12 fork simulation |
| G11 | Rollback / replay | Non-monotone state | Monotone epoch and floor; `expect_epoch`, `prev_head`; hardware shadow | `ac-core`, `ac-nv` | Old authority and old images are never accepted | TLA+; EXP-17 rollback with service tools |
| G12 | Power loss; NV hazards | Unsafe flash assumptions | NV contract; program-once units; tagged snapshots; part profiles | `ac-nv` | Device always boots into pre- or post-state | EXP-01 (≥ 50,000 cuts per family) |
| G13 | Bricking by tightening | No liveness check | Lower bound Lo in admission; renewal report | `ac-policy`, lint | A non-live table is refused on the device | Conformance vectors; fuzzing |
| G14 | Toolchain or host compromise | Devices trust compiled policy | Device re-derives U and Lo from labels and refuses | `ac-policy` | A compromised compiler cannot install an unsafe table | Negative vectors; EXP-10 proofs |
| G15 | Verifier bugs | One verifier for all atoms | Two implementations, differential tests, complementary encodings, mutation testing | D-13, D-14, D-20, D-35 | Bugs found before freeze; residual stated | EXP-16 (≥ 95% mutants killed) |
| G16 | Side-door chains | Different rules per chain | Every chain is an action under one admission rule | `ac_step` actions | No authority outside the kernel | Conformance: only `ac_step` emits authority intents |
| G17 | Upward evidence | Devices without signing keys | Gateway-witnessed MAC; conditional LM-OTS | `ac-report`, `ac-enrol` | Auditable state reports including budget status | EXP-03 |
| G18 | Real-time and safety constraints | Crypto near the control loop | Zero-crypto safety core; kernel on a communications processor | P2 pattern | No recertification of the safety image for crypto changes | E-C1 assessor view |
| G19 | Brownfield | Immutable classical verifiers | Sectored gateways as governed devices; dated exit | P3 pattern | Contained, with a replacement date | Pilot; exposure-years KPI |
| G20 | Provenance versus authority | One signature means both | STAGE provenance (any one custody signature) separate from ACTIVATE authority (T1) | D-27 | "Who built it" and "who made it effective" are separate, both public | Conformance; logs |
| G21 | Long-term verifiability | Algorithms age | Witnessed history + RFC 4998-style renewal | logs, planner | History verifiable after classes retire | Renewal drill |
| G22 | Decommission and resurrection | No end-of-life semantics | `LIFECYCLE` + resurrection anchor + `REACTIVATE` | T2 | Clean death; resurrection only with presence and anchor | End-to-end test |
| G23 | Time manipulation | Clocks grant authority | Time only restricts (lint) | D-18, P-10 | A hostile clock can only deny | Property tests with an adversarial clock |
| G24 | Counter exhaustion | Undeclared counter budgets | Capacity ≥ 2 × (life × rate + reserve) lint | D-18, part profiles | No wrap within declared life | Lint; part profile audit |

---


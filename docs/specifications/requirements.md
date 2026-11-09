# Requirements (normative)

**Level:** L2. Keywords MUST/SHOULD per RFC 2119. "Verified by" names a test or states **not yet verified**. Legacy requirements (221 in `research-archive/streams/R_requirements`, IDs UC-, SP-, FR-, NFR-, ADV-, CA-, RD-) are **not yet reconciled** with this set; this set covers the kernel only.

| REQ | Requirement | Source (CLM/ADR) | Component | Verified by |
|---|---|---|---|---|
| REQ-EVD-01 | A device MUST hold at most 8 evidence atoms of kind SIG, PRES or WIT, each with a 32-bit label word. | ADR-002 | evidence | TEST-ADM-01 (partly) |
| REQ-EVD-02 | Assumption labels MUST be derived by the device from the verifier descriptor; group, site and infrastructure labels MUST be declared at T2. | ADR-002 | evidence | not yet verified |
| REQ-EVD-03 | Duplicate key hashes MUST be rejected. | ADR-002 | evidence | not yet verified |
| REQ-ADM-01 | A table MUST be installed only if monotone, within [Lo, U] computed on-device from labels. | CLM-01, ADR-003 | admission | TEST-ADM-01 (p8check) |
| REQ-ADM-02 | A tightening MUST additionally satisfy f_new ≤ f_old. | ADR-003 | admission | TEST-ADM-02 (fixcheck) |
| REQ-ADM-03 | Absent atoms MUST count as compromised and lost in U and Lo. | CLM-05 | admission | TEST-ADM-03 (r2_absent, fixcheck) |
| REQ-ADM-04 | Malformed inputs (cap overflow, k>nf, invalid labels) MUST return an error and install nothing. | F-R2-05 | admission | TEST-ADM-04 (fixcheck) |
| REQ-ADM-05 | Stored tables MUST equal their projection onto present atoms. | F-R2-02 | admission | TEST-ADM-05 (test_projection) |
| REQ-TIER-01 | The device MUST implement tiers T0 HALT, T1 OPERATE, T2 CONSTITUTION with explicit fault budgets (T1 (1,1), T2 recoverable (1,2) default). | ADR-004 | tiers | TEST-LINT-01 (lint.py) |
| REQ-TIER-02 | Re-keying a group MUST live in exactly one tier per profile. | ADR-004 | tiers | not yet verified |
| REQ-PRES-01 | Presence MUST be sampled by the locked stage from an input firmware cannot drive and MUST never suffice alone. | ADR-005 | locked stage | not yet verified (hardware) |
| REQ-PRES-02 | A site-controller group declared at T2 MUST NOT satisfy presence for its own recovery tier in the default profile. | F-R2-04 | lint | **not implemented** |
| REQ-PUB-01 | Authorising evidence sets without presence MUST include a witnessed receipt (≥2 independent logs). | ADR-006 | witness verifier | not yet verified |
| REQ-IMG-01 | The locked stage MUST boot only the image digest committed by an authorised ACTIVATE_IMAGE. | ADR-007 | locked stage | TLA+ model (see SIM-04, incomplete) |
| REQ-CHAIN-01 | History MUST be a per-device hash chain verified under the policy in force at each link, with domain separation. | ADR-008 | record | prototypes (see tests) |
| REQ-HALT-01 | One custody atom MAY halt one bundle at most h times per epoch; a T1 RESUME cancels; a halt never lowers a floor. | ADR-009 | effect | TLA+ (incomplete) |
| REQ-STALE-01 | Chains MUST end at a fresh witnessed checkpoint; authority catch-up older than window W MUST require presence when an RTC is trusted. | ADR-010 | record | not yet verified |
| REQ-LIFE-01 | `DECLARE_CLASS_DEAD` MUST be a T1 tightening; ≥ t+s+1 live classes MUST be kept per tier. | ADR-011, CLM-02 | lifecycle | lint (partial) |
| REQ-LIFE-02 | Installing a key into an ACTIVE slot MUST require the slot holder's co-signature. | F-R2-03 | lifecycle | [M] `ac_key_install_authorised` (src/policy8.c, tested by fixcheck.c I/J/K); modelled in `Repl3OK` (simulations/tla/FirstStage.tla) — TLC run under cfg_base in progress, see GATE-08 in validation-gates.md |
| REQ-NV-01 | Tables MUST be stored with complements and decisions MUST be evaluated twice with complementary encodings. | ADR-012 | locked stage | not yet verified |
| REQ-LINT-01 | A host lint MUST reproduce the on-device bounds for a declared structure. | CLM-06 | tooling | TEST-ADM-01 |
| REQ-LINT-03 | The lint MUST support a declared site-controller group mode. | F-R2-04 | tooling | [M] `site_controller=` parameter in `structures()`/`lint()` (models/lint.py), demonstrated: OPERATE under `OWN` as site controller is unsafe (interval empty) |
| REQ-CLAIM-01 | Documentation MUST label every claim with an evidence class and MUST NOT describe unrun work as done. | ADR-013 | docs | scripts/audit_docs.py |

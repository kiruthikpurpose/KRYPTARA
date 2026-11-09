# Master Engineering Blueprint
## A modular, auditable foundation for post-quantum authority, update and evidence in OT and embedded systems

*Status date: 6 November 2026. No project name is used. Prefixes `ac_` (C) and `ac-` (crates, modules) are placeholders.*

---

## How this document was produced, and what it is not

Six design streams ran in parallel against the second-edition atlas: requirements, architecture, cryptography, embedded, fleet and protocols, and an open-source landscape audit. Two more, formal verification with supply chain and a prototype build, were cut short when you asked me to wrap up. I did **not** run a separate red-team round. In its place:

- the streams challenged the atlas (Part 11), and
- the architecture stream red-teamed its own design (Part 10).

**Read these limits before trusting any section:**

| Item | Status |
|---|---|
| Requirements (221), traceability of all 108 problems | Complete (Appendix A) |
| Architecture, data layouts, API sketches, sequences | Complete (Appendix B) |
| Cryptography, standards status, provider survey | Complete; several checks were cut off by a rate limit and are marked "unverified" inside the memo (Appendix C) |
| Embedded stage: measured sizes, tests, journal | Complete; **no real-hardware cycles** (Appendix D) |
| Fleet, ledger, update, evidence, twin simulation | Complete (Appendix E) |
| Landscape audit | Complete; GitHub APIs were blocked, some years inferred, many repos unverified (Appendix F) |
| Formal verification and supply-chain memo | **Not written.** Part 7 below is my synthesis, labelled as design intent, plus the partial TLA+ results that exist |
| Prototype memo | **Not written.** Only code and measured numbers from the embedded stream exist |
| Independent red team | **Not run as a separate pass.** Part 10 is the architecture stream's self-attack plus my own review |

Evidence labels are those of the atlas: [F] primary fact, [2nd] secondary, [V] vendor, [D] demonstrated or measured, [C] computed here, [E] estimate, [I] inference, [H] hypothesis or invention, [S] speculative. Appendices A–F are the full stream memos (about 70,000 words), unedited except for being concatenated. Where this master and an appendix disagree, **this master prevails**, and Part 11 lists the known disagreements with the atlas.

---

# Part 0. The blueprint on one page

**What we are building.** One ecosystem with a small, doubled, formally checkable *authority core* at its centre and everything else attached through three narrow interfaces. It lets long-lived devices accept change (new algorithms, new owners, new software, new authority) without ever giving a single broken assumption, a single stolen key, or a single faulty update the power to take the fleet.

**The architecture in five sentences.**

1. **An hourglass.** The waist is a frozen, byte-oriented interface: `ac_step` (messages in, intents out), a crypto provider table, and a platform table (storage, counters, entropy, a hint clock). [H]
2. **A tiny core under the waist.** A deterministic function `step(state, message) -> (state', effects)` with no I/O, no allocation, no clock and no libc. It owns the authority record, key-hash slots, floor and epoch counters, and the disjoint-quorum rule. It exists as `core-min` (locked first stage) and `core-full` (updatable second stage). [H]
3. **Three structural invariants.** Only the locked stage mutates authority. An irreversible action needs signatures from members whose assumption sets are pairwise disjoint, each verified in a layer that does not depend on another member (the *verification-locality rule*). Signed policy can only tighten. [H]
4. **Everything else is above or below the waist and replaceable:** algorithms, providers, hardware ports, formats (SUIT, COSE, EAT, CBOM), transports, protocol adapters, ledgers, tools. We reuse existing standards and projects wherever they exist and build only the gaps (Part 6).
5. **Verification is part of the design, not a phase:** two independent implementations of the core, a TLA+ model, reproducible builds, a conformance suite that every port and provider must pass, and frozen formats with a decades-long read-compatibility promise (Parts 7 and 9).

**The five most important results of this engineering pass.**

| # | Result | Evidence |
|---|---|---|
| 1 | **The atlas's recommended slot set and rule are incomplete, in three concrete ways.** (a) Every accepted disjoint pair in {ML-DSA, LMS-SHA-256, SLH-DSA-SHAKE} contains the stateful LMS key, so the fragile stateful key sits in every quorum; add a stateless SLH-DSA-SHA2 slot. (b) A SHA-256-only locked verifier cannot enforce the disjoint rule at all. (c) ML-DSA verified in the *second* stage is not an independent quorum member, because a SHA-256 break forges the second stage that carries the verdict. | Streams A, B, E [I]; (a) and (b) follow from exhaustively enumerating the pairs in the checker `code/B/dq.py` [C] |
| 2 | **A plain 2-of-3 rule is unsafe, now confirmed in a second tool.** The TLA+ model violates the single-assumption invariant under the plain rule, and the checker reproduces the atlas M2 figures: attacker success 0.5249% (plain) against 0.0274% (disjoint), a 19.2× reduction. | TLC run `out_m2_twoof.txt` [C]; `dq.py` [C] |
| 3 | **The core fits comfortably.** SHA-256 + SHAKE256 + LMS verify + the power-fail journal compiles to **3,962 B** on Cortex-M0+ (gcc -Os), 4,717 B with clang. A complete first stage is about 8 KB [E], below the atlas's 13 KB budget. The LMS verifier matched 21 independent reference vectors and rejected all 903 negative cases. The journal passed 6,720 simulated power-cut and torn-write cases with zero violations. | Stream E measured on host and cross-compiled; Thumb binaries were **not executed** [D-local] |
| 4 | **Staging alone does nothing; the halt is the safety mechanism.** In a 2,400-device, 60-site simulation with a faulty update, staged waves without halt left 2.31% of devices out of service against 2.32% for big-bang. Automatic halt cut it to 0.15%. Persisters added about 10% more. | `code/F/migration_twin.py`, 300 seeded runs [C, synthetic] |
| 5 | **We need to build less than we feared.** The ledger can be SCITT over a Tessera log; updates are SUIT in TUF-shaped metadata; evidence is EAT + CoRIM + CycloneDX CBOM; PQ backends are mlkem-native and mldsa-native. The real gaps are: a permissive, proof-backed hash-based verifier sized for a first stage; the disjoint-quorum/floor/PAM policy layer; the part-profile and conformance machinery; and the migration planner. | Streams F, L [F/2nd]; Part 6 |

**What is buildable now, what needs engineering, what needs research:** Part 9.

---

# Part 1. From problems to requirements

## 1.1 The requirements baseline

Stream R turned the 108 catalogued problems (P1–P35, N1–N73) and eleven root causes into a traceable baseline (Appendix A):

| Artifact | Count |
|---|---|
| Adversary classes | 10 |
| Stakeholders | 12 |
| Use cases (UC-01…) | 41 |
| Security properties (SP-01…) | 27 |
| Requirements (185 functional FR-, 36 non-functional NFR-) | 221 |
| Capability areas | 16 |
| Explicit non-goals | 17 |

**Coverage of the 108 problems** (computed by script from the requirements' trace columns [C]):

| Status | Count | Share |
|---|---|---|
| Covered by software requirements | 55 | 50.9% |
| Partially covered (software does its part; a residual needs policy, physics, silicon, contract or market) | 41 | 38.0% |
| Out of scope for software (N12, N33, N34, N49, N54) | 5 | 4.6% |
| Research (N35, N40) | 2 | 1.9% |
| Unitemised in the atlas (P5, P6, P7, P14, P21 mapped through cluster proxies) | 5 | 4.6% |

So **software addresses 96 of 108 (88.9%)** in whole or in part. Of the eleven root causes, four are covered and seven partial. The residuals inside "partial" rows break down as policy 25, physics 11, silicon 10, contract 6, market 4. This is the honest limit of any software project: the rest needs standards bodies, silicon vendors, contracts and procurement. The atlas never itemised P5, P6, P7, P14 and P21; I ask that the original P1–P35 list be recovered if it exists.

## 1.2 The security properties that drive the design

Stated here in compressed form; precise statements and adversary assumptions are in Appendix A (R.3).

| ID | Property | Adversary it assumes |
|---|---|---|
| SP-01 | **Single-assumption safety.** No irreversible authority change is accepted unless the accepting signer set cannot be forged by breaking any one assumption, or stealing any one key. Formally a hitting-set condition: the minimum number of assumptions whose failure forges a set must be at least 2 (Appendix C, B.2). | Remote fleet-scale forger |
| SP-02 | Floor monotonicity: the minimum acceptable security version never decreases. | Remote forger, rollback attacker |
| SP-03 | Power-cut safety: at every step of every authority operation, a reset leaves a bootable, authenticated image. | Environment |
| SP-04 | Blast-radius bound: one forged credential, one opened device or one faulty update affects a bounded, stated fraction of the fleet. | Local physical, insider, faulty vendor |
| SP-08 | Time never grants authority; staleness may only restrict, and never stops a safety function. | Clock manipulator |
| SP-xx | Revocation cannot target current authority without the escrow class and presence evidence (PAM rule). | Forger trying to brick the fleet |
| SP-xx | Evidence stays verifiable for the declared horizon (renewal before algorithm weakening). | Long-term cryptanalysis |

## 1.3 Budgets that became requirements

| Budget | Value | Basis |
|---|---|---|
| First stage, flash | ≤ 16,384 B (MV-1) | Atlas figure 12,864 B plus margin; measured core 3,962 B [D]; complete stage ~8 KB [E] |
| First stage, stack | ≤ 2,048 B | Measured worst path ~856 B [C] |
| LMS-W4 verification | ≤ 60 ms at 64 MHz | 41.5 ms [E] plus margin; **cycles not yet measured on hardware** |
| Counter capacity | ≥ 2× (asset life × rate + emergency reserve) | Atlas 6.6; lint-enforced |
| Asset life | 25–40 years | Atlas |

**Worked counter example [C].** Floor advances: 1 planned per year over 25 years, plus 4 emergency reserve = 29; with 2× margin = 58 steps. A 32-bit unary fuse field offers 32 < 58. So the design uses fuses for the coarse floor and the flash journal for fine steps, and the policy linter refuses any profile whose backing store cannot meet the margin. **Second example [C]:** a 32-bit sampled-values counter at 4,000 frames/s wraps in 2³² / 4,000 s ≈ 12.4 days, so counters must be wider or keys rotated at least daily.

---

# Part 2. Architecture

## 2.1 Seven candidates, scored

Stream A defined six genuinely different architectures and a synthesis (details Appendix B, A.1):

| ID | Architecture | Closest prior art |
|---|---|---|
| A1 | Monolithic PQ boot and update stack | MCUboot, wolfBoot, Nordic NSIB, ST OEMiRoT |
| A2 | Policy-engine-centric (interpreter on every device) | Cedar/OPA style [I] |
| A3 | Authority-ledger state-machine core with adapters | TUF root rotation as a state machine [I] |
| A4 | Layered hourglass with a thin verify waist | TUF/SUIT "verify metadata", X.509 path validation [I] |
| A5 | Microkernel / capability style | TF-M partitions, seL4 [I] |
| A6 | Protocol-gateway-centric (leave devices alone) | Atlas 11.6 generalised |
| **S** | **A3's core inside A4's layering; A5 as an optional profile; A6 for C0/C1** | New combination [H] |

Weighted scores over nine criteria (weights sum to 100; scores are one reviewer's judgement [H], arithmetic checked by script [C]): **S 4.48**, A3 4.20, A4 4.16, A6 3.12, A1 2.74, A5 2.74, A2 2.44.

**Sensitivity [C].** S ranks first under security-first, certification-first, ecosystem-first and uniform weights; first in 18 of 18 one-at-a-time perturbations; first in 65.6% of 100,000 random weight vectors (A4 33.7%). **Under a migration-cost-first weighting A4 wins (4.25 against 4.07).** That finding shapes the plan: ship the A4 layering first and let adopters opt into the authority core device class by device class (Part 9).

**DECISION D-A1.** Select S.
**WHY.** Authority semantics (floor, quorum, PAM, molting) sit in a small checkable machine; extensibility comes from registries and data; the core is a pure function with a closed input alphabet, which helps certification.
**ALTERNATIVES REJECTED.** A1 re-creates root cause R1 inside a bootloader. A2 puts an interpreter on the irreversible path. A5 needs MPU/TrustZone-class isolation that C0–C2 parts lack. A6 does not fix R1 for any updatable device, and "temporary" enclaves become permanent.
**ASSUMPTIONS.** Scores are judgements; adopters will accept a link-time-composed system.
**TRADE-OFFS.** Higher adoption cost and comprehension load than A4.
**VALIDATE.** Adopter study of integration effort; the sensitivity result above is the falsifier.

## 2.2 The layered module map

```
 L4  host / authority side (std, large deps; never on a locked device)
     ac-policyc  ac-bundle  ac-quorumlint  ac-fleetverify  ac-voucher (FDO adapter)
     ac-escrow   ac-sim (migration twin)  ac-cbom  ac-ceremony (HSM)  ac-conformance
 L3  optional device modules (core-full domain)
     ac-stage  ac-report  ac-enrol  ac-timewin  ac-debugauth  ac-lifecycle  ac-gdoi
     ac-protocols (TLS/DTLS/IKE/OPC UA/DNP3-SA/62351 glue: consumers of policy)
 L2  formats and stores (no crypto, no policy)
     ac-cbor-det  ac-cose  ac-suit-glue  ac-codec (fixed records)  ac-journal
 ═══ WAIST (T0, frozen) ═══  W1 ac_step()   W2 provider table   W3 platform table
 L0  ac-core  (core-min: locked stage | core-full: stage 2) -- depends on nothing
 L1  providers (behind W2): ac-sha2 ac-keccak ac-lms ac-slhdsa ac-mldsa ac-mlkem
                            ac-hmac ac-aead ac-hwsha (hardware) ac-ecdsa-legacy (verify only)
     ports (behind W3):     flash-journal, RPMB/secure element, fuse/OTP counters, entropy,
                            clock hint, boot target; Zephyr / bare metal / Linux
```

**Dependency rules, enforced mechanically in CI:**

1. Strict layer DAG, no cycles (`tools/depcheck` fails the build).
2. **The core depends on nothing:** freestanding, no libc, no allocator; CI checks that `nm` of the core object shows zero undefined symbols. All providers arrive through `const` tables.
3. Dependencies point toward stability: a module may depend only on something at least as stable.
4. No dynamic loading and no runtime registration in the locked stage.
5. Crypto libraries know nothing of authority; the core knows nothing of algorithm internals, only IDs and assumption masks.
6. Optional modules have no-op stubs so a C1 build links with zero of them.

**Isolation classes.** Isolated for security: the locked first stage, the HSM signer, the KDC, escrow tooling. Isolated for certification: PQ crypto services on C3 devices run in a separate partition, and `ac-core` is *linked, not merged* into safety code.

## 2.3 Trust boundaries

| # | Boundary | What crosses it |
|---|---|---|
| 1 | Factory → locked stage | **Public key hashes only.** One opened device yields no fleet authority |
| 2 | Authority domain → concentrators | Signed bytes only, never keys (offline or witnessed transfer) |
| 3 | Concentrator → `core-full` | Untrusted bytes, validated before use |
| 4 | `core-full` → `core-min` | A fixed-size proposal (`ac_tx`) which the locked stage fully re-verifies at next reset |
| 5 | Locked stage → second stage | Verified boot target only |

**Design consequence of boundary 4:** a fully compromised second stage can stage a proposal; it cannot burn a floor or replace a slot.

## 2.4 Core data models (layouts compiled and size-asserted with `gcc -std=c11` [D-local])

**Two encodings, one meaning.** Locked-stage and device-resident records are fixed-layout little-endian structs, parsable in a few dozen lines. Exchanged and archived objects are deterministic CBOR inside COSE; the locked-stage-relevant part is embedded as a fixed binary projection `ac_tx_t` whose digest the CBOR commits to. CBOR never enters the locked stage.

| Record | Size | Key fields |
|---|---|---|
| `ac_rec_hdr` | 8 B | `u16 type, u8 fmt_major, u8 fmt_minor, u16 len, u16 flags` |
| `ac_alg_desc` | 16 B | `alg_id, role, tier, assumption_mask(u32), pubkey_len, sig_or_ct_len, flags(stateful, verifiable-in-locked-stage, composite, hw-backed)` |
| `ac_slot` | 48 B | `alg_id, hash_alg, state(EMPTY/ACTIVE/SHADOW/HIDDEN/RETIRED/PENDING), assumption_mask, key_hash[32], activation_floor, group(owner)` |
| `ac_floor_rec` | 32 B | `floor_idx, authority_epoch, journal_seq, last_tx8, crc32` |

**Versioning rules.** An unknown major version returns `AC_E_VERSION` and **never guesses**. Minor versions only append fields. A critical-extension flag forces rejection by readers that do not understand it. CBOR keys: unknown non-negative keys reject; unknown negative keys ignore. Signed content is `label || fmt_version || canonical_bytes` (labels such as `"ac/tx/1"`), preventing cross-protocol replay. **Evidence-grade digests are dual: `SHA-256(x) || SHAKE256(x, 32)`**, so the history chain also has two waists.

**Assumption mask.** A 32-bit set: bit 0 SHA-2, 1 Keccak, 2 module lattice, 3 elliptic-curve discrete log, 4 factoring, 5 code-based, 6 hash-tree state discipline, 16–30 vendor atoms, **bit 31 UNKNOWN, treated as intersecting every other mask**. Masks live in signed algorithm tables, so a cryptographer's correction does not touch the core, and the linter reports how the answer changes if SHA-2 and Keccak are merged into one atom (Part 10, attack 2).

**Slot storage.** MV-1 stores raw 32 B hashes with compile-time descriptors. The full form is 48 B per slot. The atlas's 3 slots become **4** (stream E: a replacement must be provisionable without retiring a live key), so 4 × 32 = 128 B in MV-1, up to 8 × 48 = 384 B in HA-1.

## 2.5 Failure semantics and recovery

**DECISION D-A4.** *Fail closed for authority, fail operational for control.* A failed authority operation leaves the previous state; a failed boot falls through second-stage A, then B, then **last-known-good**, so the process keeps running. Devices never stop a safety function because a signature or clock check failed (SP-08). Recovery paths: alternate slot, last-known-good, board swap (field debug is disabled after commissioning), and the escrow-class quorum.

Stream A's FMEA, flow tables and sequence diagrams (first boot and enrolment, signed update with staging, floor advance with disjoint quorum, OEM-exit slot replacement, offline recovery) are in Appendix B, A.4 and A.9.

## 2.6 Extension mechanisms and stability tiers

**DECISION D-A5.** *Closed core, open registries.* New algorithms, protocols, ports and policy rules enter only through registries, provider tables and signed policy data, never by editing the core.

| Tier | Contents | Promise |
|---|---|---|
| **T0** | The waist, fixed records, the quorum rule, trust-anchor formats | Frozen. Read-compatibility for decades; changes only by major-version coexistence. **T0 is frozen only after three unrelated ports exist** (Part 10, attack 1) |
| T1 | Provider and platform table contents, registries | Additive only |
| T2 | Optional modules, CBOR schemas | Semantic versioning, deprecation windows |
| T3 | Tools, adapters, experimental algorithms | May change |

## 2.7 Configuration

**DECISION D-A6.** Declarative, signed and **tighten-only.** A policy document can narrow what the compiled core permits and can never widen it. A policy compiler (`ac-policyc`) lints for: disjoint-quorum satisfiability, counter capacity (the 2× rule), liveness (a policy must carry the previous valid quorum for rollback, so tightening cannot brick a fleet), and device-class dominance rules. Class profiles C0–C5 are presets.

## 2.8 The waist API (representative; full header Appendix B, A.8)

```c
/* ac_waist.h : T0 frozen. Freestanding. */
#define AC_ABI_MAJOR 1
typedef int32_t ac_status_t;
enum { AC_OK=0, AC_E_FORMAT=-1, AC_E_VERSION=-2, AC_E_SIG=-3, AC_E_QUORUM=-4,
       AC_E_FLOOR=-5, AC_E_STATE=-6, AC_E_PROVIDER=-7, AC_E_NV=-8, AC_E_BUDGET=-9,
       AC_E_PAM=-10, AC_E_RANGE=-11, AC_E_HOLD=-12, AC_E_UNSUPPORTED=-13 };

typedef struct {                 /* W2: const, linked, no runtime registration */
  uint16_t alg_id;  uint32_t assumption_mask;  uint16_t flags;
  ac_status_t (*verify)(const uint8_t *pk, size_t pk_len,
                        const uint8_t *msg, size_t msg_len,
                        const uint8_t *sig, size_t sig_len);
} ac_sig_ops_t;
```

The intent-based design (D-A8) means the core never performs I/O: it returns intents ("burn floor to k", "write slot", "boot image X") that a port executes, which makes the core a pure function that can be model-checked and replayed in a simulator.

## 2.9 Authority commit and hold-down

**DECISION D-A9.** Reset-time commit with kinetic hold-down. A signed transition is verified, journalled, and committed only at the next reset by the locked stage. Boot-count hold-downs buy a window for fleet detection. They are **gameable by anyone who controls reboots**, so they are never the primary control (Part 10, attack 7).

---

# Part 3. The cryptographic layer

(Full detail: Appendix C.)

## 3.1 Standards status as checked on 6 November 2026

| Item | Status | Label |
|---|---|---|
| FIPS 203 / 204 / 205 | Final | [F] |
| FIPS 206 (FN-DSA), HQC | Not final | [F] |
| NIST SP 800-230 (limited-use SLH-DSA sets) | Initial public draft, comments closed | [F, draft] |
| NIST IR 8547 | **Final, 2026-10-27**; classical asymmetric deprecated after 2030, disallowed after 2035 | [F] |
| RFC 9964 (COSE ML-DSA), 9881, 9909, 9935, 10024 | Published | [F]; stream B read them; titles not re-verified here |
| RFC 9858 | Adds SHAKE variants of LMS | [F] |
| CNSA 2.0 | **Excludes SLH-DSA**; conflicts with using SP 800-230 sets in national-security profiles | [F] |
| SUIT | MTI draft in the RFC Editor queue; **no SUIT PQ draft exists** | [2nd] |
| PQClean | Archived 2026-08-04; pqm4 deprecated | [2nd] |
| TPM spec v1.85 with PQ | Reported in a vendor post only | [V] |

**Consequence.** Standards are moving under us, so the data model is algorithm-neutral and the registry carries a **profile switch** (national-security profile uses LMS/XMSS, no SLH-DSA).

## 3.2 The disjoint-quorum rule, made exact

**Rule.** Let each signer type carry a monotone formula over assumption atoms (AND-composites fit; OR-hybrids are forbidden for authority). The *kill number* κ(S, t) of a signer set S is the minimum number of atoms (or stolen keys) whose failure lets an attacker forge t signatures from S. The rule accepts an irreversible action only if κ ≥ 2. A post-quantum epoch profile voids the classical half of hybrids once a quantum threat is declared; a theft budget is added. A safety proof sketch is in Appendix C, B.2.

**Correction to the atlas.** The atlas phrase "pairwise disjoint in at least two members" is imprecise for keys with several assumptions (ECDSA depends on both the elliptic-curve problem and SHA-2); the hitting-set definition above replaces it.

**Verification-locality rule (new).** Each quorum member must be verified in a layer whose own authenticity does not depend on another member. **Consequence:** on parts too small for a locked-stage lattice verifier, the lattice class cannot be an irreversible-quorum member, and diversity degenerates to **hash-only** diversity (SHA-2 vs Keccak). If the part can host an ML-DSA verifier in locked flash, use it. That footprint is unmeasured and is an experiment (E-B1 below).

**Per-key digest rule (stream E).** Each member signs a digest computed under its *own* hash. A shared SHA-256 digest would let a SHA-2 break forge both signatures.

## 3.3 Default slot profiles

| Profile | Slots | Notes |
|---|---|---|
| **MV-1 (minimal)** | S1 SLH-DSA-SHA2 or LMS-SHA-256 (SHA-2 class) · S2 hash verifier in the **Keccak class** · S3 operator/escrow (distinct owner group) · S4 spare for molting | A SHA-256-only verifier **cannot** enforce the disjoint rule (finding F-B2): either add a Keccak-class verifier in the locked stage, or state plainly that the device enforces only the different-slot floor rule |
| **HA-1** | Adds ML-DSA-65 (verified in the locked stage only if it fits), hardware SHA-2 and SHA-3, a twin implementation, a verified state machine | |
| **National-security profile** | LMS/XMSS only, per CNSA 2.0 | SLH-DSA excluded |

Flash cost of a Keccak-class verifier on an M0+ is **unmeasured**.

## 3.4 Provider strategy (decisions; reasons in Appendix C, B.3 and Appendix F)

| Need | Decision |
|---|---|
| ML-KEM and ML-DSA | **REUSE** mlkem-native and mldsa-native (PQCA, proof claims on their pages, tri-licensed Apache/MIT/ISC) behind our provider table |
| LMS verify, SLH-DSA verify | **BUILD** small verify-only implementations. Landscape found no permissive, proof-backed hash-based verifier sized for a first stage; wolfSSL and wolfCOSE are GPL-3.0. Differential-test against several independent implementations |
| PQClean, pqm4 | **AVOID** as dependencies (archived, deprecated); learn from them |
| liboqs | **AVOID** in firmware; usable for host-side differential testing. Not production-grade; its LMS bugs were fixed in 0.16.0; SPHINCS+ removed |
| Hardware engines | Wrap behind `ac-hwsha` |
| Signing | HSM hosts only. **Devices verify; they never sign** (FR-CRY-04) |

## 3.5 Stateful signatures

LMS and XMSS carry an index-reuse hazard. Design: signing only in HSMs with index reservation, crash-safe state, no backup-restore path, multi-HSM leaf partitioning, auditing, and a leaf-index floor on the verifier. Prefer **stateless SLH-DSA** wherever policy allows, which is why the default profile adds a stateless slot. Appendix C, B.5.

## 3.6 Hybrids and the symmetric fabric

**When not to hybridise.** Hybrids that OR classical and PQ verification are forbidden for authority. AND-composites are allowed and credited by the κ calculation.
**Process bus.** IEC 62351-6 MACs and AES-GMAC stay unchanged. ML-KEM-768 enrolment happens once per device. A site KDC derives per-device keys from an *offline* diversification root. The protocol adapter cannot sign ledger statements. Counters obey the 2× capacity rule.
**Corrections.** The atlas's "22 ms, 14.2 KB decapsulation on M0+" has no M0+ source: pqm4 targets only Cortex-M4, and the stack figure matches its unoptimised M4 build; the optimised M4 version needs about 2.8–6.5 KB. I treat the M0+ figure as **unverified**.

## 3.7 Implementation security and testing

Constant-time contract in the provider interface; zeroisation; caller-provided scratch memory with static size queries; KATs and pairwise consistency checks at boot. Tooling: dudect-style statistical testing, ctgrind/timecop-style checks, formal constant-time tools where available. Fault-attack policy is stated at the API level only (redundant verification, no secret-dependent branching); this document contains no attack methods. Test strategy: KATs, ACVP vectors, Wycheproof-style negatives, differential testing across independent implementations, fuzzing. Masking status for ML-KEM/ML-DSA on Cortex-M was not established.

## 3.8 Agility policy

Agility atrophies if unused. Therefore: **an annual slot drill** verifies a release through the *alternate* class alone (GREASE applied to trust anchors); downgrade is prevented by the floor and the policy's tighten-only rule; the registry's tier field turns algorithms through experimental → provisional → standard → deprecated → prohibited.

---

# Part 4. The device side

(Full detail: Appendix D.)

## 4.1 The locked continuity first stage

```
[Reset] → [LOCKED FIRST STAGE: hash verifier + 4 key-hash slots + floor + journal]
              │ verify second stage                trust boundary = the write-lock
              ▼
        [Second stage A | B]  core-full, ML-DSA, hybrid, PQ protocol stacks (updatable)
              │ fail → other slot → fail → last-known-good (process keeps running)
              ▼
        [Application / safety image]
```

**Germline minimalism.** Nothing enters the locked stage that could live in the updatable second stage.

**Measured sizes [D-local, host and cross-compiled, binaries not executed]:**

| Component set | Cortex-M0+ gcc -Os | Clang -Os |
|---|---|---|
| SHA-256 + SHAKE256 + LMS verify + journal core | **3,962 B** | 4,717 B |
| Complete first stage, with boot logic and glue | ~7–8 KB [E] | |
| Worst-path stack | ~856 B [C] | |
| LMS hash calls per verify (W4/H5, host, instrumented) | 473 / 563 / 503 for q = 0, 1, 2 | |
| LMS hash calls (W8/H5) | 4,088 / 3,833 / 5,108 | |
| LMS hash calls (W2/H5) | 182 | |

**Correctness.** 21 vectors from an independent reference (pyhsslms 2.0.0; SHA-256 and SHAKE256; W2/W4/W8; H5/H10) verified; 903 negative cases (bit flips, wrong message, truncation, altered key) all rejected.

**The journal.** Each flash unit is programmed once; the commit point is a SHA-256 tag; a torn entry is marked void and skipped. **6,720 simulated cut points (program units of 4/8/16/32 bytes, clean cuts and torn units with random bit subsets) produced zero violations and never a double-program.** On this design, wear is not the limit; the entry-count budget is. The journal region is the largest locked-flash cost (about 10 KB per stream E), which matters for parts with small locked regions.

**State machine invariants to prove:**
(a) no single-class signer set reaches ADVANCE_FLOOR; (b) a power cut at any step leaves a bootable image; (c) the floor never decreases; (d) revocation cannot target current authority without escrow + presence; (e) slot count never drops below quorum capability.

**Honest limits.** No cycle counts exist on real hardware; every millisecond for the first stage is [E] from measured block counts times an assumed cycles per block. Per-part lock behaviour across warm reset and RMA is unassessed. The first stage cannot be fixed in the field, hence tiny, formally checked and implemented twice.

## 4.2 Integration decisions

| Project | Finding | Decision |
|---|---|---|
| MCUboot | `main` has no PQ support [F, stream E] | Integrate at second stage and above; do not depend on its roadmap |
| wolfBoot 2.10.0 | Has ML-DSA, LMS, XMSS, hybrid [F, stream E]. Licence not verified here (the landscape audit found wolfSSL and wolfCOSE under GPL-3.0) | Learn from; check licence before any wrapping |
| Nordic immutable bootloader | Still ECDSA/Ed25519 | Standalone first stage with an ABI-versioned HAL |
| TF-M, Zephyr, ST OEMiRoT/SBSFU, UEFI/Linux | PQ status **unverified** | Re-check in M0 |
| OpenTitan Earl Grey, Caliptra | Nearest prior art: 4 P-256 + 4 SLH-DSA slots in locked OTP with per-slot revoke states; Caliptra ECC+PQC manifest. **No cross-class floor rule, no authority ledger, no exposure-years** | Learn from; compatible slot concept |

## 4.3 Hardware abstraction

A minimal HAL (flash lock/erase/program, monotonic counter, entropy, hash engine, time sources, watchdog, debug-state query) as a C vtable plus **capability bits**, an ABI version, and a **part profile**: machine-readable lock granularity, OTP size, accelerators, certification evidence, and a *physical-resistance class as a data field with a cited source*. HAL contract tests are part of `ac-conformance`; a port that fails them cannot claim a profile. No physical attack techniques are described here: resistance is assessed per part from published evidence and certification, and the design ensures one opened device yields no fleet authority.

## 4.4 Device classes (C0–C5) as build profiles

| Class | Links | Notes |
|---|---|---|
| C0 inert | Nothing; enclave and replacement date | |
| C1 symmetric-only | Providers: MAC/AEAD; `ac-enrol`; diversified key | Never signs; never shares a fleet key |
| C2 verify-capable | Locked first stage + `core-full` + `ac-stage` + `ac-report` | Decapsulates once at enrolment |
| C3 safety-critical | C2 with crypto in a separate partition; last-known-good; quorum-signed settings | No public-key operation in the control loop (SP-08) |
| C4 concentrators | Full PQ stacks, TPM identity, dual vendor | Never a single point of fleet trust |
| C5 authorities | HSM signers with multi-class quorum | Keys never touch C4 networks online |

Class numbers (flash, RAM, latency) and the pqm4 Cortex-M4 table are in Appendix D, E.4.

## 4.5 Time

A zeitgeber API fuses available time cues (RTC, GNSS, network, authenticated hint) into a *window*, never a point. Time may only restrict. Types are Y2038- and GPS-rollover-safe. Counters declare capacity, rate and life (Part 1.3).

## 4.6 Language and toolchain

**DECISION.** The locked stage and `core-min` are **C99 subset** (no heap, no recursion, bounded loops) built with **two compilers** (gcc and clang, as measured); an independent **Rust `no_std`** twin of the core is the second implementation; Rust is used for updatable layers and host tools. **WHY.** C has the broadest toolchain-qualification and certification track record on the target parts; the twin provides independent-implementation evidence. **ALTERNATIVES REJECTED.** Rust-only first stage (qualified toolchain availability and ABI maturity vary by part; the Ferrocene qualification scope was not read); Ada/SPARK (smaller ecosystem for these MCU families; kept as an option for proof); verified extraction from F*/Low* (strong for primitives, immature for state machines of this shape). **VALIDATE.** Differential testing of C core against Rust twin and the Python model on all subsets of a small universe; sizes tracked in CI against the budget.

## 4.7 Real-time and safety coexistence

The separation of safety and cryptography follows the railway EN 50159 model. A library that wants to be certification-friendly provides: no heap, no recursion, bounded loops, static-analysis evidence, a WCET table per function. IEC 61508, 62443-4-2, DO-326A, ISO 26262 and IEC 62304 clauses were **not fetched**; Appendix D states implications as [I] without clause numbers.

## 4.8 Power and bandwidth

Energy and LoRa airtime figures are [C] from stated formulas with **assumed** current draws [E]. PQ artifacts on LoRaWAN or 802.15.4 need fragmentation or, better, a gateway-held PQ session with a symmetric device key (C1). Detail in Appendix D, E.6.

---

# Part 5. The fleet, authority plane and protocol layers

(Full detail: Appendix E.)

## 5.1 The authority ledger

**DECISION.** The ledger is an **append-only, witnessed transparency log**, built as a SCITT-shaped service (RFC 9943, published 30 Jun 2026) over a tile-based log (Tessera) with C2SP-style external witnesses. We build only the **statement vocabulary and the validity rules** (disjoint-assumption quorum in `COSE_Sign`, floor monotonicity, the PAM rule) as a small verifier library.
**Devices never read the ledger.** They accept only `COSE_Sign` objects checked against their own floor and slot hashes. The ledger lets operators and auditors detect forks, rollbacks and unauthorised floor advances. This keeps clock dependence (R2) and decay (R10) out of the device path.
**ALTERNATIVES REJECTED.** A new log (needless; the stack exists). Device-side ledger reads (clock and connectivity dependence). Sigstore Rekor as-is (public-good centralisation; Rekor v2 uses Tessera so the migration path stays open).
**LIMITS.** Offline and island sites reconcile by sneakernet bundles; the ledger cannot prevent a signed-but-wrong transition, only expose it.

## 5.2 Update and staging

**One protocol: SUIT manifests in TUF/Uptane-shaped metadata**, delivered over whatever transport the site has. Dormancy is a manifest condition plus a separate small **quorum-signed activation order**; **halt is revocation of that order and needs only one signer**, so stopping is cheaper than starting. Crypto-only changes ship separately from functional ones, so they do not drag recertification along.

**Migration-twin results [C, synthetic: 2,400 devices, 60 sites, 300 seeded runs, 365-day horizon; run `python3 -I migration_twin.py 300`]:**

| Strategy | Mean devices out | p95 | Halts |
|---|---|---|---|
| A big-bang, no halt | 2.32% | 3.34% | never |
| B staged waves, no halt | 2.31% | 3.30% | never |
| C staged + auto-halt | **0.15%** | 0.41% | always, day ~31.8 |
| D C + 5% persisters | 0.13% | 0.37% | day ~31.5 |
| F D + activation lease + canary stratified by hardware revision | 0.15% | 0.33% | day ~25.9 |

*Stress case* (site-homogeneous fault, 50% rollback, 10-day report delay): big-bang 10.58%; auto-halt 1.47%; full strategy 1.14%.
*Cost of caution (good update):* exposure rises from 0.131 to about 0.27 unmigrated device-years per device per year, i.e. **staging roughly doubles exposure time** in exchange for the blast-radius reduction; migrated share at one year is 94.5–95.0%.

**Reading.** The atlas's "persisters hedge a defective fix" is only weakly supported: the benefit is about 10% when detection works. The stratified canary halts about 6 days earlier. The simulation is synthetic; real fault correlation is the unknown.

## 5.3 Evidence

**No new format.** A signed state report is an **EAT profile (RFC 9711)** carrying claims that **CoRIM** reference values can appraise (CoRIM is draft-12, not yet an RFC); fleet inventory is **CycloneDX CBOM**; preservation uses **RFC 4998** renewal. The exposure-years calculator reproduces the atlas M5 closed form (4.09 and 15.09 in the tested cases). **Open issue (stream R vs F):** FR-EVD-01 wants signed reports from devices, but the verify-only rule forbids device signing; mechanisms to choose between are hash-based one-time report keys on the device or a gateway witness. I lean to **gateway witness for C1/C2 and one-time hash-based report keys for C3**, [H], to be settled at M3.

## 5.4 Process-bus and protocol adapters

A protocol adapter provides: identity binding, key delivery hook, policy consumption, passive-inference parser. Adapters **cannot sign ledger statements** and cannot call authority intents. PQ status for OPC UA, DNP3-SA v7, IEC 60870-5-7, Modbus Security and Sparkplug is **unverified**; FDO v2.0 recommends PQ but does not mandate it, so the PQ voucher profile is something *we* must propose.

## 5.5 Enclave and gateway

Dual-vendor PQ-terminating gateways, signed gateway configuration, sectored enclaves, exit clocks (every legacy exception carries a signed expiry epoch that the gateway surfaces). Honest limit: containment protects the link, not device firmware trust, and concentrates trust in the gateway.

## 5.6 Migration planner

Class-ordered, hub-first and acquaintance algorithms (atlas M1) become `ac-plan`, taking a trust graph from inventory and emitting an order plus exposure-years projections. **Correction:** the acquaintance rule is inventory-free only in the sense of needing no trust graph; it still needs passive flow observation, so it presupposes the passive parsers.

## 5.7 Fleet failure modes

Compromised KDC, compromised authority, split brain, rollback, replay and stale spares each have a detection and recovery row in Appendix E, F.8.

---

# Part 6. Reuse, wrap, avoid: the landscape decisions

(Full tables with URLs and dates: Appendix F. GitHub APIs were blocked during that audit; release pages show no year, so some dates are inferred and marked; many repositories are marked unverified.)

| Layer | Decision |
|---|---|
| PQ primitives | REUSE mlkem-native, mldsa-native; BUILD verify-only LMS/SLH-DSA; AVOID PQClean, pqm4, liboqs in firmware |
| Bootloaders | LEARN-FROM wolfBoot, MCUboot, Nordic NSIB, ST OEMiRoT, OpenTitan, Caliptra; build the standalone first stage |
| Update and supply chain | INTEGRATE-WITH TUF, SUIT, Tessera/Rekor, Sigstore, in-toto, SLSA |
| Attestation and evidence | INTEGRATE-WITH Veraison, CoRIM, EAT, CycloneDX CBOM, IBM CBOMkit |
| OT protocol stacks | INTEGRATE-WITH open62541, libiec61850, opendnp3 and others at adapter level; no stack ships PQ profiles yet |
| Verification tooling | USE TLA+/TLC (run here), CBMC, Frama-C, Kani, Verus, Cryptol/SAW; adopt HACL*/libcrux/mlkem-native proofs for primitives |
| Host organisation | **PQCA (Linux Foundation)** is the natural host; its blog invites proposals for crypto-agility and migration software. Funding: NLnet, Sovereign Tech Agency, to be checked |

**Collision check (search-limited, not clearance).** Nearest prior art to our core is OpenTitan's root-key block and Caliptra's ECC+PQC manifest (slots and revoke states in locked OTP). Neither has a cross-class floor rule, an authority ledger or exposure-years. DARPA patent US 11,593,488 is conceptually adjacent; four other patents were seen by title only. **Freedom to operate is unverified; counsel is needed before publication.**

**Gap summary, what we genuinely build:**
1. A permissive, proof-backed hash-based verifier for the locked stage.
2. The disjoint-quorum, floor and PAM policy layer, with its compiler and linter.
3. The part-profile format, HAL contract tests and conformance suite.
4. The ledger statement vocabulary and verifier.
5. The migration planner and exposure-years calculator.
6. A PQ FDO voucher profile proposal.

Everything else is integration.

---

# Part 7. Assurance, supply chain and governance

*This part is my synthesis of the planned verification stream; its memo was not written. Items are design intent [H] unless a result is quoted.*

## 7.1 The assurance pyramid

| Level | Applies to | Technique |
|---|---|---|
| Full proof | Locked-stage state machine, record parser, disjoint-quorum checker, counter logic | TLA+ model → refinement to the C by deductive verification (Frama-C/WP) or bounded model checking (CBMC) as a floor |
| Model checking | Authority operations incl. power cut, anergy, PAM, replacement | TLA+/TLC (done in part, below) |
| Proof-backed primitives | ML-KEM, ML-DSA, hashes | Adopt upstream proofs (mlkem-native, mldsa-native, HACL*/libcrux where applicable); re-check claims, which were read from the projects' own pages |
| Differential testing | LMS/SLH-DSA verify, quorum, parser | Multiple independent implementations; C vs Rust twin vs Python model on all subsets |
| Testing only | Adapters, tools, planners | Property-based tests, fuzzing, sanitizers, mutation testing |

## 7.2 Formal model results so far

The TLA+ specification `code/V/FirstStage.tla` models states BOOT, VERIFY_B, VERIFY_ALT, RUN, LKG and BRICK_GUARD, with ADVANCE_FLOOR, REVOKE (PAM rule), REPLACE_SLOT3 and anergy, power cuts at every micro-step of every multi-step write, and an adversary that breaks at most one assumption atom or steals one slot key. TLC 2.19 ran it on two cores.

| Run | Result [C] |
|---|---|
| Plain 2-of-3 rule (`out_m2_twoof.txt`) | **Invariant `Inv_NoSingleAssumptionAdvance` violated** after about 7.2 M states generated: the model finds the single-failure attack the atlas predicted |
| Earlier version v1 (`out_cex0_...v1.txt`) | **Invariant `Inv_NoAnergyLockout` violated** (about 465 K states): the anergy mechanism could lock out legitimate authority. The specification was revised afterwards; I did not review the revision |
| Full model, disjoint rule (`out_base.txt`) | **Not completed.** The run was killed after about 64 M states generated and 13.5 M distinct with 6.6 M on the queue, **with no violation reported up to that point. This is not a proof** |

So the work to be done at M2 is to finish the exhaustive run on a bounded configuration, record state counts, and review the anergy fix. **A counterexample found in the first spec is evidence the process works, and it is also a warning: the atlas's anergy idea (Pattern 1) needs an explicit "never reduce below quorum capability" guard.**

## 7.3 Supply chain

- **Reproducible builds** with pinned, containerised toolchains; every release built independently by two parties and compared.
- **SLSA** provenance and **Sigstore**/**in-toto** attestations; **SBOM and CBOM** with each release.
- **Dogfooding.** Releases are signed with the project's own multi-class quorum, with at least two assumption classes and two named release custodians; a release ceremony is rehearsed annually (the slot-drill idea applied to ourselves).
- Dependency policy: vendored, hash-pinned, minimal; core has none.
- **Threat model of the pipeline** includes the xz-style maintainer compromise: two-person review, no single maintainer can publish, and long-term contributors rotate through release duty.

## 7.4 Independent audit and certification roadmap

| Phase | Audit |
|---|---|
| Before M2 freeze | External design review of the waist and the quorum rule (cryptographers and a formal-methods reviewer) |
| Before 1.0 | Implementation audit of `core-min`, providers, parser; constant-time review |
| Ongoing | Bug bounty, coordinated disclosure, CVE numbering authority |
| Certification (later) | FIPS 140-3 and ACVP validation of providers; IEC 62443-4-1 process; PSA Certified / SESIP evidence for the first stage; Common Criteria where an adopter needs it |

**EU CRA steward obligations were not verified from the primary text in this session.** Treat the CRA statements in the atlas as [2nd] until M1 checks them.

## 7.5 API stability and longevity

Semantic versioning with tiers (Part 2.6). ABI freeze for T0 only after three independent ports. Long-term-support branches; deprecation windows of at least one asset generation for T1/T2. **Trust-anchor formats are frozen forever, with versioned extension.**

## 7.6 Governance and the project's own exit rule

Foundation-hosted (PQCA is the natural candidate), permissive licence with patent grant (**legal uncertainty about post-quantum patents; needs counsel**), no single-company control, bus factor ≥ 3 for each T0 component, and a **graceful-death plan**: the project obeys its own OEM-exit rule, with signing authority, build reproducibility and documentation escrowed so it can be handed over if the maintainers disappear.

## 7.7 Ecosystem threat model (summary)

| Threat | Mitigation |
|---|---|
| Compromise of the project's signing keys | Disjoint multi-class quorum, HSMs, ceremony, transparency log |
| Malicious or coerced maintainer | Two-person review, reproducible builds, independent rebuilders |
| Bug in `core-min` (cannot be patched in the field) | Tiny, proved, doubled, mutation-tested; second stage cannot burn floors |
| Compromised provider library | Differential testing; multiple independent implementations of verifiers; per-key digests |
| Registry/mask error (a wrong independence judgement) | Masks in signed tables; sensitivity report; independent review |
| Faulty release | Staged activation, one-signer halt, persisters, rehearsed rollback |
| Adversary controlling reboots | Hold-down is not a primary control |

---

# Part 8. Repository, build and process

## 8.1 Monorepo layout (D-A7)

```
/core        ac-core (C99, freestanding) + ac-core-rs (Rust no_std twin)
/waist       frozen headers, ABI tests
/providers   sha2 keccak lms slhdsa mldsa mlkem hmac aead hw-adapters
/ports       zephyr baremetal linux hsm-fw + part-profiles/*.toml
/formats     codec cbor-det cose suit-glue journal
/modules     stage report enrol timewin debugauth lifecycle gdoi
/protocols   adapters (opcua, iec62351, dnp3sa, mqtt, lorawan, ...)
/host        policyc bundle quorumlint fleetverify voucher escrow plan sim cbom ceremony
/conformance vectors, HAL contract tests, interop harness
/models      TLA+, Python reference model, simulation scenarios
/docs        architecture decision records (the tables in Part 2-5 as ADRs)
```

**Build:** CMake for C with pinned containerised toolchains, Cargo for Rust; one workspace; reproducible-build job per target. **Why not Bazel or Nix as primary:** higher adoption barrier for the device-maker audience; both are acceptable as optional reproducibility layers. **Dependency rule:** the core has zero dependencies, enforced by CI.

## 8.2 Representative CI gates

1. `depcheck` layer graph. 2. `nm` shows zero undefined symbols in `core-min`. 3. Size budget (flash, stack) per profile. 4. All conformance vectors on every provider and both core implementations. 5. Differential C vs Rust vs Python on all small-universe quorums. 6. TLC bounded configuration passes. 7. Fuzzing with ASan/UBSan, time-boxed. 8. Reproducible build matches across two builders. 9. Policy linter on example fleets (counter capacity, liveness).

---

# Part 9. The phased master plan

Estimates of effort are [E] and rest on the measured lines of code in the prototype: **the reference SHA-256, LMS verifier, journal, quorum and core together came to about 510 lines of C** (`wc -l` of `fs_core.c`, `fs_journal.c`, `fs_quorum.c`, `lms.c`, `sha256.c`), which shows the *decision* code is small. The effort is in assurance, ports, formats and process, not in the core's size. Team sizes are my estimates, not benchmarks.

## 9.1 Milestones

| Milestone | Duration [E] | Deliverables | Acceptance criteria |
|---|---|---|---|
| **M0: Foundations** | 2–3 months | Repo, CI skeleton, decision records from this document, registry of assumption masks with independent crypto review, check of CRA obligations, FTO counsel engaged, re-verification of items marked unverified (TF-M, Zephyr, OEMiRoT, protocol PQ status), **E-A1 desk survey** (which MCU families offer a lockable maker-defined first stage) | E-A1 result recorded: ≥50% of families → proceed on software path; <30% → reopen new-ROM argument |
| **M1: A4 layer + providers** | 4–6 months | `ac-codec`, `ac-cbor-det`, `ac-cose`, `ac-suit-glue`, provider adapters (mlkem-native, mldsa-native), verify-only LMS and SLH-DSA, host bundle tool, conformance suite v0, reproducible build | Every provider passes KATs and differential tests; sizes within budget; two independent builders produce identical binaries |
| **M2: The authority core** | 6–9 months | `ac-core` C + Rust twin, TLA+ model completed and exhaustive on a bounded configuration, quorum compiler and linter, journal on 3 flash types, 2 ports (bare metal, Zephyr) | All five invariants proved or exhaustively checked; power-cut simulation ≥ 10^5 cases with zero violations; the C/Rust/Python differential agrees on all subsets; **external design review passed before any T0 freeze** |
| **M3: Staging, evidence, ledger** | 6–9 months | `ac-stage`, activation order + one-signer halt, state reports (EAT profile), ledger statement verifier on SCITT/Tessera, migration twin v1 calibrated with a pilot, exposure-years calculator, a third port (Linux-class) | Rollout simulation reproduces the pilot's halt behaviour; third port passes the contract tests; **T0 freeze** |
| **M4: Fleet and protocols** | 9–12 months | FDO-PQ voucher profile proposal, KDC reference, adapters (IEC 62351 GOOSE/SV, DNP3-SA, OPC UA, MQTT/Sparkplug), passive parsers, planner, gateway reference | Interoperability event with ≥ 3 external implementers; one real-site pilot |
| **M5: Assurance and certification** | 12–18 months (overlaps M4) | Implementation audit, constant-time review, formal refinement of the locked stage, ACVP/FIPS 140-3 submission for providers, IEC 62443-4-1 process evidence, PSA/SESIP evidence for the first stage | Audit findings closed; certification submissions accepted |
| **M6: Long-term stewardship** | ongoing | LTS branches, annual slot drill, annual release ceremony rehearsal, evidence-record renewal, graceful-death drill | Drills pass in the field |

**Rough team [E, H]:** M0–M1 about 6–8 engineers (cryptography, embedded, build/release); M2–M3 adds two verification engineers and a technical writer; M4–M5 adds protocol engineers and an assurance lead; about 12–15 at peak. The first useful, honest release (M2 plus part of M1) is on the order of 12–18 months from an empty repository, but **I have no reference project to benchmark that against.**

## 9.2 What can be built now, what needs engineering, what needs research

| Category | Items |
|---|---|
| **Buildable now with existing technology** | The hash-based locked first stage (the measured prototype); provider adapters; SUIT/TUF-style staging with one-signer halt; the ledger over SCITT/Tessera; CBOM generation; the quorum linter; the migration twin; the process-bus KDC with ML-KEM enrolment; slot drills |
| **Substantial engineering** | Formal refinement of the locked stage to C; per-part ports and part profiles; conformance suite and interop events; protocol adapters; passive parsers; certification evidence; the Rust twin and dual-compiler release |
| **Needs research or standards work** | A locked-stage ML-DSA verifier on small parts (footprint and independence argument); masking for ML-KEM/ML-DSA on Cortex-M; PQ profiles for OT protocols and FDO vouchers; stateful signature custody beyond HSMs; a sound, independently reviewed assumption-independence model (SHA-2 vs Keccak); real-site fault correlation for rollout models; hardware part resistance classes |

## 9.3 Prototype experiments, ordered by information value

| ID | Experiment | Duration [E] | Decides |
|---|---|---|---|
| E-A1 | Desk survey of lockable first stages across MCU families | 2 weeks | Software path vs new ROM |
| E-B1 | Measure ML-DSA-44/65 verifier and a Keccak-class SLH-DSA verifier in a locked-stage build on two parts | 3–4 weeks | Whether lattice class can join irreversible quorums on small parts |
| E-N3 | Quorum checker over real fleet configurations: does any real deployment share an assumption | 4 weeks | Real-world fraction of unsafe quorums |
| E-N7 | Audit of every counter, time field and signature budget against asset life | 2 weeks | Hidden wrap risks |
| E-T1 | Cycle-accurate measurement of the first stage on two real MCUs, incl. warm reset and RMA lock behaviour | 4 weeks | Replaces all [E] millisecond figures |
| E-V1 | Complete the bounded TLC run and review the anergy fix; refine to C by CBMC | 6 weeks | Proof of invariants a–e |
| E-F1 | Calibrate the migration twin with a real pilot's fault data | 8 weeks | Whether persisters add value |

---

# Part 10. Red team: what could be wrong with this blueprint

Stream A's own attack table is in Appendix B (A.10); the ones that matter most, plus my additions, are below. **This was not an independent red team.** An independent pass remains outstanding and is the first thing I would add if you have budget.

| # | Attack on the design | Assessment | Response and residual |
|---|---|---|---|
| 1 | **The waist is wrong and ossifies.** Frozen T0 interfaces last decades | Real | Small, byte-oriented waist; `fmt_major` coexistence; **no T0 freeze before three unrelated ports and an external review** |
| 2 | **The assumption masks encode judgements** (SHA-2 and SHA-3 are not provably independent; a cryptographer may discount independence) | Real; this is the central modelling risk | Masks live in signed tables; the linter reports sensitivity to merging atoms; independent review at M0 |
| 3 | **Verification-locality degenerates diversity to hash-only on small parts** | True for MV-1/HA-1 | Use locked-stage ML-DSA where it fits (E-B1); be honest in claims |
| 4 | **The lock is not a lock on every part** | True; claims are conditional on part profile | Per-part assessment; public hashes only in the locked stage; one opened device yields no fleet authority |
| 5 | **`core-min` is a single point of fleet-wide failure** | True; doubling helps only if truly independent | Separate authors, clean-room twin, mutation testing, TLA+; limits stated in every assurance claim |
| 6 | **Dual encoding doubles parsing risk** | Real | CBOR never in the locked stage; generated codecs; bounded decoder, fuzzed |
| 7 | **Boot-count hold-down is gameable** by anyone who controls reboots | Yes | Hold-down only buys a detection window; second-channel confirmation and objection window |
| 8 | **The second implementation will be cut under budget pressure** | Likely | It is a release gate for HA-1; no twin, no HA-1 claim; MV-1 may ship with one implementation plus differential fuzz against the Python model |
| 9 | **Adopters will take the A4 layer and ignore the core** | Plausible; A4 wins under migration-cost weighting | Deliver A4 first (M1); add the core per class |
| 10 | **OEM exit after the OEM is gone** (atlas REPLACE_SLOT3 is infeasible without slot 3 at manufacture) | Genuine design change | **Slot 3 (operator/escrow) must be provisioned at manufacture**; owner groups and a successor-diversity bound; legal enforceability of escrow triggers is unknown |
| 11 | **Tighten-only policy can brick a fleet** (liveness) | True | Linter liveness check; previous valid quorum carried for rollback; staged cohorts |
| 12 | **Standards and national mandates conflict** (CNSA 2.0 excludes SLH-DSA; SP 800-230 is a draft) | Real | Profile switch in registry; LMS profile as a first-class option |
| 13 | **Anergy can lock out legitimate authority** (found by TLC in v1) | Demonstrated | "Never reduce below quorum capability" guard; review of the revised spec |
| 14 | **Heavy dependence on a single halt signer is itself an attack surface** (a forged halt order stops all updates) | New; my addition | Halt orders are scoped, expire, and cannot lower the floor; a forged halt delays but cannot downgrade. Needs TLA+ treatment |
| 15 | **Passive inference parsers depend on protocols that change** | Real | Parsers are T3, versioned separately; the evidence value lies in regulator-accepted formats, not parsing |
| 16 | **The whole blueprint rests on one reviewer's scores** | Yes | Sensitivity analysis; adopter study as falsifier |

---

# Part 11. Where this pass disagrees with the atlas

| # | Atlas statement | Finding | Source |
|---|---|---|---|
| 1 | Three slots {OEM class A, OEM class B, operator}; quorum {ML-DSA, LMS} | Every disjoint pair contains stateful LMS; add stateless SLH-DSA-SHA2; use **four** slots | B, E |
| 2 | MV-1 with a single SHA-256 verifier enforces single-assumption safety | It cannot; needs a Keccak-class verifier in the locked stage, or restated claim | B |
| 3 | ML-DSA verified in the second stage forms an independent quorum member | Not independent unless verified in locked flash or hardware | A, E |
| 4 | First stage ≈ 13 KB | Measured core 3,962 B; full stage ≈ 8 KB [E]; the journal region is the larger locked-flash item | E |
| 5 | "ML-KEM decapsulation: 22 ms, 14.2 KB on M0+" | No M0+ source; matches pqm4's unoptimised M4 stack; **unverified** | B, E |
| 6 | "LMS-SHA256 means SHA-256 only" | RFC 9858 adds SHAKE256 variants; SLH-DSA-SHA2 uses SHA-512 at categories 3 and 5 | B |
| 7 | "10.3: pairwise disjoint in at least two members" | Imprecise for multi-assumption keys; hitting-set definition | R, B |
| 8 | Persisters hedge a defective fix | Weakly supported by the twin (~10% when detection works) | F |
| 9 | Acquaintance rule needs no inventory | Needs passive flow observation | F |
| 10 | Persister, halt and staging all add safety | **Only the halt does**; staging alone gave 2.31% vs 2.32% | F |
| 11 | FDO vouchers give a PQ ownership path | FDO v2.0 recommends PQ but does not mandate it; a PQ profile must be proposed | F |
| 12 | 32-bit counters are adequate | A 32-bit sampled-values counter wraps in 12.4 days at 4,000 frames/s | B |
| 13 | ML-DSA-44 signing stack | The 44.8 KB versus 8.4–8.9 KB conflict is unresolved, so no requirement fixes a figure | R |
| 14 | Part 4/11 references to PQClean, pqm4 and liboqs/SPHINCS+ as current | PQClean archived (2026-08-04), pqm4 deprecated, liboqs 0.16.0 removed SPHINCS+ | L |

---

# Part 12. Open questions that could still change the architecture

1. **E-B1:** Can a locked stage carry a lattice verifier on small parts? If not, diversity is hash-only on those parts.
2. **Independence of SHA-2 and Keccak** as a modelling assumption: an independent cryptographic review is needed.
3. **Real-part lock behaviour** under warm reset and RMA, and available hardware monotonic backing.
4. **Device signing for evidence** (gateway witness vs one-time hash-based keys).
5. **Enforceability of escrow triggers**, **CRA steward obligations**, **patent freedom to operate**: all need counsel and the primary texts.
6. **PQ profiles** for OPC UA, IEC 62351, DNP3-SA, Modbus Security and Sparkplug: unverified.
7. **Real fault correlation** in OT rollouts, which decides whether persisters matter.
8. **The original P1–P35 list**, to close the five unitemised problems.

---

# Part 13. Sources

Sources named are those the streams report having read, with detail and URLs in the appendices. A source list for this master alone:

- Atlas, second edition (this investigation).
- Appendix A–F stream memos (this investigation), with their own source lists: A (architecture, includes NIST SP 800-230 announcement, COSE ML-DSA and SLH-DSA drafts, Ferrocene, Kani), B (standards status and provider survey), E (pqm4 `benchmarks.csv` clone of 2026-10-23, pyhsslms 2.0.0, upstream project repositories), F (RFC 9943, RFC 9711, RFC 4998, SUIT, CoRIM draft-12, Tessera), L (project release pages).
- Code and results (all in the working directory under `blueprint/code/`): `B/dq.py`, `F/migration_twin.py` and `run_output.txt`, `V/FirstStage.tla` and TLC outputs, `P/c/*` and `E/fs/*` sources and tests.

**Not verified in this session:** IEC and ISO clause numbers; the FIPS 140-3 and CMVP status of PQ providers; the PQ roadmaps of TF-M, Nordic NSIB, ST OEMiRoT; protocol PQ profiles; the Ferrocene qualification scope.

---

*Appendices A–F follow in the companion file.*

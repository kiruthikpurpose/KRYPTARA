# STREAM A: Overall system architecture

Scope: first-principles architecture of one modular, extensible, open-source library ecosystem for OT / embedded post-quantum (PQ) authority and update security. No project name is used; the placeholder C prefix `ac_` ("authority core") and Rust crate prefix `ac-` are descriptive and replaceable.

Evidence labels follow the brief: [F] [2nd] [V] [D] [C] [E] [I] [H] [S]. Scratch code that produced every [C] number below is in `/home/claude/atlas2/blueprint/code/A/` (`matrix.py`, `quorum.py`, `ac_layouts.h` + `chk.c`, `cbor_size.py`). Layout sizes were compiled with `gcc -std=c11` and `_Static_assert`; they are measured, not estimated.

Web checks made this session (all others are atlas-derived or unverified):
- NIST announced an initial public draft of SP 800-230 (additional SLH-DSA parameter sets for limited-signature use) in April 2026 (nist.gov and csrc.nist.gov news pages in search results). Still a draft. [F, draft]
- The IETF COSE ML-DSA draft (`draft-ietf-cose-dilithium`) had reached revision -11, and an SLH-DSA COSE draft (`draft-ietf-cose-sphincs-plus-06`) existed, in search results. Neither is verified as an RFC here. [2nd]
- IETF SUIT manifest and architecture documents exist (SUIT drafts and RFC 9019 JSON seen in search results). Exact RFC numbers other than 9019 are unverified. [2nd]
- Ferrocene (qualified Rust toolchain) exists and is marketed for safety certification (ferrous-systems.com and the GitHub page in results). Which standards and levels it is qualified for was not read here: unverified.
- Kani is used for Rust standard-library verification (a `verify-rust-std` repository appeared in results). Suitability for this project is [I].

---

## A.0 Summary of the architecture in one page

**The architecture is an hourglass whose waist is a pure, byte-oriented "authority transition" interface, with a doubled, tiny, no-dependency core under it and pluggable adapters on both sides.** [H, selected in A.1]

1. **Core.** A deterministic function `step(state, message) -> (state', effects)`. It has no I/O, no allocation, no clock, no libc and no crypto code of its own. It owns exactly four things: the authority record, the key-hash slots, the floor/epoch counters and the disjoint-quorum rule. It is the only code that decides an irreversible change. It exists in two builds from one source: `core-min` (locked first stage, about 3 KB [E]) and `core-full` (updatable second stage, policy and staging).
2. **Waist.** Three narrow, versioned, language-independent surfaces, all built from bytes and fixed little-endian records: **W1** `ac_step` (messages in, intents out), **W2** the crypto provider table, **W3** the platform table (non-volatile storage, monotonic counters, entropy, a *hint* clock). Everything above (formats, protocols, tools) and below (silicon, RTOS, HSM) talks to the core only through these.
3. **Key invariants made structural** (each is a compile-time or load-time check, not a convention):
   - *Only the locked stage mutates authority.* A compromised second stage cannot burn a floor or replace a slot; it can only stage a proposal that the locked stage re-verifies at next reset.
   - *Single-assumption safety.* An irreversible action needs signatures from at least two members whose assumption sets are pairwise disjoint, and **each of those members must be verified in a layer whose own authenticity does not depend on another member** (new "verification-locality rule", A.1.5, a refinement of atlas 10.3).
   - *Policy can only tighten.* Signed policy documents are data that may narrow what the compiled core permits and can never widen it.
4. **Two encodings, one meaning.** Device-resident and locked-stage records are fixed-layout little-endian structs (parsable in a few dozen lines, no ambiguity). Everything exchanged or archived (policy, bundle manifests, state reports) is deterministic CBOR in COSE envelopes, with the locked-stage-relevant part embedded as a fixed binary projection (`ac_tx_t`) whose digest the CBOR commits to.
5. **Extension without touching the core.** Algorithms, protocols, hardware ports and policy rules enter only through registries, provider tables and signed policy data. Stability tiers T0-T3 with a decades-long read-compatibility promise for T0 formats.

Atlas claim that needs correction (detail in A.1.5 and A.10): the atlas slot set {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256} with quorum {ML-DSA, LMS} is single-assumption-safe only if ML-DSA is verified in the locked stage. When ML-DSA is verified in the second stage, which the atlas HA-1 describes, a SHA-256 break can forge the LMS signature, and through it the second stage, and through it the ML-DSA verdict. This is [I], inference from the layering; it should be modelled in TLA+ (A.10).

---

## A.1 Competing architectures, criteria, scoring and selection

### A.1.1 The seven candidates

Candidates A1-A6 were defined to be genuinely different in where authority semantics live and where the trust boundary sits. S is the refined winner and is scored separately (and flagged as benefitting from hindsight).

| ID | Architecture | Where authority semantics live | What is the "narrow part" | Closest prior art (label) |
|---|---|---|---|---|
| A1 | **Monolithic PQ boot + update stack**: extend a bootloader with PQ verification, A/B slots, rollback counter, one codebase, configuration by Kconfig | In the bootloader's update logic, implicit | None; the bootloader is the product | MCUboot, wolfBoot, Nordic NSIB, ST OEMiRoT (atlas 11.1 prior art [F]) |
| A2 | **Policy-engine-centric**: an interpreter (Cedar/OPA/Rego-like, or signed bytecode) on every device decides everything, including boot and updates | In signed policy programs | The policy language | OPA/Cedar style authorisation [I]; X.509 name constraints as a degenerate case |
| A3 | **Authority-ledger state-machine core + pluggable adapters**: a small deterministic state machine owns authority, slots, floors, epochs and an append-only transition ledger; adapters feed it events | In the state machine | The transition function | Certificate-transparency-style logs, TUF root rotation as a state machine [I] |
| A4 | **Layered hourglass with a thin verification waist**: waist is `verify(manifest, anchor) -> ok`; authority semantics, policy and floors are left to layers above | In layers above the waist | The verify interface | TUF/SUIT-style "verify metadata" interfaces, X.509 path validation [I] |
| A5 | **Microkernel / capability style**: partitions with capabilities for "sign", "burn counter", "unlock debug"; authority is capability possession and delegation | In the capability graph | The kernel and capability ABI | TF-M/PSA partitions, seL4-style capabilities [I] |
| A6 | **Protocol-gateway-centric**: leave devices alone, terminate PQ at gateways/enclaves, sign and manage centrally | In gateway and fleet services | The gateway | Atlas 11.6 containment generalised |
| S | **Synthesis**: A3's authority core placed inside A4's hourglass layering, with A5-style isolation as an optional deployment profile and A6 reserved for C0/C1 | Core + signed policy that may only tighten | The waist: `ac_step` + provider and platform tables | New combination [H] |

### A.1.2 Criteria and weights

Weights are a judgement [H], justified from the atlas: longevity and security dominate because the atlas's central finding is that long-lived devices cannot safely accept change (Part 0; R1, R10, R11).

| Criterion | Weight | Why this weight | What a 5 means |
|---|---|---|---|
| Security (single-assumption safety, blast radius, side-door closure R9) | 18 | Atlas Part 0: the exposure is authority | Authority actions structurally need disjoint quorums; one compromised layer cannot change authority |
| TCB size | 12 | Immutable code cannot be fixed (N20) | Irreversible-decision code is under ~5 KB and formally checkable |
| Flash / RAM | 8 | C1/C2 parts; first stage about 13 KB in the atlas | Fits the MV-1 budget with margin |
| Certifiability (IEC 61508/62443/CC-style evidence) | 10 | R5, recertification cost (N48) | Small, deterministic, traceable, crypto separable from safety code |
| Extensibility | 10 | New algorithms/protocols appear every few years | New algorithm without touching decision code |
| Portability | 8 | 25-40 year, multi-vendor fleets | Same core on bare metal, RTOS, Linux, HSM firmware |
| Migration cost (for adopters from today's stacks) | 8 | R8: change does not get installed | Adoptable incrementally on top of MCUboot/SUIT/TUF-like stacks |
| Decades-longevity | 18 | R10, R11; 25-40 years assets | Frozen formats, read-compat promise, no dependency on any institution or toolchain |
| Developer comprehension | 8 | Maintainers rotate over decades | A new engineer can read the decision code in a day |
| **Total** | **100** | | |

### A.1.3 Scores (1-5, higher is better) and rationale

All cell scores are [H] judgements; the reasoning for the cells that decide the outcome is given after the table.

| Criterion (weight) | A1 | A2 | A3 | A4 | A5 | A6 | S |
|---|---|---|---|---|---|---|---|
| Security (18) | 3 | 2 | 5 | 4 | 4 | 2 | 5 |
| TCB size (12) | 2 | 1 | 4 | 4 | 2 | 3 | 4 |
| Flash/RAM (8) | 4 | 2 | 4 | 5 | 2 | 5 | 4 |
| Certifiability (10) | 2 | 2 | 4 | 4 | 3 | 3 | 5 |
| Extensibility (10) | 2 | 5 | 4 | 4 | 3 | 3 | 5 |
| Portability (8) | 3 | 3 | 4 | 5 | 2 | 4 | 5 |
| Migration cost (8) | 4 | 2 | 3 | 4 | 2 | 5 | 3 |
| Longevity (18) | 2 | 3 | 5 | 4 | 3 | 2 | 5 |
| Comprehension (8) | 4 | 2 | 3 | 4 | 2 | 4 | 3 |
| **Weighted score [C]** | **2.74** | **2.44** | **4.20** | **4.16** | **2.74** | **3.12** | **4.48** |

Rationale for the cells that matter:
- **A1 security 3, longevity 2.** Authority logic is interleaved with image handling, so a bug in image parsing sits in the same trust domain as floor burning; the algorithm set is a compile-time property, which is exactly R1 re-created in a bootloader. Strength: lowest migration cost (4).
- **A2 TCB 1, certifiability 2.** An interpreter on the irreversible path is a large, hard-to-verify TCB; a policy bug is a fleet-wide authority bug. Strength: extensibility 5. Rejected as the *core*, kept as *data* (S: a non-Turing-complete decision table that can only tighten).
- **A3 vs A4 (the real contest).** A3 gets security 5 and longevity 5 because the authority semantics (floor, quorum, PAM rule, molting) are inside a small checkable machine. A4 scores better on portability, flash and migration because a verify-only waist is what existing stacks already have, but it leaves the authority semantics to every integrator, which is where atlas R9 and R10 live (N1-N8 side doors; N57 agility atrophy). A4 with no authority semantics repeats TUF's strength (metadata verification) without the atlas's laws 2, 5, 9 and 12.
- **A5 TCB 2, flash 2, portability 2.** It requires MPU/TrustZone-class isolation that C0-C2 parts often lack, and a capability kernel is itself a large TCB. Retained as an *optional deployment profile* (crypto partition on C3, KDC on C4).
- **A6 security 2, longevity 2.** It does not fix R1 for any updatable device and "temporary" enclaves become permanent (atlas 11.6, 11.10). Retained for C0/C1 only, with a dated exit.
- **S.** A3's core with A4's layering. Certifiability and extensibility rise to 5 because (a) the core is a pure function with a closed input alphabet and (b) all growth goes through registries and data. Migration 3 and comprehension 3 are deliberately not raised: S requires adopters to put an authority core under their existing updater, and a reader must learn the model (slots, floors, quorums) before reading the code.

### A.1.4 Sensitivity analysis [C]

| Test | Result |
|---|---|
| Weight sets: security-first (30/15/5/10/5/5/5/20/5), certification-first, ecosystem-first, uniform | S ranks first in all four (4.60, 4.47, 4.40, 4.33); A3 or A4 second |
| Cost/migration-first (migration 25, flash 15, comprehension 10, security 10) | **A4 wins (4.25) over S (4.07)** |
| One-at-a-time: each weight scaled by 0.5 and 1.5 (18 runs) | S first in 18 of 18 |
| 100,000 random weight vectors (symmetric Dirichlet) | S wins 65.6%, A4 33.7%, A6 0.7%, all others 0% |
| Same, excluding S | A4 80.7%, A3 18.5%, A6 0.7% |
| 20,000 runs perturbing every cell by -1/0/0/+1 | S 60.8%, A4 21.6%, A3 17.7% |
| Pessimistic S (migration 2, comprehension 2) | S 4.32 vs A4 4.16: still ahead |

Reading: S's lead is robust to weights, but **A4 is a strong, cheaper competitor and wins when adoption cost dominates**. That tells us how to sequence delivery: ship the A4 layering first (A.7 milestones), and let the authority core be the addition that adopters opt into per device class. A3 alone never wins over A4 plus A3, so the synthesis is not an artefact of tuning. Limitation: all scores are judgements by one reviewer; the experiment that would falsify them is an adopter study (E-A1 style) comparing integration effort of S against A4 on two real bootloaders [H].

### A.1.5 Decision D-A1: select S, with two refinements the scoring exposed

**DECISION.** Adopt S: hourglass layering, waist = `ac_step` plus the provider and platform tables, a doubled core that is split into `core-min` (locked) and `core-full` (updatable). Refinements:

1. **Only the locked stage mutates authority** ("single mutator rule"). `core-full` can validate, stage and propose; the irreversible commit (journal append, counter burn, slot state change) is done by `core-min` at next reset after it re-verifies the signatures itself.
2. **Verification-locality rule.** For every irreversible action the policy names a quorum with at least `d >= 2` pairwise assumption-disjoint members, and every one of those members must have its signature verified by code that is authenticated *without* relying on any other member's assumption. Concretely in MV-1/HA-1 this limits irreversible quorums to classes the locked stage can verify (hash-based: LMS-SHA-256 / SLH-DSA-SHA2 for the SHA-2 waist; SLH-DSA-SHAKE / XMSS-SHAKE for the Keccak waist). ML-DSA, verified in `stage2`, may be a *third*, additive factor and the primary class for image acceptance and non-irreversible actions, but it cannot be one of the two disjoint members unless the port can afford an ML-DSA verifier in the locked stage.

**WHY.** (1) Atlas law 12 (small, conserved, doubled core) and N20 (unfixable first-stage bug): the smaller the thing that can do irreversible things, the less there is to get wrong. It also removes a whole class of "compromised second stage burns the floor" attacks (R6, R9). (2) Derivation [I]: let `verify_ML` run in stage2 and `stage2` be authenticated by LMS-SHA-256 under slot 1. A SHA-256 failure lets the attacker forge slot 1's signature, hence the second stage, hence the ML-DSA verdict; both quorum members fall to one assumption. Delegated verification collapses the independence that the disjoint-quorum rule is meant to buy.

**ALTERNATIVES REJECTED.** (a) Core only in the second stage: shrinks first stage but any second-stage compromise yields authority change. (b) Everything in the locked stage: cannot be updated and cannot fit ML-DSA on C1/C2 [I]. (c) Trust the second stage's verdict but require it to be authenticated by a quorum itself: that makes every image update a quorum operation, breaking law 2's "boot with one class".

**ASSUMPTIONS.** Part provides lockable flash for about 16 KB (atlas E-A1 survey outcome; if <30% do, the atlas says the new-ROM argument returns); a hash-based verifier for the second waist (SHAKE) fits the HA-1 first stage (unverified size; budget in A.1.6).

**TRADE-OFFS.** Floor advances and slot changes take effect only at reset (acceptable: they ride maintenance windows, atlas 11.5). Lattice diversity is not usable for the two irreversible-quorum members on small parts.

**LIMITS.** Does not protect against a local physical attacker (atlas Part 8); the design limits harm by keeping only public hashes in the first stage. If SHA-2 and SHA-3 are both broken, no hash-based quorum survives.

**HOW WE VALIDATE.** TLA+ (or equivalent) model of `core-min` plus the layering, with the attacker able to forge any key whose assumption set contains one chosen atom; invariants: (a) no single atom failure reaches COMMIT of ADVANCE_FLOOR/REPLACE_SLOT/LIFECYCLE; (b) floor never decreases; (c) power cut at any step leaves a bootable image. Executable cross-check: `/code/A/quorum.py` already enumerates the slot set and confirms (A.1.7).

### A.1.6 Budget for the locked stage (arithmetic)

| Component | Size | Label |
|---|---|---|
| LMS verifier + SHA-256 + glue (atlas "demonstrated") | 12,864 B | [D] atlas 11.1 |
| `core-min`: slot compare, quorum check, floor/journal, record decode | about 3,000 B (about 1,500 C lines at ~2 B/line, wide error bars) | [E] |
| **MV-1 total** | **about 15.9 KB, rounded up to a 16 KB region budget** | [E] |
| Add SLH-DSA-SHAKE verifier + Keccak for HA-1 | unverified; plan 8-16 KB, so HA-1 region 32 KB | [E, low confidence] |
| RAM: LMS stack 1-1.6 KB (atlas) + authority 176 B + floor 32 B + 3 slots 144 B + journal scratch 96 B + tx 104 B (+ signature buffer from flash-resident bundle read in place) | about 2.2 KB; budget 4 KB | [E] |

Note the atlas states 13 KB for the first stage; the 16 KB here is 13 KB plus the core logic the atlas did not size. Flag for the merge agent.

### A.1.7 Executable check of the quorum rule [C]

`quorum.py` encodes assumption masks (H_SHA2, H_KECCAK, LATTICE, DLOG_EC, FACTOR) and tests the rule "accepted set contains >=2 pairwise-disjoint members":

| Signer set | Valid under disjoint rule | Note |
|---|---|---|
| {ML-DSA, SLH-SHAKE} | no | share Keccak |
| {ML-DSA, LMS-SHA256} | yes | disjoint |
| {SLH-SHAKE, LMS-SHA256} | yes | disjoint |
| all three | yes | contains a disjoint pair |

Single-failure test: a plain "any 2 of 3" rule is **unsafe** (Keccak failure forges ML-DSA and SLH-SHAKE: the tool returns `(False, bit=Keccak)`); the disjoint rule is **safe** `(True)`. A degenerate slot set {ML-DSA, SLH-SHAKE} passes the safety test *vacuously* because no valid quorum exists, so the policy linter needs two checks (safety **and** liveness: at least one valid quorum exists and honest availability is above a floor). This reproduces atlas M2/10.3 qualitatively; the 19x probability figure is the atlas's model M2 and was not re-derived here.

---

## A.2 Layered module map

### A.2.1 Classification rules

| Class | Definition | Example |
|---|---|---|
| **Core** | Decides irreversible state; depends on nothing | `ac-core` |
| **Independent library** | Useful alone, no knowledge of the core, own KATs and release cycle | `ac-lms`, `ac-sha2`, `ac-keccak`, `ac-mlkem`, `ac-cbor-det` |
| **Shared infrastructure** | Used by many modules, no policy | `ac-codec` (fixed records), `ac-registry` (IDs), `ac-ct` (constant-time helpers), `ac-test-vectors` |
| **Optional module** | Depends on core, can be omitted per class | `ac-stage` (update staging), `ac-report`, `ac-enrol`, `ac-timewin`, `ac-debugauth`, `ac-lifecycle` |
| **Isolated for security** | Runs in a separate protection domain or device | locked first stage, C3 crypto partition, HSM signer, KDC, escrow tooling |
| **Isolated for reliability / certification** | Kept out of the safety image | PQ crypto services on C3 (R5); `ac-core` is linked, not merged, into safety code |
| **Host-side tooling** | Never on a device; std, large dependencies allowed | `ac-policyc`, `ac-bundle`, `ac-fleetverify`, `ac-sim`, `ac-cbom` |

### A.2.2 Dependency rules (enforced mechanically)

1. **Layer DAG, no cycles.** Layers L0 < L1 < L2 < L3 < L4; a module may depend only on lower layers. Enforced by a build-time include/link-graph check (`tools/depcheck`, fails CI).
2. **Core depends on nothing**: no libc, no allocator, no other module; only `<stdint.h>`, `<stddef.h>`, `<stdbool.h>` under `-ffreestanding -nostdlib`. CI check: `nm` of the core object shows zero undefined symbols; all providers come via tables.
3. **Dependencies point toward stability.** A module may depend only on something at least as stable (tier-wise, A.5.2). T0 (waist, records) depends on nothing above T0.
4. **No dynamic loading, no reflection, no function pointers set at runtime in the locked stage.** Provider tables are `const` and linked.
5. **Crypto libraries know nothing of authority**; the core knows nothing of algorithm internals (only IDs and masks).
6. **Optional means removable**: every L3 module has a no-op link stub so a C1 build links with zero optional modules; module presence is declared in the build profile (A.6).

### A.2.3 Component diagram

```
 L4  host / authority side (std, large deps, never on a locked device)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ ac-policyc  ac-bundle  ac-quorumlint  ac-fleetverify  ac-voucher(FDO adapter) │
 │ ac-escrow   ac-sim/twin  ac-cbom  ac-ceremony(HSM)   ac-conformance           │
 └──────────────────────────────▲────────────────────────────────────────────────┘
                                │ uses canonical bytes (CBOR/COSE, fixed records)
 L3  optional device modules (core-full domain)                      
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ ac-stage  ac-report  ac-enrol  ac-timewin  ac-debugauth  ac-lifecycle  ac-gdoi │
 │ ac-protocols (TLS/DTLS/IKE/OPC-UA/DNP3-SA/62351 glue: *consumers* of policy)  │
 └──────────────────────────────▲────────────────────────────────────────────────┘
 L2  formats and stores (no crypto, no policy)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ ac-cbor-det  ac-cose  ac-suit-glue  ac-codec (fixed records)  ac-journal      │
 └──────────────────────────────▲────────────────────────────────────────────────┘
══════════════════════════ WAIST (T0, frozen) ═══════════════════════════════════
 W1 ac_step()  ◄── messages (bytes) in / intents out ──►  W2 provider table  W3 platform table
 L0  ac-core  (core-min: locked stage │ core-full: stage 2)    depends on nothing
══════════════════════════════════════════════════════════════════════════════════
 L1  providers (independent libraries, each behind W2)       L1  ports (behind W3)
 ┌───────────────────────────────┐                            ┌────────────────────────────┐
 │ ac-sha2 ac-keccak ac-lms      │                            │ nv: flash-journal, RPMB,   │
 │ ac-slhdsa ac-mldsa ac-mlkem   │                            │     SE; counters: fuse/OTP,│
 │ ac-hmac ac-aead ac-hwsha(hw)  │                            │     SE, locked-flash;      │
 │ ac-ecdsa-legacy (verify only) │                            │ entropy; clock hint; boot  │
 └───────────────────────────────┘                            │ target; Zephyr/ESP/Linux...│
                                                              └────────────────────────────┘
```
Note on placement: providers and ports sit *below* the waist (they implement tables the core calls); formats, services and tools sit *above* it (they produce and consume the core's byte messages). Both are arranged so the only thing they share is the waist.

### A.2.4 Trust-boundary diagram

```mermaid
flowchart TB
  subgraph FACT[Factory / CM - C5-adjacent]
    PH[Provisioning HSM: slot hashes, UUID, voucher header]
  end
  subgraph AUTH[Authority domain - C5, offline/witnessed]
    HSM1[HSM class A: LMS/SLH-SHA2]
    HSM2[HSM class B: SLH-SHAKE]
    HSM3[Operator/escrow HSM]
  end
  subgraph CONC[Concentrator zone - C4]
    GW[Gateway / KDC / update server / workstation]
  end
  subgraph DEV[Device]
    subgraph LOCK[Locked flash: TRUST ANCHOR = write-lock]
      CM[core-min + hash verifiers + slot hashes + floor]
    end
    subgraph S2[Stage 2 A/B: authenticated, updatable]
      CF[core-full + ac-stage + ac-report + providers PQ]
    end
    subgraph APP[Application / safety image: C3 isolates crypto]
      APPX[control logic]
    end
  end
  PH -->|public hashes only| CM
  AUTH -->|signed bundles, offline carry| GW
  GW -->|staged bundle (bytes)| CF
  CF -->|proposal ac_tx| CM
  CM -->|verify stage2 + commit| S2
  S2 -->|boot target| APPX
  CF -->|signed state report| GW
```
Boundaries and what crosses them: (1) factory to locked stage: public hashes only (law: one opened device yields no fleet authority); (2) authority domain to concentrators: signed bytes only, never keys (invariant "authority isolation", atlas 12.2 #4); (3) concentrator to `core-full`: untrusted bytes, validated before use; (4) `core-full` to `core-min`: a fixed-size proposal the locked stage fully re-verifies; (5) stage 2 to application: boot target only, and on C3 no public-key operation executes in the control partition (R5).

### A.2.5 Decision D-A2: modularisation and layering

**DECISION.** Modules and rules as in A.2.1-A.2.4; waist is T0 and consists of W1-W3.
**WHY.** Atlas laws 12 and 4: small conserved core, weak linkage through self-describing manifests; R4/R5 (crypto not on every endpoint, not co-located with safety). The classification lets C1 builds exclude everything but providers and a symmetric MAC, and C3 builds isolate crypto.
**ALTERNATIVES REJECTED.** (a) One library "everything": violates TCB and certifiability goals. (b) A plugin ABI with dynamic loading: a runtime-extensible TCB is the opposite of the invariants. (c) Splitting the core into per-feature micro-libraries: more interfaces, more ABI to freeze, little gain.
**ASSUMPTIONS.** Integrators accept a link-time-composed system; Linux-class devices may use shared objects above the waist but never below.
**TRADE-OFFS.** Link-time composition means any extension is a rebuild and re-release of stage 2 (fine: stage 2 is updatable). The locked stage never changes.
**LIMITS.** Optional modules multiply the combinations to test; mitigated by profile presets (A.6).
**HOW WE VALIDATE.** `depcheck` in CI; symbol audit of core; a conformance suite (`ac-conformance`) that runs the same vectors against every provider, port and both core implementations.

---

## A.3 Core data models (byte-level)

### A.3.1 Conventions and versioning rules

| Rule | Statement | Why |
|---|---|---|
| Two encodings | Device-resident and locked-stage records: fixed layout, little-endian, no padding (packed, all sizes compile-time asserted). Exchanged/archived objects: deterministic CBOR (core deterministic encoding of RFC 8949, not re-fetched this session) inside COSE | A fixed layout can be parsed by a 30-line verifier; CBOR gives schema evolution and tooling for objects the locked stage never parses |
| Record header | Every fixed record starts with `ac_rec_hdr` (8 B): `u16 type, u8 fmt_major, u8 fmt_minor, u16 len, u16 flags` | Self-describing, so records survive ports and decades |
| Major version | Change means incompatible; a reader seeing an unknown major returns `AC_E_VERSION` and **never guesses** | Fail-closed on authority data |
| Minor version | Fields may only be appended; `len` says how many bytes are present; readers ignore trailing bytes they do not know, but CRC/digests cover them | Forward compatibility |
| Critical flags | `flags` bit 15 = "critical extension present": a reader that does not understand the extension must reject | Same intent as X.509 critical extensions |
| CBOR map keys | Non-negative integer keys unknown to a reader: reject (critical). Negative integer keys unknown: ignore (non-critical) | Extension without silent semantics change |
| Domain separation | Signed content is `TBS = ctx_label || fmt_version || canonical_bytes` with labels like `"ac/tx/1"`, `"ac/policy/1"`, `"ac/report/1"` | Prevents cross-protocol replay |
| Digests | Evidence-grade digests are **dual**: `SHA-256(x) || SHAKE256(x, 32)` (64 B). Concatenation is at least as collision- and preimage-resistant as the stronger component | Two waists even in the history chain [I] |
| Integrity vs authenticity | `crc32` fields detect bit-rot only; they are never security fields | Avoid misuse |
| Counters | Every counter declares capacity, rate and asset life; policy lint requires `capacity >= 2 x (life x rate + emergency reserve)` (A.3.4) | R10/R11, atlas 6.6 |

### A.3.2 Algorithm descriptor `ac_alg_desc` (16 B, measured)

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0 | 2 | `alg_id` | Registry ID (A.5.1) |
| 2 | 1 | `role` | 1 sig, 2 hash, 3 kem, 4 mac, 5 aead, 6 kdf |
| 3 | 1 | `tier` | 0 experimental, 1 provisional, 2 standard, 3 deprecated, 4 prohibited (policy-controlled, A.5.2) |
| 4 | 4 | `assumption_mask` | Bit set of hardness assumptions (A.3.3) |
| 8 | 2 | `pubkey_len` | bytes |
| 10 | 2 | `sig_or_ct_len` | bytes |
| 12 | 2 | `flags` | bit0 stateful (index reuse hazard); bit1 verifiable-in-locked-stage; bit2 composite (v2); bit3 hardware-backed |
| 14 | 2 | `rsvd` | zero |

Policy lint reads `bit0` to demand index-reservation HSM custody (LMS) and `bit1` to enforce the verification-locality rule.

### A.3.3 Assumption-class set (32-bit mask)

| Bit | Atom | Which standard algorithms carry it (atlas 10.3, [I] on exact lists) |
|---|---|---|
| 0 | H_SHA2 | LMS-SHA-256, SLH-DSA-SHA2, ECDSA (hash), HMAC-SHA-256 |
| 1 | H_KECCAK | SLH-DSA-SHAKE, ML-DSA (SHAKE), ML-KEM (SHA-3/SHAKE) |
| 2 | LATTICE_MODULE | ML-DSA, ML-KEM (MLWE/MSIS) |
| 3 | DLOG_EC | ECDSA, Ed25519, ECDH |
| 4 | FACTORING | RSA |
| 5 | CODE_BASED | HQC, McEliece (future) |
| 6 | HASH_TREE_STRUCT | stateful hash-tree structure risk (LMS/XMSS state discipline) |
| 7-15 | reserved standard atoms | added by registry process |
| 16-30 | vendor/private atoms | never assumed disjoint from anything standard |
| 31 | UNKNOWN | **treated as intersecting every other mask** |

Rule: the intersection of two masks nonempty means "not independent". An unknown or vendor atom is conservative. A hybrid-AND key currently carries the *union* of its parts (safe but pessimistic); a v2 `composite` flag with kill-set semantics would credit AND-hybrids (forward-compat slot reserved in `flags` bit 2).

### A.3.4 Key-hash slot `ac_slot` (48 B, measured)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | `alg_id` |
| 2 | 1 | `hash_alg` (1 SHA-256, 2 SHAKE256-256) |
| 3 | 1 | `state` (0 EMPTY, 1 ACTIVE, 2 SHADOW, 3 HIDDEN, 4 RETIRED, 5 PENDING) |
| 4 | 4 | `assumption_mask` |
| 8 | 32 | `key_hash` = H(canonical public-key encoding with domain label) |
| 40 | 4 | `activation_floor` |
| 44 | 1 | `group` (owner group: 1 OEM, 2 operator, 3 escrow, ...) |
| 45 | 3 | `rsvd` |

Storage: MV-1 stores only 3 x 32 = 96 B of raw hashes plus compile-time descriptors (atlas figure); the full form is 3 x 48 = 144 B, HA-1 up to 8 slots = 384 B. `state` encodes the molting protocol (provision alongside = PENDING/SHADOW, hide = HIDDEN, shed = RETIRED). `group` lets the quorum rule count owner diversity (needed for OEM exit, A.9.4).

### A.3.5 Floor / epoch counter record `ac_floor_rec` (32 B, measured)

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | header (`type = FLOOR`) |
| 8 | 4 | `floor_idx` (minimum acceptable image security version) |
| 12 | 4 | `authority_epoch` (increments on every authority change: floor advance, slot change, lifecycle) |
| 16 | 4 | `journal_seq` |
| 20 | 8 | `last_tx8` (first 8 B of the last accepted transition digest) |
| 28 | 4 | `crc32` |

Storage: two copies (A/B) plus journal (A.3.6) in locked-write flash; where available, a hardware monotonic backing (OTP/fuse unary, secure-element or RPMB counter) holds a *shadow* `floor_idx` so a flash restore cannot rewind it. Budget arithmetic [E]: 25-year life, 1 planned advance/year + 4 emergency reserve = 29 advances; with 2x margin 58 steps. A 32-bit unary fuse field covers only 32 < 58, so the design uses fuses for the coarse floor and the flash journal for fine steps, and the lint refuses a profile whose backing store cannot meet the 2x margin. Any reset path (rewinding a counter or restoring a signer) is an authority action requiring the highest quorum plus physical-presence evidence (atlas pattern 18) and is recorded in the ledger.

### A.3.6 Authority record `ac_authority` (176 B, measured) and ledger journal

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | header (`type = AUTHORITY`) |
| 8 | 16 | `device_uuid` |
| 24 | 1 | `dev_class` (0..5 = C0..C5) |
| 25 | 1 | `lifecycle` (0 TEST, 1 PROVISIONED, 2 PROD, 3 RMA, 4 DECOMMISSIONED) |
| 26 | 1 | `slot_count` |
| 27 | 1 | `quorum_rule_id` (compiled rule: 1 = d2 disjoint) |
| 28 | 4 | `authority_epoch` (mirror) |
| 32 | 4 | `floor_idx` (mirror) |
| 36 | 4 | `flags` (bit0 debug-disabled, bit1 senescent, bit2 anergic-class set, bit3 exit-mode) |
| 40 | 32 | `policy_hash` (active policy) |
| 72 | 32 | `slots_digest` (hash of slot array) |
| 104 | 64 | `ledger_head` (dual hash chain head) |
| 168 | 4 | `crc32` |
| 172 | 4 | `rsvd0` |

Ledger journal entry `ac_journal` (96 B, measured): header 8, `seq` 4, `action` 1, `n_sigs` 1, `rsvd` 2, `new_floor` 4, `new_epoch` 4, `tx_digest` 64 (dual), `commit_marker` 8. Commit protocol (power-fail safe): write entry without marker, verify read-back, write marker, then update A/B records, then burn hardware counter; recovery replays idempotently (invariant (b)). Appended entries form the on-device "ordered memory" that atlas I-12 and pattern 18 call for.

### A.3.7 Transition projection `ac_tx` (104 B, measured)

The only authority-change object the locked stage parses.

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | header (`type = TX`) |
| 8 | 1 | `action` (1 ADVANCE_FLOOR, 2 ADD_SLOT, 3 REPLACE_SLOT, 4 LIFECYCLE, 5 REVOKE, 6 COUNTER_RESET, 7 REPLACE_OWNER_GROUP) |
| 9 | 1 | `n_sigs` |
| 10 | 2 | `rsvd` |
| 12 | 16 | `target_hash16` (device UUID or cohort selector hash; prevents cross-device replay) |
| 28 | 4 | `new_floor` |
| 32 | 4 | `new_epoch` |
| 36 | 4 | `expect_epoch` (anti-replay: must equal the device's current epoch) |
| 40 | 64 | `manifest_digest` (dual digest of the CBOR bundle manifest, binding all metadata) |

Followed by `n_sigs` entries `{u8 slot_idx, u16 alg_id, u16 sig_len, sig bytes}` signed over `TBS("ac/tx/1" || tx)`. The **PAM rule** is structural here: a `REVOKE` whose target `key_hash` matches any ACTIVE/SHADOW slot is invalid unless it carries the escrow group's signature **and** a `presence` flag in the manifest (atlas pattern 5).

### A.3.8 Signed state report (deterministic CBOR; measured example)

COSE envelope `COSE_Sign1` (device attestation key) for C2+, or `COSE_Mac0` (diversified symmetric key, tag 32 B) for C1/constrained devices (R4: no public-key work on endpoints that cannot afford it).

| Key | Field | Notes |
|---|---|---|
| 1 | `fmt` | 1 |
| 2 | `device_uuid` (16 B) | |
| 3 | `nonce` (16 B) | verifier-supplied freshness; if absent, `boot_count` + `report_seq` |
| 4 | `dev_class` | 0..5 |
| 5 | `lifecycle` | |
| 6 | `floor_idx` | |
| 7 | `authority_epoch` | |
| 8 | `slots[]` | per slot `[idx, alg_id, state, group, key_hash]` |
| 9 | `image_hash` (32 B) | active image |
| 10 | `policy_hash` (32 B) | |
| 11 | `ledger_head` (64 B) | |
| 12 | `time_window` | `{earliest_epoch, latest_epoch, source_mask}`; window, not a point (atlas 6.5) |
| 13 | `budgets[]` | `[counter_id, capacity, used]` (exposure of counters before they run out) |
| 14 | `last_drill_epoch` | slot drill (I-13) |
| 15 | `flags` | senescent, anergic, exit-mode |
| 16 | `staged[]` | hashes of staged bundles |

Measured with `cbor_size.py` (3 slots, realistic integer widths, all hashes present): **340 B payload**. Add signature: COSE_Mac0 tag 32 B -> about 400 B total [E]; with an ML-DSA-65 attestation signature of 3,309 B (FIPS 204 parameter, not re-fetched; unverified) about 3.7 KB [E]. For a LoRaWAN-class link the report is not sent raw: a 16 B truncated tag over a 64 B digest is sent instead and the full report fetched on demand [H].

### A.3.9 Transition bundle manifest (deterministic CBOR; measured example)

| Key | Field | Notes |
|---|---|---|
| 1 | `fmt` | |
| 2 | `bundle_id` (16 B) | |
| 3 | `kind` | 1 FIRMWARE, 2 AUTHORITY_ONLY, 3 POLICY, 4 ALG_TABLE, 5 COMBINED (**forbidden by default**: crypto-only changes are kept separate from functional ones, atlas N48) |
| 4 | `target` | `{class_mask, hw_family_ids[], selector}` |
| 5 | `from` | `{min_floor, min_epoch, prior_image_hash}` |
| 6 | `to` | `{new_floor, new_epoch, slot_ops[]}` |
| 7 | `payloads[]` | `{dual_digest, size, uri or SUIT manifest ref}` |
| 8 | `staging` | `{earliest_activation_epoch (coarse month index), cohort, persister_ppm, halt_ref}` |
| 9 | `rationale` | human-readable text, <= 256 B, signed (atlas I-12) |
| 10 | `assumption_decl` | mask of the assumption classes the signers claim; linted against policy |
| -n | non-critical extensions | |
| tx_bin | embedded `ac_tx` bytes | the locked-stage projection |

Measured example manifest: **300 B** without signatures. A quorum {LMS-SHA-256 W4 n=32 (2,508 B, atlas) + SLH-DSA-SHAKE (about 7.9 KB for the -128s set, FIPS 205 value, unverified)} adds about 10.4 KB, a hash-pair bundle of about 10.8 KB [E]; replacing the second member with an ML-DSA-65 signature (3,309 B) gives about 6.2 KB [E] for stage-2-only actions. For firmware, the payload manifest is a SUIT manifest wherever the target already speaks SUIT; this envelope adds only the authority metadata.

### A.3.10 Policy document (deterministic CBOR, signed by quorum)

| Key | Field | Notes |
|---|---|---|
| 1 | `fmt`, 2 `policy_id`, 3 `version`, 4 `min_authority_epoch` | |
| 5 | `applies_to` | class mask, hw families |
| 6 | `alg_table[]` | allowed `alg_id`, `tier`, `valid_until_epoch` (coarse) |
| 7 | `rules[]` | `{action, t, d, required_groups[], locus: LOCKED/STAGE2, hold_boots, objection_window}` |
| 8 | `revocation` | PAM rule parameters |
| 9 | `staging_rules` | cohorting, persister_ppm, halt conditions |
| 10 | `time_rules` | drift bound ppm, staleness epochs (can only restrict) |
| 11 | `counters[]` | `{id, capacity, rate, life, margin}` |
| 12 | `degrade_ladder` | normal -> LKG -> safe minimal -> senescent |

**The policy is data with a closed grammar, not code**: no loops, no conditionals beyond `rules[]` matching on enumerated fields. The core's own compiled minimum (rule 1 = `d >= 2` pairwise disjoint, `t >= 2`, locus LOCKED for irreversible actions) can only be tightened (`t`, `d` up, more groups, longer holds), never loosened; the loader rejects a loosening policy as `AC_E_QUORUM`.

### A.3.11 Decision D-A3: dual encoding, fixed records plus deterministic CBOR

**DECISION.** Fixed records for the locked stage and NV state; deterministic CBOR + COSE for everything exchanged; one binary projection `ac_tx` linking them.
**WHY.** R1/N20: the locked stage must have a trivially auditable parser (atlas law 12). Evidence and policy must evolve for decades (R10) and interoperate with SUIT/COSE/RATS/CBOM tooling (R7). The projection avoids CBOR in the TCB while keeping rich metadata signed (via `manifest_digest`).
**ALTERNATIVES REJECTED.** (a) CBOR everywhere: the locked stage would need a CBOR parser (attack surface in immutable code). (b) Fixed records everywhere: no evolvability for policy and reports; tool ecosystem lost. (c) ASN.1/DER: larger, historically parser-bug-prone [I]. (d) Protobuf/CBOR-without-determinism: signatures over non-canonical bytes.
**ASSUMPTIONS.** COSE PQ algorithm registrations will be completed in the IETF drafts; until then PQ algorithms use private-use COSE IDs and the `alg_id` registry here is authoritative (flag: COSE ML-DSA draft at -11, unverified final).
**TRADE-OFFS.** Two encodings mean two decoders and a consistency obligation; mitigated by generating both from one schema (A.7) and testing round-trip.
**LIMITS.** Little-endian fixed layouts are fine for the Arm/RISC-V targets in scope; a big-endian port converts at the port boundary.
**HOW WE VALIDATE.** Generated codecs plus property tests (decode(encode(x)) = x; non-canonical inputs rejected); `_Static_assert` sizes (done: all six layouts compile and match); fuzzing of decoders; cross-implementation vector exchange between the C and Rust codecs.

---

## A.4 Information and authority flow, failure propagation, recovery

### A.4.1 Information flow and authority flow

| Flow | From -> to | Carries | Authority rule |
|---|---|---|---|
| F1 provisioning | Factory HSM -> locked stage | public key hashes, UUID, voucher header | one-way, public only; log co-signed by CM and OEM (N8) |
| F2 authority bundles | C5 HSMs -> C4 distribution -> `core-full` | signed `ac_tx` + manifest | signatures in disjoint classes; offline carry allowed |
| F3 firmware | C4 -> `ac-stage` -> inactive A/B slot | payloads + SUIT | staged dormant; verified in stage 2 and locked stage |
| F4 commit | `core-full` -> `core-min` | `ac_tx` proposal | locked stage re-verifies, appends journal, burns counter |
| F5 evidence | device -> C4/C5 | state report | verified against ledger; deviations raise alarms (danger-based alerting, atlas 11.7) |
| F6 keys | KDC (C4) -> devices | per-device diversified keys | wrapped by the ML-KEM enrolment KEK |
| F7 time cues | cues -> `ac-timewin` | window updates | may only tighten, never grant (atlas 6.5 rule 3) |

Authority never flows downward by configuration (promotion rule, atlas 12.2 #5); it flows only through signed `ac_tx`.

### A.4.2 FMEA (severity S1 low to S5 fleet-wide authority loss)

| # | Component / failure | Effect | S | Detection | Containment | Recovery path |
|---|---|---|---|---|---|---|
| 1 | Locked stage verifier bug (N20) | Wrong accept or reject of images/tx | 5 | Differential test of two implementations; fleet reports with anomalous ledger | None in place: stage immutable | Doubled implementation reduces odds; board swap; enclave containment |
| 2 | `core-min` quorum logic bug | Irreversible action wrongly allowed | 5 | TLA+ model, fuzzing, two-impl differential | Policy can only tighten (A.3.10) | Same as 1; a second quorum check at stage 2 raises alarm but cannot block |
| 3 | Single hash waist broken (SHA-2 or Keccak) | Forgeable keys in that class | 4 | Cryptanalytic news; none on-device | Disjoint-quorum rule: no single class suffices | Molt: shed that class under a quorum of the other two (A.9.3) |
| 4 | Second stage compromised | Arbitrary stage-2 behaviour | 4 | Locked stage re-verifies on each boot; report mismatch | Single-mutator rule: cannot burn floor or change slots | Floor advance via locked stage; A/B rollback to LKG |
| 5 | Power loss during commit | Partial journal | 3 | Marker absent at boot | Journal-first protocol; idempotent replay | Recovery step in `ac_recover()` |
| 6 | NV store corruption (bit-rot) | Authority record invalid | 4 | crc + A/B + dual hash chain | Two copies + hardware shadow | Rebuild from journal; else LKG with senescent flag |
| 7 | Counter wrap / budget exhausted (R11) | Cannot advance floor | 4 | `budgets[]` in reports, lint at build | 2x margin rule | Reset path = top quorum + presence; else replacement |
| 8 | Restore from backup (R6) | Floor rewound | 5 | Hardware shadow mismatch | Counter backed by hardware where available; else locked journal | Treat as COUNTER_RESET attempt; require authority |
| 9 | Provider returns wrong result (HW SHA fault) | False verify | 4 | Known-answer self-test at init; dual-provider mode for HA-1 | Core fails closed on authority actions, open on run | Fall back to software provider |
| 10 | Policy doc malformed or loosening | Wrong rules | 3 | Loader rejects | Closed grammar, tighten-only | Previous policy stays active |
| 11 | OEM exit with no slot 3 (N41, N7) | Fleet orphaned | 4 | Fleet inventory (`slots[]`) | Requirement in procurement profile; lint refuses profiles without slot 3 | Replacement; "hopelessly queenless" report |
| 12 | Clock wrong (R2, R11) | Staleness misjudged | 2 | Window sanity against other cues | Time can only reduce privileges | Technician token narrows window |
| 13 | Update bricks fleet (CrowdStrike-class) | Mass outage | 5 | Staged cohorts, halt signals | Persisters, no simultaneous activation, LKG | Auto halt, LKG boot |
| 14 | HSM key loss / LMS state loss | Cannot sign in class | 4 | Slot drill failure | Disjoint classes; third slot | Quorum of remaining disjoint classes |
| 15 | LMS index reuse (R6) | Forgery by reuse | 4 | HSM index log, transparency | Index reservation, SLH-DSA preferred when final | Shed class; molt |
| 16 | Attacker holds one device (Part 8) | Local extraction | 2 (fleet) / 5 (device) | Out of scope | First stage holds only public hashes; per-device keys | Replace device; revoke its UUID-bound credentials |
| 17 | Attestation key compromised | Forged reports | 2 | Ledger cross-check | Report is evidence, not authority | Rotate attestation key by tx |
| 18 | Conflicting successors (N49-style) | Split ownership | 4 | Stop-signal objections | No irreversible step during open objection | Escalated tie-break (A.9.4) |
| 19 | Registry / tool bug in `ac-policyc` | Bad policy signed | 4 | Lint, dry-run in `ac-sim` | Dual review, dry-run on twin | Staged cohorts, persister |
| 20 | Boot failure of both A/B | No second stage | 3 | Boot counter | Last-known-good keeps running | Offline recovery (A.9.5) |

### A.4.3 Recovery paths (ordered, least to most disruptive)

1. Automatic: A/B fallback, then last-known-good image, which runs the process in a restricted-authority state (senescent flag, no authority changes accepted).
2. Staged re-try: re-download and re-verify a bundle; halt-and-hold cohorts.
3. Authority recovery by disjoint quorum: floor re-advance, slot replacement, molting.
4. Offline recovery with physical presence: signed technician token plus media (A.9.5).
5. Board swap or device replacement (field debug is disabled, atlas 11.2).
6. Enclave containment with dated exit for devices with no remaining authority path.

### A.4.4 Decision D-A4: failure semantics, fail-closed for authority, fail-operational for control

**DECISION.** `ac_step` may refuse any *authority* request; it never halts, resets or degrades the *control* function: the boot policy picks LKG. Staleness only restricts privileges.
**WHY.** Atlas 5.8 #2: nature optimises populations; a protection relay may not be sacrificed (P30 fail-safe vs fail-secure, R5). Atlas law 8: degrade in steps.
**ALTERNATIVES REJECTED.** Fail-closed on everything (brick on bad update: contradicts safety); fail-open on authority (trivial forgery).
**ASSUMPTIONS.** There is always a last-known-good image that the locked stage can verify with the currently active key set.
**TRADE-OFFS.** A device running LKG with stale authority is knowingly degraded; it reports so.
**LIMITS.** If the safety case demands a different action on authentication failure (fail-safe stop), the integrator sets it in the port's boot hook, and it is outside the core by design.
**HOW WE VALIDATE.** Fault-injection in `ac-sim` (power cuts at every intent boundary, provider faults, NV corruption), property: boot target always defined and never worse than LKG.

---

## A.5 Extension mechanisms

### A.5.1 Registries and where each kind of extension enters

| Extension | Entry point | Touches core? | Touches locked stage? |
|---|---|---|---|
| New signature/KEM/hash algorithm | New `ac-<alg>` library behind W2 + one line in the alg registry + descriptor with mask | No (core sees ID + mask) | No, unless the algorithm is to be an irreversible-quorum member (then stage must contain a verifier: only possible on a new device generation) |
| New protocol (TLS/DTLS/IKE/OPC UA/DNP3-SA/IEC 62351) | L3 `ac-protocols/<name>` consuming policy and `ac-enrol` outputs | No | No |
| New hardware port | Implement W3 tables (and optional hardware W2 providers) in `ports/<vendor>/<part>` | No | Only the port glue in the first stage build |
| New policy rule | Signed policy data in the closed grammar (A.3.10) | No | No (tighten-only) |
| New record field | Append in a minor version, or a negative CBOR key | No | No |
| New action type | New `action` code in `ac_tx` (major or minor?) | **Yes** for core-min if it needs irreversible handling | Yes: therefore actions are designed once (A.3.7 set) and new ones are added only via a major waist version |
| New transport or storage backing | W3 implementation | No | Port glue only |

Registry rules: `alg_id` u16 space: 0x0000-0x00FF core-defined and frozen; 0x0100-0x7FFF public registry (a plain Markdown+CBOR table in the repository, reviewed, never reassigned); 0x8000-0xFFFE vendor/private (never usable in policies applying to more than one vendor without a declaration); 0xFFFF reserved. IDs are never reused (R10: N25 draft-OID lesson [atlas]).

### A.5.2 Stability tiers and deprecation policy over decades

| Tier | Applies to | Promise |
|---|---|---|
| **T0 frozen** | Waist W1-W3 signatures, the fixed records of A.3 (formats v1), `ac_tx`, status codes | Never changes incompatibly. Read-compatibility promised for the life of the project; evolution only by appended minor fields. A major bump is a new waist (`ac_step_v2`) that coexists with v1 for at least one asset life [H: 25 years] |
| **T1 stable** | Provider ABI contract details, L2 formats, core-full services | Semantic versioning; deprecation announced >= 2 major releases / 3 years in advance; removal only from default build, never from the `compat` archive |
| **T2 provisional** | New algorithms (e.g. before final standards), new modules | May change in a minor release; may live at most 3 years provisional before promotion or removal |
| **T3 experimental** | Research code | No promise; excluded from default builds and from conformance claims |

Deprecation process: (1) tier `deprecated` is set in the **algorithm table of a signed policy**, not only in code; (2) a policy flag `warn_epoch` and `deny_epoch` give a coarse, month-granularity schedule; (3) `ac-compat-vN` packages keep read/verify paths for retired formats so old archives, vouchers and evidence stay verifiable (RFC 4998-style renewal for evidence, atlas 11.7); (4) *exercise requirement*: every T1/T2 extension point must be exercised in CI at least once per release and every slot class at least once a year in the field (slot drills; atlas I-13, R10).

### A.5.3 Decision D-A5: closed core, open registries

**DECISION.** The core cannot be extended in the field; the system is extended around it, by registries, tables and data.
**WHY.** Atlas laws 12 and 11 (restrain defenders), R10 (agility atrophy: unused agility rots, so make the agility paths ones that are exercised constantly, i.e. data and providers). Every plug-in point inside the TCB multiplies attack surface (A2/A5 loss in the matrix).
**ALTERNATIVES REJECTED.** (a) Plug-in modules with dynamic loading into the core (matrix A5): TCB growth; (b) Scripting for policy (A2): unbounded; (c) No extensibility at all: R1 re-created.
**ASSUMPTIONS.** Most future change is new algorithms, new protocols, new ports and tighter policy, not new authority actions (atlas 18 ideas and 11 lists a stable set).
**TRADE-OFFS.** Adding a new authority action is expensive on purpose.
**LIMITS.** Cannot add a new irreversible-quorum algorithm to already-shipped locked stages: three slots give "one generation of headroom, not infinite agility" (atlas 11.1).
**HOW WE VALIDATE.** "Extension drill" in CI: add a toy algorithm (e.g. a test-only hash-based scheme) purely through registry + provider, run the full conformance suite, and verify the core object is byte-identical before and after (reproducible build hash check).

---

## A.6 Configuration model

### A.6.1 Two tiers: build profile and signed policy

| Tier | Form | Changes when | Authority |
|---|---|---|---|
| **Build profile** (`profile.cddl` -> `profile.cbor`) | Declarative file selecting modules, algorithm set, class, storage backings, budgets; compiled into the image and reflected in the report | Each firmware build | Developer, reviewed; **checked by `ac-profilelint`** |
| **Signed policy** (A.3.10) | CBOR, signed under quorum | In the field | Authority quorum; tighten-only against the compiled minimum |

There is no third tier of free-form configuration. The linter checks: slot set single-assumption-safe **and live** (A.1.7), verification locality (A.1.5), counter budgets (A.3.1), no stateful key without HSM index custody, PAM rule enabled, debug-disable after commissioning, class dominance and diversification invariants (atlas 12.2), no C0/C1 holding authority.

### A.6.2 Device-class presets (atlas 12)

| Class | Required modules | Optional | Forbidden | Storage/crypto budget (design target, [E]) |
|---|---|---|---|---|
| **C0** inert | none (inventory entry only) | `ac-cbom` record on gateway | any authority | none |
| **C1** symmetric-only | `ac-hmac`, `ac-codec`; `ac-enrol` (KEM or physical) if updatable | hash-verified update (`ac-lms` verify) | signing; shared fleet key (diversified key mandatory) | RAM <= 4 KB, flash for verify <= 16 KB when updatable |
| **C2** verify-capable | `core-min`+`core-full`, `ac-lms`, `ac-sha2`, `ac-report`, `ac-stage` | `ac-slhdsa`, `ac-mldsa`, `ac-timewin`, `ac-debugauth` | field debug; holding signing keys | locked stage 16 KB (MV-1) or 32 KB (HA-1) |
| **C3** safety-critical | C2 + crypto partition, LKG, quorum-signed settings | hardware SHA | public-key operations in control loop; adaptive behaviour | as C2 + partition overhead |
| **C4** concentrators | full PQ protocol stacks, TPM v1.85 identity, dual-vendor | KDC, update server | single point of fleet trust | host-class |
| **C5** authorities | `ac-ceremony`, HSM drivers, `ac-voucher`, transparency log client | | single-class signing | HSM-class |

Class is a field of `ac_authority` and of the profile; the *promotion rule* (class changes only by replacement or quorum-signed re-commissioning) is enforced by the `LIFECYCLE` action requiring a quorum.

### A.6.3 Decision D-A6: declarative, signed, tighten-only configuration

**DECISION.** Two tiers (compiled profile, signed policy), declarative CDDL schemas, a linter that fails CI.
**WHY.** R7 (invisible state: configuration is what the device reports), R9 (side doors often arise from implicit config), atlas law 11. Declarative form allows formal checking (atlas I-4: automatable hitting-set check).
**ALTERNATIVES REJECTED.** Kconfig-only (not signed, not field-changeable); a configuration language with logic (A2); per-device manual configuration (does not scale to 25-year fleets).
**ASSUMPTIONS.** Operators will not write policy by hand; `ac-policyc` compiles from a small human-readable source.
**TRADE-OFFS.** Rigid grammar: some exotic operator wishes require a new T1 minor release.
**LIMITS.** The linter proves properties of the declared policy, not of the real world (a wrong assumption mask is not detectable by the tool).
**HOW WE VALIDATE.** Mutation testing of the linter (seed unsafe policies: shared-assumption quorum, missing slot 3, loosening rule, counter underflow) and expect rejection of each; adversarial review of the assumption-mask registry by cryptographers (atlas 10.3 caveat: SHA-2/SHA-3 independence is a judgement).

---

## A.7 Repository, build and language strategy

### A.7.1 Monorepo layout

```
/spec/                 normative: records (CDDL + byte tables), state machine (TLA+), registries, test vectors
/core/                 ac-core (C11 freestanding) + rust twin (ac-core-rs) + ACSL/Kani proofs
/providers/            one dir per algorithm library (ac-sha2, ac-keccak, ac-lms, ac-slhdsa, ac-mldsa, ac-mlkem, ac-hmac ...)
/codec/                ac-codec (generated from /spec), ac-cbor-det, ac-cose, ac-suit-glue, ac-journal
/modules/              ac-stage, ac-report, ac-enrol, ac-timewin, ac-debugauth, ac-lifecycle, ac-gdoi
/protocols/            consumers: tls-dtls, ikev2, opcua, dnp3sa, iec62351, lorawan ...
/ports/                per-vendor/part: nrf, stm32, nxp, esp32, riscv, linux, hsm-sim ...  (W3 + hw providers)
/tools/                ac-policyc, ac-bundle, ac-quorumlint, ac-profilelint, ac-fleetverify, ac-voucher, ac-escrow, ac-ceremony, ac-cbom, ac-sim, depcheck
/conformance/          cross-implementation vectors, differential harnesses, fault-injection scenarios
/profiles/             class presets C0-C5 + reference product profiles
/docs/                 decisions (ADRs), threat models, assurance case skeletons
/third_party/          vendored, hash-pinned, minimal (reference crypto implementations only)
```
**Governance rule**: `/spec` is the source of truth; code is generated or tested against it; a divergence is a bug in code unless the spec is amended by an ADR.

### A.7.2 Build system and dependency management

| Aspect | Choice | Reason |
|---|---|---|
| C/embedded | **CMake** with toolchain files and presets; exported packages; no Bazel | Dominant in vendor SDKs and RTOSes such as Zephyr [I]; adopters can `add_subdirectory` the library in their own build |
| Rust | **Cargo workspace** (`no_std` crates + host std crates), `cargo vendor` offline | Native; Rust crates are twins or host tooling |
| Orchestration | Small POSIX script + CTest; no custom DSL | Must be readable in 2050 [H] |
| Reproducibility | Pinned container image digest; `SOURCE_DATE_EPOCH`; build twice and compare hashes in CI | Evidence (R7); verifiable binaries for certification |
| Dependencies | **Zero third-party dependencies in `core` and `core-min`**; providers vendored in `/third_party` with hash manifests; `cargo deny` and a license check on host crates; SBOM (CycloneDX) per release | Supply-chain limits (atlas 18 side doors; R9) |
| Releases | Signed tags, release signing with the project's own multi-class quorum (dogfooding) | Credibility; exercises the mechanism (R10) |

### A.7.3 Language strategy by layer

| Layer | Language | Why | Constraints |
|---|---|---|---|
| `core-min` / `core` (L0) | **C11 freestanding as the primary shipped artefact, with an independent Rust `no_std` twin** | C compilers exist for every MCU and every qualified toolchain; independent second implementation required by atlas (HA-1: "independent second implementation of the verifier") and gives differential testing | C: MISRA C (current edition at project start) as the coding standard with documented deviations; CERT C rules; no dynamic allocation, no recursion, bounded loops, no function pointers outside const tables; ACSL contracts on `ac_step` for Frama-C/WP [I: tool chosen by suitability, not verified for this code]. Rust twin: `#![no_std]`, `#![forbid(unsafe_code)]`, Kani proofs for bounds and panic-freedom [I] |
| Providers (L1) | C (portable reference), optional Rust `no_std`, optional verified-extraction code where available (e.g. HACL*-style generated C, [I] not verified here) | Cryptography has a rich verified-implementation ecosystem; reuse beats rewrite | Constant-time discipline; known-answer tests at init; no secret-dependent branches in sign/decap paths |
| Codecs (L2) | Generated from `/spec` (CDDL + tables) into C and Rust | One schema, two encoders, drift impossible | Bounded recursion depth, max sizes as constants |
| Modules (L3) | C for device modules; Rust where the platform has a Rust toolchain | Match the platform | Same ABI |
| Tools (L4) | **Rust** (std) | Memory safety for parsers that handle hostile input; strong CLI ecosystem | `forbid(unsafe_code)` except FFI shims |
| Spec / model | TLA+ (state machine), CDDL (formats), Python reference model | Executable specification, independent of both implementations | |

Why not a verified-extraction language for the core now: a Coq/F*/Dafny-to-C route gives the strongest assurance but ties the project to a niche toolchain for decades and to rare maintainer skills (R10: skill extinction, N61); the chosen path (executable spec + TLA+ + two independent implementations + deductive proof on the small `ac_step`) keeps verified-extraction as a **future refinement** that does not change the T0 interface [H].

### A.7.4 Decision D-A7: monorepo, CMake+Cargo, C core with Rust twin

**DECISION.** As in A.7.1-A.7.3.
**WHY.** Atlas law 12 (doubled core), R10 (skills), R7 (evidence). A monorepo keeps spec, vectors, code and tests atomically consistent for decades; a single repo is also easier to hand over to a foundation (atlas 11.1 "needs a maintainer foundation").
**ALTERNATIVES REJECTED.** (a) Rust-only: excludes many qualified C toolchains and adopter ecosystems, and the first stage on legacy MCUs is C-first today [I]. (b) C-only: loses memory safety for host tooling and the second independent implementation's benefits. (c) Polyrepo: version skew between spec and code. (d) Bazel/Nix as primary: steeper adoption curve and longevity risk.
**ASSUMPTIONS.** Toolchains for C11 remain available for the target lifetime; Rust `no_std` embedded support keeps maturing (Ferrocene exists as a qualified toolchain per its project pages; the exact qualification scope is unverified here).
**TRADE-OFFS.** Doubling the core costs development effort and requires discipline to keep implementations independent (separate authors, separate code review, shared only the spec).
**LIMITS.** Two implementations can share a spec-level mistake; hence the model checking (A.1.5).
**HOW WE VALIDATE.** Differential fuzzing C vs Rust over `ac_step`; coverage targets (MC/DC for core-min as a goal [H]); binary-size budget gate (16 KB MV-1) in CI; reproducible build check.

### A.7.5 Delivery sequence (informed by A.1.4)

1. **M0** spec + vectors + Python reference model + quorum lint (usable without any device code).
2. **M1** the A4 layering: provider table, codecs, `ac-stage`/`ac-report` on top of an existing updater (MCUboot-style hook), so adoption cost is low.
3. **M2** `core-full` + policy + signed reports.
4. **M3** `core-min` in the locked first stage for two reference parts, TLA+ proof, fault-injection campaign (atlas HA-1).
5. **M4** HA-1: second hash waist, dual verification, two-implementation differential.

---

## A.8 Representative API sketches

### A.8.1 Error model and ownership rules

| Rule | Statement |
|---|---|
| Status codes | `int32_t ac_status_t`: 0 = OK, negative = error. Codes are stable T0, never reused. No `errno`, no exceptions, no panics (Rust: `Result`, panic-free proven by Kani target) |
| Totality | Every function returns for every input; invalid input yields a defined error, never undefined behaviour |
| Fail direction | Authority requests fail closed; the caller decides the control-plane fallback (A.4.4) |
| Ownership | Caller owns all buffers; the core borrows for the duration of one call and **retains no pointers**. Output buffers are caller-provided with explicit capacity; short buffers return `AC_E_RANGE` with the required size |
| Context | `ac_ctx_t` is opaque, caller-allocated (`ac_ctx_size()` bytes, aligned to `AC_CTX_ALIGN`); no globals |
| Secrets | The core holds none (public data only). Providers that hold secrets wipe them (`ac_wipe`) on every exit path |
| Concurrency | A context is single-threaded; callers serialise. No hidden threads |
| Side effects | The core performs none. It emits **intents** which the platform executes in order and acknowledges; unacknowledged intents are replayed idempotently by `ac_recover()` |
| ABI versioning | `ac_abi_version()` returns `(major<<16)|minor`; callers check at init |

### A.8.2 C ABI (waist W1, W2, W3)

```c
/* ac_waist.h : T0 frozen. Freestanding: needs only <stdint.h>, <stddef.h>. */
#include <stdint.h>
#include <stddef.h>

#define AC_ABI_MAJOR 1
#define AC_ABI_MINOR 0

typedef int32_t ac_status_t;
enum {
  AC_OK = 0,
  AC_E_FORMAT = -1,      /* malformed bytes */
  AC_E_VERSION = -2,     /* unknown major, or unknown critical field */
  AC_E_SIG = -3,         /* signature invalid */
  AC_E_QUORUM = -4,      /* signer set does not satisfy the (compiled or signed) rule */
  AC_E_FLOOR = -5,       /* would lower or skip the floor, or expect_epoch mismatch */
  AC_E_STATE = -6,       /* action not allowed in current lifecycle */
  AC_E_PROVIDER = -7,    /* algorithm unavailable or self-test failed */
  AC_E_NV = -8,          /* storage error */
  AC_E_BUDGET = -9,      /* counter capacity/margin violated */
  AC_E_PAM = -10,        /* revocation targets live authority */
  AC_E_RANGE = -11,      /* output buffer too small; *needed set */
  AC_E_HOLD = -12,       /* hold-down or objection window open */
  AC_E_UNSUPPORTED = -13
};

/* ---- W2: crypto provider table (const, linked, no runtime registration in locked stage) ---- */
typedef struct {
  uint16_t alg_id;
  uint32_t assumption_mask;
  uint16_t flags;                      /* bit1: verifiable in locked stage */
  ac_status_t (*verify)(const uint8_t *pk, size_t pk_len,
                        const uint8_t *msg, size_t msg_len,
                        const uint8_t *sig, size_t sig_len);   /* OK or AC_E_SIG */
} ac_sig_ops_t;

typedef struct {
  uint8_t hash_alg;                    /* 1 SHA-256, 2 SHAKE256-256 */
  ac_status_t (*digest)(const uint8_t *const *parts, const size_t *lens, size_t n, uint8_t out[32]);
} ac_hash_ops_t;

typedef struct {
  const ac_sig_ops_t  *sig;  size_t n_sig;
  const ac_hash_ops_t *hash; size_t n_hash;
} ac_prim_t;

/* ---- W3: platform table ---- */
typedef struct {
  ac_status_t (*nv_read)(uint32_t region, uint32_t off, uint8_t *buf, size_t len);
  ac_status_t (*nv_append_atomic)(uint32_t region, const uint8_t *rec, size_t len); /* all-or-nothing */
  ac_status_t (*ctr_read)(uint32_t id, uint64_t *v);
  ac_status_t (*ctr_advance_to)(uint32_t id, uint64_t v);   /* MUST never decrease; no decrement entry exists */
  uint64_t    (*ctr_capacity)(uint32_t id);
  ac_status_t (*entropy)(uint8_t *buf, size_t len);
  int64_t     (*clock_hint_epoch)(void);                    /* untrusted hint; may return -1 */
} ac_platform_t;

/* ---- W1: the waist ---- */
typedef struct ac_ctx ac_ctx_t;                  /* opaque */
size_t   ac_ctx_size(void);
uint32_t ac_abi_version(void);

ac_status_t ac_init(ac_ctx_t *ctx, const ac_prim_t *prim, const ac_platform_t *plat);
ac_status_t ac_recover(ac_ctx_t *ctx);           /* idempotent journal replay after reset */

typedef enum { AC_MSG_VERIFY_IMAGE = 1, AC_MSG_PROPOSE_TX = 2, AC_MSG_COMMIT_PENDING = 3,
               AC_MSG_LOAD_POLICY = 4, AC_MSG_QUERY_STATE = 5, AC_MSG_BUILD_REPORT = 6 } ac_msg_kind_t;

typedef struct { ac_msg_kind_t kind; const uint8_t *data; size_t len; } ac_msg_t;

typedef enum { AC_INT_JOURNAL_APPEND = 1, AC_INT_NV_WRITE = 2, AC_INT_COUNTER_BURN = 3,
               AC_INT_SET_BOOT_TARGET = 4, AC_INT_EMIT = 5, AC_INT_REQUEST_RESET = 6 } ac_intent_kind_t;
typedef struct { ac_intent_kind_t kind; uint32_t seq; const uint8_t *data; size_t len; } ac_intent_t;

typedef struct {                                  /* caller-provided, fixed capacity */
  ac_intent_t *items; size_t cap; size_t n;
  uint8_t *scratch; size_t scratch_cap;           /* intents' data point in here */
} ac_effects_t;

/* Pure with respect to everything except ctx: performs no I/O. */
ac_status_t ac_step(ac_ctx_t *ctx, const ac_msg_t *in, ac_effects_t *out, size_t *needed);
ac_status_t ac_ack(ac_ctx_t *ctx, uint32_t seq);  /* platform confirms an intent executed */
```
Compile-time guard in the locked build: only `AC_MSG_VERIFY_IMAGE`, `AC_MSG_COMMIT_PENDING` and `AC_MSG_QUERY_STATE` are compiled in (`core-min`); the rest are `core-full`. A message kind compiled out returns `AC_E_UNSUPPORTED`, not undefined behaviour.

### A.8.3 Rust trait sketch (twin and tooling)

```rust
#![no_std]
pub enum Status { Format, Version, Sig, Quorum, Floor, State, Provider, Nv, Budget, Pam, Range { needed: usize }, Hold, Unsupported }

pub trait Prim {
    fn hash(&self, alg: HashAlg, parts: &[&[u8]], out: &mut [u8; 32]) -> Result<(), Status>;
    fn verify(&self, alg: AlgId, pk: &[u8], msg: &[u8], sig: &[u8]) -> Result<(), Status>;
    fn descriptor(&self, alg: AlgId) -> Option<AlgDesc>;        // mask + flags
}
pub trait NvStore {
    fn read(&self, region: u32, off: u32, buf: &mut [u8]) -> Result<(), Status>;
    fn append_atomic(&mut self, region: u32, rec: &[u8]) -> Result<(), Status>;
}
pub trait MonotonicCounter {
    fn read(&self, id: u32) -> Result<u64, Status>;
    /// Must never decrease; there is deliberately no `set` or `decrement`.
    fn advance_to(&mut self, id: u32, v: u64) -> Result<(), Status>;
    fn capacity(&self, id: u32) -> u64;
}
pub trait Platform: NvStore + MonotonicCounter {
    fn entropy(&mut self, buf: &mut [u8]) -> Result<(), Status>;
    fn clock_hint_epoch(&self) -> Option<i64>;                   // hint only
}
pub trait EffectSink {                                           // caller-implemented
    fn push(&mut self, i: Intent<'_>) -> Result<(), Status>;
}

pub struct Core<P: Prim, H: Platform> { /* fixed-size arrays, no heap */ prim: P, plat: H }
impl<P: Prim, H: Platform> Core<P, H> {
    pub fn step(&mut self, msg: Msg<'_>, fx: &mut impl EffectSink) -> Result<Decision, Status>;
    pub fn recover(&mut self) -> Result<(), Status>;
}
```
Design points: the absence of `set`/`decrement` in `MonotonicCounter` is the Rust expression of "reset is the cancer path" (atlas pattern 18); `Range{needed}` carries the required size so callers never loop-guess; both languages return the same numeric codes through the C ABI shim.

### A.8.4 Decision D-A8: intent-based, byte-message waist

**DECISION.** The waist is `ac_step(msg) -> intents`, with caller-executed, acknowledged intents; no callbacks that perform authority effects.
**WHY.** A pure function with explicit effects is the property that makes deductive proof and model checking tractable and keeps the core free of I/O and OS assumptions (matrix: TCB, certifiability, portability). Byte messages give a language-independent, serialisable ABI that can be frozen for decades (R10) and that can be replayed in the simulator.
**ALTERNATIVES REJECTED.** (a) Rich struct-passing C API: layout/ABI fragility over decades. (b) Callback-heavy API where the core calls into NV and counters directly: effects interleaved with logic, harder to prove power-fail safety. (c) Message-bus/RPC runtime in the TCB: unnecessary.
**ASSUMPTIONS.** Platform can execute intents in order and acknowledge them; if power fails between intents the journal makes replay safe.
**TRADE-OFFS.** Slightly more glue code in every port; one extra round per transition.
**LIMITS.** The waist cannot express streaming/large-object verification: image verification passes digests computed by the caller (the caller hashes the image; the core verifies the signature over the digest and compares). A caller that lies about the digest is the stage-2 case handled by the locked stage's own hashing at boot.
**HOW WE VALIDATE.** Property tests on replay (kill after each intent); model-based testing against the TLA+ model; ABI snapshot tests (`abidiff`-style) in CI refusing any T0 change.

---

## A.9 Sequence diagrams

### A.9.1 First boot and enrolment

```mermaid
sequenceDiagram
  autonumber
  participant CM as Factory/CM + provisioning HSM
  participant D as Device (TEST lifecycle)
  participant L as Locked stage (core-min)
  participant S as Stage 2 (core-full)
  participant K as KDC / gateway (C4)
  participant O as Operator (voucher chain)
  CM->>D: public slot hashes (class A, class B, slot 3), UUID, voucher header (OEM dual-class signed)
  CM->>CM: co-signed provisioning log (CM + OEM)
  D->>L: lock write-protect on first stage; lifecycle TEST -> PROVISIONED (quorum tx pre-signed, A.9.1 note)
  L-->>D: authority record + floor 0 + ledger genesis (dual hash)
  Note over D,K: shipped; field debug disabled at PROD
  D->>L: first power-on: verify stage 2 (class A hash-based)
  L->>S: boot target (stage 2)
  S->>K: ML-KEM-768 enrolment (encapsulate to KDC key, once)
  K-->>S: wrapped per-device KEK (diversified)
  S->>O: signed state report #1 (slots, floor, ledger head, time window)
  O->>S: voucher chain extension, slot-3 owner (A.9.4 for details), lifecycle PROVISIONED -> PROD (quorum tx)
  S->>L: propose ac_tx(LIFECYCLE) ; locked stage verifies and commits at next reset
  L-->>S: reset, commit, report #2 (lifecycle PROD, debug-disabled flag set)
```
Note: the factory has no private keys on the device side; the device only ever receives hashes (Part 8 principle). The lifecycle transition at factory is authorised by a quorum pre-signed by the OEM authority domain, so that the factory cannot unilaterally move a device to PROD.

### A.9.2 Signed update with staging

```mermaid
sequenceDiagram
  autonumber
  participant A as Authority (C5 HSMs, classes A+B)
  participant D as Distribution (C4)
  participant S as Stage 2 (core-full + ac-stage)
  participant L as Locked stage (core-min)
  A->>D: bundle: manifest + SUIT/payload digests + ac_tx + signatures
  D->>S: deliver bytes (any channel, any time)
  S->>S: validate formats, policy, signatures (stage-2 providers incl. ML-DSA), PAM rule
  S->>S: stage payload dormant in inactive A/B slot; record staged[] hash
  Note over S: waits for window: activation requires coarse epoch gate AND maintenance window gate
  S->>L: window event: AC_MSG_PROPOSE_TX / activation request (digest of staged image)
  L->>L: re-verify tx signatures (locked-stage classes), expect_epoch, floor, hold rules
  L->>L: journal append, then counter burn (if floor changes), then set boot target B
  L->>S: boot image B (A retained as LKG)
  S->>D: signed state report (floor, slots, image hash, policy hash, time window)
  D-->>A: reports aggregated; cohort halt condition evaluated; next cohort released
```
Cohorts: the manifest's `staging.cohort` and `persister_ppm` hold a defined fraction on LKG until the field state is proven (atlas 11.5). No global simultaneous activation.

### A.9.3 Floor advance with a disjoint quorum (shedding a class, "molt")

```mermaid
sequenceDiagram
  autonumber
  participant X as Auth class A (LMS-SHA256, SHA-2 waist)
  participant Y as Auth class B (SLH-DSA-SHAKE, Keccak waist)
  participant D as Distribution
  participant S as Stage 2
  participant L as Locked stage
  Note over X,Y: Precondition: new slot provisioned SHADOW earlier (molting step 1-2); annual slot drill passed
  X->>D: sign ac_tx(ADVANCE_FLOOR 7->8, retire slot class-X-old) under slot class A
  Y->>D: sign same ac_tx under slot class B   (retired slot may not co-sign its own retirement)
  D->>S: ac_tx + 2 signatures + manifest
  S->>S: lint locally: masks disjoint (SHA2 vs KECCAK), locus LOCKED for both, expect_epoch matches
  S->>L: propose
  L->>L: verify sig1 with slot A hash-verifier, sig2 with slot B hash-verifier
  L->>L: check disjointness from slot masks; check retired slot != signer set requirement
  L->>L: hold: boots_since_propose >= hold_boots AND second channel confirmation (kinetic hold-down)
  L->>L: journal append, hardware counter burn, update A/B records, ledger_head update
  L-->>S: new epoch, new floor; images below floor refused
  S-->>D: report with ledger head; absence of report within window raises alarm
```
If only one class signs, the request is **anergic**: logged, the key put in boot-only trust until a quorum restores it (atlas pattern 1); nothing irreversible occurs.

### A.9.4 OEM exit and slot-3 replacement

Constraint found while designing (flag): atlas 11.1's `REPLACE_SLOT3` needs "a slot-1 or slot-2 signature", but after an OEM exit slots 1-2 cannot sign. The design below pre-commits OEM authorisation at manufacture (voucher header) and makes the *successor group's own diversity* the safety bound.

```mermaid
sequenceDiagram
  autonumber
  participant OEM as OEM (gone or silent)
  participant E as Escrow agent (witnessed)
  participant W as Witnesses
  participant N as New owner (operator group, two disjoint classes)
  participant S as Stage 2
  participant L as Locked stage
  OEM-->>W: signed quarterly heartbeat (stops)
  W->>E: N missed heartbeats or no fix within M days of a critical CVE (contractual trigger, not a device timer)
  E->>N: release voucher files (header = OEM dual-class, pre-signed at manufacture; chain of owner links)
  N->>N: extend chain: owner(slot3 group) -> new owner; both classes sign link (single-assumption safe inside owner group)
  N->>S: ac_tx(REPLACE_OWNER_GROUP) + voucher chain digest + objection window T_obj
  S->>S: publish proposal to witnesses; collect objections (stop signals)
  Note over S: any signed objection from a conflicting claimant halts the irreversible step; deterministic tie-break after escalation
  S->>L: propose after window; L enforces hold_boots and second-channel confirmation
  L->>L: verify header (OEM dual-class sigs vs slots 1,2 hashes), chain links (current slot-3 group), new group disjoint classes, chain length > slot3_gen
  L->>L: journal, set exit-mode flag, replace slot-3 group hashes, epoch++
  L-->>S: report: exit-mode, new group hashes, ledger head
```
Safety bound ("successor diversity" [I]): after the OEM can no longer sign, the strongest authority this device can have equals the diversity of the successor owner group. With MV-1's three slots (slot 3 single-class) an exit leaves the device exposed to a single-assumption failure of slot 3's class; HA-1 (four or more slots: owner group of two disjoint classes) keeps single-assumption safety. This is a concrete procurement requirement: buy HA-1-capable slot layouts if OEM-exit independence matters. The `chain length > slot3_gen` counter prevents rollback to an earlier owner.

### A.9.5 Offline recovery

```mermaid
sequenceDiagram
  autonumber
  participant T as Technician (present, with signed token + media)
  participant A as Authority (offline, C5)
  participant D as Device (both A/B stage-2 failed, running LKG)
  participant L as Locked stage
  A->>T: media: recovery bundle (stage-2 image, ac_tx for floor/slot if needed) + technician freshness token (signed, coarse epoch)
  T->>D: connect local interface (field debug stays disabled)
  D->>L: boot counter exceeded: locked stage enters recovery mode (no network, no time dependency)
  L->>L: accept only: stage-2 image signed by one active class (boot rule) and, if authority change is needed, a disjoint quorum tx
  L->>L: token narrows time window only (cannot grant authority); presence flag for COUNTER_RESET class actions
  L->>D: install, boot new stage 2, retain LKG
  D-->>T: signed report (ledger head, journal entries, recovery recorded)
  T-->>A: return report; authority audits the ledger entry
```
If the locked stage itself is faulty (FMEA #1), the path ends in board swap; this is why N20 needs the doubled implementation before the first device ships.

### A.9.6 Decision D-A9: reset-time commit with kinetic hold-down

**DECISION.** Irreversible commits happen in the locked stage at reset, after (a) re-verification, (b) a hold of `hold_boots` boots, (c) second-channel confirmation when policy asks, (d) an objection window for ownership actions. Holds count **boots (order)**, not wall-clock time.
**WHY.** Atlas laws 2 and 3 (two independent signals; staged accuracy; reset on doubt), M3 (staged hold-down: forger success `(1-d)^N`), and the time chapter: time may never grant authority, only order and elapsed oscillator bounds exist (atlas 6). Boot counts are available on every device and cannot be set by a time cue.
**ALTERNATIVES REJECTED.** Wall-clock hold timers (attackable and wrong in the cold-cabinet case, 6.2); immediate commit (no proofreading stage); network-attested hold (needs liveness).
**ASSUMPTIONS.** Devices reboot at least occasionally in the planned maintenance windows; a device that never reboots simply never commits (safe).
**TRADE-OFFS.** Slower authority change; emergency changes need a pre-agreed shortened policy hold signed in advance.
**LIMITS.** An attacker who controls reboots of a device and holds a forged quorum still wins that device after the hold; the hold only buys detection time across the fleet.
**HOW WE VALIDATE.** Atlas M3 reproduction with `d` varying; simulation of window alignment (`ac-sim`) with real maintenance calendars; red-team drill on the second-channel step.

---

## A.10 Self red-team

| # | Attack on the chosen design | Honest assessment | Response / residual |
|---|---|---|---|
| 1 | **The hourglass waist is wrong and ossifies.** Frozen T0 interfaces last 30 years; a wrong choice is permanent | Real. The waist is deliberately small and byte-oriented, but action codes and intent kinds will be wrong in places | `ac_step_v2` coexistence, `fmt_major` bumps; run an external design review and implement on three unrelated ports before freezing (T0 only after M3) |
| 2 | **The assumption-mask registry encodes judgements** (SHA-2 vs SHA-3 independence; ML-DSA's real dependence) | Atlas itself notes a cryptographer would discount independence somewhat | Masks are in signed policy/alg tables, so they can be corrected without touching the core; the linter reports sensitivity to merging SHA2/KECCAK atoms |
| 3 | **Verification-locality rule (D-A1) kills the lattice class as an irreversible-quorum member on small parts**, so the program degenerates into hash-only diversity | True for MV-1/HA-1. This limits the benefit of lattice schemes to stage-2 actions | If flash allows an ML-DSA verifier in the locked stage (C2+ large parts), use it. Needs an E-experiment: measure ML-DSA verify footprint in a locked stage on two parts |
| 4 | **The locked stage is not locked** (parts differ; Part 8) | Every claim of "only the locked stage mutates authority" is conditional on the lock | Per-part assessment (Stream on hardware); design limits harm: public hashes only |
| 5 | **Core-min is still a single point of fleet-wide failure** (FMEA 1-2) | True. Doubling reduces independent bug probability only if the implementations are truly independent | Separate authors, clean-room twin, mutation testing, TLA+; honest limit stated in every assurance claim |
| 6 | **Dual encoding doubles parsing risk and tooling** | Real; CBOR parsers are common attack surfaces | CBOR never in the locked stage; generated codecs; bounded decoder with fuzzing; fixed projection `ac_tx` |
| 7 | **Hold-down by boot counts is gameable**: attacker with physical or remote reboot control can run N boots | Yes, it only buys a window for the fleet to detect | Used together with second-channel confirmation and objection window; hold is not a primary security control |
| 8 | **Two-implementation C/Rust doubles cost and may be cut under budget pressure** | Likely in practice | It is a release gate for `core-min` (HA-1), explicitly: no gate, no HA-1 claim; MV-1 may ship with one implementation plus differential fuzz against the Python reference model |
| 9 | **S is more complex than A4; adopters may just take A4 and ignore the core** | Plausible (matrix says A4 wins under migration-cost-first weighting) | M1 delivers A4 layering first; the core is introduced device class by device class |
| 10 | **Atlas 11.1 REPLACE_SLOT3 is infeasible after OEM exit**; the fix introduces owner groups and a "successor diversity" bound | A genuine design change, not just an elaboration | Needs TLA+ treatment and a legal/contract review by the policy stream |
| 11 | **Policy "tighten-only" can brick fleets** (restrictive policy accepted, then no valid quorum is ever possible) | True; this is the fail-closed liveness hazard | Linter liveness check; a policy must carry the previous valid quorum for rollback; staged cohorts |
| 12 | **Time-free design leaves staleness unmanaged** | Time can only restrict; a device offline for 20 years restricts itself without anyone noticing | Reports show window and budgets; operator tooling alerts on silent devices (evidence stream) |
| 13 | **Regulatory/certification friction**: dual-class signatures and hash-based schemes may conflict with some mandates (e.g. CNSA 2.0 requires LMS/XMSS for firmware per atlas; SP 800-230 still draft) | Standards are moving | `alg_table` in signed policy and tier flags allow swapping; keep an LMS profile as the MV-1 default as the atlas recommends |
| 14 | **Scores are one reviewer's judgement** | Yes | Sensitivity table in A.1.4 shows robustness; adopter study as falsifier |

### A.10.1 Open questions for merging agents

1. Locked-stage ML-DSA verifier footprint on two reference parts (decides how often lattice participates in irreversible quorums).
2. TLA+ treatment of the verification-locality rule and of the exit-mode path (A.9.4).
3. HA-1 SLH-DSA-SHAKE verifier size in the locked stage (A.1.6 estimate is unverified).
4. Whether the 16 KB MV-1 budget reconciles with the atlas 13 KB figure (A.1.6).
5. Legal structure for the escrow trigger and heartbeat (hand to the policy/ecosystem stream).
6. Hardware stream: which parts offer a lock strong enough for "only the locked stage mutates authority" and a hardware monotonic backing for the floor shadow.

### A.10.2 Traceability summary (decisions to atlas problems)

| Decision | Primary atlas IDs |
|---|---|
| D-A1 hourglass + core + single-mutator + verification locality | R1, R6, R9, N20, laws 2, 4, 12; 10.3; 11.1 |
| D-A2 layering, classification | R4, R5, laws 4, 12; 12.2 |
| D-A3 dual encoding, versioning | R7, R10, N25, N48; 6.6 |
| D-A4 failure semantics | R5, P30, law 8; 5.8 #2 |
| D-A5 closed core, open registries | R10, N57, N61; laws 11, 12 |
| D-A6 configuration | R7, R9, laws 11; I-4, I-12 |
| D-A7 repo/language | R10, N61, N20; HA-1 second implementation |
| D-A8 intent-based waist | R5, R10; M3 |
| D-A9 reset-time commit, hold-down | R2, R11, R6; laws 2, 3, 9; M3; 6.5 |

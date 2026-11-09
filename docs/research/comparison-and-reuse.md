<!-- Title: Comparison with existing systems; what is reused and what is new -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 11. How this compares

### 11.1 Against existing standards, systems and libraries

| System | What it does well | Where it stops, for this problem | Relationship |
|---|---|---|---|
| **TUF 1.0.37** [F] | Role separation, thresholds per role, chained root rotation, offline root keys, expiry, rollback protection | Threshold-only policies; no assumption classes; no presence; clients trust expiry clocks; no on-client structural lint; recovery is out of band | We reuse its metadata shape fleet-side; our root rotation is a governed transition with interval admission |
| **Uptane 2.1.0** [F] | Director + Image repositories (an AND of two roles); release counters; ECU reports | A fixed two-repository AND, not a general policy; no class counting; no constitutional tier | Composable: an Uptane fleet could carry our `ac_tx` for authority changes |
| **SUIT, MCUboot, wolfBoot, vendor boot stages** | Compact manifests; A/B images; anti-rollback; hardware integration | Authority semantics left to integrators; single signer or fixed key sets | SUIT manifests ride inside bundles; MCUboot-style layering is the adoption path (§5.2) |
| **DICE, Caliptra, OpenTitan, secure elements** | Hardware identity, measurement, isolated keys; PQ roadmaps (Caliptra 2.0 ML-DSA via Adams Bridge; LMS on roadmap [F, deck]) | Vendor-anchored authority; multi-party custody and exits out of scope | Platform providers; their attestation becomes evidence in reports |
| **TPM 2.0 (Library v1.85, PPI)** | Physical-presence concept for owner operations (TCG PPI [F]); ML-DSA/ML-KEM per a vendor note [S] | Presence is a one-off owner gesture, not part of an analysed policy | Our PRES atom generalises the idea and puts it in the fault model |
| **FDO** | Late-binding onboarding, ownership vouchers | One-time onboarding; vouchers are bearer-like if misused | Vouchers kept as off-device evidence for CLAIM |
| **SCITT (RFC 9943), CT (RFC 9162), Sigsum, C2SP witnesses** | Append-only logs, receipts, witness cosigning | Publicity, not authorisation; consistency checkpoints optional in SCITT | WIT atom; we require checkpoints and cosignatures |
| **Threshold hash-based signing** (Kelsey–Lang–Lucks, CiC 2(2), 2025 [F]; PRAWNS and FHE-based ePrints, 2026) | One ordinary signature from many parties; verifier unchanged | Trusted dealer or GiB-scale state; no DKG in PRAWNS; unaudited | A possible inside-the-atom custody mechanism later (X-01); no device change needed |
| **Smart-contract timelocks and social-recovery wallets** | Delay with cancel; guardian recovery | Need global consensus and fees; assume online participants | Our T0/T1 halt-and-resume and T2 recovery are the device-scale analogue |
| **Macaroons, object capabilities** | Attenuation: authority only narrows when delegated | Single issuer root; no assumption classes | Tighten-only tables are attenuation; widening needs the constitution tier |

### 11.2 Against the strongest alternative architecture

The strongest incumbent alternative is **TUF/Uptane-style metadata plus a DICE- or Caliptra-class hardware root, with a vendor-run update service**. Coverage of the governed-change set (✓ covered, ◐ partial, ✗ not covered):

| Problem group | Incumbent stack | This design |
|---|---|---|
| G1–G2 classes and families | ◐ algorithm swap per release; no class counting | ✓ labels, admission, renewal |
| G3–G4 key and custodian compromise | ✓ thresholds per role | ✓ plus class-aware groups |
| G5, G7 custodian loss, vendor exit | ✗ vendor root is permanent | ✓ loss budgets, sovereign exit, recovery tier |
| G6 ownership | ◐ via FDO or vendor | ✓ |
| G8 authorised-but-harmful | ✗ | ◐ envelope tier, echo, halt |
| G9 covert change | ◐ if transparency is added server-side | ✓ device-verified publicity |
| G10–G11 stale devices, rollback | ◐ root chain walking; expiry needs clocks | ✓ chain + fresh receipt; time only restricts |
| G12 NV hazards | ◐ vendor-specific | ✓ contract + part profiles |
| G13–G14 bricking, toolchain | ✗ | ✓ on-device interval admission |
| G16 side doors | ✗ separate mechanisms | ✓ one admission rule |
| G22 end of life | ✗ | ✓ |

The incumbent wins on maturity, tooling, ecosystem and adoption cost today. That is why our delivery plan rides on its formats and bootloaders rather than replacing them (§5.2, EXP-20).

### 11.3 Invention directions considered for each major problem

| Problem | Conservative | Transformative | Radical | Selected |
|---|---|---|---|---|
| Immutable root versus 40 years of change | One LMS verifier + floor | Dual hash families + presence class + interval admission | Universal STARK or bytecode verifier | **Transformative**; radical stays research (X-02) |
| Custody and vendor death | Escrowed OEM keys | Three groups + sovereign exit + recovery tier | Threshold HBS / MPC custody | **Transformative**; radical inside atoms later (X-01) |
| Policy correctness | Host-tool lint and review | **On-device interval admission** | Proof-carrying policies verified on device | **Transformative** (the radical form adds nothing once admission is exact) |
| Equivocation and forks | Gateway-held receipts | Device-verified witnessed receipts | Device-verified verifiable maps; device gossip | **Transformative**; maps are research (X-14); gossip rejected (J-20) |
| Stale devices | Re-provision on site | Fresh receipt + RTC window + presence | Distributed roughtime + verifiable-delay functions | **Transformative**; radical research |
| Hash-family break | Accept the residual (nano) | Two families + presence | A third cryptographic class (Ascon- or AES-based hash signatures) | **Transformative**; radical conditional for remote fleets (C-16) |
| Delay without trusted time | Device tick counts | Witness-checkpoint time + optional RTC | VDF-based delays | **Transformative** |
| Safety interference | Software partition | Zero-crypto safety core | External hold-in-reset supervisor | **Transformative**; supervisor conditional (C-04) |
| Brownfield | Zone gateways | Sectored gateways as governed devices | Port-level enforcers; RAM patching | **Transformative**; enforcer conditional (C-05); RAM patching rejected for safety devices |
| Configuration intent | Workstation quorum | Device echo | Hardware diff token with independent parsers | **Transformative**; token research (X-03) |
| Evidence without device keys | Gateway MAC | Device-scoped LM-OTS with off-device leaves | Zero-knowledge posture proofs | Conservative baseline + **transformative conditional** (C-02); ZK research (X-10) |
| Recovery after two custodian losses | Contracts and courts | Presence-gated recovery tier, public and delayed | Guardian networks with timelocks on a public ledger | **Transformative** |

---


## 12. What is reused, composed, new and uncertain

| Category | Items |
|---|---|
| **Reused, established** [F/S] | SUIT, TUF-shaped metadata, COSE, SCITT (RFC 9943), RFC 9162 audit paths, C2SP checkpoints/cosignatures/witness protocol, EAT, CoRIM, FDO, CycloneDX CBOM, RFC 4998, LMS/HSS, XMSS, SLH-DSA, ML-DSA, ML-KEM (mlkem-native, mldsa-native), TLA+/TLC, CBMC, Frama-C, Kani; black-channel safety pattern; bump-in-the-wire retrofits |
| **Composed from known parts** [I] | Custody-group rule with sovereign exit and claim; hash-based locked stage with key-hash atoms (vendor prior art exists; Caliptra key-manifest overlap unconfirmed); monotone floor and epoch with a replayable chain (TUF root chain is the nearest); staged activation with a scoped halt (timelock-with-cancel pattern); device-scoped one-time reporting keys with off-device leaves; NV contract with a torn-read field |
| **Plausibly new** [N] | (1) On-device admission of monotone policies by interval membership, with bounds derived on the device from labels that mix parties, assumptions, places and publicity. (2) The diversity-budget method: per-power (t, s) budgets, with the weakest full-control path as the security level. (3) Physical presence as a first-class class in the fault model, restoring safety and liveness under a hash-family loss. (4) Publicity modelled as an exposure atom. (5) The impossibility catalogue for device governance. *Not patent-searched; limited literature searches only.* |
| **Mathematics** | Classical: access and adversary structures, the Q² condition, threshold bounds, minimal cut sets. Theorems 1–3 are short derivations, presented as applications, not breakthroughs |
| **Uncertain** [X] | SHA-2 versus Keccak independence; presence spoofing at scale; label truthfulness; witness institutions over 40 years; real-silicon cost; assessor acceptance; adoption effort |
| **Claims withdrawn after review** | "Default dual rule is single-fault tolerant" (liveness half false); "multi-party hash-based signing is research only" (out of date); "TUF's online-key model blocks offline roots" (imprecise: TUF assumes offline roots); κ presented as a new result (it is a cut-set application); "one OEM signature suffices for boot" (reversed by D-27) |

---


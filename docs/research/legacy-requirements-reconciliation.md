# Legacy requirements reconciliation (next-work item 4)

**Machine-generated** by `scripts/reconcile_legacy_requirements.py` -- a mechanical keyword-overlap first pass over all 221 `FR-`/`NFR-` rows in `research-archive/streams/R_requirements.md` against the 23 current `REQ-` rows in `docs/specifications/requirements.md`. This classifies, it does not verify: a LIKELY-COVERED match is a keyword-overlap score, not a confirmed semantic match, and every GAP-CANDIDATE still needs a human decision (new REQ-/ADR, explicit waiver, or recognise it as already out of scope for a reason this script's prefix table doesn't know about). Re-run after any change to either source file.

**Totals:** 221 legacy requirements -- 11 likely covered, 62 out of scope by area, 148 gap candidates needing triage.

## Likely covered (keyword overlap >= 3 with a current REQ-)

| Legacy ID | Priority | Milestone | Best REQ- match | Overlap score | Legacy text |
|---|---|---|---|---|---|
| FR-ASR-06 | MUST | M0 | REQ-CLAIM-01 | 3 | A claims register SHALL record every security and performance claim with an evidence label and test link. |
| FR-AUT-04 | SHOULD | M1 | REQ-CHAIN-01 | 3 | The policy compiler SHALL report, for each accepted policy, honest-availability under declared per-holder availability and SHALL flag any qu... |
| FR-AUT-06 | MUST | M1 | REQ-LIFE-02 | 3 | The floor-advance rule SHALL require a valid signature from a slot different from the slot being retired, plus satisfaction of FR-AUT-03's c... |
| FR-AUT-09 | MUST | M2 | REQ-CHAIN-01 | 3 | Every algorithm-class transition SHALL execute as the molting state machine (provision alongside, shadow-sign, hide, shed under disjoint quo... |
| FR-AUT-11 | SHOULD | M2 | REQ-EVD-02 | 3 | Each authority key SHALL carry a declared scope (action types, device set) and rate limit enforced by the verifier or policy evaluator; scop... |
| FR-FS-12 | MUST | M4 | REQ-IMG-01 | 3 | In HA-1 the first stage SHALL evaluate the compiled disjoint-quorum policy (committed by hash in the locked stage) on every ADVANCE_FLOOR, R... |
| FR-FS-13 | MUST | M2 | REQ-LIFE-02 | 3 | REPLACE_SLOT3(owner) SHALL require the ownership voucher chain plus a signature from slot 1 or slot 2 under the floor rule, and SHALL be una... |
| FR-FS-15 | SHOULD | M1 | REQ-CHAIN-01 | 3 | The first stage SHALL select the LMS parameter profile by capability: W4 where no hash engine is present, W8 where a hardware SHA engine is ... |
| FR-LC-02 | MUST | M2 | REQ-CHAIN-01 | 3 | A per-part hardware evidence register SHALL record independent certification scheme/level/scope, protection across lifecycle states, documen... |
| FR-LC-13 | SHOULD | M3 | REQ-IMG-01 | 3 | Spare devices SHALL be able to ship with only the first stage and slot hashes and SHALL accept application image and ownership only at insta... |
| FR-LC-16 | MUST | M2 | REQ-PRES-01 | 3 | A site-local physical-presence token SHALL be defined as an authority input subject to FR-AUT-05 itself (a token alone SHALL NOT grant any a... |

## Out of scope today, by area (kernel-only scope per README/roadmap)

| Legacy ID | Priority | Milestone | Why out of scope | Legacy text |
|---|---|---|---|---|
| FR-ENC-01 | MUST | M3 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | The library SHALL provide an enclave gateway profile (PQ-terminating boundary, passive inventory, signed configuration) for C0/C1 devices. |
| FR-ENC-02 | MUST | M3 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | Every legacy exception SHALL carry an owner-signed exit epoch; the gateway SHALL surface alarms as it approaches and SHALL require quorum re... |
| FR-ENC-03 | SHOULD | M4 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | Enclaves SHALL be sectorable, with independent boundary keys per sector so that one boundary failure exposes one sector. |
| FR-ENC-04 | SHOULD | M4 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | The gateway profile SHALL support dual-vendor deployment with interop tests. |
| FR-ENC-05 | MUST | M3 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | Gateway configuration SHALL be signed under FR-SIG-06 and gateway logs SHALL be witnessed. |
| FR-ENC-06 | MAY | M5 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | The library MAY ingest design-derived physical invariants as a second signal for commands and reports inside enclaves. |
| FR-ENC-07 | MUST | M3 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | The boundary rule SHALL be machine-checkable: every C0/C1 device SHALL be inside a zone whose boundary is C4, crossing via PQ-protected chan... |
| FR-ENC-08 | MUST | M3 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | Operating modes for jurisdictional constraints on remote operation SHALL be configurable and auditable. |
| FR-ENC-09 | SHOULD | M3 | enclave profile / HA-1 variant -- a port profile, not the kernel itself | The inventory SHALL carry a dated replacement plan with budget line per enclosed device. |
| FR-GOV-01 | MUST | M0 | governance institution process (custody groups, escrow contracts) -- organisational, not a device/kernel requirement | Wire and storage formats SHALL be versioned, self-describing, forward-compatible for non-critical fields and reject unknown critical fields. |
| FR-GOV-02 | MUST | M0 | governance institution process (custody groups, escrow contracts) -- organisational, not a device/kernel requirement | Format identifiers and registry entries SHALL never be reused or silently redefined. |
| FR-GOV-03 | MUST | M2 | governance institution process (custody groups, escrow contracts) -- organisational, not a device/kernel requirement | Specifications SHALL be archived in plain text with multiple independent encodings and reference implementations. |
| FR-GOV-04 | SHOULD | M0 | governance institution process (custody groups, escrow contracts) -- organisational, not a device/kernel requirement | The project SHALL be under an open licence with patent grant and maintainer governance that survives any single organisation. |
| FR-GOV-05 | SHOULD | M1 | governance institution process (custody groups, escrow contracts) -- organisational, not a device/kernel requirement | Every module SHALL declare which requirement IDs it implements. |
| FR-MIG-01 | MUST | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | The inventory model SHALL assign each device a class C0-C5 and record authority holdings per chain. |
| FR-MIG-02 | MUST | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | The tooling SHALL build a trust graph from inventory and passive observation. |
| FR-MIG-03 | MUST | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | The ordering engine SHALL compute migration order by class (C5 first), hubs first, blast-radius per step, and the acquaintance rule when inv... |
| FR-MIG-04 | MUST | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | The planner SHALL refuse to label a migration complete unless all six authority chains are classified and the residual classical channels ar... |
| FR-MIG-05 | SHOULD | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | The planner SHALL compute what a replacement budget buys in exposure-years. |
| FR-MIG-06 | MUST | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | The tooling SHALL report the unrescuable set (classical-only immutable verifier, no lockable stage, no presence access). |
| FR-MIG-07 | SHOULD | M3 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | A procurement-profile generator SHALL emit clauses (hash engine, three or more slots over two or more classes, PQ debug and vouchers, no fie... |
| FR-MIG-08 | MUST | M0 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | Migration experiments (models M1-M7) SHALL be reproducible from the repository with fixed seeds and published parameters. |
| FR-MIG-09 | SHOULD | M4 | cross-algorithm migration ceremonies -- Phase 2/4, not the kernel | Existing fleets SHALL be transitionable via the molting orchestration without requiring device replacement where class permits. |
| FR-OWN-01 | MUST | M2 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | The library SHALL support an FDO-compatible ownership voucher profile signed with ML-DSA or SLH-DSA (dual-class optional), including size ha... |
| FR-OWN-02 | MUST | M2 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | Voucher escrow SHALL archive voucher files together with a reference verifier, format specification and signing-algorithm identifiers suffic... |
| FR-OWN-03 | SHOULD | M3 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | The library SHALL define an OEM heartbeat artefact (PQ-signed liveness statement), a publisher, a verifier and an absence-evidence record fo... |
| FR-OWN-04 | MUST | M3 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | Escrow-trigger evaluation SHALL be an off-device, witnessed, contract-parameterised process (missed heartbeats, unfixed critical CVE window)... |
| FR-OWN-05 | MUST | M2 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | Supersedure SHALL be supported as an OEM-signed hand-over of authority to slot 3, executable while the OEM exists and before CRA-support end... |
| FR-OWN-06 | SHOULD | M3 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | A 'swarm' voucher operation SHALL transfer authority over a named sub-fleet (facility sale/split) with witnessed transfer log. |
| FR-OWN-07 | SHOULD | M3 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | An authority-holdings report SHALL enumerate, per facility or sub-fleet, signing keys, vouchers, debug credentials, remote portals and works... |
| FR-OWN-08 | MUST | M2 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | Ownership transfer messages (OpenTitan-style) SHALL be signed with PQ or dual-class signatures. |
| FR-OWN-09 | MUST | M3 | ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement | Fleet inventory SHALL flag every device lacking a provisioned slot 3 ('queenless') and produce the replacement-or-enclave cost report. |
| FR-PRO-01 | MUST | M3 | provisioning/enrolment mechanics -- Phase 2 (ac-enrol), not the kernel | TLS 1.3 hybrid profile (X25519MLKEM768) SHALL handle ClientHellos exceeding one MTU and be tested through representative OT firewalls. |
| FR-PRO-02 | MUST | M3 | provisioning/enrolment mechanics -- Phase 2 (ac-enrol), not the kernel | IKEv2 profile SHALL place PQ key exchange in IKE_INTERMEDIATE with multiple key exchanges per the published RFCs. |
| FR-PRO-03 | SHOULD | M4 | provisioning/enrolment mechanics -- Phase 2 (ac-enrol), not the kernel | The OPC UA profile SHALL document the application-layer fallback pending a standard PQ policy, SHALL flag non-secure modes, and SHALL track ... |
| FR-PRO-04 | MUST | M3 | provisioning/enrolment mechanics -- Phase 2 (ac-enrol), not the kernel | DNP3-SA, SecOC, LoRaWAN, GOOSE/SV profiles SHALL cover only key delivery and rekey, leaving data-path formats unchanged. |
| FR-PRO-05 | SHOULD | M4 | provisioning/enrolment mechanics -- Phase 2 (ac-enrol), not the kernel | The project SHOULD contribute PQ profiles (GDOI-PQ, FDO-PQ) to the relevant standards bodies. |
| FR-UPD-01 | MUST | M2 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | The transition-bundle format SHALL be signed, self-describing, stageable dormant, and verifiable offline. |
| FR-UPD-02 | MUST | M2 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | Devices SHALL stage verified bundles in the inactive A/B slot without activation, and activation SHALL require the conditions declared in th... |
| FR-UPD-03 | SHOULD | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | Activation SHALL require a site-local presence token and an authority signature (two-key activation), SHOULD randomise activation offset ins... |
| FR-UPD-04 | MUST | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | After each activation the device SHALL emit a signed state report per FR-EVD-01 within a declared time bound after activation. |
| FR-UPD-05 | MUST | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | A crypto-only update lane SHALL separate the cryptographic component into an independently updatable module with stable interface, so crypto... |
| FR-UPD-06 | MUST | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | The orchestrator SHALL stage activation by site, class and cohort, SHALL halt automatically on adverse signals (failed state reports, error-... |
| FR-UPD-07 | SHOULD | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | During emergency rollouts the orchestrator SHALL hold a configurable persister fraction on LKG until the new state is verified and SHALL app... |
| FR-UPD-08 | MUST | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | The orchestrator SHALL gate every irreversible fleet step (classical sunset, class retirement) on readiness of all dependent participants, w... |
| FR-UPD-09 | MUST | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | After every irreversible step the orchestrator SHALL maintain a straggler registry with per-device routing to enclave or visit. |
| FR-UPD-10 | SHOULD | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | A window-calendar model SHALL represent planned and emergency windows per site and map bundles to windows, with two-process gating (accumula... |
| FR-UPD-11 | SHOULD | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | The tooling SHALL provide a read-only adoption measurement mode producing anonymised update-adoption and downtime metrics. |
| FR-UPD-12 | SHOULD | M4 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | Where no vendor patch exists, the orchestrator SHALL support compensating-control bundles (enclave rules, disabled paths) with owner-signed ... |
| FR-UPD-13 | SHOULD | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | A rehearsal facility SHALL replay a bundle and policy against a modelled or emulated lab replica before activation. |
| FR-UPD-14 | MUST | M1 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | Rollback below the floor SHALL be refused; any signed emergency downgrade SHALL be an authority action with quorum and presence. |
| FR-UPD-15 | MUST | M3 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | A slot-drill framework SHALL verify a release through the alternate class alone at least annually (configurable), report success/failure, an... |
| FR-UPD-16 | SHOULD | M4 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | The tooling SHALL provide full-transition rehearsal packages (not only slot drills) schedulable at an interval such that each engineer parti... |
| FR-UPD-17 | MUST | M1 | OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel | An update SHALL never leave the device without a verified LKG image; a failed activation SHALL revert automatically. |
| NFR-CERT-01 | MUST | M4 | certification process evidence (FIPS/IEC) -- Phase 3 audit evidence, not the kernel | Code SHALL follow a published coding standard, be static-analysis clean, and carry requirements-to-code-to-test traceability to enable asses... |
| NFR-CERT-02 | MUST | M3 | certification process evidence (FIPS/IEC) -- Phase 3 audit evidence, not the kernel | The cryptographic component SHALL be separable with a stable interface for independent assessment. |
| NFR-CERT-03 | SHOULD | M4 | certification process evidence (FIPS/IEC) -- Phase 3 audit evidence, not the kernel | First-stage control flow SHALL be statically analysable with bounded loops and bounded cyclomatic complexity. |
| NFR-OPS-01 | SHOULD | M3 | fleet operations tooling -- Phase 2/3, not the kernel | Operator-facing outputs SHALL be human-readable and machine-readable with equivalent content. |
| NFR-OPS-02 | SHOULD | M3 | fleet operations tooling -- Phase 2/3, not the kernel | The orchestrator SHOULD scale to at least one million devices per fleet using cohort staging. |
| NFR-PORT-01 | MUST | M1 | port/toolchain portability -- a build-system property, not a kernel behaviour | The device-side core SHALL be portable freestanding C (no OS or libc dependency beyond declared intrinsics) behind a HAL; memory-safe implem... |
| NFR-PORT-02 | MUST | M1 | port/toolchain portability -- a build-system property, not a kernel behaviour | CI SHALL cover Cortex-M0+, M4, M33, RISC-V 32-bit and a host target, with at least two compiler families. |
| NFR-PORT-03 | MUST | M1 | port/toolchain portability -- a build-system property, not a kernel behaviour | The code SHALL be free of undefined behaviour and endian/alignment assumptions, verified by sanitizers and static analysis. |

## Gap candidates (kernel-relevant area, no current REQ- match) -- needs triage

| Legacy ID | Priority | Milestone | Best overlap score (below threshold) | Legacy text |
|---|---|---|---|---|
| FR-ASR-01 | MUST | M1 | 1 | Formal models SHALL live in the repository with CI model-checking on every change. |
| FR-ASR-02 | MUST | M4 | 0 | A neutral conformance suite SHALL test first stages, vouchers, debug credentials and bundles. |
| FR-ASR-03 | MUST | M1 | 0 | A power-loss harness SHALL run at least 100,000 randomised boots/transitions per release. |
| FR-ASR-04 | SHOULD | M4 | 1 | The project SHALL expose fault-injection and side-channel evaluation hooks so independent labs can run campaigns; the project itself SHALL NOT publish attack pr... |
| FR-ASR-05 | MUST | M1 | 2 | Benchmarks SHALL be published with evidence labels, parameter sets and toolchains. |
| FR-ASR-07 | MUST | M4 | 1 | Independent third-party review SHALL precede declaring the first stage stable. |
| FR-ASR-08 | SHOULD | M4 | 1 | The project SHALL supply safety-case artefacts demonstrating crypto confinement (separation, timing envelope, failure modes) reusable by assessors. |
| FR-ASR-09 | MUST | M2 | 2 | WCET analysis SHALL accompany each device-side primitive on supported targets. |
| FR-ASR-10 | MUST | M1 | 0 | All parsers SHALL be bounded and continuously fuzzed. |
| FR-ASR-11 | MUST | M1 | 1 | Supply-chain controls (dependency pinning, toolchain provenance, signed releases) SHALL be implemented. |
| FR-AUT-01 | MUST | M0 | 1 | The policy model SHALL represent every state-changing authority action (floor advance, slot replace, lifecycle transition, ownership transfer, revocation, debug... |
| FR-AUT-02 | MUST | M0 | 1 | The library SHALL ship a signed, versioned, machine-readable assumption table A(k) mapping every algorithm, parameter set, implementation and holding organisati... |
| FR-AUT-03 | MUST | M0 | 2 | A policy compiler SHALL reject any policy in which the simultaneous failure of any single assumption in A(.) lets the forged key set satisfy any accepted quorum... |
| FR-AUT-05 | MUST | M1 | 2 | The authority model SHALL implement graded authority: boot requires one valid class; any authority change requires a disjoint-quorum; re-ownership additionally ... |
| FR-AUT-07 | MUST | M1 | 2 | A revocation or blocklist record whose target set intersects the device's current authority set SHALL be structurally invalid unless it carries the escrow class... |
| FR-AUT-08 | SHOULD | M2 | 2 | Repeated validly signed authority-change attempts lacking the required second class SHALL demote the presenting key to boot-only (anergy), SHALL record the even... |
| FR-AUT-10 | MUST | M2 | 1 | Competing successor claims SHALL be arbitrated by signed objections; no irreversible step SHALL execute while an objection is unresolved; after a bounded, polic... |
| FR-AUT-12 | SHOULD | M2 | 1 | Before a policy is signed, the toolchain SHALL replay a declared corpus of planned legitimate operations (next floor advances, RMA, ownership transfer, spare ac... |
| FR-AUT-13 | MUST | M1 | 1 | Changes to algorithm-agility configuration (enabled suites, minimum groups, pinning mode) SHALL be authority actions under FR-AUT-01 and SHALL NOT be settable b... |
| FR-AUT-14 | MUST | M2 | 2 | Every authority action initiated by automation (including AI configuration assistants) SHALL require at least one human-attributable quorum signature recorded w... |
| FR-AUT-15 | MUST | M2 | 1 | The policy compiler SHALL enforce the class anti-weak-path invariants (dominance, diversification, boundary, authority isolation, promotion) and SHALL reject po... |
| FR-CRY-01 | MUST | M0 | 1 | The algorithm registry SHALL identify every algorithm and parameter set by a stable library-owned numeric identifier with an immutable status history; persisten... |
| FR-CRY-02 | MUST | M0 | 2 | Each registry entry SHALL declare its assumption set (feeding FR-AUT-02), key/signature sizes, statefulness, malleability class, and whether it is approved, dra... |
| FR-CRY-03 | MUST | M1 | 1 | The library SHALL provide verification for LMS (SHA-256 and SHAKE parameter sets), ML-DSA-44/65/87, SLH-DSA (FIPS 205; SP 800-230 sets once final), and decapsul... |
| FR-CRY-04 | MUST | M1 | 2 | Device (verify-only) builds SHALL exclude all signing code at compile time; signing primitives SHALL exist only in the host/HSM build profile. |
| FR-CRY-05 | MUST | M1 | 1 | All secret-handling code paths SHALL be free of secret-dependent branches and memory addressing, and SHALL be tested with a constant-time checker on each suppor... |
| FR-CRY-06 | MUST | M3 | 1 | The CI pipeline SHALL verify constant-time properties at binary level (post-compilation) for every released artefact, not only at source level. |
| FR-CRY-07 | SHOULD | M3 | 1 | Host-side ML-DSA signing SHALL be deployed only inside hardened modules and SHALL randomise or mask rejection-loop timing so iteration count is not observable b... |
| FR-CRY-08 | MUST | M1 | 1 | The API SHALL expose a signature malleability class (EUF-CMA vs SUF-CMA) and SHALL NOT deduplicate or key records by raw signature bytes of EUF-CMA-only composi... |
| FR-CRY-09 | MUST | M1 | 2 | A hash-engine HAL SHALL select hardware SHA-2/SHA-3 where present, fall back to constant-time software, and produce identical outputs verified by KAT. |
| FR-CRY-10 | MUST | M1 | 2 | A benchmark harness SHALL reproduce cycles, stack, RAM and flash per primitive and parameter set on named boards, and every published figure SHALL carry its par... |
| FR-CRY-11 | MUST | M1 | 1 | Every primitive SHALL pass known-answer tests from the published standards' vectors and a differential test against at least one independent implementation. |
| FR-CRY-12 | MUST | M1 | 1 | Per-primitive RAM/stack/flash budgets SHALL be published per target and enforced as CI regression gates. |
| FR-CRY-13 | SHOULD | M3 | 1 | Hybrid-strict policy SHALL be a declarable per-peer-set mode with explicit fallback behaviour, a signed expiry epoch for any fallback exception, and reporting o... |
| FR-CRY-14 | MUST | M2 | 2 | Negotiation SHALL refuse any suite weaker than the policy-declared minimum, and SHALL log attempted downgrades; defaults SHALL NOT silently select a weaker grou... |
| FR-CRY-15 | SHOULD | M3 | 2 | The policy layer SHALL support an operator-declared 'suspected' state for an algorithm or implementation (unconfirmed break), which blocks shedding of other cla... |
| FR-CRY-16 | SHOULD | M4 | 1 | Verifiers SHOULD apply fault-tolerance countermeasures (redundant comparison of the accept decision, checked branch conditions) selectable per part profile. |
| FR-CRY-17 | MUST | M2 | 1 | Enrolment SHALL use ML-KEM decapsulation exactly once per device per key-hierarchy epoch, deriving a per-device KEK through a standard KDF bound to device UUID ... |
| FR-CRY-18 | SHOULD | M2 | 1 | Firmware-encryption key wrapping SHALL use a post-quantum KEM (hybrid permitted); classical-only wrapping of firmware keys SHALL be rejected by policy. |
| FR-CRY-19 | SHOULD | M3 | 1 | Constrained-link profiles SHALL support offline (non-air) key provisioning and fragmentation-aware transports so no large public-key object is required over LoR... |
| FR-EVD-01 | MUST | M2 | 2 | Devices capable of signing SHALL emit a signed state report carrying floor, active slots and classes, image hash, policy hash, lifecycle state, senescence flag,... |
| FR-EVD-02 | MUST | M3 | 0 | Every state report SHALL carry a structured, human-readable delta from the previous report. |
| FR-EVD-03 | MUST | M3 | 1 | The tooling SHALL generate CycloneDX CBOM from state reports, inventories and surface maps, including per-part hardware evidence. |
| FR-EVD-04 | SHOULD | M4 | 0 | Reports SHALL map to TCG/IETF RATS attestation formats where the platform provides them, including TPM 2.0 v1.85 ML-KEM/ML-DSA identity where available. |
| FR-EVD-05 | SHOULD | M4 | 0 | Passive inference parsers SHALL derive crypto state for silent devices from OPC UA, TLS/DTLS, IKE and GDOI observations with a measured accuracy target of at le... |
| FR-EVD-06 | MUST | M3 | 0 | An OPC UA configuration linter SHALL flag AutoAccept and SecurityMode=None. |
| FR-EVD-07 | SHOULD | M4 | 2 | Alerts SHALL key on danger signals (authority-changing events, safety-logic signature changes, out-of-window state changes) rather than novelty. |
| FR-EVD-08 | MUST | M3 | 0 | The tooling SHALL compute exposure-years per the M5 model and report it as the primary programme metric alongside percentage migrated. |
| FR-EVD-09 | SHOULD | M4 | 2 | The tooling SHALL export evidence mapped to named regimes (CRA Art. 14, NIST IR 8547, CNSA 2.0, India CII inventory) with each regime's own 'done' definition st... |
| FR-EVD-10 | MUST | M3 | 2 | Vouchers, receipts, transition logs and state reports SHALL be archived as evidence records with RFC 4998-style timestamp and hash-tree renewal performed before... |
| FR-EVD-11 | SHOULD | M4 | 1 | Fleet slot-set commitment hashes SHALL be publishable to widely witnessed media with verification instructions. |
| FR-EVD-12 | SHOULD | M4 | 1 | Transparency-log and witness components SHALL use post-quantum or dual-class cosignatures from day one. |
| FR-EVD-13 | MUST | M3 | 1 | Monitoring taps SHALL be read-only, SHALL hold no authority keys, and SHALL be enumerated in the surface map. |
| FR-EVD-14 | MUST | M3 | 2 | Evidence archives SHALL include reference verifiers and format specs, versioned and hash-pinned. |
| FR-EVD-15 | MUST | M4 | 0 | Conformance claims SHALL be machine-checkable against the public test suite so owners can verify OEM post-quantum claims. |
| FR-EVD-16 | MAY | M5 | 0 | The tooling MAY export anonymised crypto-state posture for insurer/loss-data use. |
| FR-FS-01 | MUST | M1 | 2 | The first stage SHALL verify the second stage using a hash-based signature scheme: LMS-SHA-256 W4 in the MV-1 profile; SHA-2 and SHA-3 based schemes (LMS-SHA-25... |
| FR-FS-02 | MUST | M1 | 1 | The first stage SHALL hold at least three 32-byte key-hash slots (96 B), spanning at least two disjoint assumption classes in HA-1, with one slot reserved for t... |
| FR-FS-03 | MUST | M1 | 2 | The product SHALL enable the part's flash/boot lock over the first stage before shipment; the first stage SHALL expose a lock-status attestation and SHALL conta... |
| FR-FS-04 | MUST | M1 | 2 | The first stage SHALL store no secret key material; its only persistent cryptographic content SHALL be public-key hashes, policy commitment hashes and counters. |
| FR-FS-05 | MUST | M1 | 1 | The floor SHALL be held in redundant, non-restorable monotonic storage with a write-ahead journal; ADVANCE_FLOOR SHALL commit the journal before burning the flo... |
| FR-FS-06 | MUST | M1 | 2 | Boot failure of image A SHALL fall to image B, then to a last-known-good (LKG) image that keeps the controlled process running; a BRICK_GUARD state SHALL preven... |
| FR-FS-07 | MUST | M1 | 2 | Every state transition (ADVANCE_FLOOR, REPLACE_SLOT, image switch, journal replay) SHALL be atomic with respect to power loss: after a cut at any point the devi... |
| FR-FS-08 | MUST | M1 | 1 | Nothing that can live in the updatable second stage SHALL be placed in the first stage; the first-stage code size SHALL meet NFR-MEM-01. |
| FR-FS-09 | MUST | M4 | 1 | The verifier core SHALL have two independently written implementations (distinct teams and, where practicable, languages) and a differential test that runs on e... |
| FR-FS-10 | MUST | M4 | 2 | The first-stage state machine SHALL be formally modelled (TLA+ or equivalent) with proofs of invariants: no single-class key reaches ADVANCE_FLOOR; a power cut ... |
| FR-FS-11 | MUST | M1 | 2 | The first stage SHALL NOT require wall-clock time, network access or any external service to boot or verify. |
| FR-FS-14 | MUST | M1 | 2 | For parts that cannot lock a maker-defined first stage, the library SHALL provide a documented ANCHOR-WEAK profile, SHALL label such devices in state reports an... |
| FR-FS-16 | SHOULD | M1 | 2 | The first stage SHALL self-check the integrity of its slot store and policy commitment at every boot and SHALL fail safe (LKG, report) on mismatch. |
| FR-FS-17 | SHOULD | M1 | 0 | Revocation storage and anti-rollback storage SHALL be physically and logically separate banks. |
| FR-FS-18 | SHOULD | M1 | 1 | The verifier SHALL use a hash-engine abstraction (FR-CRY-09) and SHALL support hash engines that stream so that image hashing cost is separable from signature v... |
| FR-KEY-01 | MUST | M2 | 1 | Process-bus and field-bus data paths SHALL remain symmetric (existing MAC/AES-GMAC formats); public-key operations SHALL occur only at enrolment and authority c... |
| FR-KEY-02 | MUST | M2 | 2 | The KDC SHALL derive per-device keys by diversification so that no key is shared across devices; the diversification key SHALL reside only in C4/C5 HSMs. |
| FR-KEY-03 | SHOULD | M3 | 1 | The KDC SHALL support replication with t-of-n unlock, HSM-held KEKs and per-zone scoping, with island sites runnable on KDC replicas. |
| FR-KEY-04 | SHOULD | M3 | 2 | Group keys SHALL be distributed per GDOI-style rekey with short epochs and membership bound to per-device identity; a PQ-capable profile SHALL be specified for ... |
| FR-KEY-05 | SHOULD | M3 | 2 | Missed group rekeys SHALL be recoverable using a counter floor without per-device manual intervention. |
| FR-KEY-06 | MUST | M2 | 1 | Safety-function code SHALL interact with cryptography through a narrow, stable interface so that cryptographic components can be replaced without altering safet... |
| FR-KEY-07 | MUST | M2 | 2 | Key derivation SHALL include class, device UUID and epoch in context; keys SHALL be unusable across classes. |
| FR-KEY-08 | SHOULD | M4 | 1 | Fleet evidence SHALL flag devices or accounts holding or having used keys or group memberships beyond their role (camouflage detection). |
| FR-KEY-09 | MAY | M5 | 1 | The library MAY provide ratcheted symmetric authority for disconnected assets (SDLS-style). |
| FR-KEY-10 | MUST | M2 | 2 | The enrolment of class-C1 devices SHALL be possible physically (technician) or via a KEM through a gateway without public-key work on the device beyond a single... |
| FR-LC-01 | MUST | M0 | 1 | The library SHALL define and validate an Authorisation Surface Map schema listing, per part and product, every path able to change code, keys, owner, debug stat... |
| FR-LC-03 | MUST | M2 | 1 | Debug credentials SHALL be PQ-signed and bound to the device UUID (and optionally lifecycle state); a credential valid for one device SHALL fail on every other ... |
| FR-LC-04 | MUST | M2 | 1 | The lifecycle model SHALL define TEST, PROD, RMA and DECOMMISSIONED states; field debug SHALL be disabled on entering PROD commissioning; every transition SHALL... |
| FR-LC-05 | MUST | M2 | 1 | No reverse lifecycle transition (RMA, factory reset, re-provision) SHALL reopen general debug access; the supported repair path SHALL be board replacement with ... |
| FR-LC-06 | SHOULD | M2 | 2 | RMA/lifecycle authorisations SHALL be per-device, SHALL be revocable by floor advance, and SHALL NOT remain valid after the product's declared support-end epoch... |
| FR-LC-07 | MUST | M2 | 1 | Factory provisioning SHALL use KEM-wrapped per-device key injection; no fleet-shared secret SHALL be provisioned; the provisioning log SHALL be co-signed by the... |
| FR-LC-08 | MUST | M2 | 2 | Device identity credentials (IDevID/DICE-style) SHALL be issued with PQ or hash-based signatures, in dual-class form where the verifier population requires it. |
| FR-LC-09 | SHOULD | M3 | 1 | Feature-licence and activation tokens SHALL be PQ-signed and bound per device. |
| FR-LC-10 | MUST | M3 | 1 | Vendor remote-access portals SHALL be modelled as authority paths in the surface map; the library SHALL provide a quorum-gated, out-of-band-confirmed session-au... |
| FR-LC-11 | MUST | M2 | 1 | Decommissioning SHALL produce a signed receipt (UUID, floor, keys destroyed, trust-list removals) that SHALL be logged before the device may be reprovisioned or... |
| FR-LC-12 | MUST | M3 | 2 | Refurbish/re-commission SHALL wipe prior identity, verify first-stage lock and debug-closed state at intake, and issue a fresh identity only under presence evid... |
| FR-LC-14 | MUST | M2 | 2 | A catch-up bundle format SHALL let a device at floor k reach the current floor in bounded bytes, using sequential chain proofs and, optionally, Merkle-committed... |
| FR-LC-15 | MUST | M3 | 1 | Trust lists SHALL support removal on decommissioning receipt, and consumers SHALL reject certificates of decommissioned UUIDs. |
| FR-LC-17 | MAY | M5 | 1 | The library MAY support Merkle-committed future key sets with custody split across organisations in different assumption classes. |
| FR-SIG-01 | MUST | M1 | 1 | Release, voucher and debug-credential signing SHALL occur only in HSM-backed signing services under quorum; the library SHALL provide no code path to sign on co... |
| FR-SIG-02 | MUST | M2 | 2 | A quorum signing coordinator SHALL produce dual-class (shadow-signed) signatures for each release during molting, with members drawn from disjoint assumption cl... |
| FR-SIG-03 | MUST | M1 | 1 | Stateful-key signing SHALL use index reservation with atomic persistence; a one-time index SHALL never be used twice, including across HSM failover, crash recov... |
| FR-SIG-04 | MUST | M1 | 1 | The signing service SHALL track remaining signature budget per key (2^h for LMS; the limit for SP 800-230 sets), warn at configured thresholds (default 50% and ... |
| FR-SIG-05 | SHOULD | M3 | 1 | A documented, attested procedure SHALL exist for moving stateful-key custody between HSM vendors or for re-rooting to a fresh key via FR-AUT-09 when export is u... |
| FR-SIG-06 | MUST | M2 | 0 | Configuration, protection-setting and safety-logic artefacts SHALL be signed by an m-of-n workstation quorum with keys in tokens or TPM; devices that can verify... |
| FR-SIG-07 | SHOULD | M3 | 0 | Signing ceremonies SHALL be scripted, produce a signed ceremony record, and be rehearsable on a non-production key hierarchy. |
| FR-SIG-08 | MUST | M1 | 2 | Signed artefacts (images, bundles, vouchers, policies) SHALL use a self-describing manifest carrying algorithm ids, floor, class tags, epoch validity, and a str... |
| FR-SIG-09 | SHOULD | M4 | 1 | Artefacts SHOULD support offline-verifiable witness cosignatures with at least one post-quantum cosignature class. |
| FR-SIG-10 | MUST | M3 | 1 | Release builds SHALL be reproducible and accompanied by SBOM and CBOM; two independent rebuilds SHALL yield identical hashes. |
| FR-SIG-11 | MUST | M1 | 1 | No single human SHALL be able to release signed artefacts or change signing-policy; all release approvals SHALL be dual-controlled and logged. |
| FR-SIG-12 | MUST | M2 | 0 | Debug-credential issuance keys SHALL be distinct from release and RoT keys and held in a separate quorum. |
| FR-TIM-01 | MUST | M1 | 1 | Device-side authority decisions SHALL use counters and epochs, never calendar time. |
| FR-TIM-02 | MUST | M2 | 2 | Validity SHALL be expressed in coarse epochs of at least one month, sized to the declared oscillator drift bound; each device SHALL record the bound used. |
| FR-TIM-03 | SHOULD | M3 | 2 | A zeitgeber library SHALL ingest independent time cues, label each with what it can prove (not-before, not-after, rate), and fuse them with plausibility windows... |
| FR-TIM-04 | MUST | M1 | 2 | Time SHALL never grant authority; staleness SHALL only reduce privileges and SHALL never halt a safety function. |
| FR-TIM-05 | MUST | M2 | 1 | A defined senescent state SHALL retain control function, refuse authority changes, and be announced in every report. |
| FR-TIM-06 | MUST | M0 | 0 | No persisted format or API SHALL use 32-bit signed time; time and counters SHALL be wrap-safe for the asset life. |
| FR-TIM-07 | MUST | M0 | 1 | A counter-capacity register SHALL list every counter, time field and signature budget with capacity, consumption rate and asset life, and the build SHALL fail i... |
| FR-TIM-08 | MUST | M2 | 1 | Unauthenticated PTP or other unauthenticated time SHALL NOT feed any security policy decision. |
| FR-TIM-09 | SHOULD | M5 | 1 | Grid-cycle or ENF-derived inputs, if used, SHALL be plausibility inputs only and SHALL tolerate deviations of at least several minutes and islanding. |
| FR-TIM-10 | MUST | M2 | 1 | Certificate and credential handling SHALL support 'no well-defined expiry' encodings with issuer duty documented, and SHALL not fail closed on calendar expiry a... |
| FR-TIM-11 | MUST | M2 | 1 | Offline revocation SHALL be achieved through floor/counter advancement and signed bundles carried at visits, not through fetched CRLs. |
| FR-TIM-12 | SHOULD | M3 | 0 | A technician freshness token SHALL provide a signed not-before bound for visits to long-disconnected assets. |
| FR-TIM-13 | MAY | M5 | 1 | The library MAY support SRAM-remanence power-off timers as one labelled zeitgeber input. |
| NFR-API-01 | MUST | M2 | 1 | Public APIs SHALL follow semantic versioning with a minimum deprecation period; first-stage-facing formats SHALL be frozen once released. |
| NFR-API-02 | MUST | M2 | 2 | Storage and wire formats SHALL remain readable by later releases for the declared device lifetime. |
| NFR-DET-01 | MUST | M2 | 1 | Verification and decapsulation execution time SHALL be independent of secret data and have a bounded, analysable WCET. |
| NFR-DET-02 | MUST | M2 | 0 | On C3 devices, cryptographic operations SHALL NOT run in the control loop; ML-DSA signing SHALL be forbidden on C3 given 584 ms p99 against ~100 ms deadlines. |
| NFR-DET-03 | MUST | M3 | 0 | Release artefacts SHALL be bit-reproducible. |
| NFR-DOC-01 | MUST | M0 | 2 | Every document SHALL attach evidence labels per claim. |
| NFR-FLASH-01 | MUST | M1 | 2 | Slot, policy-hash and floor/journal storage SHALL occupy at most two erase sectors plus 96 B of slot data in the MV-1 profile. |
| NFR-FLASH-02 | MUST | M1 | 1 | Flash wear from journal and counters SHALL be computed over the asset life with a 2x margin. |
| NFR-INT-01 | MUST | M2 | 0 | The project SHALL not change IEC 62351-6 or existing field-bus frame formats. |
| NFR-LAT-01 | MUST | M1 | 1 | LMS-SHA-256 W4 signature verification SHALL complete within 60 ms at 64 MHz Cortex-M4 in software, excluding image hashing. |
| NFR-LAT-02 | SHOULD | M2 | 1 | ML-DSA-44 verification SHALL complete within 100 ms on M0+-class parts at the benchmark's declared reference clock (measured 44.0 ms on RP2040 [D]; threshold fr... |
| NFR-LAT-03 | MUST | M2 | 1 | ML-KEM-768 decapsulation SHALL complete within 50 ms on M0+-class parts. |
| NFR-LAT-04 | MUST | M1 | 2 | Boot-time budget SHALL be declared per profile with image-hash time reported separately and scaled by image size. |
| NFR-LAT-05 | MUST | M2 | 1 | No public-key operation SHALL execute within a Sampled Values or GOOSE frame path; per-frame budget is 208-250 us at 4,800-4,000 frames/s. |
| NFR-LAT-06 | SHOULD | M3 | 1 | Group rekey SHALL complete within 1 s per group without disturbing data-path latency. |
| NFR-LIFE-01 | MUST | M0 | 1 | Design life SHALL be at least 40 years: counters at least 2x margin, formats legible for 50 years, algorithm replaceable above the first stage. |
| NFR-LIFE-02 | MUST | M1 | 0 | No verification SHALL depend on a vendor-operated service existing. |
| NFR-LIFE-03 | MUST | M2 | 1 | The second stage SHALL be replaceable in the field with algorithms not known at the first stage's build. |
| NFR-MEM-01 | MUST | M1 | 1 | The MV-1 first stage SHALL fit in 16,384 B of flash (code, constants, verifier) and its static stack SHALL not exceed 2,048 B; both measured per target. |
| NFR-MEM-02 | SHOULD | M2 | 1 | The updatable second stage SHALL publish ML-DSA-44/65 verify RAM per target; target for M33-class is at most 16 KiB RAM pending E-A2 measurement. |
| NFR-MEM-03 | MUST | M2 | 0 | ML-KEM-768 decapsulation SHALL not exceed 16 KiB stack on Cortex-M0+. |
| NFR-MEM-04 | MUST | M1 | 1 | The first stage and verifier SHALL use no dynamic allocation; all buffers SHALL be statically bounded. |
| NFR-OFF-01 | MUST | M1 | 2 | All device-side verification SHALL operate fully offline with no network or time source. |
| NFR-OFF-02 | MUST | M2 | 2 | A device offline for 10 years SHALL accept a valid catch-up bundle within a declared bundle-size bound. |
| NFR-PWR-01 | SHOULD | M3 | 0 | Per-operation energy SHALL be published; C1 battery devices SHALL perform no public-key operations except enrolment. |
| NFR-PWR-02 | MUST | M1 | 0 | Power loss at any instruction SHALL be tolerated (SP-03) with at least 100,000 randomised cut tests per release. |
| NFR-SAFE-01 | MUST | M2 | 1 | A security fault SHALL never inhibit a safety function; every safe-misfire path SHALL fail operational. |
| NFR-SEC-01 | MUST | M1 | 1 | Device-side parsers SHALL reject malformed input without state change and with bounded resource use. |

# STREAM F: Fleet, authority plane, evidence and protocol layers

Scope: everything that is not on the constrained-device boot path. Author role: distributed-systems researcher and OT protocol engineer. Date of verification: 2026-11-06.

Evidence labels follow the brief: [F] primary fact, [2nd], [V], [D], [C] computed here, [E] estimate with arithmetic, [I] inference, [H] invention/hypothesis, [S] speculative. Items marked "(not re-fetched)" are standards facts I hold from prior knowledge and did not re-verify this session; treat them as [I] until checked. Atlas IDs (R#, N#, I-#, M#, C0-C5) are used for traceability.

Verified this session (fetched or seen in search results):

| Fact | Source seen this session | Label |
|---|---|---|
| SCITT architecture is RFC 9943, Proposed Standard, published 30 June 2026 | https://www.rfc-editor.org/rfc/rfc9943 | [F] |
| ML-DSA for JOSE/COSE is RFC 9964 (May 2026) | https://mirrors.ircam.fr/pub/rfc/rfc9964.json | [F] |
| Rekor v2 GA 10 Oct 2025, tile-backed on Tessera; witnessing "planned, not yet live" at that post; timestamps moved to a separate TSA | https://blog.sigstore.dev/rekor-v2-ga/ | [F] |
| C2SP tlog-witness: witnesses cosign checkpoints after verifying an RFC 6962 consistency proof (`add-checkpoint`) | https://github.com/C2SP/C2SP/blob/main/tlog-witness.md | [F] |
| draft-ietf-suit-manifest-38 (4 Nov 2026) is in the RFC Editor queue, no RFC number yet | https://datatracker.ietf.org/doc/draft-ietf-suit-manifest/ | [F] |
| CoRIM: draft-ietf-rats-corim-12 (1 Nov 2026), in WG Last Call, not an RFC | https://datatracker.ietf.org/doc/draft-ietf-rats-corim/ | [F] |
| EAT is RFC 9711 (April 2025) | search result titles at rfc-editor.org/rfc/rfc9711 | [F] |
| FDO PS v2.0 (2 Apr 2026): PQ-safe crypto "highly recommended" but "not mandated"; visible suites are ECDH/ECDSA/RSA | https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-PS-v2.0-20260402/FIDO-Device-Onboard-PS-v2.0-20260402.pdf (first 100k of 110k characters read; Appendix B not read) | [F], partial |
| TPM 2.0 Library v1.85 adds ML-KEM (Encapsulate/Decapsulate) and ML-DSA (Sign/VerifySequence, Hash-ML-DSA) commands, per an implementer; the page does not state spec publication status | https://posts.wolfssl.com/2026/05/04/the-first-firmware-tpm-with-post-quantum-cryptography/ | [V] |
| PKCS#11 v3.2 working drafts include ML-DSA/ML-KEM/SLH-DSA mechanisms; final OASIS status not confirmed by me | groups.oasis-open.org PKCS11 TC threads (search results) | [2nd], final status unverified |
| IEC 62351-9:2023 exists; PQ in Annex B.11, nothing mandated | atlas line 271 [2nd]; webstore.iec.ch listing seen | [2nd] |
| OPC UA: no PQ security policy found | atlas line 272; my searches this session found no OPC Foundation primary document | unverified |

---

## F.0 Executive summary

1. **Reuse the transparency stack, build only the policy layer.** The authority ledger should be a SCITT-shaped service (RFC 9943 signed statements and COSE receipts) over a tile-based log (Tessera, the same backend Rekor v2 now uses), with C2SP-style external witnesses. What we must build is the *ledger statement vocabulary and its validity rules* (disjoint-assumption quorum, floor monotonicity, the PAM rule), as a small verifier library, not a new log. [H, grounded in F facts above]
2. **The log is evidence, not the source of device truth.** Devices never read the ledger. Devices accept only COSE_Sign objects checked against their own floor and slot hashes. The ledger lets *operators and auditors* detect forks, rollbacks and unauthorised floor advances. This keeps R2 (clock dependence) and R10 (decay) out of the device path.
3. **One update protocol: SUIT manifests carried in TUF/Uptane-shaped metadata, delivered by whatever transport the site already has.** Dormancy is a manifest condition plus a separate small, quorum-signed *activation order*; halt is revocation of that order. [H]
4. **No new evidence format.** Signed state report = an EAT profile (RFC 9711) carrying claims that CoRIM reference values can appraise; fleet inventory = CycloneDX CBOM; long-term preservation = RFC 4998 renewal. [H]
5. **Migration-twin prototype (runnable, [C])**: in a 2,400-device, 60-site model with a faulty update, staging alone did *nothing* (2.31% of devices out vs 2.32% for big-bang), the automatic halt cut it 15-fold (to 0.15%), and persisters added a further ~10% reduction. The halt, not the stagger, is the safety mechanism. Details F.6.

Atlas claims to challenge (F.9): M1's "acquaintance rule" is inventory-free but still needs passive flow observation, so it presupposes the passive parsers of F.4.7; and "persisters are bet-hedging against a defective fix" is only weakly supported by the twin (benefit ~10% in blast radius when detection works; value appears only when detection fails).

---

## F.1 The authority plane

### F.1.1 Problem and requirements

Atlas root causes served: R3 (authority tied to one organisation), R6 (rewindable state), R7 (invisible state), R9 (uninventoried authorisation paths), R10 (unexercised capabilities). Problems: N1-N8 (side doors), N41 (bankrupt signer), N51 (HSM portability), N52 (M&A).

Requirements for the ledger [H]:

| ID | Requirement | Reason |
|---|---|---|
| L1 | Append-only, publicly (to the operator federation) auditable, with split-view detection | Detect an authority that shows different histories to different sites |
| L2 | Logs only *authority-changing* events (floor advance, slot replacement, lifecycle transition, voucher redemption, revocation, activation order, halt, drill, heartbeat) | Alarm on danger, not novelty (atlas 11.7); keeps volume small |
| L3 | Verifier rules enforced *before* a statement is accepted (log policy) and *again* by every relying party | Log operator must not be trusted to enforce policy |
| L4 | Works offline: bundles of statements plus receipts usable with no connectivity | Islands, air gaps |
| L5 | No wall-clock dependence in validity; epochs are coarse and monotonic | R2, M4 |
| L6 | Algorithms in the log's own signatures must be agile; two hash waists | M2 |
| L7 | Survives decades: data model is self-describing CBOR/COSE, tooling is open | brief |

### F.1.2 Evaluation of existing building blocks

| Candidate | What it gives | What it lacks for this use | Verdict |
|---|---|---|---|
| **SCITT (RFC 9943)** [F] | Signed statements, transparency service, COSE receipts, "transparent statements" a relying party verifies offline; a registration policy hook | No OT vocabulary; says nothing about quorum, floors, offline federation; receipts use the log's signature algorithm, which must be PQ-capable | **Adopt as the ledger's architecture and wire format** |
| **Tessera / Trillian-tiles** [F: Rekor v2 uses Tessera; backends GCP, AWS, MySQL, POSIX] | Cheap, cacheable, tile read API; POSIX backend suits an air-gapped site | Checkpoint signature algorithms are classical in the deployed ecosystem [I]; PQ checkpoints need a profile | **Adopt as storage/log engine; add PQ checkpoint cosignature profile** |
| **C2SP witnessing** [F] | Cross-log consistency cosigning by independent witnesses | Witness keys classical today [I] | **Adopt protocol; run witnesses with PQ keys in two assumption classes** |
| **Sigstore Rekor v2** [F] | Production log of `hashedrekord`/`dsse` entries | Entry types are artifact signatures; no custom statement types; tied to public-good infrastructure and OIDC identities | **Do not reuse the service; reuse the engine (rekor-tiles/Tessera) as a reference deployment** |
| **Certificate Transparency (RFC 6962)** [F, not re-fetched] | Merkle tree, SCTs, gossip concept | Web-PKI specific; SCT promises are not inclusion proofs | **Reuse the Merkle/consistency maths only (it is what Tessera and the witness spec use)** |
| **TUF (roles, delegations, threshold, snapshot/timestamp)** [F, not re-fetched] | Thresholded roles, delegations, rollback protection via snapshot versions, compromise-resilient key roles | Timestamp role assumes clocks and online freshness; JSON metadata, classical sigs by default | **Reuse the role model for the *update metadata* (F.2); not for the ledger** |
| **Uptane** [F, not re-fetched] | TUF + director/image repo split, vehicle ECU secondary verification | Automotive assumptions (primary ECU with connectivity) | **Reuse the two-repository (director vs image) idea: a signing site decides *what* to install on a site, the vendor repository decides *what exists*** |
| **in-toto** [F, not re-fetched] | Supply-chain layouts and link attestations (who did which build step) | Not a ledger; concerns build provenance | **Reuse as the *content* of statements about release provenance, registered in the ledger via SCITT** |

DECISION: the ledger is a SCITT transparency service whose registration policy is the `authority-policy` verifier (F.1.3), backed by a Tessera tile log, with at least three external witnesses.

WHY: three of the four hard parts (append-only proofs, offline-verifiable receipts, cacheable reads) are solved and standardised; the unsolved part is policy. Building another log would create a maintenance burden for decades (brief: "must last decades") for no differentiating value.

ALTERNATIVES REJECTED: (a) a blockchain/consensus ledger: needs liveness and economic assumptions, adds a new dependency class and contradicts L5; (b) plain signed Git repository: no consistency proofs, easy to rewrite history undetected; (c) Rekor v2 public instance: wrong identity model and unsuitable for sovereign or air-gapped sites; (d) TUF-only: lacks inclusion/consistency proofs, so a compromised repository can show different timelines to different sites.

ASSUMPTIONS: SCITT and Tessera implementations can carry a PQ log signature (COSE algorithm registry now has ML-DSA via RFC 9964 [F]). Whether Tessera ships a PQ checkpoint signer today: unverified; we plan a small adapter.

TRADE-OFFS: PQ signatures enlarge receipts (F.1.5 arithmetic). The witness protocol and checkpoint format are classical-first; we diverge by profile.

LIMITS: A transparency log detects, it does not prevent; prevention is the device-side floor and quorum.

HOW WE VALIDATE: split-view test (two witnesses see different tree heads; verifier must flag), rollback test (replay old checkpoint; consistency check must fail), policy-bypass test (log operator registers a non-compliant statement; relying-party verifier must reject).

### F.1.3 Ledger statement vocabulary and validity rules

All statements are COSE_Sign (multi-signer, tag 98) objects, so a quorum is *native* to the envelope rather than layered above it. Payload is deterministic CBOR (RFC 8949 section 4.2, not re-fetched).

Statement types:

| Type | Meaning | Required signers (policy default) | Device-side counterpart |
|---|---|---|---|
| `FLOOR_ADVANCE` | Raises the minimum acceptable authority index | Quorum from a slot *different from the retiring one*, disjoint assumption classes | Floor monotonic counter in first stage |
| `SLOT_REPLACE` | Replaces a key-hash slot (provision alongside, shadow-sign, hide, shed, harden) | Disjoint quorum; successor key must co-sign (proof of possession) | Slot table |
| `LIFECYCLE` | Manufacture, commissioned, RMA, decommissioned, transferred | Per-transition policy (RMA needs two roles) | Lifecycle state (side-door closure, atlas 11.2) |
| `VOUCHER_REDEEM` | Ownership transfer executed (FDO voucher extension) | Outgoing owner + incoming owner + witness | Voucher chain |
| `REVOKE` | Revokes an *artefact* (image hash, leaf cert, voucher, group) | One authority class | Revocation list or floor |
| `ACTIVATION_ORDER` | "Activate bundle B on cohort C no earlier than epoch e" | Release authority plus site authority | Activation condition in SUIT manifest |
| `HALT` | Cancels outstanding activation orders for B | Any single release-class signer (asymmetric: halting is easy, activating is hard) | Order revocation |
| `HEARTBEAT` | OEM liveness (atlas 11.4) | OEM | Escrow trigger evidence (off-device) |
| `DRILL` | Slot drill executed and outcome | Slot owner | Operator evidence only |
| `CEREMONY` | Key ceremony record (F.1.6) | Ceremony officers | None |

**Rules the registration policy and every verifier enforce** [H]:

1. *Assumption-disjoint quorum.* A statement is valid if its set of cryptographically valid signatures contains a subset S with |S| >= k (policy; k=2 default) such that assumption sets of members are pairwise disjoint *and* members come from at least two distinct custody domains. Assumption sets come from a pinned, versioned `assumption_registry` (conservative: ML-DSA {MLWE, Keccak}; SLH-DSA-SHAKE {Keccak}; SLH-DSA-SHA2 {SHA-256}; LMS-SHA256 {SHA-256}; ECDSA {ECDLP, SHA-256}) per atlas M2 [C, from atlas]. Because only two hash waists exist, valid pairs are ML-DSA with LMS or SLH-DSA-SHA2, or SLH-DSA-SHAKE with LMS or SLH-DSA-SHA2.
2. *Floor monotonicity.* `FLOOR_ADVANCE.new_floor > prior_floor`; chain-linked by `prev` hash; fork = two different statements with the same `prev`.
3. *PAM rule.* `REVOKE` may only target identifiers whose class tag is `ARTEFACT` (image, leaf, voucher, group key epoch). Any target that resolves to a slot in the current authority set is rejected at registration and by relying parties. Removing authority is done only by `SLOT_REPLACE` with a successor present. This makes "revoke the current signer and brick the fleet" structurally impossible (atlas N-series CRISPR PAM idea; [H]).
4. *Retiring-slot exclusion.* A `FLOOR_ADVANCE` that retires slot s must carry no required signature from s.
5. *Sequence.* Each (domain, type) has a strictly increasing `seq`; replay of old statements fails.
6. *Epoch, not time.* Statements carry `epoch` (coarse month index since a pinned origin) and `not_before_epoch`, used only to tighten (atlas M4). No rule depends on a device's clock.

### F.1.4 Offline, island and partition operation

Sites with no connectivity (air gap, ship, remote substation, sovereign enclave) are first-class.

| Mode | Mechanism | Detail |
|---|---|---|
| Connected | Online log, witnesses cosign checkpoints | normal |
| **Sneakernet bundle** | `authority-bundle`: statements + inclusion proofs + latest cosigned checkpoint + consistency proof from the site's last known checkpoint | A site verifies a bundle with only the log public key set and its last stored checkpoint |
| **Island authority** | Site holds a *local* sub-ledger (own Tessera POSIX log) delegated by the fleet authority for site-scoped types only (`ACTIVATION_ORDER` scoped to site, `LIFECYCLE` for local devices) | Island can never issue `FLOOR_ADVANCE` or `SLOT_REPLACE` for fleet-wide slots |
| Partition rejoin | Island uploads its sub-ledger; fleet verifier replays it under rules 1-6; conflicts are resolved deterministically | below |

**Reconciliation algorithm** [H]: statements are a DAG keyed by `prev`. On rejoin, (1) verify every island statement individually; (2) if the island chain forks from the fleet chain at a statement with the same type and `seq`, do *not* auto-merge: emit a `CONFLICT` evidence object, freeze irreversible follow-ons (floor advances) for the affected domain, and require a quorum `RESOLVE` statement; (3) site-scoped statements that do not collide merge by timestamp-free ordering (by `(domain, seq)`). This implements atlas "stop signals" (11.4) and the deterministic tie-break "after escalation".

**Freshness without time**: relying parties never reject on staleness automatically. Staleness is *reported* (checkpoint age in tree-size growth and epochs), and devices that rely on a stale authority view enter "senescence" (atlas 11.6): control continues, authority changes are refused, state is announced.

### F.1.5 Size and cost arithmetic

Sizes: ML-DSA-65 signature 3,309 B and public key 1,952 B; SLH-DSA-SHAKE-128s signature 7,856 B; ML-KEM-768 encapsulation key 1,184 B and ciphertext 1,088 B (FIPS 203/204/205; from memory, not re-fetched) [F-unverified]. LMS (RFC 8554) SHA-256, h=10, w=8: signature = 4 (q) + 4 (type) + [4 + 32 + 34x32 = 1,124] (LM-OTS) + 4 (type) + 10x32 (path) = 4+4+1,124+4+320 = 1,456 B [C, from RFC 8554 structure from memory].

Typical ledger entry (`FLOOR_ADVANCE`, two signers ML-DSA-65 + LMS): payload ~300 B + 3,309 + 1,456 + ~150 B COSE overhead ≈ 5,215 B [E]. If the log stores only hashes of statements (SCITT hash-envelope style) the leaf is ~32 B plus metadata and bodies live in cheap object storage.

Volume: 10,000 sites x 20 authority events/site/year = 200,000 entries/yr [E, assumption]. 200,000 x 5,215 B = 1.04 GB/yr [C]. Merkle tree overhead with tiles is ~1% of leaf bytes [I]. Conclusion: trivially small; the log is dominated by signature size, not event count. A POSIX tile log on one 1 TB disk holds ~960 years at this rate [C: 1e12/1.04e9].

Receipt size: inclusion proof depth log2(2e5*10 yr)=~21 hashes x 32 B = 672 B plus one checkpoint with 3 witness cosignatures: 3 x 3,309 = 9.9 KB if all ML-DSA-65 [C]. Receipts are for operators and gateways, not constrained devices.

### F.1.6 Signing authorities, HSMs, ceremonies

**Quorum protocol between authorities** (disjoint assumption classes):

```
Authority A1  (class X: ML-DSA, SHAKE waist, HSM vendor V1, org unit O1)
Authority A2  (class Y: LMS or SLH-DSA-SHA2, SHA-256 waist, HSM vendor V2, org unit O2)
Authority A3  (spare, class X or Y, dormant slot, exercised by annual drill)
Coordinator   (untrusted, stateless: assembles COSE_Sign)

1. Coordinator publishes proposal P = {type, payload, prev, seq, epoch} (hash H(P) to all)
2. Each authority independently validates P against its own copy of the ledger head + policy (no shared code path with the other authority where avoidable)
3. Each authority signs the COSE Sig_structure of P with its HSM key; stateful signers (LMS) reserve the index in the HSM BEFORE signing and persist it (R6)
4. Coordinator collects >=k signatures, checks rule 1 (disjoint) and submits to the transparency service
5. Service verifies rules 1-6, registers, returns receipt; coordinator distributes {statement, receipt}
```

Stateful hash signatures (LMS/XMSS) are the quorum member where index reuse is a risk (P3, N22, N51). Mitigation: the HSM, not the host, owns the index; no key export; backups never include the index counter; cluster designs partition the index space *by disjoint sub-trees* (LMS "L" levels / HSS) so two HSMs never share a leaf range. NIST draft SP 800-230 limited-use SLH-DSA sets are the stateless alternative (atlas Part 0) [F, draft, per atlas].

**HSM integration:**

| Interface | Role | PQ status (verified this session) |
|---|---|---|
| PKCS#11 v3.2 | Primary signing/KEM API; `provider-pkcs11` in our crypto abstraction | ML-DSA/ML-KEM/SLH-DSA mechanisms appear in OASIS v3.2 working drafts (many WD revisions seen) [2nd]; final approval status unverified. HSM vendor docs show PQ over PKCS#11 (Futurex) [V] |
| KMIP | Key lifecycle, wrapped key escrow between custodians | KMIP 3.0 PQC test material is posted to the OASIS TC [2nd]; final status unverified; HyTrust docs claim PQ in KMIP vault [V] |
| Cloud HSMs | For *non-root* roles only (coordinator audit keys, witness keys) | No primary PQ evidence gathered; treat as unverified |
| Software keys | Never for authority classes | n/a |

DECISION: define `trait AuthoritySigner` with three backends (PKCS#11, KMIP-wrapped, test-only software) and require, for production authority classes, that the two quorum classes live on *different HSM vendors and different organisations* (custody domains).

WHY: assumption diversity (M2) is defeated if both classes sit on one vendor's firmware or one admin's credentials (hidden common mode: Knight-Leveson, atlas Part 0). ALTERNATIVES REJECTED: a single HSM cluster with two partitions (common firmware and admin domain); threshold ML-DSA succession (demoted in atlas; research). ASSUMPTIONS: at least two HSM vendors ship usable PQ or hash-signature support; ML-DSA and a hash-based scheme each. TRADE-OFFS: cost and operational burden of two custody chains. LIMITS: vendor PQ support is moving; some HSMs lack LMS. HOW WE VALIDATE: ceremony dry-runs, a quarterly cross-vendor signing test (the slot drill), and a conformance suite that signs known-answer vectors on each backend.

**Ceremonies** (schema `CEREMONY`): scripted, recorded, witnessed; produce a `CEREMONY` statement containing script hash, officer identities (public key hashes), HSM attestation of key generation where the HSM offers it, and hashes of the video/log bundle. Each ceremony type has a *rehearsal requirement*: the same script is executed in a lab at least once per year (R10 skill extinction, N61). A ceremony whose rehearsal statement is older than 24 months is flagged in evidence.

---

## F.2 Update and staging protocol

### F.2.1 Landscape

| Standard / project | Role | Status seen | Use |
|---|---|---|---|
| IETF SUIT: RFC 9019 (architecture), RFC 9124 (information model) (not re-fetched), draft-ietf-suit-manifest-38 [F, RFC Editor queue 2026-11-04] | Manifest: conditions, sequences, dependencies, encryption, text | Manifest still a draft; stable enough to build on; RFC 9334 is RATS, not SUIT | **Manifest format** |
| ML-DSA in COSE: RFC 9964 [F] | PQ signature algorithm identifiers for SUIT's COSE envelopes | Published | Use directly |
| SUIT PQ profile (hash-based, SLH-DSA, LMS in COSE) | Needed for the Keccak/SHA-256 pair | I did not find a primary document this session; unverified | Define as a profile in our library until a standard exists [H] |
| TUF / Uptane (F.1.2) | Metadata roles, rollback/freeze protection, director/image split | Mature | **Metadata layer** |
| Mender, RAUC, SWUpdate [F, not re-fetched] | Agents and A/B slot machinery for Linux-class devices | Mature | **Transport/installer back-ends** behind our `UpdateAgent` trait |
| MCUboot/vendor secure boot | Constrained installers | Not researched here (stream owner for device boot path) | Device-side, other stream |
| FDO v2.0 [F] | Onboarding and ownership vouchers | PQ recommended not mandated; classical suites visible | Voucher chain with *PQ profile defined by us* |
| OPC UA GDS push/pull (Part 12) (not re-fetched) | Certificate and trust-list management for OPC UA nodes | No PQ policy found | Adapter, not core |
| IEC 62443-4-2 / 3-3 | Requirements mapping | Standards | F.2.5 |

DECISION: the unit of update is a **SUIT manifest wrapped in COSE_Sign (quorum), distributed through TUF-style metadata with a director/image split, installed through a pluggable agent (Mender/RAUC/SWUpdate/vendor).** The *core* knows only: manifest bytes, quorum evidence, activation order, cohort identity, state report.

WHY: SUIT has the semantics we need (conditions, dependency, component identity, encryption) and is IoT-sized. TUF gives battle-tested compromise-resilience semantics. Agents already own flash mechanics. ALTERNATIVES REJECTED: new bespoke bundle format (violates "do not invent a format"); using only vendor agents (no cross-vendor evidence); OTA-only designs (Part 0: only 15% patch in windows [2nd]; transport must include USB/sneakernet). ASSUMPTIONS: SUIT manifest draft stays wire-stable; it is in RFC Ed queue and has an IANA CBOR tag open item (map vs. other) [F], a small risk. TRADE-OFFS: three layers (SUIT, TUF-like metadata, agent) add integration surface. LIMITS: constrained C1 devices may support only hash-verified images, no SUIT parser. HOW WE VALIDATE: round-trip tests against two independent SUIT implementations; fuzzing the manifest parser; conformance vectors.

### F.2.2 Dormant-stage-then-activate flow

Atlas 11.5 and I-series: stage early, activate in the window. Our split:

1. **Stage** (any time): bundle (manifest + payload, signed) delivered and verified; written to the inactive A/B slot; device state `STAGED_DORMANT`. Verification already proves authenticity; nothing executes.
2. **Order** (separate, small): `ACTIVATION_ORDER` statement addressed to a *cohort* (site, class, persister-flag, hardware rev). Carries `not_before_epoch`, `bundle_hash`, `max_attempts`.
3. **Activate** (in the maintenance window): device or site controller checks order, floor, and local window gate (operator's calendar token); runs the SUIT sequence; performs self-test; commits or rolls back.
4. **Report**: signed state report (F.3.2) with floor index, active slots, image hash, policy hash, result code.
5. **Halt**: `HALT` statement revokes orders for the bundle; sites that hear it never activate; devices already active are unaffected (they follow the rollback path).

DECISION: activation is *authorised by a separate artefact from distribution*, and `HALT` requires only a single signer of the release class while `ACTIVATION_ORDER` requires a quorum.

WHY: stopping must be cheaper and faster than starting (asymmetry; the CrowdStrike lesson in atlas 11.5). A single compromised signer can halt (availability harm, bounded, detectable in the ledger) but not activate. ALTERNATIVES REJECTED: halt needs quorum (too slow in an incident); time-limited bundle validity (needs clocks, R2). ASSUMPTIONS: devices can store the order or fetch it via gateway before the window. TRADE-OFFS: an attacker with one signer can denial-of-update the fleet; mitigated by the floor rule that a halt cannot cancel an already-activated floor advance and by an escalation `RESOLVE` quorum. LIMITS: offline sites activate on their last known order; see F.8 stale-order discussion. HOW WE VALIDATE: migration twin (F.6): halt propagation with partitions.

### F.2.3 Persister cohort and staged rollout

- **Persister cohort**: a fraction p (default 5%, [H]) of devices in *every site* are flagged in inventory and excluded from activation until a `PERSISTER_RELEASE` order, issued only after the full rollout has been quiet for a soak period. Per-site (not per-site-subset) distribution means every site keeps some last-known-good devices, so a faulty update cannot take down a whole site's redundancy.
- **Waves**: wave 0 canary (3% of sites, including at least one site from each hardware stratum in inventory), then 12%, 30%, 55% (default in twin) with a gap between waves. Class order follows F.7.
- **Automatic halt**: controller computes failure rate = failed reports / activation reports over reported results; halts if n >= n_min and rate >= threshold (defaults n_min=15, 5%). Controller *and* an independent watcher both can issue `HALT` (two-signal rule; atlas 5.7).
- **Partition awareness**: results from partitioned sites arrive late; the controller treats "no report yet" as unknown, counted in an "in-flight exposure" gauge shown to the operator.

### F.2.4 FDO vouchers with a PQ profile

Observed: FDO PS v2.0 recommends PQ safety but mandates none [F]. Our profile (to propose to FIDO Alliance) [H]:

| Element | Classical in FDO v2.0 | Our PQ profile |
|---|---|---|
| Voucher entry signatures | ECDSA P-256/P-384, RSA | COSE_Sign with ML-DSA-65 *and* a hash-based signature (disjoint classes), per hop |
| TO2 key exchange | ECDH, DH, asymmetric KEX | ML-KEM-768 + X25519 hybrid (as policy) |
| Voucher hash chain | SHA-256/384 | SHA-256 and SHA3-256 dual hash headers |
| Redemption | Rendezvous + owner | Redemption statement logged as `VOUCHER_REDEEM` in the ledger |

Escrow: voucher chain plus the *slot 3* provision is required (atlas "critical dependency": OEM-exit works only if slot 3 was provisioned at manufacture). Voucher files are crown jewels (N7); store in HSM-backed vault, log every redemption.

### F.2.5 IEC 62443 mapping (clause identifiers from memory; verify against the purchased texts)

| 62443 requirement family | Our mechanism | Evidence artefact |
|---|---|---|
| 3-3 SR 3.4 / 4-2 CR 3.4 software and information integrity | Quorum-signed SUIT, first-stage floor | Signed state report |
| 4-2 EDR 3.14 integrity of boot process | Locked first stage (device stream) | Attestation claim `boot.floor` |
| 4-2 EDR 3.10 support for updates | Dormant/activate, A/B rollback | Update ledger entries |
| 3-3 SR 4.3 / 4-2 CR 4.3 use of cryptography | `assumption_registry`, CBOM | CycloneDX CBOM |
| 3-3 SR 2.8 auditable events, SR 2.12 non-repudiation | Authority ledger | Receipts |
| 3-3 SR 1.5 authenticator management | KDC enrolment and rekey (F.4) | Enrolment statements |
| 2-3 patch management; 4-1 SUM practices | Staged rollout plan, rollout twin report | Twin report archived |

[I]: IDs are "from memory, unverified". The brief forbids inventing clauses; treat this table as a checklist to confirm.

---

## F.3 Attestation and evidence

### F.3.1 Principles: do not invent a format

| Need | Existing format | Our addition |
|---|---|---|
| Device attestation of state | RATS architecture RFC 9334 (not re-fetched), EAT RFC 9711 [F] | An **EAT profile** (profile URI and claim set), no new envelope |
| Reference values/endorsements | CoRIM (draft-ietf-rats-corim-12, WGLC [F]) | Our CoRIM profile for "floor index, slot hashes, policy hash" |
| Hardware identity | TCG DICE; TPM 2.0 v1.85 PQ commands [V] | Verify claims; pin PQ algorithm sets |
| Crypto inventory | CycloneDX CBOM (version not verified this session) | Mapping from observations to CBOM components |
| Software inventory | SPDX/CycloneDX SBOM; VEX for exploitability | Link CBOM to SBOM by component hash |
| Long-term preservation | RFC 4998 ERS (not re-fetched) | Renewal scheduler (F.3.5) |

DECISION: our only invented artefact is a **profile document** (list of claims and appraisal policies), published as a spec plus CDDL. WHY: avoids a new wire format and reuses implementations and tooling. ALTERNATIVES REJECTED: a custom JSON report (adoption friction; no signature semantics); full SPDX-only (no crypto-agility modelling). ASSUMPTIONS: EAT profile mechanism is flexible enough for floor/slot claims. TRADE-OFFS: CoRIM is not yet an RFC; EAT is. LIMITS: DICE/TPM PQ in the field is thin. HOW WE VALIDATE: appraisal round-trip with an open RATS verifier; interoperability test with a second implementation.

### F.3.2 Signed state report (EAT profile)

Claims (CBOR map; labels from the private/profile range, to be registered when stabilised):

| Claim | Type | Meaning | Size (B) |
|---|---|---|---|
| `ueid` / `sn` | bstr | device identity | 17 |
| `floor` | uint | current floor index | 1-4 |
| `slots` | array of 3-5 bstr | key-hash slot digests (truncated 16 B) or slot IDs | 48-80 |
| `slot_states` | array | active/hidden/shed per slot | ~5 |
| `image_hash` | bstr | SHA-256 of active image | 32 |
| `policy_hash` | bstr | SHA-256 of active policy | 32 |
| `lifecycle` | uint | lifecycle state | 1 |
| `bundle_state` | uint | none/staged/activated/rolled_back | 1 |
| `nonce` | bstr | verifier nonce or `seq` (offline: monotonic counter) | 8-16 |
| `epoch` | uint | coarse epoch label supplied by gateway | 2 |

Report total ~240 B before signature [E]. Signature: for C2+ devices ML-DSA-44 (2,420 B) or HMAC under the per-device key (32 B) where no signing key exists. HMAC reports are verified by the KDC/gateway (symmetric attestation), documented as *weaker* (verifier holds the key) [I].

### F.3.3 Exposure-years computation (spec, links to atlas M5)

Definitions [H, formulas; arithmetic checked [C]]:

- For device d, scenario S (a set of broken assumptions), time tau: `exposed(d, tau, S) = 1` if some authority quorum Q acceptable to d at tau has every member's assumption set intersecting S (conservative M2 dependency model) or d still accepts a classical-only path.
- Weight `w_d = class_weight(d) * reach(d)`; `reach` is the size of the connected component of unmigrated trust edges containing d, divided by fleet size (M1 blast radius).
- Scenario-conditional: `EY(S, T) = sum_d w_d * integral_{T}^{H} exposed(d, tau, S) dtau`.
- Expected: `E[EY] = sum_S sum_T P(S) f(T) * EY(S, T)`.

Check against the atlas closed form for uniform replacement rate r: exposure after T = `(1-r)^T / (-ln(1-r))`. r = 0.10, T = 8: 0.9^8 = 0.43047; -ln 0.9 = 0.10536; 0.43047 / 0.10536 = 4.086 [C], matching the atlas 4.1. r = 0.05, T = 5: 0.77378/0.051293 = 15.09 [C], matching 15.1. So the calculator discretises the same quantity, with per-device exposure and graph weights instead of a uniform average.

Inputs: inventory (`device`, `class`, `site`, `slots`, `algorithms`), trust graph (F.7), scenario set, migration plan with dates, replacement schedule. Output: time series of `EY`, `exposed_fraction`, `blast_radius`, per-site contribution. Programme KPI: `EY` remaining to horizon; target is monotone decreasing with planned completion.

### F.3.4 Passive and active collection

Observation (F.4.7) feeds `CryptoObservation` records, which are mapped to CBOM `cryptographic-asset` components and to inventory facts with confidence labels (`measured`, `inferred`, `declared`). A device that is silent has `declared` or `inferred` only, and the exposure calculator treats unknown as exposed (conservative).

### F.3.5 Evidence-record renewal

State reports, voucher chains and decommissioning receipts must stay verifiable beyond the life of their signature algorithms. Use RFC 4998 Evidence Record Syntax semantics: archive hash trees, timestamps over the root, and *timestamp renewal* (new timestamp over old evidence with a stronger algorithm) and *hash-tree renewal*. Our scheduler:

- `renew_due(record)`: record's current timestamp algorithm has an age or risk tag reaching a policy threshold (default: renew at 50% of the algorithm's assumed lifetime, *before* weakness; atlas Part 7).
- Renewal timestamps are produced by registering the archive root hash as a SCITT statement (F.1) and carrying the cosigned checkpoint under a PQ class; the ASN.1 ERS structure holds the proofs for tools that expect it. [H, assumption: ERS accepts a non-TSA timestamp token; unverified]
- Dual-hash: archive trees use SHA-256 and SHA3-256 roots to preserve both waists.

---

## F.4 Key distribution for the symmetric process-bus fabric

### F.4.1 What must be true

Atlas: real-time data paths are symmetric and AES/HMAC survive quantum attack [F]. Exposure is *how long-term keys first arrive* (R4, N10, P19, P20). Requirements: C1 devices must use unique per-device keys; no public-key work in the data path (class C3 forbids it); group keys rekey within ~1 s without disturbing traffic (E4 experiment target).

### F.4.2 KDC design

```
          +------------------- C5 offline ----------------+
          |  Fleet Diversification Authority (FDA)        |
          |  root diversification secret DS (HSM only)     |
          +----------------------+------------------------+
                                 | wraps DS_site (KMIP/PKCS#11)
                  +--------------v--------------+
                  |  Site KDC (C4, in enclave)  |   two instances, two vendors
                  |  holds DS_site only         |
                  +------+---------------+------+
        ML-KEM enrol     |               | group keys (GDOI-style, rekey)
        (rare)           |               |
        +---------------v--+      +------v------------------+
        |  Device (C2+)    |      | Bus members (GOOSE/SV)  |
        |  K_dev = KDF(DS_site, uuid||purpose||epoch)       |
        +------------------+      +-------------------------+
```

- **Per-device diversification**: `K_dev = HKDF-SHA256(DS_site, info = "dev" || uuid || purpose || epoch)`; alternative KMAC if the SHAKE waist is wanted. The site KDC can *recompute* K_dev (it needs it to wrap group keys), so a site KDC compromise loses that site only, never other sites; the FDA never leaves the offline authority. (Atlas anti-weak-path invariant 2.)
- **Enrolment** (once per epoch): C2+ devices run ML-KEM-768 *once*: device publishes `ek` (1,184 B), the KDC encapsulates (1,088 B ciphertext), both derive `K_enrol = KDF(ss)`, used to deliver K_dev material and bind identity. Hybridise with a classical KEM if policy requires. C1 devices have no KEM: physical commissioning token or gateway-assisted enrolment; the gateway's authority is bounded to the C1 boundary zone.
- **Group keys**: per-group `GK_e` generated in the HSM-backed KDC, wrapped per member with `K_dev` using AES-256-GCM or AES-KW: payload per member ≈ 32 B key + 12 B nonce + 16 B tag + ~8 B header = 68 B [E]. For a group of 200 members: 200 x 68 = 13.6 KB; at 100 Mbit/s = 13,600*8/1e8 = 1.1 ms of link time [C]; practical latency is dominated by the KDC computing 200 wraps and device scheduling. Target < 1 s per group is plausible [E], to be proven by the E4 experiment.
- **Epoch overlap**: members hold `GK_e` and `GK_{e+1}` so a missed rekey during a partition does not drop traffic; epochs are counters not dates (R2).
- **Device identity binding**: group membership grants are statements by the KDC signed with its own key (ML-DSA-44, C4 holds keys) and logged to the site sub-ledger; a role-mismatch detector flags devices holding keys beyond their role ("camouflage detection", atlas 11.3).

DECISION: site KDC derived from an offline FDA, per-device diversification, ML-KEM enrolment, GDOI-compatible rekey semantics. WHY: confines the PQ public-key step to a rare enrolment, leaves IEC 62351-6 MACs unchanged, bounds a KDC breach to a site. ALTERNATIVES REJECTED: (a) pure pre-shared fleet key (N10); (b) per-message public-key authentication (does not fit GOOSE timing); (c) one central fleet KDC (single point of fleet-wide trust, violates invariant 2 for C4). ASSUMPTIONS: device can hold a unique 128-256 bit secret; the site has an HSM-class store for DS_site. TRADE-OFFS: site KDC is a high-value C4 asset; mitigated by dual-vendor and by never giving it signing authority over firmware. LIMITS: symmetric attestation weakness; KDC availability for rekey. HOW WE VALIDATE: E4 rekey-vs-latency test; KDC compromise tabletop (F.8); known-answer tests for the KDF.

### F.4.3 Protocol-by-protocol PQ status

| Protocol | Cryptography used | PQ-relevant surface | Status verified this session | Adapter action |
|---|---|---|---|---|
| IEC 61850 GOOSE/SV, IEC 62351-6 | HMAC/AES-GMAC on frames | Group key delivery only | 62351-6 not re-fetched; 62351-9:2023 PQ discussed in Annex B.11, none mandated [2nd] | Pass-through; KDC supplies keys |
| IEC 62351-9 (GDOI) | GDOI/IKE-derived key distribution | KEK establishment | As above | Implement GDOI-compatible adapter; PQ profile proposed to TC57 WG15 [H] |
| DNP3-SA v5/v6 (IEEE 1815.1) | HMAC; update key change via symmetric or asymmetric | Update-key-change path | A UCC paper (title seen) proposes a quantum-safe hybrid for DNP3-SAB [2nd, abstract-only]; no standardised PQ found | Adapter handles update key via KDC; treat asymmetric UKC as legacy |
| IEC 60870-5-7 (SA, 62351-5 lineage) | HMAC (SA-like) | Update key | Not verified | Same as DNP3-SA |
| OPC UA | Security policies (RSA, ECC), OpenSecureChannel | Policy negotiation, cert trust | Atlas: no PQ policy; 1.05.07 adds ECC [2nd]; no primary found by me; spec Part 2 2026 edition exists (title seen) | Passive policy extraction; GDS adapter; prefer SecurityMode SignAndEncrypt |
| MQTT / Sparkplug | TLS | Broker TLS groups | Not verified here; PQ follows the TLS stack | Observe TLS groups |
| Modbus Security (Modbus/TCP Security) | TLS with X.509 | Cert and TLS groups | Not re-fetched | Observe TLS |
| LoRaWAN | AES-128 root keys (AppKey/NwkKey), join server | Root key provisioning and join server trust | Not re-fetched | KDC-style root key delivery; ML-KEM at join-server provisioning |
| CCSDS SDLS (355.0-B-1) | Symmetric (AES-GCM etc.) | OTAR/key management | Standard exists (listing seen); ESA papers discuss quantum-safe key delivery [2nd] | Ratcheted symmetric authority (idea I-series) for disconnected assets |
| FDO | ECDSA/ECDH visible; PQ not mandated [F] | Voucher chain | F.2.4 | Voucher PQ profile |

All "not verified" cells are exactly that. Per rule 2 I do not assert more.

### F.4.4 Protocol adapter architecture

Principle: **protocols stay out of the core.** The core manages *keys, identities, statements, evidence, plans*. An adapter translates between that and a wire protocol.

```rust
/// Provided by every protocol adapter. The core never imports a protocol crate.
pub trait ProtocolAdapter: Send + Sync {
    fn id(&self) -> &'static str;                        // "iec62351-6", "dnp3-sa", "opcua"
    fn key_profile(&self) -> KeyProfile;                 // what key types/lengths/rekey it needs
    fn assumptions(&self) -> &'static [AssumptionTag];   // pins to assumption_registry
    fn observe(&self, frame: &Frame, ctx: &ObsCtx) -> Vec<CryptoObservation>;   // passive
    fn enrol(&self, dev: &DeviceRecord, kdc: &dyn KeySource) -> Result<EnrolPlan, AdapterError>;
    fn rekey(&self, group: &GroupId, epoch: u64, kdc: &dyn KeySource) -> Result<Vec<RekeyMsg>, AdapterError>;
    fn limits(&self) -> AdapterLimits;                   // latency budget, max frame, MAC truncation
}

pub struct KeyProfile { pub alg: SymAlg, pub key_bits: u16, pub mac_trunc_bits: Option<u8>,
                        pub group: bool, pub epoch_overlap: u8, pub max_rekey_ms: u32 }
pub struct CryptoObservation { pub device_hint: DeviceHint, pub protocol: &'static str,
                        pub kind: ObsKind, pub algorithm: AlgorithmId, pub confidence: Confidence,
                        pub source: Evidence }   // Evidence = pcap ref, offset, hash
```

An adapter must provide: (1) key profile, (2) passive observe (never actively probes live safety traffic; passive tap or span), (3) enrol/rekey mapping, (4) declared latency and truncation limits so the core can reject policies that violate safety timing (e.g., MAC truncated to 24 bits in some SecOC profiles is flagged), (5) a conformance test vector set. Adapters are separate crates/packages with their own release cadence, the same way TUF clients ship per-language.

Core invariant: **a protocol adapter cannot sign a ledger statement** and cannot hold a root diversification secret; it only receives per-purpose derived keys. This keeps R5 (crypto co-located with safety) from reappearing through adapters.

### F.4.5 Safety separation (EN 50159-style)

The safety code (e.g., the protection function) accepts "message authentic Y/N, fresh Y/N" from a cryptography layer through a narrow interface, so the cryptographic layer can migrate without reopening the safety case (atlas Part 0). The adapter interface exposes only these two bits plus a diagnostic code to the safety side.

### F.4.6 What "no PQ needed" really means

Symmetric crypto: Grover reduces effective strength roughly to half the key length, so AES-256/HMAC-SHA-256 stay comfortable; AES-128 in 62351-6 profiles has a smaller margin but is not the priority [I]. The exposure remains enrolment, GDOI/IKE-style key transport with classical public-key, and any asymmetric update-key change. Hence the single rare ML-KEM step.

### F.4.7 Passive inference parsers for silent devices

Silent devices (no reports) are observed on the wire. Parser set (each emits `CryptoObservation`):

| Parser | Extracts | Confidence | Notes |
|---|---|---|---|
| OPC UA OpenSecureChannel | policy URI, security mode, cert chain algorithms | measured | Flag `None` and AutoAccept patterns (N38) |
| TLS/DTLS ClientHello/ServerHello | supported_groups, signature_algorithms, selected group | measured | Detects hybrid KEM groups |
| IKEv2 | proposals, KE methods | measured | |
| GDOI / IEC 62351-9 | group policy, algorithms | measured | |
| DNP3-SA, 60870-5-7 | SA version, MAC algorithm id, challenge sizes | measured | |
| GOOSE/SV | presence/absence of authentication extension | measured | Absence is itself a finding |
| LoRaWAN | MIC presence, join behaviour | inferred | Via gateway packet forwarder logs |
| Modbus TCP | presence of TLS wrapper | measured | |

Design: parsers are *pure functions over bytes* (no network), fuzzed, memory-safe (Rust), and run on a sensor outside the control path. Atlas caution: incumbent OT-visibility vendors will absorb passive parsing; the durable value is evidence regulators accept, so we make the parsers a reference library and push value to the statement/evidence layer.

---

## F.5 Enclave and gateway

For devices that cannot change (C0/C1 and some C2).

### F.5.1 Dual-vendor PQ-terminating gateway

| Option | Description | Verdict |
|---|---|---|
| Single gateway | PQ TLS/IPsec to the control centre; legacy on the inside | Minimal form; vendor and implementation monoculture |
| **Series, nested** | Gateway X (vendor 1 stack) outer tunnel, gateway Y (vendor 2 stack) inner tunnel for authority-bearing traffic (management, config, firmware transfer) | **Recommended for authority-bearing paths** |
| Parallel hot-standby | Two gateways, same policy, failover | **Recommended for data paths (availability)** |
| Combined KEM in one tunnel | Hybrid of two KEMs in one session | Does not diversify implementation; keep as a crypto-level hybrid inside each gateway |

Overhead of nesting: each ESP tunnel adds about 20 (outer IP) + 8 (ESP header) + 16 (IV) + ~2 (trailer/pad) + 16 (ICV) = 62 B; two layers = 124 B per packet [E]. A GOOSE/SV frame of ~100-300 B grows by ~40-120%; for TCP management traffic the cost is immaterial. Control traffic on legacy segments uses neither because it does not cross the boundary.

Equivalence check: both gateways load the same signed configuration (F.5.3); each publishes a hash of its *effective* policy in a state report; a verifier compares hashes (policy drift detection). This is the cross-check that catches one vendor's bug.

DECISION: nested for authority paths, parallel for data paths, signed config both. WHY: independence of implementation (M7: put diversity inside each path where possible). ALTERNATIVES REJECTED: a single large gateway (N43 concentration), same-vendor pair (common mode). ASSUMPTIONS: two vendors can interoperate on a common PQ profile; PQ IPsec/TLS stacks mature. TRADE-OFFS: cost, complexity, latency. LIMITS: "contains the link, not the device's firmware trust" (atlas 11.6). HOW WE VALIDATE: differential testing of the two stacks against the same handshake vectors; failure injection (one gateway down).

### F.5.2 Sectored enclaves and exit clocks

- **Sectoring**: split an enclave into k sectors with independent boundary pairs so that one boundary failure takes down at most 1/k of devices. Choose k so that sector size is no larger than the *largest group the process can lose safely* (e.g., one feeder, one production cell). Loss on one failure = 1/k of devices [C, trivial]; cost grows linearly with k (gateway pairs). Policy picks k by process analysis, not by the library.
- **Exit clock**: every legacy exception is a signed record:

```
exception_record = {
  device_id, zone_id, reason, owner_authority,
  expiry_epoch,           ; coarse epoch (months), not a date
  escalation: [ {epoch_offset: -6, level: "warn"}, {-3, "manager"}, {-1, "block-renewal"} ],
  replacement_plan_ref,   ; budget line id
  sig: COSE_Sign          ; quorum (operator + risk owner)
}
```

The gateway reads the record, surfaces warnings as the current epoch approaches `expiry_epoch`, and *never silently extends*. Epoch for a gateway comes from its time source (GNSS/PTP/NTP) with fallback to the highest epoch seen in any signed config, so the clock can tighten but not rewind (atlas M4 rule: time may tighten privileges but never stop a safety function).

### F.5.3 Signed configuration

Configuration (zones, conduits, allowed algorithms, exit records) is a SUIT-like manifest or CBOR map wrapped in COSE_Sign with an engineer-plus-reviewer quorum (atlas 11.8). Gateways reject unsigned or lower-`seq` config; they publish `config_hash` in the state report. AI configuration assistants (N47) can *propose* but cannot hold quorum keys.

---

## F.6 Fleet-scale simulation: the migration twin

### F.6.1 Specification

Purpose: rehearse an update or migration against a model of the fleet to estimate blast radius, time to completion and exposure-years *before* the real rollout, and to back-test halt rules. This is the "migration twin" practice named in atlas 11.5.

| Element | Spec |
|---|---|
| Entities | `Site` (windows, connectivity schedule, hardware strata), `Device` (class, hw rev, persister flag, state), `Controller` (release policy, halt rule), `Authority` (orders/halts) |
| Events | `release(wave)`, `deliver(site)`, `window(site)`, `report`, `fail(latent)`, `recover`, `partition_start/end`, `halt`, `persister_release` |
| Inputs | Inventory export (JSON/CBOR), window calendar, partition model, fault model (fraction, latent share, rollback success), strategy parameters |
| Outputs | JSON: failed devices, transient failures, site outages, halt time, migrated fraction, exposure-days, per-run seeds |
| Time | Days; discrete-event priority queue |
| Determinism | Seeded RNG; every run reproducible |
| Validation | (1) conservation checks (device state counts add up); (2) back-test against historical rollouts if logs exist; (3) sensitivity sweeps over detection delay and halt threshold; (4) compare against closed forms (M5) for the no-fault case |

### F.6.2 Prototype and results

Code: `/home/claude/atlas2/blueprint/code/F/migration_twin.py` (stdlib only, ~250 lines). Raw output: `/home/claude/atlas2/blueprint/code/F/run_output.txt`. Run: `python3 -I migration_twin.py 300`. All figures below are model output [C] under the stated assumptions; they are not measurements.

Assumptions (all in `Params`): 60 sites, 20-60 devices each (about 2,400 devices); 20% of sites are "bad-hardware" sites where 70% of devices carry the faulty revision, other sites 3% (overall about 16%); maintenance windows every 30 days (70% of sites) or 90 days with random phase; hold-down 7 days; waves of 3/12/30/55% of sites 21 days apart; 15% of sites suffer a partition of 20-120 days; 3 sites are permanent islands (never reached); fault: 70% immediate, 30% latent (14 days); rollback success 85%; report delay 1 day; halt at 5% failure among at least 15 reported activations; 300 runs per strategy (seeds 0-299).

**Faulty update** (blast radius = devices left out of service after rollback attempts; "transient" = rolled back to last-known-good):

| Strategy | Mean % out | p95 % | Max % | Mean site outages | Transient % | P(halt) | Halt day |
|---|---|---|---|---|---|---|---|
| A big-bang, no halt | 2.32 | 3.34 | 3.96 | 0.01 | 13.12 | 0.00 | none |
| B staged waves, no halt | 2.31 | 3.30 | 3.91 | 0.03 | 13.14 | 0.00 | none |
| C staged + auto-halt | 0.15 | 0.41 | 0.73 | 0.00 | 0.85 | 1.00 | 31.8 |
| D C + 5% persisters | 0.13 | 0.37 | 0.64 | 0.00 | 0.79 | 1.00 | 31.5 |
| E D + activation lease 45 d | 0.13 | 0.37 | 0.64 | 0.00 | 0.79 | 1.00 | 31.5 |
| F E + stratified canary | 0.15 | 0.33 | 0.54 | 0.00 | 0.85 | 1.00 | 25.9 |

**Good update** (cost of caution; exposure = unmigrated device-years per device over one year, 5% unreachable island devices dominate the floor):

| Strategy | Migrated % by day 365 | Exposure (device-years per device) | False halts |
|---|---|---|---|
| A big-bang | 95.0 | 0.131 | 0.00 |
| B/C staged | 95.0 | 0.264 | 0.00 |
| D/E/F (persisters) | 94.5 | 0.272 | 0.00 |

**Stress** (fault in 100% of devices at bad sites, rollback 50%, report delay 10 days, 70% latent):

| Strategy | Mean % out | p95 % | Sites fully lost | P(halt) |
|---|---|---|---|---|
| A big-bang | 10.58 | 14.93 | 0.00 | 0.00 |
| B staged, no halt | 10.58 | 14.82 | 0.00 | 0.00 |
| C staged + halt | 1.47 | 4.18 | 0.00 | 1.00 |
| D + persisters | 1.35 | 3.86 | 0.00 | 1.00 |
| F + stratified canary | 1.14 | 2.97 | 0.00 | 1.00 |

### F.6.3 What the twin tells us [C, model-bound]

1. **Staging without a halt is worth nothing against a fault that is not self-limiting.** B equals A (2.31% vs 2.32%). The stagger only buys time; the halt spends it. Cohort staggering therefore must be coupled to a *reporting path and a halt rule*, or it is theatre.
2. **Auto-halt gives a ~15x reduction** (2.31% to 0.15%; stress: 10.58% to 1.47%, about 7x).
3. **Persisters help modestly here** (0.15 to 0.13; stress 1.47 to 1.35), roughly proportional to p (5%) plus latent effects; they do *not* show a distinctive benefit in this model because the halt contains the damage first. The model's "site fully lost" metric stayed at zero in every strategy, so persisters' redundancy value is *not demonstrated*. Atlas claim of persisters as bet-hedging is plausible [I] but unproven by this twin; E-series experiment needed with a model where redundancy within a site matters (see F.9).
4. **Stratified canary** (inventory-aware: one canary per hardware stratum) halted ~6 days earlier (25.9 vs 31.5) and cut p95 in the stress case from 3.86% to 2.97%. Inventory quality directly buys safety.
5. **Activation lease** (site must have heard the controller within 45 days) made no difference *here* because partitions rarely overlapped the critical window. Its value is for the case where a halt cannot reach an offline site holding a staged bundle; under these parameters that case is rare. Keep as optional policy with the cost of delay (not observed in this run after fixing the heard-time bookkeeping: 94.5% migrated).
6. **Caution costs exposure**: staged rollout doubles exposure-years in the good-update case (0.131 to 0.264) for this schedule [C]. This is the direct trade between blast radius and exposure that F.7's planner optimises.

Limitations of the prototype: no device-level correlation beyond hardware revision; reports are all-or-nothing with fixed delay; wave order is random (class ordering not implemented, see F.7); no operator behaviour (skipped windows); fault effects are binary; persisters never fail; partition model independent per site. These are conservative or arbitrary in unknown directions; sensitivity sweeps are future work.

---

## F.7 Migration planner

### F.7.1 Inputs and outputs

Inputs: inventory `devices[]` (id, class C0-C5, site, hw rev, firmware, algorithms, updatable flag), `trust_edges[]` (src, dst, credential type, direction, forgeable-by-CRQC flag), `windows[]` (site calendar, epoch), `constraints` (class rules, e.g., C3 only after recertification path; budget per window), `knowledge_level` (full graph, class only, none).

Trust graph source: passive inference (F.4.7) plus configuration import (OPC UA GDS trust lists, PKI issuances, KDC membership, vendor remote-access accounts). Edges inferred from observation carry `confidence`.

Outputs: `plan` = ordered list of `(device or group, action, window epoch)`, predicted blast radius curve, predicted exposure-years series, list of keystone nodes, and unresolved unknowns.

### F.7.2 Algorithms (from atlas M1 [C, atlas])

| Algorithm | Knowledge | Atlas M1 result: fraction to migrate for blast radius <= 5% | Use |
|---|---|---|---|
| Random | none | 73% (67-82%) | baseline only |
| Acquaintance | local observation | 44% (38-50%) | when no inventory but passive flows exist |
| **Class-ordered** (C5 -> C4 -> C3 -> C2 -> C1 -> C0) | class only | 10% (9-11%) | **default** |
| Hub-first (degree, recomputed) | full trust graph | 6% | when graph is good |

On the scale-free control the numbers were 79%, 44% and 16% (random, acquaintance, degree-targeted) [C, atlas]. The planner implements all four plus a hybrid: class-ordered with ties broken by recomputed degree, constrained by windows and budget.

```python
# planner/core.py (spec)
def plan(inv: Inventory, graph: TrustGraph, windows: Calendar, knowledge: Knowledge,
         budget: Budget, policy: Policy) -> Plan:
    order = {Knowledge.FULL: hub_first, Knowledge.CLASS: class_ordered,
             Knowledge.NONE: acquaintance}[knowledge](inv, graph)
    if policy.hybrid:
        order = sorted(order, key=lambda d: (class_rank(d), -graph.degree(d, recomputed=True)))
    plan = pack_into_windows(order, windows, budget, constraints=policy.class_rules)
    return annotate(plan, blast_radius_curve(plan, graph), exposure_years(plan, inv, graph))

def acquaintance(inv, graph_observed):
    while remaining:
        x = rng.choice(remaining)                       # random node
        n = rng.choice(observed_neighbours(x))          # something it talks to/trusts
        yield n                                         # migrate the neighbour
```

DECISION: default to class-ordered with degree tie-breaks; fall back to acquaintance when the inventory is incomplete; always schedule keystones (workstations, vendor remote-access portals, PKI, KDC, gateways) first (atlas 12.4). WHY: M1: ~11% of nodes (all C4/C5) cut the worst-case blast radius from 100% to 4.5%. ALTERNATIVES REJECTED: percent-migrated metric as steering (leaves a residual; integrates nothing); random order. ASSUMPTIONS: class assignment correlates with hubness (true in M1's synthetic Purdue topology, unverified in real plants: E-N4). TRADE-OFFS: order by class may conflict with windows (C3 safety devices wait for recertification). LIMITS: synthetic topology, undirected unweighted edges. HOW WE VALIDATE: replay the planner on an anonymised real graph (atlas E-N4) and on the twin (F.6).

### F.7.3 Exposure-years calculator

See F.3.3. Interface:

```
exposure_years(plan, inventory, graph, scenarios, T_dist, horizon) -> {
   series: [(epoch, EY_cum, exposed_frac, blast_radius)],
   per_site: [...], per_class: [...], assumptions_used: [...] }
```

Defaults: scenario set = {ECDLP broken, ECDLP+MLWE, ECDLP+SHA-256, ...}, T distribution given by the operator (e.g., uniform 2030-2040 as in atlas 11.10; not a forecast).

---

## F.8 Failure modes and recovery for the fleet plane

| Failure | Impact | Prevention / detection | Recovery |
|---|---|---|---|
| **Compromised site KDC** (C4) | Attacker reads/forges group keys for that site's groups; cannot sign firmware or ledger statements | Per-device diversification from site secret only; KDC never holds authority keys; role-mismatch alerts; two vendors | Rotate `DS_site` at FDA (offline), re-enrol devices (ML-KEM), site sub-ledger `CEREMONY` + `LIFECYCLE`; sector isolation limits scope |
| **Compromised FDA / diversification root** | All sites' derived keys at risk | Offline HSM, split custody, never networked (invariant 4) | Fleet re-keying campaign; plan expects this as a drill (I-series: "prescribed burn") |
| **Compromised single authority key** | Cannot produce valid quorum alone | Disjoint-assumption quorum; PAM rule; drills | `SLOT_REPLACE` using the other class; if both lost: out-of-band physical re-commissioning (known hard boundary) |
| **Same-waist double compromise** (e.g., Keccak break) | Quorum rule 1 rejects same-class pairs | `assumption_registry` update via signed statement | Replace affected slots using the other class |
| **Collusion of two custody domains** | Valid quorum forged | Independent orgs and HSM vendors; witness cosigning detects unlogged statements | Out of scope for crypto; contractual/legal; ledger gives evidence |
| **Split brain (island vs fleet)** | Two competing authority chains | Island authority limited to site scope; fork = two statements with same `prev`; witnesses | `CONFLICT` freeze, quorum `RESOLVE` (F.1.4) |
| **Log operator misbehaviour / split view** | Different histories to different relying parties | Witness cosigning; relying-party verifiers re-check policy | Switch log; checkpoint cosignature gaps flagged; ledger is re-hostable from statements |
| **Rollback attack** (old statements/bundles replayed, old floor) | Device accepts old authority or vulnerable image | Device holds monotonic floor; manifests carry sequence; ledger consistency proofs; TUF-like snapshot version | Device rejects; operator alerts when a gateway presents lower `floor` |
| **Replay of activation order/halt** | Wrong cohort activated or order resurrected | Per-order nonce plus `bundle_hash` plus `seq`; orders bound to cohort | Reject duplicates; log |
| **Stale spares** (dormant slot never exercised) | Slot fails when needed | Annual `DRILL` statements, evidence flagged if overdue | Rehearsal, replace slot using the other class |
| **Halt cannot reach offline site** | Staged bundle activates despite known fault | Activation lease (optional); site-scoped order expiry in epochs | Operator sneakernet `HALT` bundle; twin simulation ahead of time |
| **Faulty update with silent latent failure** | Detected late | Soak period; persisters; latent-aware halt window | Rollback, hold persisters |
| **Evidence archive algorithm aging** | Old proofs become unverifiable | Renewal scheduler (F.3.5) | Re-timestamp, renew hash trees |
| **Time source attack on gateways** | Wrong epoch, early expiry exceptions | Epoch only tightens; monotonic maximum | Reset by signed config |
| **Voucher theft** (N7) | Attacker redeems ownership | HSM vault, ledger-logged `VOUCHER_REDEEM`, two-party redemption | Revoke voucher artefact (permitted by PAM rule: it is an artefact) |

Sequence diagrams:

**Authority change (floor advance)**
```
Operator     Coordinator        A1(HSM,vendor1)  A2(HSM,vendor2)   TransparencyService   Witnesses   Device/Gateway
   | request     |                    |                 |                    |                |            |
   |------------>| propose P          |                 |                    |                |            |
   |             |------------------->| validate vs head+policy               |                |            |
   |             |---------------------------------->| validate               |                |            |
   |             |<--- sig(ML-DSA) ---|                 |                    |                |            |
   |             |<------------------ sig(LMS, index reserved in HSM) ------|                |            |
   |             | check rule 1 (disjoint)                                  |                |            |
   |             |------------------------------------------------------------------------>| register   |
   |             |                                                          | verify rules 1-6           |
   |             |                                                          |--- checkpoint ------------>| cosign
   |             |<---------------- receipt (inclusion + cosigned checkpoint) |<---------------|            |
   |             | distribute statement+receipt (or sneakernet bundle) ------------------------------------>| verify, store dormant
```

**Dormant stage then activate, with halt**
```
Release     Controller        Site gateway        Device                Watcher
  |  bundle  |                    |                  |                      |
  |--------->| wave k release     |                  |                      |
  |          |------------------->| deliver bundle   |                      |
  |          |                    |----------------->| verify, STAGED_DORMANT
  |          | ACTIVATION_ORDER (quorum) cohort k    |                      |
  |          |------------------->| order stored     |                      |
  |          |                    |  [window opens]  |                      |
  |          |                    |----------------->| activate, self-test  |
  |          |<--- signed report (EAT) --------------|--------------------->| observe
  |          | failure rate >= threshold? ---------->|                      |
  |          |<-------------------------------------------- HALT (single signer, independent) 
  |          |--- HALT statement -->| order revoked   |                      |
  |          |                    |  (unreached offline sites: sneakernet HALT)
```

**KDC enrolment and group rekey**
```
Device              Site KDC (C4)                HSM / FDA(offline)
  |  ek (1184B) ------->|                                 |
  |<-- ct (1088B) ------| derive K_enrol, K_dev           |
  |  bind identity       |<--- DS_site (provisioned once) -|
  |...periodic epoch...  |
  |<- AEAD-wrap(GK_e+1, K_dev) (~68B/member) --|  (overlap: GK_e and GK_e+1 both valid)
```

---

## F.9 Open issues and atlas challenges

1. **Persister value is unproven by the twin** (F.6.3 item 3). Experiment needed: model within-site redundancy and fault homogeneity where losing all non-persisters means losing the site. Until then, treat p=5% as [H].
2. **M1's acquaintance rule depends on observation.** It needs *some* neighbour discovery (passive flows). In a plant with truly no visibility it is not "inventory-free". Link F.4.7 as a prerequisite.
3. **FDO PQ** is not defined by FIDO as of v2.0 (2 Apr 2026) [F]; atlas Part 0 item 4 is correct that it must be built, but the voucher PQ profile is *ours to propose*, not an existing standard. Appendix B of PS v2.0 was not read; re-check.
4. **SUIT PQ profile** (hash-based and SLH-DSA in COSE): I found RFC 9964 (ML-DSA in COSE) but not a SUIT-specific PQ document; unverified.
5. **Unverified this session:** OPC UA PQ roadmap (primary), DNP3-SA v7, IEC 60870-5-7, Modbus Security, MQTT Sparkplug PQ posture, CBOM version, PKCS#11 3.2 final status, KMIP 3.0 final status, TPM v1.85 publication status. These are listed so another stream or a follow-up does not assume them.
6. **Witness PQ**: no primary evidence that Tessera/C2SP define PQ checkpoint signatures; our profile is a proposal [H].
7. **Assumption registry governance**: who updates the dependency table (the "conservative model") and how a device learns of it. Proposal: statements `REGISTRY_UPDATE` signed by a disjoint quorum; devices embed a baseline table in the first stage.
8. **Twin calibration**: no real rollout logs to back-test; parameters are assumptions.

## F.10 Traceability

| Section | Atlas IDs served |
|---|---|
| F.1 ledger, quorum, offline | R3, R6, R7, R9, R10; N1-N8, N41, N51, N52, N61, N64; M2, M3, M4; I-series PAM, stop signals |
| F.2 update and staging | R8, R9; N13, N14, N15, N47, N48, N7; atlas 11.4-11.5 |
| F.3 evidence | R7; N31, N32, N35; M5; atlas 11.7 |
| F.4 symmetric fabric | R4, R5; P19, P20, N10, N38, N43; atlas 11.3, E4 |
| F.5 enclave | N43; atlas 11.6, 11.8; I-9 exit clocks |
| F.6 twin | atlas 11.5 "migration twin"; M1, M5 |
| F.7 planner | R7; M1, M5, M6; atlas 12.4 |
| F.8 failure modes | R2, R6, R10; atlas 7.3 and Part 11.4 |

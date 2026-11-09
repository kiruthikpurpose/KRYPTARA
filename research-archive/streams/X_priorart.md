# X. Prior art, citation check, cross-domain transfer, overlooked technology

Scope and method. About 30 tool calls on 2026-11-06: web searches and page fetches, plus a grep of the project's own materials. Labels follow BRIEF.md. "Seen" means I fetched the page or saw it in a search result this session. Items I know only from memory are marked **[I, memory, not fetched]** and must be checked before they go into a bibliography. Some sites refused fetches (dblp, Crossref, PMC). Where that blocked a detail, I say so.

## X.1 Bottom line

1. Each of (a) to (f) has close prior art as a part. The nearest are TUF/Uptane (threshold roles, chained root rotation, rollback counters), SCITT/CT (append-only logs with receipts), and secret-sharing theory (monotone access structures). Fault-tree minimal cut sets are the nearest analogue for the order-≥2 rule (c).
2. A modest claim that survives my searches: **the composition is unclaimed**. I mean one on-device artefact that does all of the following together:
   - It holds a monotone policy as a fixed-size truth table.
   - It checks single-fault safety and tighten-only locally.
   - It models cryptographic assumptions and key custody as the same kind of corruptible party.
   - It sits on a monotone floor/retire/sovereign state with a replayable log.
   - Its immutable root needs only a one-way function.

   "Not found in my searches" is a weaker statement than "does not exist". I did not search patents, IEC 61508 or Common Criteria texts, or the full TCG/OpenTitan documentation.
3. The most important new fact is in section X.5: threshold and distributed hash-based signing is no longer absent. The sources are one peer-reviewed paper (2025) and two ePrints (September and October 2026). Several project statements treat it as "research, not an engineering option" or "speculative". That needs rewording, though the practical caveats are real.
4. Hirt-Maurer is confirmed (X.3), with one detail still to check (volume and pages).

## X.2 Closest prior art per component

Legend for the "Gap" column: what I could not find in the cited work.

### (a) Monotone authority state (floor / retire / sovereign)

| Prior art | What it does | Source status | Gap versus ours |
|---|---|---|---|
| TUF spec 1.0.37, last modified 8 Oct 2026 | Clients never accept a lower metadata version. Root versions must go up by exactly one. Expiry gives freeze protection. | [F] fetched: theupdateframework.github.io/specification/latest | Versions are per-file counters. There is no cross-slot "floor" over key classes and no one-way retire/sovereign lifecycle. The expiry is wall-clock based. |
| Uptane standard 2.1.0 | Adds a release counter in custom metadata so rollback is blocked even if the Director is compromised. Adds nonces and time in ECU reports. | [F] fetched: uptane.org/papers/uptane-standard.2.1.0.pdf | The counter covers image rollback, not a monotone *authority* state. |
| Monotonic counters in secure elements, ROM anti-rollback fuses | Physical one-way state. | **[I, memory]**. Product-specific, not fetched. | Typically a single image-version counter, not a lifecycle lattice. |
| CRDT / semilattice state (Shapiro et al. 2011) | Monotone state that merges without coordination. | **[I, memory, not fetched]** | We use the idea (state only moves up, so replay is order-tolerant). I found no CRDT work applied to device trust roots. |
| Blockchain upgrade timelocks, e.g. OpenZeppelin TimelockController | A delay between proposal and execution, with roles for proposer, executor and canceller. | [F] seen in search results (GitHub links) but **not fetched**; role details are **[I, memory]** | Related to staged activation (f). The mechanism is on-chain and assumes a global consensus clock. |

### (b) Policy as a monotone Boolean function over key slots, checked on device

| Prior art | What it does | Source status | Gap |
|---|---|---|---|
| Benaloh and Leichter, "Generalized Secret Sharing and Monotone Functions", Crypto '88 | Secret sharing for any access structure expressed as a monotone function. | [F] fetched (Microsoft Research page; the Crypto '88 venue is on the page, the year is inferred from the name) | This is the theoretical home of "monotone Boolean function as authority". It is not about verifying a policy encoding on a constrained device. |
| Ito, Saito and Nishizeki 1987, monotone access structures | General access structures. | **[I, memory]**. The search returned a DOI, 10.1007/BF02620229, but I did not open it, so I cannot confirm that it is this paper. | Same. |
| TUF and Uptane thresholds | Per-role "k of n" with a keyid-uniqueness rule (one signature per keyid counts). | [F] fetched | Only threshold policies. Uptane gets "AND of two repositories" by requiring Director and Image metadata to agree. This is a fixed AND of two thresholds, not a general monotone function. |
| TUF delegations | Ordered, path-scoped delegation chains. A target must be allowed by every role in the chain. | [F] fetched | This is a fixed AND/priority structure, not a function over slots. |
| 256-bit truth table encoding | I found nothing like it. | not found in my searches | Plausibly an unclaimed *encoding*. An 8-input function has 2^8 = 256 truth-table bits [C, arithmetic]. The idea of a table is trivial. The claim is only the on-device single-fault and tighten-only validation of it. |

Observation [I]. With a truth table `f` over 8 slots, "no single slot authorises" is 8 lookups (`f(e_i) = 0`). "Tighten-only" is bitwise: `f_new ≤ f_old` for the same set of authorised inputs, so `f_new & ~f_old == 0`. Both checks are O(32 bytes), which fits a locked-stage verifier. Monotonicity itself is a check over the 8 × 128 single-bit-flip edges of the cube. This lets the device refuse a malformed policy rather than trust the compiler.

### (c) Parties = assumptions + custody groups in a general adversary structure; no single corruptible set authorised

| Prior art | Relevance | Source status |
|---|---|---|
| Hirt and Maurer, general adversary structures | Defines the adversary as a monotone family of corruptible sets rather than a threshold. | [F] confirmed to exist, see X.3 |
| Fault tree analysis, minimal cut sets, hardware fault tolerance (HFT) in IEC 61508 | A minimal cut set of order 1 is a single point of failure. HFT ≥ 1 is the requirement that no single fault defeats the safety function. | **[I, memory, not fetched]**. No clause numbers; the project's own appendix also says it did not fetch IEC clauses. |
| Attack trees (Schneier) | Tree of attacker goals with AND/OR nodes. | **[I, memory, not fetched]** |
| Minimal hitting sets / transversals | A minimal cut set is a minimal transversal of the minimal path sets. | [I] (standard duality, no source needed beyond the definition) |
| Diverse redundancy and common-cause failure (beta-factor, IEC 61508 practice) | The safety-engineering name for "two keys that share a hidden dependency are not independent". | **[I, memory]** |

What I could not find: a source that treats *cryptographic assumptions* (for example "SHA-2 is collision resistant") and *key-custody groups* as one uniform set of corruptible parties, and that then requires order ≥ 2 for authority changes. I did not search for it exhaustively. The nearest I can name are common-cause analysis in safety engineering and the "Q^2/Q^3" style conditions on adversary structures [I]. The two worlds exist side by side. I did not find the join.

Precise mapping [I]. Let the policy be monotone `f` over slots. Let the adversary structure Z be the family of sets of parties that the model deems simultaneously corruptible by one event. Each party p disables or corrupts a set of slots `S(p)`. The safety property is: for every Z in the structure, `f(∪_{p∈Z} S(p)) = 0`. With Z = all single parties, this is the "minimal cut-set order ≥ 2" condition. With a richer Z, such as "any one custody group, or any one assumption", it is the Hirt-Maurer-style "no corruptible set is authorised" condition. In secret-sharing language, Z is the adversary structure and `f` is the access structure, and the requirement is `Z ∩ Access = ∅`. This is the standard compatibility condition. The new use is in key governance, not the mathematics.

### (d) Hash-chained, append-only transition log; any party replays trust state; stale devices catch up

| Prior art | What it gives | Source status | Gap |
|---|---|---|---|
| TUF root chain | Clients walk root versions one at a time (`N.root.json`). A stale client can follow many rotations if each is signed by a threshold of the old and new keys. | [F] fetched | This is the closest existing "catch up by replay" for trust roots. The log carries only root metadata, and the signing rule is threshold-only. |
| SCITT, RFC 9943 (June 2026, Standards Track) | Append-only log of signed statements. Receipts prove inclusion. | [F] fetched | The RFC requires inclusion proofs, but consistency proofs are optional, and it requires no signed checkpoint. A device-trust log that needs replay should *add* consistency or a hash chain. This is a place where we are stricter, not novel. Receipts are COSE Single Signer objects defined in RFC 9942, per the RFC 9943 text I fetched. |
| Certificate Transparency | Merkle log with consistency proofs. | **[I, memory]**. Not fetched; the RFC number (9162) is also memory, so check it. | CT assumes online monitors and gossip. |
| Authenticated data structures (Tamassia, Merkle trees) | Authenticated state with succinct proofs. | **[I, memory]** | Our state is a few hundred bytes, so a chain is enough. A Merkle structure only matters if devices must verify a *subset*. |
| Sigstore root-signing | A TUF root signing ceremony with a key-holder threshold. | Repository `sigstore/root-signing` is [seen in search results, not fetched]. | Uses TUF thresholds, with human key holders. |

### (e) Immutable root needs only a one-way function

| Prior art | Source status |
|---|---|
| Lamport one-time signatures (1979); Naor-Yung (1989) universal one-way hash functions imply signatures; Rompel (1990) one-way functions imply signatures | **[I, memory, not fetched]**. Treat the exact dates as unverified. |
| LMS/HSS (RFC 8554) and XMSS (RFC 8391) stateful hash-based signatures; NIST SP 800-208, published 29 Oct 2020 | SP 800-208 date [F] fetched from csrc.nist.gov news page. RFC numbers are mentioned on the NIST page (RFC 8391 for XMSS) and in the RFC 9858 text I fetched (RFC 8554). |
| RFC 9858, "Additional Parameter Sets for HSS/LMS", October 2025, Informational (IRTF/CFRG), by Fluhrer and Dang | [F] fetched. The RFC says it is a research document and not ready for production. |
| SUIT algorithm draft (`draft-ietf-suit-mti-23`, 22 July 2025) | [F] fetched. It makes HSS/LMS a recipient "RECOMMENDED" profile. It does not mention ML-DSA. It had expired on 23 Jan 2026 as an individual version, and I did not check for a later revision. |

Gap. The theory that "signatures need only a one-way function" is old. What is not common is the *engineering consequence* of making the immutable root rely on nothing else, together with the physical-monotonicity requirement. I did not find that argument written down for device roots. Hash-based locked boot stages in vendor silicon exist (see X.6), but the vendors do not, in what I fetched, frame the root around "one-way function plus physical monotonicity only".

### (f) Staged activation with a scoped one-signer halt

| Prior art | Relevance | Source status |
|---|---|---|
| Uptane/TUF expiry and role separation | Timestamp-style freshness. | [F] fetched |
| Blockchain timelocks and guardian/canceller roles | A delay with one party able to cancel. | **[I, memory]** for the canceller detail; the TimelockController source was seen as a link only. |
| Two-person integrity, nuclear Permissive Action Links, aviation dual authorisation | Two-party control for *enabling*. Fail-safe actions can often be single-party. | **[I, memory]**. I did not fetch any source on these. I cannot give PAL details and have not tried. |
| CCSDS Space Data Link Security (SDLS) | Authentication and encryption of spacecraft links. | Search returned ESA and NASA papers; I did **not** read them. The existence of SDLS and of ESA work on quantum-safe satellite links is visible in the result titles only. |

Asymmetry principle [I]. "Any one signer may stop; two must start" is a common safety pattern (an emergency stop is easier than a start). I found no source that scopes it to a bundle and gives it an expiry. The scoping is a design detail; I would not call it novel.

### X.2.1 Key-insulated, forward-secure and evolving signatures

Bellare-Miner forward-secure signatures (1999) and Dodis-Katz-Xu-Yung key-insulated signatures (2002) are from memory **[I, not fetched]**. Their relevance is that they also make the signing key *evolve* so that earlier keys cannot be recovered. Our floor is a different object: it advances the *verifier's* acceptance set, not the signer's key. The two compose, since a signer could use a forward-secure scheme while the device enforces a floor. I found no work that links them.

## X.3 The Hirt-Maurer citation

**Confirmed (two independent routes):**
- The dblp record key `journals/joc/HirtM00` appeared in a search result, with the title "Player Simulation and General Adversary Structures in Perfect Multiparty Computation".
- A Springer Professional page, fetched, gives: authors Martin Hirt and Ueli Maurer; *Journal of Cryptology*, issue 1 of 2000; DOI `10.1007/s001459910003`. The page did not give a volume or page range.

**Recommended citation:**
> M. Hirt and U. Maurer, "Player Simulation and General Adversary Structures in Perfect Multiparty Computation," *Journal of Cryptology*, 2000, issue 1, DOI 10.1007/s001459910003.

**Still unverified:** the volume (13) and pages (31 to 60) are from my memory and should be checked against the DOI landing page. Crossref and dblp could not be reached from this sandbox.

**The earlier conference version.** A dblp key `conf/podc/HirtM97` appeared in a search result for the title "Complete characterization of adversaries tolerable in secure multi-party computation" (PODC 1997). I did not open that record, so the pages and publisher are unverified. I would cite it as "PODC 1997" only, and only after checking.

**Naming caution.** The "Q^2" and "Q^3" conditions on adversary structures are from Hirt and Maurer's work and its follow-ups **[I, memory]**. I did not re-read the paper. Do not attribute exact bounds without checking the paper. The claim in section X.2(c), `Z ∩ Access = ∅`, is a generic compatibility statement that I derived from definitions. It is not a theorem quoted from Hirt-Maurer.

## X.4 What is not already done (modest novelty statement)

Safe to say, as claims restricted to what I searched:

1. **Not found:** a device-side policy language that is a *fixed-size monotone truth table*, together with a *device-side* checker for single-fault safety and tighten-only on update. TUF, Uptane and SUIT use thresholds, delegations and counters. None of them, in what I fetched, expresses a general monotone function.
2. **Not found:** a single model in which cryptographic assumptions and key-custody groups are both "parties" in one adversary structure and the order ≥ 2 requirement is applied over both. Safety engineering has common-cause analysis; cryptography has adversary structures. The project joins them.
3. **Not found:** monotone authority state with sovereign exit that is *replayable from a hash-chained log by third parties* and consumed by stale devices. TUF's root chain is the nearest, and it covers the replay half only.
4. **Not found:** an argument that the immutable root should be restricted to a one-way function and physical monotonicity, framed as a design rule for device governance.

Not safe to say:

- "First" threshold or multi-party control of device roots (TUF, Sigstore and Uptane already do thresholds).
- "First" append-only log for trust (SCITT and CT).
- Novel use of hash-based signatures for boot (vendor and standards prior art, X.6).
- Novel mathematics. The property is the compatibility of an access structure with an adversary structure, which is textbook.

The project's own Final Blueprint ledger (section 10) already says the custody-group rule is "not proven novel; not patent-cleared". My findings support that wording. They do not support anything stronger. They also suggest that the κ checker is a re-derivation of minimal cut sets (see X.7).

## X.5 Cross-domain transfer

The common problem is: a long-lived artefact whose *rules of change* must outlive its algorithms and its keyholders.

| # | Domain | Authority object | Existing mechanism | What the calculus would add |
|---|---|---|---|---|
| 1 | Satellites and space systems | Command authentication keys and the authority to re-key or patch on orbit | CCSDS SDLS for link security (existence seen only in search-result titles); ESA/NASA key-management papers appeared in results but were not read | A one-way-function root that survives a re-keying gap with no contact for years; monotone "retire" for compromised ground stations; a one-signer halt scoped to a command bundle |
| 2 | Implantable and other medical devices | Programmer/clinic authority; manufacturer service authority | **[I]** Vendor-specific; I did not research this | Dual custody between maker and clinic, with patient-side or regulator-side exit (sovereign) when the maker disappears |
| 3 | Vehicles | Software update authority for ECUs over 15 to 20 years | Uptane 2.1.0 [F]: threshold roles, Director plus Image repositories, release counters | A general monotone policy instead of two fixed repositories; a replayable log for ECUs that were offline for years; an explicit order ≥ 2 check over repositories and algorithms |
| 4 | Software package registries | Publisher-key and maintainer-set authority | TUF [F]; Sigstore root-signing (seen, not fetched); SCITT RFC 9943 [F] | Tighten-only policy changes; checking that two "independent" maintainers do not share an upstream assumption |
| 5 | Long-term digital archives | Authenticity of preserved records over centuries | Glass media claims exist (see X.6). Archival timestamping practice is **[I]** and not researched | A one-way-function root plus a hash-chained transition log is the natural fit when no party stays online. The media do not change the authority question |
| 6 | Legal and financial instruments | Who may amend or revoke a mandate or beneficial-ownership record | Multi-signature controls and notarial practice **[I]** | Monotone amendment (tighten-only); exit for the owner when the custodian fails |
| 7 | Smart meters and utility metering | Utility key and firmware authority across 15-year meter lives | **[I]** Not researched | Same as vehicles. Heavily constrained devices make the 256-bit table and hash-only root attractive |
| 8 | Autonomous machines and AI agents | Authority to change an agent's configuration, tools or permissions | **[I]** Not researched | Monotone "permissions only tighten without sovereign sign-off", two-party loosening, and a one-signer halt. This is the same pattern with different parties |

Caveat [I]. Rows 2, 5, 6, 7 and 8 are by analogy. I did not verify what the existing regimes in those domains do. Before writing any of them into a plan, someone should check each against actual regulation and standards.

## X.6 Technology from the last two years that could change direction

Only items I verified. "Verified" means the page said it. Several are vendor statements.

1. **Threshold and distributed hash-based signatures (material).**
   - Kelsey, Lang and Lucks, "Turning Hash-Based Signatures into Distributed Signatures and Threshold Signatures", *Communications in Cryptology* vol. 2 no. 2, article 24, 7 July 2025 [F, fetched]. It builds a threshold or distributed signer on LMS/XMSS. It needs a trusted dealer, a reference value of several GiB held by an aggregator, and two round trips per trustee. Security is reduced to the base scheme plus a PRF. The paper says a dishonest aggregator can block signing but cannot forge.
   - "PRAWNS: Threshold Hash-Based Signatures from Threshold PRFs" (Boneh, Bünz and co-authors), ePrint 2026/2142, 21 Sep 2026 [F, fetched; preprint, not peer reviewed]. Output looks like an ordinary signature. Parties and thresholds can change without changing the public key. The abstract states no efficient distributed key generation and no direct fit for SLH-DSA.
   - Cheon, Choi, Joo and Kim, "One-Round Threshold XMSS and SPHINCS+ from FHE", ePrint 2026/2360, Oct 2026 [F, fetched; preprint]. Signatures verify under unmodified RFC 8391 and FIPS 205 verifiers. The reported time is 0.69 s for online threshold XMSS signing, on hardware the abstract does not describe.
   - Consequence [I]. The *verifier* does not change, which is what matters for the immutable root. The signing side is still heavy, needs a dealer or lacks DKG, and none of it is audited. Treat it as a candidate for an off-device signing service, not as part of the device. The project's "speculative" label on threshold universal verification (Final Blueprint section 10) and its comment that off-device multi-party signing is "research, not an engineering option" should be updated to "published, unaudited, preprint-stage for the newest work".
2. **PQ in TPM 2.0.** A wolfSSL blog post dated 5 May 2026 says the TCG TPM 2.0 Library Specification v1.85 adds ML-DSA (44, 65, 87) and ML-KEM (512, 768, 1024) [2nd/V, fetched]. The post does not say whether v1.85 is final, and I did not reach a TCG page. Check the status on tcg.org before citing.
3. **PQ secure elements (vendor claims only).** SEALSQ's 2026 roadmap release lists ML-KEM-1024 and ML-DSA-87 on its QS7001 and QVault TPM 185 [V, fetched]. It says production samples of QS7001 V1 and the QVault TPM 183 became available in March 2026. Every certification (CC, FIPS 140-3, TCG) is listed as a target. No certificate was shown. Use as a market signal only.
4. **Caliptra 2.0.** A CHIPS Alliance DAC 2025 deck says Caliptra 2.0 has PQC-capable DICE/DPE, ML-DSA support (via the Adams Bridge integration), and an LMS verification primitive on the roadmap [F/V, fetched]. The deck does not mention key manifests or hybrid signing. The project's list of Caliptra as prior art for "hash-based locked stage with key-hash slots" is therefore **not confirmed by what I read**. Check the Caliptra and OpenTitan documents directly.
5. **OpenTitan.** ePrint 2024/1192 "Towards ML-KEM & ML-DSA on OpenTitan" appeared in search results [seen, not read]. Do not cite beyond its existence.
6. **COSE/JOSE ML-DSA.** `draft-ietf-cose-dilithium` was announced as approved for Proposed Standard by the IESG on 15 Oct 2025 [F, fetched announcement]. I did not confirm an RFC number. The earlier draft (-06) registers COSE algorithm values -48, -49, -50 for the three ML-DSA sets, and defines an AKP key type [F, fetched, but the numbers may have changed after -06]. This removes one blocker for PQ in SUIT, but `draft-ietf-suit-mti-23` still has no ML-DSA profile.
7. **CHERI on small cores.** The CHERI Alliance page for CHERIoT lists `cheriot-ibex`, a 32-bit RISC-V core implementing CHERIoT 1.0, certification date 26 March 2026, with formal proofs reported, and cites a VeriCHERI paper (ICCAD 2025) [F/V, fetched]. The page does not say whether silicon ships. A press item on a "first CHERIoT commercial tapeout" appeared in search results [seen, not read]. Relevance [I]: memory safety for the *rest* of the device helps keep a compromise of the application from reaching the authority code. It does not change the root design.
8. **Hash-based signature standards.** I could not confirm that NIST SP 800-230 exists as a draft. The NIST HBS news page says a revision of SP 800-208 that "would enable key export" is under way. No date was given. I did not find a verified draft number. Keep any mention of SP 800-230 labelled "unverified". RFC 9858 is verified (above).
9. **FIDO.** A FIDO Authenticator Allowed Cryptography List v1.7 (RD 20260506) appeared in search results [seen, not read]. I cannot report whether it covers PQ algorithms. No further claim.
10. **Long-lived media.** Multiple news items say Microsoft's Project Silica writes data in glass with a claimed 10,000-year life [2nd, search results only]; the PMC article I tried was blocked, so I could not check what is measured and what is extrapolated. Treat the lifetime as an accelerated-ageing extrapolation until read **[I]**. Direction impact: media longevity makes the *authority* problem more pressing (the data outlives the keys) and does not change the design.
11. **Not found / no result:** a verified PQC profile for Uptane, a verified EAL certificate for any PQ secure element, and a verified threshold hash-based implementation on a microcontroller.

Net assessment [I]. Nothing I verified overturns the architecture. Threshold HBS (item 1) is the one development that changes the project's framing, because it makes "off-device custody of an LMS/XMSS signer by several parties" a published design instead of a hypothesis. It keeps the device-side verifier unchanged, which is the project's own position.

## X.7 Claims in the project's materials that my findings contradict or weaken

Checked by grep in the Atlas, Master Blueprint, Final Blueprint and Appendices. Line numbers as of this session.

| # | Project statement | Where | Finding | Severity |
|---|---|---|---|---|
| 1 | The independent investigation was faulted because off-device multi-party signing of standard hash-based signatures "is research, not an engineering option". | Final Blueprint, verdict paragraph near line 13 | Published and peer-reviewed work now exists (Kelsey, Lang, Lucks 2025), with two 2026 preprints. Still research-grade (trusted dealer, GiB-scale state, no DKG in PRAWNS). The statement is defensible in spirit but out of date. | Medium |
| 2 | "Threshold and STARK-based universal verification: Speculative research [S]". | Final Blueprint section 10 | The threshold half is no longer purely speculative. I did not check the STARK half. | Medium |
| 3 | "TUF's online-key model does not address offline PQ root with locked flash." | Appendices L.3 conclusions, line ~3836 | The TUF spec I fetched says online keys must not be used for roles that clients ultimately trust, and expects only timestamp and mirror keys online. So TUF *does* assume offline root keys. The real gap is the PQ signature suite and the locked-flash floor, not the online-key model. | Medium |
| 4 | "Hash-based locked stage with key-hash slots: Prior art (Nordic, ST, OpenTitan, Caliptra)." | Final Blueprint section 10 | The Caliptra source I read does not mention key manifests. I did not fetch Nordic, ST or OpenTitan. "Prior art" may be correct, but is **unverified here**. | Low to medium |
| 5 | "κ hitting-set checker and the disjoint-quorum rule: Combination; model-validated only [H]." The Master Blueprint also presents the κ definition as a correction to the Atlas's "pairwise disjoint" wording. | Final Blueprint section 10; Master Blueprint lines ~271 to 273 | The κ ≥ 2 check is, in the vocabulary of fault trees, a minimal cut set order check, and in secret-sharing terms a compatibility check between an access structure and an adversary structure. It is a recognised construction and should be presented as an application, with citations (Hirt-Maurer, Benaloh-Leichter, FTA). It is not a new result. | Medium (framing) |
| 6 | The Atlas's CBOM-like artefact: "No equivalent artefact was found, but a full search has not been done." | Atlas line ~2652 | I did not search for this, so I cannot confirm or contradict it. | None |
| 7 | SCITT is listed as "established; reused". | Final Blueprint section 10 | Consistent. Note that SCITT is now RFC 9943 (June 2026, Standards Track), and that consistency proofs and signed checkpoints are optional. The project's replay requirement needs the stricter hash-chain or consistency proof, so it cannot be delegated to SCITT without an added profile. | Low |
| 8 | SUIT is "established; reused" as a PQ-capable path. | Final Blueprint section 10 | Not contradicted, but the only PQ-relevant profile in `draft-ietf-suit-mti-23` is HSS/LMS. ML-DSA is absent, and the draft I fetched had expired on 23 Jan 2026. Do not assume an ML-DSA SUIT profile. | Low |
| 9 | The Atlas and blueprints cite IEC 61508 and 62443 without clauses. | Appendices lines ~15, ~2593 | Consistent with my method. Note that my statement about HFT and minimal cut sets is also from memory. Neither side has verified the standard text. | Low |

No evidence found against: the monotone-state design, the truth-table encoding, the one-way-function root argument, or the staged-activation design. The absence of contradicting prior art means only that I did not find it in a limited search.

## X.8 Recommended follow-up (cheap, high value)

1. Check the volume and pages of the Hirt-Maurer article from the DOI landing page.
2. Read the Caliptra and OpenTitan integration/manifest documents before keeping them as prior art for key-hash slots.
3. Obtain the IEC 61508 definitions of HFT and common-cause failure from the standard, and cite them with clause numbers or drop them.
4. Fetch the TCG v1.85 status page.
5. Search patents on "monotone" access policies in firmware update and on "key-hash slots". The project has said it is not patent-cleared.
6. Read the Kelsey et al. paper's reference-value size and the PRAWNS DKG limitation in full before writing an off-device custody design on them.
7. Reword items 1, 2, 3 and 5 of X.7 in the project's text.

## X.9 Source list (seen this session)

- TUF specification 1.0.37: https://theupdateframework.github.io/specification/latest/ (fetched)
- Uptane standard 2.1.0: https://uptane.org/papers/uptane-standard.2.1.0.pdf (fetched)
- RFC 9943 SCITT architecture: https://www.rfc-editor.org/rfc/rfc9943.html (fetched)
- RFC 9858: https://www.rfc-editor.org/rfc/rfc9858 (fetched)
- NIST stateful HBS news page: https://csrc.nist.gov/Projects/stateful-hash-based-signatures/news (fetched)
- Kelsey, Lang, Lucks: https://csrc.nist.gov/pubs/journal/2025/07/turning-hash-based-signatures-into-distributed-sig/final (fetched)
- PRAWNS: https://eprint.iacr.org/2026/2142 (fetched)
- Threshold XMSS/SPHINCS+ from FHE: https://eprint.iacr.org/2026/2360 (fetched)
- Hirt-Maurer listing: https://www.springerprofessional.de/en/player-simulation-and-general-adversary-structures-in-perfect-mu/11643828 (fetched); dblp key journals/joc/HirtM00 (search result only)
- Benaloh-Leichter: https://www.microsoft.com/en-us/research/?p=151053 (fetched)
- SUIT MTI: https://datatracker.ietf.org/doc/html/draft-ietf-suit-mti (fetched)
- COSE ML-DSA IESG announcement: https://mailarchive.ietf.org/arch/msg/ietf-announce/mA8ozj_xkqAQH6OKZOM-qZ1NEYk/ (fetched); draft -06: https://www.ietf.org/archive/id/draft-ietf-cose-dilithium-06.txt (fetched)
- wolfSSL TPM v1.85 post: https://www.wolfssl.com/post-quantum-cryptography-is-coming-to-wolftpm/ (fetched)
- SEALSQ roadmap: https://www.sealsq.com/investors/news-releases/sealsq-announces-comprehensive-2026-certification-roadmap-for-qs7001-secure-element-and-qvault-tpm-product-lines (fetched, vendor)
- Caliptra DAC 2025 deck: https://www.chipsalliance.org/events/DAC_Caliptra_2025.pptx.pdf (fetched)
- CHERIoT page: https://cheri-alliance.org/cheri-enabled/cheriot/ (fetched)

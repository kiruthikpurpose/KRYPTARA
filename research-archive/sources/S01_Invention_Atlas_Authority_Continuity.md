# The Invention Atlas: Authority Continuity for OT and Embedded Post-Quantum Security

Post-quantum migration is not itself the root problem. The root problem is that industrial devices cannot accept a new authority under the failures they actually face: a new algorithm family, a new owner, or a new epoch of trust. The highest-leverage invention is a small authority-continuity kernel committed into silicon at manufacture. It uses only hash functions, commits to several algorithm families, and is paired with symmetric-first operation and threshold succession. A new PKI or a migration SaaS would be lower leverage.

## TL;DR

- **The root causes.** Seven root causes explain almost all of the 35 named problems. Four dominate:
  - trust anchors are bound to one algorithm family in immutable silicon;
  - validity depends on wall-clock time that offline devices lack;
  - authority is bound to one organisation (the OEM), with no succession;
  - public-key operations are pushed into every endpoint even where symmetric cryptography suffices.
  Fixing these four removes most migration complexity rather than managing it.
- **The best inventions.** The weighted ranking (scores out of 100) puts four ideas on top:
  - a multi-family root manifest pre-committed in OTP (84);
  - symmetric-first operation with ML-KEM-only enrolment (80);
  - a minimal ROM verifier that uses only hash functions (79);
  - time-free epoch/counter validity, tied with threshold succession escrow for OEM exit (77 each).
  LMS custody, the Mission 2 favourite, ranks 16th (65). It is useful but commoditising. NIST SP 800-208 currently requires signing in non-exporting hardware modules at FIPS 140 Level 3 or higher, so HSM vendors will bundle custody. NIST's CSRC project page also says it is "working on a revision of SP 800-208 that would enable key export, but also mitigate security concerns", which would erode the custody moat further.
- **The hard boundary.** Some devices cannot be rescued by cryptography: those whose immutable verifier speaks only a classical family and that stay offline until a cryptographically relevant quantum computer (CRQC) exists. Only physical presence, network compensation or replacement helps them. So every device shipped from now on should carry a PQ-capable, multi-family commitment. The first experiments are:
  - a hash-only first stage plus a multi-family manifest on a Cortex-M33 board, tested under power-loss fuzzing;
  - a TLA+ model of threshold succession across OEM exit.

## Evidence legend and research process log

Labels used throughout:

| Label | Meaning |
|---|---|
| [F] | Fact or primary-source statement |
| [V] | Unverified vendor claim |
| [D] | Demonstrated engineering result |
| [E] | Estimate, with arithmetic shown |
| [I] | Own inference |
| [H] | Invention hypothesis |
| [S] | Speculation |

**Step 1 — Re-verify Mission 2's foundations.**
- [F] NIST IR 8547 final was published on 27 October 2026. It deprecates all quantum-vulnerable public-key algorithms after 2030, regardless of key size, and disallows them after 2035. NIST's Andrew Regenscheid said the 2035 disallowance was not intended to apply to hybrid modes.\[1\]\[2\]
- [F] OMB M-26-15 implements the 22 June 2026 Executive Order "Securing the Nation Against Advanced Cryptographic Attacks". It sets a 2031 phase for migrating signatures on high-value assets, and agencies must submit PQC Migration Plans within 120 days.\[3\] I did not independently verify the EO number "14412" that Mission 2 cited.
- [F] Gidney (arXiv 2505.15917, 21 May 2025): RSA-2048 can be factored in under a week with fewer than one million noisy qubits.\[4\] This assumes "a gate error rate of 0.1%, a surface code cycle time of 1 microsecond, and a control system reaction time of 10 microseconds". The 2019 Gidney+Ekerå estimate was 20 million qubits.
- [F] Google Quantum AI (30 March 2026): ECDLP-256 needs ≤1,200 logical qubits with 90M Toffolis, or ≤1,450 with 70M. This runs on fewer than 500,000 physical qubits in minutes.\[5\]\[6\]
- [F] Alice & Bob (IACR ePrint 2026/2665; press release 29 October 2026):
  - RSA-2048 needs 22,593 physical cat qubits for 3.14 days. LDPC-cat codes "more than halve the qubit count, from 49,649 to 22,593".
  - The same paper gives ≤29,588 cat qubits for 61.8 minutes for ECDLP-256.
  - The headline figures "assume no bit flips during the computation". With bit flips about once an hour, "RSA 2048 needs about 45,000 qubits".
  - Marin Ivezic (PostQuantum.com) notes that the demonstrated error correction "is a distance-3 repetition code against phase flips on three data qubits, not yet below threshold".
- [D] On the RP2040, ML-DSA-44 signing has a p99 of 584.2 ms and a maximum of 1,156.8 ms over 10,000 signatures (arXiv 2603.19340).\[7\]
- Corrections to Mission 2:
  - The market components sum to $0.11B, not $0.13B.
  - Post-quantum IKEv2 needs IKE_INTERMEDIATE (RFC 9242) plus RFC 9370.

**Step 2 — Check what root-of-trust silicon can actually verify.** This turned out to be the decisive discovery.
- [F] TI's AM263P4 ROM cannot verify PQC. TI plans to put it in a secondary bootloader instead.\[8\]
- [F] OpenTitan's ROM verifies ECDSA P-256 plus optional SPHINCS+-128s. RFC #30765 flags this as non-compliant with CNSA 2.0.\[9\]
- [V] Vendors claim the following, unverified at parameter level:
  - Microchip MEC175xB: "embedded immutable post-quantum cryptography", supporting ML-KEM, ML-DSA and LMS.\[10\]\[11\]
  - NXP MCX A5: PQC hybrid secure boot in ROM.\[12\]\[13\]
  - ST STM32G5 (announced 3 November 2026): a hardware core accelerating LMS, ML-KEM, ML-DSA and SLH-DSA.\[14\]

**Step 3 — Look at how other domains handle the same problem.**
- [F] Microsoft Support (KB5062710) lists the UEFI Secure Boot 2011 expiries:
  - Microsoft Corporation KEK CA 2011 on 24 June 2026;
  - Microsoft UEFI CA 2011 on 27 June 2026;
  - Microsoft Windows Production PCA 2011 on 19 October 2026.
  The 2023 CAs replace them. Devices without the 2023 certificates still boot, but can no longer receive boot-level security updates.
- [F] CCSDS SDLS Extended Procedures use only symmetric master keys.\[15\]
- [F] Roughtime became RFC 10049 (Experimental, October 2026).\[16\]
- [F] Threshold ML-DSA became practical for small groups during 2025–2026.\[17\]\[18\]

**Step 4 — Prior-art checks.** I checked:
- Intel patents US 11405213 and US 12137169 (fast XMSS/LMS verification for secure boot);\[19\]\[20\]\[21\]
- the OCP Hardware Secure Boot specification, which already allows a "table of hashes" of public keys in eFuses;\[22\]
- KEMTLS-PDK;\[23\]
- the Aquaman transparent PQ proxy.

These downgraded several "novel" ideas to "existing technology, new application".

**Step 5 — Subagent gap-fill on hash-based verification cost.**
- [D] Campos et al. (AFRICACRYPT 2020): LMS verification (SHA-256, h=10, w=16) takes 2,658,884 cycles on a Cortex-M4 and about 1,044 B of stack. XMSS takes 13.07M cycles.\[24\]
- [D] Banegas et al. (arXiv 2106.05577): LMS verification takes 123 ms on an nRF52840 at 64 MHz, using 1,580 B of stack.\[25\]

These figures made the hash-only verifier the strongest silicon-level idea.

**Scope note.** This work rests on about 60 sources (18 searches, several fetches, one subagent), not the 500–600 sources invited. I prioritised verifying the claims the conclusions depend on. Section 13 lists where more sourcing would most change the conclusions.

## 1. The complete problem universe

**Mathematical and cryptographic**
- **P1 — Algorithm-family monoculture in anchors.** Hybrid signatures and agile libraries do not help at the immutable layer [I].
- **P2 — HNDL-to-authority.** Once classical keys can be forged, an attacker can inject a fake "successor root" into any device that has not yet moved to a PQ root. This problem has a hard deadline [I].
- **P3 — LMS/XMSS state reuse.** [F] SP 800-208 requires signing in non-exporting hardware modules at FIPS 140 Level 3 or higher, and calls these schemes "not suitable for general use". NIST says it is working on a revision that "would enable key export, but also mitigate security concerns".
- **P4 — ML-DSA rejection-sampling latency and leakage.** [D] The RP2040 study recovered iteration counts from wall-clock time alone. The authors claim no key recovery, but warn that the history of attacks on BLISS counsels caution.\[7\]
- **P5 — Hybrid downgrade.** [F] CVE-2026-2673: OpenSSL TLS 1.3 servers using DEFAULT may negotiate a weaker group than configured.\[26\]
- **P6 — Side-channel certification of PQ hardware.** [F] Independent analyses (Saarinen; Karabulut and Azarderakhsh) found leakage in the masking of the first Adams Bridge ML-DSA accelerator.\[27\]
- **P7 — Certified entropy on cold-booting MCUs.**

**Silicon and hardware**
- **P8 — Immutable ROM verifiers that cannot learn new families.**
- **P9 — Scarce OTP that competes between revocation and anti-rollback.** [F] OCP says key revocation "shall not be mixed with anti-rollback revocation OTP".\[22\]
- **P10 — RAM ceilings.** [D] In reference C, ML-DSA-44 signing needs 50.6 KB of stack, ML-DSA-87 needs 119.6 KB, and ML-KEM-512 decapsulation needs 9.4 KB.\[7\]
- **P11 — Silicon generations last 3–5 years; assets last 20–40 years.**

**Firmware and software**
- **P12 — Single-format boot chains.** An ML-DSA-87 header grows by 2,592 + 4,627 = 7,219 B.
- **P13 — Engineering project files and configurations are unsigned,** and the authority to change them sits on engineering workstations.
- **P14 — Each vendor's crypto library has its own PQ readiness.**

**Embedded infrastructure**
- **P15 — Devices without trustworthy time.**
- **P16 — Devices that can never be updated.**
- **P17 — Weak processors.** [D] On an RP2040, ECDSA P-256 verification takes 321 ms, versus 44.0 ms for ML-DSA-44.\[7\] PQ verification is often cheaper than classical; signing and RAM are the real constraints.

**Communication**
- **P18 — MTU fragmentation.** An X25519MLKEM768 ClientHello exceeds 1,500 B. On LoRaWAN EU868, an ML-KEM-768 key needs 24 frames.
- **P19 — Process-bus frames must stay symmetric.** A Sampled Values frame leaves only 208–250 µs.
- **P20 — Group keys.** [F] IEC 62351-9:2023 distributes GOOSE/SV/PTP group keys via GDOI. It discusses post-quantum crypto in Annex B.11 but mandates no PQ mechanism.\[28\]\[29\]
- **P21 — OPC UA has no PQ security policy yet.** This comes from a practitioner source and is unconfirmed.\[30\]

**Fleet and lifecycle**
- **P22 — Catch-up cost.** In a TUF-style scheme, each rotation of an ML-DSA-65 root (5 keys, threshold 3) costs about 29.8 KB [E].
- **P23 — Orphaned fleets when the OEM exits.**
- **P24 — Spares sitting on shelves with stale roots.**
- **P25 — Backups that restore old crypto state.**
- **P26 — Revocation on offline devices.**
- **P27 — Certificate expiry as an authority cliff.** [F] Microsoft-trusting devices left without the 2023 certificates "will no longer be able to receive new security protections for the early boot process".\[31\]

**Safety and certification**
- **P28 — Crypto changes trigger safety recertification.**
- **P29 — Watchdog conflicts.** A signing p99 of 584 ms is far beyond a 100 ms deadline.\[7\]
- **P30 — Fail-safe versus fail-secure at boot.**

**Organisational and economic**
- **P31 — A responsibility gap between OEM, integrator and operator.**
- **P32 — Regulatory clocks.** [F] Under the EU CRA, reporting obligations apply from 11 September 2026 and full obligations from 11 December 2027. Support periods must be at least five years, and updates must remain available for ten. Products placed on the market before December 2027 stay outside most of the law.\[32\]\[33\]\[34\]
- **P33 — No standard of evidence that migration is complete.**
- **P34 — A small standalone market.** Mission 2's estimate, corrected: $0.4–1.9B globally [E].
- **P35 — Devices have no machine-readable self-description of their cryptography.**

**Root-cause compression**

| Root cause | Problems explained |
|---|---|
| R1 Algorithm-bound anchors in immutable silicon | P1, P2, P8, P9, P11, P12, P16 |
| R2 Time-dependent validity | P15, P22, P24, P26, P27 |
| R3 Organisation-bound authority | P13, P23, P27, P31 |
| R4 Public-key work at every endpoint | P4, P10, P17, P18, P19, P20 |
| R5 Crypto co-located with safety | P28, P29, P30 |
| R6 Copyable or rewindable state | P3, P24, P25 |
| R7 Invisible state and misaligned incentives | P31, P32, P33, P34, P35 |

**Still unexplored:** outage cost per substation, and the fraction of fleets that can be updated remotely. No primary data was found for either.

## 2. The interconnected system and its hidden leverage points

**How authority flows [I].** Silicon ROM key → OEM root → release key → firmware → device identity → operator PKI/KDC → session keys → commands. Configuration authority bypasses this chain entirely through engineering workstations.

**Central nodes.** The central nodes are the ROM verifier, the OEM release key, the workstation, the KDC/GDOI server and the time sources. Of these, only the ROM verifier cannot be re-issued, so it is the true bottleneck. Certificate expiry, catch-up size and revocation latency are symptoms of it.

**Feedback loops.**
- Reinforcing — deferral: uncertainty leads to deferral, which grows the classical installed base, which raises cost, which reinforces deferral.
- Reinforcing — OEM exit: small OEMs cannot fund PQ roots, customers distrust them, and exit becomes more likely.
- Balancing — regulation (CRA, IR 8547).
- Missing — there is no feedback from device crypto state back to the operator (R7). An unobservable system cannot be controlled.

**Information-theoretic limits.**
- An offline device cannot tell "no update exists" from "updates are being withheld". A freeze attack is undetectable without an external freshness signal.
- Succession needs at least one authenticated channel that outlives the predecessor family. That is either a pre-committed key from an independent family or physical presence.
- A hash commitment to a whole key set costs 32 B of OTP.

**30 leverage points**
1. A hash-only ROM verifier.
2. OTP that commits to a Merkle root over several family roots.
3. A one-way "classical sunset" latch.
4. Counters and epochs instead of time.
5. Pre-rotation: commit the hash of the next key.
6. Threshold across organisations, not just across keys.
7. Public-key work at enrolment only.
8. A KDC with ML-KEM key transport.
9. A separate crypto core.
10. A workstation quorum for configuration signing.
11. Witness cosignatures shipped with images.
12. Device crypto self-description.
13. Passive CBOM from observed handshakes.
14. A pinned hybrid-strict policy.
15. Anti-rollback hold-down.
16. A physical-presence channel.
17. A spares activation ceremony.
18. Monotonic counters outside restorable storage.
19. LMS index reservation.
20. Capability-scoped signing keys.
21. Rate-limited authority.
22. A neutral escrow custodian.
23. Procurement clauses.
24. A regulator evidence format.
25. Gateway termination for unpatchable devices.
26. A GDOI-PQ profile.
27. KEMTLS-PDK.
28. Moving signing out of devices.
29. A migration digital twin.
30. Insurance pricing on attestations.

Leverage points 1, 2, 4 and 6 act on the bottlenecks. Points 7–30 mostly reduce cost or improve observability.

## 3. Outputs of the independent invention engines

**Engine A — First principles**
- A1, the "commitment-first device": the only immutable knowledge is a hash commitment to a set of authority descriptors [H].
- A2, the "symmetric-only endpoint": the endpoint holds only symmetric keys and a hash verifier, and an enrolment authority does all public-key work, as spacecraft SDLS does [H].\[15\]
- A3, the "owner-sovereign device": the operator holds the root, and the OEM is one signer in a threshold [H].

**Engine B — TRIZ contradictions**

| Contradiction | Resolution |
|---|---|
| Immutable vs evolvable | Separate by abstraction: the immutable part is a hash plus a commitment ("preliminary action"). |
| Offline vs revocable | Separate in time: use counter-bounded authority and counter floors. |
| Large signatures vs small RAM | Stream LMS verification (about 1 KB stack) and move signing off-device. |
| Rotation vs availability | Make-before-break with hold-down, as in RFC 5011. |
| Central governance vs concentrated risk | Threshold across organisations. |
| Certification vs updates | Separate by partition: a crypto cell. |

**Engine C — Morphological design space.** Dimensions:
- anchor: ROM, OTP commitment, secure element or token;
- primitive: ECC, lattice, hash or MAC;
- authority: single, threshold of keys, or threshold of organisations;
- validity: time, counter, epoch or event;
- revocation: CRL, short-lived certificates, counter floor or rate limit;
- recovery: signed, physical presence or escrow.

The best unexplored combination is OTP commitment + hash verifier + threshold of organisations + counter validity + escrow, which became Architecture 1. Ledger authority plus time-based validity was rejected because of the liveness it demands.

**Engine D — Inversion**

| Failure | Defence |
|---|---|
| OEM disappears | Escrow plus threshold |
| All classical keys forged | Sunset latch, effective only if the device has already moved to PQ |
| Wrong clock | Counters |
| Gateway compromised | End-to-end authority |
| Power loss during renewal | A/B slots with commit-after-verify |
| Backup restore | Non-restorable counters |
| Malicious organisation | Threshold, rate limits and transparency |
| Isolated islands | Bounded-scope site quorum |

**Limit:** collusion by a full threshold of parties cannot be prevented, only detected afterwards.

**Engine E — Cross-domain transfer**
- Spacecraft SDLS-EP: symmetric master keys and over-the-air rekeying. The SDLS-DR proposal adds double-ratchet post-compromise recovery [F].\[35\]
- DNSSEC RFC 5011: hold-down periods.
- UEFI's 2026 expiry: never tie device authority to an X.509 notAfter date.
- KERI: pre-rotation.
- Immune systems: diverse recognisers, i.e. multi-family verifiers.
- Error-correcting codes: k-of-n reconstruction.
- Certificate Transparency and Sigstore: witness cosigning, made usable offline.

**Engine F — Remove a constraint, then restore it**
- Unlimited memory: ship every family's verifier. Once memory is restored, only hash verifiers remain small enough.
- 100-year security: only hash-based and symmetric assumptions are conservative enough.
- No trusted party: a threshold of three or more independent organisations.
- Contact once every six months: size the epochs to the contact interval.

**Engine G — Mathematics and physics**
- Hash functions are the only primitive shared by every NIST PQ family (SHA-3/SHAKE in ML-KEM and ML-DSA; SHA-256 in LMS). That makes hash engines the universal accelerator.\[25\]\[36\]
- Verification is cheaper than signing for every scheme, so all signing should move off-device.
- PUFs store keys; they do not provide algorithm agility.
- Small anchor state machines can be formally verified in TLA+ or Tamarin.

**Engine H — Missing categories**
- An authority-continuity kernel.
- A trust-anchor escrow utility.
- A crypto-state attestation format.
- A migration rehearsal twin.

## 4. Multi-solution matrix

| Problem | Algorithm | Hardware | Software | Protocol/infra | Governance | Boundary |
|---|---|---|---|---|---|---|
| P1/P8 ROM | Multi-family Merkle commitment | Hash-only ROM; PQ accelerator [V] | Second-stage PQ bootloader (wolfBoot LMS/XMSS/ML-DSA [F])\[37\]\[38\]\[39\] | Signed family-activation manifests | Procurement mandate | Classical-only ROM with no second stage cannot be fixed cryptographically |
| P2 HNDL-to-authority | Sunset latch | Monotonic fuse | Walk campaign tooling | Transparency of root changes | Deadline before a credible CRQC | Devices not yet moved: physical presence only |
| P15 time | Counter/epoch | Drift-bounded uptime counter | Max-staleness policy | Roughtime RFC 10049 | Contact SLAs | Freeze undetectable offline |
| P23 OEM exit | Threshold of organisations | Escrow leaf in OTP | Escrow release tooling | Custodian service | Contractual triggers; CRA support end | Escrow not committed at manufacture cannot be added without the OEM |
| P3/P25 state | SLH-DSA for roots | HSM index reservation | Persist-then-sign | Signer log | Clone/backup audits | Detect via transparency |
| P10/P17 weak devices | Symmetric-first; KEM-only | Hash accelerator | Stack-reduced libraries | GDOI-PQ, KEMTLS-PDK | Device-class policy | Class 0: hardware or gateway only |
| P22 catch-up | Pre-rotation chain | Metadata buffer | Skip lists | Checkpoints | Rotation caps | History must be retained |
| P28/P29 safety | Verify-only on device | Crypto core | Bounded-time scheduler | Offloaded signing | Separate security case | Shared-core devices need recertification |
| P35 invisibility | Signed crypto claims | Attestation key | CBOM agent | Passive CBOM | Evidence format | Silent devices: passive inference only |

**Comparisons**
- A second-stage bootloader is available now, but it inherits the classical ROM's HNDL exposure: whoever can forge the ROM signature can replace the second stage. Only a commitment at the ROM or OTP level closes that gap [I].
- A KDC wins on process buses; KEMTLS-PDK wins on point-to-point IP links.

## 5. Solution hypotheses (110)

Each entry gives a category and a novelty status.
- **Categories:** A = buildable now, B = advanced engineering, C = frontier research, D = radical.
- **Novelty:** Impl = already implemented, Prior = prior art exists, NewApp = existing technology in a new application, Comb = meaningful combination, Arch = architectural innovation, Hyp = research hypothesis.

**Roots and silicon**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| S1 | OTP Merkle root over multi-family roots | B | Comb (OCP hash tables are prior art) |
| S2 | Hash-only ROM verifier | B | NewApp |
| S3 | Sunset latch | A | Comb |
| S4 | Escrow leaf | B | Comb |
| S5 | Pre-rotation | A | Prior (KERI) |
| S6 | A/B anchor slots | A | Prior |
| S7 | Separate revocation and anti-rollback fuse banks | A | Impl |
| S8 | Anti-rollback hold-down | A | Hyp |
| S9 | SHA-2 + SHA-3 engine in every industrial MCU | B | NewApp |
| S10 | Streaming LMS verify | A | Impl |
| S11 | Commitment-verified family plug-ins | C | Hyp |
| S12 | Dual-verifier boot | A | Impl |
| S13 | Physical-presence channel | A | Prior |
| S14 | Crypto co-processor | B | NewApp |
| S15 | PUF-wrapped anchors | A | Impl |
| S16 | Certified masked PQ IP | B | emerging |
| S17 | Spares ceremony | A | Comb |
| S18 | Non-restorable counters | A | Impl |
| S19 | Fuse-budget planner | A | NewApp |
| S20 | ROM verification VM | C | Hyp; killed in red team |

**Authority and governance**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| G1 | Threshold of organisations | B | Comb |
| G2 | Neutral custodian | B | Arch |
| G3 | Capability-scoped keys | A | Prior |
| G4 | Rate-limited authority | A | Hyp |
| G5 | Witness transparency | A | Comb |
| G6 | Workstation quorum | A | Comb |
| G7 | Integrator delegation | A | Prior |
| G8 | CRA-linked escrow triggers | A | NewApp |
| G9 | Regulator evidence reports | B | Hyp |
| G10 | Attestation-priced insurance | B | NewApp |
| G11 | Procurement clause library | A | NewApp |
| G12 | Sector root-of-roots | C | Arch |
| G13 | Open succession reference implementation | A | NewApp |
| G14 | Island authority | B | Comb |
| G15 | Malicious-signer detection | B | Comb |
| G16 | Orphan adoption protocol | B | Arch |
| G17 | Owner-sovereign root | A | Prior (OpenTitan) |
| G18 | Integrator LMS sub-trees | A | Comb |
| G19 | Remote decommission | B | Prior |
| G20 | Crypto-readiness registry | A | NewApp |

**Time and validity**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| T1 | Counter epochs | A | NewApp |
| T2 | Staleness restricts privileges, never safety functions | A | Hyp |
| T3 | Roughtime quorum | A | Impl |
| T4 | Peer gossip of the highest counter | B | Hyp |
| T5 | Drift-bounded RTC windows | A | NewApp |
| T6 | Contact-sized epochs | A | NewApp |
| T7 | Laptop freshness tokens | A | Comb |
| T8 | Authenticated PTP | B | Prior |
| T9 | Expiry-free anchors | A | Prior |
| T10 | Counter-floor revocation | A | Comb |
| T11 | TESLA beacons, connected sites only | B | Prior |
| T12 | VDF time evidence | D | Hyp; killed |

**Keys and protocols**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| K1 | Symmetric-first with ML-KEM enrolment | A | NewApp |
| K2 | GDOI-PQ | B | NewApp |
| K3 | KEMTLS-PDK | B | Prior |
| K4 | PQ gateway | A | Prior (Aquaman) |
| K5 | Pinned hybrid-strict | A | Comb |
| K6 | IKE_INTERMEDIATE profiles | A | Impl |
| K7 | Fragment-aware DTLS | B | NewApp |
| K8 | Ratcheted symmetric authority | B | Prior (SDLS-DR) |
| K9 | PSK mixing (RFC 8784-style) | A | Impl |
| K10 | LoRaWAN commissioning enrolment | A | Comb |
| K11 | Unchanged process-bus MACs | A | NewApp |
| K12 | OPC UA PQ policy | B | NewApp |
| K13 | DNP3-SA PQ key update | B | NewApp |
| K14 | Rekey scheduling twin | B | NewApp |
| K15 | Maintenance-port rekey | A | Prior |
| K16 | Hash broadcast authentication for slow telemetry | B | Prior |
| K17 | Split-ClientHello test harness | A | NewApp |
| K18 | Pre-distributed intermediates | A | Prior |
| K19 | Merkle-tree certificates for OT | C | Prior; not verified here |
| K20 | Island KDC replicas | B | Comb |

**Fleet and lifecycle**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| L1 | Pre-rotation catch-up | A | Comb |
| L2 | Threshold checkpoints | A | Prior |
| L3 | Backup-aware state | A | Comb |
| L4 | LMS index reservation | A | Prior |
| L5 | SLH-DSA for rare root signatures | A | NewApp |
| L6 | Crypto passport | B | Comb |
| L7 | Passive CBOM | A | NewApp |
| L8 | Migration twin | B | NewApp |
| L9 | Firmware crypto static analysis | A | emerging |
| L10 | Walk orchestrator | B | NewApp |
| L11 | Orphan takeover kit | B | Hyp |
| L12 | Authority handover at CRA support end | B | Hyp |
| L13 | Fleet risk score | A | NewApp |
| L14 | Spare-shelf refresh | A | NewApp |
| L15 | Key-destruction proofs | B | Prior |
| L16 | Integrator change traceability | A | Comb |
| L17 | Canaries with rollback | A | Impl |
| L18 | Adversarial authority simulation | B | NewApp |
| L19 | Supplier scoring | A | NewApp |
| L20 | "PQ-ready" label | B | NewApp |

**Safety and assurance**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| Q1 | Crypto cell safety case | B | NewApp |
| Q2 | Verify-only devices | A | Comb |
| Q3 | Constant-time or randomised ML-DSA loop | B | Prior |
| Q4 | Idle precomputation | A | Prior |
| Q5 | Certified fallback image | A | Prior |
| Q6 | TLA+ anchor state machine | A | NewApp |
| Q7 | Tamarin succession model | B | NewApp |
| Q8 | PQ-verify fault suite | B | Prior |
| Q9 | Deadline-aware crypto scheduler | B | NewApp |
| Q10 | Update-delta safety argument templates | B | Hyp |

**Radical**

| ID | Hypothesis | Cat. | Novelty |
|---|---|---|---|
| X1 | Trust renewal as a utility | D/B | Arch |
| X2 | Fleet algorithm diversity | C | Hyp |
| X3 | Peer-attested authority votes | C | Hyp |
| X4 | Tamper-evident commissioning tokens | B | Comb |
| X5 | QKD for field devices | — | Killed |
| X6 | Blockchain authority | — | Killed |
| X7 | 100-year hash-only device | C | Hyp |
| X8 | Property-named security layer | C | Hyp |

## 6. Thirty cross-disciplinary combinations

1. S1+S2+S3, the continuity kernel: solves P1, P2, P8, P9 and P12.
2. S1+S4+G1+G2, succession escrow: solves P23, P27 and P31.
3. K1+K2+K11, symmetric fabric: solves P10, P17, P19 and P20.
4. T1+T2+T10, time-free validity: solves P15, P26 and P27.
5. L1+S5+L2, catch-up: solves P22 and P24.
6. Q1+Q2+Q9, safety isolation: solves P28 and P29.
7. L6+L7+G9, observability evidence: solves P33 and P35.
8. G5+G15+G4: bounds the damage a malicious organisation can do.
9. S13+X4+S17: physical rescue path for offline assets.
10. L4+L5+G18: hash-signature custody.
11. K4+K5+L7: legacy wrapping.
12. S12+S9: dual verification with a universal hash engine.
13. L8+L18+L10: migration rehearsal.
14. K8+T1: the spacecraft pattern for disconnected OT.
15. G6+L16: configuration authority.
16. S18+L3: backup safety.
17. G8+L12+G2: CRA handover.
18. K3+S9: accelerated KEMTLS-PDK.
19. S14+K2: crypto cell as a GDOI member.
20. T3+T5+T7: layered freshness.
21. G12+G2: sector custodians.
22. X2+G15: diversity with cross-checking.
23. L13+G10: insurance.
24. Q6+Q7+S1: a verified kernel.
25. K12+L7: OPC UA PQ plus verification.
26. S8+G4: hold-down plus rate limits.
27. L11+S13: orphan takeover.
28. L19+G11+L20: market pull.
29. K10+S17: LoRaWAN enrolment.
30. Q5+S6: atomic recovery.
31. X8+K1: property-named symmetric security.
32. X1+2+4: the trust-renewal utility.

Combinations 1, 2, 3, 4 and 7 together cover 27 of the 35 named problems (counted from the coverage table) [I].

## 7. Eleven architectural proposals

**Architecture 1 — Authority Continuity Kernel (ACK)**
- **Thesis:** the only immutable things are a hash engine and a 32-byte commitment to authorities in several families.
- **Components:**
  - a ROM SHA engine;
  - an LMS verifier using about 1 KB of stack [D];
  - an OTP Merkle root over {classical root, LMS root, ML-DSA root, escrow root, policy};
  - a monotonic sunset latch;
  - A/B anchor slots.
- **Flow:** the boot stage verifies an LMS-signed second stage, which carries the ML-DSA, hybrid and protocol stacks. Activating or retiring a family needs signatures from two committed families, or from the escrow leaf plus one family.
- **Failures:**
  - a lattice break leaves LMS plus escrow;
  - an LMS signer compromise leaves ML-DSA plus the threshold;
  - power loss is handled by the A/B slots.
- **Offline operation:** complete. The design uses no time.
- **Resources:**
  - [E] boot verification of 2.66M cycles is about 42 ms at 64 MHz and about 17 ms at 160 MHz;
  - [D] verifier code of 12,864 B of flash, including the library;\[25\]
  - [E] 32 B of OTP plus a few fuses.
- **What is new:** each element has prior art (OCP hash tables, wolfBoot hybrid boot, OpenTitan SPHINCS+).\[9\]\[22\]\[37\] What I found no prior art for is the combination in one commitment: cross-family activation rules, an escrow leaf and a sunset latch. That makes it a meaningful combination, not a patent-safe novelty.
- **Limitation:** native support needs new ROMs, roughly from 2028 onward [E].

**Architecture 2 — Symmetric-First Industrial Fabric**
- ML-KEM-768 enrolment delivers a key-encryption key. A GDOI-PQ KDC then distributes group and session keys. IEC 62351-6 MACs on the data path are unchanged.
- [D] ML-KEM-768 decapsulation takes 22.0 ms on a Cortex-M0+ with 14.2 KB of stack, once per enrolment.\[7\]
- **Risk:** the KDC is central. It is replicated and needs a threshold to unlock.
- **Prior art:** CCSDS SDLS-EP; arXiv 2608.22123 (ML-KEM for Sampled Values).\[15\]\[40\]

**Architecture 3 — Threshold Succession Network**
- Fleet authority is k-of-n across the OEM, the operator and neutral custodians.
- **Conservative mode:** independent multi-signatures.
- **Advanced mode:** threshold ML-DSA, now practical for small groups [F]:
  - Celi et al.: up to 6 parties;\[41\]
  - Mithril: USENIX Security 2026;\[18\]
  - TALUS: one online round, 0.62–1.94 ms in its TEE variant.\[18\]

**Architecture 4 — Time-Free Validity Layer**
- Authority objects carry epoch counters, not notAfter dates. Revocation raises a counter floor.
- Staleness restricts only privileged operations.
- Roughtime is an optional accelerator when connected.

**Architecture 5 — Pre-Rotation Catch-up Chain**
- Each root commits to SHA-256(next root).
- [E] Catching up after 10 missed rotations costs 10 × 32 B + 29.8 KB ≈ 30.1 KB, versus 10 × 29.8 KB = 298 KB for a sequential TUF walk. That is a ratio of about 0.10.

**Architecture 6 — Crypto Cell**
- A separate crypto core with its own "no interference" safety argument.
- The control core receives verified images and keys over a fixed-latency interface.

**Architecture 7 — Offline Transparency Bundle**
- Images ship with witness cosignatures, so offline devices can detect targeted malicious releases.

**Architecture 8 — Physical-Presence Authority Bridge**
- A sealed commissioning token plus on-site presence authorises a one-time move to a PQ second stage on classical-only devices.

**Architecture 9 — Crypto Passport and Observable Fleet**
- Devices sign a description of their families, roots, latch, counters and library versions. Silent devices are inferred passively.
- This turns migration into a control loop.

**Architecture 10 — Trust Renewal Utility**
- A managed bundle of custodian, escrow, threshold signer, checkpoint server and witness, for OEMs and orphan-fleet operators.

**Architecture 11 — Hash-Only 100-Year Device**
- Only hash-based signatures and symmetric keys. Enrolment happens through physical commissioning.

## 8. Red-team analysis and eliminated ideas

**Killed**

| Idea | Reason |
|---|---|
| Blockchain authority | Needs a liveness that offline devices lack; transparency logs give its benefits more cheaply. |
| QKD for field devices | Needs optical links, and gives no authentication without pre-shared keys. |
| Per-frame PQ signatures on process buses | 208–250 µs per frame. |
| TESLA on offline devices | Needs loose clock synchronisation. |
| VDF time evidence | Too costly, and depends on assumptions about attacker speed. |
| PUF as algorithm agility | A PUF stores keys; it cannot change algorithms. |
| Fully autonomous AI migration | Safety cases require human authorisation; kept only as rehearsal (L8). |

**Modified**
- **S20 ROM VM → S11, plug-ins running from flash.** This keeps the immutable attack surface small.
- **G2 custodian.** At least two custodians in different jurisdictions inside the threshold, so the custodian does not become a new single point of failure.
- **ACK.** ROM masks freeze 18–36 months before volume production [E]. So the commitment can instead live in OTP programmed at OEM provisioning, on existing ROMs that check a hash-of-key table, behind a first stage that uses only hash functions.
- **LMS custody.** HSM vendors will bundle reservation, so it is retained as a feature of the utility.

**Assumptions to test**
- Mainstream MCUs can host a 32-byte manifest root in OEM-provisioned OTP.
- Operators accept custodians.
- Assessors accept the crypto-cell argument.
- Hash-only first stages meet boot budgets on low-clock parts.

**Is replacement better?** Yes for Class 0 devices, and for classical-ROM assets with under about 10 years of remaining life: replace them, with gateway isolation in the interim [I].

## 9. The 20 highest-potential inventions

Score = Σ (weight × rating / 5). Rating order: problems (15), feasibility (15), security (15), novelty (10), deployment (10), cost (10), willingness to pay (10), strategic (5), defensibility (5), expansion (5).

| Rank | Invention | Ratings | Score | Confidence | Fatal-flaw risk |
|---|---|---|---|---|---|
| 1 | Multi-family committed manifest + latch + escrow leaf | 5,4,5,3,4,4,4,5,3,4 | 84 | Medium | Silicon/provisioning adoption lag |
| 2 | Symmetric-first fabric with ML-KEM enrolment | 4,5,4,2,5,5,4,4,2,3 | 80 | High | KDC compromise is fleet-wide |
| 3 | Hash-only minimal ROM verifier | 4,5,5,2,4,4,3,5,2,4 | 79 | High | Vendors favour ML-DSA ROMs for CNSA 2.0 |
| 4 | Time-free counter validity | 4,5,4,3,4,4,3,4,2,4 | 77 | High | Freeze attacks remain |
| 5 | Threshold succession escrow | 5,3,4,4,3,3,4,5,4,4 | 77 | Medium | Legal acceptance |
| 6 | Neutral custodian utility | 4,3,3,4,3,4,4,5,4,4 | 73 | Low–Medium | Liability |
| 7 | Offline transparency bundle | 4,4,4,3,3,3,3,4,3,4 | 71 | Medium | Witness ecosystem |
| 8 | Crypto cell | 4,4,3,3,3,3,4,4,3,4 | 70 | Medium | Assessor acceptance |
| 9 | Pre-rotation catch-up | 3,4,3,4,4,4,3,3,3,3 | 69 | High | Long-lived next-key secrecy |
| 10 | Passive CBOM | 3,5,2,2,5,4,4,3,2,3 | 68 | High | Easily copied |
| 11 | Dual-family verifier boot | 3,4,5,2,3,3,3,4,2,3 | 67 | High | Already implemented |
| 12 | Scoped, rate-limited authority | 3,4,4,3,3,3,3,4,3,3 | 67 | Medium | Policy complexity |
| 13 | Workstation signing quorum | 3,4,4,2,4,3,4,3,2,3 | 67 | Medium | Workflow friction |
| 14 | Pinned hybrid-strict policy | 3,5,4,2,4,4,2,3,1,2 | 66 | High | Trivially reproducible |
| 15 | Crypto passport | 3,4,2,3,4,3,4,4,3,4 | 66 | Medium | Needs a standard |
| 16 | LMS custody with reservation | 3,5,4,1,4,3,3,3,2,2 | 65 | High | Commoditised |
| 17 | Ratcheted symmetric authority | 3,4,4,3,3,4,2,3,2,3 | 65 | Medium | Desynchronisation |
| 18 | Migration rehearsal twin | 3,4,2,3,3,4,4,3,3,4 | 65 | Medium | Model fidelity |
| 19 | Anti-rollback hold-down | 2,5,3,3,4,4,2,3,2,2 | 63 | Medium | Delays urgent fixes |
| 20 | PQ gateway proxy | 3,5,2,1,5,4,4,2,1,2 | 63 | High | Prior art; last hop stays classical |

Check for rank 1: 15 + 12 + 15 + 6 + 8 + 8 + 8 + 5 + 3 + 4 = 84.

## 10. Engineering blueprints

**Blueprint 1 — ACK**

**A. What it is.** Silicon/firmware IP plus a provisioning specification.

**B. Architecture.**
- OTP holds `ACK_ROOT` (32 B), `SUNSET` (1 bit) and `FLOOR` (counter fuses).
- Each manifest leaf is `{family_id, pubkey_hash, activation_policy}`.
- The transitions are `ADD_FAMILY`, `RETIRE_FAMILY`, `SET_SUNSET`, `RAISE_FLOOR` and `ESCROW_RELEASE`. Each needs two active families, or the escrow leaf plus one family.

**C. Workflow.**
1. The OEM provisions `ACK_ROOT`.
2. Normal boot: LMS stage 1, then a hybrid ML-DSA+ECDSA application.
3. Before a CRQC, `SET_SUNSET` is signed by LMS + ML-DSA. After that, classical-only signatures are rejected permanently.
4. If lattices break, `RETIRE_FAMILY(ML-DSA)` is signed by LMS + escrow.

**D. Security.**
- No single-family compromise gives control.
- The latch is monotonic.
- Anchor updates are atomic under power loss.
- Validation: a TLA+ model plus latch fault injection.

**E. Resources.**
- [D] 2.66M cycles to verify.
- LMS SHA-256 (n=32, w=8, h=10) signatures are 1,452 B; w=4 gives 2,508 B. Computed from RFC 8554 as 4 + (4 + 32 + p·32) + 4 + 10·32, with p = 34 or 67.

**F. Roadmap.**
- Emulate now in a second stage (wolfBoot already supports LMS/XMSS/ML-DSA [F]).\[38\]\[39\]
- Build provisioning tools.
- ROM support from about 2028.
- An OCP/GlobalPlatform profile.

**H. Commercialisation.**
- Licence the kernel to MCU vendors and sell an OEM provisioning service.
- Competitors: Caliptra and OpenTitan, plus vendor ROMs [V].\[42\]\[43\]

**I. Defensibility.** Moderate. Standards participation and the reference implementation matter more than patents, given the OCP and Intel prior art.

**Blueprint 2 — Symmetric-First Fabric**
- **What it is:** a KDC/GDOI-PQ product plus a device SDK.
- **Key sizes:** ML-KEM-768 encapsulation key 1,184 B; ciphertext 1,088 B [F].
- **Recovery and islands:** missed rekeys are recovered through the counter floor; islands run KDC replicas.
- **Main risk:** compromise of the KDC. Mitigations are HSM-held key-encryption keys and scoping per substation.
- **Cost:** [V] wolfSSL reports 8.3 ms for ML-KEM-768 decapsulation on a newer STM32 (clock unspecified).\[25\]\[44\] The data path is unchanged.
- **First customers:** utilities already deploying IEC 62351-9. Standards route: IEC TC57 WG15.
- **Defensibility:** depth of integration with protection relays.

**Blueprint 3 — Threshold Succession and Custodian Utility**
- **Healthy OEM:** the OEM plus one other party signs.
- **On a trigger** (end of CRA support, or insolvency): the custodians plus the operator sign.
- **Metadata size:** about 3 × 3,309 B ≈ 9.9 KB using ML-DSA-65 multi-signatures [E].
- **Timeline:** contracts now, the protocol in 1–2 years, threshold ML-DSA once NIST's threshold call matures.\[45\]
- **Pricing:** per device-year.

**Blueprints 4–7, in brief**
- **Time-free validity:** a library and metadata profile. Withheld updates remain undetectable offline, and the safety case must say so.
- **Pre-rotation:** a TUF/Uptane extension. Next keys are held offline under a threshold.
- **Crypto cell:** a reference board plus a safety template. The ML-DSA-44 signing p99 of 584 ms is why signing stays out of control partitions.\[7\]
- **Passive CBOM:** a parser for OPC UA OpenSecureChannel policies, TLS/DTLS groups, IKE proposals and GDOI, producing CycloneDX CBOM plus signed passport claims.\[30\]

## 11. Experiment plans (owned lab environments only)

| ID | Hypothesis / set-up | Success criterion | If it fails / next step |
|---|---|---|---|
| E1 | ACK FSM on a Cortex-M33 board (STM32G5 when available) with wolfBoot LMS; 100,000 boots with random power cuts | No brick, no illegal state, verify ≤100 ms | Illegal state → add journaling; too slow → w=4/h=5 or a hash accelerator. Next: E2 |
| E2 | TLA+/Tamarin model of ACK and threshold succession | No path from a single family or organisation to control at depth ≥12 | Use counterexamples to redesign |
| E3 | 10,000 simulated devices offline for 1–10 years, with withholding and replay | Zero acceptance of authority below the floor | — |
| E4 | GDOI-PQ rekey of GOOSE/SV across 20 emulated IEDs | Data-path latency unchanged; under 1 s per group | — |
| E5 | Three-organisation OEM-exit drill plus protocol prototype | Release authorised in under 72 h; no single party can act alone | — |
| E6 | Pre-rotation catch-up vs sequential TUF over N = 1–50 rotations | ≥5× reduction at N=10 | — |
| E7 | Passive CBOM on captured lab traffic | ≥95% of policies correctly identified | — |
| E8 | Crypto-cell WCET: control jitter with and without partition | — | — |
| E9 | Split-ClientHello through industrial firewalls (lab) | Measure drop/reset rates | — |
| E10 | ML-DSA iteration-count leak on target MCUs | Latency randomisation removes the leak | — |

## 12. Three future visions

**Vision 1 — Evolutionary (2027–2032).**
- Components:
  - PQ second-stage bootloaders on existing MCUs;
  - a symmetric-first fabric;
  - counter-based validity;
  - passive CBOM;
  - gateways for legacy devices;
  - escrow contracts tied to CRA support periods.
- **Weakness:** classical ROMs keep the HNDL-to-authority exposure until devices are moved to PQ.

**Vision 2 — Transformational (2028–2040).**
- Every new device carries an ACK.
- Fleet authority is a threshold across organisations, with custodians.
- Validity is time-free.
- Crypto passports are accepted as regulatory evidence.
- **Weakness:** governance and custodian liability.

**Vision 3 — Radical (2035 onward).**
- Trust renewal is a utility, like time service.
- Subfleets are deliberately diverse in algorithm.
- The longest-lived assets use hash-only devices.
- Applications name security properties, not algorithms.
- **Requires:** fleet-diversity theory, a property-level protocol layer and international custodian governance.

## 13. Biggest unanswered questions

1. Neutral, current benchmarks for LMS/XMSS verification on Cortex-M0+/M33 with hardware SHA. The best figures found date from 2020–2021.
2. Which shipping ROMs verify which PQ families, at parameter level [V].
3. Formal security definitions for cross-family activation rules.
4. Whether ML-DSA iteration-count leakage can aid key recovery.
5. Masking margins for PQ hardware.
6. Whether assessors accept crypto-cell partitioning under IEC 61508/62443.
7. How escrow works legally across jurisdictions.
8. What fraction of fleets can be updated remotely, and what outages cost.
9. PQ roadmaps for OPC UA, DNP3 and IEC 62351.
10. How realistic the falling quantum resource estimates are in hardware.
11. How secret a pre-rotated next key stays over long periods.
12. How middleboxes behave with large hybrid handshakes.

## 14. Prioritised roadmap

- **0–6 months:**
  - run E1, E2, E6 and E7;
  - publish an open ACK reference second stage and the TLA+ model;
  - draft an escrow contract template;
  - engage IEC TC57 WG15 on GDOI-PQ.
- **6–18 months:**
  - run E3, E4, E5 and E8;
  - pilot the symmetric-first fabric with one utility;
  - pilot the custodian with two small OEMs;
  - submit an ACK profile to OCP/GlobalPlatform.
- **18–36 months:**
  - ROM integration with a silicon partner;
  - threshold ML-DSA in the custodian service;
  - a regulator evidence format.
- **Continuously:** move every updatable classical-root device to PQ before any credible CRQC, starting with those that have the longest remaining life.

**Strategic verdict**
- **Defensible businesses:** the custodian/escrow utility and the symmetric-first fabric.
- **Standards and IP play:** the ACK, licensed to MCU vendors.
- **Features that incumbents will absorb:** passive CBOM, pinned hybrid policy, LMS custody and PQ gateways.

## Final coverage table

| Invention | R1 algorithm | R2 time | R3 organisation | R4 endpoint public key | R5 safety | R6 state | R7 invisibility |
|---|---|---|---|---|---|---|---|
| ACK manifest + sunset latch | ● | ○ | ◐ | ○ | ○ | ◐ | ○ |
| Hash-only ROM verifier | ● | ○ | ○ | ◐ | ◐ | ○ | ○ |
| Symmetric-first fabric | ○ | ◐ | ○ | ● | ◐ | ○ | ○ |
| Time-free validity | ○ | ● | ○ | ○ | ○ | ◐ | ○ |
| Threshold succession + custodian | ◐ | ○ | ● | ○ | ○ | ○ | ◐ |
| Pre-rotation catch-up | ◐ | ● | ○ | ○ | ○ | ○ | ○ |
| Crypto cell | ○ | ○ | ○ | ◐ | ● | ○ | ○ |
| Offline transparency bundle | ◐ | ○ | ◐ | ○ | ○ | ◐ | ◐ |
| Passive CBOM + passport | ○ | ○ | ○ | ○ | ○ | ○ | ● |
| LMS custody | ◐ | ○ | ○ | ○ | ○ | ● | ○ |
| Backup-aware state | ○ | ○ | ○ | ○ | ○ | ● | ○ |
| PQ gateway | ◐ | ○ | ○ | ● (legacy) | ○ | ○ | ○ |

● = solves; ◐ = partially solves; ○ = does not address.

**The combination that solves the most.** Five inventions fully address R1–R4 and R7 and partly address R5 and R6:
1. the ACK manifest;
2. the symmetric-first fabric;
3. time-free validity;
4. threshold succession with a custodian;
5. crypto passport and passive CBOM.

Adding the crypto cell closes R5, and backup-aware state completes R6. This seven-part minimal portfolio is the recommended direction. It supersedes the original five-plane Industrial Trust Plane while absorbing its missing provisioning, time, revocation and governance layers.

## Sources

1. [NIST IR 8547 Final: Post-Quantum Deadlines Become Vendor Requirements](https://labs.cloudsecurityalliance.org/research/csa-research-note-nist-ir8547-pqc-transition-20261030-csa-st/)
2. [NIST IR 8547 Final: What Changed From the Draft](https://postquantum.com/security-pqc/nist-ir-8547-final/)
3. [Execution of the Migration to Post-Quantum Cryptography](https://www.whitehouse.gov/wp-content/uploads/2026/06/M-26-15-Execution-of-the-Migration-to-Post-Quantum-Cryptography.pdf)
4. [How to factor 2048 bit RSA integers with less than a million ...](https://arxiv.org/pdf/2505.15917)
5. [The Decryption Threshold — Re-estimating the Quantum Threat to Blockchain Infrastructure - Quantum Computing Report](https://quantumcomputingreport.com/the-decryption-threshold-re-estimating-the-quantum-threat-to-blockchain-infrastructure/)
6. [Safeguarding cryptocurrency by disclosing quantum vulnerabilities responsibly](https://research.google/blog/safeguarding-cryptocurrency-by-disclosing-quantum-vulnerabilities-responsibly/)
7. <https://arxiv.org/pdf/2603.19340>
8. [AM263P4: Post-quantum signature verification in ROM bootloader - Arm-based microcontrollers forum - Arm-based microcontrollers - TI E2E support forums](https://e2e.ti.com/support/microcontrollers/arm-based-microcontrollers-group/arm-based-microcontrollers/f/arm-based-microcontrollers-forum/1585960/am263p4-post-quantum-signature-verification-in-rom-bootloader)
9. [\[RFC\] CNSA 2.0 Compliance Rooted in the ROM · Issue #30765 · lowRISC/opentitan · GitHub](https://github.com/lowRISC/opentitan/issues/30765)
10. [Microchip Adds Quantum Resistance to Embedded Controllers](https://www.electropages.com/blog/2025/05/microchip-adds-quantum-resistance-embedded-controllers)
11. [Microchip Brings Hardware Quantum Resistance to Embedded Controllers :: Microchip Technology Incorporated (MCHP)](https://ir.microchip.com/news-events/press-releases/detail/1312/microchip-brings-hardware-quantum-resistance-to-embedded-controllers)
12. [2419289\_en-US - NXP Community](https://community.nxp.com/t5/Multi-Source-Translation-Content/2419289-en-US/ta-p/2423842?profile.language=en)
13. [NXP MCX A5 Cortex-M33 MCU family supports 10BASE-T1S Single Pair Ethernet and Post-Quantum Cryptography - CNX Software](https://www.cnx-software.com/2026/08/19/nxp-mcx-a5-cortex-m33-mcu-family-supports-10base-t1s-single-pair-ethernet-and-post-quantum-cryptography/)
14. [STMicroelectronics Launches MCU With Hardware For Post-quantum Cryptography](https://quantumzeitgeist.com/stmicroelectronics-post-quantum-mcu-hardware-cryptography/)
15. [On Requirements & Concepts for TT&C Link Key Management Christoph Bader](https://www.ndss-symposium.org/wp-content/uploads/spacesec2024-53-paper.pdf)
16. [RFC 10049 - Roughtime: A Protocol for Rough Time Synchronization](https://datatracker.ietf.org/doc/rfc10049/)
17. [Efficient Threshold ML-DSA Full Version](https://eprint.iacr.org/2026/013.pdf)
18. [TALUS: Threshold ML-DSA with One-Round Online Signing via Boundary Clearance and Carry Elimination](https://arxiv.org/html/2603.22109v1)
19. [Low latency post-quantum signature verification for fast secure-boot](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12137169)
20. [Low latency post-quantum signature verification for fast secure-boot](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11405213)
21. [Low Latency Post-quantum Signature Verification For Fast Secure-boot GHOSH; SANTOSH ; et al. \[Intel Corporation\]](https://uspto.report/patent/app/20190319796)
22. [Hardware Secure Boot OCP Security workgroup](https://www.opencompute.org/documents/secure-boot-2-pdf/)
23. [More Efficient Post-quantum KEMTLS with Pre-distributed Public Keys](https://repository.ubn.ru.nl/bitstream/handle/2066/238044/1/238044.pdf)
24. <https://eprint.iacr.org/2020/470.pdf>
25. [Quantum-Resistant Security for Software Updates on Low-power Networked Embedded Devices](https://arxiv.org/pdf/2106.05577)
26. [Nothing Breaks: No Single Peer Can Soundly Gate Post-Quantum Delivery](https://arxiv.org/pdf/2609.07849)
27. [The 1-Bit Barrier is Universal: k-Stage Pipeline Composition and Unified Leakage Bounds for Standard Modular Reductions in PQC Hardware](https://arxiv.org/pdf/2605.02856)
28. [EN IEC 62351-9:2023 - Cyber Security Key Management for Power Systems](https://standards.iteh.ai/catalog/standards/clc/f1ceebd5-a922-41e5-a200-9a36aad3c9bd/en-iec-62351-9-2023)
29. [IEC 62351-9:2023 Cyber Security Key Management for Power Systems](https://standards.iteh.ai/catalog/standards/iec/d57aa4c9-5283-4548-b3a2-8b199d65a92e/iec-62351-9-2023)
30. [Release Issue 03: Finding the cryptography inside an OPC UA deployment · foikwuogu/quantum-safe-pipeline-notes · GitHub](https://github.com/foikwuogu/quantum-safe-pipeline-notes/releases/tag/issue-03)
31. [When Secure Boot certificates expire on Windows devices](https://support.microsoft.com/en-us/servicing/os/secure-boot/2026/02/when-secure-boot-certificates-expire-on-windows-devices)
32. [Cyber Resilience Act: What Manufacturers Need to Know - WILLIAM FRY](https://www.williamfry.com/knowledge/cyber-resilience-act-what-manufacturers-need-to-know/)
33. [The EU Cyber Resilience Act explained: what changes, and who it affects](https://www.csl-group.com/blogs/eu-cyber-resilience-act-reporting/)
34. [EU Cyber Resilience Act: Scope, Requirements and Deadlines](https://noru.tech/frameworks/cyber-resilience-act)
35. [Double Ratchet Key Evolution for CCSDS Telecommand and Telemetry](https://eprints.gla.ac.uk/396322/1/396322.pdf)
36. [Keccak Acceleration for Post-Quantum Cryptography: A DMA-Enhanced RISC-V](https://lup.lub.lu.se/student-papers/record/9230814/file/9230834.pdf)
37. [wolfBoot Now Supports NXP’s New MCX A and MCX W Microcontrollers - wolfSSL](https://www.wolfssl.com/wolfboot-now-supports-nxps-new-mcx-a-and-mcx-w-microcontrollers/)
38. [GitHub - Frauschi/wolfBoot: wolfBoot is a portable, OS-agnostic, secure bootloader for microcontrollers, supporting firmware authentication and firmware update mechanisms. · GitHub](https://github.com/Frauschi/wolfBoot)
39. [wolfBoot Secure Bootloader](https://www.wolfssl.com/products/wolfboot/)
40. [A Lightweight and Post-Quantum Secure Framework for ...](https://arxiv.org/pdf/2608.22123)
41. [Poster: Efficient Threshold ML-DSA up to 6 Parties](https://dl.acm.org/doi/10.1145/3719027.3760739)
42. [Post-Quantum - wolfSSL](https://www.wolfssl.com/category/post-quantum/)
43. [GitHub - chipsalliance/Caliptra: Caliptra IP and firmware for integrated Root of Trust block · GitHub](https://github.com/chipsalliance/Caliptra)
44. [Updated Post-Quantum Benchmarks for ML-KEM and ML-DSA on STM32 - wolfSSL](https://www.wolfssl.com/updated-post-quantum-benchmarks-for-ml-kem-and-ml-dsa-on-stm32/)
45. [Mithril: Efficient Threshold ML-DSA from Secret Sharing with ...](https://csrc.nist.gov/csrc/media/Projects/threshold-cryptography/documents/TCall-1/Mithril-PW01.pdf)

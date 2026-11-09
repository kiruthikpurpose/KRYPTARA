# Trust That Outlives Its Makers
## A Unified Atlas of Post-Quantum Security for OT and Embedded Infrastructure
### Second edition, with a codex of what nature, physics and history already know about long-lived trust

*Everything this investigation has produced, rewritten into one argument: six research passes (the newest through biology, physics and history), one interactive verification lab, two invention rounds, two red-team rounds and seven quantitative models. 6 November 2026.*

---

## How to read this document

This is not a stack of reports stapled together. Each pass changed what the earlier ones meant, so the material has been re-derived into one line of reasoning. Where a later pass overturned an earlier belief, only the surviving belief appears in the main text. The overturned ones are kept in **Part 19 (the corrections ledger)**, so you can see how the understanding moved and why.

**What is new in this edition:**
- **Part 5, the Living Trust Codex:** 36 mechanisms from immune systems, bee colonies, cells, seeds, trees, hearts, forests and fireflies, each taken through evidence → principle → mechanism → where the analogy breaks → kill test. They are distilled into twelve laws (5.7), with a section on where nature is the wrong teacher (5.8).
- **Part 6, time without a clock:** measured oscillator drift, every available time cue and what it can prove, the governed grid clock, and counters that wrap.
- **Part 7, what lasted:** a 1,300-year renewal cycle, centuries-old commons, the DNSSEC root rollover, deep-time markers, evidence that stays verifiable, how long real migrations take, and precedents from cars, rail, aviation, medicine, telecom and space.
- **Part 8, hardware:** what the lock protects and against whom; physical trust; memory that outlives the chip.
- **Part 9, seven models** that put numbers on migration order, quorum independence, hold-downs, drift, exposure and diversity. Two of them changed recommendations.
- **2.6, the extinction record** of cryptographic families, and new material threaded through Parts 3, 4 and 10–21: two new root causes (R10, R11), 18 new problems (N56–N73), 22 new ideas (I-13 to I-34), new experiments, corrections and rankings.

**Three ways to read it:**
- **In twenty minutes:** Part 0, the twelve laws (5.7), and the ranking (20.2).
- **As an architect:** Parts 0, 3, 4 and 8, then 10–12, with Part 9 for the numbers behind the rules.
- **As a researcher:** Parts 5–9, then 16 (experiments), 18 (ideas) and 19 (what we got wrong).

**Evidence labels used throughout**

| Label | Meaning |
|---|---|
| **[F]** | Primary fact: a standard, a specification, an official document, a peer-reviewed paper |
| **[2nd]** | A fact reported by a secondary source; the primary was not opened |
| **[V]** | Vendor or sponsor claim, not independently verified |
| **[D]** | Demonstrated or measured result from a paper or benchmark |
| **[C]** | Computed here and cross-checked (Python, the verification lab, or the models in Part 9) |
| **[E]** | Estimate; the arithmetic is shown |
| **[I]** | Inference by this investigation |
| **[H]** | Invention or hypothesis: proposed, not validated |
| **[S]** | Speculative long-range possibility |

**Honesty about coverage.** You invited 500–600 sources. The two passes before this edition touched about 130 distinct sources, of which about 80 were decisive; their register is 21.5. This edition adds about 170 more: 132 in the new register (21.6), 128 of them with a URL matched to the citation, and about 40 further papers cited inline in Parts 2.6 and 5–8. That brings the sources named in this document to about 300. Older passes used further sources that are not reproduced. Where a claim rests on one source, a vendor or a draft, it says so. Every natural analogy is labelled for what it is: a source of candidate designs and known failure modes, never proof. Part 20 lists what to verify next.

---

## Contents

0. The answer on one page
1. How the understanding evolved
2. Foundations: the threat, the mathematics, the machines, and the extinction record
3. The problem universe, compressed to its root causes
4. The hidden structure: how authority flows, and where it leaks
5. The Living Trust Codex: what nature already knows about long-lived trust
6. Time without a clock: what a disconnected device can know
7. What lasted, and how migrations really go
8. Hardware: what the lock protects, and what outlives the chip
9. Quantitative models built for this edition
10. The solution space after two invention rounds and two red teams
11. The recommended architecture stack
12. Allocating security by device class
13. Seven deployment scenarios, end to end
14. Economics: who pays, why they wait, and what makes them act early
15. The design debate and where it converged
16. Validation programme: experiments ordered by information value
17. The long view: infrastructure meant to last 50–100 years
18. The innovator's notebook: new ideas from the synthesis
19. Corrections ledger: what we got wrong and fixed
20. Open questions, rankings and the roadmap
21. Appendices: number card, glossary, opportunity map, method log, source registers

---

# 0. The answer on one page

**The problem is not "replace RSA with ML-KEM".** For OT and embedded systems, post-quantum migration is a special case of a broader failure. **Long-lived devices cannot safely accept change.** They resist new algorithms, new owners, new software, new authority and new epochs of trust. The quantum computer is the first change agent with a deadline, but not the last. [I]

**Living systems have faced this problem for a very long time.** An immune system must accept new defences without attacking itself. A bee colony must replace its queen without a ruler to order it. A tree must survive centuries of wounds it cannot heal. A seed must wait out decades without a clock. The solutions they converged on map closely onto the engineering answer below, and in four places they changed it (Part 5).

**What actually breaks.** Real-time OT data paths (IEC 61850 GOOSE and Sampled Values, DNP3-SA, SecOC, LoRaWAN) are already symmetric. AES and HMAC survive quantum attack. [F] The exposure sits in **authority**:
- who may sign firmware, configuration and settings;
- who may unlock debug, transfer ownership or inject keys at the factory;
- how long-term symmetric keys were first delivered.

An attacker who can forge classical signatures after a cryptographically relevant quantum computer (CRQC) exists does not need to decrypt anything. They sign. [I]

**Three findings from the earlier passes reshaped the direction.**
1. **The binding constraint is not the boot ROM but update adoption.** In one vendor analysis, 60% of PLCs ran firmware with eight or more exploitable CVEs although fixes had existed for over ten years [V]. Only 15% of facilities patch in routine maintenance windows [2nd]. A post-quantum signature that nobody installs protects nothing.
2. **Many existing MCUs can already host a post-quantum, hash-based, immutable first stage in locked flash**, without new mask ROM (Nordic NSIB, ST OEMiRoT [F]). The earlier plan to licence a new kernel into silicon aimed at the wrong bottleneck.
3. **The worst exposures are classical side doors around secure boot:** debug-unlock certificates, ownership-transfer messages, FDO vouchers, factory key injection and engineering-workstation configuration authority. Each gives a quantum-capable forger full control without touching the boot chain. [F/I]

**Four findings from this edition changed it again.**
1. **Count assumptions, not algorithms.** Every standard post-quantum signature depends on SHA-2 or SHA-3/SHAKE, so there are **only two independent "waists"**. The previous edition's slot set was unsafe under a plain 2-of-3 rule: one Keccak failure handed an attacker a quorum. Accepting only quorums whose members share no assumption cuts the modelled attacker success about **19-fold** at almost no cost (M2, 10.3). Knight and Leveson's 1986 experiment and the 1970 corn blight say the same thing from software and from farming: diversity that shares a hidden dependency fails all at once.
2. **Order beats speed.** Treating migration as network immunisation, migrating the authorities and concentrators first (11% of a modelled fleet) shrank the worst-case blast radius of one forged credential from 100% to 4.5%. Random order needed **73%** coverage to reach 5%. Without an inventory, migrating a *neighbour* of a randomly chosen device cuts the work by about 40% compared with random order: 44% of nodes instead of 73% (M1). [C, synthetic topology]
3. **Unexercised capabilities decay, and the ground moves.** Spare slots that are never used fail when needed; the DNSSEC root rollover relied on an automated mechanism never tested at scale (7.3). Counters wrap inside asset lives (Year 2038; the next GPS week rollover is 20 November 2038). The grid clock is governed rather than physical: Europe's mains clocks ran about six minutes slow in 2018. Cheap crystals drift by more than an hour a year in a cold cabinet (Part 6). Hence two new root causes, R10 and R11, and a remedy nature uses everywhere: **exercise the change path on a rhythm** (slot drills, renewal rehearsals, prescribed burns; Ise Jingu has rebuilt on a 20-year cycle since 690).
4. **The lock faces two adversaries.** It defeats the remote, fleet-scale forger by design, because its integrity comes from write-protection, not a signature. Against someone holding a device, resistance varies by part. So the design must ensure **one opened device never yields fleet-wide authority**: the first stage holds only public hashes, and every device holds only its own keys (Part 8).

**What to build first, ranked robustly across two weightings** (Parts 11 and 20; this edition's additions in italics):
1. **An open, locked-flash continuity first stage** with a hash-based verifier and at least three key-hash slots spanning both hash waists, and a floor rule: *advancing the floor needs a signature from a different slot than the one being retired.* *Quorums must have disjoint assumption sets; the alternate slot is exercised by an annual slot drill; transitions follow the molting protocol (provision alongside, shadow-sign, hide, shed, harden).* [H, buildable now]
2. **Side-door closure.** Disable field debug after commissioning, use PQ debug credentials bound to device UUID, and audit every lifecycle transition. *Revocations must structurally be unable to target current authority (the CRISPR "PAM rule").* [H/F]
3. **Symmetric process-bus fabric.** ML-KEM-768 enrolment once; a KDC in the enclave with per-device key diversification; IEC 62351-6 MACs unchanged. *Keep the safety code separate from the cryptography, as railway signalling (EN 50159) does, so the cryptography can migrate without reopening the safety case.* [H, buildable now]
4. **PQ-capable FDO ownership vouchers with contractual escrow**, so an OEM exit does not orphan the fleet. *A signed OEM heartbeat whose absence releases the escrow within a defined window, modelled on how honeybee colonies detect and replace a lost queen.* [H]
5. **Maintenance-window-aligned staging.** Signed transition bundles wait dormant until the planned window; devices report signed state afterwards. *A small persister cohort is held back from every rollout, as bacteria hold back dormant cells, because security updates can themselves be the outage (CrowdStrike, 2024).* [H]
6. **Enclave containment with a dated exit** for devices that cannot change. *Migrate in class order, hubs first; announce cryptographic end-of-support dates, as medical-device guidance now expects (IMDRF N70).* [2nd/H]
7. **Fleet crypto-state evidence** in CycloneDX CBOM plus TCG/IETF attestation formats. *Steer by exposure-years, which integrates risk over time, not by "percentage migrated", which leaves a residual; renew evidence records before their algorithms age (RFC 4998).* [H]

**What nature teaches, compressed** (5.7): recognise self by structure; act irreversibly only on two independent signals; buy accuracy with time and stages; independence beats magnitude; prepare successors before you need them; signal liveness; seal what you cannot heal; degrade in steps; count what you cannot undo; let small changes prevent large catastrophes; restrain the defenders; keep the core small, conserved and doubled. **And where nature is the wrong teacher** (5.8): it optimises populations, not individuals, and it tolerates losses that a substation cannot.

**What was demoted to research:** new-ROM kernel licensing; a neutral custodian utility; threshold ML-DSA succession; a "time-free validity" product; linear pre-rotation (it saves only 1.5–3×); stateful LMS custody as a business (NIST draft SP 800-230 adds limited-use SLH-DSA sets for firmware signing [F, draft]).

**The hard boundary.** Some devices cannot be rescued by cryptography: an immutable verifier that only speaks a classical family, no lockable stage, and offline until a CRQC exists. Only physical presence, network containment or replacement helps them. So **every device shipped from now on should carry a multi-class, hash-anchored first stage.** Each year of delay adds devices to the unrescuable set. [I]

**The cheapest, highest-value experiments.**
- **E-A1:** a two-week desk survey of what fraction of industrial MCU families support a lockable, maker-defined immutable first stage. If ≥50% do, the software path wins. If <30% do, the new-ROM argument returns.
- **E-N7 and E-N3** (new): a two-week audit of every counter, time field and signature budget against asset life, and a four-week checker that rejects quorums sharing an assumption. Both look for flaws that stay invisible until they fail all at once.

---

# 1. How the understanding evolved

The investigation began as a global hunt for billion-dollar opportunities. Hardware and software were scanned first, then software alone. **OT and embedded post-quantum migration** stood out as an under-served problem with a regulatory clock. Six deep passes and one verification build followed. Each pass attacked the one before it.

| Pass | Central belief | What overturned or refined it |
|---|---|---|
| **1. First-principles reinvention** | Migration is more than algorithm swaps. It needs a managed **Industrial Trust Plane** of five planes (root, authority, session, knowledge, assurance), and root succession is the open problem. | Pass 2 found root succession *is* solved in outline (TUF/Uptane, RFC 5011, UEFI CA rotation, OpenTitan ownership transfer, DICE). It also found four missing layers: provisioning, time, revocation/decommissioning, governance. |
| **2. Audit and foundations** | The remaining gaps are narrow: immutable ROM verifiers, weak-device revocation, offline time, orphaned fleets, and **HNDL-to-authority** (a forgeable classical root can hijack the transition itself). The standalone market is small: $0.38–1.88B global. | The verification lab caught arithmetic slips (market sum, masking factor, IKE fragmentation framing, TLS downgrade nuance). Pass 3 reframed the whole problem. |
| **Verification lab (51 interactive scenes)** | Every quantitative claim must be recomputable. | Confirmed the FIPS/SP sizes, LoRa frame counts and SV budgets. Exposed the discrepancies listed in Part 19. |
| **3. Invention pass** | The root problem is *authority continuity*. The top invention is a hash-only, multi-family **Authority Continuity Kernel (ACK)** committed in ROM/OTP, plus symmetric-first operation, threshold succession, time-free validity and a neutral custodian. 110 hypotheses, 32 combinations, 11 architectures, a weighted top 20. | Pass 4 found three arithmetic errors, a self-contradiction in the "existing ROM" variant, deployed prior art making new ROM unnecessary, and two large problem areas absent from the model: **update non-adoption** and **classical side doors**. |
| **4. Second-pass challenge** | The thesis survives but moves layer. The bottleneck is adoption plus uninventoried authorisation paths. Build on existing standards (NSIB-style locked stages, FDO, SP 800-230, TPM 2.0 v1.85, CycloneDX). | The first synthesis reconciled the passes and added a device-class model, a five-kinds-of-change framing and new hypotheses (I-1 to I-12). |
| **5. Nature, physics and history pass (this edition)** | The architecture is right; what remains is detail. | Studying how immune systems, colonies, cells, seeds, trees and centuries-old institutions keep trust showed **design errors, not details**: a quorum rule that one hash failure defeats (M2), a migration order that wastes most of the effort (M1), a lock whose threat model mixed two adversaries (Part 8), and two missing root causes: **capabilities decay when unexercised (R10)**, and **the ground moves under long-lived devices (R11)**. It added 36 patterns, 18 problems, 22 ideas, 7 models and 15 corrections. |

**The hidden assumptions that, once challenged, changed most.** The first three came from the earlier passes; the last three from this edition.
1. *"The cryptographic root is the scarcest resource."* It isn't. The scarcest resources are **maintenance windows, people who understand the device, and authorisation paths nobody inventoried**.
2. *"Changing the immutable verifier requires new silicon."* Often it doesn't. A maker-defined locked flash region can be the immutable root, and its integrity comes from the **lock**, not from a classical signature.
3. *"Secure boot is the authority chain."* It is one of at least six chains. The others are debug, RMA/lifecycle, ownership, factory provisioning and configuration. The attacker uses the cheapest.
4. *"Diversity means using different algorithms."* It means **not sharing assumptions**, and post-quantum signatures share hash functions. Two waists, not three classes.
5. *"A device that works on the day it ships keeps working if left alone."* Unused paths rot, counters wrap, clocks are governed, networks are switched off and roots expire. Long life needs **rhythm**: scheduled, rehearsed, small changes.
6. *"Migration progress is a percentage."* It is a **graph and an integral**. Which devices migrate first matters more than how many, and the risk that remains is the area under the curve, not the last data point.

---

# 2. Foundations: the threat, the mathematics, the machines, and the extinction record

## 2.1 What a quantum computer breaks, and what it does not

- **Shor's algorithm** solves factoring and discrete logarithms in polynomial time by finding the period of a modular function with the quantum Fourier transform. RSA, DH, ECDH, ECDSA and EdDSA all fall. [F]
- **Grover's algorithm** gives only a square-root speed-up on unstructured search, and it parallelises poorly. AES-128 drops to about 2⁶⁴ ideal serial work; AES-256 stays comfortable. Hash functions at 256 bits remain strong. [F]
- The verification lab built working toys:
  - Shor for N = 15: 7ˣ mod 15 has period 4, and gcd(48,15)=3, gcd(50,15)=5 give the factors.
  - A Diffie–Hellman toy (p = 23, g = 5): secrets 6 and 15, shared secret 2. [C]

| Primitive | Role in OT | Quantum status |
|---|---|---|
| AES, HMAC/CMAC/GMAC | GOOSE/SV MACs, DNP3-SA, SecOC (often 24-bit truncated CMAC), LoRaWAN | Safe |
| SHA-2 / SHA-3 | Image digests, Merkle trees, hash-based signatures | Safe |
| DH/ECDH, RSA key transport | TLS, IKE, OPC UA channel setup, Zigbee SE, **provisioning and key delivery** | **Broken** (and harvestable today) |
| RSA/ECDSA/EdDSA signatures | Firmware, certificates, boot keys, **debug, ownership, licences** | **Broken** (forgeable once a CRQC exists) |

**Two different exposures:**
- **Confidentiality (harvest now, decrypt later, HNDL).** A recording made today is decrypted later. In OT this mainly threatens **key-delivery sessions**: recover the long-term symmetric key and everything after it opens. It also threatens firmware-encryption keys wrapped with RSA/ECDH (firmware IP exposure). [I]
- **Authority (harvest now, forge later).** Signatures cannot be forged retroactively. But every *trust anchor still accepted* when a CRQC arrives becomes forgeable. For a relay with a 30-year life, or a ROM key, the exposure equals the **lifetime of what trusts the key**. [I]

## 2.2 How close is a cryptographically relevant quantum computer?

| Estimate | Claim | Status |
|---|---|---|
| Gidney (arXiv 2505.15917, May 2025) | RSA-2048 with <1 M noisy qubits in under a week. Assumes 0.1% gate error, 1 µs surface-code cycle, 10 µs reaction time. The 2019 estimate was 20 M. | [F] |
| Google Quantum AI (30 Mar 2026) | ECDLP-256 with ≤1,200 logical qubits / 90 M Toffoli, or ≤1,450 / 70 M; <500 k physical qubits; minutes. The disclosure used a zero-knowledge proof. | [F] |
| Alice & Bob (IACR ePrint 2026/2665, Oct 2026) | RSA-2048 with 22,593 cat qubits in 3.14 days (LDPC-cat codes, down from 49,649). ECDLP-256 with ≤29,588 qubits in 61.8 min. Assumes **no bit flips**; at about one flip per hour, RSA needs ~45,000. The demonstrated error correction is a distance-3 repetition code, not yet below threshold. | [F]/[2nd] |
| Iceberg "Pinnacle" preprint | RSA-2048 with <100 k physical qubits (qLDPC) | [2nd], not rechecked |
| Quantinuum Helios (Nov 2025) | 48 logical / 98 physical qubits demonstrated | [2nd] |

**Reading the trend [I]:**
- Resource estimates fell by more than an order of magnitude in seven years, and **elliptic curves now look cheaper to break than RSA**. Most OT certificates and debug credentials are ECC.
- Demonstrated machines are still one to two orders of magnitude short in logical qubits.
- A naive surface-code count (1,200 logical × (2d²−1) physical) exceeds Google's quoted <500 k, so the published designs use denser accounting. Do not compute physical counts naively. [C]
- Google's use of a zero-knowledge disclosure means independent groups cannot fully check the estimate (problem N54).

**Policy treats the date as known even though science does not:**

| Regime | Requirement | Status |
|---|---|---|
| NIST IR 8547 (final, 27 Oct 2026) | Quantum-vulnerable public-key algorithms deprecated after 2030, disallowed after 2035, at all key sizes. NIST staff said the 2035 disallowance was not aimed at hybrid modes. **For devices that cannot be updated, the code-signing keys should be quantum-resistant from the start**, and it points to the stateful hash-based schemes (LMS, XMSS) for that use. | **[F] — checked at the primary in this edition** |
| US Executive Order of 22 June 2026 ("Securing the Nation Against Advanced Cryptographic Attacks"; EO 14412 per two secondaries) and OMB M-26-15 | PQC key establishment for high-value assets by 31 Dec 2030; signatures by 31 Dec 2031; migration plans within 120 days | [2nd]/[F] (OMB PDF cited) |
| NSA CNSA 2.0 (FAQ v2.1) | Firmware signing: PQ preferred 2025, exclusive 2030. Names LMS/XMSS, and v2.1 excludes HSS and XMSS^MT. "Starting in 2027, no new product for NSS should have a burned-in root of trust relying on a non-QR primitive." New NSS acquisitions compliant from 1 Jan 2027; non-compliant equipment phased out by 31 Dec 2030; all NSS by 2035. Algorithms: ML-KEM-1024, ML-DSA-87, LMS/XMSS for firmware. | [2nd] |
| EU Cyber Resilience Act | Reporting obligations from 11 Sep 2026; full obligations from 11 Dec 2027. Support period ≥5 years (Art 13(8)); updates available ≥10 years (Art 13(9)). **Article 14 reporting also covers products already on the market.** | [F]/[2nd] |
| India DST Task Force roadmap (2026) | Critical information infrastructure: foundations 2027, priority migration 2028, completion 2029. Power, telecom and ONGC named as urgent. Recommends containing "classical-only systems within controlled enclaves where immediate migration is not feasible". Test labs by Dec 2026. | [2nd] (DST PDF cited) |
| EU Coordinated Implementation Roadmap (NIS Cooperation Group, June 2025) | Member states start the transition by the end of 2026; high-risk use cases by the end of 2030; as many systems as feasible by 2035 | [2nd] |
| UK NCSC, Australia ASD | Comparable 2030–2035 horizons | Cited earlier, **not rechecked** |

**India's 2029 critical-infrastructure date is the most aggressive in the world for OT.** Set against 15–30-year asset lives, it makes **enclave containment the de facto national strategy** for most installed OT. That is a large, concrete market for containment, evidence and labs. [I]

## 2.3 The post-quantum toolkit, with sizes recomputed

**Lattices (Module-LWE).** Security rests on recovering s from b = A·s + e (mod q) when the noise e is small. ML-KEM (FIPS 203) uses q = 3329 and 256-coefficient polynomials. Its Fujisaki–Okamoto re-encryption check with **implicit rejection** turns a passively secure scheme into one secure against chosen-ciphertext attack.

| Object | 512 | 768 | 1024 | Formula |
|---|---|---|---|---|
| ML-KEM encapsulation key | 800 B | 1,184 B | 1,568 B | 384k + 32 [C] |
| ML-KEM ciphertext | 768 B | 1,088 B | 1,568 B | 32(k·d_u + d_v) [C] |

**ML-DSA (FIPS 204)** is built on Fiat–Shamir with aborts. The signer rejects any candidate z = y + c·s that would leak s, so **signing time is a random variable with a long tail**. Verification is deterministic.

**Hash-based signatures.**
- LMS/XMSS (SP 800-208) are **stateful**: reusing a one-time index enables forgery. The lab demonstrated a real forgery from WOTS reuse with SHA-256.
- SLH-DSA (FIPS 205) is stateless but large.
- Draft **SP 800-230** adds six limited-use SLH-DSA sets for software, firmware and certificate signing, capped at 2²⁴ signatures per key. They are "not approved for general-purpose use". [F, draft]

| Signature system | Public key + signature (bytes) | Notes |
|---|---|---|
| ECDSA P-256 | 64 + 64 | Classical baseline |
| FN-DSA-512 | 897 + 666 | FIPS 206 not final |
| LMS SHA-256/192, h=10, W8 | 48 + 900 | [C] |
| LMS SHA-256/192, h=10, W4 | 48 + 1,500 | [C] |
| LMS SHA-256, h=10, W8 | 56 + 1,452 | [C] |
| LMS SHA-256, h=10, W4 | 56 + 2,508 | [C] |
| ML-DSA-44 / 65 / 87 | 1,312+2,420 / 1,952+3,309 / **2,592+4,627 = 7,219** | [C] |
| SLH-DSA-128s / 192s / 256s (FIPS 205) | 32+7,856 / 48+16,224 / 64+29,792 | [F] |
| SP 800-230 limited-use sets | smallest ≈3.9 KB (unofficial post); bc-java lists 7,752 B (192-bit) and 14,944 B (256-bit) | **Conflicting secondary data; wait for the final standard** |

LMS size formula (RFC 8554 / SP 800-208): u = ⌈8n/w⌉, v = ⌈(⌊log₂((2ʷ−1)u)⌋+1)/w⌉, p = u+v, and signature = 4 + (4 + n + p·n) + 4 + h·n. For n = 32, W4: p = 67, so the signature is 2,508 B. For W8: p = 34, so 1,452 B. [C]

**The structural insight the passes converged on [I]:** hash functions are the only primitive shared by every NIST PQ family. ML-KEM and ML-DSA use SHAKE/SHA-3; LMS and SLH-DSA-SHA2 use SHA-256. **A hardware hash engine is therefore the universal post-quantum accelerator**, and hash-based verification is the most conservative long-term anchor. But SHA-2 and SHA-3 are *different* assumptions. A "hash-only" design that uses only SHA-256 is itself a monoculture (Part 10.3).

## 2.4 The machines: what fits where

**Embedded benchmarks and their reliability**

| Measurement | Value | Source | Status |
|---|---|---|---|
| ML-DSA-44 signing on RP2040 (M0+) | mean 158.9 ms, p99 584.2 ms, max 1,156.8 ms over 10,000 runs; iteration count recoverable from wall-clock time | arXiv 2603.19340 | [D] |
| ECDSA P-256 vs ML-DSA-44 verify on RP2040 | **321 ms vs 44.0 ms** | same | [D]: PQ verification can be *cheaper* than classical |
| ML-DSA-44 signing stack | 44,832 B (pqm4, M4F) / 50.6 KB reference C; ML-DSA-87 119.6 KB | pqm4; inherited | [D]. **Conflict:** the RP2040 paper snippet reports 8.4–8.9 KB memory. Unresolved; it may count a different quantity |
| ML-KEM-768 decapsulation | 22.0 ms on M0+, 14.2 KB stack; wolfSSL 8.3 ms on a newer STM32 (clock not stated) | inherited; [V] | — |
| Masked vs unmasked ML-KEM decapsulation | 2,978,441 vs 707,827 cycles = 4.21× | [C] from quoted cycles; the 3.5× figure stated elsewhere does not reproduce | — |
| LMS verify, SHA-256, Cortex-M4 (Campos et al., ePrint 2020/470) | **2,658,884 cycles at W4 (Winternitz value 16), h = 10, ~1,044 B stack; 23,252,036 cycles at W8 (value 256), h = 5** | [D] | Earlier passes mislabelled "w=16" and paired the W4 cycles with the W8 size (fixed in Part 19) |
| LMS verify on nRF52840 @64 MHz | 123 ms, 1,580 B stack | arXiv 2106.05577 | [D] |
| SLH-DSA-SHAKE-128s verify with SLotH hash unit | 179,603 cycles; software Keccak ≈12,000 and SHA2-256 ≈3,000 cycles per call on M4 | Saarinen 2024 | [D]: hash hardware gives roughly two orders of magnitude |

**Boot-time arithmetic, corrected [E]:**
- W4 software: 2.66 M / 64 MHz = **41.5 ms** (signature 2,508 B).
- W8 software: 23.25 M / 64 MHz = **363 ms** (signature 1,452 B).
- W8 with hardware SHA at an assumed ~100 cycles/compression instead of ~3,000: 23.25 M × 100/3,000 ≈ 0.78 M cycles ≈ **12 ms**.
- **Rule:** use W4 without a hash engine and W8 with one. Image hashing often costs more than signature verification. A hardware SHA engine matters more than the choice between ECDSA and PQ.

**Design consequence [I].** Constrained endpoints can **verify** and **decapsulate**. They should almost never **sign**. Signing belongs in gateways and HSMs. That decides where signing keys live and therefore the threat model.

**Silicon readiness, from deployed evidence to unverified claims**

| Part / project | Claim | Status |
|---|---|---|
| Nordic NSIB | Immutable bootloader in write-protected flash; key hashes (OTP on nRF91/nRF5340); a higher key index invalidates lower ones | [F], deployed |
| ST OEMiRoT | Unique boot entry + write protection + RDP L2 + HDP make user-flash code immutable | [F] |
| TI AM263P4 | ROM cannot verify PQC; PQC planned in a secondary bootloader | [F] (vendor forum) |
| OpenTitan | Docs say the ROM supports ML-DSA-87 via OTBN. RFC #30765 lists gaps: keys don't fit OTP slots, ownership is ECDSA-only. Proposes ML-DSA-87 + P-384 hybrid. | **Conflicting; treat as in progress** |
| Microchip MEC175xB | "Embedded immutable PQC" (ML-KEM, ML-DSA, LMS verify) | [V]; a **notebook/data-centre embedded controller, not OT evidence** |
| NXP MCX A5 | PQC hybrid secure boot in ROM | [V], not rechecked |
| ST STM32G5 (announced 3 Nov 2026) | Hardware core for LMS, ML-KEM, ML-DSA, SLH-DSA | [V] |
| Caliptra Adams Bridge ML-DSA accelerator | Independent CPA attack on the Oct 2024 release with 10,000 traces; the project's own TVLA shows leakage from ~5 K traces with masking off, and passes 1 M traces with masking on | [D] |
| TCG TPM 2.0 Library v1.85 (Mar 2026) | ML-KEM endorsement key, ML-DSA attestation key | [F]; **installed TPMs stay classical** |

**Pattern [I]:** PQ root-of-trust silicon arrives in data-centre and PC parts first. Industrial MCUs lag (N55). Shipped PQ accelerators can leak, so "PQ in hardware" is not "PQ done".

## 2.5 The wire: protocols and real-time budgets

- **Process bus.** IEC 61850-9-2 Sampled Values at 4,000–4,800 frames/s leave **208–250 µs** per frame. Per-frame public-key signatures are infeasible with *any* scheme, classical or PQ, so the data path stays symmetric. [C]
- **Hybrid TLS 1.3** (X25519MLKEM768, codepoint 0x11EC):
  - The client key share is 1,184 + 32 = **1,216 B**; the server's is 1,088 + 32 = **1,120 B**. [C]
  - The ClientHello grows past one 1,500-byte MTU, and some middleboxes mishandle the split.
  - TLS 1.3 downgrade protection is only as strong as the handshake's own primitives against a real-time quantum-capable active attacker. Hence "hybrid-strict" pinning.
  - CVE-2026-2673 shows OpenSSL TLS 1.3 servers using DEFAULT negotiating a weaker group than configured. [F]
- **IKEv2.** IKE_SA_INIT cannot be fragmented. PQ key exchange therefore goes in **IKE_INTERMEDIATE** (RFC 9242) with RFC 9370 multiple key exchanges, where RFC 7383 fragmentation applies. [F]
- **LoRaWAN EU868.** Payload is 51 B at SF10–12, so an ML-KEM-768 key needs **24 frames** and an ML-DSA-65 signature **65 frames**. With the 1% duty cycle, adding a KEM over the air is impractical. [C] LoRaWAN itself needs no public-key exchange; its PQ issue is provisioning and the join server.
- **IEC 62351-9:2023** distributes GOOSE/SV/PTP group keys via GDOI. PQ is discussed in Annex B.11, but no PQ mechanism is mandated. [2nd]
- **OPC UA.** No PQ security policy was found (1.05.07 adds ECC). Field reports of AutoAccept and SecurityMode=None mean many deployments are insecure before PQ even matters. [V/2nd; OPC Foundation primary not checked]
- **Composite ML-DSA** (IETF LAMPS draft in the RFC Editor queue) gives EUF-CMA, not SUF-CMA. Signatures can be malleable, which matters if images or logs are deduplicated by signature bytes. RFCs 9881, 9909 and 9964 are published. [F]

## 2.6 The extinction record: cryptographic families do fail suddenly

The case for multi-class trust anchors rests on one empirical claim: cryptographic families, and the implementations of sound families, can fail suddenly, years after deployment. This pass checked the record. [F unless marked]

| Year | What failed | How fast, how cheaply | Status at the time | Lesson |
|---|---|---|---|---|
| 2012 | **MD5 in Microsoft code signing (Flame malware)** | An attacker forged a certificate chaining to the Microsoft Root Authority using a new variant of an MD5 chosen-prefix collision. The certificate came through Terminal Server Licensing enrolment, which used MD5 with predictable serial numbers. Microsoft revoked the hierarchy (Security Advisory 2718704; Stevens, CWI). | MD5 had been known to be broken since 2004–2008 but was still trusted in a corner of the PKI | **Forged authority through cryptanalysis has already happened at nation-state level**, through a forgotten side path. That is the CRQC scenario in miniature, and a side-door warning |
| 2017 / 2020 | **SHA-1** | SHAttered: 2⁶³·¹ compressions, about 6,500 CPU-years / about 100 GPU-years. Shambles (2020): chosen-prefix collision at 2⁶³·⁴, estimated at about US$45k of rented GPU time (the authors' actual run cost US$75k), demonstrating PGP key impersonation. NIST set a phase-out deadline of 31 December 2030. | Theoretical attacks first appeared in 2005 | **From first theoretical attack to retirement took about 25 years.** Hash families decay slowly and visibly |
| Feb 2022 | **Rainbow** (multivariate signatures) | Key recovery for the security-level-1 parameters in an average of 53 hours on a standard laptop (Beullens, ePrint 2022/214; CRYPTO 2022) | One of NIST's three round-3 **finalist** signature schemes | **A finalist fell over a weekend** |
| Jul 2022 | **SIKE / SIDH** (isogenies) | SIKEp434 broken in about an hour on a single core in the first version of the paper, about ten minutes in the revised version. Microsoft's US$50k IKEp217 challenge fell in about six minutes (Castryck & Decru, ePrint 2022/975). | Selected as a NIST round-4 candidate on 5 July 2022, **25 days before the attack** | **A family can go from standard-track to dead in under a month**, on a laptop |
| 2020 | **GeMSS** (multivariate) | Parameters shown "not as secure as claimed" (Tao, Petzoldt & Ding, ePrint 2020/1424) | Round-3 alternate | Security margins erode before outright breaks |
| Apr 2024 | **Lattices, briefly** | A preprint claimed a polynomial-time quantum algorithm for LWE. About a week later its author withdrew the claim after a bug was found (Chen, ePrint 2024/555). | — | **A single preprint can put a whole class in doubt for days.** Operators need a policy for "suspected" breaks, not only confirmed ones |
| Dec 2023 – 2024 | **KyberSlash** (implementations of ML-KEM's predecessor) | A secret-dependent timing leak in many widely used libraries, including the reference code, allowed key recovery in published demonstrations. Most libraries were patched by early 2024 (Bernstein et al., TCHES 2025) | The **algorithm** was fine | Implementations fail more often than mathematics |
| 2024 | **Clangover** | Some compiler versions turned constant-time ML-KEM reference code into a secret-dependent branch, making key recovery possible (public research disclosure, 2024) | The source code was constant-time | **The compiler can silently remove a security property.** Verify binaries, not only sources |
| 2023–2025 | **ML-DSA (Dilithium) signing implementations** | Academic side-channel and fault-injection research showed that unprotected embedded *signing* implementations can leak their keys (for example Ulitzsch et al., TCHES 2023; Zhou et al., TCHES 2025). Related work showed fault attacks against hash-based *signing* (SPHINCS+) as well | Unprotected or partially protected implementations | **Signing on constrained or physically exposed devices is a key-extraction risk.** Keep signing in hardened HSMs with fault countermeasures |
| 2024–2025 | **Adams Bridge ML-DSA accelerator** | Masking leakage found by independent analysis (Part 2.4) | Open-source silicon root of trust | PQ in hardware is not PQ done |

**NIST's own response is diversification.**
- When it selected the first four post-quantum algorithms (5 July 2022), NIST kept SPHINCS+ (now SLH-DSA) explicitly as a **hash-based backup** because the other selections all rely on structured lattices.
- In September 2022 it opened a call for **additional signatures not based on structured lattices**; Round 3 was announced on 14 May 2026.
- On 11 March 2025 it selected **HQC**, a code-based KEM "based on a different math approach than ML-KEM", as a backup. A draft standard is expected around 2026 and a final in 2027. [F]

**What the record teaches [I]:**
1. **Mathematical breaks are sudden and cheap when they come.** Laptops, days, weeks.
2. **Implementation and side-channel breaks are far more frequent** than mathematical ones, and they hit sound algorithms. Diversity must extend to *implementations*: two independently written, formally verified verifiers per class (Part 11.1).
3. **Hash functions die slowly.** From first theoretical attack to retirement, SHA-1 took about 25 years, and the decay was visible throughout. That is why hash-based anchors are the conservative "germline", and why the two-waist rule (SHA-2 and SHA-3) is a hedge against slow, visible decay rather than overnight collapse.
4. **The standards bodies themselves hedge.** An OT trust design that commits to a single post-quantum family is less conservative than NIST's own portfolio.

---

# 3. The problem universe, compressed to its root causes

Across the passes, **108 distinct problems** were catalogued: 35 in the first problem universe (P1–P35), 55 added by the second pass (N1–N55), and 18 added in this edition's nature, physics and history pass (N56–N73). Listing them one by one hides the structure, so they are reorganised here by **root cause**. A small number of causes explains almost everything, and each cause points at an intervention layer.

## 3.1 Eleven root causes

The invention pass found seven root causes (R1–R7). The second pass showed that two of the largest problem clusters fitted none of them; both were added as **R8** and **R9**, and R1 was narrowed. This edition adds **R10** and **R11**, which emerged from studying how long-lived natural and human systems fail.

| Root cause | What it means at the deepest level | Problems it explains |
|---|---|---|
| **R1. Algorithm-bound immutable anchors** | The only code nothing can overwrite verifies one algorithm family. It was chosen 18–36 months before the chip shipped, for a device that lives 20–40 years. | P1 monoculture, P2 HNDL-to-authority, P8 frozen ROM, P9 scarce OTP, P11 silicon cadence vs asset life, P12 single-format boot chain, P16 never-updatable, N12 un-upgradable TPM/SE, N20 unfixable first-stage bug, N55 OT silicon lag |
| **R2. Validity tied to wall-clock time** | Certificates and policies expire by date, but offline devices have no trustworthy date. | P15, P22 catch-up, P24 stale spares, P26 offline revocation, P27 expiry as an authority cliff (the UEFI 2011 CAs expired 24 Jun, 27 Jun and 19 Oct 2026), N23 |
| **R3. Authority tied to one organisation** | The OEM is the only party able to authorise change, and nothing defines what happens when it leaves. | P13, P23 orphaned fleets, P31 responsibility gap, N7 voucher holders, N41 bankrupt signer, N49 unpriced sunsets, N52 M&A diligence |
| **R4. Public-key work pushed to every endpoint** | Every device is expected to do asymmetric operations, even where symmetric cryptography suffices. | P4, P10 RAM, P17, P18 fragmentation, P19 process bus, P20 group keys, N10 shared keys |
| **R5. Cryptography co-located with safety** | Crypto shares the core, the timing and the change process with the safety function. | P28 recertification, P29 watchdog (584 ms p99 vs a ~100 ms deadline), P30 fail-safe vs fail-secure, N48 bundled recertification |
| **R6. Copyable or rewindable state** | Keys, counters and indices live where backups, clones or restores can move them backwards. | P3 LMS reuse, P25 backups, N22 floor burn, N39 restored archives, N51 HSM portability |
| **R7. Invisible state and misaligned incentives** | No device states what it trusts, and no party is paid to know. | P32, P33, P34, P35, N31 incompatible "done", N32 unverifiable claims, N35 insurers, N50 |
| **R8 (new). Change does not get installed** | Updates exist but are not applied. The cost of a window, the risk of misoperation and recertification make "don't update" rational. | **N13** (60% of PLCs with fixes >10 years old [V]), **N14** windows collide with emergencies, **N15** 25–34% of OT advisories ship with no patch [V], N33 downtime dwarfs labour, N34 no substation benchmark |
| **R9 (new). Uninventoried authorisation paths** | Several classical paths besides secure boot can change code, keys, ownership or debug state, and nobody maps them. | **N1/N2** debug unlock, **N3/N4** RMA and lifecycle, **N5/N6** ownership transfer and FDO vouchers, **N8** factory key injection, N9 firmware-encryption key wrap, N11 DICE/IDevID identity certs, N16 feature licences, N17 relay settings and SIS logic, N18 workstations, N19 remote-access portals, N36 refurbished gear |
| **R10 (this edition). Unexercised capabilities decay** | Mechanisms and skills that are used only once a generation rot before they are needed: algorithm slots, rollover automation, ceremony knowledge, extension points. | **N57** agility atrophy, **N61** skill extinction, **N64** untested automation (the DNSSEC root rollover relied on an automated-update mechanism never tested in production), N45 strict pinning breaks interoperability, N25 draft OIDs |
| **R11 (this edition). The ground moves under long-lived devices** | Counters wrap, shared clocks are governed rather than physical, networks and certificate roots are switched off, and jurisdictions change the rules, all within one device lifetime. | **N56** time-counter overflow (Y2038, GPS week rollover), **N59** governed clocks, **N63** infrastructure sunsets (3G, analogue lines, root expiries), **N65** jurisdictional constraints on remote operation, P27 certificate cliffs |

**Why R8–R11 matter more than R1 [I].** R1 is real but its fix is cheap and partly deployable now (Part 11.1). R8 decides whether *any* fix reaches the field. R9 decides whether the boot-chain fix even protects the device: an attacker who can forge a debug certificate never touches the boot chain. R10 and R11 decide whether a design that works on the day it ships still works in year 20: the slot that was never exercised fails when needed, and the counter that was never sized wraps.

## 3.2 The 55 problems the earlier model missed

The full list is given because these are the "unknown unknowns" the investigation set out to find. Each is distinct from P1–P35. **[F]** means documented, **[I]** inferred, **[H]** plausible but unverified.

**Side doors and lifecycle authority**

| ID | Problem | Basis |
|---|---|---|
| N1 | Classical debug-unlock tokens grant full access after a CRQC (Silicon Labs Series 2 signs with ECDSA-P256-SHA256) | AN1190 [F] |
| N2 | Debug certificates chain to the RoT keys, so a RoT break opens debug fleet-wide unless each certificate is bound to a device UUID | NXP AN13814 [F] |
| N3 | RMA lifecycle authorisations outlive product support | Infineon TRAVEO [F]; [I] |
| N4 | RDP Level 2 is permanent and blocks RMA, which tempts OEMs to ship weaker locks | ST [F]; [I] |
| N5 | Ownership-transfer messages are ECDSA-signed | OpenTitan [F] |
| N6 | FDO vouchers are classical and sit off-device for years: harvest-now-forge-later on ownership | FDO spec [F]; [I] |
| N7 | Whoever holds the voucher files when the OEM exits controls onboarding | [I] |
| N8 | Contract-manufacturer key injection under classical key wrapping | [H] |
| N9 | Firmware-encryption keys wrapped with RSA/ECDH are harvestable, exposing firmware IP | [I] |
| N10 | A fleet-wide shared symmetric key means one extraction compromises everything | [I] |
| N11 | DICE/IDevID identity certificates on ECDSA allow device impersonation | [I] |
| N12 | Installed TPMs and secure elements cannot gain PQ (v1.85 helps only new parts) | TCG [F]; [I] |
| N16 | Feature-licence and activation signatures become forgeable | [H] |
| N17 | Protection-relay setting files and safety-instrumented-system logic are unsigned or classically signed | [I] |
| N18 | Engineering workstations hold signing authority with weak custody (56% have an unpatched critical CVE) | Armis 2023 [V] |
| N19 | Vendor remote-access portals sit outside migration plans | [H] |
| N36 | Refurbished OT equipment carries a prior identity or unlocked debug | [H] |
| N37 | Certificates of decommissioned devices stay in trust lists | [I] |
| N53 | Spare-parts brokers resell devices with stale roots | [H] |

**Adoption and operations**

| ID | Problem | Basis |
|---|---|---|
| N13 | Patches available for more than 10 years remain uninstalled | aDolus [V] |
| N14 | Annual or biannual windows collide with emergency transitions | aDolus [V]; SANS [2nd] |
| N15 | 25–34% of OT advisories ship with no patch: 34% (2022); 28% of 531 (2023); 26% of 606 (2024), with 18% having neither patch nor mitigation; 25% (2025) | Dragos [V] |
| N33 | Downtime cost dwarfs visit cost, so crypto work waits for planned outages | ABB, S&C [V] |
| N34 | No public substation downtime benchmark exists | [I] |
| N45 | Strict hybrid pinning breaks interoperability, so operators disable security | [I] |
| N47 | AI configuration assistants bypass signing quorums | [H] |
| N48 | Crypto updates get bundled with recertification and delayed | [I] |

**State and transitions**

| ID | Problem | Basis |
|---|---|---|
| N20 | A bug in a locked first stage has no fix path | [I] |
| N21 | Flash locks resist remote attackers but, on some part families, not a local attacker with physical access; resistance varies by part (refined in this edition: N70, Part 8.1) | [I] |
| N22 | A monotonic floor can be burned by anyone holding a valid higher-index image, locking out the owner | NSIB [F]; [I] |
| N23 | A spare at key index k cannot boot an image at k+3 without catch-up | [I] |
| N39 | Restored engineering archives bring back old key indices | [I] |
| N40 | Merkle-committed future keys must stay secret for 20+ years | [I] |
| N41 | A bankrupt threshold signer freezes a fleet | [I] |
| N42 | Unauthenticated PTP undermines ordering and any time-based policy | [H] |
| N43 | KDCs and enclave gateways become fleet-wide targets | [I] |
| N44 | Agility configuration enables downgrade | CVE-2026-2673 [F] |
| N46 | Monitoring taps become privileged positions | [I] |

**Standards, regulation and markets**

| ID | Problem | Basis |
|---|---|---|
| N24 | Composite signatures are EUF-CMA only (malleable) | IETF [F] |
| N25 | Devices that pin draft OIDs become orphaned when the RFC changes them | [I] |
| N26 | PQ accelerators ship only partially masked | Adams Bridge [D] |
| N27 | Inconsistent benchmarks mislead procurement | arXiv 2603.19340 [D] |
| N28 | CRA reporting covers legacy products, but the duty to fix does not | [I] |
| N29 | A 5-year CRA support floor vs 20–40-year assets | [F]/[I] |
| N30 | India's 2029 date forces de facto unstandardised enclaves | [2nd]/[I] |
| N31 | Each regulatory regime defines "done" differently | [I] |
| N32 | Owners cannot verify OEM PQ claims until labs exist | DST [2nd] |
| N35 | Insurers have no crypto-state loss data | [H] |
| N38 | OPC UA AutoAccept and SecurityMode=None make PQ policy moot | [V] |
| N49 | Mid-support algorithm sunsets are unpriced in contracts | [I] |
| N50 | Devices cannot state which keys they trust | [I] |
| N51 | LMS state cannot migrate between HSM vendors | [I] |
| N52 | Facility M&A omits authority diligence (keys, vouchers, debug credentials) | [H] |
| N54 | Zero-knowledge-only resource estimates limit independent timeline checks | Google [F] |
| N55 | PQ RoT silicon arrives data-centre-first, and OT MCUs lag | [I] |

Candidates such as fuse ageing and flash retention lacked evidence and were folded into N20/N21.

## 3.2a Eighteen problems found by studying nature, physics and history

These did not appear in any earlier pass. Each comes from a precedent in Parts 5–8.

| ID | Problem | Basis |
|---|---|---|
| N56 | **Time and counter overflow inside the asset's life.** 32-bit Unix time overflows at 03:14:07 UTC on 19 January 2038, inside the service life of devices shipping now. GPS's 10-bit week counter rolled over in April 2019 and broke receivers. Every LMS tree (2ʰ), fuse bank and floor index is a counter that can run out | [F]; Part 6 |
| N57 | **Agility atrophy.** Alternate algorithm paths that are never exercised fail when finally needed. TLS needed GREASE (RFC 8701) because unexercised extension points ossified, and post-quantum ClientHellos broke servers that assumed one-packet hellos (tldr.fail) | [F]; Part 7.6 |
| N58 | **The hash waist.** Every standard post-quantum signature depends on SHA-2 or SHA-3/SHAKE, so at most two independent assumption classes exist | [C]; Part 9, M2 |
| N59 | **Shared "natural" clocks are governed.** Mains-synchronous clocks depend on grid operators' time-deviation management, and Continental Europe's clocks drifted by minutes in 2018 during a balancing dispute | [F]; Part 6 |
| N60 | **Evidence and reader obsolescence.** Vouchers, receipts and logs must stay verifiable for decades, but their algorithms weaken and their readers disappear (the BBC Domesday Project became practically inaccessible within 16 years). RFC 4998 renewal exists but is rarely used in OT | [F]; Part 7.4–7.5 |
| N61 | **Skill extinction between transitions.** Transitions every 20–30 years mean nobody in the organisation has done the last one (the Ise renewal cadence exists to prevent exactly this) | [I]; Part 7.1 |
| N62 | **Security updates as outages.** One faulty security content update crashed about 8.5 million Windows machines in hours (19 July 2024). Automated crypto updates in OT can fail the same way | [F]; Part 7.6 |
| N63 | **Infrastructure sunsets under long-lived devices.** 3G shutdowns stranded millions of alarm systems and vehicle safety features. The UK analogue switch-off disrupted telecare, with deaths reported. Root-certificate expiry broke old clients overnight. The classical-algorithm sunset of 2030/2035 will behave the same way for unchangeable devices | [F]; Part 7.6 |
| N64 | **Untested rollover automation.** The DNS root rollover relied on RFC 5011 automation never tested in production at that scale; telemetry revealed that about 5–8% of reporting resolvers were not ready, and the rollover was postponed a year | [F]; Part 7.3 |
| N65 | **Jurisdictional limits on remote operation.** India's CEA (Cyber Security in Power Sector) Regulations 2026, in force from 1 April 2027, allow remote operation of OT only from within India over dedicated channels isolated from the internet. Vendor-portal-based migration and remote key management models must change for Indian power utilities | [2nd: CEA notification coverage]; Part 14 |
| N66 | **Defence autoimmunity as a base rate.** Mature defence systems misfire on their own host at a structural rate (about 10% of people have an autoimmune disorder). Strict security mechanisms will misfire too, and must fail operational | [F/I]; Part 5, Pattern 4 |
| N67 | **Competing successor authorities.** After islanding or a disputed OEM exit, two valid-looking successors can split a fleet. No earlier design had a deadlock-breaking rule | [I]; Part 5, Pattern 12 |
| N68 | **Classical transparency layers.** Leading witness-cosigning designs use Ed25519 today (Sigsum), so an OT transparency layer built on them inherits a classical dependency. The C2SP cosignature specification already recommends ML-DSA-44 for new deployments | [F]; Part 7.5 |
| N69 | **Attackers move to the weakest remaining channel.** After EMV migrations, card-not-present fraud surged in several countries as fraudsters switched targets. In the US, where magnetic-stripe fallback stayed usable, the shift was gradual and much old-channel fraud simply continued (Kansas City Fed). Migrating the boot chain alone either moves attackers to the side doors or leaves them on the classical paths that remain | [F]; Part 7.6 |
| N70 | **Physical defeat of flash protections on some older MCU families.** Published research has shown that readout and debug protections on some older, widely deployed microcontrollers can be defeated by an attacker with physical access, and vendors addressed this in newer silicon rather than in firmware. The lead architecture's *physical* threat model must therefore be assessed per part | [F]; Part 8 |
| N71 | **Compiler-introduced side channels.** Some compiler versions turned constant-time ML-KEM reference code into a secret-dependent branch (Clangover, 2024). Verifying source code is not enough | [F]; Part 2.6 |
| N72 | **Stragglers after every irreversible step.** Even after a year of outreach, about 4% of reporting resolvers still did not trust the new DNS root key weeks after the rollover. Every irreversible fleet step leaves a residual that needs enclaves or visits | [F]; Part 7.3 |
| N73 | **Folklore as evidence.** Positive-citation bias can make unsupported claims look established (the mycorrhizal-network case in ecology). In this domain, the belief that "post-quantum verification is too slow for MCUs" was wrong: ML-DSA-44 verification measured faster than ECDSA P-256 on an RP2040 | [F/I]; Parts 2.4, 5.8 |

## 3.3 Security problems created by security solutions

This was the least explored dimension before the second pass. Every recommended mechanism creates a successor problem, and the recommendations in Part 11 carry their own mitigations.

| Mechanism | Successor problem it creates |
|---|---|
| Cryptographic agility | A downgrade surface (N44); infinitely configurable policy |
| A locked immutable first stage | Bugs that can never be fixed (N20); lock-in by design |
| Monotonic floors / sunset latches | Floor burn against the owner (N22); spares that cannot boot (N23) |
| RDP-style permanent locks | No RMA path, so OEMs ship weaker locks (N4) |
| Gateways and enclaves | Concentration (N43); "temporary" enclaves become permanent and nothing inside them migrates |
| A central KDC | One breach compromises a fleet unless keys are diversified (N10, N43) |
| Threshold authority | Liveness failure when a signer disappears (N41) |
| Hybrid strict pinning | Interoperability breaks, so security is disabled (N45) |
| Pre-committed future keys | Decades-long secrecy obligations (N40) |
| Monitoring and passive CBOM | Taps become privileged positions (N46) |
| Window staging | Attackers learn the windows |
| Automation and AI assistants | Bypass of human quorum (N47) |
| Automated, simultaneous security rollout | A global outage from one defective update (N62) |
| Two-signal and staged authority rules | Latency, and a malicious participant who stalls a legitimate change (bounded holds, then escalation) |
| Gossip of floors among peers | Prion-like spread of a corrupted state, unless only signed evidence is adopted (Part 5, Pattern 33) |
| Witness networks | A classical dependency (N68) and a new concentration point |

## 3.4 Information-theoretic limits that no design escapes

These are boundaries, not engineering gaps.

1. **The freeze limit.** An offline device cannot distinguish "no update exists" from "updates are being withheld". Without an external freshness signal, a freeze attack is undetectable. Designs can only *bound its effect*: staleness reduces privileges and never safety functions.
2. **The succession limit.** A device can accept a successor authority after its current family breaks only if there is an authenticated channel that outlives that family. That means either a pre-committed key or commitment from an independent assumption class, or physical presence.
3. **The collusion limit.** A full authorising quorum that colludes cannot be prevented, only *detected afterwards* (transparency) and *bounded* (rate limits, scoped capabilities).
4. **The commitment limit.** A hash commitment pins the future to choices made today. A 32-byte commitment can name any set of keys, but those keys' families are fixed at commitment time.
5. **The unrescuable set.** A device with a classical-only immutable verifier, no lockable stage and no physical access before a CRQC cannot be cryptographically re-anchored. The set grows with every such device shipped.

---

# 4. The hidden structure: how authority flows, and where it leaks

## 4.1 The authority graph (corrected)

The earlier model drew a single chain:

```
silicon ROM key → OEM root → release key → firmware → device identity
                → operator PKI/KDC → session keys → commands
```

The corrected graph has at least **six authority chains** converging on the same device. Each can change what the device runs or who controls it.

```
                       ┌──────────── (1) BOOT ───────────────┐
 ROM / locked stage ───┤ key-hash slots → firmware images    │
                       └─────────────────────────────────────┘
 (2) DEBUG     RoT-chained debug certs / unlock tokens ─────► full device access
 (3) LIFECYCLE TEST→PROD→RMA transitions, signed tokens ────► reopen debug, re-key
 (4) OWNERSHIP OEM→distributor→integrator→operator vouchers ► who may re-key
 (5) PROVISION contract manufacturer key injection ─────────► identity, KEK
 (6) CONFIG    engineering workstation → settings, SIS logic, project files
                                                    ▲
                     vendor remote-access portals ──┘ (often bypass all of the above)
```

**The weakest chain sets the security level.** Today (2), (3), (4) and (5) are classical on most parts, and (6) is often unsigned. Migrating chain (1) alone buys little until the others are mapped. [I]

**The same graph, seen as an hourglass (this edition).** Biology and the internet both evolve around narrow, conserved "waists": a few components everything depends on, with diversity above and below (Pattern 21). The authority graph has the same shape, with two waists that are easy to miss [I]:
- **The hash waist.** Every post-quantum signature in the standard toolkit depends on SHA-2 or SHA-3/SHAKE (M2). Diversity above the waist (lattice, hash-based, code-based) does not remove the dependency below it.

```
   ML-DSA    FN-DSA    SLH-DSA-SHAKE      |      LMS-SHA-256   XMSS-SHA-256   SLH-DSA-SHA2
        \       |       /                 |              \          |          /
         SHA-3 / SHAKE (Keccak)           |                SHA-2 (SHA-256)
               waist 1                    |                   waist 2
```
*(SP 800-208 also defines SHAKE-based LMS and XMSS parameter sets. Those sit on waist 1, so the parameter set, not the scheme name, decides the waist.)*

- **The organisational waist.** Many chains that look independent terminate in one OEM's signing infrastructure, one contract manufacturer or one remote-access portal. An attacker who reaches that waist reaches every chain above it.

Waists are not defects: they are what make a system evolvable. But each must be **conserved deliberately** (kept minimal, verified and monitored) and **counted honestly** when judging independence (the disjoint-quorum rule, 10.3).

## 4.2 Central nodes and their replaceability

| Node | Can it be re-issued? | Consequence |
|---|---|---|
| ROM verifier | No | Bottleneck, but bypassable by a locked stage on many parts |
| Locked first stage | No (by design) | Must be small, formally verified and multi-class |
| OEM release key | Yes | Needs custody (HSM) and a succession path |
| Debug root | Often equal to the RoT key | Must be separated and UUID-bound |
| Voucher holder | Yes, contractually | A new crown jewel |
| Engineering workstation | Yes | Highest exposure today (N18) |
| KDC / GDOI server | Yes | Concentration risk; diversify per device |
| Time sources | Yes | Avoid making safety depend on them |

## 4.3 Feedback loops

- **Reinforcing: deferral.** Uncertainty leads to deferral, which grows the classical installed base, which raises the eventual cost, which reinforces deferral.
- **Reinforcing: OEM exit.** Small OEMs cannot fund PQ roots, so customers distrust them, so they are more likely to exit, which leaves more orphans.
- **Reinforcing: patch avoidance (new).** Rare updates make each update riskier, which makes operators more reluctant, so updates become rarer still. **Breaking this loop is the largest lever in the system.**
- **Reinforcing: bundling (new).** Crypto changes bundled with functional changes trigger recertification, so updates are delayed further.
- **Balancing: regulation.** CRA, IR 8547, CNSA 2.0 and India's roadmap.
- **Missing: crypto state back to the operator.** No device reports what it trusts, so the system cannot be controlled. That makes fleet crypto-state evidence a control-theory necessity, not a dashboard.
- **Reinforcing: fuel accumulation (this edition).** Every deferred change adds untested paths and lost skills, so the eventual forced change is larger and more dangerous, which makes operators defer more. Fire ecology calls this the wildfire paradox (Pattern 29). It is the patch-avoidance loop seen over decades rather than years.
- **Reinforcing: skill extinction (this edition).** Transitions that happen once a generation leave no one who has done the last one, so each is harder than the last (R10; Ise, 7.1).
- **Balancing loop the programme must build: integral control (this edition).** Steering by "percentage migrated" is proportional control and leaves a permanent residual. Steering by exposure-years integrates the error and keeps pushing until the residual is gone (Pattern 34; M5).

## 4.4 Leverage points (consolidated and re-ranked)

The invention pass listed 30 leverage points. After the second pass they sort into four tiers.

**Tier 1: act on bottlenecks, high leverage, low burden**
1. A locked hash-based first stage with key-hash slots across ≥2 assumption classes.
2. A floor rule: advancing needs a signature from a different slot. This fixes floor burn.
3. Mapping and closing side doors: disable debug in the field, PQ debug credentials bound to UUID.
4. Aligning cryptographic change with existing maintenance windows: signed dormant staging.
5. Doing public-key work at enrolment only, and keeping the process bus symmetric.
6. FDO-style off-device ownership vouchers with a PQ profile and contractual escrow.
7. Procurement clauses: a hash engine, ≥3 slots over ≥2 classes, PQ debug and vouchers, no field debug.

**Tier 2: reduce cost or improve observability**
8. KDC with ML-KEM key transport and per-device diversification.
9. A workstation signing quorum for configuration and settings.
10. Witness co-signatures shipped with images (offline transparency).
11. Fleet crypto-state evidence (CBOM + attestation).
12. Separating revocation and anti-rollback fuse banks (OCP requirement).
13. Non-restorable monotonic counters.
14. Enclave containment with dated exit plans.
15. A pinned hybrid-strict policy where both ends are known to support it.

**Tier 3: valuable in specific niches**
16. Merkle-committed future key sets for decade-offline assets.
17. Physical-presence authority bridges for classical-only devices.
18. A crypto cell or partition for safety devices.
19. Rate-limited, capability-scoped authority.
20. SDLS-style ratcheted symmetric authority for disconnected assets.
21. Spares activation at installation.

**Added in this edition: leverage from ordering, diversity rules and rhythm**
22. **Migrate in class order, hubs first** (C5 authorities → C4 concentrators → C3 → C2 → C1 → C0). In model M1, migrating the 11% of nodes that are authorities and concentrators cut the worst-case blast radius from 100% to 4.5%. Random order needed 73% coverage for the same effect. This is network immunisation, and it is the single largest leverage point this edition found. [C, synthetic topology]
23. **Without an inventory, migrate acquaintances.** Pick any device and migrate what it trusts or talks to. In M1 this cuts the work by about 40% compared with random order (44% of nodes instead of 73%), using only local observation. [H, supported by M1]
24. **Count assumptions, not algorithms** (the disjoint-quorum rule, M2). Near-zero cost; cuts the modelled attacker success about 19×.
25. **Exercise the change path on a rhythm** (slot drills, renewal rehearsals, prescribed burns). Cheap per year, and the only remedy found for R10.

**Tier 4: demoted to research**

New-ROM kernels, neutral custodians, threshold ML-DSA, a time-free validity *product*, linear pre-rotation, attestation-priced insurance, sector root-of-roots, and a migration digital twin as a product (it is kept as an engineering rehearsal practice).

## 4.5 Problem-to-intervention-level matrix

●● means best leverage per unit of burden, ● useful, ○ poor, and — not applicable.

| Problem | Crypto | Silicon | Firmware | Protocol | Topology | Authority | Lifecycle | Procedure | Procurement | Standards | Remove the requirement |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Algorithm-bound anchors | ● | ● | **●●** locked stage | — | — | ● | ● | — | ● | ● | — |
| Update non-adoption | ○ | ○ | ● A/B | ● | ● | ○ | **●●** | **●●** window staging | ● | ○ | ● stable first stage |
| Debug / RMA | ● | ● | ● | — | — | ● UUID-bound | **●●** | ● | **●●** | ● | **●●** no field debug |
| Ownership | ● | — | ● | ● FDO | — | **●●** | ● | ● | ● | **●●** FDO-PQ | — |
| Large signatures | ● SP 800-230 | **●●** hash engine | ● | ● | ● | — | — | — | — | ● | ● verify once |
| Offline revocation | ○ | — | ● | — | ● | ● | ● | ● | — | — | **●●** no remote path |
| Process bus | — | — | — | ● | **●●** enclave | — | — | — | — | ● | **●●** keep MACs |
| Orphaned fleets | — | — | ● | ● | — | ● | ● | ● | **●●** escrow | ● | — |
| Legacy, un-updatable | ○ | ○ | ○ | ● | **●●** enclave | — | ● | ● | ● | — | — |
| Configuration authority | ● | — | ● | ● | ● | **●●** quorum | ● | ● | — | — | — |

**The pattern [I].** The highest leverage is rarely cryptographic. It sits in procedure, lifecycle, procurement and topology, plus **one firmware artefact**. "Remove the requirement" wins wherever a capability can simply be deleted: field debug, remote revocation paths for offline devices, and per-frame public-key work.

---

# 5. The Living Trust Codex: what nature already knows about long-lived trust

Every problem in this atlas has been faced, in some form, by living systems for hundreds of millions of years:
- recognising self from impostor;
- deciding together without a leader;
- replacing a failed authority;
- surviving a change of environment without dying in the transition;
- keeping time in the dark;
- living for centuries while being attacked.

This chapter goes through those solutions one mechanism at a time.

**The rule of this chapter.** A natural mechanism is used here only as a **source of candidate designs and of known failure modes**. Each pattern follows the same five steps:
1. what happens in nature, with the evidence;
2. the abstract principle;
3. the concrete OT/post-quantum mechanism it suggests;
4. where the analogy breaks;
5. its status and the test that would kill it.

Nothing here is accepted because it is natural. Several natural mechanisms that were copied naively into computer security failed, and §5.8 records them.

**A finding about method, from biomimetics research.** Vincent, Bogatyreva, Bogatyrev, Bowyer and Pahl (J. R. Soc. Interface, 2006) used TRIZ to compare how biology and technology resolve technical problems. They found **only about 12% similarity** between the two sets of inventive principles: technology solves problems largely by **manipulating the usage of energy**, while biology relies on **information and structure**, which technology largely ignores. [F]

That one observation matches the conclusion this investigation reached independently from the security side. The cheapest security gains come from **structure** (who can authorise what, in which order, with which independent evidence) and **information** (commitments, ordered records, self-description), not from **more computation**.

## 5.1 Recognition: knowing self from impostor

### Pattern 1 — Two signals before action (lymphocyte co-stimulation)

**In nature.** In the two-signal model of lymphocyte activation, antigen recognition (signal 1) alone does not activate the cell. Sustained signal 1 without a second signal inactivates it. The model was first proposed by Bretscher and Cohn (Science, 1970). Lafferty later proposed a distinct version in which the co-stimulatory second signal comes from the antigen-presenting cell. Bretscher's 2019 historical review in the Scandinavian Journal of Immunology separates the two proposals. [F]

**Principle.** A credential that matches is necessary but not sufficient for consequential action. A second, independent confirmation must arrive by a different path. A matching credential *without* the second signal should make the system **less** responsive to that credential, not merely reject the request.

**In OT post-quantum trust:**
- This is the biological form of the graded-authority rule (Part 18, I-2): boot with one valid class; change authority only with two.
- It adds something the earlier design lacked: **anergy**. A device that repeatedly receives validly signed authority-change requests *without* the required second class or window token should:
  - log the attempts;
  - put that key into a reduced-trust state, accepting it for boot verification but not for authority changes until a quorum re-enables it;
  - include the event in its signed state report.

  That turns repeated probing with a stolen or forged key into a visible, self-limiting event. [H]

**Where it breaks.** Lymphocytes are disposable, but a device's authority keys are not. Anergy must therefore be reversible by a quorum, or an attacker could use it to switch off the OEM's key (an availability attack). The reduced-trust state must never affect boot or safety functions.

**Status.** [H], buildable now. Kill test: in the E-B2 TLA+ model, check whether an attacker who can produce single-class signatures can use anergy to lock out the legitimate authority faster than a quorum can restore it.

### Pattern 2 — Delay commitment until evidence persists (kinetic proofreading)

**In nature:**
- Hopfield (PNAS, 1974) showed how a molecular machine can exceed the accuracy that binding energies alone allow. It spends energy on an extra, delayed, irreversible step during which wrong substrates are more likely to fall off. In his original scheme **one proofreading stage roughly squares the equilibrium error rate** (f₀ → f₀²).
- Measured overall fidelity in real systems is often far better: about 10⁻³ per amino acid in translation, and about 10⁻¹⁰ per base in E. coli replication once polymerase, exonuclease proofreading and mismatch repair are all counted. [F/D]
- McKeithan (PNAS, 1995) applied the same idea to T-cell receptors. After a ligand binds, the receptor complex must complete a series of modification steps before signalling, and **if the ligand unbinds, the accumulated steps reset**. This lets the cell tell foreign peptides from self-peptides of only modestly lower affinity.
- A modern restatement (Britain, Town & Weiner, eLife 2022) notes that ten proofreading steps can turn a twofold difference in binding lifetime into roughly a thousandfold difference in output. [F]

*Correction to an earlier draft.* "Error falls as fᴺ for N stages" is a simplification, not Hopfield's general result. This atlas now uses only the square-per-stage statement and the measured figures above.

**Principle.** Discrimination can be bought with **time and sequential confirmations** instead of a stronger lock. The impostor must hold its false state *continuously* through every stage, and **any lapse resets progress**.

**In OT post-quantum trust:**
- This is the mathematical heart of **hold-down periods** (RFC 5011's 30-day add hold-down) and staged authority changes.
- A new root, slot replacement or floor advance progresses through N stages, each confirmed by an independent observation:
  - a witness co-signature;
  - a second-class signature;
  - a planned-window token;
  - a technician's on-site confirmation;
  - consistency with what the fleet's other devices report.
- If any stage sees a contradiction, the change **resets** rather than pausing.
- With per-stage detection probability d, a forger's chance of completing N stages is (1−d)ᴺ (Part 9, model M3). With d = 0.3 it is 0.70 for N = 1, 0.17 for N = 5 and 0.058 for N = 8. With d = 0.5 and N = 8 it is 0.0039. [C]
- The honest cost is latency, and a small false-reset rate (0.8% for N = 8 at 0.1% false alarms per stage). [C]

**Where it breaks:**
- Biology proofreads millions of times a second.
- Authority changes are rare and slow, so the attacker has time to keep a false view consistent, for example by isolating a whole island.
- Stages must therefore be **independent in channel**, not merely repeated on one channel. Eight witness checks over the same compromised gateway are one stage, not eight.

**Status.** Existing practice (hold-down) plus a formalisation [H]. Kill test: E-B2 model checking with a channel-isolating adversary.

### Pattern 3 — Respond to danger, not to novelty (the danger model)

**In nature.** Matzinger (Annual Review of Immunology, 1994) argued that the immune system's driving force is detecting **danger**, meaning tissue damage, rather than foreignness as such. Tolerance or activation depends on whether a T cell receives a second signal from an antigen-presenting cell. Those cells are activated in the presence of tissue destruction. [F]

**Principle.** Novelty alone is a poor alarm in a world full of harmless novelty. Watch instead for the specific, consequential changes an attack *must* cause, and for actual harm.

**In OT post-quantum trust.** Fleet monitoring should not try to flag every unfamiliar packet; OT networks are full of unusual but harmless traffic. It should alarm on **authority-changing events**, which every authority attack must eventually produce:
- floor advances;
- slot replacements;
- lifecycle transitions (to RMA or debug);
- ownership-voucher redemptions;
- configuration-signature changes on safety-system logic.

It should also alarm on **physical-process damage signals**: consistency of process measurements with physics, discussed in Part 6.

This is an alarm design that a quantum-capable attacker cannot evade by forging better signatures, because the *effect* of forged authority is an authority change, and the effect is what is watched.

**Where it breaks.** Danger detection reacts after harm begins. For irreversible authority changes the response must be **pre-emptive**: the hold-down of Pattern 2 is what buys the time to react.

**Status.** [H]; cheap to adopt in the fleet-evidence product (Part 11.7).

### Pattern 4 — Regulate the defenders (tolerance, regulatory T cells, autoimmunity)

**In nature:**
- Thymic selection removes most self-reactive T cells or diverts them into regulatory T cells.
- Because this central tolerance is efficient but incomplete, escapees are made anergic or deleted in the periphery (Xing & Hogquist, Cold Spring Harb. Perspect. Biol., 2012).
- It still fails often. Across 19 autoimmune disorders in a UK cohort of about 22 million people, **10.2% of the population** (13.1% of women, 7.4% of men) had at least one (Conrad et al., The Lancet, 2023). [F]

**Principle.** Every defence system attacks its own host at a non-trivial rate, even after hundreds of millions of years of evolution. Mature defence architectures therefore contain **mechanisms whose only job is to restrain the defence**.

**In OT post-quantum trust.** The security mechanisms recommended in this atlas can all harm their owner:
- a floor burned by a valid but malicious image (N22);
- a mass revocation that bricks spares;
- RDP-style permanent locks that make RMA impossible (N4);
- strict hybrid pinning that breaks interoperability (N45);
- a fleet-wide update that takes the plant down. The CrowdStrike Falcon update of 19 July 2024 crashed an estimated 8.5 million Windows machines (Part 7). [F]

The regulatory layer this suggests:
- **"Thymic" policy testing.** Before a policy ships, run every *planned legitimate* future operation through it: the next three floor advances, an RMA, an ownership transfer, a spare activation. Reject the policy if any would be refused. [H]
- **Regulatory rate limits on destructive actions.** No more than k floor advances per window. Revocations that would invalidate all current slots must carry escrow and physical presence.
- **A designed "autoimmunity budget".** Assume the security subsystem *will* misfire, so every misfire must fail operational (last-known-good keeps running), never fail into a hazard.

**Status.** [H]; directly testable in the TLA+ model and in E1's power-cut fuzzing.

### Pattern 5 — An ordered memory that cannot target itself (CRISPR)

**In nature:**
- CRISPR arrays store short "spacers" copied from past invaders.
- New spacers are added at the **leader end**, so the array is a **chronological archive** of infections, newest first (Proteopedia summary; Heler/Sorek-group reviews in Molecular Cell 2016). [F]
- Self-targeting is avoided structurally, not by hoping no spacer matches self:
  - In type I and II systems, a short protospacer-adjacent motif (PAM) must be present next to a target. It is absent from the host's own array, so the array never matches itself.
  - In the type III system studied by Marraffini and Sontheimer (Nature, 2010), sequences *outside* the spacer pair perfectly with the host's own repeats, and that complementarity is what protects self.
  - The short PAM is described as a trade-off between efficient acquisition and avoiding autoimmune self-targeting.
- Even so, self-targeting spacers are occasionally acquired. One deep-sequencing study found 120 spacer types matching the host chromosome among 443,871 sampled spacers, about 0.04%. These appear lethal and are selected out (Nature Communications, 2013). [D]

**Principles:**
1. A threat memory should be **append-only and ordered**.
2. Self-protection should be **structural**: a threat record must carry a marker that a legitimate self-record can never carry.
3. Accept that rare self-targeting will occur, and make it **non-propagating**.

**In OT post-quantum trust:**
- **Revocation and threat lists** (revoked keys, bad image hashes, compromised witness keys) are append-only, ordered by epoch, and signed. A device that has seen epoch e can reject any list claiming to be older. [H]
- **A "PAM rule" for revocation.** A revocation record is *structurally* invalid if it would match the device's current authority set, unless it carries the escrow class plus physical-presence evidence. Current authority means the active slot hashes at or above the floor. An attacker who forges a revocation of the OEM's current key therefore cannot use it to brick the device, while revocation of *retired* keys and bad images works normally. [H]
- **Rare self-targeting** (a revocation that wrongly hits a live key) must not propagate. Peers never adopt another device's revocation state without verifying its signatures (Pattern 24, the prion warning).

**Where it breaks.** Bacteria tolerate killing a few cells; a substation cannot tolerate bricking a relay. The structural rule must be strict, and the exception path must be human-mediated.

**Status.** [H]; a small rule in the first-stage policy, testable in E-B2 and E-B4.

### Pattern 6 — Self-marks get stolen (restriction–modification)

**In nature:**
- In restriction–modification (R-M) systems, a methyltransferase marks the cell's own DNA at specific sites. A restriction enzyme cuts DNA in which those sites are *unmarked*, which is how foreign phage DNA is destroyed (reviews in Microbiology and Molecular Biology Reviews and Nucleic Acids Research).
- Some viruses respond by **acquiring or imitating the mark**, modifying their own DNA so it passes as self.
- Some bacteria counter that with **Type IV systems that attack modified DNA**, the mark itself.
- Roughly a quarter of bacteria carry R-M systems, and about half of those carry more than one type (Wikipedia summary of Wilson 1991; treat as approximate).
- R-M modules can behave like toxin–antitoxin "addiction" systems: if the cell loses the module, residual restriction activity kills it (**post-segregational killing**). [F]

**Principles:**
1. Identity by mark works until the adversary learns to apply the mark. Defence then needs a second, *different* recognition system that does not rely on the same mark.
2. Layered recognition systems coexist in one organism.
3. Some defences become **addictive**: once installed, removing them is fatal.

**In OT post-quantum trust:**
- The "mark" is the signing key. A quantum-capable forger (or a thief) applies the mark, and the defence is a second recognition system that does not depend on it: a second assumption class, a witness log, physical presence.
- The addiction lesson matters for procurement: **a hardware root of trust is an addiction module**. RDP Level 2, fused key hashes and permanent lifecycle states are irreversible dependencies. Choose them knowing that removal is impossible, and design the escape path (slot 3, board swap) *before* installing them. [I]

**Status.** Supports existing recommendations (multi-class slots, side-door closure); adds the procurement framing. [I]

### Pattern 7 — Signatures gain strength from decorrelation (brood-parasite egg signatures)

**In nature:**
- Hosts of brood-parasitic birds must recognise their own eggs among mimetic parasite eggs.
- Caves, Stevens, Iversen and Spottiswoode (Proc. R. Soc. B, 2015) measured nine aspects of egg colour, pattern and luminance across two African bird families, using information-theoretic entropy as an index of the identity information each egg can carry.
- **Parasitised species had consistently higher entropy than related unparasitised species.** The gain came **mainly from lower correlation between egg traits, not from more variation in any single trait**. Hosts improve their "signatures" by arranging traits into **unpredictable combinations**. [F]

**Principle.** Against a mimic, the strength of an identity signal comes less from the size of any one feature than from the **independence** of its features.

**In OT post-quantum trust.** This is the biological twin of the disjoint-quorum result in Part 9 (model M2):
- Adding more signatures that depend on the **same** assumption (two Keccak-dependent keys) barely helps.
- Adding a signature from an **independent** assumption class helps a great deal.
- At fleet level, the same law argues for **per-device key diversification**. Every device's identity should be independent of every other's, like each female's distinctive clutch, not a shared colony pattern (compare Pattern 9). [I]

**Status.** Conceptual support for the disjoint-quorum rule [I]; the rule itself is computed in Part 9.

### Pattern 8 — When location stops identifying you, use two independent voices (penguin two-voice system)

**In nature:**
- Emperor and king penguins breed without nests, so partners and chicks cannot use a place to find each other.
- They recognise each other by voice in very noisy colonies. Their syrinx produces **two simultaneous fundamental frequencies whose interaction creates an individual "beat" pattern** that survives propagation through crowded bodies.
- In playback experiments, birds answered normal two-voice calls but **not calls with one voice experimentally suppressed** (Aubin, Jouventin & Hildebrand, Proc. R. Soc. B, 2000).
- The two-voice structure is absent in the 14 nesting penguin species and is interpreted as having evolved with the loss of territoriality.
- King penguins detect a familiar call even 6 dB below the background (Aubin & Jouventin, 1998). [F]

**Principle.** While identity can lean on *place* (a nest, a perimeter), a single channel suffices. When place-based identity disappears, identity must become **multi-channel and noise-robust**.

**In OT post-quantum trust:**
- OT trust has leaned heavily on place: the air gap, the substation fence, "it's on the control network".
- That location-based trust is eroding through remote access, IT/OT convergence and cloud historians.
- The penguin's answer, independently mirrored by the multi-class slot design, is identity carried in **two independent "voices"** (two assumption classes) whose combination is checked as a whole.
- Single-voice acceptance (only one class verifying) is the equivalent of answering a one-voice call. It should be accepted for boot, but never for authority changes. [I]

**Status.** Conceptual support [I]; no new mechanism beyond Patterns 1 and 7.

### Pattern 9 — Shared colony odours are what parasites copy (ant nestmate recognition)

**In nature:**
- Ant colonies recognise nestmates by a shared blend of cuticular hydrocarbons, the colony odour.
- The caterpillars of the large blue butterfly *Phengaris (Maculinea) rebeli* get themselves carried into *Myrmica* nests and fed as brood.
- Akino and colleagues (Proc. R. Soc. B, 1999) gave the first direct evidence of the mechanism. The caterpillars **biosynthesise** many of the host's recognition compounds (chemical mimicry), then **acquire additional hydrocarbons inside the nest** (chemical camouflage), becoming near-perfect mimics.
- Nash and colleagues (Science, 2008) found that the closer the caterpillar's surface chemistry matched a host colony, the more easily that colony was exploited, varying in a geographic mosaic.
- Some populations synthesise an "aggregate odour" carrying specific compounds of several host species at once. [F]

**Principle.** A **shared group credential** is the easiest identity to counterfeit: copying one profile admits you to everything that trusts it. An insider then accumulates more of the credential.

**In OT post-quantum trust.** GOOSE/SV group keys, fleet-wide shared keys (N10) and shared maintenance passwords are colony odours. The ant's weakness predicts the attack pattern:
- an adversary who obtains the group key once is treated as kin by every member;
- once inside, it gathers more keys (lateral credential harvesting).

Defences:
- per-device identity underneath group membership;
- short group epochs (GDOI rekey);
- **detection of "camouflage"**: devices or accounts that accumulate credentials beyond their role. [H]

The prinia's egg strategy (Pattern 7) beats the ant's colony odour (Pattern 9) against mimics. That is a two-species argument, from nature, for key diversification.

**Status.** Supports existing recommendations; adds camouflage detection to fleet evidence [H].

## 5.2 Deciding together: authority without a single ruler

### Pattern 10 — Quorums, quenching and cheaters (bacterial quorum sensing)

**In nature:**
- Many bacteria release small signal molecules (autoinducers) and switch behaviour only when the local concentration crosses a threshold.
- A classic case is light production in *Vibrio fischeri*.
- Competitors and hosts can **quench** the signal by degrading it.
- "Cheater" cells can benefit from the public goods the quorum produces without paying to make them.

These are textbook features of quorum sensing; the term was coined by Fuqua, Winans and Greenberg in 1994. [F, textbook; not independently re-checked in this pass]

**Principle.** Threshold decisions need protection against three failures:
- **suppression**, where the signal is quenched so the threshold is never reached;
- **spoofing**, where fake signals push it over;
- **free-riding**, where members benefit from collective security without contributing.

**In OT post-quantum trust:**
- Witness and quorum designs must assume **quenching**: an attacker who blocks witness traffic can stall a legitimate emergency change. The mitigation is escalation paths (Pattern 19) and multiple witness channels.
- They must also assume **spoofing**: witnesses must be authenticated under a class other than the one being changed.
- The **cheater problem** is the migration commons. A facility that never migrates benefits from its neighbours' migration (fewer stepping stones) while remaining a stepping stone itself. That is a reason for **regulatory** rather than voluntary floors in interconnected sectors (Part 14). [I]

**Status.** [I]; informs threat models.

### Pattern 11 — Independent scouts, a quorum at the site, and a tuned threshold (honeybee house-hunting)

**In nature:**
- A honeybee swarm chooses a new home through a few hundred scouts, a few percent of the swarm, which inspect sites independently and advertise them by waggle dances.
- The decision is not a consensus. Scouts sense a **quorum at the site itself**. When roughly 10–15 or more bees are present at one candidate cavity, they begin "piping", which prepares the swarm to fly (Seeley & Visscher, Behav. Ecol. Sociobiol. 2003/2004; Cornell press reports).
- Modelling by Passino and Seeley (Behav. Ecol. Sociobiol., 2006) treats the quorum threshold as tuned for a **speed–accuracy trade-off**. In a press account of the model, lowering the quorum gave quick but error-prone choices, while raising it above 20–30 gave slower and only slightly better ones. [F]

**Principles:**
1. Evaluators must **inspect the thing itself independently**, not relay each other's opinions.
2. The quorum is measured **at the artefact**.
3. The threshold trades speed for accuracy, and the trade-off curve flattens. Beyond a moderate quorum, extra votes buy little accuracy at a real cost in speed.

**In OT post-quantum trust:**
- **Witnesses must each verify the artefact directly**, re-computing the image hash and checking the transition against policy themselves, and co-sign the artefact hash. A witness that co-signs because another witness did is not a scout.
- The flattening curve argues for **small quorums of genuinely independent parties** (2 of 3, or 3 of 5) over large committees. That is consistent with the multisignature recommendation and against heavy threshold-cryptography machinery. [I]

**Status.** Design guidance [I].

### Pattern 12 — Breaking deadlocks with targeted stop signals (honeybee cross-inhibition)

**In nature:**
- Seeley and colleagues (Science, 2012) showed that nest-site scouts deliver **stop signals**, a short buzz with a head-butt, to scouts dancing for *competing* sites.
- The inhibition grows with the size of each group, and a modelling analysis showed it **solves deadlock between equally good sites**.
- Without cross-inhibition, the swarm could stay split. [F]

**Principle.** When two legitimate-looking options compete, a collective needs explicit, targeted inhibition that **amplifies an early lead into a single decision**, or it splits and fails.

**In OT post-quantum trust.** This scenario was never analysed in the earlier passes: **two competing successor authorities**. Examples:
- After an island loses connectivity, an island authority and the fleet authority each issue a different next floor.
- After an OEM exit, an escrow claimant and the original OEM's successor company both present valid-looking vouchers.

Devices that accept "the first valid one" will split the fleet. The bee-inspired mechanism:
- **signed objections** (stop signals) from quorum members, attached to a competing proposal;
- a **deterministic tie-break**, for example the proposal with more distinct-class endorsements, then the lower hash;
- a rule that **no irreversible step executes while an unresolved objection exists**. This ties into Pattern 19. [H]

**Status.** New [H]. Kill test: TLA+ model of two concurrent successors with partitioned devices (add to E-B2).

### Pattern 13 — Succession needs a heartbeat, a window, and a prepared successor (honeybee queen loss)

**In nature:**
- A queen's presence is signalled continuously by queen mandibular pheromone (QMP).
- When workers stop detecting it, they begin **emergency queen rearing**. Usually within a few hours, they build queen cells around worker larvae **less than about four days old** (University of Georgia bee programme).
- The colony has only about **six days after the last egg was laid** to start, because older larvae can no longer become queens (Sagili et al., Scientific Reports, 2018).
- If the window passes, the colony becomes **"hopelessly queenless"**. Workers' ovaries, no longer suppressed, start producing **laying workers**, and the colony dies unless a beekeeper introduces a queen (UGA).
- Colonies also replace an *ageing* queen while she still lives (**supersedure**), and divide by **swarming**: the old queen leaves with part of the colony and a new queen is raised for the rest (Sagili et al. describe emergency, supersedure and swarming as the three routes). [F]

**Principle.** Succession is safe only if:
- the authority's **liveness is continuously signalled**;
- loss is **detected quickly**;
- successors are **already latent** in the population;
- succession happens **inside a bounded window**.

Planned succession during the incumbent's life is preferable to emergency succession. Splitting is a first-class operation.

**In OT post-quantum trust.** This is the clearest natural model of OEM exit found in this investigation:
- **Heartbeat.** The OEM signs an epoch "liveness statement" at a fixed cadence (say quarterly). It is published to the operator, the escrow agent and the witness network.
- **Detection and window.** Contracts define: if no statement arrives for N cadences, *or* no security fix ships within M days of a critical CVE, the escrow trigger fires.
- **Latent successors.** Slot 3 (operator or escrow key hash) is provisioned at manufacture. These are the "young larvae". A fleet manufactured without slot 3 is a colony with no young brood: it can only be "requeened" from outside, by replacement.
- **Laying workers.** Hopelessly orphaned fleets do not stay idle. They acquire grey-market maintainers, cracked firmware and unofficial key material. That is the failure mode to price (N7, N53).
- **Supersedure.** The preferred path is planned succession while the OEM still exists. At the end of CRA support, the OEM signs the hand-over to the operator's slot 3 itself (L12).
- **Swarming.** When a facility is sold or split, authority over part of the fleet *leaves* with the new owner. "Split ownership" therefore needs to be a defined voucher operation, not an improvisation (N52). [H]

**Where it breaks.** Pheromone is unforgeable in practice; a heartbeat signature is forgeable after a CRQC. The heartbeat must be signed in a PQ class, and the trigger should be **contractual and witnessed**, not a device-side timer, because devices lack trustworthy time.

**Status.** [H]; contract template plus witness service, both buildable now. E5 (OEM-exit drill) tests it.

### Pattern 14 — Stop dividing, keep working, tell the neighbours (senescence and apoptosis)

**In nature.** Damaged cells can follow two paths, and p53 sits at the decision point between them:
- **Senescence:** permanent arrest of division while the cell stays alive and secretes signals to neighbours (the senescence-associated secretory phenotype, SASP).
- **Apoptosis:** orderly self-destruction.

Senescent cells are useful in the short term (they stop damaged cells from proliferating). When they accumulate they contribute to inflammation and ageing, which is why the body clears them. [F, textbook; SASP after Coppé et al., 2008 — not re-checked in this pass]

**Principle.** A unit that can no longer be trusted to *change* the system can still be trusted to *function*, provided it stops proliferating authority and announces its state. Accumulated stale units must be cleared, or the whole ages.

**In OT post-quantum trust:**
- This is exactly the staleness rule: staleness restricts privileges, never the safety function.
- A device whose authority view is old (floor not refreshed for E epochs) enters **senescence**. It keeps running its control function, accepts no authority changes except through the quorum path, and **reports its senescence** in every state report (its SASP).
- **Apoptosis** is key zeroisation on confirmed tamper or decommissioning. It must never be automatic on mere staleness: that would turn a freeze attack into a destruction attack.
- **Clearance** is the dated replacement plan. Enclaves full of senescent devices age the facility. [H]

**Status.** [H]; mostly a naming and reporting rule over existing mechanisms.

## 5.3 Changing safely: renewal, transition and the dangers of reprogramming

### Pattern 15 — Grow the new shell underneath before shedding the old (arthropod molting)

**In nature.** Arthropods cannot grow inside a rigid exoskeleton, so they molt:
1. The epidermis separates from the old cuticle (apolysis).
2. A **new cuticle is secreted underneath while the old one is still in place**.
3. The animal then sheds the old shell (ecdysis).
4. The new cuticle hardens over hours to days. During that period the animal is soft, vulnerable and often hides.

[F, textbook entomology; the time-and-longevity stream verified the sources (source register)]

**Principle.** A protective structure that cannot change must be **replaced, not modified**. The replacement is **built and tested underneath** while the old one still protects. The changeover is the most dangerous moment, so it should be short, hidden and followed by a hardening period.

**In OT post-quantum trust — the molting protocol** [H]:
1. **Apolysis.** Provision the new authority (new slot hashes, new second-stage verifier) *alongside* the old, without retiring anything. The device now verifies both.
2. **New cuticle.** Run the new class in shadow: every release is signed in both classes. The device verifies both and reports any disagreement in its state report.
3. **Hide.** Before shedding, reduce exposure. Tighten the enclave boundary, suspend remote authority operations and require on-site tokens. This is the window in which HNDL-to-authority bites.
4. **Ecdysis.** Advance the floor to retire the old class. This needs the new class plus the old class (or escrow) under the disjoint-quorum rule.
5. **Hardening.** For E epochs after shedding, the device accepts no further authority changes except recovery. The witness network watches for anomalies.

This was the implicit shape of "make-before-break" in earlier passes. Molting adds two steps they lacked: an **explicit hide phase** and an **explicit hardening phase**.

**Status.** [H]; specifiable as a state machine and checkable in E-B2.

### Pattern 16 — Duplicate first, then diverge (gene duplication)

**In nature.** Ohno (*Evolution by Gene Duplication*, 1970) argued that duplication is a major source of evolutionary novelty. One copy keeps the original function while the redundant copy is free to change. [F, classic]

**Principle.** Never mutate the only copy of something essential. Duplicate it, keep one copy stable, and let the other evolve.

**In OT post-quantum trust.** A/B image slots and multi-class key slots are gene duplication. The design rule that follows is that **every essential verifier, key slot and image must exist in at least two copies at the moment it is changed**. That rules out single-slot designs on devices meant to survive algorithm change. [I]

**Status.** Existing practice; elevated to a mandatory rule for C2+ devices.

### Pattern 17 — Keep the germline small and sequestered (Weismann barrier)

**In nature.** The germline that carries heritable information is set aside early in development and protected. The disposable body (soma) changes and dies. [F, classic]

**Principle.** What must last generations should be minimal, isolated early and changed almost never. Everything else can be disposable.

**In OT post-quantum trust.** The locked first stage is the germline: a ~13 KB hash verifier with slot commitments, set aside at manufacture. The second stage and application are soma. The more the germline grows (parsers, protocol stacks, ML-DSA), the more permanent bugs it carries (N20). **The first stage should contain nothing that could be deferred to the second stage.** [I]

**Status.** Design rule.

### Pattern 18 — Count what you cannot undo, and guard the reset (telomeres)

**In nature:**
- Normal human cells divide only about **40–60 times** in culture before senescence (the Hayflick limit), because telomeres shorten at each division.
- Cancers escape by reactivating telomerase, the enzyme that **resets** the counter. Kim and colleagues (Science, 1994) found telomerase activity in **98 of 100 immortal cell populations and 90 of 101 tumour biopsies**, but in **none of 50 normal somatic tissues**. Reviews commonly summarise this as about 85% of human cancers. [F/D]

**Principle.** A monotonic budget is a safety mechanism, and the ability to reset it is the most dangerous capability in the system.

**In OT post-quantum trust:**
- Every monotonic budget in this atlas is a telomere:
  - LMS tree capacity (2ʰ signatures; h = 10 gives 1,024);
  - SP 800-230's limit of 2²⁴ signatures per key;
  - fuse bits for anti-rollback;
  - floor indices;
  - certificate serial spaces.
- **Size every budget for the asset's lifetime**, with margin. A nightly-signed LMS H10 tree lasts only 2.8 years [C].
- **Treat any reset or rollback capability as the cancer path**: RMA resets, factory resets, restoring a signer from backup. Each must require the strongest authority class plus physical presence, and must leave an indelible record. [H]

**Status.** Design rule plus audit item in the side-door map.

### Pattern 19 — One unattached kinetochore halts the irreversible step (spindle assembly checkpoint)

**In nature:**
- Before a dividing cell separates its chromosomes (anaphase, an irreversible step), the spindle assembly checkpoint waits until **every** chromosome is properly attached.
- Rieder and colleagues (J. Cell Biol., 1994; 1995) showed that **even a single unattached kinetochore delays anaphase**, through an inhibitory signal that kinetochore produces.
- When the last unattached kinetochore was destroyed with a laser, the cell entered anaphase about 20 minutes later. Normally anaphase follows the last attachment by about 23 minutes. [F/D]

**Principle.** For an irreversible transition, a single unready participant must be able to **hold** the transition. The wait signal comes from the unready part itself, and the transition proceeds promptly once every part reports ready.

**In OT post-quantum trust:**
- Before an irreversible fleet step (classical sunset, retirement of a family, a mass floor advance), the coordinator should wait until every *dependent* participant has reported "attached":
  - every device in scope has staged the new artefacts;
  - every witness has co-signed;
  - every island has acknowledged.
- A single "unattached" report holds the step.
- This prevents a common failure: retiring the old authority while some devices have not yet learned the new one, which strands them. [H]

**Where it breaks.** A malicious participant could hold the step forever. Cells have a related escape (prolonged arrest can end in "mitotic slippage"). The engineering version is **escalation, not infinite wait**: after a bounded hold, the step goes to human review with the list of holders. Holders that are compromised get quarantined in the enclave rather than allowed to block the fleet.

**Status.** [H]; straightforward to add to the walk orchestrator (L10).

### Pattern 20 — Reprogramming is where tumours come from (Waddington's landscape and iPS cells)

**In nature:**
- Development is pictured as balls rolling down Waddington's epigenetic landscape into differentiated valleys; going back uphill is hard.
- Takahashi and Yamanaka (Cell, 2006) showed that four transcription factors can reprogram adult cells to pluripotency.
- When Okita, Ichisaka and Yamanaka (Nature, 2007) generated germline-competent mice from such cells, **about 20% of offspring developed tumours attributable to reactivation of the c-Myc transgene**. They concluded that retroviral c-Myc should be avoided for clinical use, and later protocols removed it. [F/D]

**Principle.** Reverse transitions to a more capable, less constrained state are inherently dangerous. They must be designed to work **without the components that cause uncontrolled growth**.

**In OT post-quantum trust:**
- Device lifecycle states (TEST → PROD → RMA → DECOMMISSIONED) are Waddington's valleys.
- Every path back uphill (RMA unlock, factory reset, re-provisioning) is a reprogramming event, and the equivalent of c-Myc is **general debug reopening**.
- Design reprogramming without it:
  - RMA by **board swap**;
  - re-provisioning that installs only new slot hashes through the floor rule;
  - no reopened debug access;
  - every reverse transition recorded in the ordered memory (Pattern 5). [I]

**Status.** Strengthens side-door closure (Part 11.2).

### Pattern 21 — A conserved core, weak links and compartments (evolvability, bow ties and hourglasses)

**In nature and in networks:**
- Kirschner and Gerhart (PNAS, 1998) described properties that make organisms *evolvable*: conserved core processes, **weak regulatory linkage** between modules, exploratory behaviour and compartmentation.
- Csete and Doyle (Trends in Biotechnology, 2004) described **bow-tie architectures** in metabolism: many inputs and outputs funnelled through a small, highly conserved core. Carlson and Doyle (PNAS, 2002) called such optimised systems "robust yet fragile": robust to expected perturbations and catastrophically fragile at the core.
- Akhshabi and Dovrolis (SIGCOMM, 2011) showed with an abstract evolutionary model, EvoArch, that layered protocol stacks **tend to evolve into an hourglass** whatever their starting shape. The waist protocols become **ossified**, and the waist "kernels" are often not the best protocols, but ones that appeared early with the right connections. [F]

**Principle.** Long-lived evolving systems converge on a narrow, conserved waist. The waist is what everything depends on and what can no longer change. Choose it deliberately, keep the links around it weak, and do not let the waist be a single point of failure.

**In OT post-quantum trust:**
- The analysis in Part 9 (model M2) found that **every standard post-quantum signature depends on either SHA-2 or SHA-3/SHAKE**. That makes hashing the **waist of the post-quantum hourglass**, and it will ossify.
- This is the "robust yet fragile" core, and it yields two rules:
  1. Keep **two waists**: one SHA-2 path and one SHA-3 path. That is the maximum independence the standard toolkit offers.
  2. Keep the linkage weak: algorithm identifiers, self-describing manifests (SUIT, CBOM), and negotiated profiles let the layers above and below the waist change without breaking the waist.
- The EvoArch warning applies to our own proposals. Whichever first-stage format, voucher profile or manifest layout becomes popular *early* will ossify, whether or not it is the best. That argues for **publishing a carefully reviewed open reference early**, before an inferior proprietary one becomes the waist. [I]

**Status.** Strategic guidance [I]; the two-waist rule is quantified in Part 9.

## 5.4 Keeping time in the dark

### Pattern 22 — A free-running clock, entrained by many cues (circadian rhythms)

**In nature:**
- **The rhythm is self-sustained.** Cyanobacteria's KaiA, KaiB and KaiC proteins, mixed with ATP in a test tube, produce a self-sustained rhythm of KaiC phosphorylation with a period close to 24 hours (Nakajima et al., Science, 2005).
- **It is temperature-compensated.** A modelling paper reporting the data shows the period changing by only about 10% between 25 and 35 °C, a Q₁₀ near 1.1. Terauchi et al. (PNAS, 2007) found KaiC's ATPase activity to be inherently temperature-invariant.
- **Human clocks free-run.** In people, the intrinsic period under tightly controlled lighting averaged **24.18 hours** (Czeisler et al., Science, 1999).
- **Phase-dependent correction entrains them.** The clock is kept on local time by *zeitgebers*, chiefly light. The response depends on phase: light before the core-body-temperature minimum delays the clock, light after it advances it, and light at the minimum has no effect (Khalsa et al., J. Physiol., 2003). [F]

**Principle.** A good internal clock does three things:
- it runs on its own with a **known, bounded error**;
- it is **compensated against the main disturbance** (temperature);
- it is **corrected gently and repeatedly** by external cues, whose influence depends on how plausible the correction is at that moment.

It never jumps to whatever the latest cue says.

**In OT post-quantum trust.** This is the zeitgeber stack of Part 6 (I-23):
- The RTC free-runs with a known drift bound. A ±20 ppm crystal drifts about ±10.5 minutes a year.
- Temperature compensation (a TCXO) tightens the bound tenfold.
- Every independent time source is a zeitgeber that **nudges within a plausibility window** sized by the drift bound since the last trusted correction, rather than setting the clock outright.

A spoofed time source then has bounded power: it can move the device's clock only as far as the window allows. [I]

**Status.** [H]; specified in Part 6.

### Pattern 23 — Agreement without a conductor (firefly synchronisation)

**In nature and engineering:**
- **Mirollo and Strogatz** (SIAM J. Appl. Math., 1990) proved that identical pulse-coupled oscillators, each nudging the others when it "fires", end up firing in unison from almost all starting conditions. Fireflies were the motivating example.
- **Werner-Allen and colleagues** (ACM SenSys, 2005) built a firefly-inspired algorithm that coped with radio delay and loss, and synchronised a multi-hop sensor testbed to within about 100 µs.
- **Wang and Wang** (IEEE Trans. Signal Processing, 2020) designed pulse-coupled synchronisation that reaches agreement **despite multiple Byzantine nodes** sending arbitrary pulses. They noted that earlier fault-tolerant schemes, including Lamport and Melliar-Smith's, needed nodes to start nearly synchronised. [F]

**Principle.** A population can agree on time without a master, if each member corrects itself a little toward its neighbours. With the right rules, a bounded number of liars cannot break the agreement.

**In OT post-quantum trust:**
- In islands cut off from authenticated time, peers can agree on a shared epoch by pulse-coupled or median-based exchange of *signed* time claims.
- This supports staleness decisions (whether the island has been isolated too long) without trusting any single node.
- It does not prove absolute time. It proves **consensus time among authenticated peers**, which is what island-level policy needs. [H]

**Status.** [H]; prior art exists for the synchronisation, though not for its use in authority staleness.

### Pattern 24 — Maintenance happens in sleep (glymphatic clearance and the two-process model)

**In nature:**
- **Clearance happens in sleep.** Xie and colleagues (Science, 2013) found that in sleeping or anaesthetised mice the brain's interstitial space expanded by more than 60%, and β-amyloid was cleared about twice as fast as in waking. Sleep is when the brain does its cleaning.
- **Two processes time it.** Borbély's two-process model (Human Neurobiology, 1982) explains when sleep occurs as the interaction of:
  - a homeostatic **pressure** that builds with time awake;
  - a **circadian gate** that opens and closes on a daily rhythm. [F]

**Principle.** Systems that run continuously need scheduled offline periods for maintenance. When maintenance happens is best set by **accumulated need meeting an allowed window**, not by either alone.

**In OT post-quantum trust.** Maintenance windows are the plant's sleep. The two-process model gives a scheduling rule for cryptographic transitions (Part 11.5): activate when **accumulated pressure** meets **an open gate**.
- **Pressure:** unapplied changes, exposure-years, staleness.
- **Gate:** the plant's maintenance calendar.

Plants that never "sleep" accumulate change debt (Pattern 29). [I]

**Status.** Scheduling heuristic [I].

### Pattern 25 — Dormancy that ends only on the right combination of cues (seeds)

**In nature:**
- **Seeds can outlast centuries.** In W. J. Beal's buried-seed experiment, begun in 1879 at Michigan State with 20 bottles of seeds, the 14th bottle was dug up in 2021 and seeds of *Verbascum* still germinated. Four bottles remain.
- **Some outlast millennia.** A date-palm seed from Masada germinated in 2005. Its own shell fragments radiocarbon-dated to about 1,700 years old, and control seeds from the same site to about 2,000 (Sallon et al., Science, 2008). Fertile *Silene stenophylla* plants were regenerated from fruit tissue about 31,800 years old preserved in Siberian permafrost, and they set viable seed (Yashina et al., PNAS, 2012).
- **Dormancy can be stabilised.** Tardigrades survive drying by expressing intrinsically disordered proteins that help vitrify their cells (Boothby et al., Molecular Cell, 2017).
- Many seeds end dormancy only after a *combination* of cues, such as cold followed by moisture, or light (textbook seed biology). [F]

**Principle.** Long dormancy is survivable if the dormant state is **minimal and stable**, and if waking requires **several independent cues together**, so that one false cue does not trigger it.

**In OT post-quantum trust:**
- **Spares and long-idle devices should be seeds.** They hold only the immutable first stage and slot hashes, and take on application images, ownership and keys only when **several cues coincide** at installation (I-5):
  - a valid voucher for this site;
  - the current signed bundle;
  - an on-site technician token.
- A spare stolen from a warehouse, or a device "found" on the grey market, then carries no live authority (N36, N53). [H]

**Status.** [H]; I-5 sharpened.

## 5.5 Surviving damage and change

### Pattern 26 — Seal what you cannot heal (compartmentalisation of decay in trees)

**In nature:**
- Trees do not repair wounded wood. Shigo and Marx's model of **Compartmentalization Of Decay In Trees** (CODIT; USDA Forest Service Agriculture Information Bulletin 405, 1977) describes trees **walling off** damage with four barriers:
  1. plugging of vertical vessels (the weakest);
  2. the last-formed cells of each growth ring;
  3. the rays;
  4. a **barrier zone** formed by the cambium after wounding (the strongest).
- The bulletin itself warns the system works "most of the time—not all of the time".
- The popular slogan "trees don't heal, they seal" paraphrases this idea; it is not a quotation from the bulletin. [F]

**Principle.** When damage cannot be repaired, contain it with layered barriers, the strongest formed *after* the wound, and keep growing new, healthy tissue outside the walls.

**In OT post-quantum trust.** This is the natural model of enclave containment (Part 11.6):
- Devices that cannot be migrated are the decay. The enclave boundary is the barrier zone. Weaker walls inside the enclave (segmentation, monitoring, physics invariants) still help.
- **Two consequences follow:**
  1. **Containment is not cure.** The decay stays inside the wall, so new growth (replacement) must happen outside it.
  2. **The strongest wall is the one built deliberately after the problem is understood.** Retrofitting a designed boundary beats relying on whatever segmentation happened to exist. [I]

**Status.** Supports the enclave design and its dated exit.

### Pattern 27 — Lose a sector, keep the tree (sectored architecture in very old trees)

**In nature:**
- Great Basin bristlecone pines include individuals of about 4,800 years by ring count. "Methuselah" has been counted at 4,857 years.
- In very old trees, often only a narrow strip of living tissue connects roots to a few living branches. When a major root dies, the sector of trunk and crown it supplied dies, while the rest of the tree lives (PBS NOVA; strip-bark growth in *Pinus longaeva*, Leland et al., JGR Biogeosciences, 2018).
- Sectored hydraulic architecture, in which shoot segments are tied to specific roots, is described for other long-lived conifers. A peer-reviewed sectoriality study specific to bristlecone was not found in this pass. [F, partly verified]

**Principle.** Longevity can come from **independent sectors**: a failure in one supply line kills only what that line feeds.

**In OT post-quantum trust:**
- **Sectored enclaves:** several small boundaries rather than one large one (Part 11.6).
- **Sectored authority:** per-site KDC scopes, per-substation key diversification and per-cohort rollout rings.

A single compromise then kills one sector, not the fleet. [I]

**Status.** Design rule.

### Pattern 28 — Fall back to a slower rhythm, but keep beating (cardiac escape rhythms)

**In nature.** The heart has a hierarchy of pacemakers, each with an intrinsic rate. OpenStax *Anatomy and Physiology* gives:
- the sinoatrial node at about 80–100 per minute intrinsically, slowed by nervous input;
- the atrioventricular node at 40–60;
- the atrioventricular bundle at 30–40;
- the Purkinje fibres at 15–20.

If the sinoatrial node fails, the atrioventricular node takes over at its slower rate. Clinical texts quote slightly different conventional ranges; the hierarchy, not the exact numbers, is the point. [F]

**Principle.** A life-critical function needs a **hierarchy of fallbacks**, each simpler and slower than the last, each able to sustain life on its own.

**In OT post-quantum trust.** The boot and control hierarchy should mirror the heart:
1. the current A/B second stage;
2. the alternate slot;
3. the last-known-good image;
4. a minimal safe mode that keeps the safety function running with no network authority at all.

**A security failure should push the device one step down this hierarchy, never stop it.** That is how fail-operational behaviour is engineered rather than hoped for. [I]

**Status.** Design rule; testable in E1's power-cut and fault campaign.

### Pattern 29 — Suppressing small fires builds megafires (the wildfire paradox)

**In nature and land management:**
- Calkin, Thompson and Finney (Forest Ecosystems, 2015; Finney is at the US Forest Service) describe the "wildfire paradox" as fully realised in most western US forests. Decades of aggressive suppression have reduced fire but let fuels accumulate, and the fires that escape are larger and more damaging. Remedies include prescribed burning, managed wildfire and fuel treatment.
- Kreider and colleagues (Nature Communications, 2024) simulated about 5 million fires. Under maximum suppression, mean burn severity rose by an amount equivalent to about 102 years of climate-driven drying. In the same comparison, the largest 1% of fires burned 91% of the total area under maximum suppression, against 4% with no suppression. [F]

**Principle.** Preventing every small disturbance concentrates risk into rare, catastrophic ones. Regular, controlled, small disturbances keep the system resilient.

**In OT post-quantum trust.** This is the clearest natural model of the patch-avoidance loop (R8).
- Every deferred update adds "fuel": accumulated vulnerabilities, untested change paths, lost skills. When change is finally forced, it is large, urgent and dangerous.
- The remedy is **prescribed burns**: small, frequent, planned changes and drills (window staging, slot drills, renewal rehearsals) that keep the change path open and the people practised.
- The 60% of PLCs running firmware with fixes over ten years old (Part 2; R8) is a forest that has not burned for a decade. [I]

**Status.** Strong analogy with quantitative natural evidence; supports R8 interventions.

### Pattern 30 — Monocultures fail all at once; response diversity does not (crops, salmon, software, reactors)

**In nature and agriculture:**
- **Southern corn leaf blight, 1970.** Texas male-sterile (cms-T) cytoplasm was estimated to be in about 85% of US hybrid corn. A pathogen race specific to it destroyed about 15% of the US crop, worth about US$1 billion at the time, with some local losses near total. cms-T was abandoned in 1971 (Bruns, Agronomy Journal, 2017). [F]
- **Bananas.** The export trade ran on one cultivar, Gros Michel, until Fusarium wilt Race 1 destroyed it. The trade switched to resistant Cavendish. Cavendish now dominates exports, and Tropical Race 4, first identified in Taiwan in 1990, has spread across several continents (Ploetz, 2011; Kema et al., Frontiers in Plant Science, 2021). [F]
- **The Irish famine** killed around a million people and drove about a million to emigrate. The popular story that Ireland depended on the "Lumper" potato alone is an oversimplification: other varieties then in use also succumbed (Ó Gráda, History Ireland, 1993; pathogen lineage in Yoshida et al., eLife, 2013). [F]
- **The positive counterexample.** Bristol Bay sockeye salmon return in several hundred distinct populations. Year-to-year variability in returns is **2.2 times lower** than it would be for one homogeneous stock, and fishery closures would be about **ten times more frequent** without that diversity (Schindler et al., Nature, 2010). Ecologists call the protective property **response diversity**: the variety of responses to the same environmental change among species or populations that perform the same function (Elmqvist et al., Front. Ecol. Environ., 2003). [F]

**In engineering:**
- **Diversity is less independent than it looks.** Knight and Leveson (IEEE TSE, 1986) had 27 programmers independently write versions of the same specification. Each version passed 200 acceptance tests and was then run on 1,000,000 test inputs. Independently written versions **failed together far more often than independence predicts**. In one case eight versions failed on the same input, and the independence hypothesis was rejected at 99% confidence. [F]
- **Regulators already require diversity against common-cause failure.** The US NRC's Branch Technical Position 7-19 (Rev. 9, May 2024, retitled to address common-cause failure due to latent design defects) names **identical copies of software in redundant divisions** as a vulnerability. Where a postulated common-cause failure cannot be prevented, mitigated or shown not to be risk-significant, it requires a **diverse means** of performing the function. [F]
- **The computer-security version.** Forrest, Somayaji and Ackley (HotOS, 1997) argued for "avoiding unnecessary consistency" between computers. Geer and colleagues' CCIA report *CyberInsecurity: The Cost of Monopoly* (2003) used the single-crop farm analogy against software monoculture. [F]

**Principle:**
- Uniformity converts a local failure into a systemic one.
- Diversity protects only if the diverse parts **respond differently to the same shock**, which is response diversity, not mere variety.
- Even deliberately independent designs share hidden correlations, so independence must be **argued from mechanism, not assumed**.

**In OT post-quantum trust:**
- **Assumption-class diversity is the response diversity of cryptography.** Lattice and hash-based schemes respond differently to the same mathematical shock.
- **Knight and Leveson's warning is why the disjoint-quorum rule (M2) reasons about shared assumptions rather than counting algorithms.** ML-DSA and SLH-DSA-SHAKE look like different families but share Keccak, much as two independently written programs shared the same difficult input cases.
- **The NRC's D3 doctrine is the closest regulated precedent for multi-class key slots.** It gives OT operators a vocabulary their safety assessors already accept: a defence-in-depth and diversity analysis for the trust anchor. [I]

**Status.** Strong precedent; directly usable in safety-case arguments (Part 15, safety engineer).

### Pattern 31 — Hedge bets when you cannot know the future (seed germination, bacterial persisters)

**In nature:**
- Cohen (J. Theor. Biol., 1966) modelled annual plants whose seeds either germinate or stay dormant in a randomly varying climate, and derived the optimal germination fraction. In the general form of the result, the long-run optimum maximises **expected logarithmic (geometric-mean) fitness**, the same mathematics as Kelly's betting rule (Bell System Technical Journal, 1956). When the "wrong" choice is fatal, the optimal fraction committed to an outcome equals that outcome's probability (Donaldson-Matasci, Bergstrom & Lachmann, 2010). [F]
- Balaban and colleagues (Science, 2004) showed at single-cell resolution that some *E. coli* cells are already slow-growing or dormant **before** antibiotic exposure. These **persisters** survive the drug and regrow, and the authors present this as bet-hedging. [F]

**Principle.** When you must act before knowing which future arrives, commit only a fraction to each option, so that no single outcome destroys everything. The quantity to maximise is the geometric mean, because one zero wipes out the product.

**In OT post-quantum trust:**
- **Emergency rollouts keep persisters.** When a fix must ship before it is proven, a defined fraction of each class stays on last-known-good until field evidence arrives (I-33).
- **For devices that can carry only one verifier (class C1),** split the sub-fleet across two independent key-delivery mechanisms, so that no single compromise loses it all.
- **Where devices *can* carry several classes, do better than bet-hedging.** Model M7 shows per-device diversity removes partial-loss events that fleet splitting cannot. [C/I]

**Status.** Existing practice in canary rollouts, formalised here; I-33 is new.

### Pattern 32 — Protect the hubs; find them through their neighbours (network immunisation)

**In nature and network science:**
- On scale-free contact networks, **random immunisation has no effective threshold**, while immunising the most connected nodes sharply cuts spread (Pastor-Satorras & Vespignani, Phys. Rev. E, 2002).
- **Acquaintance immunisation** immunises random *neighbours* of randomly chosen nodes. It finds hubs without any global knowledge and dramatically lowers the coverage needed (Cohen, Havlin & ben-Avraham, PRL, 2003). [F]

**In OT post-quantum trust.** Model M1 applied this to a Purdue-like trust graph:
- Class-ordered migration (authorities and concentrators first) needed about 10% coverage to cut the worst-case blast radius below 5%.
- Acquaintance migration needed about 44%.
- Random migration needed about 73%.

**Two consequences:**
1. **Order the programme by class.**
2. **Where the inventory is unknown, migrate what devices trust, not the devices themselves** (I-20).

**Status.** Supported by model M1 [C]; needs a real-topology test (E-N4).

### Pattern 33 — Spread news like an epidemic, but never like a prion (gossip, anti-entropy, misfolded state)

**In nature and distributed systems:**
- Demers and colleagues (PODC, 1987) adapted epidemic models to keep replicated databases consistent in the Xerox Clearinghouse:
  - **anti-entropy** (random pairwise reconciliation) is reliable but costly;
  - **rumour mongering** is cheap but leaves some sites un-updated, so anti-entropy backs it up;
  - deletions spread as **"death certificates"**.
  [F]
- In biology, misfolded prion proteins propagate by **templating their misfolded shape onto healthy copies** (textbook biology). A corrupted state that copies itself without verification spreads through a whole population.
- Tero and colleagues (Science, 2010) showed that the slime mould *Physarum* grows transport networks with efficiency, fault tolerance and cost comparable to the Tokyo rail network. Their model derives such networks from simple local reinforcement rules. [F]

**Principle.** Local exchange of state can keep a disconnected population consistent without a centre. A peer's state must be **verified before it is adopted**, or one corrupted node misfolds the rest.

**In OT post-quantum trust:**
- In islands and long-disconnected sites, devices can **gossip** their highest *signed* floor, epoch and revocation list (T4). "Death certificates" are the revocation records with the PAM rule of Pattern 5.
- **The prion warning.** A device must never raise its own floor, or adopt a revocation, because a peer did. It adopts only what carries valid signatures under the disjoint-quorum rule. Gossip moves *evidence*, not *conclusions*.
- Physarum-style reinforcement offers a principled way to **place KDC and witness replicas** so that islands stay served when links fail. This is a minor, optional design aid. [H]

**Status.** [H]; the gossip-of-evidence rule is a cheap addition to the islands design (G14, K20).

### Pattern 34 — Integrate the error, or it never reaches zero (integral feedback in bacterial chemotaxis)

**In nature.** Bacteria adapt perfectly to a constant background of attractant, returning to the same tumbling rate whatever its level. Yi, Huang, Simon and Doyle (PNAS, 2000) showed that **integral feedback control** is built into the chemotaxis network and is **necessary** for a robust implementation of such perfect adaptation. [F]

**Principle.** A controller that reacts only to the current error tolerates a permanent residual. A controller that **accumulates** the error over time keeps pushing until the residual is zero.

**In OT post-quantum trust:**
- Migration programmes measured by "percentage migrated" behave like proportional controllers. They relax once most devices are done, leaving a stubborn residual that carries most of the risk.
- **Exposure-years** (unmigrated devices × criticality × time, model M5) is the integral of the error. A programme steered by it keeps pressure on the residual until it is gone (I-21). [I]

**Status.** Metric proposal; trivial to compute from fleet evidence.

## 5.6 Signals and honesty

### Pattern 35 — A forgeable signal collapses when fakes become common (frequency-dependent mimicry)

**In nature.** In Batesian mimicry, a harmless species copies the warning signal of a dangerous one. Classic theory and experiments in evolutionary ecology hold that this works only while mimics are **rare relative to their models**. When fakes become common, predators learn that the signal no longer predicts danger and ignore it, so model and mimic both lose protection. Conversely, signals that are **costly or impossible to fake** stay informative ("honest signalling"). [F, textbook ecology; not re-checked in this pass]

**Principle.** A signal keeps its meaning only while forging it is rare. The moment forgery becomes cheap and common, receivers abandon the *whole* signal class, honest senders included.

**In OT post-quantum trust.** This is the right frame for the day a CRQC exists:
- ECDSA and RSA signatures do not merely become "weaker". As forgeries become available, *every* classical signature becomes uninformative, so receivers must stop believing the entire class at once.
- Devices that cannot stop believing it (classical-only immutable verifiers) are the predators who cannot learn.
- The transition must therefore be **complete before mimics become common**. That is the deeper reason the classical sunset (floor rule) must be executed *before* a CRQC is suspected, not when one is confirmed.
- PQ signatures restore an **honest**, costly-to-fake signal. [I]

**Status.** Conceptual [I]; reinforces the timing arguments of Parts 2 and 17.

### Pattern 36 — Watch what physics forbids (the process as a witness)

**In nature and in plants.** Organisms detect injury from signals that only real damage can produce (Pattern 3). Industrial processes have their own unforgeable regularities: conservation of mass and energy, tank levels that must follow flows, voltages that must obey network laws.

Research on Singapore's SWaT water-treatment testbed derived **physical invariants** from plant design and used them, distributed across controllers, to detect attacks that compromised several sensors and actuators at one stage (Adepu & Mathur, AsiaCCS 2016, on a testbed with 42 sensors and actuators). Follow-up work found that **neither design-derived nor data-derived invariants suffice alone** (Umer et al., IJCIP 2020), and that data-derived invariants can themselves be attacked adversarially (IEEE TDSC 2023). [F]

**Principle.** The laws of physics are a "key" no attacker can forge. A command or report that violates them is false whatever its signature says.

**In OT post-quantum trust.** Physical invariants give a **cryptography-independent second signal** (Pattern 1) for operational commands and reported states. They are especially valuable inside enclaves, where devices cannot be migrated: a forged command that would make a tank overflow is caught by physics even when its classical signature is forged perfectly. They do **not** protect firmware or authority changes, which have no immediate physical signature. That is why they complement, and do not replace, the continuity first stage. [I]

**Status.** Existing research with mixed results; recommended as an enclave-layer control [I].

## 5.7 The synthesis: twelve laws of long-lived trust, as nature writes them

Reading the patterns together, the same few laws recur across immune systems, bee colonies, trees, cells and seeds. Each law below names the patterns that support it and the engineering rule it becomes in this atlas.

| # | Law | Nature's evidence | Engineering rule in this atlas |
|---|---|---|---|
| 1 | **Recognise self by structure, not by luck** | CRISPR PAM and repeat complementarity; R-M self-marking | Revocation records that structurally cannot target current authority (the "PAM rule") |
| 2 | **Act irreversibly only on two independent signals** | Two-signal lymphocyte activation; penguin two-voice | Boot with one class; change authority with two disjoint classes; anergy on single-signal probing |
| 3 | **Buy accuracy with time and stages; reset on doubt** | Kinetic proofreading (Hopfield; McKeithan) | Staged, channel-independent hold-downs that reset on contradiction (M3) |
| 4 | **Independence beats magnitude** | Egg signatures gain entropy by decorrelating traits; response diversity | Disjoint-quorum rule; two hash waists; per-device diversification (M2) |
| 5 | **Prepare successors before you need them** | Young larvae for emergency queens; supersedure; molting's new cuticle | Slot 3 at manufacture; supersedure before CRA end; molting protocol |
| 6 | **Signal liveness; detect absence fast; act within a window** | Queen pheromone; emergency rearing window | OEM heartbeat with contractual, witnessed escrow trigger |
| 7 | **Seal what you cannot heal** | CODIT; bristlecone sectors | Enclaves with walls, exit clocks and dated replacement |
| 8 | **Degrade in steps, never all at once** | Cardiac escape rhythms; senescence | A/B → last-known-good → safe minimal mode; staleness restricts privileges only |
| 9 | **Count what you cannot undo, and guard the reset** | Telomeres; telomerase in cancer | Size every monotonic budget for life; resets need the strongest authority plus presence |
| 10 | **Let small, frequent changes prevent large, rare catastrophes** | Fire ecology; sleep; bet hedging | Window staging, slot drills, staged rollout with persisters |
| 11 | **Restrain the defenders** | Tolerance; regulatory T cells; ~10% autoimmune prevalence | Thymic policy testing; rate-limited destructive actions; safe misfire |
| 12 | **Keep the core small, conserved, and doubled** | Weismann barrier; bow ties; hourglasses | ~13 KB first stage; two hash waists; weak linkage through self-describing manifests |

**Why the convergence matters [I].** The striking thing about these twelve laws is not any single mechanism but their recurrence. T cells, honeybee swarms, bacteria, trees and cell division have no common design. They are separated by hundreds of millions of years of evolution and built from different materials, yet they keep arriving at the same few solutions: two independent signals before irreversible action, staged commitment that resets on doubt, prepared successors, sealed compartments, counted budgets, small frequent renewals. In biology, convergent evolution is the closest thing nature has to a replication study. When unrelated lineages find the same answer, the answer usually reflects a constraint of the problem rather than an accident of history. That is the best reason to take these patterns seriously in engineering. Any system that must stay trustworthy while it changes, among adversaries, for longer than its makers can watch over it, faces the same constraints. Much of the beauty in these mechanisms comes from that economy: very little machinery, placed exactly where the problem forces it.

## 5.8 Where nature is the wrong teacher

Biomimicry fails when it copies the surface of a mechanism without its context. Four warnings, each from evidence.

1. **Naive copies of immune mechanisms underperformed.** The best-known computer-security transfer from immunology is "negative selection" anomaly detection, inspired by Forrest and colleagues (IEEE S&P, 1994). Stibor, Timmis and Eckert tested it extensively and concluded that, as applied, it was **not appropriate for real-world network intrusion or anomaly detection**, and was **not competitive with statistical anomaly-detection methods** (IEEE CEC 2005; ICARIS 2005; Stibor's 2006 dissertation, TU Darmstadt). [F] The lesson is not that immunology is useless. The patterns in this chapter are borrowed for their **architecture** (staging, two signals, structural self-protection), not for their pattern-matching machinery.
2. **Nature optimises populations; safety engineering protects individuals.** Bet hedging, apoptosis and the culling of self-targeting cells all accept the death of individuals so that the lineage survives. A protection relay may not be sacrificed to save the fleet. Every borrowed pattern here has been re-checked for **individual-level** safety. Where nature accepts loss (bricking a fraction of devices), the engineering rule is **fail operational**.
3. **Nature's adversaries are slow; ours are fast and intelligent.** Arms races between hosts and parasites run over generations. A human adversary with a CRQC adapts in days and can study the defence in advance. Patterns that rely on *gradual* adaptation, such as evolving recognition over time, are discounted. Patterns that are **structural and immediate** (two signals, disjoint quorums, staged commitment) are preferred.
4. **Popular nature stories can be wrong.** The claim that forest trees share resources and "talk" through common mycorrhizal networks spread widely in popular media. Karst, Jones and Hoeksema (Nature Ecology & Evolution, 2023) reviewed the evidence and found key claims (that such networks are widespread and that they transfer resources to increase seedling performance) **insufficiently supported**. They also found that unsupported claims in the literature had doubled in 25 years through positive citation bias. [F] Every natural mechanism in this chapter was therefore checked against primary research before use, and those that could not be checked are labelled.

There is one more, subtler disanalogy. **Biology rarely needs to prove anything to a third party; infrastructure does.** An immune response need not be auditable, but a floor advance on a substation relay must be explainable to an operator, an assessor and a regulator. That is why this atlas pairs every nature-derived mechanism with a **signed, human-readable record** of what changed and why (Part 18, I-12).

---

# 6. Time without a clock: what a disconnected device can know

Earlier passes made one rule, "time may tighten privileges but never stop a safety function", and one limit, the freeze limit. This chapter replaces that rule of thumb with physics, measured data and a concrete design. [F unless marked]

## 6.1 Three different things called "time"

Devices need three different properties, and no single source provides all of them:
1. **Absolute time.** What the date is (UTC). Needed for certificate validity and for correlating logs.
2. **Elapsed time.** How long since an event. Needed for hold-downs, rate limits and staleness.
3. **Order and freshness.** Whether this message is newer than that one, or was created after a given moment. Needed to reject replays and rollbacks.

Most designs blur these together and then fail when the absolute clock is wrong. Counters give order without time. Free-running oscillators give elapsed time with a bounded error. External cues give absolute time, but only as trustworthy as their source.

## 6.2 What a free-running clock can know: measured drift

Commodity real-time clocks run from 32.768 kHz tuning-fork crystals. A representative datasheet (Raltron R38) specifies:
- frequency tolerance ±20 ppm;
- a turnover temperature of 25 ± 5 °C;
- a parabolic temperature coefficient of −0.034 ± 0.006 ppm/°C²;
- ageing of up to ±3 ppm in the first year;
- operation from −40 to +85 °C.

An Analog Devices application note (AN58) puts 20 ppm at roughly one minute a month. [F]

| Error source | ppm | Drift per year [C] |
|---|---|---|
| Tolerance | ±20 | ±631 s (10.5 min); about ±1.75 h per decade |
| Sustained 0 or 50 °C (temperature effect alone) | −21 | about −11 min |
| Sustained +85 °C (temperature effect alone) | −122 | about −64 min |
| Sustained −40 °C (temperature effect alone) | −144 | about −76 min; about −86 min with worst-case tolerance added (Part 9, M4) |
| First-year ageing | up to ±3 | up to about ±95 s |
| Temperature-compensated oscillator (TCXO), typical | ±2 | ±63 s |

**Consequence.** A cheap clock in a hostile cabinet can drift by more than an hour a year, and by more than half a day over a decade (about 14 hours in the worst case of Part 9, M4). A TCXO stays within about a minute a year. **Validity rules should use coarse epochs (months), sized to the device's drift bound.** Any decision that needs hours or minutes needs an external cue.

## 6.3 Nature's design: free-run, compensate, entrain

The circadian system (Pattern 22) shows the architecture:
- an oscillator that runs on its own with a known error;
- **temperature compensation**, which the cyanobacterial Kai clock achieves biochemically;
- **phase-dependent entrainment** by several cues, where each cue's influence depends on when it arrives.

It never resets to whatever the latest cue says. Translated, each device's time is:

> **estimate = last trusted correction + elapsed oscillator time, inside a window of ± (drift bound × time since correction)**

Every new cue is accepted only if it falls inside the window, or if enough *independent* cues agree to move the window.

## 6.4 The zeitgeber stack: every available time cue, and what it can prove

| Zeitgeber | What it can prove | Trust assumption | Known failure | Where it fits in OT |
|---|---|---|---|---|
| **Free-running RTC** | Elapsed time, with the drift bound of §6.2 | The crystal and its supply | Battery loss resets it; temperature extremes | Every device with a battery-backed RTC |
| **Monotonic counters** (boot count, floor index, message counters) | **Order only** | Non-restorable storage | Counter wrap or budget exhaustion (§6.6); restore from backup (R6) | Every device. Automotive SecOC already builds freshness from counters, because vehicle ECUs rarely share a synchronised clock (AUTOSAR SecOC specification). The JASPAR profile combines a trip counter, a reset counter and a message counter (§7.7) |
| **Power-off remanence timer** | A bound on how long the device was unpowered | The physics of SRAM decay | Strong temperature dependence and chip-to-chip variation. TARDIS (USENIX Security 2012) reported usable ranges from seconds to several hours | Rate-limiting attacks that rely on repeated power cycling; flagging implausibly long "instant" reboots (I-26) |
| **Authenticated network time** (Roughtime RFC 10049, Experimental; authenticated PTP) | Absolute time, when connected | The time servers and their signature algorithm | Unavailable offline; classical signatures need migration | Connected sites |
| **Grid frequency as a clock** (counting mains cycles: 4.32 million a day at 50 Hz) | Long-run absolute time to within the grid operator's managed time deviation; precise *relative* timing among devices on the same grid | The grid operator's **governance**, not physics | Disputes and policy: in 2018 Continental Europe's average frequency sagged to about 49.996 Hz from mid-January during a Kosovo/Serbia balancing dispute (about 113 GWh missing), and mains clocks ran about **6 minutes slow** until restored in April (ENTSO-E). Cross-check [C]: −4 mHz is −80 ppm, and 80 ppm over about 50 days is about 5.8 minutes. Continental Europe's operating rules (UCTE Policy 1) leave deviations within ±20 s uncorrected, aim to stay within ±30 s normally and ±60 s exceptionally, and correct by shifting the frequency setpoint ±10 mHz for whole days. North America retired its time error correction reliability standard in 2017 (FERC approved the BAL-004-0 retirement on 18 Jan 2017), and the matching NAESB business practice was removed the same year. Islanding breaks the shared signal | Substation devices, meters, RTUs. For **relative** synchronisation and plausibility, not as a UTC authority |
| **Grid-frequency fluctuation fingerprints** (ENF) | **"Created after" evidence**: the fine fluctuations are hard to predict in advance but common across a synchronous area | The physics of the grid plus a local measurement | Too little entropy over short windows, local noise, islanding | Forensics already dates recordings this way (Grigoras, 2005). Research uses grid-voltage cycle-length fluctuations as a time fingerprint: average synchronisation error of 0.1 ms over about 10 km, robust to packet-delay attacks (Viswanathan, Tan & Yau, IEEE RTSS 2016; ACM TOSN 2018). Nodes on the same floor agreed to about 10 µs. The Syntonistor (Rowe, Gupta & Rajkumar, SenSys 2009) tuned a 58 µW receiver to the mains magnetic field and reached typically sub-millisecond network-wide synchronisation, and kept working while nodes were disconnected. ENF has also been proposed as the basis of a ledger consensus mechanism ("Proof-of-ENF", EconLedger, 2021). **No use for authority-freshness decisions was found** (I-25) |
| **GNSS** | Absolute time | Satellite signals, which are unauthenticated in civil use | Spoofing and jamming; counter wrap. The 10-bit GPS week number rolled over at 23:59:42 UTC on 6 April 2019 and knocked out New York City's municipal wireless network, cutting communication with traffic signals at 12,389 intersections (Inside GNSS, 2019) | A plausibility cue only, never the sole authority |
| **Technician freshness token** | Absolute time, signed, at the moment of a visit | The visiting organisation's signing key | Only as frequent as visits | Long-offline sites; spares activation |
| **Peer consensus** (pulse-coupled or median-based, Byzantine-tolerant) | Consensus time among authenticated peers | A bound on the number of lying peers | Collusion beyond the bound | Islands (Pattern 23) |
| **Celestial and pulsar timing** | Independent physical time | Physics | Impractical for field devices. NASA's SEXTANT experiment used four millisecond pulsars, observed from the ISS in November 2017, to fix position within a few miles after about eight hours of observation, and pulsar time-scales agree with atomic time within uncertainties | [S] An existence proof of time from physics, not a design element |

## 6.5 Fusing the stack

The fusion rule this edition proposes (I-23) [H]:
1. **Keep an interval, not a point.** Device time is a window [earliest, latest] that widens at the drift bound since the last trusted correction.
2. **Each cue proposes, nothing sets.** A cue inside the window narrows it. A cue outside the window is recorded and ignored unless at least two *independent* classes of cue agree on the new position: for example, grid-cycle count plus technician token, or authenticated network time plus peer consensus.
3. **Never derive authority from time alone.** Time can reduce privileges (staleness puts the device in its senescent state, Pattern 14), but it can never *grant* authority, advance a floor or unlock a lifecycle state.
4. **Report the window, not just the estimate,** in every signed state report, so operators can see how uncertain each device's time is.
5. **Treat grid time as governed.** Its long-run accuracy is a service of the grid operator, and 2018 showed it can be off by minutes for weeks. Use it for relative timing and plausibility, weighted accordingly.

## 6.6 Counters that run out

Time representations and monotonic budgets are themselves counters, and counters wrap or run out inside long asset lives (N56):
- **Year 2038.** A signed 32-bit Unix time ends at 03:14:07 UTC on 19 January 2038 and wraps to 1901. Linux 5.6 (2020) and glibc 2.34 (2021) added 64-bit time on 32-bit platforms, but devices shipping today with 32-bit time will cross the boundary in service. Embedded systems that live as long as the machines they control are the most exposed [I].
- **GPS week rollovers** recur every 1,024 weeks (about 19.7 years). The next falls on 20 November 2038, ten months after the Year 2038 boundary, so devices that survive one may still fail the other.
- **Cryptographic budgets:**
  - LMS trees allow 2ʰ signatures (1,024 at h = 10; about 2.8 years of nightly signing).
  - SP 800-230's limited-use SLH-DSA sets allow 2²⁴ signatures per key.
  - Fuse banks allow as many anti-rollback increments as they have bits.
- **"No expiry" is a defined value, not an omission.** RFC 5280 says certificates for devices with no well-defined expiration *should* use the special notAfter value 99991231235959Z, and that the issuer must then make sure no valid chain remains once it stops maintaining revocation status.

**Rule [I].** For every counter and time field in a design, write down its capacity, its consumption rate and the asset's maximum life. Require margin of at least two times. Make any reset path the most protected operation on the device (Pattern 18).

## 6.7 What time can and cannot do for trust

- **It can bound staleness.** A device knows, within its drift window, how long since its last trusted contact. That is enough to enter a senescent, reduced-privilege state.
- **It can help reject replays.** With grid-fingerprint evidence (if I-25 proves out) or signed technician tokens, a device can tell that an authority message was created after some recent moment.
- **It cannot detect withholding.** The freeze limit (Part 3.4) stands. No local physics tells a device that newer updates exist and are being withheld from it.
- **It must never be the root of authority.** Every time source in the stack is either governed by an institution (grid, GNSS, NTP operators) or bounded by physics in a way an attacker can influence (temperature, power).

---

# 7. What lasted, and how migrations really go

Nature shows how living systems last. Human history shows how **institutions, artefacts and technologies** last, and how long their transitions really take. This chapter records the precedents checked in this pass and what each changes in the design. [F unless marked]

## 7.1 Continuity through scheduled renewal: Ise Jingu

**The precedent:**
- Japan's Ise Jingu has been **rebuilt every 20 years** since the first ceremony in 690, under Empress Jitō. Each time a new sanctuary of the same dimensions goes up beside the old one, and the sacred apparel and treasures are remade.
- The 62nd renewal was in 2013. The rituals of the 63rd began in 2025, with the transfer ceremonies scheduled for October 2033.
- Each cycle runs about eight years and some thirty rituals.
- Mie Prefecture's tourism authority describes the 20-year cycle as a way to pass craft knowledge to the next generation. That rationale is widely repeated but is **not** stated on the shrine's own page.

Sources: Ise Jingu; Mie Prefecture tourism; Ise-Shima tourism.

**What it teaches.** Continuity can be achieved by **renewing on a schedule rather than by building to last**. The schedule is chosen so that every generation of craftspeople performs the renewal more than once. The knowledge survives because it is *used*.

**In OT post-quantum trust.** The scarcest resource identified in the second pass was people who know how a device's trust actually works. Cryptographic transitions that happen once every 20–30 years guarantee that **nobody in the organisation will have done the last one**. Two adaptations follow:
- **Slot drills** (I-13) keep the *mechanism* exercised.
- **Full renewal rehearsals** at an interval short enough that each engineer takes part at least twice (I-30) keep the *people* exercised.

The Ise lesson also says the renewal is the product, not an interruption to it: the eight-year cycle *is* the operating model. [I]

## 7.2 Institutions that govern shared resources for centuries

**The precedents:**
- **The Valencia Water Tribunal** has met **every Thursday at noon at the door of Valencia Cathedral** to settle irrigation disputes. It traces to the al-Andalus period; the often-quoted founding date of 960 is traditional, not documented. UNESCO inscribed it in 2009 with the Council of Wise Men of the plain of Murcia. [F]
- **Elinor Ostrom's eight design principles** for long-enduring common-pool resource institutions (*Governing the Commons*, 1990) were found "well supported" in a review of 91 studies (Cox, Arnold & Villamayor Tomás, Ecology and Society, 2010):
  1. clearly defined boundaries;
  2. rules fitted to local conditions;
  3. collective-choice arrangements;
  4. monitoring by monitors accountable to the users;
  5. graduated sanctions;
  6. cheap, quick conflict resolution;
  7. minimal recognition of the right to organise;
  8. nested enterprises for larger systems. [F]

**What they teach.** Shared infrastructure outlives its founders when its users govern it, monitor it, settle disputes quickly and sanction proportionately, and when small units nest inside larger ones.

**In OT post-quantum trust.** Several recommended components are commons: shared resources that no single company owns and everyone depends on.
- The **open first-stage reference** and its maintainer foundation.
- The **witness network** that co-signs releases and authority changes.
- The **voucher escrow and ceremony** arrangements for slot 3.
- The **benchmark and conformance lab** (I-10).

Ostrom's principles give their governance a tested template:

| Ostrom principle | Applied to the trust commons |
|---|---|
| Defined boundaries | Members are named OEMs, operators and labs, with a defined scope of devices |
| Local rules | Sector profiles (power, water, rail) rather than one global rule set |
| Collective choice | Users vote on algorithm-profile changes |
| Accountable monitoring | Witnesses are themselves monitored, and their logs are public |
| Graduated sanctions | From a warning, to suspension of a witness key, to expulsion |
| Fast conflict resolution | The Valencia model: a standing body that meets on a fixed cadence |
| Right to organise | Recognition by regulators (CEA, CRA bodies, NERC) |
| Nested enterprises | Site → utility → sector → national lab |

This answers the second pass's objection to custodians (no demand, unclear liability) differently: **not a company, but a governed commons**, which Ostrom found to be the form that lasts. [I]

## 7.3 The internet's root trust anchor: custody and rollover

The DNS root key-signing key (KSK) is the single trust anchor for DNSSEC validation worldwide. Its history is the best real-world case found in this investigation of **rotating a trust anchor across a fleet the operator does not control and cannot inspect**. [F]

**A long-lived, multi-party custody institution:**
- Since July 2010 the root KSK has lived in hardware security modules at two facilities (Culpeper, Virginia and El Segundo, California).
- It is operated in **quarterly key ceremonies** that alternate between the sites.
- Activating the HSM requires **at least 3 of 7 Crypto Officers** for that site, each holding a key to a safe-deposit box with an operator smart card.
- The Crypto Officers are **Trusted Community Representatives**: volunteers from the technical community who are not affiliated with ICANN, Verisign or the US Department of Commerce, and are not contractually bound.
- A separate group of **Recovery Key Share Holders** holds M-of-N smart-card shares (5 of 7 in the launch design) of the key that encrypts the backup KSK, in case both facilities are lost.
- Ceremonies are scripted, video-recorded, published and attended by independent auditors.

Sources: IANA KSK Operator Key Management Procedure, 2024; ICANN 2010 launch materials; ICANN TCR consultation, 2014.

**The first rollover was postponed because the fleet said it was not ready:**
- The first KSK rollover was scheduled for 11 October 2017.
- On 27 September 2017 ICANN postponed it. Data from **RFC 8145 trust-anchor signalling**, a then-new mechanism by which validating resolvers tell root servers which anchors they hold, showed that a significant share of reporting resolvers still trusted only the old key. Reported shares range from more than 5% (SIDN) to about 7–8% (ICANN presentation) and 6–8% (Huston's analysis).
- Verisign noted that the RFC 5011 automated-update mechanism the rollover relied on **had never been tested in production for a root KSK rollover**.
- After outreach, public comment and a revised plan with a back-out scenario, ICANN rolled the key on **11 October 2018**, one year late.
- SIDN Labs saw no major resolver issues. RFC 8145 data still showed about 4% of sources not trusting the new key weeks later, and a 2019 study (Müller et al., IMC '19) analysed the challenges seen at every stage.

**What this precedent establishes for OT [I]:**
1. **Neutral, multi-party custody of a global root works and has lasted over fifteen years.** Volunteers, quorum credentials, recovery shares, audits and recorded ceremonies are all in operation. The second pass demoted the "neutral custodian" for OT for lack of demand evidence, but its *institutional form* is proven. A sector body or national lab could run ceremonies for OT escrow roots (slot 3) on this model.
2. **Anchor telemetry changes decisions.** Without RFC 8145, the 2017 rollover would have gone ahead and broken a meaningful fraction of validators. That is the strongest available evidence for the earlier hypothesis H23 (anchor telemetry) and for the spindle-checkpoint gating of irreversible fleet steps (I-27).
3. **Untested automation is the risk.** The mechanism every validator depended on had never been exercised at scale. That is the case for slot drills (I-13): exercise the alternate path before you need it.
4. **Stragglers remain after the step.** Even a year of outreach left a few per cent of reporters behind. OT plans must assume a residual population that needs enclaves or visits after any irreversible step.

## 7.4 Designing for deep time

**The precedents:**
- **The Clock of the Long Now.** Danny Hillis's design principles for a clock meant to keep time for 10,000 years (longnow.org) are:
  - **longevity** (correct time for ten millennia);
  - **maintainability** (repairable with Bronze-Age technology);
  - **transparency** (its workings understandable by inspection);
  - **evolvability** (improvable over time);
  - **scalability** (the same design works from tabletop to monument).
- **Warning the far future about nuclear waste.** In 1980 the US Department of Energy's Human Interference Task Force commissioned the semiotician Thomas Sebeok to study messages that must survive ten millennia (report BMI/ONWI-532, 1984).
  - Sebeok recommended **relay systems that re-encode the message every few generations**, mixed sign types and heavy redundancy. He proposed an "atomic priesthood" to carry the truth forward.
  - US regulation (40 CFR 191.14) gives **no credit to active institutional controls beyond 100 years** after disposal, and requires "the most permanent markers, records, and other passive institutional controls practicable".
  - The WIPP marker concept (Sandia, 1993) uses massive granite monuments and a message room in seven languages. [F]
- **The Rosetta Stone** (196 BC) carries the same decree in hieroglyphic, Demotic and Greek. Because the Greek was readable, the other scripts could be deciphered; Champollion announced his breakthrough on 27 September 1822 (British Museum). [F]
- **The BBC Domesday Project** (1986) recorded a portrait of Britain from about a million contributors on LaserVision discs read by BBC Micro hardware. By 2002 it was described as practically inaccessible: the discs survived, but the players were obsolete. It was rescued by emulation (CAMiLEON, 2002). The 1086 Domesday Book is still readable at Kew (The Observer, 2002; Ariadne 36, 2003). [F]

**What they teach:**
1. **Do not rely on institutions lasting longer than about a century.** Regulators already discount them.
2. **Carry critical messages in several independent encodings**, so that one can decode the others.
3. **Re-encode periodically** rather than trusting one encoding forever.
4. **The failure mode of digital records is the reader, not the medium.** Durable meaning needs a durable way to interpret it.

**In OT post-quantum trust:**
- **Rosetta = multi-class signatures.** A transition record signed in two independent classes remains verifiable when one class becomes unreadable (broken). The Rosetta Stone is a hybrid signature 2,200 years old.
- **Re-encoding = evidence renewal** (§7.5). Records must be re-protected under new algorithms before the old ones fail, exactly as Sebeok's relay re-encodes the warning.
- **The reader problem = verifier availability.** A 2027 ownership voucher is useless in 2060 if no software can parse its format or verify its algorithm. Keep **reference verifiers and format specifications in the escrow archive**, not only the records. The Domesday lesson is cheap to apply and expensive to forget.
- **Institutional half-life.** Escrow designs that rely on a single custodian organisation existing in 50 years are making the assumption that 40 CFR 191 refuses to make. Prefer passive, distributed, multiply-encoded evidence plus governed commons (§7.2). [I]

## 7.5 Keeping evidence verifiable for decades

**The precedents:**
- **Evidence Record Syntax (RFC 4998, 2007; XML version RFC 6283, 2011)** keeps signed or timestamped data provable for the long term, through two renewal operations:
  - **Timestamp renewal** extends the chain when the timestamping authority's key is at risk, its algorithms weaken or its certificate nears expiry. It does not need access to the archived data.
  - **Hash-tree renewal** re-hashes all archived data and evidence under a new algorithm when the tree's hash algorithm weakens, and starts a new chain. [F]
- **Widely witnessed publication.** Since 1995, the timestamping company Surety has printed a weekly hash of its customers' seals in a small *New York Times* classified ad (VICE, 2018). This is the Haber–Stornetta linking idea (*How to time-stamp a digital document*, J. Cryptology, 1991) anchored in a medium almost anyone can check decades later. [F]
- **Trust from a tiny seed.** In 2023 GNU Guix announced a "full-source bootstrap" that roots its package graph in a **357-byte** program (the hex0 seed for x86). Everything else is built up from source through a verifiable chain of ever more capable tools: stage0-posix, GNU Mes, TinyCC and early GCC. This answers Ken Thompson's *Reflections on Trusting Trust* (1984) with structure rather than faith. The coverage is not total: the Linux kernel and some language toolchains are outside it. [F]
- **Transparency logs and witnesses.** Sigsum's design lets end users verify log proofs **offline, without new outbound connections**. Witnesses cosign only fresh (no more than five minutes old), append-only tree heads, so the logs can later be shut down safely. Sigsum currently supports only **Ed25519 and SHA-256**. The C2SP cosignature specification says **ML-DSA-44 SHOULD be used for new deployments** because it is quantum-resistant. [F]

**What they teach.** Long-term verifiability is a **process** (periodic renewal before weakness), not a property of one signature. The smallest trustworthy root is a seed from which everything else is **rebuilt verifiably**, not a large thing that must stay perfect.

**In OT post-quantum trust:**
1. **Archive vouchers, decommissioning receipts, transition logs and state reports as evidence records**, and renew them on a schedule tied to the algorithm-policy calendar (I-29). A voucher must still be provable in the 2050s, when an orphaned fleet needs it.
2. **Use widely witnessed publication for fleet root commitments.** Publishing the hash of each fleet's slot set in a medium the operator, regulator and courts can all check later (a regulator's gazette, a sector registry, several public logs) costs almost nothing and outlives any vendor.
3. **The first stage is the hex0 seed of the device.** The Guix result is the strongest external support for keeping the immutable part *tiny* and letting everything else be rebuilt and verified above it.
4. **Witness networks need their own migration.** The leading designs are Ed25519-based today. An OT transparency layer built on them inherits a classical dependency, so it should start with ML-DSA cosignatures (or dual-class cosignatures) from day one (new problem N68).

## 7.6 How long migrations really take

The previous edition assumed fleet transitions take "one or two window cycles". The historical record says the real time constants are much longer, and that the tail matters more than the median. [F]

| Migration | Start | Milestone | Time constant | What drove it |
|---|---|---|---|---|
| **SHA-1 retirement** | First practical collision attack announced 15 Feb 2005 (about 2⁶⁹ work) | CA/B Forum Ballot 118 (Oct 2014): no new SHA-1 certificates from 1 Jan 2016. Chrome 56 removed support (Jan 2017). SHAttered collision (23 Feb 2017). NIST retirement 31 Dec 2030 | **11 years** to stop issuing in the WebPKI; **about 25 years** to full retirement | Browser vendors' unilateral policy; a public collision |
| **IPv6** | RFC 2460, Dec 1998 | Google measured above **50%** of users for the first time on 28 Mar 2026 (Internet Society Pulse); multi-source average about 43% | **About 27 years** to a bare majority | No forcing function; dual-stack coexistence for decades |
| **Hybrid post-quantum TLS** | Chrome 124 enabled X25519Kyber768 by default on desktop (2024) after months on 10% of stable users | Breakage in middleboxes and servers that could not handle a ClientHello split across packets (tldr.fail lists Vercel, Zscaler, Broadcom ProxySG, Palo Alto, Apache Traffic Server, all since patched). Chrome 131 then **replaced** Kyber with ML-KEM, changing the codepoint, with no dual support | **Two migrations in under a year** for the earliest adopters | A browser vendor's control of both ends; an enterprise opt-out policy |
| **Let's Encrypt root expiry** | DST Root CA X3 expired 30 Sep 2021 | Older clients without ISRG Root X1, or using OpenSSL 1.0.x, failed; problems were reported across firewall and appliance vendors | **An overnight cliff** for long-lived devices | A certificate notAfter date |
| **US 3G shutdowns** | AT&T from Feb 2022; T-Mobile mid-2022; Verizon by 31 Dec 2022 (FCC) | The alarm industry said about **6 million alarm systems** relied partly on AT&T or Verizon 3G. Vehicles lost crash notification and SOS features | **Hard sunset** of infrastructure under long-lived devices | The network operator's business decision |
| **UK analogue landline switch-off** | Most customers to switch by end of Jan 2027 (gov.uk) | About 1.8 million households use telecare. Two people died in 2023 when telecare failed after switchover, and non-voluntary migrations were paused (Which?, 2025) | **Years, with deadly edge cases** | Infrastructure modernisation |
| **EMV chip cards (US)** | Liability shift 1 Oct 2015 (fuel pumps later) | Visa reported counterfeit fraud down 76% at chip-enabled merchants (Dec 2015 to Dec 2017) as their number rose from 392,000 to about 2.9 million. In countries that migrated earlier, card-not-present fraud **surged** as fraudsters switched targets (Kansas City Fed studies, 2013 and 2017). In the US, a 2025 Kansas City Fed briefing found **no sudden surge**: card-not-present fraud on debit cards rose gradually over 2011–2021, partly because magnetic-stripe fraud stayed feasible | **About 2–3 years** for the bulk | **Liability shift**: whoever had not migrated paid for fraud |
| **Y2K** | 1990s | US Commerce estimated about **$100 billion** of US spending (1995–2001). Press reports gave Gartner estimates of $300–600 billion worldwide | A hard, known deadline | The calendar |
| **CrowdStrike Falcon content update** | 19 Jul 2024 | Microsoft estimated **8.5 million** Windows devices crashed (under 1% of all Windows machines). A content file supplied 21 input fields where the sensor expected 20, causing an out-of-bounds read. Remedies included staged deployment rings and customer control of rollout | **Hours**, for a security update to cause a global outage | Automated, simultaneous deployment of a security change |

**The lessons [I]:**
1. **Without a forcing function, long-lived infrastructure migrates on a 25-year time constant** (SHA-1, IPv6). Post-quantum migration in OT has no natural forcing function except regulation (IR 8547, CRA, CEA, India's roadmap) and liability.
2. **Liability shifts work, and attackers go to whatever weak channel remains.** Where the old channel closed, EMV pushed fraud to card-not-present. Where magnetic-stripe fallback stayed open, as in the US, many fraudsters simply kept using the old channel. In OT the same two outcomes await: migrating the boot chain alone either moves attackers to the side doors or leaves them on the classical paths that remain (R9). Plan side-door closure **in the same programme**, or the migration buys displacement rather than security.
3. **Hard sunsets are the most common way long-lived devices actually die.** Certificate expiry, network shutdown, analogue switch-off. The classical-algorithm sunset of 2030/2035 will behave like the 3G shutdown, not like a gentle deprecation, for every device that cannot change. Inventory, budget and replacement planning should treat it that way.
4. **Even early adopters migrate twice.** Chrome went from Kyber to ML-KEM within months, and witness specifications already prefer ML-DSA over Ed25519. Any OT design that hard-codes today's post-quantum parameter set, or a draft codepoint (N25), will need its own migration. Self-describing formats and slots are cheaper than replacements.
5. **Security updates can be the outage.** CrowdStrike's own remedy was staged rings and customer-controlled rollout, which is window staging and persister cohorts under another name.

## 7.7 Sector precedents worth copying

Other sectors with long-lived, safety-relevant devices have already solved parts of the problem. None has solved all of it, but together they cover most of the pieces this atlas needs. [F unless marked]

| Sector | Precedent | What it already solves | What OT post-quantum trust should copy |
|---|---|---|---|
| **Automotive** | AUTOSAR SecOC, with a Freshness Manager. The JASPAR profile builds freshness from a trip counter and a reset counter (each up to 24 bits) and a message counter (up to 48 bits) | Replay protection on buses where ECUs rarely share a synchronised clock | **Freshness from counters, not clocks** (Part 6). Counter widths chosen up front for the vehicle's life |
| **Automotive** | UN Regulations 155 (cybersecurity management) and 156 (software update management), in force since January 2021. In the EU, R155 became mandatory for new vehicle types from July 2022 and for all new registrations from July 2024; R156 is phased in on similar schedules by vehicle category | Makes an audited **update-management system a condition of selling the product** | The strongest forcing function found outside Y2K (§7.6, lesson 1). The EU CRA does something similar for products with digital elements; OT procurement can do it contractually now |
| **Railway signalling** | EN 50159:2010 (safety-related communication; replaced by a 2026 edition, which this atlas did not review). It names seven threats: repetition, deletion, insertion, resequencing, corruption, delay and masquerade. Its defences include sequence numbers, timestamps, time-outs, source and destination identifiers, feedback messages, identification procedures, safety codes and cryptographic techniques | It **separates the safety code**, which catches random corruption, **from cryptographic protection** against deliberate attack | The direct answer to R5. If the safety layer does not depend on the cipher, the cipher can migrate without reopening the safety case. This is the single most important structural precedent for P28 and N48 [I] |
| **Aviation** | ARINC 665 (loadable software parts); ARINC 835-1 (2014) on digital signatures for loadable software; a revision, ARINC 835-2, published 2 December 2025; DO-326A/ED-202A airworthiness security process (RTCA now also lists a DO-326B) | Signed, versioned software parts with a defined loading process, inside certification | Part-number discipline for firmware and **signature formats defined separately from the aircraft**. Whether 835-2 addresses post-quantum signatures was not checked |
| **Medical devices** | IMDRF N70 (2023) on legacy medical devices. It defines a legacy device as one that cannot reasonably be protected against current cybersecurity threats, and sets four life-cycle stages: development, support, limited support and end of support. At end of support, responsibility passes to the healthcare provider. Manufacturers should communicate end-of-life and end-of-support dates as early as possible; the guidance uses two years' notice as a reference point, and summaries describe two to three years | **A vocabulary and a handover for devices that can no longer be secured** | Exactly the senescence pattern (Pattern 14) and the dated exit (11.6). OT has no equivalent of an announced end-of-support date for cryptography; it should |
| **Medical devices (US)** | FD&C Act section 524B, effective 29 March 2023. Premarket submissions for "cyber devices" must include a plan to monitor and address postmarket vulnerabilities, update processes and an SBOM. FDA began refusing incomplete submissions from 1 October 2023 | Update capability and a bill of materials as **a condition of market entry** | CBOM as an entry condition (11.7) |
| **Telecom** | GSMA PQ.03 v2.0 (4 October 2024), post-quantum guidelines for operators. It flags remote SIM provisioning (eSIM) as needing action and recommends tunnelling legacy traffic where endpoints cannot migrate | A sector-wide inventory of where long-lived embedded credentials sit | Treat provisioning infrastructure, not just traffic, as the priority; tunnel what cannot change (the enclave pattern, 11.6) |
| **Nuclear I&C** | NRC BTP 7-19, Rev. 9 (May 2024): diverse means against common-cause failure (Pattern 30) | Regulators requiring **diversity** where identical copies could fail together | The disjoint-quorum rule (M2) as a regulatory expectation |
| **National security systems** | CNSA 2.0: LMS/XMSS for software and firmware signing; ML-KEM-1024 and ML-DSA-87; new NSS acquisitions compliant from 1 January 2027; phase-out of non-compliant equipment by 31 December 2030; all NSS by 2035 | A dated, procurement-driven schedule | Procurement dates are the clock that actually moves vendors |
| **Space** | NASA-STD-1006 (Space System Protection Standard, approved 29 Oct 2019; revised as 1006A in July 2022): command uplinks must be encrypted, with exceptions such as spacecraft designed to operate beyond 2 million km, for which command authentication is still recommended at minimum (NASA FAQ, 2020) | Command authority for assets that are never physically reachable again | **Authentication is the floor even when confidentiality is impractical.** The same split suits deep OT field devices |
| **Space** | Voyager 1: on 14 Nov 2023 its flight data system began returning unreadable data. Engineers traced the fault to one failed memory chip and on 18 Apr 2024 sent commands that moved the affected code elsewhere in memory, confirmed on 20 Apr. The spacecraft was more than 24 billion km away; each command took about 22.5 hours to arrive | A remote repair of a 46-year-old computer | **Spare capacity, relocatable code and people who still understand the system.** The last of these is the scarcest (R10, N61) |
| **Space** | Curiosity rover: switched to its redundant B-side computer on 28 Feb 2013 after a memory problem on the A side | Redundant compute sides that can be swapped remotely | The A/B slot and the multi-slot first stage are the same idea at smaller scale |

**What the precedents teach together [I]:**
1. **Each piece exists somewhere; no sector has all of them.** Automotive has freshness without clocks and update management as a sales condition. Railway has the safety/crypto separation. Medicine has a legal vocabulary for end of support. Space has authentication-first command links and decades-long remote repair. OT post-quantum trust can be assembled largely from proven parts.
2. **The safety/crypto separation is the most valuable single import.** It turns post-quantum migration from a safety recertification into a security change (R5).
3. **Market-entry conditions beat guidance.** UN R156 and FDA 524B changed behaviour because products could not be sold without them. Voluntary guidance has a 25-year time constant (§7.6).
4. **Long remote life needs headroom and people.** Voyager was saved by spare memory and by engineers who could still read 1970s documentation. Slots, budgets and counters need margin (Part 6), and ceremonies need practised people (Pattern 29's prescribed burns; slot drills, I-13; the renewal cadence of §7.1).

---

# 8. Hardware: what the lock protects, and what outlives the chip

Earlier editions treated the locked first stage as if the lock were absolute. This chapter makes the threat model explicit, separates the two adversaries the lock faces, and gathers the hardware precedents that matter for trust lasting decades. It stays at the level of architecture and procurement. Attack techniques are deliberately out of scope.

## 8.1 Two adversaries, two different answers

| | **Remote, fleet-scale forger** | **Local attacker with a device in hand** |
|---|---|---|
| **Who** | Anyone who can forge classical signatures once a CRQC exists, and push them to many devices | Someone with physical access to one device: a stolen spare, a field unit, a returned board |
| **Goal** | Install their own code or authority across a fleet | Read secrets or change code on that device |
| **What the locked first stage does** | **Defeats them.** Its integrity comes from hardware write-protection, not from a signature, so a forged signature cannot rewrite it. It accepts only releases that verify against its hash-anchored slots | **Depends on the part.** Physical resistance varies widely by family and generation. Public research has shown that on some older general-purpose MCU families, physical access can defeat flash protections (N70) |
| **Scale of harm** | Whole fleet | One device, unless that device holds something shared by the fleet |

**Consequence [I].** The lock is the right defence against the quantum-era threat this atlas is about, because that threat is remote and scales. Against a local attacker it is one layer among several, and the design must ensure that **one opened device never yields fleet-wide authority**. That is achieved by what the device does *not* hold (§8.3), not by how strong its lock is.

## 8.2 Choosing parts: ask for evidence, not adjectives

Procurement questions that separate parts without anyone needing attack expertise [I]:
1. **Independent certification that covers physical attacks.** Which scheme, which level, which lab, and which attack classes were in scope. For example, ST reports PSA Certified Level 3 and SESIP Level 3 for STM32H5 and STM32U5 families [V]. Nordic documents countermeasures against fault attacks for its nRF54L series and does not claim them for older series [V].
2. **Protection across lifecycle states.** Is protection preserved through RMA, debug re-enable and ownership transfer? These are the side doors of R9.
3. **Documented countermeasures and their limits**, in the vendor's security manual rather than its marketing.
4. **Field history.** Have public results affected this family or its predecessors? No public results for a newer certified part is **absence of evidence, not proof**.
5. **Record the answers in the CBOM** (11.7), so a later finding against a part family can be mapped to affected devices within hours.

## 8.3 Layering: the lock is one wall of several

The CODIT model (Pattern 26) suggests walls that each limit spread in a different direction. Applied to a device:

| Wall | What it limits | Mechanism |
|---|---|---|
| **1. Hash-anchored, locked first stage** | Remote code replacement | Write-protected boot entry; multi-class hash slots; floor rule (11.1) |
| **2. Immutable ROM/OTP checks where the part offers them** | Tampering with the first stage itself | Vendor ROM verifying a hash of the first stage, where available |
| **3. Nothing secret in the first stage** | What an opened device reveals | The first stage stores **only hashes of public keys**. Opening it reveals nothing useful for forging |
| **4. Per-device keys, diversified from a master that never leaves the enclave** | Spread from one opened device | One device's key opens one device (11.3) |
| **5. Fleet evidence and anomaly signals** | Undetected compromise | Signed state reports; a device whose state changes outside a window raises a danger signal (Pattern 3) |
| **6. Tamper evidence and procedures** for the highest-consequence classes | Unnoticed physical access | Seals, inspection at windows, custody records for spares and returns |
| **7. Containment** | Escalation from device to network authority | Enclaves (11.6); devices hold no authority over peers |

**Rule [I].** Walls 3 and 4 matter most. A design in which every device holds only its own key and only public hashes turns a physical compromise into a local incident, whatever the lock's strength.

## 8.4 Where the signing keys live

The other end of every chain is the signing infrastructure. One signing key covers a whole fleet, so its physical protection matters more than any field device's [I].
- **Hardened HSMs with documented physical and side-channel countermeasures**, validated under FIPS 140-3 or equivalent.
- **Stateful hash-based keys need state that cannot be cloned or rolled back** (R6, N51). LMS and XMSS state must live in hardware that refuses export and restore; SP 800-208 already requires this for those schemes.
- **Quorum for release signing** (11.8), with members drawn from disjoint assumption classes (M2).
- **Post-quantum implementations need the same hardening as classical ones.** The extinction record (2.6) includes timing problems found and fixed in ML-KEM and ML-DSA implementations. Prefer implementations with constant-time validation and, where available, formal verification (§8.8).

## 8.5 Post-quantum silicon is arriving, and it is updatable

| Product | Date | What it offers | Status |
|---|---|---|---|
| **Caliptra 2.0** (open-source silicon root of trust, CHIPS Alliance) | Apr 2025 | Adds the Adams Bridge ML-DSA accelerator | [F] |
| **Caliptra 2.1** | Oct 2025 | Adams Bridge 2.0 with ML-DSA and ML-KEM, and side-channel countermeasures. Academic work had reported leakage in the earlier accelerator (2.6) | [F] |
| **Lattice MachXO5-NX TDQ** (control FPGA) | 13 Oct 2025 | Vendor claims CNSA 2.0 algorithm support and **in-field update of cryptographic algorithms** | [V] |
| **NXP SAM AV3** (secure access module for readers) | Shipping | A separate secure element, with hardware certified to Common Criteria EAL6+, that holds reader keys outside the host processor | [V] |

**What this changes [I].** Two design patterns are now commercially real. **Open, auditable roots of trust** (Caliptra) let operators inspect what they rely on. **Field-updatable cryptography in the root of trust** (MachXO5-NX TDQ) turns algorithm agility from a slot-reservation exercise into a supported feature. Neither yet has public long-term field data, and the second relies on vendor claims.

## 8.6 Identity from physics: PUFs and provenance markers

- **Physical unclonable functions.** Pappu and colleagues introduced physical one-way functions in Science in 2002. Rührmair and colleagues (2010) later showed that several "strong" PUF designs could be modelled by machine learning from observed challenge–response pairs. The defensive reading: PUFs are good for **deriving and storing a device key** (with error correction), but treating a strong PUF as an authentication protocol by itself needs care. [F]
- **Supply-chain provenance markers.** The US Defense Logistics Agency required DNA marking for microcircuits in Federal Supply Class 5962 from 15 November 2012, using Applied DNA Sciences' technology, and the programme was still active in 2021. Physical provenance complements cryptographic identity, especially for spares and refurbished parts (N36). [F]

## 8.7 Memory that outlives the chip

Evidence that must stay verifiable for decades (7.5) needs a medium that outlives vendors.
- **Glass.** Microsoft's Project Silica writes data into glass with femtosecond lasers. A Nature paper published in February 2026 describes writing into ordinary borosilicate glass, and Microsoft claims lifetimes of at least 10,000 years. [V; the lifetime is an extrapolation]
- **DNA.** Grass and colleagues (2015) encapsulated DNA in silica and extrapolated survival of about a million years at −18 °C. DNA Fountain (Erlich & Zielinski, Science, 2017) reached a theoretical density of 215 petabytes per gram. [D; extrapolations]

**Lesson [I].** The medium is not the binding constraint; the **format** is. The BBC Domesday Project was unreadable after 16 years (7.4) while 1,000-year-old parchment was not. Long-lived evidence needs re-encoding on a schedule (RFC 4998 renewal, I-29), not just a durable substrate.

## 8.8 Verified code for the parts that cannot change

The immutable first stage is small, so it is a candidate for formal verification, in line with keeping the germline minimal (Pattern 17) and the hex0 seed argument (7.5).
- **Verified post-quantum code is in production.** The formally verified libcrux ML-KEM implementation is reported in use by Firefox, OpenSSH and Signal (2025 talk) [2nd]. OpenSSH has used a hybrid post-quantum key exchange by default since 2022 (Streamlined NTRU Prime with X25519). OpenSSH 9.9 (19 Sep 2024) added mlkem768x25519-sha256, and OpenSSH 10.0 (9 Apr 2025) made it the default. [F] That is another early adopter that migrated twice (§7.6, lesson 4).
- **Verified kernels have survived red teams.** The seL4 microkernel was used in DARPA's HACMS programme, including on Boeing's Unmanned Little Bird helicopter. [F]

**Proposal [H].** Verify the first stage's hash-based verifier, slot logic and floor rule formally, and publish the proofs with the code. The first stage is the one component every later migration depends on, and the one that can never be patched.

## 8.9 The trust cartridge (I-31)

**Idea [H].** Put the replaceable part of trust — keys, algorithm implementations, slot set — into a **field-replaceable, certified module**, in the way that SIM cards, eSIMs and reader SAMs already work. Cryptographic migration then becomes **swapping a cartridge at a planned window**, not replacing a device.

| For | Against |
|---|---|
| Decouples a 30-year device from a 10-year cryptographic life | Needs physical access, which fits window staging but not remote sites |
| Certifies the cartridge once for many host designs | The cartridge supply chain becomes a new side door: provisioning must itself be post-quantum (GSMA flags remote SIM provisioning for exactly this reason, 7.7) |
| Proven at scale in telecom and payments | Sockets and contacts in harsh environments; added cost per device |
| Lets an operator keep its own trust root independent of the OEM (R3) | The host still needs a first stage that decides which cartridges to trust |

**Status.** A strong candidate for C2–C3 devices with long lives and planned maintenance. It complements the first stage rather than replacing it.

## 8.10 Hardware rules for this edition [I]

1. **Use the lock against remote forgers. Count on it against physical attackers only to the extent that independent certification shows.**
2. **No fleet secret in any field device.** Per-device keys only.
3. **The first stage holds only public hashes.**
4. **Record certification evidence per part in the CBOM**, so a new finding maps to affected devices quickly.
5. **Keep signing keys in hardened HSMs under quorum, and keep stateful hash-based state unclonable.**
6. **Prefer replaceable trust modules where device life far exceeds cryptographic life.**
7. **Formally verify the smallest immutable parts.**

---

# 9. Quantitative models built for this edition

Earlier passes reasoned about ordering, diversity and hold-downs qualitatively. This pass built small, reproducible models: Python scripts, kept alongside the atlas, with every assumption stated. They are **models, not measurements**. Their value is that they make the structure of a decision visible and testable, and in two cases they overturned a recommendation.

## M1. Migration order as network immunisation

**Question.** Fleets cannot migrate everything at once. In what order should devices be migrated to shrink, fastest, the blast radius of a forged classical credential?

**Inspiration.** Epidemiology and network science:
- In heterogeneous networks, random immunisation needs very high coverage.
- Targeting hubs works far better (Pastor-Satorras & Vespignani, Phys. Rev. E, 2002).
- **Acquaintance immunisation** reaches hubs without a map of the network: pick random nodes and immunise a random *neighbour* of each (Cohen, Havlin & ben-Avraham, PRL, 2003). [F]

**Model.**
- **Purdue-like network.** 1,146 nodes and 2,479 trust edges across 20 sites. Each site has 2 gateways, 3 engineering workstations, a historian, 10 controllers (30% safety class C3) and 40 field devices (60% class C1 symmetric-only, 40% class C0). Workstations program two controllers each and connect to a shared vendor remote-access portal and to the enterprise PKI. Each site has one shared field key linking 15 field devices (problem N10).
- **Scale-free control.** A Barabási–Albert graph (n = 2,000, m = 2).
- **Trust edges.** An edge is a path a CRQC-capable attacker can traverse by forging a classical credential that the far end accepts.
- **Migration.** Migrating a node to PQ-safe, diversified credentials removes it as a stepping stone.
- **Metric.** The largest connected set of unmigrated nodes, as a fraction of all nodes: the worst-case blast radius of one forged credential.

**Results** (5 seeds; [C], synthetic topology):

| Strategy | Knowledge needed | Blast radius after migrating 10% of nodes | 20% | 40% | Fraction to migrate before blast radius ≤ 5% |
|---|---|---|---|---|---|
| Random | none | 87% | 75% | 50% | **73%** (67–82%) |
| Acquaintance (random node → migrate a random neighbour) | local observation only | 74% | 49% | 6% | **44%** (38–50%) |
| Class-ordered (C5 authorities → C4 concentrators → C3 → C2 → C1 → C0) | device class only | 18% | 4% | 1% | **10%** (9–11%) |
| Degree-targeted, recomputed after each removal | complete trust graph | 4% | 1% | 0.1% | **6%** |

On the scale-free control the needed fractions were 79% (random), 44% (acquaintance) and 16% (degree-targeted).

**What this changes:**
1. **Migrate authorities and concentrators first.** In this topology, migrating all 126 C4/C5 nodes (11% of the fleet) cut the worst-case blast radius from 100% to 4.5%. Class ordering came close to the theoretical best (degree-targeting), because device class is a good proxy for "hub". This quantitatively supports the class model of Part 12.
2. **Without an inventory, migrate acquaintances, not random devices.** Many operators do not know their trust graph (R7). The acquaintance rule needs only local observation: pick any device, look at what it talks to or trusts, and migrate that. It cuts the work by **about 40% compared with random** order (44% of nodes instead of 73%). That makes it a practical, inventory-free migration heuristic, and new to this atlas. [H, supported by M1]
3. **Remote forgery paths close early.** In the model, migrating the six internet-facing authorities (vendor portal, enterprise nodes, PKI, KDC) reduced the CRQC attacker's *remote* reach to zero. Random migration of 20% still left 74% reachable. This result is partly built into the model: remote entry is assumed to happen only through those nodes. The design lesson is still sound: **the CRQC-specific remote attack surface is the set of internet-reachable systems that accept classical credentials, and they should be first.**
4. **Diversifying the shared field key alone barely changed connectivity** (98% blast radius), because field devices stay connected through controllers. Key diversification matters for a *different* threat: physical extraction from one device (N10), not graph reachability.

**Caveats.** The topology is synthetic, edges are undirected and unweighted, and real trust graphs need measurement. E-N4 (Part 16) applies the same analysis to an anonymised real plant graph.

Reproduce with `models/immunise.py` and `models/immunise2.py`.

## M2. Quorums over assumption classes: the disjoint-quorum rule

**Question.** If authority changes need two signatures from a set of key slots, which pairs should count?

**Model.**
- Each key is mapped to the hardness assumptions it depends on, using a **conservative dependency model** in which a scheme falls if any assumption it relies on falls:
  - ML-DSA → {Module-LWE/SIS, Keccak/SHAKE};
  - LMS-SHA-256 → {SHA-256};
  - SLH-DSA-SHAKE → {Keccak};
  - ECDSA → {ECDLP, SHA-256}.
- Illustrative break probabilities over the asset horizon (**assumptions, not forecasts**): ECDLP 0.5, MLWE 0.05, SHA-256 0.005, Keccak 0.005. All scenarios are enumerated exactly.
- "Honest" means the legitimate authority can still form a valid quorum from unbroken keys. "Attacker" means a valid quorum can be formed from broken keys.

**Results** [C]:

| Slot set and rule | P(honest can still change authority) | P(attacker can change authority) | Single assumption failures that hand the attacker a quorum |
|---|---|---|---|
| {ML-DSA, LMS-SHA-256, SLH-DSA-SHAKE}, **any 2 of 3** | 0.99475 | **0.00525** | **Keccak** (ML-DSA and SLH-DSA-SHAKE both fall) |
| Same slots, **only pairs with disjoint assumption sets** | 0.99002 | **0.00027** | none |
| {ECDSA, ML-DSA, LMS}, any 2 of 3 | 0.968 | 0.032 | **SHA-256** (ECDSA and LMS both fall) |
| {ECDSA, ML-DSA, LMS}, disjoint pairs only | 0.941 | 0.028 | none (but ECDLP + MLWE is plausible) |

**What this changes:**
1. **Correction to the previous edition.** That edition recommended the slot set {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256} as the "minimum robust set" and noted only that the ML-DSA/SLH-DSA-SHAKE pair "must be paired with care". The model shows that **with a plain 2-of-3 rule, a single Keccak failure gives the attacker a quorum**. The rule must **exclude quorums whose members share an assumption**. That cuts the attacker's chance about **19-fold** (0.00525 → 0.00027) for a half-point cost in honest availability.
2. **There are only two independent "waists".** Every NIST post-quantum signature in the standard toolkit depends on SHA-2 or on SHA-3/SHAKE. ML-DSA, FN-DSA and SLH-DSA-SHAKE use SHAKE; LMS and SLH-DSA-SHA2 use SHA-256. So **at most two pairwise-independent assumption classes exist** under the conservative model. A third slot adds *availability* (the honest party can survive more failures), not *independence*. This is the quantitative form of Pattern 21's hourglass.
3. **Classical keys must leave the quorum before a CRQC.** With ECDSA in the set, the attacker's chance is dominated by ECDLP falling together with any second assumption. This is why the floor rule retires the classical class as soon as two PQ classes are live.

**How conservative is the dependency model?** A Keccak collision attack does not automatically yield ML-DSA forgeries; ML-DSA's security proof uses SHAKE in specific ways. The model deliberately over-counts dependencies, in line with the cryptographer's red-team stance. Whether the SHA-2/SHA-3 split is "independent enough" remains a judgement (Part 5.3 of the earlier edition, Part 10 here).

Reproduce with `models/quorum.py` and `models/diversity.py`.

## M3. Hold-downs as proofreading

**Question.** How much does a staged authority change, in which each stage is an independent confirmation and any contradiction resets progress, reduce a forger's success?

**Model.** Each stage independently detects a forged state with probability d. A forger must pass all N stages, and an honest change is falsely reset with probability f per stage. [C]

| Per-stage detection d | N = 1 | N = 2 | N = 3 | N = 5 | N = 8 |
|---|---|---|---|---|---|
| 0.2 | 0.80 | 0.64 | 0.51 | 0.33 | 0.17 |
| 0.3 | 0.70 | 0.49 | 0.34 | 0.17 | 0.058 |
| 0.5 | 0.50 | 0.25 | 0.13 | 0.031 | 0.0039 |

Honest false-reset probability with f = 0.001 and N = 8 is 0.8%.

**What this changes.** The value of a hold-down comes from the **number of independent channels** that must be fooled, not from its calendar length. A 30-day hold-down watched through a single gateway is one stage, however long it lasts. Design guidance: three to five **channel-independent** confirmations, such as a witness network, a second-class signature, an on-site token and peer consistency, chosen so that no single compromised component can satisfy two of them. (Pattern 2 gives the biology.)

## M4. Clocks that drift: what an offline device can know about time

**Model.** Free-running real-time-clock drift (arithmetic [C]; crystal parameters to be confirmed against datasheets, Part 6):

| Oscillator | Drift (ppm) | Per year | Over 10 years |
|---|---|---|---|
| TCXO | ±2 | ±63 s | ±0.2 h |
| 32.768 kHz tuning fork at 25 °C | ±20 | ±631 s (10.5 min) | ±1.8 h |
| Same crystal at a sustained −40 °C (parabolic coefficient −0.034 ppm/°C²: −143.7 ppm) plus tolerance | ≈ −164 | ≈ −86 min | ≈ −14.3 h |

**What this changes.** A device offline for a decade can still know the date to within about a day, even with a cheap crystal in an arctic cabinet. It cannot know the time to the minute. **Validity should therefore be expressed in coarse epochs (months, not hours).** Freshness decisions need hours or minutes, so they need an external zeitgeber (Part 6). This puts a number on the earlier rule that time may tighten privileges but must never stop a safety function.

## M5. Exposure-years: what a replacement rate buys

**Model.** Fixed-ROM devices (classical-only, unlockable) are replaced at rate r per year. A CRQC arrives at year T. Exposure-years per installed device after T = (1−r)ᵀ / (−ln(1−r)). [C]

| Replacement rate | T = 5 | T = 8 | T = 12 |
|---|---|---|---|
| 5%/yr | 15.1 | 12.9 | 10.5 |
| 10%/yr | 5.6 | 4.1 | 2.7 |
| 20%/yr | 1.5 | 0.8 | 0.3 |

**What this changes.** Doubling the replacement rate from 5% to 10% cuts post-threat exposure by about three times. Doubling again to 20% cuts it by another four to nine times, depending on when the CRQC arrives. Exposure-years is a better programme metric than "percentage migrated" because it **integrates** risk over time, in the same way that integral feedback in bacterial chemotaxis drives a steady-state error to zero (Yi et al., PNAS, 2000; Pattern 34). A programme that tracks only the proportion migrated can look 90% done while the remaining 10% carries most of the exposure.

## M6. Random migration and the herd-immunity analogy

If a compromised device can, on average, compromise R₀ others through shared or forgeable credentials, random migration must cover 1 − 1/R₀ of the fleet to stop spread. That is 67% for R₀ = 3 and 90% for R₀ = 10 [C]. M1's 73% random threshold sits inside this range, and its 6–10% targeted threshold shows why targeting matters. The analogy is only qualitative: trust graphs are not well-mixed populations.

## M7. Per-device diversity versus fleet diversity

**Model.** Two families each break independently with probability 0.05 [C]:
- If every device uses family A, the fleet is lost with probability 0.05.
- If the fleet is split 50/50 between A and B, the chance of losing at least half rises to 0.0975, and the chance of losing everything falls to 0.0025.
- If **every device carries both** A and B (multi-class slots), losing everything still has probability 0.0025, but **no partial-loss events occur**.

**What this changes.** Bet-hedging across a population (Cohen 1966; bacterial persisters) is what nature does when individuals *cannot* carry more than one strategy. Engineers can usually do better: **put the diversity inside each device**. Fleet-level diversity remains the right tool only for class C1 devices that cannot hold two verifiers. For them, splitting a fleet across two key-delivery mechanisms (for example, half enrolled through a KDC and half through physical commissioning tokens) is genuine bet-hedging.

---

# 10. The solution space after two invention rounds and two red teams

## 10.1 How the solutions were generated

The invention round ran eight independent engines before combining their outputs:

- **(A) first-principles reinvention.** Strip away PKI and conventional secure boot, and start from "a device must know what it can trust".
- **(B) TRIZ contradiction analysis.**
- **(C) morphological design-space search.**
- **(D) inversion.** Assume the OEM, keys, clock, gateway or family have all failed.
- **(E) cross-domain transfer.** Spacecraft, DNSSEC, UEFI, KERI, Certificate Transparency, immune systems, error-correcting codes.
- **(F) constraint removal and progressive restoration.**
- **(G) mathematical and physical inspiration.**
- **(H) missing-category invention.**

This produced 110 hypotheses in seven families, 32 combinations and 11 architectures. The second pass then attacked them, adding ten stakeholder perspectives and an eight-position design debate.

**The TRIZ contradictions and the separations that resolve them** have survived both rounds, refined:

| Contradiction | Separation principle | Resolution (current form) |
|---|---|---|
| The root must be immutable, but cryptography must evolve | Separation by **abstraction** | Make immutable only a hash verifier plus *commitments to* keys in several assumption classes. The algorithms that evolve live in the updatable second stage. |
| Offline, yet revocable | Separation in **time** | Index floors and counter epochs instead of dates. Staleness reduces privileges and never touches safety. |
| Signatures are large, RAM is small | Separation in **space** | Verify-only devices with streaming hash verification (~1 KB stack). Signing happens in an HSM. |
| Rotate often, never disrupt | Separation by **condition** | Make-before-break with hold-down, staged dormant until the maintenance window. |
| Central governance concentrates risk | Separation by **responsibility** | Multiple organisations' key slots, combined as multisignature (no threshold maths needed), plus a contractual escrow trigger. |
| Certification resists updates | Separation by **partition** | Confine crypto to boot and update paths. Keep the last-known-good image running if crypto fails. |
| Debug is needed for RMA, and debug is a side door | Separation by **lifecycle phase** | No field debug. RMA by board swap. Lab units use UUID-bound PQ credentials. |

## 10.2 Status of every solution family after review

The full 110-item list is preserved in spirit but consolidated here. **Status:** ✅ build, 🔧 modified, 🔬 research only, ❌ killed.

**Roots and silicon**

| Idea | Status | Why |
|---|---|---|
| Multi-family committed manifest in OTP (ACK) | 🔧 → becomes the *locked continuity first stage* | The same idea without new ROM, deployable now on lockable parts |
| Hash-only ROM verifier in new silicon | 🔬 / procurement ask | Valuable for parts that cannot lock flash; silicon cycles are slow |
| Sunset latch as a new fuse | 🔧 → the floor rule | NSIB-style key-index invalidation already ships |
| Escrow leaf | 🔧 → slot 3 (operator or escrow key hash) | — |
| Pre-rotation (KERI-style) | 🔬 | Saves only 1.5–3× (Part 19) |
| A/B anchor slots, separate revocation and anti-rollback fuses, non-restorable counters | ✅ (existing practice) | Already implemented by vendors |
| SHA-2 + SHA-3 hash engine in every industrial MCU | ✅ procurement requirement | Two orders of magnitude for hash-based verification |
| Streaming LMS verification | ✅ | ~1 KB stack (demonstrated) |
| Dual-verifier boot | ✅ (exists, e.g. wolfBoot hybrid) | — |
| Physical-presence channel | ✅ niche | The only rescue for classical-only parts |
| Crypto co-processor or cell | 🔬 | Assessor acceptance unknown |
| PUF-wrapped anchors | ✅ for key storage only | ❌ as an agility mechanism: a PUF stores keys, it does not change algorithms |
| Certified masked PQ IP | 🔬 | Adams Bridge shows the maturity gap |
| ROM verification VM | ❌ | Enlarges immutable attack surface; replaced by flash plug-ins |

**Authority and governance**

| Idea | Status | Why |
|---|---|---|
| Threshold of organisations | 🔧 → independent multisignatures across slots | ≈9.9 KB for 3 × ML-DSA-65; no threshold maths needed |
| Threshold ML-DSA | 🔬 | Practical for small groups (Celi et al. ≤6 parties; Mithril; TALUS) but unnecessary for OT [2nd] |
| Neutral custodian utility | 🔬 | No demand evidence, liability unclear, liveness risk; FDO vouchers plus contracts do more with less |
| Workstation signing quorum | ✅ | Closes chain (6) |
| Witness transparency / offline co-signatures | ✅ | Detects targeted malicious releases |
| Capability-scoped, rate-limited authority | ✅ | Bounds the collusion limit |
| CRA-linked escrow triggers | ✅ contract clause | — |
| Procurement clause library | ✅ | Highest leverage per cost |
| Regulator evidence reports | ✅ via the evidence product | — |
| Attestation-priced insurance | 🔬 | No loss data (N35) |
| Sector root-of-roots | 🔬 / ❌ | Creates the concentration it was meant to avoid |
| Blockchain authority | ❌ | Needs liveness offline devices lack; transparency logs give the benefit more cheaply |

**Time and validity**

| Idea | Status | Why |
|---|---|---|
| Counter epochs and index floors | ✅ (exists in NSIB) | Not a product; a design rule |
| Staleness restricts privileges, never safety | ✅ design rule | — |
| Roughtime quorum (RFC 10049, Experimental) | ✅ optional accelerator | Connected sites only |
| Drift-bounded RTC windows, contact-sized epochs, laptop freshness tokens | ✅ | Layered freshness |
| Authenticated PTP | ✅ where time matters | Addresses N42 |
| TESLA beacons | 🔧 connected sites only | Needs loose clock sync |
| VDF time evidence | ❌ | Costly; depends on assumptions about attacker speed |

**Keys and protocols**

| Idea | Status | Why |
|---|---|---|
| Symmetric-first with ML-KEM enrolment | ✅ | Matches the 208–250 µs budget |
| GDOI-PQ profile (IEC 62351-9) | ✅ standards work | — |
| Per-device key diversification | ✅ mandatory | Addresses N10 |
| KEMTLS-PDK | 🔬 | Prior art; useful point-to-point |
| PQ gateway or proxy | ✅ (Aquaman is prior art) | Inside the enclave model |
| Pinned hybrid-strict | ✅ where both ends support it | Watch N45 |
| IKE_INTERMEDIATE profiles, RFC 8784-style PSK mixing | ✅ (implemented) | — |
| Ratcheted symmetric authority (SDLS-DR) | 🔬 | For disconnected assets |
| Split-ClientHello test harness | ✅ | Cheap, high-value lab tool |
| OPC UA PQ policy; DNP3-SA PQ key update | standards work | — |
| QKD for field devices | ❌ | Needs optical links, and gives no authentication without pre-shared keys |
| Per-frame PQ signatures on the process bus | ❌ | Physically impossible within 208–250 µs |

**Fleet and lifecycle**

| Idea | Status | Why |
|---|---|---|
| Passive CBOM | ✅ but commoditising | Incumbents parse OT protocols |
| Crypto passport | 🔧 → CycloneDX CBOM + TCG/IETF attestation | Do not invent a format |
| Migration twin / rehearsal | 🔧 engineering practice | Not a product |
| Walk orchestrator, canaries with rollback | ✅ | — |
| LMS index reservation | ✅ HSM feature | Commoditised |
| SLH-DSA for rare root signatures | ✅ once SP 800-230 is final | Removes state catastrophe |
| Spares activation and shelf refresh | ✅ | — |
| Orphan takeover kit | 🔧 → voucher escrow procedure | — |
| "PQ-ready" label | 🔬 | Worthless without independent lab testing |
| Fully autonomous AI migration | ❌ | Safety cases need human authorisation |

**Safety and assurance**

| Idea | Status | Why |
|---|---|---|
| Verify-only devices | ✅ | — |
| Certified fallback image (last-known-good) | ✅ | Fail-operational |
| TLA+ / Tamarin models of anchor and succession state machines | ✅ | Cheap and decisive |
| PQ-verify fault-injection suite | ✅ | — |
| Deadline-aware crypto scheduler | ✅ | Only if crypto runs at runtime |
| Constant-time or randomised ML-DSA loop | 🔬 | Iteration-count leak (P4) |
| Crypto-cell safety case | 🔬 | E-C1 decides |

## 10.3 A formal rule the passes discovered: single-assumption safety

"Two families" turned out to be a loose notion. If the escrow leaf is LMS and the operational root is LMS, "LMS + escrow" survives a lattice break, but **both die together if SHA-256 breaks**. The second pass formalised the requirement. [I]

Let **A(k)** be the set of hardness assumptions that key k depends on:
- ML-DSA → {MLWE/MSIS, SHAKE}
- SLH-DSA-SHAKE → {Keccak}
- LMS-SHA-256 or SLH-DSA-SHA2 → {SHA-256}
- ECDSA → {ECDLP, SHA-2}

A transition rule is **single-assumption-safe** if no single assumption's failure leaves the attacker able to satisfy an authorising quorum. Equivalently: every quorum the rule accepts must contain keys whose assumption sets are **pairwise disjoint in at least two members**.

**Minimum robust set, corrected in this edition.** The previous edition recommended the slot set {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256}, held by at least two organisations, and warned only that the ML-DSA/SLH-DSA-SHAKE pair "must be paired with care". The exact enumeration in Part 9 (model M2) shows that this is not enough:
- Under a plain **2-of-3** rule, a single Keccak failure hands the attacker a quorum, because ML-DSA (through SHAKE) and SLH-DSA-SHAKE fall together. With illustrative horizon probabilities, the attacker's chance of forcing an authority change is about 0.52%.
- Under a **disjoint-quorum** rule, which accepts only the pairs {ML-DSA, LMS-SHA-256} and {LMS-SHA-256, SLH-DSA-SHAKE}, no single assumption failure suffices. The attacker's chance falls to about 0.027% (19× lower), at a cost of about half a percentage point of honest availability.

The slot set stays the same. The **rule over it changes**: a quorum is valid only if its members' assumption sets are disjoint. [C]

**There are only two independent waists.** Every standard post-quantum signature depends on SHA-2 or on SHA-3/SHAKE, so at most two pairwise-independent classes exist under a conservative dependency model. A third slot buys honest *availability*, not attacker-side independence (Part 5, Pattern 21).

**Practical form [H].** Policy authors declare quorums, and a tool computes the minimal hitting sets of the assumption graph to reject any quorum that one assumption failure can satisfy. This is an automatable check (Part 18, idea I-4).

**A residual caveat [I].** Treating SHA-2 and SHA-3 as fully independent is a judgement call. They have different constructions (Merkle–Damgård vs sponge), but both are symmetric primitives studied by the same community. A cryptographer on the review board would discount the independence somewhat, not entirely.

---

# 11. The recommended architecture stack

Part 0 listed the stack. Here each element gets its thesis, mechanism, minimal and high-assurance forms, failure behaviour, resources, prior art and what it does **not** guarantee.

## 11.1 Continuity First Stage (replaces the Authority Continuity Kernel)

**Thesis.** The only code that must never change is a small hash-based verifier in **write-locked flash**. Its trust comes from the lock, not from a classical signature, and it holds commitments to keys in several assumption classes. Everything that evolves lives above it.

**Why the earlier ACK design was wrong in an important way.** The "existing-ROM" variant put the commitment behind a first stage that the classical boot ROM authenticates by signature. If that stage is remotely replaceable, a quantum-capable forger simply replaces it: the same HNDL-to-authority exposure the design was meant to remove. The variant is safe only if the first stage is **made immutable by a lock**, at which point the lock, not the signature, provides the security. Once seen, this makes the new ROM unnecessary wherever flash can be locked. [I]

**Minimal form (MV-1)**
- A locked first stage of ≈13 KB of flash. The demonstrated LMS verifier plus library was 12,864 B.
- One hash verifier:
  - LMS-SHA-256 **W4** (signature 2,508 B; ≈42 ms at 64 MHz in software), or
  - an SP 800-230 limited-use SLH-DSA set once that standard is final.
- **Three key-hash slots** (3 × 32 = 96 B): slot 1 for the OEM, slot 2 for the OEM in an alternate assumption class, slot 3 for the operator or escrow.
- An **index floor**. Advancing it requires a signature from a slot other than the one being retired.
- No time and no network dependency.

**High-assurance form (HA-1)**
- Hardware SHA-2 **and** SHA-3.
- Slots spanning {LMS-SHA-256, SLH-DSA-SHAKE, ML-DSA-65}. ML-DSA is verified in the second stage, under the slot's key hash.
- The single-assumption-safe rule enforced in the floor-advance logic.
- A/B second stages plus a **last-known-good** image that keeps running if both fail.
- A state machine verified in TLA+ and an independent second implementation of the verifier.
- A fault-injection campaign against the lock.
- UUID-bound PQ debug credentials, with debug disabled after commissioning.

```
[Reset] → [LOCKED FIRST STAGE: hash verifier + 3 key-hash slots + floor]
              │ verify second stage (LMS / SLH-DSA)    trust boundary = write-lock
              ▼
        [Second stage A | B] — ML-DSA, hybrid, protocol PQ stacks (updatable)
              │ fail → other slot → fail → last-known-good (process keeps running)
              ▼
        [Application]
Authority:     slot1 OEM-classA · slot2 OEM-classB · slot3 operator/escrow
Floor advance: needs a signature from a slot ≠ the slot being retired
Recovery:      board swap (field debug disabled)
```

**State machine (to be model-checked).** States are BOOT, VERIFY_B, VERIFY_ALT, RUN, LKG and BRICK_GUARD. Transitions:
- ADVANCE_FLOOR(k → k′) requires a valid signature under a slot of a different class, plus a journal commit before the floor is burned.
- REPLACE_SLOT3(owner) requires the voucher chain plus a slot-1 or slot-2 signature.

**Invariants to prove:**
- (a) no single-class key reaches ADVANCE_FLOOR;
- (b) a power cut at any step leaves a bootable image;
- (c) the floor never decreases.

**Resources.** About 13 KB of flash and 96 B of slot storage. Stack is about 1–1.6 KB for LMS. Verification takes 42 ms (W4 software) or about 12 ms (W8 with a hash engine) [E].

**What it does not guarantee:**
- Protection against a **local, physical** attacker. That depends on the part's certified physical resistance (Part 8.1–8.2; E-A4, revised). The design limits the harm instead: the first stage holds only public hashes, and each device holds only its own keys (Part 8.3).
- A fix path for bugs in the first stage itself (N20). Hence it must be tiny, formally verified and implemented twice.
- Unlimited future: three slots give **one generation of headroom**, not infinite agility.

**Interim note on stateful signatures.** Until SP 800-230 is final, MV-1 uses LMS, which keeps the index-reuse hazard alive. The hazard is manageable for root signatures because they are rare: a few per year, inside an HSM with index reservation. Switch to SLH-DSA limited-use sets when final, except where CNSA 2.0 mandates LMS/XMSS.

**Prior art.** Nordic NSIB (locked stage, key hashes, monotonic index invalidation); ST OEMiRoT; OCP Hardware Secure Boot ("table of hashes" of public keys in eFuses; revocation OTP must not be mixed with anti-rollback OTP); wolfBoot (LMS/XMSS/ML-DSA, hybrid); Intel patents US 11405213 and US 12137169 (fast XMSS/LMS verification for secure boot); OpenTitan (SPHINCS+ and ML-DSA work).

**Novelty classification:** a meaningful combination (multi-class slots plus a cross-class floor rule plus an owner slot in a locked stage), *not* a patent-safe invention. Defensibility comes from being the open reference implementation, from formal verification, and from porting and assurance services.

**What this edition adds to the first stage** (nature-derived patterns, Part 5; models, Part 9):
- **Disjoint-quorum rule** for every authority change (floor advance, slot replacement, lifecycle transition). Pairs of keys sharing an assumption do not count (M2).
- **Anergy.** Validly signed authority-change requests that lack the second class put that key into a reduced-trust state (boot-only) until a quorum restores it, and are reported (Pattern 1).
- **The molting protocol** for every class transition: provision alongside → shadow-sign → hide (reduce exposure) → shed under the disjoint-quorum rule → harden for E epochs (Pattern 15).
- **Budget sizing.** Every monotonic counter (floor indices, fuse bits, LMS leaves, SP 800-230's 2²⁴ signatures) is sized for the asset's life with margin. Any reset path is treated as the most dangerous capability (Pattern 18).
- **Duplication before change.** No verifier, slot or image is ever modified while it is the only copy (Pattern 16).
- **Germline minimalism.** Nothing goes into the locked stage that could live in the updatable second stage (Pattern 17).
- **Slot drills** (Part 18, I-13). Once a year, a release is verified through the *alternate* class alone in a controlled window, proving the path works before an emergency needs it. This is GREASE (RFC 8701) applied to trust anchors.
- **Physical threat class per part** (Part 8). The lock defends against the *remote, fleet-scale* forger, the threat a CRQC creates. Resistance to a *local, physical* attacker must be assessed per MCU family from published research and independent certification, not assumed.

## 11.2 Side-door closure

**Thesis.** Every classical authorisation path that can change code, keys, ownership or debug state is part of the root of trust, whether or not anyone designed it that way.

**Mechanism**
1. **Authorisation Surface Map** per part family. Enumerate debug, lifecycle/RMA, ownership, provisioning, configuration, licence and remote-access paths, with the algorithm and key holder for each (Part 18, I-1).
2. **Disable field debug** after commissioning. Handle RMA by board swap so that RDP-style permanent locks are not tempted down to weaker levels (N4).
3. **PQ debug credentials** for lab and RMA units only, bound to the device UUID so that one root break does not open the fleet (N2). Arm ADAC-style certificate chains carry PQ signatures.
4. **Lifecycle transitions** (TEST → PROD → RMA) authorised by the same multi-class rule as floor advances.
5. **Factory provisioning.** KEM-wrapped key injection, with per-device keys, and a provisioning log co-signed by the contract manufacturer and the OEM (N8).

**What it does not guarantee:** protection against physical invasive attacks on parts without tamper resistance.

**What this edition adds to side-door closure:**
- **The PAM rule for revocations** (Pattern 5). A revocation or blocklist record that would match the device's *current* authority set is structurally invalid unless it carries the escrow class and physical-presence evidence. Retired keys and bad images can be revoked normally; the OEM's live key cannot be "revoked" by a forgery to brick the fleet.
- **Reprogramming without the oncogene** (Pattern 20). Every reverse lifecycle transition (RMA, factory reset, re-provisioning) is designed so that it never reopens general debug access. Board swap replaces debug-based repair.
- **Reset as the cancer path** (Pattern 18). Any operation that rewinds a counter or restores a signer from backup needs the strongest authority plus presence, and leaves an indelible record in the device's ordered memory.

## 11.3 Symmetric process-bus fabric

**Thesis.** Keep the real-time data path exactly as it is: IEC 62351-6 MACs and AES-GMAC. Move all public-key work to a single, rare **enrolment** event.

**Minimal form**
- ML-KEM-768 enrolment at commissioning delivers a per-device key-encryption key. Decapsulation costs 22 ms and 14.2 KB of stack on an M0+, once.
- A KDC inside the enclave distributes group and session keys via GDOI.
- **Per-device key diversification**, so that no fleet key is ever shared (N10).

**High-assurance form**
- Replicated KDC with t-of-n unlock.
- TPM 2.0 v1.85 identity (ML-KEM EK, ML-DSA AK) on KDC and gateways.
- A GDOI-PQ profile proposed to IEC TC57 WG15.
- Missed rekeys recovered through the counter floor.
- Island sites run KDC replicas.

**What it does not guarantee.** A KDC compromise exposes every key it issued. Mitigate with HSM-held KEKs, scoping per substation and diversification.

**Prior art.** CCSDS SDLS Extended Procedures (symmetric-only master keys, with the SDLS-DR double-ratchet proposal); arXiv 2608.22123 (ML-KEM for Sampled Values); IEC 62351-9 GDOI.

**What this edition adds to the fabric:**
- **Group keys are colony odours** (Pattern 9). Anyone who acquires one is treated as kin, and insiders accumulate more. Bind group membership to per-device identity, keep GDOI group epochs short, and add **camouflage detection** to fleet evidence: alert on devices or accounts that hold keys beyond their role.
- **Signatures by decorrelation** (Pattern 7). Per-device diversification is not a nicety. It is the difference between the prinia's individually distinctive eggs and the ant colony's copyable shared odour.

## 11.4 Ownership continuity via PQ FDO vouchers

**Thesis.** Ownership lives **off-device** in a signed voucher chain (OEM → distributor → integrator → operator), as FIDO Device Onboard already specifies. Give the chain PQ signatures, and escrow the voucher files rather than keys.

**Minimal form**
- FDO vouchers with an ML-DSA or SLH-DSA signature profile.
- The operator's key hash provisioned into slot 3 at manufacture or first onboarding.
- Voucher files escrowed contractually.

**High-assurance form**
- Dual-class voucher signatures.
- An OEM-exit trigger in the contract: end of CRA support, insolvency, or failure to ship a security fix within N days.
- A transfer log witnessed by two parties.

```
OEM ─signs─► Voucher ─► Distributor ─► Integrator ─► Operator   (all off-device)
OEM exit:  voucher chain + escrow release ─► REPLACE_SLOT3 via the floor rule
```

**Why this replaces the neutral custodian.**
- It uses an existing standard and needs no new organisation.
- It has no liveness requirement at boot.
- Its liability sits in contracts, where it already belongs.

The voucher files become crown jewels (N7), and facility M&A diligence must include them (N52).

**Critical dependency [I]:** the OEM-exit path works only if **slot 3 was provisioned at manufacture**. Without it, an orphaned device can only be replaced.

**What this edition adds to ownership continuity** (the honeybee model, Patterns 12–13):
- **Heartbeat.** The OEM signs a quarterly liveness statement under a PQ class, published to the operator, the escrow agent and witnesses.
- **Trigger and window.** Contracts define the escrow trigger: N missed heartbeats, or no fix within M days of a critical CVE. The trigger is contractual and witnessed, never a device-side timer, because devices lack trustworthy time.
- **Supersedure first.** The preferred hand-over is planned while the OEM still exists. At the end of CRA support, the OEM signs the transfer of authority to slot 3 itself.
- **Swarming.** Facility sale or split is a defined voucher operation that transfers authority over a named sub-fleet.
- **Stop signals.** When two successors compete (an island authority and the fleet authority; an escrow claimant and the OEM's acquirer), quorum members attach signed objections. No irreversible step runs while an objection is unresolved, and a deterministic tie-break settles the case after escalation.
- **The "hopelessly queenless" warning.** A fleet without slot 3 cannot be requeened from inside. It drifts towards grey-market maintenance, or must be replaced. That is the cost to put in front of procurement.

## 11.5 Maintenance-window-aligned staging

**Thesis.** Cryptographic transitions fail because they arrive as unplanned work. Make them ride windows that already exist.

**Mechanism**
- The signed transition bundle is downloaded, verified and **staged dormant** in the inactive A/B slot long before the window.
- In the window, a single, short, pre-rehearsed activation step runs. The device then emits a **signed state report**: floor index, active slots, image hash and policy hash.
- Crypto-only changes are kept separate from functional changes, so they do not bundle with recertification (N48).
- Rehearse against a lab replica of the site, using the "migration twin" as an engineering practice.

**Why it matters.**
- Fewer than 30% of facilities patch on a schedule, and only 15% in routine windows. [2nd]
- The economic model in Part 14 shows the value lies in converting emergency work into planned work.

**What it does not guarantee.** It cannot help if no window comes before the threat. Attackers who learn the windows gain timing knowledge, so staged artefacts must be signed and attested.

**What this edition adds to staging** (Patterns 10, 29–31; Part 7):
- **Prescribed burns, not suppression.** Small, regular, planned changes keep the change path healthy. Deferral builds "change debt" until a forced, catastrophic change (Pattern 29).
- **Two-process scheduling.** Borrowed from the sleep model: activation happens when accumulated pressure (unapplied changes, exposure-years) meets an allowed gate (the plant's maintenance calendar). Either alone is not enough.
- **Persisters.** In an emergency rollout, a defined fraction of devices stays on last-known-good until the new state is proven in the field. This is bet-hedging against a defective fix.
- **No global simultaneous activation.** The 2024 CrowdStrike incident showed that one faulty security update can take down millions of machines at once (Part 7). Activation is staged by site, class and cohort, with automatic halt on adverse signals.

## 11.6 Enclave containment with a dated exit

**Thesis.** For devices that cannot be changed, stop pretending to migrate them. Contain them behind a PQ-terminating boundary, inventory them, and schedule their replacement.

**Minimal form.** A PQ-terminating gateway, a passive inventory, and a replacement plan with dates and budget lines.

**High-assurance form.**
- Two gateways from different vendors, avoiding a monoculture.
- TPM v1.85 identity.
- Signed gateway configuration.
- Witnessed logs.

**Honest limits [I].**
- Containment protects the **link**, not the device's own firmware trust.
- It concentrates trust in the gateway (N43).
- "Temporary" enclaves tend to become permanent. The **dated exit plan** is therefore part of the design, not paperwork.

**What this edition adds to enclaves** (Patterns 14, 26–27):
- **Seal what you cannot heal** (CODIT). The enclave is the barrier zone formed after the wound. It contains decay; it does not cure it. New growth, meaning replacement, must happen outside.
- **Senescence, not death.** Devices inside the enclave whose authority view is stale keep running their control function, accept no authority changes, and announce their state in every report.
- **Sectored enclaves.** Several small enclaves with independent boundaries, rather than one large one, so that one boundary failure loses one sector (bristlecone sectoring).
- **Exit clocks** (Part 18, I-9). Every legacy exception carries a signed expiry epoch that the gateway surfaces as it approaches.

## 11.7 Fleet crypto-state evidence

**Thesis.** The missing feedback loop (Part 4.3) is closed by devices and observers reporting cryptographic state in **existing** formats, packaged as compliance evidence that someone already has to produce.

**Mechanism**
- Signed state reports from devices that can sign them.
- Passive inference for silent devices: parse OPC UA OpenSecureChannel policies, TLS/DTLS supported groups, IKE proposals and GDOI.
- Output as CycloneDX CBOM, plus TCG/IETF RATS attestation where available.
- Mapped to CRA Article 14 reporting and India's critical-infrastructure inventory requirement.

**Commercial caution.** Passive parsing will be absorbed by incumbent OT-visibility vendors. The durable value is in **evidence that regulators accept**, not in the parser.

**What this edition adds to evidence** (Patterns 3, 14, 34; Part 7):
- **Alarm on danger, not novelty.** Monitor authority-changing events (floor advances, slot replacements, lifecycle transitions, voucher redemptions, safety-logic signature changes) and physical-process inconsistency, rather than every unfamiliar packet.
- **Exposure-years as the programme metric.** Integrate unmigrated exposure over time (M5), rather than reporting the percentage migrated. Integral feedback is what drives a residual error to zero.
- **Evidence that stays verifiable for decades.** State reports, voucher chains and decommissioning receipts are archived with Evidence Record Syntax-style renewal (RFC 4998). Hash trees are re-timestamped under stronger algorithms *before* old ones weaken (Part 7).

## 11.8 Workstation signing quorum

**Thesis.** Configuration, protection settings and safety-system logic (chain 6) need the same authority discipline as firmware.

**Mechanism**
- Settings files and project archives are signed by a 2-of-n quorum: an engineer and a reviewer, with keys in tokens or TPM v1.85.
- Devices that can verify do so.
- Others are checked at the gateway against a signed manifest.

**Watch for:** workflow friction, and AI configuration assistants bypassing the quorum (N47).

## 11.9 Complexity removed versus introduced

| Design | Components | Trust relationships | New dependencies | Device resources | Maintenance |
|---|---|---|---|---|---|
| Earlier ACK (new ROM) | ROM + OTP manifest + latch + escrow leaf | 4–5 | MCU vendor ROM cycle, licensing | 32 B OTP + fuses | Licence management |
| **Continuity First Stage (MV-1)** | Locked stage + 3 hashes + floor | 3 | Lock integrity | ~13 KB flash, 96 B | Open project; needs a maintainer foundation |
| Threshold custodian (earlier) | Utility + signers + legal entity | 3+ organisations | Legal, liveness | — | High |
| **FDO-PQ vouchers** | Voucher files + contract | One chain | FDO | KB-scale, off-device | Low |
| Time-free validity layer (earlier) | Library + metadata profile | — | — | Small | Medium |
| **Index floor (now)** | A counter + a rule | — | — | Bytes | Negligible |

**Net [I].** The redesign moves complexity into **contracts and existing standards that already have owners**, rather than inventing new organisations and silicon.

## 11.10 Long-term lifecycle behaviour

Assumptions: a CRQC is plausible between 2030 and 2040, CRA support lasts 5 years, and assets live 25 years.

| Architecture | 5 years | 10 years | 20 years | 40 years |
|---|---|---|---|---|
| Classical legacy | Containable | Side doors forgeable if a CRQC exists | Replace | — |
| Continuity First Stage | Fine | One floor advance used | Slot exhaustion possible | Replace; hash conservatism helps |
| Symmetric fabric | Fine | KDC refresh | Platform replaced | Protocol replaced |
| FDO-PQ ownership | Fine | OEM exits; vouchers used | Voucher format migration | Unknown |
| Enclave | Fine | Boundary refresh | **Becomes a permanent risk** unless exited | — |

---

# 12. Allocating security by device class

One universal architecture is inefficient. A battery sensor and a protection relay do not need the same cryptography. The danger is the opposite mistake: a **weak class becomes a hidden path into a strong one**. The class model below was the first synthesis's proposal [H]; this edition added the migration order in 12.4. It builds on the second pass's recommendation of "hash engines for new designs, enclaves for legacy".

## 12.1 The classes

| Class | Typical devices | What it must do | What it must never do | Mechanisms |
|---|---|---|---|---|
| **C0: Inert** | Legacy sensors, drives, old RTUs with no crypto or no updates | Nothing cryptographic | Hold authority over anything | Enclave, passive inventory, replacement date |
| **C1: Symmetric-only constrained** | LoRaWAN or 802.15.4 sensors, M0-class nodes | MAC its data with a **diversified** key | Sign; share a fleet key | Commissioning-time enrolment (physical or KEM via a gateway); hash-verified updates if updatable |
| **C2: Verify-capable controller** | PLCs, RTUs, IEDs on M4/M33/A-class parts | Verify firmware and authority; decapsulate once at enrolment | Hold signing keys; allow field debug | Continuity First Stage, symmetric fabric member, signed state report |
| **C3: Safety-critical** | Protection relays, SIS logic solvers, interlocks | Everything C2 does, with crypto confined to boot and update | Run public-key operations in the control loop; fail closed into a hazard | C2 plus last-known-good, crypto partition, quorum-signed settings |
| **C4: Concentrators** | Gateways, KDCs, data diodes, engineering workstations, historians | Full PQ stacks, TLS/IKE hybrids, attestation | Become a single point of fleet-wide trust | TPM v1.85 identity, dual-vendor, witnessed logs |
| **C5: Authorities** | Release-signing HSMs, voucher holders, debug-credential issuers | Sign, under a multi-class quorum | Hold single-family authority alone | HSMs, index reservation (LMS) or SLH-DSA, transparency logs |

## 12.2 The anti-weak-path invariants

These are what keep the tiering honest.

1. **Dominance rule.** No device of a lower class may hold authority, keys or configuration rights over a device of a higher class. A C1 sensor's key never opens a C3 relay's settings.
2. **Diversification rule.** Any symmetric key below C4 is unique per device and derived from a diversification key held only at C4 or C5.
3. **Boundary rule.** Every C0 and C1 device sits inside a zone whose boundary is C4. Crossing the boundary requires PQ-protected channels.
4. **Authority isolation.** C5 keys never touch C4 networks online. Signing happens in HSMs, with offline or witnessed transfer.
5. **Promotion rule.** A device can move to a higher class only by replacement or by a quorum-signed re-commissioning. It can never move by configuration alone.

## 12.3 Three allocation models compared

| Model | Description | Cost | Complexity | Security boundary | Long-term maintenance |
|---|---|---|---|---|---|
| **Universal** | Every device runs the full PQ stack | Highest; infeasible for C0/C1 | Uniform, but forces impossible requirements | Clear on paper, unrealised in practice | Every device migrates every generation |
| **Tiered (recommended)** | Classes C0–C5 with invariants | Proportional to risk | Moderate; needs class assignment | Explicit at zone boundaries | Most migrations happen at C4/C5 |
| **Dynamically adaptive** | Devices change their behaviour with the threat level, for example strict hybrid after an alert | Medium | High; new failure modes | Can drift; needs verified policy | Hard to certify for C3 |

**Recommendation [I].** Use the tiered model, with one adaptive element: **floor advances and policy tightening are the only adaptive actions**, and they are quorum-signed and staged. Adaptive behaviour inside C3 is excluded, because safety cases need predictable behaviour.

## 12.4 Classes also decide the migration order

The class model has a second use: it **orders the migration**. In the network-immunisation model (Part 9, M1), migrating C5 authorities and C4 concentrators first had these effects:
- About 11% of nodes migrated brought the worst-case blast radius of a forged credential below 5%, close to the theoretical best order that needs a full trust graph.
- Random order needed about 73%.
- Where no inventory exists, the **acquaintance rule** (take any device, migrate something it trusts or talks to) needed about 44%.

Ecology has a name for nodes whose removal reshapes a whole system: **keystone species**. In OT trust graphs, the keystones are:
- engineering workstations;
- vendor remote-access portals;
- the PKI;
- the KDC;
- gateways.

They are few, mostly updatable (C4/C5) and should be first. [C/I]

---

# 13. Seven deployment scenarios, end to end

Each scenario was walked through for initial conditions, steps, failure points, recovery and remaining risk. At the end, a verdict says which ideas survive real deployment.

### Scenario A: a new industrial device designed today
- **Choose** an MCU with lockable flash and a SHA-2 + SHA-3 engine. Check that its debug, lifecycle and provisioning paths are documented (side-door audit).
- **Provision** three key hashes across two assumption classes, plus slot 3 for the operator or escrow. Burn the floor at 0. Inject per-device keys with KEM wrapping and a co-signed provisioning log.
- **Ship** with debug disabled at commissioning, an FDO-PQ voucher, and a signed state report.
- **Failure points:** contract-manufacturer key injection (N8) and lock faults.
- **Remaining risk:** physical attacks on the lock.
- **Cost driver:** roughly 13 KB of flash, a hash engine, and provisioning-line changes.

### Scenario B: an old device that cannot be modified
- **Achievable:** link confidentiality and integrity inside an enclave, segmentation, monitoring, and a replacement schedule.
- **Impossible:** device-level authority continuity, and protection against a forged firmware image if the device accepts classical signatures from any reachable path.
- **Steps:** inventory → segment → PQ gateway → disable remote firmware paths where possible → date the exit.
- **Remaining risk:** gateway concentration, and the enclave becoming permanent.

### Scenario C: a mixed-vendor facility
- **Steps:**
  1. Map all six authority chains per vendor, including debug and engineering-workstation paths.
  2. Assign device classes.
  3. Put zone enclaves at C4 boundaries.
  4. Use FDO where vendors support it.
  5. Produce fleet evidence (CBOM).
  6. Apply the workstation quorum for configuration.
- **Failure points:** integrator handover loses knowledge; vendors disagree on algorithms (N31).
- **Remaining risk:** divergent trust state across vendors. A signed state report from each class-C2+ device is the detection mechanism.

### Scenario D: a long-disconnected installation
- **Design:** MV-1 with W4 (no hash engine assumed). Use contact-sized epochs. If decades offline and catch-up matters, use Merkle-committed future key sets.
- **Steps:** pre-commit at manufacture; update only at visits using a technician freshness token; staleness reduces privileges and never the safety function.
- **Failure points:** freeze attacks (undetectable, so bounded only); the secrecy of future keys over decades (N40).
- **Time, from nature** (Part 6). Treat the device clock like a circadian clock:
  - a free-running oscillator, temperature-compensated where possible, with a known drift bound (about ±11 min per year at 20 ppm);
  - entrained at every opportunity by independent zeitgebers: a technician token at visits, grid-cycle counting where the device is grid-connected, authenticated time when connected, and peer medians in islands.
  - Validity is in coarse epochs, consistent with the drift bound.
- **Dormancy, from seeds** (Patterns 25, I-5). Spares and long-idle units hold only the first stage and slot hashes, and "germinate" only on a combination of cues: a valid voucher, the current bundle, and an on-site token.

### Scenario E: the OEM disappears
- **With slot 3:**
  1. The escrow trigger fires.
  2. The operator presents the voucher chain.
  3. REPLACE_SLOT3 then hands authority to the operator's key, via the floor rule with a remaining-class signature.
  4. The operator, or a contracted maintainer, signs future images.
- **Without slot 3:** replacement or an enclave. There is no cryptographic path.
- **Failure points:** voucher files lost; contracts silent on the trigger.
- **Lesson:** OEM-exit protection is bought at manufacture, not later.
- **The honeybee version of this scenario** (Pattern 13):
  - The OEM's quarterly heartbeat stops.
  - The contract's trigger fires after the agreed window.
  - Slot 3 (the "young larva" prepared at manufacture) becomes the new authority through the floor rule.
  - Competing claims (an acquirer of the OEM's assets, an escrow claimant) are settled with signed objections and a deterministic tie-break before any irreversible step.
  - Without slot 3 the fleet is "hopelessly queenless". Without an outside rescue it drifts towards grey-market maintenance.

### Scenario F: an emergency cryptographic event
- **Example:** a lattice break, or compromise of a signing key in one class.
- **Steps:**
  1. Sign a floor advance with the surviving class (SLH-DSA-SHAKE or LMS-SHA-256).
  2. Stage the bundle.
  3. Activate in the next window. Use an emergency window only for exposed, high-consequence assets.
  4. Collect signed state reports.
- **Cost driver:** unplanned downtime. ABB's 2023 survey median is $124,669 per hour, US about $103k [V, plant-oriented].
- **Remaining risk:** devices with only one class. They can only be contained.
- **Do not let the cure become the outbreak** (Patterns 4 and 31; Part 7). Emergency rollouts are where security systems most often harm their hosts. The 19 July 2024 CrowdStrike update crashed an estimated 8.5 million Windows machines worldwide. Keep a **persister fraction** on last-known-good until the fix is proven, stage by cohort, and halt automatically on adverse signals.

### Scenario G: a planned fleet-wide transition
- **Steps:**
  1. Inventory (evidence) and class assignment.
  2. Lab rehearsal on a replica.
  3. Canary sites.
  4. Staged dormant bundles.
  5. Activation over one or two window cycles.
  6. Signed state reports as completion evidence.
- **Failure points:** non-adoption, which is the dominant risk; strict pinning breaking interoperability (N45).
- **Duration:** bounded by the window cycle (annual or biannual), not by engineering. Plan **multi-year**.
- **Order:** C5 → C4 → C3 → C2 → C1, with the acquaintance rule wherever the inventory is incomplete (Part 9, M1).
- **Irreversible steps wait for every dependent participant to report ready**: the spindle-checkpoint rule (Pattern 19). A single unready participant holds the classical sunset. After a bounded hold, the step escalates to human review rather than waiting forever.
- **Molting** (Pattern 15). Shadow-sign every release in both classes for at least one window cycle before shedding the old class.

**Survives real deployment:** the locked stage, side-door closure, the symmetric fabric, voucher escrow, window staging and enclaves.

**Works only on paper today:** neutral custodians, threshold ML-DSA succession, a separate time-validity layer, attestation-priced insurance, and sector root-of-roots.

---

# 14. Economics: who pays, why they wait, and what makes them act early

## 14.1 The actors

| Question | Answer |
|---|---|
| Who experiences the problem? | The operator |
| Who owns the asset? | The operator |
| Who controls the technical decision? | The OEM (and, upstream, the MCU vendor) |
| Who controls the budget? | The operator's maintenance and capex budget, shaped by regulators in utilities |
| Who bears the liability? | Split by the CRA: the OEM during the support period, the operator after |
| Who implements? | The integrator |
| Who maintains? | The OEM during support, then whoever holds the vouchers and keys |
| Who benefits from reduced risk? | The operator, insurers and the public |
| Who can block? | Plant engineering (availability), procurement (cost) and safety assessors |
| Who becomes dependent? | Whoever holds signing authority and voucher files |

**The core coordination failure [I].** The party with the technical control (the OEM) is not the party with the long-term risk (the operator). The CRA's 5-year support floor caps how far the OEM will commit. Every mechanism that moves authority to the operator at the right moment helps: slot 3, vouchers and escrow triggers.

## 14.2 The market, corrected and demoted

- **Bottom-up US components:** $113.5M–$565M per year. Global at a 30% US share: $113.5M ÷ 0.30 = **$0.38B** to $565M ÷ 0.30 = **$1.88B**. A standalone vendor at 10% share earns **$38M–$188M per year**. [E; inputs unverified]
- **Adjacent transactions** (cited, not re-verified): Nozomi Networks ~$883M; Venafi ~$1.54B; CyberArk ~$25B; Accenture's three cyber acquisitions ~$4.175B combined; Keyfactor >$200M ARR.

**Interpretation.** A pure "OT-PQC vendor" is a niche. The large outcomes in adjacent markets came from owning **machine identity** or **OT visibility** platforms. PQ migration is a **feature and an occasion**, not a market by itself. **Do not use these numbers for fundraising.**

## 14.3 The early-action model: converting emergency work into planned work

Fleet of 10,000 devices, 20 devices per visit, so 500 visits in total.
- A full visit costs $1,000.
- The marginal cost in a planned window is 25% of that ($250).
- 33% of emergency visits need a second trip.
- r is the remotely updatable share. **No source measures r, so it is varied.** [E]

| r | Visits needed | Planned-window cost | Emergency cost ($1,000 × 1.33) | Downtime if every emergency visit costs 1 h at $125k | If 5% of visits cost 1 h |
|---|---|---|---|---|---|
| 0.1 | 450 | $112,500 | $598,500 | $56.25M | $2.81M |
| 0.4 | 300 | $75,000 | $399,000 | $37.5M | $1.88M |
| 0.7 | 150 | $37,500 | $199,500 | $18.75M | $0.94M |

**Conclusion [E/I].** Labour is small and **downtime dominates**. The economic reason to act early is that a transition done in planned windows costs tens of thousands of dollars per 10,000 devices. Forced into emergency outages it plausibly costs **millions**. The downtime figures are vendor-sponsored and plant-oriented. Substation-specific numbers do not exist publicly (N34), so this is the most valuable number to measure.

## 14.4 Value for customers who do not care about quantum computing

Every recommended mechanism pays for itself on a non-quantum axis:

| Mechanism | Non-quantum value |
|---|---|
| Continuity First Stage | Secure boot that survives *any* key compromise or algorithm deprecation; CRA-friendly update integrity |
| Side-door closure | Removes today's debug-port and RMA attack paths |
| FDO-PQ vouchers and escrow | Supplier independence; OEM-exit protection; M&A diligence |
| Window staging | Higher patch adoption for *all* vulnerabilities, not just crypto (the 60%-outdated-PLC problem) |
| Fleet evidence | CRA Article 14 reporting, India critical-infrastructure inventories, audit readiness |
| Workstation quorum | Protection against insider and ransomware tampering with settings |

**This is the real go-to-market [I].** Sell firmware governance, update adoption and compliance evidence. Post-quantum readiness arrives as a by-product that justifies the timing.

## 14.5 Business models, ranked by fit

1. **An open first-stage reference plus paid porting and assurance** to OEMs (formal verification, fault testing, certification support).
2. **A compliance-evidence product:** CRA Article 14, India critical-infrastructure inventories and IR 8547 transition reporting.
3. **Window-aligned migration engineering** services to operators, especially Indian power, telecom and oil and gas facing the 2027–2029 dates.
4. **Procurement-clause libraries and test-lab services.** India's roadmap calls for labs, and owners cannot verify OEM claims without them (N32).

**Weak fits:** per-device subscriptions (operators resist recurring per-device cost in OT); a custodian utility (liability without demand); new-ROM licensing (slow and commercially irrelevant if locked flash suffices).

---

# 15. The design debate and where it converged

Eight positions argued their case.

| Position | Most important problem | Preferred architecture | Attack on others | Would change its mind if… |
|---|---|---|---|---|
| **Cryptographic purist** | Side doors and single-assumption failure | Slots for ML-DSA + SLH-DSA-SHAKE + LMS-SHA-256; single-assumption rule; PQ debug and vouchers | Minimalist: "one hash is a monoculture" | SP 800-230 verification on a hash-engine MCU exceeds 100 ms |
| **Embedded minimalist** | RAM and boot time | One hash verifier in the first stage; ML-DSA only in the updatable second stage | Purist: "three verifiers are three bug surfaces" | A structural attack on SHA-256 or SHAKE appears |
| **Industrial pragmatist** | Non-adoption | Window staging, enclaves, replacement plans | Everyone: "nothing helps if updates sit uninstalled" | Pilots show >80% remote adoption without downtime |
| **Distributed-systems architect** | Divergent trust state | Floors, signed state digests, gossip of the highest floor | Pragmatist: "enclaves diverge silently" | — |
| **Hardware architect** | Flash locks are weaker than ROM; no hash engine | Hash engines and OTP key-hash slots required through procurement | Minimalist: "software W8 takes 363 ms" | Fault tests show locks hold |
| **Safety engineer** | Recertification bundling and fail-closed hazards | Crypto confined to boot and update; failures degrade privileges, never safety; last-known-good | Purist: "fail-closed in an SIS is a hazard" | Assessors accept a crypto partition argument |
| **Security auditor** | Unverifiable claims | Independent labs, TVLA requirements, benchmark methodology | Everyone's vendor numbers | — |
| **Entrepreneur** | No budget line for "quantum" | Sell compliance evidence and adoption tooling; PQ as a by-product | Inventors: "the custodian has no buyer" | A paid pilot appears |
| **Naturalist** (added in this edition) | Brittleness: systems built to be optimal rather than to adapt | Two signals before irreversible change; staged commitment that resets on doubt; prepared successors; seal-not-heal enclaves; small frequent renewals | Purist: "a perfect lock without a regulator is an autoimmune disease"; pragmatist: "suppressing small changes buys a megafire" | A controlled pilot shows staged, two-signal authority changes add unacceptable latency, or that regular slot drills cause more outages than they prevent |

**Convergence**
- **Agreement:** a hash-based locked first stage; closed side doors; a symmetric process bus.
- **Unavoidable trade-off:** diversity (purist) versus attack surface (minimalist). **Resolution:** diversity *in slots and assumption classes*, with one formally verified verifier per class, and only the first-stage verifier immutable.
- **Clearly superior point:** the pragmatist's adoption argument. It reorders every priority.
- **Class-dependent:** hash engines for new designs, enclaves for legacy, crypto confinement for C3.
- **Unresolved, no responsible conclusion yet:** whether assessors accept crypto partitioning (E-C1); whether operators accept escrow and custodians; how much physical resistance each part family really has (E-A4, now a certification review; Part 8).
- **What the naturalist added to the convergence:**
  1. **Timing beats strength.** Several positions agreed that *when* and *in how many independent stages* an authority change happens matters more than the strength of any single check (Pattern 2, M3).
  2. **Restrain the defenders.** The purist accepted that strict mechanisms need explicit "regulatory" limits (rate limits, safe misfire), or they turn on the operator (Pattern 4).
  3. **Practise renewal.** The pragmatist and the naturalist converged on regular, small, planned renewal (slot drills, window staging) as the cure for both the adoption problem and the agility-atrophy problem.

  The minimalist objected that every added stage is code. The resolution: the **stages live in the updatable second stage and in the fleet service, never in the locked first stage**, which keeps only the floor rule and slot hashes.

---

# 16. Validation programme: experiments ordered by information value

These merge the invention pass's experiments (E1–E10) with the second pass's experiments (E-A/B/C). They are reordered so that **cheap tests that could kill whole strands run first**. All of them run on owned or authorised equipment only; none touch live critical infrastructure.

| Order | ID | Question | Method | Cost | Supports / disproves | Decision it drives |
|---|---|---|---|---|---|---|
| 1 | **E-A1** | What share of industrial MCU families support a lockable, maker-defined immutable first stage? | Desk survey: ST, NXP, Renesas, Microchip, TI, Infineon, Nordic, Silicon Labs, Espressif, GigaDevice | ~2 weeks | ≥50% supports / <30% disproves | Locked flash vs new ROM |
| 2 | **E-A3** | Which authorisation paths (debug, lifecycle, ownership, provisioning, licence) are classical, per family? | Documentation review plus lab confirmation | ~3 weeks | — | Side-door map; procurement clauses |
| 3 | **E-A2** | What does verification cost for LMS W4/W8, the SP 800-230 sets and ML-DSA-44 on M0+ and M33, with and without hardware SHA? | Owned boards; publish neutral benchmarks | ~4 weeks | ≤100 ms / >300 ms | Algorithm and parameter choice; settles the RP2040 memory conflict |
| 4 | **E-B4** | Can a floor be burned against the owner? | NSIB-style lab demonstration | ~2 weeks | Exploitable / not | Validates the floor rule |
| 5 | **E-B2** | Is the single-assumption rule sound, and do the state-machine invariants hold? | TLA+ and Tamarin models (the invention pass's E2) | ~6 weeks | No path / counterexample | Slot and quorum design |
| 6 | **E-A4 (revised)** | Which part families have independent certification covering physical attacks, and what would one opened device yield? | Certification-scope review; architecture review confirming no fleet secret sits in any device; evaluation by an accredited lab where certification is missing | ~6 weeks | Certified and contained / uncertified or fleet secret found | Part choice per device class (Part 8.2) |
| 7 | **E1** | Does the first stage survive power loss? | 100,000 boots with random power cuts on a Cortex-M33 with wolfBoot-derived LMS | ~4 weeks | No brick, no illegal state / any brick | Journal design |
| 8 | **E6 (revised)** | Catch-up: sequential TUF vs linear pre-rotation vs Merkle future sets | Simulation, N = 1–50 rotations | ~2 weeks | Expect ~1.5–3× linear, ~29× Merkle | Whether pre-rotation is worth doing at all |
| 9 | **E-B3** | Does FDO-PQ interoperate? | Open FDO stack plus PQ signature profile, two OEM simulators | ~8 weeks | Works / sizes break | Ownership standard contribution |
| 10 | **E4** | Does GDOI-PQ rekey disturb IEC 61850 traffic? | 20 emulated IEDs | ~6 weeks | Data-path latency unchanged; <1 s per group | Fabric viability |
| 11 | **E9** | Does a split ClientHello survive industrial firewalls? | Lab harness, common OT firewalls | ~3 weeks | Drop and reset rates | Hybrid-strict deployability |
| 12 | **E10** | Does the ML-DSA iteration-count leak help an attacker on target MCUs? | Timing study | ~4 weeks | Randomisation removes leak | Signing placement |
| 13 | **E-B1** | What is real remote-update adoption? | Read-only measurement at a consenting operator | ~3 months | Pragmatist's 80% threshold | Priority of window staging |
| 14 | **E3** | 10,000 simulated devices offline for 1–10 years with withholding and replay | Simulation | ~4 weeks | Zero acceptance below the floor | Offline design |
| 15 | **E5** | Can an OEM-exit drill complete in under 72 hours with no single party able to act alone? | Tabletop plus prototype with three organisations | ~2 months | — | Escrow contract design |
| 16 | **E8** | Does a crypto partition remove control jitter? | WCET measurement with and without partition | ~6 weeks | — | C3 design |
| 17 | **E-C1** | Will functional-safety assessors accept crypto confinement? | Interviews with two assessment bodies | ~2 months | Accept / reject | Safety-class architecture |
| 18 | **E7** | Is passive CBOM accurate? | Captured lab traffic | ~4 weeks | ≥95% correct | Evidence product |
| 19 | **E-C2** | Does it survive an independent security review? | Third-party audit of the open first stage | Budgeted | — | Public release |

**Highest information value per cost: E-A1.** Two weeks of reading decides whether the entire new-silicon strand lives or dies.

**Highest consequence: E-B2.** If the formal model finds a path by which one assumption class can advance the floor or change authority, the slot and quorum design must change. (The earlier edition named E-A4. This edition separates the threats: the lock defeats the remote, quantum-era forger by design, and physical resistance is a per-part, per-class question that limits harm to one device when walls 3 and 4 of Part 8.3 hold.)

**Research priority scores** (1–5 each; total out of 20):

| Question | Importance | Uncertainty | Information value | Changes architecture | Total |
|---|---|---|---|---|---|
| E-A1 lockable share | 5 | 3 | 5 | 5 | 18 |
| E-A4 physical resistance per part (revised) | 4 | 4 | 3 | 3 | 14 |
| E-B1 adoption | 5 | 5 | 4 | 3 | 17 |
| E-A3 side doors | 5 | 3 | 4 | 4 | 16 |
| E-A2 benchmarks | 4 | 3 | 4 | 4 | 15 |
| E-C1 assessors | 4 | 5 | 3 | 3 | 15 |

## 16.1 Experiments added by the nature, physics and history pass

These test the rules this edition introduced. All run on owned equipment, desk material or consenting operators' anonymised data.

| Order | ID | Question | Method | Cost | Supports / disproves | Decision it drives |
|---|---|---|---|---|---|---|
| N1 | **E-N7 Counter-capacity audit** | Does any counter, time field or signature budget in current designs run out within the asset's life? | Desk review: time_t width, GPS week handling, LMS and SP 800-230 budgets, fuse banks, message counters | ~2 weeks | Margin ≥2× everywhere / a wrap or exhaustion found | The §6.6 rule; procurement clauses |
| N2 | **E-N3 Disjoint-quorum checker** | Can a tool find quorums in which one assumption is shared by every member? | Encode each slot's dependencies (hash function, lattice, code, implementation, organisation) and check the M2 rule automatically | ~4 weeks | Finds real violations / finds none | Design-review tooling; 10.3 |
| N3 | **E-N8 Exposure-years baseline** | What is an operator's exposure-years trajectory today, and what does a given replacement budget buy? | Asset register plus replacement plan through the M5 model | ~2 weeks | — | Programme KPI (11.7) |
| N4 | **E-N4 Ordering on real topology** | Does targeted migration order (M1) beat random order on real OT architectures? | Apply the M1 strategies to an anonymised asset and trust-relationship inventory | ~4 weeks | Targeted threshold far below random / no difference | Migration order (12.4) |
| N5 | **E-N5 Molting-protocol model** | Is provision-alongside → shadow-sign → hide → shed → harden safe under all interleavings, including power loss? | TLA+ model, extending E-B2 | ~4 weeks | No unsafe state / counterexample | The transition protocol (11.1) |
| N6 | **E-N1 Slot-drill pilot** | Does exercising the alternate slot once a year reveal latent faults before an emergency? | Owned boards, then a consenting test fleet: one release verified through the alternate class only, in a planned window | ~2 months | Path works / latent fault found | Whether slot drills become a requirement (I-13) |
| N7 | **E-N6 Two-signal latency** | How much delay would a two-signal rule (valid signature plus an independent context signal) have added to past emergency fixes? | Replay of historical emergency patches as a tabletop | ~6 weeks | Within the operational window / too slow | Anergy and two-signal rules (11.1) |
| N8 | **E-N2 Grid-time measurement** | Are mains-cycle counts and ENF fingerprints stable enough at device scale to serve as plausibility inputs? | Passive measurement at several sites on one synchronous area over months, on owned equipment | ~3 months | Agreement within the fusion window / too noisy | I-24, I-25 |

**Cheapest and most likely to find real defects:** E-N7 and E-N3. Counter wraps and shared assumptions are the kind of flaw that is invisible until it fails all at once (Patterns 18 and 30). **Most novel:** E-N2, the only test of a genuinely new trust input.

---

# 17. The long view: infrastructure meant to last 50–100 years

## 17.1 Three visions, updated after both challenge rounds

**Vision 1: Evolutionary (2026–2032), deployable progressively**
- New devices: a locked continuity first stage with multi-class slots, PQ debug credentials and FDO-PQ vouchers.
- Process buses stay symmetric, keyed through ML-KEM enrolment.
- Legacy devices sit in dated enclaves.
- Cryptographic change rides maintenance windows.
- Compliance evidence is produced in CycloneDX and attestation formats.
- India's critical-infrastructure milestones (2027/2028/2029), the CRA (Dec 2027) and IR 8547 (2030/2035) set the pace.
- **Weakness:** installed classical-ROM devices without locks remain exposed until replaced.

**Vision 2: Transformational (2028–2040)**
- Procurement standards require a hash engine (SHA-2 + SHA-3), ≥3 key-hash slots across ≥2 assumption classes, PQ debug and vouchers, and no field debug. These enter IEC 62443-4-2 and national lab criteria.
- Authority moves to the operator at defined triggers.
- Signed state reports become regulatory evidence.
- OT MCU vendors ship PQ-capable ROMs and certified masked PQ IP.
- **Weakness:** governance and liability for escrow; operators' capacity to hold authority.

**Vision 3: Radical (2035 onward)**
- **Trust renewal as a public-utility service.** Witness networks, time and freshness services, and voucher registries are run like time synchronisation, by several independent parties.
- **Algorithm-diverse subfleets**, so that one cryptanalytic break cannot take an entire grid.
- **Hash-only devices** for assets meant to outlive all current public-key assumptions.
- **Property-named security.** Applications request "authenticated, fresh, owner-authorised" and never name an algorithm.
- **Requires:** a theory of fleet diversity, a property-level protocol layer, and international governance of witness and voucher infrastructure.

## 17.2 Design principles for a device meant to last decades

These consolidate what survived every pass. [I]

1. **Make immutable only what is minimal and conservative:** a hash verifier and commitments. Never an algorithm-specific public-key verifier alone.
2. **Commit to diversity at birth.** At least two assumption classes, held by at least two organisations, with one slot reserved for the eventual owner.
3. **Separate booting from re-authorising.** Booting needs one valid class. Changing authority (floor, slots, owner, lifecycle) needs more.
4. **Never tie authority to a calendar.** Use counters and epochs. Time may tighten privileges but must never stop a safety function, and it must never *grant* authority. Part 6 puts numbers on this: validity epochs should be months, sized to the oscillator's drift bound.
5. **Keep state monotonic and non-restorable.** Anything that a backup can rewind is not security state.
6. **Delete capabilities you cannot protect.** Field debug, remote paths to offline devices and per-frame public-key work.
7. **Keep public-key work rare.** Do it at enrolment and authority changes; run symmetric operations everywhere else.
8. **Every authorisation path is part of the root of trust.** Map it, or assume an attacker will.
9. **Design for the change to be installed.** Staged, dormant and window-aligned, separate from functional change, with signed confirmation.
10. **Plan the device's death on day one.** Decommissioning revokes, destroys and records.
11. **Make the device say what it trusts.** Signed state is the sensor of the control loop.
12. **Prefer contracts and existing standards to new organisations.** New organisations are new single points of failure with unclear liability.

## 17.3 The question at the heart of it

*How does a device know an update is trustworthy when the technology that originally established its trust is no longer trustworthy?*

**Answer:** only through something committed **before** that technology failed and **independent** of it. That is a commitment to a key from a different assumption class, or a person physically present. Everything else is a delivery mechanism. This is why the most consequential engineering decision is made at manufacture, and why every year of shipping single-class devices enlarges the set of devices that can never be rescued. [I]

## 17.4 What nature and the oldest institutions add to the long view

The nature, physics and history pass did not overturn the principles of 17.2. It added eight that none of the earlier passes had, each grounded in a system that has already lasted far longer than any device. [I]

13. **Renew on a schedule, not only when something breaks.** Ise has been rebuilt every 20 years since 690, and fire-adapted forests stay healthy through frequent small burns (7.1; Pattern 29). A trust system that changes only in emergencies changes badly.
14. **Exercise every path you will one day need.** Unused capabilities decay (R10). The DNSSEC root rollover depended on an automated mechanism never tested at scale (7.3). Slot drills and renewal rehearsals are the remedy.
15. **Never let one assumption sit in every quorum.** Diversity that shares a hash function, an implementation or an organisation is one point of failure in disguise (M2; Pattern 30; Knight and Leveson).
16. **Require two independent signals before anything irreversible.** T cells need antigen plus co-stimulation, and kinetic proofreading multiplies accuracy by stages (Patterns 1 and 2; M3). One valid signature is antigen without co-stimulation.
17. **Plan succession while the authority is healthy.** Honeybee colonies replace an ageing queen while she still lives (supersedure). A colony that loses its queen and misses the short window for raising another becomes "hopelessly queenless" and dies (Pattern 13). OEM heartbeat and escrow triggers belong in the first contract, not the last.
18. **Size every counter for the asset's life, with margin.** Time fields, week numbers and signature budgets are telomeres: finite, and fatal when they run out (Pattern 18; Part 6).
19. **Keep the immutable part tiny, conservative and verified.** Germline minimalism, the hex0 seed and formal verification all say the same thing (Pattern 17; 7.5; 8.8).
20. **Re-encode evidence before its format dies.** The Rosetta Stone survived because it said one thing three ways. The Domesday discs failed in 16 years because one machine could read them (7.4). Evidence records must be renewed (RFC 4998; I-29).

**Updates to the three visions:**
- **Vision 1** gains slot drills, the disjoint-quorum check and class-ordered migration. All three are cheap and can start now.
- **Vision 2** gains **announced cryptographic end-of-support dates** on the medical-device model (7.7), and procurement clauses requiring counter-capacity statements.
- **Vision 3** gains **renewal as a civic ritual**: sector-wide renewal of trust roots on a fixed cadence (I-30), governed as an Ostrom commons (7.2), with evidence stamped into widely witnessed records.

**The question of 17.3, answered by nature.** Living systems face the same question every generation: how to trust a new signal when old defences may have been subverted. Their answers match the one above. They commit diversity before it is needed (gene duplication, many MHC alleles), require independent confirmation before irreversible action (co-stimulation, quorum thresholds, the spindle checkpoint), and keep the founding information minimal and protected (the germline). Nature adds one thing engineering usually omits: **it exercises its defences continuously**, so they are never untried when the real threat comes.

---

# 18. The innovator's notebook: new ideas from the synthesis

Reading all passes together surfaced ideas that none of them stated on its own. All are **[H]**: proposed, unvalidated. Each comes with its prior-art status as far as is known, and the test that would kill it.

**I-1. The Authorisation Surface Map as a first-class artefact.**
- **Idea:** a machine-readable description, per part and per product, of every path that can change code, keys, owner, debug state, lifecycle or configuration. For each path it records the algorithm, key holder, binding (per-device or fleet) and whether it is classical. An "exposure score" is the fraction of paths that are classical or fleet-bound.
- **Why it is new:** CBOMs list algorithms *in use*. They do not map *authority paths*, which is where the side doors live.
- **Prior art:** CBOM, threat modelling. No equivalent artefact was found, but a full search has not been done.
- **Kill test:** if E-A3 shows that vendors' documentation is too incomplete to populate it without lab work for every part.

**I-2. Graded authority: "boot with one, change with two, re-own with two plus presence".**
- **Idea:** a single rule family covering boot, floor advance, slot replacement and lifecycle transitions, with increasing quorum strength. It generalises the floor rule.
- **Benefits:** it closes floor burn (N22) and stops a single-class compromise from re-owning a device. Physical presence for re-ownership defeats remote attackers entirely.
- **Kill test:** E-B2 counterexamples, or operator rejection of presence requirements.

**I-3. Dormant transition bundles with a "two-key activation".**
- **Idea:** the crypto-transition bundle is staged dormant. Activation needs a site-local token (proving a planned window) *and* an authority signature.
- **Benefits:** an attacker who obtains a valid bundle cannot trigger it outside a window, and operators get deterministic timing.
- **Kill test:** if the site token becomes a new side door (it must itself follow I-2).

**I-4. An assumption-graph policy compiler.**
- **Idea:** policy authors declare quorums over keys. The compiler computes, from a maintained table mapping each key to its assumptions, whether any single assumption failure (or any *k* failures) satisfies a quorum. It rejects unsafe policies before they are signed.
- **Why it matters:** it turns "family independence" from a slogan into a check.
- **Kill test:** if assumption tables cannot be agreed (SHA-2 vs SHA-3 independence is a judgement), the tool still helps by making the judgement explicit.

**I-5. Spares that activate on installation, not on the shelf.**
- **Idea:** spares ship with only the first stage and slot hashes. The application image and ownership arrive at installation, via the voucher plus the current bundle.
- **Benefit:** the stale-root problem (P24, N23, N53) disappears, because the spare never held stale authority.
- **Kill test:** sites with no connectivity at installation need a technician-carried bundle (acceptable) or the idea fails.

**I-6. Decommissioning receipts.**
- **Idea:** decommissioning produces a signed receipt (device UUID, floor, keys destroyed, trust-list removals) that must be logged before a device can be resold or refurbished.
- **Problems addressed:** N36, N37, N53.
- **Prior art:** key-destruction proofs exist in the HSM world.
- **Kill test:** devices that cannot sign; then a gateway witness signs on their behalf, which is weaker.

**I-7. Crypto-only update lanes.**
- **Idea:** firmware architecture separates the cryptographic component (verifier, key slots, protocol suites) into an independently updatable, independently certified module with a stable interface.
- **Benefit:** crypto changes do not re-trigger the functional safety case (N48, P28).
- **Prior art:** partitioning, TrustZone-M and separate cores.
- **Kill test:** E-C1, if assessors refuse to accept the separation argument.

**I-8. Window-aware attack hardening.**
- **Idea:** because staging publicises when changes happen, randomise the activation offset within the window and require signed state reports to be counter-signed by a second observer. Activation timing then cannot be predicted, and silent failed activations cannot be hidden.
- **Kill test:** if randomisation conflicts with plant procedures.

**I-9. Enclave exit clocks.**
- **Idea:** every enclave configuration carries an expiry epoch for its legacy exception, signed by the asset owner. The gateway raises a visible alarm as the epoch approaches, and the exception must be re-authorised by quorum.
- **Benefit:** "temporary" becomes measurable, which addresses the tendency of enclaves to become permanent.
- **Kill test:** alarm fatigue.

**I-10. A shared, neutral benchmark and conformance lab for OT PQ.**
- **Idea:** neutral, reproducible benchmarks (problem N27) and conformance tests for first stages, vouchers and debug credentials, co-located with the labs India's roadmap calls for.
- **Benefit:** owners can verify OEM claims (N32).
- **Commercial form:** test-lab services.
- **Kill test:** if national labs absorb the role entirely (then partner, don't compete).

**I-11. Merkle future-key commitments, split across custodians.**
- **Idea:** the 29× catch-up saving needs K future key sets kept secret for decades (N40). Split the custody of each future set across separate organisations in different assumption classes, so that no single holder's leak lets an attacker skip ahead.
- **Status:** research. It adds the complexity the second pass warned about, so it is justified only for decade-offline, high-value assets.

**I-12. "Explain what changed" as a signed, human-readable diff.**
- **Idea:** every state report carries a structured, human-readable delta: floor 3 → 4, slot 2 retired, algorithm set {…}. Operators can then distinguish a valid transition from a compromised one, which addresses the operational-uncertainty problem.
- **Prior art:** release notes. What is new is binding the diff into the signed state.
- **Kill test:** low, since this is cheap.

## 18.1 New ideas from the nature, physics and history pass

These came from reading the natural, physical and historical precedents (Parts 5–8) against the problem universe. All are **[H]**. Each names the precedent it comes from, the closest prior art found, and the test that would kill it.

**I-13. Slot drills: GREASE for trust anchors.**
- **Idea:** once a year, in a controlled window, a release is verified through the *alternate* assumption class alone, and the result is reported. Every slot path is then exercised before an emergency depends on it. Drills can rotate across classes.
- **Precedent:** TLS GREASE (RFC 8701) exists because unexercised extension points ossified in deployed middleboxes, the ossification effect of Pattern 21. The DNSSEC root rollover showed the same risk for trust anchors (7.3), and fire ecology shows it for whole systems (Pattern 29).
- **Prior art:** disaster-recovery drills; key-ceremony rehearsals. No firmware-slot equivalent was found.
- **Kill test:** if drills cause more outages than the latent slot failures they reveal (measure in pilots).

**I-14. Anergic keys.**
- **Idea:** a key that repeatedly presents validly signed authority changes *without* the required second class is demoted to boot-only until a quorum restores it, and the event is reported.
- **Precedent:** signal-1-without-signal-2 inactivation of lymphocytes (Pattern 1).
- **Kill test:** if an attacker can use demotion to lock out the legitimate OEM faster than a quorum can restore it (E-B2).

**I-15. The PAM rule for revocations.**
- **Idea:** a revocation record that would match the device's current authority set is structurally invalid unless it carries the escrow class plus presence evidence.
- **Precedent:** CRISPR's self/non-self discrimination (Pattern 5).
- **Kill test:** if legitimate emergency revocation of a live, compromised key becomes too slow. Mitigation: a pre-provisioned escrow path with an on-site token.

**I-16. The molting protocol.**
- **Idea:** every class transition runs five explicit phases: provision alongside, shadow-sign, hide (reduce exposure), shed under the disjoint-quorum rule, harden.
- **Precedent:** arthropod molting (Pattern 15).
- **Kill test:** TLA+ (E-B2) finds a phase ordering in which a partially transitioned device accepts an attacker's authority, or field pilots show the hide phase is operationally unacceptable.

**I-17. OEM heartbeat with a witnessed escrow trigger.**
- **Idea:** the OEM signs quarterly PQ liveness statements. N missed heartbeats, or failure to fix a critical CVE within M days, triggers voucher escrow release by contract, attested by witnesses.
- **Precedent:** queen mandibular pheromone and emergency queen rearing (Pattern 13).
- **Prior art:** source-code escrow agreements; dead-man switches.
- **Kill test:** if courts or procurement will not enforce trigger-based release (legal review; E5).

**I-18. Successor stop-signals with a deterministic tie-break.**
- **Idea:** when two successor authorities compete, quorum members attach signed objections. No irreversible step runs while an objection stands, and a deterministic rule settles the case after escalation.
- **Precedent:** honeybee cross-inhibition (Pattern 12).
- **Kill test:** if a malicious objector can stall a legitimate succession indefinitely (bound the hold, then escalate).

**I-19. The disjoint-quorum compiler (sharpens I-4).**
- **Idea:** the policy tool accepts only quorums whose members' assumption sets are pairwise disjoint. It reports the probability-weighted attacker and honest success for declared horizon assumptions, using the exact enumeration in `models/quorum.py`.
- **Precedent:** egg-signature decorrelation (Pattern 7); model M2.
- **Kill test:** low; the main risk is that the dependency table is disputed. The tool makes the dispute explicit.

**I-20. Acquaintance migration.**
- **Idea:** when no inventory exists, migrate what a randomly chosen device trusts or talks to, rather than the device itself. This reaches hubs without a map.
- **Precedent:** acquaintance immunisation (Cohen, Havlin & ben-Avraham, 2003). Model M1: about 44% of nodes migrated versus 73% for random to bring the blast radius below 5%.
- **Kill test:** E-N4 on a real anonymised plant trust graph shows no advantage over random.

**I-21. Exposure-years as the regulatory and programme metric.**
- **Idea:** report integrated exposure (unmigrated devices × criticality × time), not the percentage migrated.
- **Precedent:** integral feedback in chemotaxis (Pattern 34); model M5.
- **Kill test:** regulators and boards find the metric uninterpretable (user testing).

**I-22. Thymic policy testing.**
- **Idea:** before any trust policy ships, replay every planned legitimate future operation (the next floor advances, an RMA, an ownership transfer, a spare activation) against it, and reject the policy if any is refused.
- **Precedent:** central tolerance (Pattern 4).
- **Kill test:** if the planned-operation corpus cannot be enumerated in practice.

**I-23. The zeitgeber stack.**
- **Idea:** device time is a free-running oscillator plus a ranked set of independent entrainment sources. Each is labelled with what it can prove (not-before, not-after or rate) and fused with plausibility windows, never trusting one source alone.
- **Precedent:** circadian entrainment by multiple zeitgebers (Part 6).
- **Kill test:** a lab study shows fusion rules that spoofing of any single source can push outside its window.

**I-24. Grid-cycle entrainment for grid-connected devices.**
- **Idea:** relays, meters and RTUs on a synchronous grid count mains cycles as a long-run clock whose accumulated error is held down by the grid operator's time-deviation management, where practised. It is checked against the RTC drift bound and other zeitgebers.
- **Precedent:** mains-synchronous clocks; the Syntonistor, which reached typically sub-millisecond synchronisation from the mains magnetic field on 58 µW (SenSys 2009); grid-voltage cycle-length fingerprints used for time synchronisation at about 0.1 ms over about 10 km (RTSS 2016, TOSN 2018). Relative synchronisation from the grid is therefore **prior art**. The new part is using it as one labelled input to an authority-freshness decision.
- **Warning:** the 2018 Continental Europe deviation (Part 6) showed this clock is *governed*, not physical, and can drift by minutes. Europe still corrects time deviation by rule (UCTE Policy 1: ±10 mHz whole-day corrections beyond ±20 s). North America retired its reliability standard for time error correction in 2017, so long-run accuracy there is not assured by rule.
- **Kill test:** the plausibility-window fusion cannot tolerate realistic deviations and islanding.

**I-25. Electrical-network-frequency "not-before" stamps.**
- **Idea:** grid frequency fluctuates in a way that is hard to predict but is common across a synchronous area, which is why forensic analysts use it to date recordings. An authority could embed a recent ENF fingerprint in a signed message. A grid-connected device that records ENF locally could then check that the message was created *after* a recent window, which defeats replay of old, validly signed authority.
- **Precedent:** ENF forensics (Part 6).
- **Limits:** this provides recency, not authentication, which the signature still provides. It does not detect withheld updates.
- **Prior art found in this pass:** forensic dating of recordings (Grigoras, 2005); ENF-based time synchronisation robust to packet-delay attacks (Viswanathan, Tan & Yau, RTSS 2016; TOSN 2018); ENF as a ledger consensus input ("Proof-of-ENF", EconLedger, 2021). **No application to device authorisation or authority freshness was found**, so that narrower claim remains open.
- **Kill test:** ENF entropy per minute is too low, or local measurements are too noisy, to match fingerprints reliably at device scale. A measurement study is needed (E-N2).

**I-26. Remanence timers for power-off intervals.**
- **Idea:** use the measurable decay of SRAM contents during power loss to bound how long a device was unpowered, as TARDIS did for clockless RFID-class devices (Part 6). This rate-limits attacks that rely on repeated power cycling, and flags implausibly long "instant" reboots.
- **Kill test:** temperature dependence makes the bound useless outdoors.

**I-27. Spindle-checkpoint gating for irreversible fleet steps.**
- **Idea:** the walk orchestrator executes a classical sunset or family retirement only when every dependent participant (devices in scope, witnesses, islands) reports ready. A single unready participant holds the step, and a bounded hold escalates to humans.
- **Precedent:** Pattern 19.
- **Kill test:** fleets are too large for complete readiness reporting, in which case readiness is gated per cohort.

**I-28. Camouflage detection.**
- **Idea:** fleet evidence flags devices or accounts that hold, or have used, keys or group memberships beyond their role.
- **Precedent:** social-parasite chemical camouflage (Pattern 9).
- **Kill test:** too many false positives in real plants.

**I-29. Evidence-record renewal for vouchers, receipts and logs.**
- **Idea:** ownership vouchers, decommissioning receipts and transition logs are archived under RFC 4998-style evidence records. Their hash trees are re-timestamped under a stronger algorithm *before* the current one weakens, so a voucher signed in 2027 is still provable in 2060.
- **Prior art:** RFC 4998/6283 Evidence Record Syntax (Part 7). Rarely used in OT.
- **Kill test:** low; this is standards reuse.

**I-30. The Ise cadence for people.**
- **Idea:** schedule a full cryptographic renewal rehearsal (not only a slot drill) at an interval short enough that every engineer takes part at least twice in a career. That keeps transition knowledge alive in people, not only in documents.
- **Precedent:** the 20-year rebuilding of Ise Jingu (Part 7).
- **Kill test:** cost; measure against the cost of a botched real transition.

**I-31. The trust cartridge.**
- **Idea:** for new device designs, put the post-quantum trust functions (verifier, key slots, KEM decapsulation) in a **replaceable secure module**, so that a future algorithm change is a module swap rather than a device replacement. The host's own first stage then verifies under the module's authority.
- **Precedent:** transit readers' replaceable Secure Access Modules, and SIM/eSIM (Part 8).
- **Limits:** the module interface becomes the new waist.
- **Kill test:** a host-to-module bus that cannot be protected against a local attacker, or module cost exceeding the savings.

**I-32. Physics as a second signal inside enclaves.**
- **Idea:** inside enclaves of un-migratable devices, operational commands and reported states are checked against design-derived physical invariants before being acted on.
- **Precedent:** Pattern 36; SWaT research.
- **Limits:** this protects operations, not firmware or authority.
- **Kill test:** invariant false-positive rates are too high in a pilot plant.

**I-33. Persister cohorts in emergency rollouts.**
- **Idea:** during any emergency transition, a defined fraction of each class stays on last-known-good until the new state is proven, and is then moved.
- **Precedent:** bacterial persisters (Pattern 31); the 2024 CrowdStrike outage (Part 7).
- **Kill test:** the persister fraction itself becomes the attacker's preferred target during the window. Mitigate by tightening enclave controls for persisters.

**I-34. Senescence reporting.**
- **Idea:** a device whose authority view is stale enters a defined senescent state (function retained, authority changes refused) and announces it in every report. Stale devices then become a visible, countable population to clear.
- **Precedent:** Pattern 14.
- **Kill test:** low; this is mostly naming plus reporting.

---

# 19. Corrections ledger: what we got wrong and fixed

This ledger is part of the result. Each error was found by recomputing, not by rereading.

| # | Earlier claim | Correction | Found by | Consequence |
|---|---|---|---|---|
| 1 | US market low end $0.13B | Components sum to **$113.5M ($0.11B)**; global $0.38–1.88B | Verification lab | Market thesis demoted |
| 2 | Masking overhead ~3.5× | Only **4.21×** reproduces (2,978,441 / 707,827 for ML-KEM decapsulation); 3.5× has no source | Lab | Use measured values per operation |
| 3 | PQ IKEv2 fragments the first exchange | **IKE_SA_INIT cannot be fragmented.** PQ key exchange goes in IKE_INTERMEDIATE (RFC 9242) plus RFC 9370 | Lab | Gateway firmware must support three RFCs |
| 4 | TLS 1.3 downgrade protection is absolute | **Only as strong as the handshake's own primitives** against a real-time quantum attacker | Lab | Hybrid-strict pinning |
| 5 | Naive surface-code count is a forecast | 1,200 × (2d²−1) overshoots Google's <500k; **do not compute physical qubits naively** | Lab | Cite published estimates only |
| 6 | An FN-DSA verify figure of ~6.5 M cycles | Implausible; **dropped** | Lab | — |
| 7 | Root succession is unsolved | **Solved in outline** (TUF/Uptane, RFC 5011, UEFI, OpenTitan, DICE) | Pass 2 | Focus moved to narrow gaps |
| 8 | The Trust Plane is complete | **Missing** provisioning, time, revocation/decommission and governance | Pass 2 | Superseded by the stack in Part 11 |
| 9 | Campos LMS "w=16" is wrong notation | **Winternitz value 16 = LM-OTS W4.** The cycles (2,658,884) are valid | Pass 4 | — |
| 10 | Boot ≈42 ms with a **1,452 B** LMS signature | 42 ms is **W4 (2,508 B)**. W8 is **≈363 ms** in software (23.25 M cycles, measured at h=5), or ≈12 ms with hardware SHA | Pass 4 | Parameter rule: W4 without a hash engine, W8 with one |
| 11 | Pre-rotation catch-up ≈10× (30.1 KB vs 298 KB) | The device still needs each intermediate key set. Linear pre-rotation saves **1.5×**, a pure hash chain **3.0×**; **29.4×** only with Merkle-committed future sets (10,152 B vs 298,140 B) | Pass 4 | Pre-rotation demoted to research |
| 12 | "LMS + escrow" = two families | If both are SHA-256 hash-based, they **share one assumption**. Needs disjoint assumption sets | Pass 4 | Single-assumption-safe rule |
| 13 | The ACK can sit behind existing classical ROMs | A **classical ROM-verified, replaceable** first stage re-creates HNDL-to-authority. Safe only if **locked**, and then the lock provides the security | Pass 4 + synthesis | New ROM unnecessary on lockable parts |
| 14 | ACK needs new ROMs from ~2028 | Locked-flash first stages ship today (Nordic NSIB, ST OEMiRoT) | Pass 4 | Lead architecture changed |
| 15 | MEC175xB shows PQ ROMs reaching OT | It is a **notebook, desktop and data-centre embedded controller** | Pass 4 | Not OT evidence |
| 16 | The CRA excludes legacy products | **Article 14 reporting covers products already on the market**; the duty to fix does not | Pass 4 | Evidence demand exists for legacy |
| 17 | Stateful LMS custody is a business | **SP 800-230 draft** (limited-use SLH-DSA) erodes it, as does NIST's planned SP 800-208 revision to allow key export | Passes 3–4 | Kept only for CNSA-bound systems |
| 18 | The root verifier is "the true bottleneck" | **Update adoption and side doors** are | Pass 4 | Priorities reordered |
| 19 | Top-20 ranking | Built without weight-sensitivity analysis; **rebuilt** and tested under two weightings | Pass 4 | Part 20.2 |
| 20 | ML-DSA-44 signing stack = 50.6 KB | The RP2040 study snippet says 8.4–8.9 KB memory. **Unresolved** | Pass 4 | E-A2 must measure |
| 21 | The minimum robust slot set {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256} is safe under any 2 of 3 | **A single Keccak failure hands the attacker a quorum** (ML-DSA and SLH-DSA-SHAKE fall together). Only quorums with disjoint assumption sets may count, which cuts the attacker's chance about 19× | This edition, model M2 | The disjoint-quorum rule (10.3) |
| 22 | Three slots give three independent classes | Every standard PQ signature depends on SHA-2 or SHA-3/SHAKE: **only two independent waists exist**. The third slot buys availability, not independence | M2 plus toolkit review | Slot design rationale restated |
| 23 | Flash-lock fault resistance is "the kill test for the lead architecture" (E-A4) | **Two adversaries, two answers.** The lock defeats the remote, fleet-scale forger by design. Physical resistance varies by part, and the harm of one opened device is bounded by holding no secrets in the first stage and only per-device keys | This edition, hardware review | E-A4 becomes a certification review; Part 8; E-B2 becomes the highest-consequence test |
| 24 | Draft: N proofreading stages cut error to fᴺ | Hopfield's scheme: **one stage roughly squares the error**. The general fᴺ form is a simplification. M3 models independent confirmation channels instead | Source check by a research stream | Pattern 2 restated |
| 25 | Draft: a loose paraphrase of the BioTRIZ comparison | Restated from the paper: **about 12% similarity**; technology resolves problems mainly through energy, biology through information and structure | Source check | Part 5 introduction |
| 26 | Draft: SIKE fell "in about an hour" | About an hour in the **first** version of the attack paper; **about ten minutes** in the revised version; the US$50k IKEp217 challenge in about six minutes | Source check | 2.6 |
| 27 | Draft: a 2,000-year-old seed germinated at Masada | The seed's own shell fragments dated to **about 1,700 years**; control seeds from the site to about 2,000 | Source check | Pattern 25 |
| 28 | Draft: "trees don't heal, they seal" quoted as if from the CODIT bulletin | A **popular paraphrase**, not a quotation from the bulletin | Source check | Pattern 26 |
| 29 | Draft: cardiac pacemaker rates from memory | Aligned to OpenStax (80–100, 40–60, 30–40, 15–20 per minute) and flagged that texts differ | Source check | Pattern 28 |
| 30 | Draft: overstated Knight and Leveson's shared-failure result | **In one case eight versions failed on the same input**; independence was rejected at 99% confidence | Source check | Pattern 30 |
| 31 | Draft: overstated what Yi et al. showed about integral feedback | Yi et al. showed integral feedback is **necessary** for robust perfect adaptation; nothing stronger is claimed | Source check | Pattern 34 |
| 32 | Draft: grid-cycle and ENF time cues for devices treated as new (I-24, I-25) | **ENF time synchronisation is prior art** (RTSS 2016, TOSN 2018; Syntonistor 2009; Proof-of-ENF ledgers 2021). Only its use for authority freshness was not found | This edition's time stream | I-24 and I-25 narrowed |
| 33 | Research note: OpenSSH made the ML-KEM hybrid the default in 9.9 | 9.9 (Sep 2024) made it **available by default**; 10.0 (Apr 2025) made it **the default** key agreement | Release notes | 8.8 |
| 34 | Draft: a Kansas City Fed study showed US card fraud moving to card-not-present after EMV | The strong shift was seen in **other countries**. The Fed's 2025 US briefing found **no sudden surge**, partly because magnetic-stripe fraud stayed feasible | Source check while building the register | 7.6 and N69 restated; the lesson is stronger: close the old channel completely, or attackers stay on it |
| 35 | Research note: Project Silica's Nature paper dated 2025 | Published in Nature on **18 February 2026** | Source check while building the register | 8.7 |

**Meta-lesson for this edition [I].** Rows 21–23 are design errors found by **modelling**, not by checking numbers: a rule that looked safe failed once every combination was enumerated, and a threat model that looked complete mixed two adversaries. Rows 24–35 are precision errors found by **going back to the source** for facts that "everyone knows". Analogies from nature are especially prone to this: the popular version of a biological fact is often more dramatic than the paper.

**Meta-lesson [I].** The errors clustered in places where **two numbers from different contexts were paired**: a size from one parameter set with cycles from another, or a sum quoted rather than computed. The defence is mechanical: recompute everything, and keep a parameter set attached to every number.

---

# 20. Open questions, rankings and the roadmap

## 20.1 Questions that could still change the architecture

| Question | Current belief | Why it may be wrong | Experiment | Decision it drives |
|---|---|---|---|---|
| What share of industrial MCUs can lock a first stage? | Many (Nordic, ST) | Two vendors are not an industry | E-A1 | Locked flash vs new ROM |
| How much physical resistance does each part family have? | The lock defeats remote forgers regardless; physical resistance varies by part | Older families have public physical breaks; newer certified parts have none public, which is not proof | E-A4 (certification review) | Which parts suit which device classes; whether C4–C5 need certified parts or ROM checks |
| What is real remote-update adoption? | Low (60% outdated PLCs; 15% patch in windows) | Vendor- and survey-based; no direct measurement | E-B1 | Priority of window staging |
| What do the final SP 800-230 parameters cost on MCUs? | Comparable to LMS with a hash engine | Draft; signature sizes conflict across secondary sources | E-A2, after the final standard | Stateful vs stateless roots |
| Does CNSA 2.0 accept SLH-DSA for firmware? | No; LMS/XMSS are named | Secondary sources conflict on ML-DSA for firmware | Primary NSA documents | Defence-adjacent OT |
| Will safety assessors accept crypto confinement? | Unknown | No evidence either way | E-C1 | C3 architecture |
| What is the OPC UA PQ roadmap? | No PQ policy yet | Practitioner sources only | Contact the OPC Foundation | Protocol plans |
| What crypto do contract manufacturers use to inject keys? | Classical wrapping | No data | Interviews, audits | Provisioning design |
| How mature is MCU-class PQ IP against side channels? | Immature (Adams Bridge) | One project examined | TVLA on shipped parts | Silicon choice |
| What does a substation outage cost? | Unknown | No public benchmark | Utility interviews | The business case |
| Is the ML-DSA iteration leak exploitable? | Not shown | The history of BLISS attacks counsels caution | E10 | Signing placement |
| How realistic are falling quantum estimates in hardware? | Trend down, demonstrations far behind | ZK-only disclosure; bit-flip assumptions | Track independent reproductions | Urgency |
| Are SHA-2 and SHA-3 independent enough to count as two waists? | Yes, with a discount (10.3) | Both are symmetric designs studied by one community | Cryptographer review | Whether a non-hash third class is ever worth seeking |
| Can a genuinely third independent signature class exist? | Probably not soon: most signature designs also use SHA-3/SHAKE internally [I; not checked scheme by scheme] | NIST's additional-signature round may include a scheme whose security does not reduce to either hash | Review the round's candidates' hash dependencies | Slot design after 2030 |
| Do OT safety protocols already separate safety from security? | Partly: safety fieldbuses built on the "black channel" principle (IEC 61784-3) treat the channel as untrusted [I] | IEC 61850 trip paths and many vendor protocols may not | Protocol review against the EN 50159 model (7.7) | Whether crypto migration reopens safety cases (R5) |
| Will operators accept slot drills in their windows? | Yes, if bundled with planned work | Each window is already over-full (N14) | E-N1 | Whether slot drills become a requirement |
| Does targeted migration order help on real topologies? | Yes: M1 gives 6–10% targeted vs 73% random | Synthetic topology | E-N4 | Migration programme design |
| Are grid-derived time cues useful plausibility inputs? | Plausible for relative timing; governed for absolute | Islanding, noise, 2018-style disputes | E-N2 | I-24, I-25 |
| Will OT vendors announce cryptographic end-of-support dates? | Not without procurement pressure | No sector precedent outside medical devices (IMDRF N70) | Procurement pilots | Dated exits (11.6) |
| Do counters in shipping designs wrap within asset life? | Some will (Y2038, GPS week, LMS budgets) | Unknown until audited | E-N7 | Procurement clauses |

## 20.2 Revised ranking of what to build

The criteria were security gain, deployability on existing silicon, burden removed, and evidence plus demand pull. They were tested under a **security-heavy** weighting (40/20/15/15/10) and a **deployability-heavy** weighting (20/35/20/15/10).

| Rank | Invention | Earlier rank(s) | Robust to weights? |
|---|---|---|---|
| 1 | Locked continuity first stage (multi-class slots, floor rule) | 1 and 3 (ACK, hash-only ROM) | Yes |
| 2 | Side-door closure (PQ debug, field-debug disable, lifecycle audit, Authorisation Surface Map) | New | Yes |
| 3 | Symmetric process-bus fabric with per-device diversification | 2 | Yes |
| 4 | FDO-PQ vouchers with contractual escrow | Replaces custodian and threshold (5, 6) | Yes |
| 5 | Window-aligned dormant staging with signed state reports | New | Yes |
| 6 | Enclave containment with dated exit | 20 | 7th under security-heavy |
| 7 | Fleet crypto-state evidence (CBOM + attestation) | 10, 15 | No |
| 8 | Workstation signing quorum | 13 | No |
| 9 | Hash-engine procurement requirement | 11 | 6th under security-heavy |
| 10 | Merkle-committed future keys | 9 | No |
| — | Neutral custodian, threshold ML-DSA, time-validity product, insurance pricing, new-ROM licensing | 4–6 previously | Research only |

**What this edition adds to the ranking.** The nature, physics and history pass did not produce a new number-one invention. It produced **rules and practices that make the top five safer and cheaper to run**. They attach to existing ranks rather than competing with them. [I]

| Addition | Attaches to | Cost | Evidence | Verdict |
|---|---|---|---|---|
| **Disjoint-quorum rule** (M2) | #1 first stage; #8 workstation quorum | Near zero: a policy rule and a checker | Modelled: about 19× lower attacker success | **Adopt now** |
| **Class-ordered and acquaintance migration** (M1, 12.4) | The whole programme; #6 enclaves | Planning effort only | Modelled: migrating 6–10% of nodes (targeted) vs 73% (random) brings the worst-case blast radius below 5% | **Adopt now; validate with E-N4** |
| **Slot drills and renewal rehearsals** (I-13, I-30) | #1 first stage; #5 window staging | One window slot a year | Precedent: DNSSEC rollover, GREASE, Ise | **Adopt; pilot with E-N1** |
| **Molting transition protocol** (provision alongside, shadow-sign, hide, shed, harden) | #1 and #4 | Engineering | Pattern 15; to be model-checked (E-N5) | **Adopt as the default transition shape** |
| **OEM heartbeat and escrow trigger** (Pattern 13) | #4 FDO-PQ vouchers with escrow | Contract terms plus a signed heartbeat | Precedent: honeybee succession; medical end-of-support | **Adopt in contracts** |
| **Exposure-years KPI** (M5) | #7 fleet evidence | Trivial | Modelled | **Adopt** |
| **Counter-capacity statements** (6.6) | #9 procurement requirement | Desk work | Y2038, GPS rollover, LMS budgets | **Adopt; run E-N7** |
| **Evidence-record renewal** (I-29) | #7 fleet evidence | Low | RFC 4998 | **Adopt** |
| **Safety/crypto separation** (EN 50159 model, 7.7) | #3 fabric; C3 design | Architecture | Railway precedent | **Adopt for new designs** |
| **Trust cartridge** (I-31) | New designs | Hardware | SIM, eSIM, SAM precedents | **Research; strong for C2–C3** |
| **ENF not-before stamps, grid-cycle entrainment** (I-24, I-25) | Time stack | Measurement study | Prior art for synchronisation only | **Research (E-N2)** |

## 20.3 Roadmaps with decision gates

**Roadmap A: practical entry (0–9 months)**
- **0–3 months:**
  - Run E-A1, E-A3 and E-A2, plus the two cheapest new checks: E-N7 (counter capacity) and E-N3 (disjoint-quorum checker).
  - Build the side-door audit kit and the Authorisation Surface Map format.
  - Interview 5 OEMs and 5 operators, including Indian power, telecom and oil-and-gas critical infrastructure.
  - **Gate:** ≥50% of MCU families lockable → continue. <30% → pivot to silicon procurement asks and hash-only OTP designs.
- **3–9 months:**
  - Prototype the first stage on two families (an STM32U5/H5-class part and an nRF5340, or an nRF54L where documented physical countermeasures matter), using LMS W4 with three slots, the floor rule and the disjoint-quorum rule.
  - Build the TLA+ model and run E-B2, E-B4, E1 and the E-A4 certification review. Extend the model to the molting protocol (E-N5), and run the first slot drill on the prototype (E-N1).
  - **Gate:** verification takes ≤100 ms and the formal model finds no single-class path → continue. A remote or software path that rewrites the locked stage → retreat to the ROM/OTP strategy. Weak physical resistance on a family → restrict that family to lower-consequence classes.

**Roadmap B: strategic expansion (9–24 months)**
- An open release of the first stage with formal verification and a second independent implementation.
- An FDO-PQ profile contributed to the FIDO Alliance.
- A window-staging pilot with signed state reports.
- The compliance-evidence product (CRA Article 14, India critical-infrastructure inventories).
- A pilot with an Indian critical-infrastructure operator.
- Exposure-years baseline (E-N8) and ordering on the pilot's real topology (E-N4); a grid-time measurement campaign (E-N2) at a consenting utility.
- **Gate:** one paying pilot. If incumbents ship the evidence product first, drop it and partner.

**Roadmap C: ecosystem transformation (2–10 years)**
- Procurement standard text: hash engine, ≥3 slots over ≥2 classes, PQ debug and vouchers, no field debug.
- Submissions to IEC 62443-4-2, IEC TC57 WG15 (GDOI-PQ) and national lab criteria.
- A maintainer foundation for the open first stage, so that it does not become the next orphan.
- Five or more MCU families supported. SP 800-230 sets adopted when final.
- Announced cryptographic end-of-support dates and counter-capacity statements as standard procurement clauses.
- A governed trust commons (7.2) for witnesses, vouchers and the open first stage, with a fixed renewal cadence (I-30).
- **Gate:** two OEM adopters shipping it in products.

---

# 21. Appendices

## 21.1 Verified number card

All figures were recomputed in Python for this document.

| Quantity | Value |
|---|---|
| ML-KEM-512/768/1024 encapsulation key | 800 / 1,184 / 1,568 B |
| ML-KEM-512/768/1024 ciphertext | 768 / 1,088 / 1,568 B |
| ML-DSA-87 public key + signature | 2,592 + 4,627 = 7,219 B |
| LMS n=24, h=10, W8 / W4 | 900 / 1,500 B (p = 26 / 51) |
| LMS n=32, h=10, W8 / W4 | 1,452 / 2,508 B (p = 34 / 67) |
| LMS H10 capacity | 1,024 signatures (≈2.8 years of nightly signing) |
| X25519MLKEM768 key share, client / server | 1,216 / 1,120 B |
| LoRaWAN SF10–12 frames: ML-KEM-768 key / ML-DSA-65 signature | 24 / 65 |
| Sampled Values frame period at 4,000 / 4,800 frames/s | 250 / 208 µs |
| LMS verify at 64 MHz: W4 software / W8 software / W8 with hardware SHA (assumed 100 cycles per compression) | 41.5 / 363 / ≈12 ms |
| TUF-style ML-DSA-65 root (n = 5, t = 3) | 29,814 B; ECDSA equivalent ≈0.9 KB |
| Catch-up over 10 rotations: TUF / pre-rotation / hash chain / Merkle with K = 64 | 298,140 / 198,870 / 99,600 / 10,152 B |
| Global market range (from inherited US inputs) | $0.38–1.88B; 10% share = $38–188M |
| Toy checks | DH (p = 23, g = 5) shared secret 2; Shor N = 15 → 3 × 5 |
| **Added in this edition** | |
| M1: share of nodes to migrate before worst-case blast radius ≤5% (synthetic Purdue-like fleet) | random 73% / acquaintance 44% / class-ordered 10% / degree-targeted 6% |
| M1: migrating all C4/C5 nodes (11% of fleet) | blast radius 100% → 4.5% |
| M2: attacker chance of forcing an authority change, {ML-DSA, LMS-SHA-256, SLH-DSA-SHAKE} | any 2 of 3: 0.00525; disjoint pairs only: 0.00027 (≈19× lower); honest availability 0.99475 → 0.99002 |
| M3: forger success through N independent stages, (1−d)ᴺ, d = 0.3 | N = 1 / 5 / 8: 0.70 / 0.17 / 0.058; honest false reset 0.8% at f = 0.001, N = 8 |
| M4: 32.768 kHz crystal drift | ±20 ppm = ±631 s a year; −40 °C worst case ≈ −164 ppm ≈ −86 min a year ≈ −14.3 h a decade; TCXO ±2 ppm = ±63 s a year |
| M5: exposure-years per device after a CRQC at T = 5 / 8 / 12 years | 5%/yr replacement: 15.1 / 12.9 / 10.5; 10%/yr: 5.6 / 4.1 / 2.7; 20%/yr: 1.5 / 0.8 / 0.3 |
| M6: random-migration threshold 1 − 1/R₀ | 67% (R₀ = 3), 90% (R₀ = 10) |
| M7: two families, each breaking with p = 0.05 | 50/50 fleet split: P(lose ≥ half) 0.0975, P(lose all) 0.0025; both on every device: P(lose all) 0.0025, no partial losses |
| Kinetic proofreading | one Hopfield stage ≈ squares the error; ten stages turn a 2× lifetime difference into ≈1,000× (2¹⁰ = 1,024) |
| Grid time | 50 Hz = 4.32 M cycles a day; −4 mHz = −80 ppm; 80 ppm for 50 days ≈ 5.8 min (Europe, 2018: about 6 min) |
| Counters that wrap | signed 32-bit Unix time ends 03:14:07 UTC, 19 Jan 2038; GPS week rollover every 1,024 weeks (≈19.7 years), next 20 Nov 2038; LMS h = 10 gives 1,024 signatures |

## 21.2 Glossary

- **CRQC:** cryptographically relevant quantum computer.
- **HNDL:** harvest now, decrypt later. **HNDL-to-authority** (harvest now, forge later) is its signature counterpart: authority that is still trusted when a CRQC arrives becomes forgeable.
- **First stage:** the immutable code that runs right after reset.
- **Locked flash:** a maker-defined region protected by write protection and readout locks.
- **Key-hash slot:** 32 bytes committing to a public key.
- **Floor:** a monotonic index below which keys and images are rejected.
- **Assumption class:** the set of hardness assumptions a key depends on.
- **Single-assumption-safe:** no single assumption failure satisfies an authorising quorum.
- **FDO:** FIDO Device Onboard. An **ownership voucher** is the off-device signed chain transferring ownership.
- **GDOI:** Group Domain of Interpretation, used by IEC 62351-9 for group keys.
- **KDC:** key distribution centre.
- **CBOM:** cryptographic bill of materials.
- **Enclave:** a zone containing legacy devices behind a PQ-terminating boundary.
- **Window staging:** pre-positioning a dormant, signed transition until a planned maintenance window.
- **RDP/HDP/WRP:** STM32 readout protection, hide protection and write protection.
- **NSIB:** nRF Secure Immutable Bootloader.
- **SP 800-230:** NIST draft with limited-use SLH-DSA parameter sets.
- **Disjoint-quorum rule:** an authority-changing quorum counts only if its members' assumption sets are disjoint (M2).
- **Waist:** a shared component that everything above depends on, as in an hourglass. Post-quantum signatures have two: SHA-2 and SHA-3/SHAKE.
- **Zeitgeber:** "time-giver"; an external cue that corrects a free-running clock (Part 6).
- **ENF:** electrical network frequency; its small fluctuations are common across a synchronous grid.
- **Co-stimulation, two-signal rule:** act only on a valid signature *plus* an independent confirming signal (Pattern 1).
- **Anergy:** a key that keeps sending validly signed authority-change requests without the required second class is put into a reduced-trust, boot-only state until a quorum restores it, and the event is reported (Pattern 1; I-14).
- **Kinetic proofreading:** buying accuracy with delay and independent stages, where any lapse resets progress (Pattern 2).
- **Molting protocol:** provision the new class alongside, shadow-sign, hide the old, shed it, harden (Pattern 15).
- **Heartbeat and escrow trigger:** a signed, periodic sign of life from the OEM whose absence for a defined period releases escrowed authority (Pattern 13).
- **Supersedure:** planned succession while the current authority still functions.
- **Slot drill:** a scheduled release verified through an alternate slot only, to prove the path works (I-13).
- **Exposure-years:** unmigrated devices × criticality × time; the integral of migration error (M5).
- **Acquaintance migration:** migrate a neighbour of a randomly chosen device; reaches hubs without an inventory (M1).
- **Persister cohort:** a small share of devices deliberately held back from a rollout as insurance (Pattern 31).
- **Senescence (device):** a reduced-privilege state entered when trust contact is stale; keeps working, stops changing (Pattern 14).
- **CODIT:** compartmentalisation of decay in trees; walls that limit spread in different directions (Pattern 26).
- **Evidence record (ERS):** a renewable chain of hash-tree timestamps keeping signed data provable after algorithms age (RFC 4998).
- **Spindle-checkpoint gating:** an irreversible fleet step waits until every dependent participant reports ready (Pattern 19).
- **Trust cartridge:** a field-replaceable certified module carrying keys, algorithms and slots (I-31).
- **Black channel:** a safety protocol that treats the communication channel as untrusted, so the channel's cryptography can change without changing the safety layer.
- **Response diversity:** variety in how components that perform the same function respond to the same disturbance (Pattern 30).

## 21.3 The new opportunity map

| Type | Opportunity |
|---|---|
| Technology | Locked hash first stage; SP 800-230 limited-use SLH-DSA; SHA-2 + SHA-3 hash engines; graded-authority rule; assumption-graph policy compiler |
| Product | Side-door audit kit and Authorisation Surface Map; compliance-evidence product; window-staging tooling; decommissioning receipts |
| Infrastructure | Open first-stage foundation; FDO-PQ profile; GDOI-PQ profile; neutral benchmark and conformance lab |
| Research | Lock fault resistance; single-assumption theory; floor-burn defences; crypto-confinement safety arguments; fleet algorithm diversity |
| Commercial entry | OEM porting and assurance; Indian critical-infrastructure pilots (2027–2029 deadlines); test-lab services; procurement clause libraries |
| **Added in this edition** | |
| Technology | Disjoint-quorum checker; zeitgeber fusion library; counter-capacity analyser; molting-protocol reference implementation |
| Product | Slot-drill and renewal-rehearsal tooling; exposure-years dashboards; acquaintance-migration planner that works without a full inventory |
| Infrastructure | A governed trust commons (Ostrom model) for witnesses, vouchers and the open first stage; evidence-record renewal service |
| Research | ENF not-before stamps; grid-cycle entrainment; trust cartridges for long-lived devices; a third independent signature class |

## 21.4 Method log: how the investigation was run

1. **Opportunity scan.** A global, then software-only, search for billion-dollar opportunities surfaced OT and embedded post-quantum migration as under-served and deadline-driven.
2. **First-principles pass.** Fifteen dimensions from quantum to economics produced the Industrial Trust Plane and H1–H22.
3. **Audit pass.** This established the foundations, the protocol atlas, the root-of-trust survey, a reassessment of H1–H42, the commercial challenge and the future outlook.
4. **Verification lab.** A 51-scene interactive build with live assertions recomputed every number. Discrepancies were disclosed rather than hidden.
5. **Invention pass.** Eight independent engines, then 110 hypotheses, 32 combinations, 11 architectures, a red team, weighted ranking, blueprints, experiments and three visions. About 60 sources.
6. **Second-pass challenge.** A traceability audit, a challenge register (C1–C22), 55 new problems, ten stakeholder perspectives, a layer matrix, simplification, second-order consequences, a technology register, an eight-position debate, redesigns, deployment scenarios, economics and a challenge board. About 70 sources.
7. **The first synthesis (previous edition).** Reconciled all passes, re-verified all arithmetic, added root causes R8 and R9, the six-chain authority graph, the device-class model with anti-weak-path invariants, the innovator's notebook (I-1 to I-12) and the consolidated corrections ledger.

8. **This edition: the nature, physics and history pass.**
   - **Five parallel research streams:** (1) immunology, molecular proofreading and collective decision-making; (2) biological and physical time, dormancy and longevity; (3) diversity, resilience and network science; (4) long-lived human institutions and the history of migrations; (5) hardware and sector precedents.
   - **About 45 further searches of my own** to cross-check the streams' key claims, which produced the corrections in rows 24–35 of Part 19 (rows 34 and 35 surfaced while the source register was being built).
   - **Seven quantitative models** in Python (M1–M7), kept with the atlas as `models/*.py`. Two of them changed recommendations (M2 on quorums, M1 on migration order).
   - **Three parallel lookups** to recover primary-source URLs for the register. They surfaced two more corrections (Part 19, rows 34–35). The per-turn web-search limit was reached near the end, so four register entries are given without URLs.
   - **Scope limits.** One research stream (biology) stopped partway; its key items were re-verified directly, and synthetic-biology detail was left out. Physical attack techniques on hardware were deliberately excluded, so Part 8 stays at the level of architecture and procurement.
   - **Method rule.** Every natural pattern had to pass five steps: evidence, principle, mechanism, where the analogy breaks, and a kill test. Several popular "nature facts" failed the evidence step and were corrected (Part 19).

**Where the syntheses made their own judgement calls [I]:**
- It ranked R8 and R9 above R1.
- It treated the device-class model as a recommendation, although no pass validated it.
- It kept stateful LMS for the interim first stage, despite the second pass's "eliminate stateful custody", because SP 800-230 is still a draft.
- It treated SHA-2 and SHA-3 as two independent waists, while noting that a cryptographer would discount that independence somewhat.
- It gave each codex pattern a status (established practice, formalisation, hypothesis, analogy only) by its own judgement. No pass has validated those statuses.
- It preferred counters to clocks wherever both would work, on the strength of Part 6's drift numbers and the automotive precedent.

## 21.5 Source register for the earlier passes (decisive sources from the two passes before this edition)

The source lists of the first passes are not reproduced. These are the sources on which the conclusions of the two passes before this edition rest; 21.6 lists this edition's.

**Policy and standards**
- NIST IR 8547 final analysis: https://postquantum.com/security-pqc/nist-ir-8547-final/ ; https://labs.cloudsecurityalliance.org/research/csa-research-note-nist-ir8547-pqc-transition-20261030-csa-st/ ; https://quantumcomputingreport.com/nist-releases-final-ir-8547-establishing-definitive-post-quantum-cryptography-transition-timeline-and-deprecation-schedules/
- OMB M-26-15: https://www.whitehouse.gov/wp-content/uploads/2026/06/M-26-15-Execution-of-the-Migration-to-Post-Quantum-Cryptography.pdf ; EO analysis: https://arxiv.org/pdf/2609.26225
- NIST SP 800-230 ipd: https://csrc.nist.gov/pubs/sp/800/230/ipd ; https://csrc.nist.gov/News/2026/nist-releases-draft-sp-800-230
- CNSA 2.0 FAQ v2.1: https://postquantum.com/security-pqc/nsa-cnsa-2-0-faq-v2-1-update/ ; https://quantumsentinel.uk/cnsa-2-0-1-january-2027-deadline/
- EU CRA: https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Cyber_Resilience_Act/cyber_resilience_act_node.html ; https://www.williamfry.com/knowledge/cyber-resilience-act-what-manufacturers-need-to-know/
- India: https://dst.gov.in/sites/default/files/Quantum-Safe-Ecosystem-in-India.pdf ; https://www.orfonline.org/expert-speak/india-s-post-quantum-cryptography-migration-roadmap ; https://postquantum.com/security-pqc/indias-quantum-safe-roadmap/
- Roughtime RFC 10049: https://datatracker.ietf.org/doc/rfc10049/
- Composite ML-DSA: https://datatracker.ietf.org/doc/html/draft-ietf-lamps-pq-composite-sigs
- TCG TPM 2.0 v1.85: https://trustedcomputinggroup.org/new-computing-specification-implements-pqc-measures-to-protect-users-from-quantum-attacks/
- FIDO Device Onboard: https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-WD-v2.0-20250617/FIDO-Device-Onboard-WD-v2.0-20250617.html
- OCP Secure Boot: https://www.opencompute.org/documents/secure-boot-2-pdf/
- IEC 62351-9:2023: https://standards.iteh.ai/catalog/standards/iec/d57aa4c9-5283-4548-b3a2-8b199d65a92e/iec-62351-9-2023
- Microsoft Secure Boot CA expiry: https://support.microsoft.com/en-us/servicing/os/secure-boot/2026/02/when-secure-boot-certificates-expire-on-windows-devices

**Quantum estimates**
- Gidney 2025: https://arxiv.org/pdf/2505.15917
- Google Quantum AI: https://research.google/blog/safeguarding-cryptocurrency-by-disclosing-quantum-vulnerabilities-responsibly/ ; https://quantumai.google/static/site-assets/downloads/cryptocurrency-whitepaper.pdf

**Silicon, boot and side doors**
- Nordic NSIB: https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/samples/bootloader/README.html
- ST OEMiRoT: https://wiki.st.com/stm32mcu/wiki/Security:OEMiRoT_for_STM32C5 ; ST debug authentication: https://wiki.st.com/stm32mcu/wiki/Security:Debug_Authentication ; RDP/WRP/HDP: https://www.openstm32.org/article3-RDP-WRP-PCROP-and-HDP-on-STM32
- Silicon Labs secure debug: https://www.silabs.com/documents/public/application-notes/an1190-efr32-secure-debug.pdf ; https://docs.silabs.com/iot-security/1.2.3/series2-secure-debug/05-debug-unlock
- NXP debug credentials AN13814: https://www.nxp.com/docs/en/application-note/AN13814.pdf
- Infineon TRAVEO lifecycle: https://community.infineon.com/t5/Knowledge-Base-Articles/Secure-Microcontrollers-Migrate-a-TRAVEO-T2G-device-to-the-SECURE-lifecycle/ta-p/333987
- Arm ADAC: https://documentation-service.arm.com/static/628bad10e3c4322a76af60ef
- OpenTitan secure boot and RFC #30765: https://docs.opentitan.org/doc/security/specs/secure_boot/ ; https://github.com/lowRISC/opentitan/issues/30765
- TI AM263P4: https://e2e.ti.com/support/microcontrollers/arm-based-microcontrollers-group/arm-based-microcontrollers/f/arm-based-microcontrollers-forum/1585960/am263p4-post-quantum-signature-verification-in-rom-bootloader
- Microchip MEC175xB: https://ir.microchip.com/news-events/press-releases/detail/1312/microchip-brings-hardware-quantum-resistance-to-embedded-controllers
- NXP MCX A5: https://www.cnx-software.com/2026/08/19/nxp-mcx-a5-cortex-m33-mcu-family-supports-10base-t1s-single-pair-ethernet-and-post-quantum-cryptography/
- ST STM32G5: https://quantumzeitgeist.com/stmicroelectronics-post-quantum-mcu-hardware-cryptography/
- wolfBoot: https://www.wolfssl.com/products/wolfboot/
- Intel patents: https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11405213 ; https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12137169
- Adams Bridge side-channel analysis: https://github.com/chipsalliance/adams-bridge/blob/main/docs/AdamsBridgeSCA.md ; https://mjos.fi/doc/20250530-hardwear-abr.pdf ; https://www.etsi.org/wp-content/uploads/S33_PQSecure_Azarderakhsh.pdf

**Benchmarks**
- RP2040 ML-DSA study: https://arxiv.org/pdf/2603.19340
- Campos et al. LMS/XMSS on Cortex-M4: https://eprint.iacr.org/2020/470.pdf
- Banegas et al. on nRF52840: https://arxiv.org/pdf/2106.05577
- wolfSSL STM32 ML-KEM/ML-DSA: https://www.wolfssl.com/updated-post-quantum-benchmarks-for-ml-kem-and-ml-dsa-on-stm32/
- SLotH: https://link.springer.com/chapter/10.1007/978-3-031-68376-3_9
- ML-KEM for Sampled Values: https://arxiv.org/pdf/2608.22123
- Threshold ML-DSA (Mithril): https://csrc.nist.gov/csrc/media/Projects/threshold-cryptography/documents/TCall-1/Mithril-PW01.pdf

**Operations and economics** (mostly vendor-sponsored)
- aDolus, OT firmware patching: https://blog.adolus.com/the-wretched-state-of-ot-firmware-patching
- ABB downtime survey: https://new.abb.com/news/detail/107660/abb-survey-reveals-unplanned-downtime-costs-125-000-per-hour
- S&C truck-roll cost: https://www.sandc.com/en/gridtalk/2017/march/20/the-real-cost-of-a-truck-roll
- OPC UA misconfiguration: https://shieldworkz.com/blogs/securing-opc-ua-certificates-policies-and-common-misconfigurations-2026-update ; https://www.trout.software/resources/securing-opc-ua
- Spacecraft SDLS: https://www.ndss-symposium.org/wp-content/uploads/spacesec2024-53-paper.pdf

## 21.6 Source register for this edition

These are the sources added by the nature, physics and history pass, grouped by the part they support. Each URL was located and matched to the citation by title and year in this pass. Where no URL could be verified, the citation is given in full so it can be found. Many further papers are cited inline in Part 5 and listed at the end.

**Immunology, molecular proofreading and recognition (Part 5.1)**
- Hopfield (1974), Kinetic proofreading, PNAS: https://doi.org/10.1073/pnas.71.10.4135
- McKeithan (1995), Kinetic proofreading in T-cell receptor signal transduction, PNAS: https://doi.org/10.1073/pnas.92.11.5042
- Britain, Town & Weiner (2022), Progressive enhancement of kinetic proofreading in T cell antigen discrimination, eLife: https://doi.org/10.7554/eLife.75263
- Matzinger (2002), The danger model: a renewed sense of self, Science: https://doi.org/10.1126/science.1071059
- Conrad et al. (2023), autoimmune disorders in 22 million UK individuals, The Lancet: https://doi.org/10.1016/S0140-6736(23)00457-9
- Stibor, Mohr, Timmis & Eckert (2005), Is negative selection appropriate for anomaly detection?, GECCO: https://doi.org/10.1145/1068009.1068061

**Collective decisions and succession (Part 5.2)**
- Seeley et al. (2012), Stop signals provide cross inhibition in honeybee swarms, Science: https://doi.org/10.1126/science.1210361
- Seeley & Visscher (2004), Quorum sensing during nest-site selection by honeybee swarms, Behav. Ecol. Sociobiol.: https://doi.org/10.1007/s00265-004-0814-5
- University of Georgia Bee Program, queenless colonies and laying workers: https://bees.caes.uga.edu/beekeeping-resources/honey-bee-disorders/honey-bee-disorders-non-infectious-diseases-and-pests.html
- Sagili et al. (2018), larval selection for emergency queen rearing, Scientific Reports: https://doi.org/10.1038/s41598-018-25976-7

**Time, rhythm, dormancy and longevity in living systems (Part 5.4)**
- Nakajima et al. (2005), in-vitro reconstitution of the cyanobacterial KaiC clock, Science: https://doi.org/10.1126/science.1108451
- Czeisler et al. (1999), near-24-hour period of the human circadian pacemaker, Science: https://doi.org/10.1126/science.284.5423.2177
- Khalsa et al. (2003), phase response curve to single bright light pulses, J. Physiol.: https://doi.org/10.1113/jphysiol.2003.040477
- Mirollo & Strogatz (1990), Synchronization of pulse-coupled biological oscillators, SIAM J. Appl. Math.: https://doi.org/10.1137/0150098
- Werner-Allen et al. (2005), Firefly-inspired sensor network synchronicity, ACM SenSys: https://doi.org/10.1145/1098918.1098934
- Wang & Wang (2020), synchronisation of pulse-coupled oscillators under Byzantine attacks, IEEE Trans. Signal Processing: https://doi.org/10.1109/TSP.2020.2993643
- Xie et al. (2013), Sleep drives metabolite clearance from the adult brain, Science: https://doi.org/10.1126/science.1241224
- Borbély (1982), A two process model of sleep regulation, Human Neurobiology: https://pubmed.ncbi.nlm.nih.gov/7185792/
- Michigan State University, the 2021 dig of Beal's 1879 seed experiment: https://msutoday.msu.edu/news/2021/05/ask-the-expert-beal-seed-experiment
- Sallon et al. (2008), Germination, genetics, and growth of an ancient date seed, Science: https://doi.org/10.1126/science.1153600
- Yashina et al. (2012), whole fertile plants from 30,000-year-old fruit tissue, PNAS: https://doi.org/10.1073/pnas.1118386109

**Damage, resilience and ecology (Part 5.5)**
- Shigo & Marx (1977), Compartmentalization of decay in trees, USDA Forest Service AIB 405: https://research.fs.usda.gov/treesearch/5292
- OpenStax, Anatomy and Physiology, cardiac muscle and electrical activity: https://openstax.org/books/anatomy-and-physiology/pages/19-2-cardiac-muscle-and-electrical-activity
- Calkin, Thompson & Finney (2015), Negative consequences of positive feedbacks in US wildfire management, Forest Ecosystems: https://doi.org/10.1186/s40663-015-0033-8
- Kreider et al. (2024), Fire suppression makes wildfires more severe, Nature Communications: https://doi.org/10.1038/s41467-024-46702-0
- Bruns (2017), Southern corn leaf blight: a story worth retelling, Agronomy Journal: https://doi.org/10.2134/agronj2017.01.0006
- Kema et al. (2021), Editorial: Fusarium wilt of banana, a recurring threat, Frontiers in Plant Science: https://doi.org/10.3389/fpls.2020.628888
- Yoshida et al. (2013), the P. infestans lineage behind the Irish potato famine, eLife: https://doi.org/10.7554/eLife.00731
- Schindler et al. (2010), Population diversity and the portfolio effect, Nature: https://doi.org/10.1038/nature09060
- Elmqvist et al. (2003), Response diversity, ecosystem change, and resilience, Front. Ecol. Environ.: https://doi.org/10.1890/1540-9295(2003)001%5B0488:RDECAR%5D2.0.CO;2
- Balaban et al. (2004), Bacterial persistence as a phenotypic switch, Science: https://doi.org/10.1126/science.1099390
- Cohen (1966), Optimizing reproduction in a randomly varying environment, J. Theor. Biol.: https://doi.org/10.1016/0022-5193(66)90188-3
- Yi, Huang, Simon & Doyle (2000), integral feedback in bacterial chemotaxis, PNAS: https://doi.org/10.1073/pnas.97.9.4649
- Tero et al. (2010), Rules for biologically inspired adaptive network design, Science: https://doi.org/10.1126/science.1177894
- Karst et al. (2023), citation bias on common mycorrhizal networks, Nature Ecology & Evolution: https://doi.org/10.1038/s41559-023-01986-1
- Vincent et al. (2006), Biomimetics: its practice and theory, J. R. Soc. Interface: https://doi.org/10.1098/rsif.2006.0127

**Diversity, networks and engineered resilience (Parts 5.5, 9)**
- Knight & Leveson (1986), independence in multiversion programming, IEEE TSE: https://doi.org/10.1109/TSE.1986.6312924
- US NRC, Branch Technical Position 7-19, Rev. 9 (2024): https://www.nrc.gov/docs/ML2400/ML24005A077.pdf
- Forrest, Somayaji & Ackley (1997), Building diverse computer systems, HotOS-VI: https://doi.org/10.1109/HOTOS.1997.595185
- Geer et al. (2003), CyberInsecurity: the cost of monopoly: https://ccianet.org/wp-content/uploads/2003/09/cyberinsecurity%20the%20cost%20of%20monopoly.pdf
- Pastor-Satorras & Vespignani (2002), Immunization of complex networks, Phys. Rev. E: https://doi.org/10.1103/PhysRevE.65.036104
- Cohen, Havlin & ben-Avraham (2003), Efficient immunization strategies, Phys. Rev. Lett.: https://doi.org/10.1103/PhysRevLett.91.247901
- Demers et al. (1987), Epidemic algorithms for replicated database maintenance, PODC: https://doi.org/10.1145/41840.41841
- Adepu & Mathur (2016), Using process invariants to detect cyber attacks on a water treatment system, IFIP SEC: https://doi.org/10.1007/978-3-319-33630-5_7

**Long-lived institutions, deep time and evidence (Part 7.1–7.5)**
- Ise Jingu, Shikinen Sengu: https://www.isejingu.or.jp/en/ritual/index.html#sengu
- Mie Prefecture tourism, Ise Jingu Sengu and craft transmission: https://kankomie.or.jp/report/1728?wovn=en
- UNESCO (2009), Irrigators' tribunals of the Spanish Mediterranean coast: https://ich.unesco.org/en/RL/irrigators-tribunals-of-the-spanish-mediterranean-coast-the-council-of-wise-men-of-the-plain-of-murcia-and-the-water-tribunal-of-the-plain-of-valencia-00171
- Cox, Arnold & Villamayor Tomás (2010), design principles for community-based resource management, Ecology and Society: https://doi.org/10.5751/ES-03704-150438
- ICANN (2018), first root KSK rollover successfully completed: https://www.icann.org/en/announcements/details/first-root-ksk-rollover-successfully-completed-15-10-2018-en
- RFC 5011, Automated Updates of DNSSEC Trust Anchors: https://www.rfc-editor.org/info/rfc5011
- Sebeok (1984), Communication Measures to Bridge Ten Millennia, ONWI-532: https://www.osti.gov/biblio/6705990
- 40 CFR 191.14, assurance requirements: https://www.ecfr.gov/current/title-40/chapter-I/subchapter-F/part-191/subpart-B/section-191.14
- Long Now Foundation, design principles of the 10,000-year Clock: https://longnow.org/clock/principles/
- RFC 4998, Evidence Record Syntax: https://www.rfc-editor.org/info/rfc4998
- RFC 6283, XML Evidence Record Syntax: https://www.rfc-editor.org/info/rfc6283
- Haber & Stornetta (1991), How to time-stamp a digital document, J. Cryptology: https://doi.org/10.1007/BF00196791
- GNU Guix (2023), the full-source bootstrap: https://guix.gnu.org/blog/2023/the-full-source-bootstrap-building-from-source-all-the-way-down/
- Sigsum, witness cosigning: https://www.sigsum.org/docs
- C2SP, transparency-log cosignature and witness specifications: https://c2sp.org/tlog-witness

**The extinction record and how migrations really go (Parts 2.6, 7.6)**
- Fillinger & Stevens (2015), Reverse-engineering of the cryptanalytic attack used in the Flame super-malware, ASIACRYPT: https://marc-stevens.nl/research/papers/AC15-FS.pdf
- Stevens et al. (2017), The first collision for full SHA-1 (SHAttered): https://doi.org/10.1007/978-3-319-63688-7_19
- Leurent & Peyrin (2020), SHA-1 is a Shambles, USENIX Security: https://www.usenix.org/conference/usenixsecurity20/presentation/leurent
- NIST (2022), NIST retires SHA-1: https://www.nist.gov/news-events/news/2022/12/nist-retires-sha-1-cryptographic-algorithm
- Beullens (2022), Breaking Rainbow takes a weekend on a laptop, ePrint 2022/214: https://eprint.iacr.org/2022/214
- Castryck & Decru (2022), An efficient key recovery attack on SIDH, ePrint 2022/975: https://eprint.iacr.org/2022/975
- NIST (2022), first four quantum-resistant cryptographic algorithms: https://www.nist.gov/news-events/news/2022/07/nist-announces-first-four-quantum-resistant-cryptographic-algorithms
- NIST (2025), HQC announced as a fourth-round selection: https://csrc.nist.gov/news/2025/hqc-announced-as-a-4th-round-selection
- NIST (2026), nine candidates advance to the third round of additional signatures: https://csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc
- Internet Society Pulse (2026), 18 years later, IPv6 reaches majority: https://pulse.internetsociety.org/en/blog/18-years-later-ipv6-reaches-majority/
- Chromium blog (2023), hybrid Kyber KEM in Chrome: https://blog.chromium.org/2023/08/protecting-chrome-traffic-with-hybrid.html
- Chromium blog (2024), ML-KEM in Chrome: https://security.googleblog.com/2024/09/a-new-path-for-kyber-on-web.html
- tldr.fail: https://tldr.fail/
- Let's Encrypt (2021), DST Root CA X3 expiration: https://letsencrypt.org/docs/dst-root-ca-x3-expiration-september-2021/
- FCC, plan ahead for the phase-out of 3G networks: https://www.fcc.gov/sites/default/files/plan_ahead_for_3g_shutoff_consumer_guide.pdf
- gov.uk, Telecare National Action Plan for the digital phone switchover: https://www.gov.uk/government/publications/telecare-national-action-plan-protecting-telecare-users-throughout-the-digital-phone-switchover
- Which? (2025), Closing the gaps: protecting telecare users in the analogue-to-digital shift: https://www.which.co.uk/policy-and-insight/article/closing-the-gaps-protecting-telecare-users-in-the-shift-from-analogue-to-digital-azmhv4i4Uknj
- Visa (2018), Chip card update: counterfeit fraud down 76% at chip-enabled merchants: https://usa.visa.com/dam/VCOM/global/visa-everywhere/documents/visa-emv-chip-infographic-q1-2018.pdf
- Hayashi (2025), Card-not-present fraud rates in the US after the migration to chip cards, Federal Reserve Bank of Kansas City: https://www.kansascityfed.org/research/payments-system-research-briefings/card-not-present-fraud-rates-in-the-united-states-after-the-migration-to-chip-cards/
- US Department of Commerce (1999), The economics of Y2K and the impact on the United States: https://www.commerce.gov/data-and-reports/reports/1999/11/economics-y2k-and-impact-united-states
- CrowdStrike (Aug 2024), External technical root cause analysis: Channel File 291 (URL not verified)
- Microsoft (20 Jul 2024), blog post estimating 8.5 million affected Windows devices (URL not verified)

**Time without a clock (Part 6)**
- Raltron, R38 32.768 kHz crystal datasheet: https://www.raltron.com/webproducts/specs/CRYSTAL/R38.pdf
- Analog Devices, AN58: Crystal considerations with Analog Devices real-time clocks: https://www.analog.com/en/resources/design-notes/crystal-considerations-with-analog-devices-realtime-clocks-rtcs.html
- Rahmati et al. (2012), TARDIS, USENIX Security: https://www.usenix.org/conference/usenixsecurity12/technical-sessions/presentation/rahmati
- ENTSO-E (2018), Continental Europe frequency deviation: https://www.entsoe.eu/news/2018/03/06/press-release-continuing-frequency-deviation-in-the-continental-european-power-system-originating-in-serbia-kosovo-political-solution-urgently-needed-in-addition-to-technical/
- UCTE Operation Handbook, Policy 1: load-frequency control: https://eepublicdownloads.entsoe.eu/clean-documents/pre2015/publications/entsoe/Operation_Handbook/Policy_1_final.pdf
- FERC (18 Jan 2017), letter order approving retirement of BAL-004-0, Docket RD17-1-000 (URL not verified)
- Grigoras (2005), the ENF criterion in audio forensics: https://journal.equinoxpub.com/IJSLL/article/view/9977
- Viswanathan, Tan & Yau (2016), power-grid clock synchronisation for industrial IoT, IEEE RTSS: https://doi.org/10.1109/RTSS.2016.023
- Rowe, Gupta & Rajkumar (2009), clock synchronisation from AC power lines (Syntonistor), ACM SenSys: https://www.andrew.cmu.edu/user/agr/pubpg/sensys-09.pdf
- EconLedger (2021), Proof-of-ENF consensus: https://www.mdpi.com/1999-5903/13/10/248
- NASA (2018), NASA team first to demonstrate X-ray navigation in space (SEXTANT): https://www.nasa.gov/centers-and-facilities/goddard/nasa-team-first-to-demonstrate-x-ray-navigation-in-space/
- GPS.gov, GPS week number rollover (2019): https://www.gps.gov/support/user/rollover/
- Inside GNSS (2019), GPS rollover and the New York City wireless network: https://insidegnss.com/gps-rollover-hamstrings-new-york-city-wireless-network-and-a-handful-of-other-systems/
- StateScoop (2019), NYCWiN reboot; next GPS rollover in 2038: https://statescoop.com/nyc-works-to-reboot-wireless-network-after-gps-update-crashed-it/
- RFC 5280, certificate validity (99991231235959Z): https://www.rfc-editor.org/rfc/rfc5280#section-4.1.2.5

**Sector precedents (Part 7.7)**
- AUTOSAR, Specification of Secure Onboard Communication: https://autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_SecureOnboardCommunication.pdf
- UN Regulation No. 155, cyber security and CSMS (EU Official Journal text): https://eur-lex.europa.eu/eli/reg/2025/5/oj
- UN Regulation No. 156, software updates and SUMS (EU Official Journal text): https://eur-lex.europa.eu/eli/reg/2021/388/oj
- UK Vehicle Certification Agency, R155/R156 application dates: https://www.vehicle-certification-agency.gov.uk/connected-and-automated-vehicles/cyber-security-and-software-updating/
- CENELEC, EN 50159:2010 safety-related communication in transmission systems (replaced by EN 50159:2026): https://shop.standards.ie/en-ie/standards/en-50159-2010-351552_saig_cenelec_cenelec_802417
- SAE ITC / ARINC, 835-2: https://saemobilus.sae.org/standards/arinc835-2-arinc-835-2-guidance-security-loadable-software-parts-using-digital-signatures
- RTCA, DO-326 airworthiness security process specification (DO-326A; DO-326B also listed): https://www.rtca.org/security/
- IMDRF (2023), N70: cybersecurity of legacy medical devices: https://www.imdrf.org/sites/default/files/2023-04/IMDRF%20Principles%20and%20Practices%20of%20Cybersecurity%20for%20%20Legacy%20Medical%20Devices%20Final%20%28N70%29.pdf
- FDA, refuse-to-accept policy for cyber devices (section 524B): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-refuse-accept-policy-cyber-devices-and-related-systems-under-section
- NASA-STD-1006, Space System Protection Standard (2019 baseline; Rev. A 2022 at standards.nasa.gov/node/2430): https://soma.larc.nasa.gov/STP/tdmo/pdf_files/nasa-std-1006.pdf
- NASA (2020), FAQs for protecting spaceborne assets: https://discovery.larc.nasa.gov/discovery/pdf_files/2019AO/33_FAQs%20for%20Protecting%20Spaceborne%20Assets%2013-May-2020.pdf
- NASA JPL (2024), Voyager 1 resumes sending engineering updates to Earth: https://www.jpl.nasa.gov/news/nasas-voyager-1-resumes-sending-engineering-updates-to-earth/
- NASA JPL (2013), Curiosity rover's recovery on track (B-side computer): https://www.jpl.nasa.gov/news/curiosity-rovers-recovery-on-track
- NSA, CNSA 2.0 and quantum computing FAQ (v2.1): https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ_.PDF
- GSMA, PQ.03 post-quantum guidelines for telecom: https://www.gsma.com/newsroom/gsma_resources/pq-03-post-quantum-cryptography-guidelines-for-telecom-use-cases

**Hardware and verified code (Part 8)**
- CHIPS Alliance, Caliptra overview at DAC 2025 (2.0 and Adams Bridge): https://www.chipsalliance.org/events/DAC_Caliptra_2025.pptx.pdf
- CHIPS Alliance (2025), Caliptra launches 2.1 RTL release: https://www.chipsalliance.org/news/caliptra2-1/
- CHIPS Alliance, Adams Bridge repository: https://github.com/chipsalliance/adams-bridge
- Lattice (2025), MachXO5-NX TDQ: https://ir.latticesemi.com/news-releases/news-release-details/lattice-launches-industry-first-pqc-ready-fpga-family-machxo5-nx
- NXP, MIFARE SAM AV3 secure access module (hardware certified to CC EAL6+): https://www.nxp.com/products/rfid-nfc/mifare-hf/mifare-sam/mifare-sam-av3:MIFSAMAV3
- Pappu, Recht, Taylor & Gershenfeld (2002), Physical one-way functions, Science: https://doi.org/10.1126/science.1074376
- Rührmair et al. (2010), Modeling attacks on physical unclonable functions, ACM CCS: https://doi.org/10.1145/1866307.1866335
- Applied DNA Sciences (2012), Defense Logistics Agency mandates DNA marking on microchips (FSC 5962): https://www.globenewswire.com/news-release/2012/08/16/1211640/0/en/Defense-Logistics-Agency-Mandates-SigNature-R-DNA-on-Microchips.html
- Microsoft Research (2026), Laser writing in glass for dense, fast and efficient archival data storage, Nature: https://www.nature.com/articles/s41586-025-10042-w
- Grass et al. (2015), DNA in silica, Angewandte Chemie: https://doi.org/10.1002/anie.201411378
- Erlich & Zielinski (2017), DNA Fountain, Science: https://doi.org/10.1126/science.aaj2038
- Cryspen (2024), verified ML-KEM in Rust (libcrux): https://cryspen.com/post/ml-kem-implementation/
- OpenSSH 10.0 release notes; 9.9 notes at openssh.com/releasenotes.html: https://www.openssh.com/txt/release-10.0
- seL4 and DARPA HACMS: https://sel4.systems/About/history.html

**Policy and standards checked at the primary in this edition (Part 2.2)**
- NIST IR 8547 (final), Transition to Post-Quantum Cryptography Standards: https://csrc.nist.gov/pubs/ir/8547/final
- NIST FIPS 203, ML-KEM: https://csrc.nist.gov/pubs/fips/203/final
- NIST FIPS 204, ML-DSA: https://csrc.nist.gov/pubs/fips/204/final
- NIST FIPS 205, SLH-DSA: https://csrc.nist.gov/pubs/fips/205/final
- NIST SP 800-208, stateful hash-based signatures: https://csrc.nist.gov/pubs/sp/800/208/final
- NIS Cooperation Group (2025), EU coordinated implementation roadmap for PQC: https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography
- India Central Electricity Authority, Cyber Security in Power Sector Regulations (notified 31 Jul 2026; in force 1 Apr 2027) (URL not verified)

**Further sources cited inline in Parts 2.6 and 5–8, not repeated above** (full citations at the point of use)
- *Immunology:* Bretscher & Cohn (1970), Science; Xing & Hogquist (2012), Cold Spring Harbor Perspectives in Biology.
- *Recognition:* a deep-sequencing study of acquired CRISPR spacers (Nature Communications, 2013); Caves, Stevens, Iversen & Spottiswoode (2015), Proc. R. Soc. B; Aubin & Jouventin (1998) and Aubin, Jouventin & Hildebrand (2000), Proc. R. Soc. B; Akino et al. (1999), Proc. R. Soc. B.
- *Collective decisions:* Passino & Seeley (2006), Behavioral Ecology and Sociobiology.
- *Change and development:* Ohno (1970), *Evolution by Gene Duplication*; Kim et al. (1994), Science; Rieder et al. (1994, 1995), Journal of Cell Biology; Takahashi & Yamanaka (2006), Cell; Okita, Ichisaka & Yamanaka (2007), Nature.
- *Architecture of evolvable systems:* Kirschner & Gerhart (1998), PNAS; Csete & Doyle (2004), Trends in Biotechnology; Carlson & Doyle (2002), PNAS; Akhshabi & Dovrolis (2011), ACM SIGCOMM.
- *Time and longevity:* Boothby et al. (2017), Molecular Cell; Leland et al. (2018), JGR Biogeosciences.
- *Bet hedging:* Kelly (1956), Bell System Technical Journal; Donaldson-Matasci, Bergstrom & Lachmann (2010).
- *Crops and famine:* Ploetz (2011); Ó Gráda (1993), History Ireland.
- *Institutions and deep time:* Ostrom (1990), *Governing the Commons*; the Sandia WIPP marker report (1993); CAMiLEON (2002) and Ariadne 36 (2003) on the BBC Domesday Project.
- *Process invariants:* Adepu & Mathur (2016), ACM AsiaCCS; Umer et al. (2020), International Journal of Critical Infrastructure Protection.
- *Cryptographic failures:* Microsoft Security Advisory 2718704 and Stevens (CWI) on Flame; Tao, Petzoldt & Ding (2020), ePrint 2020/1424; Chen (2024), ePrint 2024/555; Bernstein et al. (2025), TCHES; Ulitzsch et al. (2023), TCHES; Zhou et al. (2025), TCHES.

---

## Closing note

The investigation started by asking how to migrate industrial cryptography to post-quantum algorithms. It ends with a different question: **how do you build machines that can accept change, safely, long after the people and companies who made them are gone?**

Post-quantum migration is the first hard deadline that question has faced. The answer is small rather than grand:
- a few kilobytes of locked, hash-based code;
- three 32-byte commitments spanning both hash waists;
- one rule that makes changing authority harder than booting, and one that refuses any quorum sharing a weakness;
- the courage to delete debug ports and remote paths nobody can protect;
- contracts that move authority to the owner before the maker disappears, triggered by a heartbeat that stops;
- changes that arrive in small, rehearsed steps during maintenance windows rather than as emergencies;
- a migration order that protects the hubs first.

None of this is new to life. A T cell waits for a second signal before it acts. A bee colony raises a successor while the old queen still lives. A tree walls off what it cannot heal and keeps growing around it. A seed waits out decades and wakes only when several independent cues agree. Ise has stayed the same shrine for thirteen centuries by being rebuilt every twenty years. Systems that last do not resist change. They make change routine, staged, confirmed and survivable.

Everything else is delivery. The next steps cost two weeks each: find out how many industrial MCUs can lock their first stage, and check every counter and every quorum in your designs for the flaw that fails all at once.

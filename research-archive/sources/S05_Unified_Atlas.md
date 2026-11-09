# Trust That Outlives Its Makers
## A Unified Atlas of Post-Quantum Security for OT and Embedded Infrastructure

*Everything this investigation has produced so far, rewritten into one argument: five research passes, one interactive verification lab, two invention rounds and two red-team rounds. 6 November 2026.*

---

## How to read this document

This is not a stack of reports stapled together. Each earlier pass changed what the earlier ones meant, so the material has been re-derived into one line of reasoning. Where a later pass overturned an earlier belief, only the surviving belief appears in the main text. The overturned ones are kept in **Part 14 (the corrections ledger)**, so you can see how the understanding moved and why.

**Evidence labels used throughout**

| Label | Meaning |
|---|---|
| **[F]** | Primary fact: a standard, a specification, an official document |
| **[2nd]** | A fact reported by a secondary source; the primary was not opened |
| **[V]** | Vendor or sponsor claim, not independently verified |
| **[D]** | Demonstrated or measured result from a paper or benchmark |
| **[C]** | Computed here and cross-checked (Python and in-browser in the verification lab) |
| **[E]** | Estimate; the arithmetic is shown |
| **[I]** | Inference by this investigation |
| **[H]** | Invention or hypothesis: proposed, not validated |
| **[S]** | Speculative long-range possibility |

**Honesty about coverage.** You invited 500–600 sources. The two most recent passes touched about 130 distinct sources between them, and about 80 were decisive. The earlier passes used more, but their source lists are not reproduced here. Where a claim rests on one source, a vendor or a draft, it says so. Part 15 lists what to verify next.

---

## Contents

0. The answer on one page
1. How the understanding evolved
2. Foundations: the threat, the mathematics, the machines
3. The problem universe, compressed to its root causes
4. The hidden structure: how authority actually flows, and where it leaks
5. The solution space after two invention rounds and two red teams
6. The recommended architecture stack, in minimal and high-assurance forms
7. Allocating security by device class
8. Seven deployment scenarios, end to end
9. Economics: who pays, why they wait, and what makes them act early
10. The design debate and where it converged
11. Validation programme: experiments ordered by information value
12. The long view: principles for infrastructure meant to last 50–100 years
13. The innovator's notebook: new ideas from the synthesis
14. Corrections ledger: what we got wrong and fixed
15. Open questions and the roadmap with decision gates
16. Appendices: verified number card, glossary, source register

---

# 0. The answer on one page

**The problem is not "replace RSA with ML-KEM".** For OT and embedded systems, post-quantum migration is a special case of a broader failure. **Long-lived devices cannot safely accept change.** They resist new algorithms, new owners, new software, new authority and new epochs of trust. The quantum computer is the first change agent with a deadline, but not the last. [I]

**What actually breaks.** Real-time OT data paths (IEC 61850 GOOSE and Sampled Values, DNP3-SA, SecOC, LoRaWAN) are already symmetric. AES and HMAC survive quantum attack. [F] The exposure sits in **authority**:
- who may sign firmware, configuration and settings;
- who may unlock debug, transfer ownership or inject keys at the factory;
- how long-term symmetric keys were first delivered.

An attacker who can forge classical signatures after a cryptographically relevant quantum computer (CRQC) exists does not need to decrypt anything. They sign. [I]

**Three findings reshaped the direction.**

1. **The binding constraint is not the boot ROM but update adoption.**
   - In one vendor analysis of Microsoft customer data, 60% of PLCs ran firmware with eight or more exploitable CVEs, even though fixes had been available for over ten years. [V]
   - Fewer than 30% of facilities patch on a defined schedule, and only 15% patch in routine maintenance windows (SANS 2023 survey of 700+ respondents). [2nd]
   - A post-quantum signature that nobody installs protects nothing.
2. **Many existing MCUs can already host a post-quantum, hash-based, immutable first stage in locked flash, without new mask ROM.**
   - Nordic's NSIB runs from write-protected flash and stores only public-key *hashes*. Using a higher key index permanently invalidates lower ones. [F]
   - ST's OEMiRoT combines a unique boot entry with write protection, RDP Level 2 and HDP. [F]
   - The earlier plan to licence a new "Authority Continuity Kernel" into silicon from about 2028 was aimed at the wrong bottleneck.
3. **The worst exposures are classical side doors around secure boot.** Each of these gives a quantum-capable forger full control without touching the boot chain:
   - debug-unlock certificates (Silicon Labs ECDSA-P256; NXP RoT-chained debug credentials);
   - ownership-transfer messages (OpenTitan ECDSA-only);
   - FIDO Device Onboard (FDO) ownership vouchers (SECP256R1/384R1);
   - factory key injection;
   - engineering-workstation configuration authority. [F/I]

**What to build first, ranked robustly across two weightings** (Part 6 has the detail):

1. **An open, locked-flash continuity first stage.**
   - It holds a hash-based verifier and **at least three key-hash slots spanning at least two independent assumption classes**.
   - It enforces a floor rule: *advancing the floor needs a signature from a different slot than the one being retired.* [H, buildable now]
2. **Side-door closure.** Disable field debug after commissioning, use PQ debug credentials bound to device UUID, and audit every lifecycle transition. [H/F]
3. **Symmetric process-bus fabric.**
   - ML-KEM-768 enrolment happens once.
   - A KDC inside the enclave uses per-device key diversification.
   - IEC 62351-6 MACs stay unchanged. [H, buildable now]
4. **PQ-capable FDO ownership vouchers with contractual voucher escrow**, so an OEM exit does not orphan the fleet. [H]
5. **Maintenance-window-aligned staging.** Signed transition bundles wait dormant in the A/B slot until the planned window, and devices report signed state afterwards. [H]
6. **Enclave containment plus a dated replacement plan** for devices that cannot be changed. India's national roadmap recommends exactly this for classical-only systems. [2nd]
7. **Fleet crypto-state evidence**, using CycloneDX CBOM plus TCG/IETF attestation formats rather than a new format, tied to EU CRA and India's critical-infrastructure deadlines. [H]

**What was demoted to research:**
- new-ROM kernel licensing;
- a neutral custodian utility;
- threshold ML-DSA succession;
- a "time-free validity" product (index floors already ship);
- linear pre-rotation (it saves only 1.5–3×, not the 10× first claimed);
- stateful LMS root custody as a business. NIST draft SP 800-230 adds SLH-DSA parameter sets limited to 2²⁴ signatures, tailored to firmware signing. [F, draft]

**The hard boundary.** Some devices cannot be rescued by cryptography:
- an immutable verifier that only speaks a classical family;
- no lockable stage;
- remaining offline until a CRQC exists.

Only physical presence, network containment or replacement helps them. So **every device shipped from now on should carry a multi-class, hash-anchored first stage.** Each year of delay adds devices to the unrescuable set. [I]

**The single cheapest, highest-value experiment.** Do a two-week desk survey of what fraction of industrial MCU families support a lockable, maker-defined immutable first stage (E-A1).
- If ≥50% do, the silicon strand is closed and the software path wins.
- If <30% do, the new-ROM argument returns.

---

# 1. How the understanding evolved

The investigation began as a global hunt for billion-dollar opportunities. Hardware and software were scanned first, then software alone. **OT and embedded post-quantum migration** stood out as an under-served problem with a regulatory clock. Five deep passes and one verification build followed. Each pass attacked the one before it.

| Pass | Central belief | What overturned or refined it |
|---|---|---|
| **1. First-principles reinvention** | Migration is more than algorithm swaps. It needs a managed **Industrial Trust Plane** of five planes (root, authority, session, knowledge, assurance), and root succession is the open problem. | Pass 2 found root succession *is* solved in outline (TUF/Uptane, RFC 5011, UEFI CA rotation, OpenTitan ownership transfer, DICE). It also found four missing layers: provisioning, time, revocation/decommissioning, governance. |
| **2. Audit and foundations** | The remaining gaps are narrow: immutable ROM verifiers, weak-device revocation, offline time, orphaned fleets, and **HNDL-to-authority** (a forgeable classical root can hijack the transition itself). The standalone market is small: $0.38–1.88B global. | The verification lab caught arithmetic slips (market sum, masking factor, IKE fragmentation framing, TLS downgrade nuance). Pass 3 reframed the whole problem. |
| **Verification lab (51 interactive scenes)** | Every quantitative claim must be recomputable. | Confirmed the FIPS/SP sizes, LoRa frame counts and SV budgets. Exposed the discrepancies listed in Part 14. |
| **3. Invention pass** | The root problem is *authority continuity*. The top invention is a hash-only, multi-family **Authority Continuity Kernel (ACK)** committed in ROM/OTP, plus symmetric-first operation, threshold succession, time-free validity and a neutral custodian. 110 hypotheses, 32 combinations, 11 architectures, a weighted top 20. | Pass 4 found three arithmetic errors, a self-contradiction in the "existing ROM" variant, deployed prior art making new ROM unnecessary, and two large problem areas absent from the model: **update non-adoption** and **classical side doors**. |
| **4. Second-pass challenge** | The thesis survives but moves layer. The bottleneck is adoption plus uninventoried authorisation paths. Build on existing standards (NSIB-style locked stages, FDO, SP 800-230, TPM 2.0 v1.85, CycloneDX). | This synthesis: reconciles the passes, adds a device-class model, a five-kinds-of-change framing and new hypotheses (Part 13). |

**The three hidden assumptions that, once challenged, changed most:**

1. *"The cryptographic root is the scarcest resource."* It isn't. The scarcest resources are **maintenance windows, people who understand the device, and authorisation paths nobody inventoried**.
2. *"Changing the immutable verifier requires new silicon."* Often it doesn't. A maker-defined locked flash region can be the immutable root, and its integrity comes from the **lock**, not from a classical signature.
3. *"Secure boot is the authority chain."* It is one of at least six chains. The others are debug, RMA/lifecycle, ownership, factory provisioning and configuration. The attacker uses the cheapest.

---

# 2. Foundations: the threat, the mathematics, the machines

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
| NIST IR 8547 (final, 27 Oct 2026) | Quantum-vulnerable public-key algorithms deprecated after 2030, disallowed after 2035, at all key sizes. NIST staff said the 2035 disallowance was not aimed at hybrid modes. | [2nd] (NIST PDF not opened) |
| US Executive Order of 22 June 2026 ("Securing the Nation Against Advanced Cryptographic Attacks"; EO 14412 per two secondaries) and OMB M-26-15 | PQC key establishment for high-value assets by 31 Dec 2030; signatures by 31 Dec 2031; migration plans within 120 days | [2nd]/[F] (OMB PDF cited) |
| NSA CNSA 2.0 (FAQ v2.1) | Firmware signing: PQ preferred 2025, exclusive 2030. Names LMS/XMSS, and v2.1 excludes HSS and XMSS^MT. "Starting in 2027, no new product for NSS should have a burned-in root of trust relying on a non-QR primitive." | [2nd] |
| EU Cyber Resilience Act | Reporting obligations from 11 Sep 2026; full obligations from 11 Dec 2027. Support period ≥5 years (Art 13(8)); updates available ≥10 years (Art 13(9)). **Article 14 reporting also covers products already on the market.** | [F]/[2nd] |
| India DST Task Force roadmap (2026) | Critical information infrastructure: foundations 2027, priority migration 2028, completion 2029. Power, telecom and ONGC named as urgent. Recommends containing "classical-only systems within controlled enclaves where immediate migration is not feasible". Test labs by Dec 2026. | [2nd] (DST PDF cited) |
| UK NCSC, Australia ASD, EU coordinated roadmap | Comparable 2030–2035 horizons | Cited earlier, **not rechecked** |

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

**The structural insight the passes converged on [I]:** hash functions are the only primitive shared by every NIST PQ family. ML-KEM and ML-DSA use SHAKE/SHA-3; LMS and SLH-DSA-SHA2 use SHA-256. **A hardware hash engine is therefore the universal post-quantum accelerator**, and hash-based verification is the most conservative long-term anchor. But SHA-2 and SHA-3 are *different* assumptions. A "hash-only" design that uses only SHA-256 is itself a monoculture (Part 5.3).

## 2.4 The machines: what fits where

**Embedded benchmarks and their reliability**

| Measurement | Value | Source | Status |
|---|---|---|---|
| ML-DSA-44 signing on RP2040 (M0+) | mean 158.9 ms, p99 584.2 ms, max 1,156.8 ms over 10,000 runs; iteration count recoverable from wall-clock time | arXiv 2603.19340 | [D] |
| ECDSA P-256 vs ML-DSA-44 verify on RP2040 | **321 ms vs 44.0 ms** | same | [D]: PQ verification can be *cheaper* than classical |
| ML-DSA-44 signing stack | 44,832 B (pqm4, M4F) / 50.6 KB reference C; ML-DSA-87 119.6 KB | pqm4; inherited | [D]. **Conflict:** the RP2040 paper snippet reports 8.4–8.9 KB memory. Unresolved; it may count a different quantity |
| ML-KEM-768 decapsulation | 22.0 ms on M0+, 14.2 KB stack; wolfSSL 8.3 ms on a newer STM32 (clock not stated) | inherited; [V] | — |
| Masked vs unmasked ML-KEM decapsulation | 2,978,441 vs 707,827 cycles = 4.21× | [C] from quoted cycles; the 3.5× figure stated elsewhere does not reproduce | — |
| LMS verify, SHA-256, Cortex-M4 (Campos et al., ePrint 2020/470) | **2,658,884 cycles at W4 (Winternitz value 16), h = 10, ~1,044 B stack; 23,252,036 cycles at W8 (value 256), h = 5** | [D] | Earlier passes mislabelled "w=16" and paired the W4 cycles with the W8 size (fixed in Part 14) |
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

---

# 3. The problem universe, compressed to its root causes

Across the passes, **90 distinct problems** were catalogued: 35 in the first problem universe (P1–P35) and 55 added by the second pass (N1–N55). Listing them one by one hides the structure, so they are reorganised here by **root cause**. A small number of causes explains almost everything, and each cause points at an intervention layer.

## 3.1 Nine root causes

The invention pass found seven root causes (R1–R7). The second pass showed that two of the largest problem clusters fitted none of them. Both are added here as **R8** and **R9**, and R1 is narrowed.

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

**Why R8 and R9 matter more than R1 [I].** R1 is real but its fix is cheap and partly deployable now (Part 6.1). R8 decides whether *any* fix reaches the field. R9 decides whether the boot-chain fix even protects the device: an attacker who can forge a debug certificate never touches the boot chain.

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
| N21 | Option-byte flash locks are vulnerable to fault injection | [I] |
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

## 3.3 Security problems created by security solutions

This was the least explored dimension before the second pass. Every recommended mechanism creates a successor problem, and the recommendations in Part 6 carry their own mitigations.

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

# 5. The solution space after two invention rounds and two red teams

## 5.1 How the solutions were generated

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

## 5.2 Status of every solution family after review

The full 110-item list is preserved in spirit but consolidated here. **Status:** ✅ build, 🔧 modified, 🔬 research only, ❌ killed.

**Roots and silicon**

| Idea | Status | Why |
|---|---|---|
| Multi-family committed manifest in OTP (ACK) | 🔧 → becomes the *locked continuity first stage* | The same idea without new ROM, deployable now on lockable parts |
| Hash-only ROM verifier in new silicon | 🔬 / procurement ask | Valuable for parts that cannot lock flash; silicon cycles are slow |
| Sunset latch as a new fuse | 🔧 → the floor rule | NSIB-style key-index invalidation already ships |
| Escrow leaf | 🔧 → slot 3 (operator or escrow key hash) | — |
| Pre-rotation (KERI-style) | 🔬 | Saves only 1.5–3× (Part 14) |
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

## 5.3 A formal rule the passes discovered: single-assumption safety

"Two families" turned out to be a loose notion. If the escrow leaf is LMS and the operational root is LMS, "LMS + escrow" survives a lattice break, but **both die together if SHA-256 breaks**. The second pass formalised the requirement. [I]

Let **A(k)** be the set of hardness assumptions that key k depends on:
- ML-DSA → {MLWE/MSIS, SHAKE}
- SLH-DSA-SHAKE → {Keccak}
- LMS-SHA-256 or SLH-DSA-SHA2 → {SHA-256}
- ECDSA → {ECDLP, SHA-2}

A transition rule is **single-assumption-safe** if no single assumption's failure leaves the attacker able to satisfy an authorising quorum. Equivalently: every quorum the rule accepts must contain keys whose assumption sets are **pairwise disjoint in at least two members**.

**Minimum robust set:** {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256}, held by at least two organisations. Its member assumption sets are {MLWE/MSIS, SHAKE}, {Keccak} and {SHA-256}. ML-DSA and SLH-DSA-SHAKE share Keccak, so the rule must pair them with care.

**Practical form [H].** Policy authors declare quorums, and a tool computes the minimal hitting sets of the assumption graph to reject any quorum that one assumption failure can satisfy. This is an automatable check (Part 13, idea I-4).

**A residual caveat [I].** Treating SHA-2 and SHA-3 as fully independent is a judgement call. They have different constructions (Merkle–Damgård vs sponge), but both are symmetric primitives studied by the same community. A cryptographer on the review board would discount the independence somewhat, not entirely.

---

# 6. The recommended architecture stack

Part 0 listed the stack. Here each element gets its thesis, mechanism, minimal and high-assurance forms, failure behaviour, resources, prior art and what it does **not** guarantee.

## 6.1 Continuity First Stage (replaces the Authority Continuity Kernel)

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
- Protection against an attacker who can fault the lock (E-A4 decides).
- A fix path for bugs in the first stage itself (N20). Hence it must be tiny, formally verified and implemented twice.
- Unlimited future: three slots give **one generation of headroom**, not infinite agility.

**Interim note on stateful signatures.** Until SP 800-230 is final, MV-1 uses LMS, which keeps the index-reuse hazard alive. The hazard is manageable for root signatures because they are rare: a few per year, inside an HSM with index reservation. Switch to SLH-DSA limited-use sets when final, except where CNSA 2.0 mandates LMS/XMSS.

**Prior art.** Nordic NSIB (locked stage, key hashes, monotonic index invalidation); ST OEMiRoT; OCP Hardware Secure Boot ("table of hashes" of public keys in eFuses; revocation OTP must not be mixed with anti-rollback OTP); wolfBoot (LMS/XMSS/ML-DSA, hybrid); Intel patents US 11405213 and US 12137169 (fast XMSS/LMS verification for secure boot); OpenTitan (SPHINCS+ and ML-DSA work).

**Novelty classification:** a meaningful combination (multi-class slots plus a cross-class floor rule plus an owner slot in a locked stage), *not* a patent-safe invention. Defensibility comes from being the open reference implementation, from formal verification, and from porting and assurance services.

## 6.2 Side-door closure

**Thesis.** Every classical authorisation path that can change code, keys, ownership or debug state is part of the root of trust, whether or not anyone designed it that way.

**Mechanism**
1. **Authorisation Surface Map** per part family. Enumerate debug, lifecycle/RMA, ownership, provisioning, configuration, licence and remote-access paths, with the algorithm and key holder for each (Part 13, I-1).
2. **Disable field debug** after commissioning. Handle RMA by board swap so that RDP-style permanent locks are not tempted down to weaker levels (N4).
3. **PQ debug credentials** for lab and RMA units only, bound to the device UUID so that one root break does not open the fleet (N2). Arm ADAC-style certificate chains carry PQ signatures.
4. **Lifecycle transitions** (TEST → PROD → RMA) authorised by the same multi-class rule as floor advances.
5. **Factory provisioning.** KEM-wrapped key injection, with per-device keys, and a provisioning log co-signed by the contract manufacturer and the OEM (N8).

**What it does not guarantee:** protection against physical invasive attacks on parts without tamper resistance.

## 6.3 Symmetric process-bus fabric

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

## 6.4 Ownership continuity via PQ FDO vouchers

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

## 6.5 Maintenance-window-aligned staging

**Thesis.** Cryptographic transitions fail because they arrive as unplanned work. Make them ride windows that already exist.

**Mechanism**
- The signed transition bundle is downloaded, verified and **staged dormant** in the inactive A/B slot long before the window.
- In the window, a single, short, pre-rehearsed activation step runs. The device then emits a **signed state report**: floor index, active slots, image hash and policy hash.
- Crypto-only changes are kept separate from functional changes, so they do not bundle with recertification (N48).
- Rehearse against a lab replica of the site, using the "migration twin" as an engineering practice.

**Why it matters.**
- Fewer than 30% of facilities patch on a schedule, and only 15% in routine windows. [2nd]
- The economic model in Part 9 shows the value lies in converting emergency work into planned work.

**What it does not guarantee.** It cannot help if no window comes before the threat. Attackers who learn the windows gain timing knowledge, so staged artefacts must be signed and attested.

## 6.6 Enclave containment with a dated exit

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

## 6.7 Fleet crypto-state evidence

**Thesis.** The missing feedback loop (Part 4.3) is closed by devices and observers reporting cryptographic state in **existing** formats, packaged as compliance evidence that someone already has to produce.

**Mechanism**
- Signed state reports from devices that can sign them.
- Passive inference for silent devices: parse OPC UA OpenSecureChannel policies, TLS/DTLS supported groups, IKE proposals and GDOI.
- Output as CycloneDX CBOM, plus TCG/IETF RATS attestation where available.
- Mapped to CRA Article 14 reporting and India's critical-infrastructure inventory requirement.

**Commercial caution.** Passive parsing will be absorbed by incumbent OT-visibility vendors. The durable value is in **evidence that regulators accept**, not in the parser.

## 6.8 Workstation signing quorum

**Thesis.** Configuration, protection settings and safety-system logic (chain 6) need the same authority discipline as firmware.

**Mechanism**
- Settings files and project archives are signed by a 2-of-n quorum: an engineer and a reviewer, with keys in tokens or TPM v1.85.
- Devices that can verify do so.
- Others are checked at the gateway against a signed manifest.

**Watch for:** workflow friction, and AI configuration assistants bypassing the quorum (N47).

## 6.9 Complexity removed versus introduced

| Design | Components | Trust relationships | New dependencies | Device resources | Maintenance |
|---|---|---|---|---|---|
| Earlier ACK (new ROM) | ROM + OTP manifest + latch + escrow leaf | 4–5 | MCU vendor ROM cycle, licensing | 32 B OTP + fuses | Licence management |
| **Continuity First Stage (MV-1)** | Locked stage + 3 hashes + floor | 3 | Lock integrity | ~13 KB flash, 96 B | Open project; needs a maintainer foundation |
| Threshold custodian (earlier) | Utility + signers + legal entity | 3+ organisations | Legal, liveness | — | High |
| **FDO-PQ vouchers** | Voucher files + contract | One chain | FDO | KB-scale, off-device | Low |
| Time-free validity layer (earlier) | Library + metadata profile | — | — | Small | Medium |
| **Index floor (now)** | A counter + a rule | — | — | Bytes | Negligible |

**Net [I].** The redesign moves complexity into **contracts and existing standards that already have owners**, rather than inventing new organisations and silicon.

## 6.10 Long-term lifecycle behaviour

Assumptions: a CRQC is plausible between 2030 and 2040, CRA support lasts 5 years, and assets live 25 years.

| Architecture | 5 years | 10 years | 20 years | 40 years |
|---|---|---|---|---|
| Classical legacy | Containable | Side doors forgeable if a CRQC exists | Replace | — |
| Continuity First Stage | Fine | One floor advance used | Slot exhaustion possible | Replace; hash conservatism helps |
| Symmetric fabric | Fine | KDC refresh | Platform replaced | Protocol replaced |
| FDO-PQ ownership | Fine | OEM exits; vouchers used | Voucher format migration | Unknown |
| Enclave | Fine | Boundary refresh | **Becomes a permanent risk** unless exited | — |

---

# 7. Allocating security by device class

One universal architecture is inefficient. A battery sensor and a protection relay do not need the same cryptography. The danger is the opposite mistake: a **weak class becomes a hidden path into a strong one**. The class model below is this synthesis's proposal [H]. It builds on the second pass's recommendation of "hash engines for new designs, enclaves for legacy".

## 7.1 The classes

| Class | Typical devices | What it must do | What it must never do | Mechanisms |
|---|---|---|---|---|
| **C0: Inert** | Legacy sensors, drives, old RTUs with no crypto or no updates | Nothing cryptographic | Hold authority over anything | Enclave, passive inventory, replacement date |
| **C1: Symmetric-only constrained** | LoRaWAN or 802.15.4 sensors, M0-class nodes | MAC its data with a **diversified** key | Sign; share a fleet key | Commissioning-time enrolment (physical or KEM via a gateway); hash-verified updates if updatable |
| **C2: Verify-capable controller** | PLCs, RTUs, IEDs on M4/M33/A-class parts | Verify firmware and authority; decapsulate once at enrolment | Hold signing keys; allow field debug | Continuity First Stage, symmetric fabric member, signed state report |
| **C3: Safety-critical** | Protection relays, SIS logic solvers, interlocks | Everything C2 does, with crypto confined to boot and update | Run public-key operations in the control loop; fail closed into a hazard | C2 plus last-known-good, crypto partition, quorum-signed settings |
| **C4: Concentrators** | Gateways, KDCs, data diodes, engineering workstations, historians | Full PQ stacks, TLS/IKE hybrids, attestation | Become a single point of fleet-wide trust | TPM v1.85 identity, dual-vendor, witnessed logs |
| **C5: Authorities** | Release-signing HSMs, voucher holders, debug-credential issuers | Sign, under a multi-class quorum | Hold single-family authority alone | HSMs, index reservation (LMS) or SLH-DSA, transparency logs |

## 7.2 The anti-weak-path invariants

These are what keep the tiering honest.

1. **Dominance rule.** No device of a lower class may hold authority, keys or configuration rights over a device of a higher class. A C1 sensor's key never opens a C3 relay's settings.
2. **Diversification rule.** Any symmetric key below C4 is unique per device and derived from a diversification key held only at C4 or C5.
3. **Boundary rule.** Every C0 and C1 device sits inside a zone whose boundary is C4. Crossing the boundary requires PQ-protected channels.
4. **Authority isolation.** C5 keys never touch C4 networks online. Signing happens in HSMs, with offline or witnessed transfer.
5. **Promotion rule.** A device can move to a higher class only by replacement or by a quorum-signed re-commissioning. It can never move by configuration alone.

## 7.3 Three allocation models compared

| Model | Description | Cost | Complexity | Security boundary | Long-term maintenance |
|---|---|---|---|---|---|
| **Universal** | Every device runs the full PQ stack | Highest; infeasible for C0/C1 | Uniform, but forces impossible requirements | Clear on paper, unrealised in practice | Every device migrates every generation |
| **Tiered (recommended)** | Classes C0–C5 with invariants | Proportional to risk | Moderate; needs class assignment | Explicit at zone boundaries | Most migrations happen at C4/C5 |
| **Dynamically adaptive** | Devices change their behaviour with the threat level, for example strict hybrid after an alert | Medium | High; new failure modes | Can drift; needs verified policy | Hard to certify for C3 |

**Recommendation [I].** Use the tiered model, with one adaptive element: **floor advances and policy tightening are the only adaptive actions**, and they are quorum-signed and staged. Adaptive behaviour inside C3 is excluded, because safety cases need predictable behaviour.

---

# 8. Seven deployment scenarios, end to end

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

### Scenario E: the OEM disappears
- **With slot 3:**
  1. The escrow trigger fires.
  2. The operator presents the voucher chain.
  3. REPLACE_SLOT3 then hands authority to the operator's key, via the floor rule with a remaining-class signature.
  4. The operator, or a contracted maintainer, signs future images.
- **Without slot 3:** replacement or an enclave. There is no cryptographic path.
- **Failure points:** voucher files lost; contracts silent on the trigger.
- **Lesson:** OEM-exit protection is bought at manufacture, not later.

### Scenario F: an emergency cryptographic event
- **Example:** a lattice break, or compromise of a signing key in one class.
- **Steps:**
  1. Sign a floor advance with the surviving class (SLH-DSA-SHAKE or LMS-SHA-256).
  2. Stage the bundle.
  3. Activate in the next window. Use an emergency window only for exposed, high-consequence assets.
  4. Collect signed state reports.
- **Cost driver:** unplanned downtime. ABB's 2023 survey median is $124,669 per hour, US about $103k [V, plant-oriented].
- **Remaining risk:** devices with only one class. They can only be contained.

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

**Survives real deployment:** the locked stage, side-door closure, the symmetric fabric, voucher escrow, window staging and enclaves.

**Works only on paper today:** neutral custodians, threshold ML-DSA succession, a separate time-validity layer, attestation-priced insurance, and sector root-of-roots.

---

# 9. Economics: who pays, why they wait, and what makes them act early

## 9.1 The actors

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

## 9.2 The market, corrected and demoted

- **Bottom-up US components:** $113.5M–$565M per year. Global at a 30% US share: $113.5M ÷ 0.30 = **$0.38B** to $565M ÷ 0.30 = **$1.88B**. A standalone vendor at 10% share earns **$38M–$188M per year**. [E; inputs unverified]
- **Adjacent transactions** (cited, not re-verified): Nozomi Networks ~$883M; Venafi ~$1.54B; CyberArk ~$25B; Accenture's three cyber acquisitions ~$4.175B combined; Keyfactor >$200M ARR.

**Interpretation.** A pure "OT-PQC vendor" is a niche. The large outcomes in adjacent markets came from owning **machine identity** or **OT visibility** platforms. PQ migration is a **feature and an occasion**, not a market by itself. **Do not use these numbers for fundraising.**

## 9.3 The early-action model: converting emergency work into planned work

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

## 9.4 Value for customers who do not care about quantum computing

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

## 9.5 Business models, ranked by fit

1. **An open first-stage reference plus paid porting and assurance** to OEMs (formal verification, fault testing, certification support).
2. **A compliance-evidence product:** CRA Article 14, India critical-infrastructure inventories and IR 8547 transition reporting.
3. **Window-aligned migration engineering** services to operators, especially Indian power, telecom and oil and gas facing the 2027–2029 dates.
4. **Procurement-clause libraries and test-lab services.** India's roadmap calls for labs, and owners cannot verify OEM claims without them (N32).

**Weak fits:** per-device subscriptions (operators resist recurring per-device cost in OT); a custodian utility (liability without demand); new-ROM licensing (slow and commercially irrelevant if locked flash suffices).

---

# 10. The design debate and where it converged

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

**Convergence**
- **Agreement:** a hash-based locked first stage; closed side doors; a symmetric process bus.
- **Unavoidable trade-off:** diversity (purist) versus attack surface (minimalist). **Resolution:** diversity *in slots and assumption classes*, with one formally verified verifier per class, and only the first-stage verifier immutable.
- **Clearly superior point:** the pragmatist's adoption argument. It reorders every priority.
- **Class-dependent:** hash engines for new designs, enclaves for legacy, crypto confinement for C3.
- **Unresolved, no responsible conclusion yet:** whether assessors accept crypto partitioning (E-C1); whether operators accept escrow and custodians; whether option-byte locks survive fault injection (E-A4).

---

# 11. Validation programme: experiments ordered by information value

These merge the invention pass's experiments (E1–E10) with the second pass's experiments (E-A/B/C). They are reordered so that **cheap tests that could kill whole strands run first**. All of them run on owned or authorised equipment only; none touch live critical infrastructure.

| Order | ID | Question | Method | Cost | Supports / disproves | Decision it drives |
|---|---|---|---|---|---|---|
| 1 | **E-A1** | What share of industrial MCU families support a lockable, maker-defined immutable first stage? | Desk survey: ST, NXP, Renesas, Microchip, TI, Infineon, Nordic, Silicon Labs, Espressif, GigaDevice | ~2 weeks | ≥50% supports / <30% disproves | Locked flash vs new ROM |
| 2 | **E-A3** | Which authorisation paths (debug, lifecycle, ownership, provisioning, licence) are classical, per family? | Documentation review plus lab confirmation | ~3 weeks | — | Side-door map; procurement clauses |
| 3 | **E-A2** | What does verification cost for LMS W4/W8, the SP 800-230 sets and ML-DSA-44 on M0+ and M33, with and without hardware SHA? | Owned boards; publish neutral benchmarks | ~4 weeks | ≤100 ms / >300 ms | Algorithm and parameter choice; settles the RP2040 memory conflict |
| 4 | **E-B4** | Can a floor be burned against the owner? | NSIB-style lab demonstration | ~2 weeks | Exploitable / not | Validates the floor rule |
| 5 | **E-B2** | Is the single-assumption rule sound, and do the state-machine invariants hold? | TLA+ and Tamarin models (the invention pass's E2) | ~6 weeks | No path / counterexample | Slot and quorum design |
| 6 | **E-A4** | Do option-byte flash locks survive voltage and EM glitching? | Fault injection on owned parts | ~6 weeks | Hold / fail | **The kill test for the lead architecture** |
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

**Highest consequence: E-A4.** If locks fail reliably, the lead architecture retreats to "new ROM or hash-only OTP checks" and the hardware architect wins the debate.

**Research priority scores** (1–5 each; total out of 20):

| Question | Importance | Uncertainty | Information value | Changes architecture | Total |
|---|---|---|---|---|---|
| E-A1 lockable share | 5 | 3 | 5 | 5 | 18 |
| E-A4 lock faults | 5 | 4 | 4 | 5 | 18 |
| E-B1 adoption | 5 | 5 | 4 | 3 | 17 |
| E-A3 side doors | 5 | 3 | 4 | 4 | 16 |
| E-A2 benchmarks | 4 | 3 | 4 | 4 | 15 |
| E-C1 assessors | 4 | 5 | 3 | 3 | 15 |

---

# 12. The long view: infrastructure meant to last 50–100 years

## 12.1 Three visions, updated after both challenge rounds

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

## 12.2 Design principles for a device meant to last decades

These consolidate what survived every pass. [I]

1. **Make immutable only what is minimal and conservative:** a hash verifier and commitments. Never an algorithm-specific public-key verifier alone.
2. **Commit to diversity at birth.** At least two assumption classes, held by at least two organisations, with one slot reserved for the eventual owner.
3. **Separate booting from re-authorising.** Booting needs one valid class. Changing authority (floor, slots, owner, lifecycle) needs more.
4. **Never tie authority to a calendar.** Use counters and epochs. Time may tighten privileges but must never stop a safety function.
5. **Keep state monotonic and non-restorable.** Anything that a backup can rewind is not security state.
6. **Delete capabilities you cannot protect.** Field debug, remote paths to offline devices and per-frame public-key work.
7. **Keep public-key work rare.** Do it at enrolment and authority changes; run symmetric operations everywhere else.
8. **Every authorisation path is part of the root of trust.** Map it, or assume an attacker will.
9. **Design for the change to be installed.** Staged, dormant and window-aligned, separate from functional change, with signed confirmation.
10. **Plan the device's death on day one.** Decommissioning revokes, destroys and records.
11. **Make the device say what it trusts.** Signed state is the sensor of the control loop.
12. **Prefer contracts and existing standards to new organisations.** New organisations are new single points of failure with unclear liability.

## 12.3 The question at the heart of it

*How does a device know an update is trustworthy when the technology that originally established its trust is no longer trustworthy?*

**Answer:** only through something committed **before** that technology failed and **independent** of it. That is a commitment to a key from a different assumption class, or a person physically present. Everything else is a delivery mechanism. This is why the most consequential engineering decision is made at manufacture, and why every year of shipping single-class devices enlarges the set of devices that can never be rescued. [I]

---

# 13. The innovator's notebook: new ideas from the synthesis

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

---

# 14. Corrections ledger: what we got wrong and fixed

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
| 8 | The Trust Plane is complete | **Missing** provisioning, time, revocation/decommission and governance | Pass 2 | Superseded by the stack in Part 6 |
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
| 19 | Top-20 ranking | Built without weight-sensitivity analysis; **rebuilt** and tested under two weightings | Pass 4 | Part 15.2 |
| 20 | ML-DSA-44 signing stack = 50.6 KB | The RP2040 study snippet says 8.4–8.9 KB memory. **Unresolved** | Pass 4 | E-A2 must measure |

**Meta-lesson [I].** The errors clustered in places where **two numbers from different contexts were paired**: a size from one parameter set with cycles from another, or a sum quoted rather than computed. The defence is mechanical: recompute everything, and keep a parameter set attached to every number.

---

# 15. Open questions, rankings and the roadmap

## 15.1 Questions that could still change the architecture

| Question | Current belief | Why it may be wrong | Experiment | Decision it drives |
|---|---|---|---|---|
| What share of industrial MCUs can lock a first stage? | Many (Nordic, ST) | Two vendors are not an industry | E-A1 | Locked flash vs new ROM |
| Do flash locks resist fault injection? | Weaker than ROM, maybe adequate | Option bytes are a known glitch target | E-A4 | Lead architecture survives or retreats |
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

## 15.2 Revised ranking of what to build

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

## 15.3 Roadmaps with decision gates

**Roadmap A: practical entry (0–9 months)**
- **0–3 months:**
  - Run E-A1, E-A3 and E-A2.
  - Build the side-door audit kit and the Authorisation Surface Map format.
  - Interview 5 OEMs and 5 operators, including Indian power, telecom and oil-and-gas critical infrastructure.
  - **Gate:** ≥50% of MCU families lockable → continue. <30% → pivot to silicon procurement asks and hash-only OTP designs.
- **3–9 months:**
  - Prototype the first stage on two families (an STM32U5/H5-class part and an nRF5340), using LMS W4 with three slots and the floor rule.
  - Build the TLA+ model and run E-A4, E-B4 and E1.
  - **Gate:** locks hold and verification takes ≤100 ms → continue. A reliable lock bypass → retreat to the ROM/OTP strategy.

**Roadmap B: strategic expansion (9–24 months)**
- An open release of the first stage with formal verification and a second independent implementation.
- An FDO-PQ profile contributed to the FIDO Alliance.
- A window-staging pilot with signed state reports.
- The compliance-evidence product (CRA Article 14, India critical-infrastructure inventories).
- A pilot with an Indian critical-infrastructure operator.
- **Gate:** one paying pilot. If incumbents ship the evidence product first, drop it and partner.

**Roadmap C: ecosystem transformation (2–10 years)**
- Procurement standard text: hash engine, ≥3 slots over ≥2 classes, PQ debug and vouchers, no field debug.
- Submissions to IEC 62443-4-2, IEC TC57 WG15 (GDOI-PQ) and national lab criteria.
- A maintainer foundation for the open first stage, so that it does not become the next orphan.
- Five or more MCU families supported. SP 800-230 sets adopted when final.
- **Gate:** two OEM adopters shipping it in products.

---

# 16. Appendices

## 16.1 Verified number card

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

## 16.2 Glossary

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

## 16.3 The new opportunity map

| Type | Opportunity |
|---|---|
| Technology | Locked hash first stage; SP 800-230 limited-use SLH-DSA; SHA-2 + SHA-3 hash engines; graded-authority rule; assumption-graph policy compiler |
| Product | Side-door audit kit and Authorisation Surface Map; compliance-evidence product; window-staging tooling; decommissioning receipts |
| Infrastructure | Open first-stage foundation; FDO-PQ profile; GDOI-PQ profile; neutral benchmark and conformance lab |
| Research | Lock fault resistance; single-assumption theory; floor-burn defences; crypto-confinement safety arguments; fleet algorithm diversity |
| Commercial entry | OEM porting and assurance; Indian critical-infrastructure pilots (2027–2029 deadlines); test-lab services; procurement clause libraries |

## 16.4 Method log: how the investigation was run

1. **Opportunity scan.** A global, then software-only, search for billion-dollar opportunities surfaced OT and embedded post-quantum migration as under-served and deadline-driven.
2. **First-principles pass.** Fifteen dimensions from quantum to economics produced the Industrial Trust Plane and H1–H22.
3. **Audit pass.** This established the foundations, the protocol atlas, the root-of-trust survey, a reassessment of H1–H42, the commercial challenge and the future outlook.
4. **Verification lab.** A 51-scene interactive build with live assertions recomputed every number. Discrepancies were disclosed rather than hidden.
5. **Invention pass.** Eight independent engines, then 110 hypotheses, 32 combinations, 11 architectures, a red team, weighted ranking, blueprints, experiments and three visions. About 60 sources.
6. **Second-pass challenge.** A traceability audit, a challenge register (C1–C22), 55 new problems, ten stakeholder perspectives, a layer matrix, simplification, second-order consequences, a technology register, an eight-position debate, redesigns, deployment scenarios, economics and a challenge board. About 70 sources.
7. **This synthesis.** Reconciled all passes, re-verified all arithmetic, added root causes R8 and R9, the six-chain authority graph, the device-class model with anti-weak-path invariants, the innovator's notebook (I-1 to I-12) and the consolidated corrections ledger.

**Where this synthesis made its own judgement calls [I]:**
- It ranked R8 and R9 above R1.
- It treated the device-class model as a recommendation, although no pass validated it.
- It kept stateful LMS for the interim first stage, despite the second pass's "eliminate stateful custody", because SP 800-230 is still a draft.

## 16.5 Source register (decisive sources from the two most recent passes)

The source lists of the earlier passes are not reproduced here. These are the sources on which the current conclusions rest.

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

---

## Closing note

The investigation started by asking how to migrate industrial cryptography to post-quantum algorithms. It ends with a different question: **how do you build machines that can accept change, safely, long after the people and companies who made them are gone?**

Post-quantum migration is the first hard deadline that question has faced. The answer is small rather than grand:
- a few kilobytes of locked, hash-based code;
- three 32-byte commitments spanning independent assumptions;
- one rule that makes changing authority harder than booting;
- the courage to delete debug ports and remote paths nobody can protect;
- contracts that move authority to the owner before the maker disappears;
- changes that arrive during maintenance windows rather than as emergencies.

Everything else is delivery. The next step costs two weeks: find out how many industrial MCUs can lock their first stage.

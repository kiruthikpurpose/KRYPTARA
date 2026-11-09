# Post-Quantum Migration for OT and Embedded Infrastructure, Re-examined: Audit, Foundations and a Revised Thesis (November 2026)

The prior report got its central idea right: in operational technology (OT), the post-quantum problem is mostly about who may change a device's firmware, keys and identity, not who can read its traffic. Its claim that renewing a deployed root of trust is an unsolved frontier does not survive audit. Quorum-based root succession is already standardised and deployed in TUF/Uptane (automotive), automated trust-anchor rollover (RFC 5011) has run twice on the DNS root, and OpenTitan offers in-silicon ownership transfer. What remains unsolved is narrower and more physical:
- putting multiple independent post-quantum verifiers into silicon before it ships;
- revoking keys on devices too weak to process rotation metadata;
- validity and time on offline devices;
- governing orphaned fleets.

The prior commercial thesis, an "Industrial Trust Plane" worth low single-digit billions a year, is roughly an order of magnitude too optimistic for a standalone vendor.

## TL;DR

- **Policy verified.** NIST's final IR 8547 (27 Oct 2026) deprecates every quantum-vulnerable RSA/ECC/DH algorithm after 2030 and disallows them after 2035, regardless of key size. It lets hybrid key establishment be FIPS 140-validated if one input is approved. "Deprecated" still means usable with documented risk acceptance. The binding dates are federal (EO 14412, OMB M-26-15): PQC key establishment by 31 Dec 2030 and signatures by 31 Dec 2031 for high-value and high-impact systems.
- **The technical thesis survives, refined.** Protect authority first: immutable boot verifiers in new silicon, and the transport of long-lived symmetric keys (where "harvest now, decrypt later" becomes "forge later"). The real-time data path is mostly symmetric, but not everywhere. OPC UA, (D)TLS 1.2 profiles such as CIP Security, Zigbee Smart Energy and ECC-based metering need protocol redesign, not just new key management.
- **The commercial thesis shrinks.** Root-rotation protocols exist, and both 2026 mega-rotations (UEFI, DNSSEC) went to classical keys and took years. Value is being captured by PKI, HSM, silicon and OT-visibility incumbents. The best opportunities are a stateful-hash-signature custody and secure-boot toolkit, passive crypto-posture content for OT-visibility platforms, and services, most likely ending in acquisition.

## Key Findings

1. **IR 8547 is primary-confirmed.**
   - Tables 2 and 4 mark ECDSA, EdDSA, RSA, DH and MQV "Deprecated after 2030, Disallowed after 2035" at all approved strengths.\[1\]
   - Hybrid key establishment "can be FIPS 140-validated, even if other inputs are disallowed".\[1\]
   - "The security properties of hybrid signatures are complex and need to be carefully analyzed."\[1\]
   - Three sentences the prior report missed matter more for OT:
     - devices that cannot update verification code "should be designed to require quantum-resistant signatures";\[1\]
     - authentication "may continue to use quantum-vulnerable algorithms until" a cryptanalytically relevant quantum computer (CRQC) exists;\[1\]
     - systems that cannot support PQC "should be identified and prioritized for replacement or decommissioning."\[1\]
2. **Root succession is a solved protocol but an unsolved engineering problem.** Uptane requires Root metadata version N+1 to be signed by a threshold of version N keys and a threshold of version N+1 keys, which is the prior hypothesis H1 in all but name.\[2\] Uptane also admits that partial-verification ECUs, which skip Root metadata, have "no truly secure way to invalidate a signing key".\[3\]
3. **2026's largest trust-anchor rotations stayed classical.**
   - Microsoft's 2011 KEK expired 24 June 2026, the UEFI CA 27 June and the Windows PCA 19 October. The replacement is "Microsoft Corporation KEK 2K CA 2023".\[4\]\[5\]
   - The DNS root KSK rollover was scheduled for 11 October 2026 after 21 months of pre-publication. It is RSA-2048 to RSA-2048, and the next algorithm roll (expected around 2029) is to ECDSA.\[6\]
4. **Resource estimates for breaking public-key cryptography collapsed in 2025–26; hardware remains far away.**
   - Estimates:
     - Gidney (May 2025): RSA-2048 with fewer than 1 million noisy qubits in under a week.
     - Google (Mar 2026): ECDLP-256 with about 1,200 logical qubits and 90M Toffoli gates, under 500k physical qubits, in minutes.\[7\]
     - Iceberg's Pinnacle preprint: RSA-2048 with fewer than 100k physical qubits.\[8\]
     - Alice & Bob (Oct 2026): 22,593 cat qubits, 3.14 days.\[9\]
   - Hardware: at its November 2025 launch, Quantinuum said Helios ran "48 fully error-corrected logical qubits at a remarkable 2:1 encoding rate" (98 physical qubits). Its Apollo system, planned for 2029, targets hundreds of logical qubits.
   - Elliptic-curve cryptography, which dominates embedded systems, is now the cheaper target.\[10\]
5. **No industrial protocol has a standardised PQC profile.** That covers OPC UA, IEC 62351, DNP3-SAv6, CIP Security, AUTOSAR and ERTMS. DNP3-SAv6 is unballoted, with its IEEE project reportedly extended to December 2027.\[11\] AUTOSAR R25-11 still says TLS lacks post-quantum asymmetric cryptography.\[12\] CIP Security is "standardized on TLS 1.2 and DTLS 1.2".\[13\]
6. **Embedded PQC is real but uneven.**
   - wolfBoot supports ML-DSA, LMS/HSS and XMSS.\[14\]
   - MCUboot added LMS only in a simulator-only pull request (May 2026); its imgtool offered no post-quantum key type as of 2 Nov 2026.\[15\]\[16\]
   - Thales Trusted Cyber Technologies says its Luna T7 module (FIPS 140-3 certificate #5450, firmware 7.15.1, August 2026) is "the world's first HSM to include all the NSA… CNSA Suite 2.0 PQC algorithms within a FIPS 140-3 validation". That covers ML-DSA, ML-KEM and LMS at Level 3.
7. **The market is consolidating into incumbents.**
   - Mitsubishi Electric paid USD 883 million for the 93% of Nozomi Networks it did not already own (9 Sep 2025 filing). The deal closed on 28 January 2026. Nozomi's net revenue was $74.7M in 2024 (about 11.8×) and $101.7M in 2025.
   - CyberArk bought Venafi for "approximately $1.54 billion" (about $1 billion cash and $540 million shares; SEC 6-K, 1 Oct 2024). Palo Alto Networks then agreed to buy CyberArk at "approximately $25 billion" equity value and closed on 11 February 2026 for $2.3 billion in cash and 112 million shares.
   - Accenture (newsroom, 18 Jun 2026) took a majority stake in Dragos and bought runZero and NetRise at a "combined enterprise value of approximately $4.175 billion". The three carry about $208M ARR, up 53% year on year. NetRise closed 31 Jul, Dragos 16 Sep and runZero 17 Sep 2026.
   - Keyfactor "exceeded $200 million in annual recurring revenue in the beginning of Q3 2026", growing more than 35% year over year (9 Sep 2026).

---

# PART I — Audit of the Previous Report

**Correct:**
- The authority framing.
- The "frozen cryptography" diagnosis: ROM algorithms, parser buffers, recertification.
- The preference for hash-based roots. NIST now names LMS/XMSS "for applications like software and firmware signing" and rates LMS SHA-256/192 Category 3, above ML-DSA-44's Category 2 (which drops to Category 1 with a weaker RNG).\[1\]
- Scepticism toward QKD.

**Missed:**
1. Prior art for root succession: TUF/Uptane thresholds, RFC 5011 hold-downs, OpenTitan ownership transfer, the 2026 UEFI rotation.
2. **HNDL-to-authority.** Long-lived symmetric authority keys moved under RSA/ECDH can be decrypted later while still valid. Examples: DNP3 SAv5 asymmetric update-key change, OPC UA password encryption, ETCS KMC delivery. Harvest-now-decrypt-later then becomes forgery.
3. **The TLS 1.2 trap.** Hybrid groups are standardised for TLS 1.3, so TLS 1.2 profiles need a version migration first.
4. NIST's authentication carve-out (§3.1.2).\[1\]
5. Rollover telemetry: DNSSEC's 2017 roll paused a year on RFC 8145 signals, and OT has no equivalent.\[17\]\[18\]
6. Sectors: medical, avionics/space, smart metering, rail key management, national standards.
7. No sourced market inputs.

| # | Prior claim | Verdict | Finding |
|---|---|---|---|
| 1 | IR 8547 final 27 Oct 2026 | Confirmed | CSRC lists Final 10/27/2026; draft withdrawn same day\[19\]\[20\] |
| 2 | All quantum-vulnerable PK deprecated after 2030, disallowed after 2035, any size | Confirmed | Tables 2 and 4\[1\] |
| 3 | Draft's 128-bit carve-out dropped | Confirmed, nuanced | P-256/RSA-3072 now deprecated after 2030 = usable with risk acceptance, not banned\[20\] |
| 4 | Hybrid KEM FIPS-validatable with one approved input | Confirmed | Verbatim; SP 800-56C to allow either ordering\[1\] |
| 5 | Hybrid-signature caution | Confirmed | §3.2.2 |
| 6 | ML-KEM-768 default | Confirmed | "NIST recommends using ML-KEM-768 as the default parameter set"\[1\] |
| 7 | EO 14412 / M-26-15 dates | Confirmed | Cited in IR 8547; one secondary source misnumbers the EO as 14409\[1\]\[21\] |
| 8 | FAR rule ~19 Dec 2026; CBOM elements ~19 Mar 2027 | Confirmed (secondary) | Derived from 180- and 270-day clocks\[22\]\[23\] |
| 9 | FN-DSA not final | Confirmed | "NIST is developing a FIPS"\[1\] |
| 10 | HQC selected | Confirmed | FIPS "under development"; "FIPS 207" and 2027 date not verified\[1\] |
| 11 | CSWP 39 upd1 final 29 Jun 2026 | Confirmed | NIST publications list\[19\] |
| 12 | Ascon = SP 800-232 | Confirmed | IR 8547 Table 7\[1\] |
| 13 | Composite signatures in RFC Editor queue | Confirmed (secondary) | Oct 2026 commentary\[20\] |
| 14 | No OPC UA PQC SecurityPolicy | Confirmed (absence) | Nov 2026 practitioner note\[24\] |
| 15 | IEC 62351-9 no PQC measures | Confirmed (secondary) | IEC 62351:2026 series pack (30 Jul 2026)\[25\] |
| 16 | DNP3-SAv6 "under final review before IEEE ballot" | **Corrected** | 2024 statement; P1815 reportedly extended through Dec 2027; SAv6 uses "elliptic curve algorithms"; no public evidence it is "designed to accommodate PQC"\[11\]\[26\] |
| 17 | CIP Security no PQC plans | Confirmed | TLS/DTLS 1.2\[13\] |
| 18 | AUTOSAR TLS not PQ-ready | Confirmed | Unchanged in R25-11\[12\] |
| 19 | ERTMS no PQC; SUBSET-137 TLS/ECC | Confirmed | 2024 Users Group guideline has no PQC\[27\] |
| 20 | pqm4 ML-DSA-44 sign stack 44,816 B; verify 8,912/2,712 B | Confirmed ±16 B | 2026 pqm4-framework run: 44,832 B sign, 8,912 B verify\[28\]\[29\] |
| 21 | M0+ only 1.81× slower than M4 | Explained | Both reference C; RP2040 ML-DSA-44 verify 5,849k cycles vs pqm4 assembly ~1.42–1.50M (~4×)\[28\]\[30\] |
| 22 | LMS H10 W8 sig ≈900 B | Confirmed by recomputation | 4+(4+24+26×24)+4+10×24 = 900 B; public key 48 B |
| 23 | LoRa ML-KEM-1024 62 packets; ~50% success | Confirmed by arithmetic | 3,136/51 → 62; 0.99^62 ≈ 0.54 |
| 24 | ML-KEM-768 = 18 802.15.4 frames | **Corrected** | ~100 usable B/frame → ~23–26 frames |
| 25 | Gidney 2025 | Confirmed, superseded | See Key Finding 4 |
| 26 | Thales OTCEP deck points | Unverifiable | Deck not obtained; Class A/B/C taxonomy not found elsewhere |
| 27 | wolfBoot ML-DSA-87 i.MX95 5.25 ms | Plausible, vendor | ~7 KB header growth = 4,627 + 2,592 B |
| 28 | CNSA 2.0, UK, Australia, Canada timelines | Not re-verified | EU roadmap confirmed secondarily |
| 29 | Analyst market sizes | Not used | Replaced by a bottom-up model |

**Over-optimistic conclusions:** "root renewal unsolved", "data path already symmetric", "billions per year", and H8 safety isolation as "the biggest lever" (no assessor evidence).

**Unasked questions:**
- Who signs configuration and logic downloads, as distinct from firmware?
- How many fielded devices verify any signature at all?
- What is the worst-case verification time against the watchdog?
- How do we learn device anchors without active scanning?

---

# PART II — Foundations

**Classical computing.** Bits are definitely 0 or 1, manipulated by deterministic gates. Cryptography uses problems that are easy one way and infeasible in reverse without a secret.

**Qubits.** A qubit's state is α|0⟩+β|1⟩, and measurement gives 0 with probability |α|².
- Superposition gives n qubits 2^n amplitudes, but you read only one outcome.
- Entanglement means joint states don't factor into per-qubit states.
- Interference is the real resource: algorithms arrange for wrong answers to cancel.
- A quantum computer is not "trying all answers"; it only helps on structured problems.

**Why RSA, DH and ECC fall.** Factoring N=pq and discrete logs (find x from g^x, or from xP on a curve) both reduce to finding the period of f(a)=g^a mod N.
- Shor's algorithm superposes over exponents, computes f (modular exponentiation is the costly arithmetic), applies the quantum Fourier transform so period information interferes into measurable peaks, then finishes classically.
- The cost is polynomial, so larger keys barely help.
- Grover's algorithm gives only a quadratic, poorly parallelisable speed-up on key search. NIST therefore keeps AES-128 at Category 1 and does "not expect to need to transition away" from symmetric standards.\[1\]
- *Exercise:* why does doubling an AES key defeat Grover, while doubling an RSA key barely slows Shor?

**What a CRQC needs.**
- Physical qubits err about once per 10³ operations, so they must be encoded into logical qubits.
- The surface code repeatedly measures parity checks on a 2D grid, and a real-time classical decoder corrects errors. Below threshold, logical error falls exponentially with code distance (Google Willow, 2024).\[31\]
- Quantinuum reported each distance step cutting logical errors 12× (Oct 2026).\[32\]
- Non-Clifford gates (T/Toffoli) need magic-state distillation factories, so Toffoli counts drive cost.
- qLDPC codes (Pinnacle) and cat qubits (Alice & Bob) cut overhead.
- Today's best is tens to about 100 logical qubits. A CRQC needs roughly 1,000–1,500 logical qubits running for hours to days.

**Why it matters now.** Mosca's inequality: shelf-life + migration time > time-to-CRQC means you are already late.\[1\] OT assets installed in 2026 run to 2041–2056, and a CRQC builder need not announce it.\[20\]

**Dissent at full strength.** Cloudflare argues post-quantum authentication "is needed only after Q-Day risk materializes".\[33\] OT practitioners note that attackers win via default passwords. Both are right for *online* authentication and wrong for verifiers frozen in silicon.

| Primitive | Role | OT example | Quantum status |
|---|---|---|---|
| AES | Encryption | GOOSE/SV options, LoRaWAN | Safe |
| HMAC/CMAC/GMAC | Integrity | DNP3-SA, SecOC, 62351-6 | Safe |
| SHA-2/3 | Fingerprint, Merkle trees | Image digests | Safe |
| DH/ECDH | Key agreement | TLS, IKEv2 | Broken by Shor |
| RSA/ECDSA/EdDSA | Signatures | Firmware, certificates | Broken by Shor |
| PKI | Binds identity to key | OPC UA, 62351 | Inherits its signature algorithm |
| DRBG | Randomness | Key generation | Safe if well seeded |

**Lattices.**
- LWE publishes b=A·s+e mod q with small noise e; recovering s is believed hard.
- Module-LWE uses polynomial rings (n=256, q=3329) for compactness. Module-SIS (find short z with Az=0) underpins ML-DSA.
- The Number-Theoretic Transform makes polynomial multiplication O(n log n). It is the hot loop.

**ML-KEM (FIPS 203).**
- Public key: (A, t=As+e).
- Encapsulation: u=Aᵀr+e₁, v=tᵀr+e₂+encode(m).
- Decapsulation: round v−sᵀu to recover m.
- The Fujisaki–Okamoto transform re-encrypts m and compares. Implicit rejection returns a pseudorandom key on mismatch.
- That comparison is where wolfSSL's 2026 flaw lay, so bugs there are key-recovery bugs.\[20\]\[34\]

**ML-DSA (FIPS 204), "Fiat–Shamir with aborts".**
- The signer commits w=Ay, hashes the message and the high bits of w into challenge c, and outputs z=y+cs.
- If z would leak s, the signer aborts and retries (rejection sampling). Signing time is therefore random: on RP2040, ML-DSA-44 signing averaged 158.9 ms, p99 584 ms, max 1,157 ms over 10,000 runs.\[30\]\[34\]
- The public key keeps only the high bits of t; a hint vector lets the verifier recover the high bits of w.
- Verification is deterministic and fast.

**FN-DSA (Falcon).** Hash-and-sign over NTRU lattices with discrete Gaussian sampling.
- Signature about 666 B.\[35\]
- Floating-point signing is hard to make constant-time; verification is integer-only.\[35\]
- Good for verify-only devices, hazardous for signers.

**Hash-based signatures.**
- A Winternitz one-time signature reveals hash-chain values; signing twice with the same key leaks enough to forge.
- Merkle trees authenticate many one-time keys under one root.
- LMS/XMSS (SP 800-208) are stateful: never reuse an index.\[36\]
- SLH-DSA (FIPS 205) removes state using FORS plus a hypertree, at 7,856–49,856 B per signature.
- Security rests only on hash functions.
- **Statefulness changes disaster recovery:** restoring an HSM backup or failing over can reuse indices. NIST notes "strict operational controls to track signature indices across distributed systems."\[1\]

**HQC** is a code-based backup KEM with larger sizes.

**Hybrid.**
- Key exchange: secrets combined in a KDF. SP 800-227 warns that combining only the secrets does not generally preserve CCA security; bind the ciphertexts too.\[20\]
- Signatures: dual signatures. ML-DSA+ECDSA loses strong unforgeability because ECDSA is malleable.\[20\]

*Thought experiment:* a transmitter and controller provisioned in the same factory never need public-key cryptography. PKC matters only for first contact and for renewing authority.

---

# PART III — The OT Ecosystem, End to End

```
[Vendor build HSM]-sign->[Firmware pkg]->[Portal/USB/Eng. workstation (TIA, Studio 5000, PCM600)]
L4 IT / vendor remote access <-DMZ-> L3 historian, OPC UA, jump host
L2 SCADA/DCS/HMI  -- IEC 104, DNP3, OPC UA, MMS --
L1 PLC/RTU/IED/safety PLC -- GOOSE/SV, PROFINET, EtherNet/IP, Modbus --
L0 sensors/actuators/WirelessHART/ISA100
Device: Boot ROM (key hash in OTP) -> bootloader -> RTOS/Linux -> app/safety image
```

The Purdue model is contested: cloud historians, IIoT gateways and remote access flatten it. Its durable lesson is that trust crosses levels via maintenance paths (updates, project downloads, backups, laptops), not control traffic.

| Authority | Holder | Algorithm today | Renewable? |
|---|---|---|---|
| ROM anchor (OTP hash) | Silicon vendor/OEM | RSA/ECDSA | Only with spare slots or revocation fuses |
| Firmware signing key | OEM HSM | RSA/ECDSA; LMS emerging | If the anchor allows |
| IDevID | OEM factory CA | ECDSA P-256 | Re-enrolment (EST/CMP/BRSKI) |
| Operational certificates | Operator CA/GDS | RSA/ECC | Yes |
| Logic/config download | Engineering tool + password | Often proprietary or none | Tool-dependent |
| Session/group keys | Master/KDC | Symmetric, sometimes RSA-transported | Yes |

**Walkthroughs:**

- **Substation IED or PLC.**
  - Lifecycle: ROM verifies against an OTP hash → OEM burns its signing-key hash and an IDevID → integrator loads SCL via the vendor tool (rarely signed) → optional TLS for MMS (62351-3/4) and GOOSE MACs with GDOI group keys (62351-9; most installed GOOSE is unauthenticated) → signed firmware pushed from the workstation, with safety retest.
  - When cryptography breaks: an ECDSA-only ROM can never verify a post-quantum signature, so the device must be replaced or have its delivery paths fenced. TLS can migrate if the device has RAM and flash headroom. GOOSE MACs survive, but GDOI must migrate.
  - Authority sits in the fuses and in whoever controls the workstation and vendor HSM.
- **Pipeline.**
  - Setup: RTUs and flow computers over VSAT (~600 ms latency) or cellular, carrying DNP3/Modbus/104 inside router VPNs, feeding leak detection.
  - IKEv2 PQC uses RFC 9370 intermediate exchanges plus RFC 7383 fragmentation, because ML-KEM-1024's 1,568 B key overflows an unfragmented 1,500 B IKE_SA_INIT.
  - Priorities: hybrid VPN, and replacing RTUs whose anchors cannot move. Mechanical relief and shutdown systems limit the consequence of forged firmware.
- **IEC 61850 station vs process bus.** The station bus carries MMS and GOOSE; the process bus carries Sampled Values at roughly 4,000–4,800 frames/s per stream. Public-key cryptography can never sit there. PQC work is entirely in GDOI and engineering authority, so the prior claim holds here.
- **Manufacturing.**
  - Authority sits in the engineering project. Siemens's per-device PLC certificates (TIA Portal V17) followed the hard-coded global key in CVE-2022-38465.
  - **OPC UA bites first:** asymmetric operations at every OpenSecureChannel, session signatures, and UserName passwords encrypted under the server's RSA key, so recorded sessions expose passwords later.
  - Mitigations now: certificate or issued-token user authentication, hybrid TLS 1.3 transport where available.
- **Small water utility.** CRS report R47315 counts "nearly 50,000 community water systems" as of June 2022, and "approximately 81% … serve fewer than 3,300 individuals." The rational plan:
  - hybrid-TLS/VPN clauses in hosting and remote-access contracts;
  - fixing PLCs that accept unsigned logic;
  - normal refresh.
  "Contract clauses only" is defensible here. *Thought experiment:* would $50k be better spent on PQC or on removing internet-exposed HMIs?
- **Rail ERTMS/ETCS.**
  - Euroradio derives session keys from KMACs distributed offline (SUBSET-114) or online (SUBSET-137, TLS with ECC PKI).\[27\]\[37\] Online delivery is exposed to HNDL-to-authority.
  - Domain knowledge, not re-verified: the Euroradio MAC is 3DES-based, a classical weakness.
  - Fix: TLS 1.3 hybrid, shorter KMAC lifetimes, cross-border KMC coordination.
- **Hospital devices.** OEM-signed images with regulatory change control. HL7/DICOM-over-TLS data has 50-year-plus confidentiality, so HNDL applies. The hospital's lever is procurement (crypto-agile updates, CBOM). Recertification, not size, is the constraint.
- **Satellites and avionics.** CCSDS link security is symmetric, with keys loaded pre-launch. Space already runs the "symmetric, physically provisioned" model; its exposure is ground PKI and asymmetric rekey. Avionics (ARINC 645 loadable software, DO-326A) shares the frozen-verifier problem with costlier recertification.

---

# PART IV — Technical Deep Dives

| Scheme | Public key (B) | Sig/ct (B) | Notes |
|---|---|---|---|
| ECDSA P-256 | 64–65 | 64 | Baseline |
| ML-KEM-768 / 1024 | 1,184 / 1,568 | 1,088 / 1,568 | NIST default / CNSA |
| ML-DSA-44/65/87 | 1,312/1,952/2,592 | 2,420/3,309/4,627 | Fast verify |
| FN-DSA-512 | 897 | ~666 | Signing hazardous |
| SLH-DSA-128s | 32 | 7,856 | Stateless |
| LMS SHA-256/192 H10 W8 | 48 | 900 | Cat 3, 1,024 sigs |
| LMS SHA-256/192 H10 W4 | 48 | 1,500 | ~8.7× fewer verify hashes |
| LMS SHA-256 H10 W8 | 56 | 1,452 | Cat 5 |

LMS sizes come from p=u+v, with u=⌈8n/w⌉, v=⌈(⌊log₂((2^w−1)u)⌋+1)/w⌉, and signature = 4+(4+n+pn)+4+hn.

**Filling the LMS/XMSS benchmark gap.**
- Campos et al. (Cortex-M4): LMS needs fewer cycles than XMSS, with at least 85% of time spent hashing.\[38\]
- Rapidly-verifiable XMSS cut M4 verification from 13.85M to 6.56M cycles.\[39\]
- Kampanakis et al.'s 0.049–0.173 Mcycles were measured on a ~2.2 GHz desktop.\[40\] Do not transfer them to MCUs.
- Constructed estimate, assuming ~1,500–4,000 cycles per software SHA-256 block on M4:

| Parameter | Avg / worst hashes | Est. cycles | At 64 MHz |
|---|---|---|---|
| LMS H10 W8 | ~3,330 / ~6,640 | 5–13M avg | 80–210 ms; worst ~410 ms |
| LMS H10 W4 | ~395 / ~777 | 0.6–1.6M | 10–25 ms |
| ML-DSA-44 verify (pqm4, measured) | — | ~1.42–1.50M | ~23 ms |
| SLH-DSA-SHA2-128s verify (pqm4) | — | ~7.5M | ~117 ms |

W4 gives a bounded, secret-free, hardware-SHA-friendly verifier. W8 halves size but has a 2× worst-case spread, so size watchdogs for the worst case. *Experiment:* benchmark wolfBoot LMS on an STM32 with and without the HASH peripheral.

| Platform | Operation | Cycles | Stack |
|---|---|---|---|
| M4 (pqm4 m4f) | ML-DSA-44 sign / verify | ~3,017k / ~1,496k | 44,832 / 8,912 B\[28\] |
| M4 (m4fstack) | ML-DSA-44 sign / verify | ~10,330k / ~3,242k | ~5,064 / 2,712 B\[41\] |
| M0+ RP2040 (ref C) | ML-DSA-44 keygen/sign/verify | 5,297k / 21,135k / 5,849k | sign 50.6 KB\[30\] |
| M0+ RP2040 | ML-DSA-65 / 87 sign peak | — | 77.6 / 119.6 KB\[30\] |
| M7 (SLOTHY vs pqm4) | ML-DSA-44 sign | 7,633k vs 8,512k | —\[42\] |

**Lessons.**
- Stack, not cycles, binds signing on small MCUs.
- Signing latency has a heavy tail.
- Verification fits any Cortex-M boot budget.
- Vendor claims such as PQShield's "ML-KEM in 5 KB RAM" are unverified; open alternatives are PQCA's mlkem-native and mldsa-native.\[34\]

**LoRa** (51 B payload, ~2.5 s airtime, 1% duty ⇒ ~247 s per frame):
- ECDSA signature: 2 frames (~8 min).
- LMS W8: 18 frames (~1.2 h).
- ML-DSA-44: 48 frames (~3.3 h).
- SLH-DSA-128s: 155 frames (~10.6 h).
- ML-KEM-1024 exchange: 62 frames (~4.3 h, ~54% success without retries).

For a 100 KB image, even SLH-DSA adds under 8%. Size dominates only in interactive handshakes, which is why LoRaWAN's symmetric join is correct. In TLS, an X25519MLKEM768 ClientHello grows ~1.2 KB and may split, and some middleboxes reject that (tldr.fail).\[20\] Test industrial firewalls and DPI first.

**Is the data path already symmetric?**

| Protocol | Asymmetric entry point | Verdict |
|---|---|---|
| GOOSE/SV (62351-6) | GDOI group keys (62351-9) | **Holds** |
| MMS / IEC 104 (62351-3/4/5) | TLS handshake per session | Partly |
| DNP3 SAv5 | Optional RSA update-key change | Holds, but HNDL-to-authority |
| DNP3 SAv6/AMP | Elliptic-curve algorithms; unballoted | Holds in design\[11\]\[26\] |
| OPC UA | Every channel and session; RSA password encryption | **Fails**\[24\] |
| CIP Security | (D)TLS 1.2 handshake | **Fails** until (D)TLS 1.3\[13\] |
| BACnet/SC | TLS 1.3 | Partly |
| LoRaWAN | None at device | **Holds strongly** |
| WirelessHART/ISA100 | Optional certificate join | Holds |
| Zigbee Smart Energy | ECC implicit certificates (CBKE) | **Fails** |
| AUTOSAR SecOC | Backend key provisioning | Holds; in-vehicle TLS/V2X fails |
| ETCS | SUBSET-137 ECC TLS | Data holds; KMAC delivery exposed |
| DLMS/COSEM | Suites 1/2 ECDH/ECDSA | **Fails** for suites 1/2 |
| MACsec / PTP | MKA (pre-shared CAK or EAP-TLS) / key management | Holds with pre-shared keys |
| Nuclear I&C | Maintenance paths; diodes | Crypto rarely the right control |

The prior claim holds on hard-real-time paths and fails as a generalisation.

**Stacks: what exists vs what is missing.**
- **MCUboot:** TLV-based image verification. LMS PR (TLV 0x26, "no platforms support this yet"); no ML-DSA or SLH-DSA; maintainers request a hybrid "double signature" mode.\[15\]
- **wolfBoot:** ML-DSA, LMS/HSS, XMSS.\[14\]
- **TF-PSA-Crypto:** LMS in extras/lms.c, reused by MCUboot.\[15\] PSA ML-KEM/ML-DSA not verified.
- **U-Boot FIT and TF-A:** gaps.
- **wolfSSL:** full PQC; 2026 FO-check bug.\[20\]
- **OpenSSL 3.5:** ML-KEM, ML-DSA, SLH-DSA; X25519MLKEM768 by default;\[20\] provider model.
- **HACL\*/libcrux:** verified implementations. Bernstein's 2026 ML-DSA key-recovery-via-bugs work\[20\] makes verified or tested code a requirement.
- **Keyfactor:** EJBCA has LMS, ML-DSA and ML-KEM from 9.1 and SLH-DSA from 9.3; SignServer 7.1.\[43\]
- **Enrolment:** a KEM key cannot sign a CSR, so enrolment needs CMP-style KEM proof of possession. SCEP cannot do this, so retire it. BRSKI/cBRSKI handle zero-touch onboarding.
- **OpenTitan:** ROM verifies the Creator ROM_EXT, which supports ownership transfer. Documented owner keys are RSA-3072 and ECDSA-P256.\[44\]\[45\] Post-quantum ROM support in Caliptra/OpenTitan not verified.
- **DICE:** identities change automatically with firmware.
- **Matter:** a consortium root plus a ledger at consumer scale.
- **CycloneDX CBOM:** the de facto format.

**Genuinely new software needed:**
- (1) LMS state custody with index-reserving backup and multi-site failover;
- (2) MCUboot post-quantum TLVs, imgtool support and hybrid images;
- (3) passive OT crypto-posture extraction;
- (4) KEM replacement for asymmetric key transport in DNP3/62351-5 and the ETCS KMC;
- (5) OT conformance tests for large handshakes.

---

# PART V — Root Causes and Hidden Bottlenecks

1. **Signature growth → flash layout.**
   - ML-DSA-87 adds ~7 KB of TLV/header.
   - It can cross 4–128 KB erase sectors in both A/B slots.
   - Re-partitioning in the field is itself a bricking risk, so the change slips to the next hardware revision.
   - Fix: size headroom now (H11), or store only a key hash in the image.
2. **Statefulness → CI and DR.** A nightly CI that signs every build exhausts a 2^10 tree in about 3 years, which forces HSS multi-level trees or SLH-DSA. HSM restore becomes a hazard, and runbooks must reserve index ranges per site.
3. **Hybrid → test-matrix explosion** across modes, chains and peer versions. Interoperability plug-fests already strain; expect years of conformance cost.
4. **Handshakes → timeouts.** Larger handshakes over 600 ms links can trip application or failsafe timers. Operators may lengthen timeouts and weaken detection.
5. **Downgrade.** Unalarmed classical fallback can be selected by an adversary. Enforce hybrid-strict and log negotiated groups.\[20\]
6. **Spares and version skew** silently reintroduce old anchors. Tag spares by crypto capability.
7. **Safety certification.** Crypto inside a SIL image triggers IEC 61508/61511 impact analysis. Isolation needs a freedom-from-interference argument, and there is no public evidence that assessors accept one.
8. **Entropy.** ML-DSA-44 falls to Category 1 with a random-bit generator under 192 bits.\[1\] Marginal MCU TRNGs now matter.
9. **Time.** Certificates assume trusted time; OT often has unauthenticated NTP/PTP and no RTC battery. Uptane resets clocks when its time-server key rotates; OT has no analogue.\[46\]
10. **Audit-gated budgets.** From 2031, each classical use needs a documented risk decision. "Boards fund obligations, not threats."\[20\]
11. **The real root cause is a three-way deadlock.** OEMs wait for standards, standards move on 3–10-year cycles (SAv6: 2015 to at least 2027), and operators won't pay ahead of the standards. Only regulation and procurement break it.

---

# PART VI — The Root-of-Trust Investigation

**Physical reality.**
- The mask ROM reads key hashes from OTP/eFuse, verifies stage one and jumps to it.
- Anti-rollback counters are finite fuse bits.
- Some parts offer several key slots plus one-time revocation.
- Secure elements and TPMs hold keys separately.
- DICE derives per-boot identity from a unique device secret plus measurements.

**Rotation, succession and transfer** mean, respectively: a new key under the same authority; authority moving to a new key or algorithm; authority moving to a new owner.

| System | Mechanism | Proves | Does not solve |
|---|---|---|---|
| TUF/Uptane | Root N+1 signed by thresholds of old and new keys; roles; expiry\[2\] | Deployed quorum succession | Partial-verification ECUs can't revoke; needs time\[3\] |
| RFC 5011 / DNSSEC | New key signed by old; 30-day hold-down; revoke bit | Internet-scale automated rollover (2018; Oct 2026)\[6\]\[47\] | Stale VMs/containers fail; 2017 pause; still RSA, next roll to ECDSA\[6\]\[18\] |
| UEFI 2026 | KEK-signed db/dbx; 2011→2023 CAs\[4\] | Fleet rotation if the PK stays trusted | OEM firmware dependence; revocation "cannot be reverted under Secure Boot"; RSA\[5\] |
| OpenTitan | Creator keys in ROM; owner keys in ROM_EXT; owner endorses next owner; Creator cannot unlock a locked owner\[45\]\[48\] | Transfer without the manufacturer\[49\] | Classical algorithms; Creator is a single root |
| Android Verified Boot | Rollback indexes, chained vbmeta | Consumer-scale anti-rollback | Single authority |
| CT / binary transparency | Append-only logs | Detects covert signing | Detection only |
| Matter DCL | Consortium root + ledger | Multi-vendor governance | Classical; consumer threat model |

**H1 verdict.** The succession logic is Uptane's, and the hold-down is RFC 5011's. What remains new:
- (a) multiple algorithm-family verifiers in ROM, so succession can switch families;
- (b) monotonic-counter hold-downs for offline devices;
- (c) fault-injection hardening;
- (d) formal proof.

That is engineering and standards work, not a new protocol.

**The bootstrap problem.** If the authorising root is itself broken, only four answers exist:
1. **Pre-commitment:** hashes of independent keys in other families, held by other custodians, committed before any break. This is the most valuable action today.
2. **Time:** hold-downs allow a veto, but offline devices cannot hear one.
3. **Physical presence:** a technician unlock.
4. **Replacement:** IR 8547's default.

*Thought experiment:* OEM gone, ECDSA root forgeable, device offline, and no pre-commitment. Only presence or replacement remain. The problem is solvable only prospectively.

**Attacks.**
- Fault injection skipping the compare branch; countered by redundant checks and sensors in silicon.
- Rollback of root epochs; counters must cover epochs.
- Freeze attacks; expiry reintroduces the time problem.
- Custodian collusion; thresholds need organisational and algorithmic independence.

I found no published Tamarin or ProVerif model of multi-family ROM succession. That is a clear research gap.

---

# PART VII — Competitive Landscape

| Layer | Shipping (verified) | Unverified / announced | Gap |
|---|---|---|---|
| Silicon/IP | — | PQShield (customers reported to include AMD, Microchip, Collins Aerospace, Lattice),\[50\] Infineon, NXP, ST, Microchip, Rambus, Synopsys, Secure-IC, Caliptra, OpenTitan | Multi-family ROM verifiers as a requirement |
| Bootloaders | wolfBoot | MCUboot LMS PR | MCUboot ML-DSA/SLH-DSA, hybrid images |
| HSM | Thales Luna T7 (FIPS 140-3 cert #5450, fw 7.15.1) | Entrust, Utimaco | Multi-site stateful-HBS custody |
| PKI/CLM | Keyfactor EJBCA/SignServer | DigiCert, AppViewX, Venafi (Palo Alto Networks), MTG | OT-protocol-aware issuance |
| OT visibility | Nozomi, Claroty, Dragos, Armis, Forescout | Crypto-inventory features | Passive PQ posture\[51\] |
| Automation OEMs | No verified PQ shipments: Siemens, Schneider, Rockwell, ABB, Honeywell, Emerson, Yokogawa, GE Vernova, Hitachi Energy, SEL | — | PQ anchors in new PLCs/IEDs |
| Device management | Mender, Memfault, AWS, Azure, LwM2M | PQ signing unverified | Stateful signing integration |

**Deals.**
- Nozomi: USD 883 million for the 93% Mitsubishi Electric didn't own. The deal closed on 28 January 2026. Nozomi's net revenue was $74.7M in 2024 and $101.7M in 2025.
- Venafi: "approximately $1.54 billion" (≈$1B cash + ≈$540M shares; SEC 6-K, 1 Oct 2024).
- CyberArk: "approximately $25 billion" equity value. Closed 11 Feb 2026 for $2.3B cash and 112M Palo Alto Networks shares.
- Claroty: >$100M ARR (2023).\[52\]
- Dragos+runZero+NetRise: ~$208M ARR, +53% (Accenture, 18 Jun 2026). Dragos closed 16 Sep 2026.
- Keyfactor: ">$200 million" ARR at the start of Q3 2026, growing ">35%". The $1B+ Summit Partners investment was announced 6 Jul 2026.

**Implication:** a post-quantum OT component is more likely to be bought than to displace these companies.

---

# PART VIII — Hypotheses H1–H22 Reassessed, and H23–H42

| H | Verdict |
|---|---|
| H1 Trust constitution | Keep, re-scoped (N2 P4 I5): multi-family ROM, counter hold-down, fault hardening, proofs |
| H2 Gateway proxies | Keep as compensating control; attest the proxy |
| H3 Signature-free devices | Keep for new designs; KEM-EDHOC immature |
| H4 KDC for closed cells | Keep; strong prior art (LoRaWAN join server, ISA100, KMC) |
| H5 Threshold stateful-HBS custody | Keep: top commercial wedge |
| H6 Binary crypto lifting | Keep, narrowed to CBOM; precision unproven |
| H7 Crypto digital twin | Merge into H12/H36 |
| H8 Crypto/safety separation | Keep as research priority; no assessor evidence |
| H9 Verify-once, attest-many | Weaken; shifts trust to the gateway |
| H10 Merkle-batched manifests | Minor; TUF/SUIT prior art |
| H11 Crypto headroom | Keep: cheapest high-impact rule |
| H12 Posture as a service | Feature for OT-visibility vendors |
| H13–15 PHY keys, QKD, QRNG | Kill as strategy |
| H16 Short-lived credentials | Keep; needs time and EST/CMP |
| H17 Verified parsers | Keep |
| H18 Insurance pricing | Market signal via 2031 deprecation records |
| H19 Hybrid-strict + telemetry | Keep; NIST logging advice |
| H20 Trust escrow | Keep, modelled on the Matter DCL; governance-heavy |
| H21 Ascon for 8/16-bit | Niche |
| H22 Hash-only ROMs | Merge into H1/H29 |

**New hypotheses:**
- **H23 Anchor telemetry.** RFC 8145-style key-tag reporting in IEC 62351-7 NSM objects or OPC UA diagnostics; makes rollovers measurable.
- **H24 Counter-based hold-down.** Boots or authenticated heartbeats replace the 30-day clock; needs a formal model against boot-spinning.
- **H25 Epoch-based validity.** Validity is counted in root epochs, not wall-clock time.
- **H26 KEM retrofit for DNP3-SA, IEC 62351-5 and KMC key transport.** Closes the most concrete HNDL-to-authority exposure.
- **H27 OPC UA over TLS 1.3 hybrid transport** plus non-password user tokens, as the fast path.
- **H28 Deadline-aware parameter choice.** LMS W4 or a hardware SHA engine, with a worst-case bound written into the safety case.
- **H29 "Hash engine first" ROMs.** SHA-accelerated LMS/SLH-DSA verification plus multiple key slots.
- **H30 Crypto partition as a pre-certified Safety Element out of Context (SEooC).**
- **H31 LMS index allocation logged** in an append-only, HSM-co-signed log; backups restore only unused ranges.
- **H32 Offline-verifiable firmware transparency** checked by the engineering workstation.
- **H33 Escrowed pre-signed succession manifests** for OEM exit.
- **H34 PQ conformance and fuzz suite for OT** ("tldr.fail for OT").
- **H35 Engineering workstation as PQ chokepoint.** PQ-signed download tokens.
- **H36 Passive CBOM** from ClientHello groups, UA policy URIs, DNP3-SA objects and certificate chains.
- **H37 Automated deprecation records** for each classical use from 2031.
- **H38 TESLA-style one-way key chains** for 8/16-bit devices.
- **H39 Spare-part crypto tagging.**
- **H40 DICE/SPDM-attested proxies.**
- **H41 Dual-family ROM requirement** in PSA Certified, IEC 62443-4-2 or procurement profiles.
- **H42 DER inverter fleets** (TLS-native IEEE 2030.5) as the first mass PQ OT target.

**Ranking:** H11 > H29/H41 > H5/H31 > H26 > H36 > H35 > H23 > H34 > H1 > H30/H8 > H27 > H42.

---

# PART IX — Commercial Opportunities

**Who's who.** Operators carry the risk; OEMs hold the signing keys; silicon vendors and OEMs control the anchors; budgets follow refresh cycles and contracts; OEMs and operators resist because of recertification and downtime.

**Sourced counts.**
- 3,405 EIA-861 filers for 2025, including 3,065 retail-serving utilities.\[53\]
- 1,929 public-power utilities and 918 co-ops (2024).\[54\]
- "Nearly 50,000" community water systems as of June 2022, about 81% serving fewer than 3,300 people (CRS R47315).
- ~55,000 US substations (weakly sourced).\[55\]

| Segment | Count | Spend assumption (mine) | US annual |
|---|---|---|---|
| Large electric | ~200 | $250k–$1M | $50–200M |
| Mid electric | ~800 | $20–75k | $16–60M |
| Small electric | ~2,000 | ≤$10k | ≤$20M |
| Water >3,300 served | ~9,500 | $5–30k | $48–285M |

**Model.**
- US operator-side program spend: ~$0.13–0.57B a year at peak.
- Assuming the US is 25–35% of global spend, and that oil and gas, manufacturing, rail and health roughly double the base, global program spend is ~$0.7–3B a year in the early 2030s, mostly services and refresh hardware.
- The software-addressable share for a standalone vendor is plausibly $100–600M a year.
- Sanity check: three OT-visibility leaders together run at ~$0.4–0.5B recurring revenue after a decade.

| Option | Verdict |
|---|---|
| Full Industrial Trust Plane | No: too broad, incumbent-crowded |
| Stateful-HBS custody + secure-boot SDK for OEMs and silicon (H5/H31/H29) | Best wedge; exit to HSM/PKI/IP vendor |
| Passive PQ posture via OT-visibility partners (H36) | Good component |
| Services (inventory, RFP clauses, conformance H34) | Real revenue now, low moat |
| Safety assurance (H30) | Long-term |

**MVP:** LMS/HSS signing with index-reserving multi-HSM custody and an audit log, integrated with MCUboot and wolfBoot, plus a hybrid manifest. **Pilot:** one OEM line plus one HSM partner, 6–9 months. **Sales cycles:** OEMs 6–12 months; utilities 18–36 months.

---

# PART X — Outlook

- **To 2031:**
  - hybrid TLS/IKE standard in OT gateways;
  - new MCUs with LMS/ML-DSA in ROM;
  - FN-DSA and HQC published;
  - deprecation records drive audits;
  - the DNS root moves only to ECDSA (~2029).
- **To 2036:**
  - disallowance;
  - brownfield devices isolated or replaced;
  - a public CRQC is plausible *if* the 2026 estimates and the 2029–2030 vendor roadmaps hold (a forecast, not a fact).
- **15–20 years:** a second transition (hybrid → pure PQ, or lattice → backup family). Devices designed in 2027 must survive two transitions, which argues for multi-family ROMs, epoch validity and DICE identity.
- **Geopolitics:** SM2/3/4, GOST and KpqC divergence requires pluggable families and regional anchors (OpenSSL providers, PSA drivers).

# PART XI — Learning Roadmap

1. **Mathematics:** modular arithmetic and polynomial rings, then Regev's LWE paper and FIPS 203/204/205.
2. **Quantum:** Nielsen & Chuang (QFT, Shor), Gidney 2025, and Google's 2026 ECDLP white paper.
3. **Embedded:** wolfBoot LMS/ML-DSA on STM32/nRF, timed with and without the hardware SHA engine; pqm4 on a NUCLEO-L4R5ZI; port the MCUboot LMS PR to real hardware.
4. **Protocols:**
   - Wireshark DNP3 SAv5 and GOOSE/MMS traces.
   - An open62541 OpenSecureChannel.
   - An X25519MLKEM768 handshake through an industrial firewall.
5. **Root of trust:** the Uptane standard, RFC 5011, ICANN's 2019 review, and the OpenTitan ownership docs; model two-family succession in Tamarin.
6. **CBOM:** generate a CycloneDX CBOM for a firmware image.
7. **Policy:** IR 8547, M-26-15, EO 14412.

# PART XII — Twenty Unanswered Questions

1. Will assessors accept crypto partitions as freedom-from-interference elements? (Pilot certifications; IEC TC65 proposal.)
2. Is there a formally verified multi-family ROM succession state machine? (Tamarin/ProVerif.)
3. How can partial-verification devices handle revocation? (Protocol plus counters.)
4. How do offline devices get trustworthy time, or avoid needing it? (H25.)
5. What are measured LMS/XMSS verify cycles and stack across M0+/M4/M33/M55/RISC-V? (Open benchmark.)
6. What share of fielded OT devices verify any signature? (Passive study.)
7. Which firewalls and DPI engines break on split ClientHellos or fragmented IKE? (H34.)
8. When will OPC UA, IEC 62351, DNP3 and CIP publish PQ profiles?
9. Is HNDL-to-authority exploitable given real key lifetimes? (Field survey.)
10. How do you do multi-site stateful-HBS custody safely? (H31 prototype.)
11. Is masking needed on verify-only devices? (Verification uses no secrets, so likely not.)
12. Who governs anchors for orphaned devices? (H33.)
13. Will lattice margins last 30 years? (Family diversity.)
14. Can passive CBOM reach high precision?
15. What will insurers and auditors demand under the 2031 "deprecated" status?
16. When is replacement cheaper than migration? (TCO models.)
17. What does an adversary actually gain from breaking OT crypto, compared with weak controls?
18. How should SM2 or GOST anchors coexist with NIST anchors?
19. When will DNSSEC, UEFI and WebPKI roots move to post-quantum?
20. Is there a venture-scale standalone business here? (H5/H31 pilots.)

## Recommendations

**Operators:**
- Write headroom (≥16 KB signatures, ≥4 KB keys), hybrid key exchange, post-quantum firmware verification and CBOM delivery into every OT RFP now.
- Move HNDL-to-authority paths to hybrid by 2030.
- Log negotiated groups and alarm on downgrade.
- Tag spares by crypto capability.
- Document "contract clauses only" for low-consequence, tiny-budget assets.

**OEMs:**
- Specify at least two algorithm-family ROM verifiers plus a SHA engine in new silicon.
- Sign firmware with LMS/HSS under index-reserving custody.
- Migrate TLS 1.2 to 1.3 before PQC.

**Builders:** pursue stateful-HBS custody and secure-boot tooling, or passive posture as a component; expect an acquisition exit.

## Caveats

- Secondary-sourced items: FAR and CBOM dates, composite RFC status, UEFI post-June outcomes, and the outcome of the 11 Oct 2026 DNSSEC rollover (scheduled; outcome not verified).
- Quantum estimates are preprints or white papers; roadmaps are forward-looking statements.
- Members-only drafts may hold unseen PQC work.
- LMS cycle figures are constructed estimates.
- Market tiering and spend levels are my assumptions.
- The Thales OTCEP deck could not be obtained.

## Running Glossary

- **AMP:** DNP3 authorisation protocol.
- **BRSKI:** zero-touch bootstrap.
- **CBOM:** cryptographic bill of materials.
- **CMP/EST/SCEP:** certificate enrolment protocols.
- **CRQC:** cryptanalytically relevant quantum computer.
- **Deprecated/Disallowed:** NIST statuses meaning "usable with risk" vs "not allowed".\[1\]
- **DICE:** measurement-derived device identity.
- **FO transform:** CCA conversion with a re-encryption check.
- **GDOI:** group key distribution.
- **GOOSE/SV:** IEC 61850 multicast messages.
- **HNDL:** harvest now, decrypt later.
- **HNDL-to-authority:** harvesting the transport of long-lived authority keys.
- **Hold-down:** waiting period before a new anchor is trusted.
- **IDevID:** factory device identity certificate.
- **KEM:** key encapsulation mechanism.
- **KMC:** ETCS key management centre.
- **LMS/XMSS:** stateful hash-based signatures.
- **Logical qubit:** an error-corrected qubit.
- **Magic state:** distilled non-Clifford resource.
- **Module-LWE/SIS:** lattice hardness assumptions.
- **NTT:** number-theoretic transform.
- **OTP/eFuse:** one-time-programmable memory.
- **Partial-verification ECU:** an Uptane device that skips Root metadata.
- **Rejection sampling:** aborting signatures that would leak the key.
- **SecOC:** AUTOSAR message authentication.
- **SEooC:** safety element out of context.
- **Surface code:** 2D quantum error-correcting code.
- **TUF/Uptane:** thresholded secure-update frameworks.
- **Winternitz W:** the size/speed trade-off parameter.

## Sources

1. <https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf>
2. [IEEE-ISTO 6100.1.0.0 Uptane Standard for Design and Implementation](https://uptane.org/papers/ieee-isto-6100.1.0.0.uptane-standard.pdf)
3. [Best Practices 2.1.0](https://uptane.org/docs/2.1.0/deployment/best-practices)
4. [Windows Secure Boot certificate expiration and CA updates](https://support.microsoft.com/en-us/servicing/os/secure-boot/2025/06/windows-secure-boot-certificate-expiration-and-ca-updates)
5. [Secure Boot Certificate Rotation 2026: What Breaks and What to Do](https://safeguard.sh/resources/blog/secure-boot-certificate-rotation-2026-what-breaks-and-what-to-do)
6. <https://www.icann.org/en/system/files/files/ksk-rollover-expect-27jul26-en.pdf>
7. [Google: Quantum resources required to break elliptic-curve cryptography are significantly lower than previously expecte…](https://www.techflowpost.com/en-US/newsletter/118524)
8. [New Architecture Could Cut Quantum Hardware Needed to Break RSA-2048 by Tenfold, Study Finds](https://thequantuminsider.com/2026/02/13/new-architecture-could-cut-quantum-hardware-needed-to-break-rsa-2048-by-tenfold-study-finds/)
9. [Alice & Bob Estimates 22,593 Qubits to Break RSA-2048](https://thequantuminsider.com/2026/10/29/alice-bob-22593-qubits-break-rsa-2048/)
10. [Quantum algorithms: A survey of applications and end-to-end complexities](https://arxiv.org/pdf/2310.03011)
11. [The Case Against DNP3 SAv6 and AMP](https://stepfunc.io/blog/case-against-dnp3-sav6/)
12. [Explanation of Security Overview AUTOSAR FO R25-11 Document Title](https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SecurityOverview.pdf)
13. [Constrained CIP Security Best Practices](https://www.odva.org/wp-content/uploads/2023/10/2023-ODVA-Conference_Visoky-Korbel_Constrained-CIP-Security-Best-Practices.pdf)
14. [wolfBoot: Secure Boot now with support for FIPS 204 ML-DSA post-quantum signature algorithm - wolfSSL](https://www.wolfssl.com/wolfboot-secure-boot-now-with-support-for-fips-204-ml-dsa-post-quantum-signature-algorithm/)
15. [Add LMS signature support by d3zd3z · Pull Request #2707 · mcu-tools/mcuboot · GitHub](https://github.com/mcu-tools/mcuboot/pull/2707)
16. [A post quantum key type for image signing with ML DSA · Issue #2937 · mcu-tools/mcuboot · GitHub](https://github.com/mcu-tools/mcuboot/issues/2937)
17. [ICANN](https://www.icann.org/en/system/files/files/octo-035-18jul22-en.pdf)
18. [What you need to know about the first-ever DNSSEC root key rollover on October 11, 2018](https://www.redhat.com/en/blog/what-you-need-know-about-first-ever-dnssec-root-key-rollover-october-11-2018)
19. [Post-Quantum Cryptography Project Publications](https://csrc.nist.gov/Projects/post-quantum-cryptography/publications)
20. [NIST IR 8547 Final: What Changed From the Draft](https://postquantum.com/security-pqc/nist-ir-8547-final/)
21. [White House PQC Mandates Explained: EO 14409 & M-26-15](https://www.wiz.io/blog/white-house-post-quantum-cryptography-executive-order)
22. [OMB M-26-15 Sets 2030 Execution Deadlines for Post-Quantum Migration and Adds Cryptographic Bill of Materials Mandate](https://govconfeed.com/article/omb-m-26-15-post-quantum-cryptography-cbom-mandate-june-2026)
23. [NIST Just Rewrote the Post-Quantum Deadline. Your RSA-3072 Plan Is Out of Date - DEV Community](https://dev.to/indirectb/nist-just-rewrote-the-post-quantum-deadline-your-rsa-3072-plan-is-out-of-date-3a35)
24. [Release Issue 03: Finding the cryptography inside an OPC UA deployment · foikwuogu/quantum-safe-pipeline-notes · GitHub](https://github.com/foikwuogu/quantum-safe-pipeline-notes/releases/tag/issue-03)
25. [IEC 62351 Guide: Power System Communications Security](https://nhimg.org/iec-62351-guide)
26. [How DNP3-SAv6 and AMP Meet OT Security Requirements Like Nothing Else](https://cdn.asp.events/CLIENT_CL_US_323E7AA7_5056_B733_8303D39C538813E0/sites/DI-2025/media/libraries/How-DNP3-SAv6-and-AMP---DTECH24-PPT.pdf)
27. [EEIG ERTMS Users Group 123-133 Rue Froissart, 1040 Brussels, Belgium](https://ertms.be/wp-content/uploads/2024/07/20E234-2-_Extension-Key-Request-Function.pdf)
28. [Low-Stack HAETAE for Memory-Constrained Microcontrollers](https://arxiv.org/pdf/2604.15868)
29. [SHA-34: E1.4 ML-DSA verify benchmark on target and go/no-go decision by smhasan94 · Pull Request #3 · smhasan94/keelsign · GitHub](https://github.com/smhasan94/keelsign/pull/3)
30. [Benchmarking NIST-Standardised ML-KEM and ML-DSA on ARM Cortex-M0+: Performance, Memory, and Energy on the RP2040](https://arxiv.org/html/2603.19340v5)
31. [Quantum Error Correction Explained 2026: 7 Essential Concepts](https://quantumzeitgeist.com/what-is-quantum-error-correction/)
32. [Quantinuum Breaks Error-Correction World Record by 10x, Validating Its Leading Path to Fault-Tolerant Quantum Computing by 2029](https://ir.quantinuum.com/news-releases/news-release-details/quantinuum-breaks-error-correction-world-record-10x-validating)
33. [The White House's post-quantum executive order is an important milestone. It’s time to get to work](https://blog.cloudflare.com/post-quantum-eo-2026)
34. [1 Benchmarking NIST-Standardised ML-KEM and ML-DSA on ARM Cortex-M0+: Latency,](https://arxiv.org/pdf/2603.19340)
35. [Lattice: A Post-Quantum Settlement Layer](https://arxiv.org/pdf/2603.07947)
36. [Towards Quantum-Resistant Trusted Computing: Architectures for Post-Quantum Integrity Verification Techniques](https://arxiv.org/pdf/2601.11095)
37. [European Rail Traffic Management System, what you need to know](https://www.linkedin.com/pulse/european-rail-traffic-management-system-what-you-need-amine-aloui)
38. [LMS vs XMSS: Comparison of Stateful Hash-Based Signature Schemes on ARM Cortex-M4](https://link.springer.com/chapter/10.1007/978-3-030-51938-4_13)
39. [Rapidly Veriﬁable XMSS Signatures](https://eprint.iacr.org/2020/898.pdf)
40. [Post-Quantum LMS and SPHINCS+ Hash-Based Signatures for UEFI Secure Boot](https://eprint.iacr.org/2021/041.pdf)
41. [Signing on ML-DSA-44 benchmark leaderboard · SOTA2 Research](https://www.sota2.com/research/sota/signing-on-ml-dsa-44)
42. [Enabling Microarchitectural Agility: Taking ML-KEM & ML-DSA](https://kannwischer.eu/papers/2025_slothy-m7_20250304.pdf)
43. [PQC Capabilities Matrix (PQCCM)](https://pkic.org/wg/pqc/pqccm/)
44. [Ownership Transfer - OpenTitan Documentation](https://opentitan.org/book/doc/security/specs/ownership_transfer/)
45. [Secure Boot - OpenTitan Documentation](https://opentitan.org/book/doc/security/specs/secure_boot/)
46. [Uptane Deployment Best Practices v.1.2.0](https://uptane.org/papers/V1.2.0_uptane_deploy.html)
47. [Proposal for Future Root Zone KSK Rollovers](https://www.icann.org/en/system/files/files/proposal-future-rz-ksk-rollovers-01nov19-en.pdf)
48. [Ownership Transfer](https://opensecura.googlesource.com/3p/lowrisc/opentitan/+/3a436251530eed1ca21b05fbcd2041199e22adf5/doc/security/specs/ownership_transfer/README.md)
49. [ROM\_EXT Ownership Transfer - OpenTitan Documentation](https://opentitan.org/book/sw/device/silicon_creator/rom_ext/doc/ownership.html)
50. [Quantum computers could be coming: PQShield just raised \$37m to protect tech against them](https://sifted.eu/articles/quantum-pqshield-seriesb-raise-news)
51. [Dragos’s Competitors, Revenue, Number of Employees, Funding, Acquisitions & News - Owler Company Profile](https://www.owler.com/company/dragossecurity)
52. [Cyber unicorn Claroty raises \$100 million, surpasses \$100 million in ARR](https://www.calcalistech.com/ctechnews/article/h1mm411u6p)
53. [U.S. Electric Utility Directory and ISO Map: Every Utility, County and Grid Operator](https://deaudits.com/blog/us-electric-utility-directory/)
54. [Public Power & Electric Co-ops by State: All 50 Lists](https://www.kensingtonsalesgroup.com/resources/utilities-by-state.html)
55. [Substation](https://en.wikipedia.org/wiki/Substation)

# Reinventing Post-Quantum Migration for OT and Embedded Infrastructure: From Algorithm Swaps to a Managed Trust Plane

The most important finding: in OT, the post-quantum problem is mainly about who is allowed to change a device's firmware and identity, not about who can read its traffic. It cannot be fixed one endpoint at a time. Most field devices installed today will still be running when NIST disallows RSA and ECC in 2035. Their cryptography is frozen into silicon, bootloaders, protocol parsers and safety certifications. So the winning approach is to manage trust renewal as an external, continuously operated layer, built on hash-based roots, gateways and symmetric keys. Swapping ML-KEM and ML-DSA into every PLC is not that approach.

## TL;DR

- **The deadline is set.** NIST published the final IR 8547 on 27 October 2026. It deprecates every quantum-vulnerable public-key algorithm after 2030 and disallows them after 2035, regardless of key size. The EU wants critical infrastructure's high-risk use cases migrated by the end of 2030, and Australia wants classical public-key cryptography gone by the end of 2030. OT assets bought today have 15–30-year lives, so most will outlive these dates.
- **The real threats are forgery and frozen roots, not decryption.** The big OT exposures are forged firmware and forged device identity, plus trust anchors that cannot be changed once deployed. Harvest-now-decrypt-later matters for long-lived keys, engineering data and remote-access sessions, but much less for sensor telemetry. Stateful hash-based signatures (LMS/XMSS) are the strongest near-term tool for firmware roots. CNSA 2.0 already required them to be "supported and preferred" by 2025, with exclusive use by 2030.
- **The opportunity is a "trust plane", not another scanner.** That means a continuously operated layer for managing cryptographic trust: hash-based root anchors with remote renewal, signature-free KEM-based handshakes for constrained links, gateways that block downgrades, binary-level crypto discovery, and symmetric key distribution for devices that can never run PQC. Industrial protocol standards are the binding constraint. OPC UA, IEC 62351, DNP3-SA, CIP Security and AUTOSAR SecOC have no published PQC profiles yet, so for most of this decade the only control an asset owner can deploy alone is wrapping at the boundary.

## Key Findings

1. **The policy clock has hardened.** The final NIST IR 8547 (27 Oct 2026) dropped the draft's carve-out that let RSA-3072, P-256 and Ed25519 run to 2035. All approved quantum-vulnerable public-key schemes are now deprecated after 2030 and disallowed after 2035. Executive Order 14412 (22 June 2026) and OMB M-26-15 (24 June 2026) require federal high-value and high-impact systems to use PQC for key establishment by 31 Dec 2030 and for signatures by 31 Dec 2031. A FAR rule for contractors is due around 19 Dec 2026. CISA's minimum elements for a cryptographic bill of materials (CBOM) are due around 19 March 2027.\[1\]
2. **Hybrid now has a validation path; hybrid signatures remain unsettled.** IR 8547 states that a hybrid key-establishment scheme "can be FIPS 140-validated" if at least one input comes from an approved scheme. For hybrid signatures, NIST says "the security properties of hybrid signatures are complex and need to be carefully analyzed."\[1\] The signature half of the migration, which is the half that matters most for OT, is therefore the slower half.
3. **Industrial protocols are the bottleneck, not algorithms.** As of November 2026 there is no OPC UA PQC SecurityPolicy (its newest asymmetric policies are ECC, from v1.05).\[2\] IEC 62351-9:2023 says that "at this time being no specific measures are provided" for PQC.\[3\] DNP3-SAv6 is only "designed to accommodate" PQC and is still in draft.\[4\]\[5\] ODVA's October 2026 CIP Security announcements mention no PQC.\[6\] AUTOSAR states that "current TLS standards available don't provide post quantum ready asymmetric cryptography yet."\[7\] OEMs cannot ship compliant PQC firmware for protocols whose standards do not yet define it.
4. **Microcontroller compute is mostly solved; bytes, stack and side channels are not.** On Cortex-M4, ML-KEM-768 decapsulation takes 707,827 cycles (pqm4 m4fspeed), about 30 ms at 24 MHz.\[8\]\[9\] ML-DSA-44 verification takes 1.42 M cycles with 8.9 KB of stack. The hard parts are elsewhere: ML-DSA-44 signing needs about 44.8 KB of stack,\[8\] and signatures are 2.4–4.6 KB against 64 bytes for ECDSA. A first-order masked ML-KEM-768 decapsulation costs about 3 M cycles, a 3.5× overhead. And radio frames are tiny: an ML-KEM-768 exchange needs 18 IEEE 802.15.4 frames.
5. **Secure boot with PQC is already practical on mid-range parts.** wolfBoot verified an ML-DSA-87 image on an NXP i.MX95 Cortex-M7 in 5.25 ms (vendor-measured). Its bootloader code was 940 bytes smaller than the ECDSA P-256 build, but each image header grew by about 7 KB. Infineon's OPTIGA TPM SLB 9672, announced in February 2022, has a firmware update mechanism protected by XMSS signatures, so the TPM "can still be updated if the standard algorithms are no longer trusted." The cost moves out of compute and into image headers, slot sizes and key-state management.
6. **The deepest unsolved problem is renewing roots of trust in fielded devices.** Siemens' S7-1200/1500 hardcoded-key case (CVE-2022-38465) showed what happens when a trust anchor sits in a secure element that cannot be patched. Every device shipping today with a single classical root key is a future replacement liability.
7. **Market numbers are unreliable.** Published 2025 "PQC market" estimates range from USD 0.42 B (MarketsandMarkets) to USD 1.6 B (Grand View Research), a fourfold spread in the base year alone, and none models OT specifically. My bottom-up estimate puts addressable OT and embedded trust-lifecycle spend in the low single-digit billions per year by the early 2030s.

---

# Part I — The Big Picture

## What the threat actually is

Shor's algorithm solves integer factorisation and discrete logarithms (finite-field and elliptic-curve) in polynomial time on a fault-tolerant quantum computer. That breaks RSA, DH, ECDH, ECDSA and EdDSA completely: no key-size increase helps. Grover's algorithm gives only a quadratic speed-up against symmetric ciphers and hashes, and it parallelises poorly.\[10\] AES-128 keeps meaningful security, and AES-256, SHA-384 and SHA-512 are comfortable. **In short: every public-key operation must change, and symmetric primitives mostly need not.** That asymmetry is the single most under-exploited fact in OT migration planning.

How far away a cryptographically relevant quantum computer is remains a moving estimate. In May 2025 Craig Gidney (Google Quantum AI) estimated that RSA-2048 could be factored "in less than a week by a quantum computer with less than a million noisy qubits," a 20-fold reduction from his 2019 estimate with Ekerå of 20 million qubits.\[11\]\[12\]\[13\] It is a resource estimate, not a demonstrated attack.\[14\]\[15\] Later 2026 preprints claim further reductions; treat them as unverified until peer-reviewed. The direction matters more than any single number: estimated attack costs keep falling faster than hardware is improving.

## Why OT is different (and harder)

Mosca's inequality frames the risk: if the time data must stay secure (x) plus the time to migrate (y) exceeds the time until a quantum attack is possible (z), you are already exposed. In IT, x is often short and y is 3–5 years. In OT, three things change:

- **Asset life is far longer.** The Thales OTCEP 2026 deck for Singapore's CSA gives typical OT lifetimes of 7–10 years for ICS gateways, 15–20 years for RTUs and protection relays, and 25–30 years for safety PLCs and turbine control. A safety PLC commissioned in 2026 runs about 21 years past the 2035 disallowance date.\[16\]
- **Migration takes much longer.** OEM firmware, IEC 61508/62443 recertification, outage windows and vendor-standard dependencies stretch migration to a decade or more. CISA's October 2024 guidance calls OT PQC migration "a significant and enduring challenge."\[17\]
- **The asset that matters is authority, not secrecy.** A forged firmware signature or device certificate gives an attacker persistent control of a physical process; a decrypted Modbus reading usually reveals little. Thales calls the relevant variant "HNFL", harvest-now-forge-later: capture a vendor's public firmware-signing key today, derive its private key once a quantum computer exists.\[16\]

## The core reframing

The usual question is "how do we put ML-KEM and ML-DSA into every device?" The better question is how a 30-year physical system can **renew its own cryptographic authority** several times during its life, without being physically touched and without recertifying its safety function each time. NIST's own final report expects hybrid to lead to "a second transition to post-quantum-only cryptography."\[18\] The SIKE and Rainbow breaks (both 2022) show that newly standardised families can fail suddenly. A 30-year asset should therefore expect two or three cryptographic transitions in its life, not one.

---

# Part II — The Existing System: A Layer-by-Layer Map

| Layer | What it does today | Typical crypto | Why it exists | PQC limitation | What could replace or improve it |
|---|---|---|---|---|---|
| Silicon RoT (ROM bootloader, OTP fuses, secure element, PUF) | Anchors the first verification step | ECDSA P-256 or RSA-2048 public-key hash in fuses; SE such as ATECC608 | Makes trust immutable so malware cannot change it | Fused classical keys cannot be rotated; SE firmware is often unpatchable | Multiple fused roots of different types (classical + LMS/XMSS + SLH-DSA); hash-only ROM verifiers |
| TPM 2.0 / DevID (IEEE 802.1AR IDevID/LDevID) | Device identity, attestation, measured boot | RSA-2048 or ECC P-256 keys | Manufacturer-backed identity | TPM PQC is only on roadmaps; IDevID certificates issued at manufacture for life | PQC-capable TPMs (Infineon roadmap); LDevID re-enrolment via KEM-based protocols |
| Bootloader / update (MCUboot, wolfBoot, U-Boot, vendor) | Verifies images; A/B slots, rollback | ECDSA/RSA + SHA-256 | Blocks malicious firmware | Fixed header and TLV sizes, flash slot sizing, verification RAM | LMS/XMSS or ML-DSA verifiers (wolfBoot ships both); SUIT manifests |
| RTOS / embedded Linux crypto (mbedTLS/PSA, wolfSSL, OpenSSL) | TLS, DTLS, signatures | ECDHE + ECDSA | Secure channels | Static buffers, ASN.1 parsers with hard size limits | PSA Crypto with PQC drivers; size-agnostic parsers |
| Field protocols (Modbus/TCP, DNP3-SA, IEC 61850 GOOSE/SV with IEC 62351-6, OPC UA, CIP Security, PROFINET Security, BACnet/SC) | Process data and commands | None (Modbus) or HMAC/AES with RSA/ECC key setup | Real-time determinism | No PQC profiles published (Part IV) | Keep symmetric data path; move PQC into key distribution and management |
| Constrained wireless (802.15.4/6LoWPAN, Zigbee, WirelessHART, LoRaWAN, BLE) | Sensor networks | AES-CCM with network or pre-shared keys; LoRaWAN AES root keys | Energy and bandwidth limits | 127-byte frames; LoRa payloads as small as 51 bytes | Symmetric data paths already quantum-resistant; PQC only at join servers and back ends |
| Automotive (CAN/CAN-FD, SecOC, automotive Ethernet) | ECU messaging | AES-128 CMAC (e.g., SecOC Profile 2: 24-bit CMAC)\[19\] | 8–64-byte frames | Data path quantum-safe; key management and backend PKI are not | PQC backend PKI and OTA signing |
| Gateways, remote access, IDMZ | Segmentation, translation, vendor access | IPsec/IKEv2, TLS, SSH | Boundary control | Software-updatable, so easiest place to start | Hybrid IKEv2 (X25519 + ML-KEM-768), already demonstrated |
| Enterprise PKI, HSMs, code signing | Issue certificates, sign firmware | RSA/ECDSA CAs, HSMs | Centralised trust | HSM upgrades; stateful HBS state management | PQC HSMs; HBS state-managed signing services |
| Rail ERTMS/ETCS | Train-to-trackside keys | Classical PKI over TLS (UNISIG SUBSET-137, 2015)\[20\] | Interoperable safety signalling | No public PQC plan found | Symmetric KMC continuity plus PQC online key management |

**What each component hides.** Across the stack, **cryptographic sizes are hard-coded in places nobody calls "crypto"**: buffer sizes in protocol parsers, fixed certificate fields in engineering tools, TLV length fields in image headers, flash partition maps, EEPROM layouts for key storage. This is the "crypto is 2% of the code but 100% of the blocker" problem. The algorithm is a library call; the sizes are architecture.

**A cautionary case study.** In 2022, Claroty's Team82 extracted a hardcoded global private key protecting Siemens SIMATIC S7-1200/1500 PLC families (CVE-2022-38465). Siemens' fix was a new PKI with per-device keys in TIA Portal V17.\[21\] A 20 October 2022 CPO Magazine report argues Siemens "opted to hardcode the credentials to save users and integrators from the complexities of key management systems, which did not exist at the time for industrial systems." That sentence explains much of OT cryptography: **key management was the missing infrastructure, and hardcoding was the workaround.** PQC migration will repeat this failure unless key management is supplied as infrastructure.

---

# Part III — The Fundamental Problems

## Root causes (why the problems exist)

1. **Immutability was the security goal.** Roots of trust are fused into hardware so attackers cannot change them, and that same immutability makes cryptographic renewal impossible. The trade-off was rational when RSA and ECC were expected to last indefinitely.
2. **Safety certification freezes the whole binary.** Under IEC 61508 and its sector derivatives, changing a safety-relevant binary triggers impact analysis and often re-assessment. If the crypto library is linked into the safety image, an algorithm swap is a safety change. Thales notes TÜV/SIL recertification "adds years per family."\[16\]
3. **The protocol standards come first, and they have not moved.** Thales: "OEMs cannot ship compliant firmware before the standards move."\[16\]
4. **The economics are misaligned.** The asset owner bears the risk, the OEM controls the firmware, the integrator holds the configuration, and the standards body controls interoperability. Nobody owns the whole trust chain, so nobody pays for its renewal.
5. **Real-time determinism rules out large handshakes in the data path.** GOOSE trip messages must arrive within a few milliseconds (Thales cites GOOSE < 4 ms). Thales' conclusion: "Deterministic protection traffic (GOOSE / SV) is not the migration target — PQC protects key distribution and boundary trust only."\[16\]
6. **Physics and radio limits.** An IEEE 802.15.4 frame is 127 bytes; a single ML-DSA-65 signature (3,309 bytes) spans dozens of frames, and every extra frame raises the chance a handshake fails on a lossy link.\[22\]

## The second- and third-order cascade

Moving from ECDSA (64-byte signature) to ML-DSA-65 (3,309-byte signature, 1,952-byte public key) or ML-DSA-87 (4,627/2,592 bytes) sets off a chain:

- **Larger image headers:** roughly 7 KB more per signature for ML-DSA-87 (wolfBoot i.MX95); hybrid dual signatures add more.\[23\]
- **Slot and memory layout:** header growth can push an A/B layout past a sector boundary; verification RAM rises (ML-DSA-44 verify needs 8.9 KB of stack in pqm4's fast variant)\[8\] and can collide with statically allocated RTOS memory.
- **Partition maps and bricking risk:** changing the partition map usually needs a bootloader update, the riskiest field operation, requiring a maintenance window.
- **Delivery over slow links:** larger bundles and certificate chains take longer over narrowband backhaul, meaning longer exposure windows and more failed transfers.
- **Certification and budget:** a firmware change on a safety function triggers recertification, budgeted per product family; missing the operator's capex cycle slips migration by years.
- **Engineering tools:** workstations and configuration tools with fixed certificate buffers must change too.
- **Hybrid adds downgrade risk:** Thales warns that "unalarmed fallback to classical is an adversary-selectable downgrade," so every hybrid deployment needs downgrade detection.\[16\]

## Industry misconceptions

| Common belief | Reality |
|---|---|
| "PQC is too slow for microcontrollers." | Mostly false for ML-KEM and ML-DSA verification on Cortex-M4 and above. The binding limits are signing stack, signature size on the wire, and side-channel protection. |
| "We're air-gapped, so quantum doesn't matter." | Thales: "Air-gapped does not mean crypto-free … trust still crosses via: updates, backups, vendor tools, engineering access, signed firmware."\[16\] |
| "HNDL is the main risk." | For telemetry, usually low-value. For firmware-signing roots, vendor remote-access sessions, engineering project files and long-lived keys, high. |
| "Crypto-agility means supporting multiple algorithms." | Real agility needs headroom in sizes, buffers, slots and RAM, plus a renewable root. Thales: "Agility ends at vendor microcode: Class C never becomes agile."\[16\] |
| "Hybrid is always safer." | Hybrid key exchange is cheap insurance. Hybrid signatures double sizes, have complex security semantics (per NIST),\[1\] and invite downgrades. ASD does not recommend hybrid long-term.\[24\] |
| "QKD solves the problem." | QKD does not authenticate the parties. ASD states QKD is not supported for secure communications; NSA and NCSC prioritise PQC.\[16\]\[24\] |

## What an experienced OT engineer would reject that a cryptographer finds reasonable

- **Fail-closed on a failed handshake.** For a protection relay, a lost connection can be more dangerous than an unauthenticated one. Thales lists "Fail-open/closed per boundary; alarm on fallback."\[16\]
- **Frequent re-keying that forces reconnects.** Reconnect storms interact with failsafe timers; Thales asks for "P95 latency vs failsafe timers."\[16\]
- **Active scanning for crypto discovery.** Thales: "no active scanning at lower OT levels."\[16\]
- **"Just update the firmware."** Outage windows may come once every few years.

## What a cryptographer sees that OT practitioners often miss

- **Stateful signature misuse.** Reusing an LMS/XMSS one-time key, e.g., after restoring an HSM from backup or a cloned build server, can enable forgery. State management is an operational discipline.
- **Entropy at first boot.** Devices generating keys before the TRNG has accumulated entropy have historically produced shared or weak keys; ML-KEM encapsulation and masking add randomness demand.
- **Side channels in fielded devices.** Masking ML-KEM costs about 3.5× in cycles at first order; masking AES is comparatively cheap.\[25\] Physically exposed devices need protected implementations.
- **Downgrade and negotiation attacks** in mixed fleets.
- **Long-term secrets inside "non-confidential" OT data:** engineering files, network maps and embedded credentials stay valuable for decades.

---

# Part IV — The State of the Art

## Standards and policy status (as of 5 November 2026)

| Item | Status | Notes |
|---|---|---|
| FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA | Final, 13 Aug 2024\[26\]\[27\]\[28\] | ML-KEM-768 named recommended default in IR 8547 final\[1\] |
| FIPS 206 FN-DSA (Falcon) | Not final; NIST "is developing a FIPS"\[18\] | Draft submitted for approval 28 Aug 2025; sources conflict on whether the public draft is out; CAs will not ship until final\[29\]\[30\] |
| HQC (expected FIPS 207) | Selected 11 Mar 2025; final planned for 2027\[31\]\[32\] | NIST presented "FIPS 207: HQC-KEM" Sept 2025; leaning toward seed-only private keys; no confirmed public draft found\[33\]\[34\]\[35\] |
| NIST IR 8547 | **Final, 27 Oct 2026** | Deprecated after 2030, disallowed after 2035 at all key sizes; Ascon (SP 800-232) approved; hybrid KEMs validatable\[1\] |
| NIST CSWP 39 (crypto agility) | Update final 29 June 2026\[36\] | |
| NIST SP 800-208 (LMS/XMSS) | Final 2020\[37\] | Basis for CNSA 2.0 firmware signing |
| NSA CNSA 2.0 | Firmware/software signing: prefer by 2025, exclusive by 2030; networking exclusive by 2030; OS and web/cloud by 2033; all NSS by 2035\[37\]\[38\]\[39\] | ML-KEM-1024, ML-DSA-87, LMS/XMSS (LMS SHA-256/192 recommended)\[39\] |
| US EO 14412 / OMB M-26-15 | June 2026 | HVAs: PQC key establishment by 31 Dec 2030, signatures by 31 Dec 2031\[1\] |
| EU Coordinated Implementation Roadmap | 23 June 2025 | Start by end-2026; high-risk use cases by end-2030; "as many systems as practically feasible" by 2035\[38\]\[40\]\[41\] |
| UK NCSC | Discovery by 2028; priority migration 2028–31; complete 2031–35\[38\] | |
| Australia ASD ISM | Cease traditional asymmetric crypto by end-2030\[42\] | Approves ML-KEM-768/1024, ML-DSA-65/87; hybrid not recommended long-term; QKD not supported\[43\] |
| Canada | Non-classified federal IT by 2035\[38\] | |
| IETF | RFC 9881 (ML-DSA in X.509, Oct 2025); RFC 9909 (SLH-DSA in X.509, Dec 2025);\[44\] composite signatures in RFC Editor queue;\[45\] X25519MLKEM768 widely deployed | IKEv2 ML-KEM and EDHOC PQC work active |

## Industrial protocol readiness (the real bottleneck)

| Protocol/standard | PQC status (Nov 2026) | Evidence |
|---|---|---|
| OPC UA | No PQC SecurityPolicy; newest asymmetric policies are ECC (v1.05)\[46\] | OPC 10000-2 release 1.05.06 (22 Oct 2025) says only "new security policies are composed to support new algorithms"; PQC-OPC-UA work is academic (IACR ePrint 2021/1563, ProVerif-verified)\[47\]\[48\]\[49\]\[50\] |
| IEC 62351 (TC57 WG15) | No PQC measures\[51\] | IEC 62351-9:2023: "at this time being no specific measures are provided"; annex B.11 discusses PQC\[3\]\[52\] |
| DNP3-SAv6 (IEEE 1815) | Draft "designed to accommodate" PQC in association handshake; sessions already symmetric\[5\] | DNP Users Group workshop notes, 31 Oct 2024; "under final review before IEEE ballot"\[4\]\[5\] |
| ODVA CIP Security | No public PQC plans | 22 Oct 2026 release on TÜV certification to IEC 62443-4-2 SL-C 3\[6\] |
| AUTOSAR SecOC / TLS | Gap acknowledged; SecOC symmetric (CMAC)\[7\] | AUTOSAR FO R24-11 Security Overview |
| ERTMS/ETCS | No public PQC plan found | UNISIG SUBSET-137 classical PKI over TLS\[20\] |

**What this means.** The parts of OT that are already symmetric (DNP3-SAv6 sessions, SecOC, LoRaWAN, GOOSE with IEC 62351-6 MACs) are quantum-resistant in their data path; only their key distribution must change. That is a strong argument for migrating key management, not data paths.

## Measured performance (Cortex-M class)

| Operation | Implementation / platform | Cycles | Memory | Source type |
|---|---|---|---|---|
| ML-KEM-768 keygen / encaps / decaps | pqm4 m4fspeed, Cortex-M4 | 642,096 / 658,754 / 707,827\[8\] | ~6.7 KB peak stack (hybrid X25519 build)\[53\] | Measured (pqm4; ePrint 2026/1414) |
| ML-KEM-768 full handshake | Reference C, RP2040 Cortex-M0+ | 7,530k (56.6 ms) vs 4,163k on M4\[54\] | — | Measured (arXiv 2603.19340); M0+ only 1.81× slower\[54\] |
| ML-DSA-44 verify | pqm4 m4f / m4fstack | 1,421,623 / 3,242,333\[8\] | 8,912 B / 2,712 B stack\[8\] | Measured (pqm4) |
| ML-DSA-65 verify | pqm4 m4f | 2,415,944\[8\] | 9,888 B stack\[8\] | Measured (pqm4) |
| ML-DSA-44 sign | pqm4 m4f | — | 44,816 B stack\[8\] | Measured (pqm4) |
| ML-DSA-65 sign | Cortex-M4 | ~17.1 M\[53\] | — | Measured (ePrint 2026/1414) |
| FN-DSA-512 keygen / sign / verify | Cortex-M4 | 75.1 M / 34.4 M / 6.5 M\[53\] | — | Measured (ePrint 2026/1414) |
| SLH-DSA-SHA2-128s verify | pqm4 clean | 7,471,794\[8\] | 1,968 B stack\[8\] | Measured (pqm4) |
| HQC (all three operations) | Cortex-M4 | 19.6–74.5 M total vs 3.7–8.8 M for lattice KEMs\[53\] | — | Measured (ePrint 2026/1414) |
| First-order masked ML-KEM-768 decaps | Cortex-M4 | 2,978,441\[55\]\[56\] | — | Measured (Heinz, Kannwischer et al.) |
| ML-DSA-87 secure boot verify | wolfBoot, i.MX95 Cortex-M7, 800 MHz | 4,201,179 (5.25 ms); 2.4× ECDSA P-256\[23\] | .text 21,608 B\[23\] | Vendor-measured (wolfSSL) |
| LMS/XMSS verify | — | **Not in pqm4** | — | Gap: no neutral benchmark |

**Sizes (bytes):** RSA-2048 key and signature 256 each. ECDSA P-256 key 64–65, signature 64.\[57\] ML-KEM-768 encapsulation key 1,184, ciphertext 1,088.\[58\] ML-DSA-44 key 1,312, signature 2,420; ML-DSA-65 1,952/3,309; ML-DSA-87 2,592/4,627.\[57\] SLH-DSA-128s key 32, signature 7,856.\[59\]\[60\] FN-DSA-512 signature about 666.\[28\] LMS public keys about 48–56; a single-tree LMS SHA-256/192 signature with h=10, w=8 is about 900 bytes (my calculation from SP 800-208 formulas).

**Interpretation.** For firmware verification, LMS gives the smallest public key, a sub-kilobyte signature and hash-only verification, so a ROM needs only a hash engine most MCUs already have. That makes LMS the most natural root anchor for constrained devices, subject to signing-side state management. ML-DSA verification is fast but expensive in bytes. FN-DSA has the smallest lattice signatures, but floating-point Gaussian sampling makes signing hard to protect, and it is not final.\[61\] SLH-DSA is the conservative stateless backup root. HQC is about 5–10× more expensive than ML-KEM on the M4: a backup, not an embedded default.\[53\]

**Network effects.** On IEEE 802.15.4, an ML-KEM-768 exchange needs 18 frames.\[62\] On LoRa with a 51-byte payload, ML-KEM-1024 needs 62 packets, and handshake success can fall toward 50% even with high per-packet delivery (MDPI *Future Internet*, 2026).\[22\] ML-KEM-1024 cannot fit an unfragmented IKE_SA_INIT on a 1,500-byte path;\[58\] Thales' lab demo used RFC 7383 IKEv2 fragmentation at MTU 1,280.\[16\] When Chrome 124 enabled the hybrid key exchange (the pre-standard X25519Kyber768 draft, not final ML-KEM), the larger ClientHello split into two packets, and the Chromium Blog (23 May 2024) reported "a 4% median latency increase to all TLS handshakes in Chrome on desktop." On constrained links, **bytes, not cycles, are the binding constraint.**

**Signature-free handshakes are the key embedded insight.** In PQ-EDHOC tests on an nRF52840 over BLE, Pocero Fraile et al. ("Enabling Quantum-Resistant EDHOC") found ML-KEM-512 suites paired with HAWK1 and FALCON1 ran "19% and 54% faster" than secp256r1/ECDSA, at about 13% more RAM. A signature-free, KEM-authenticated EDHOC has also been proposed, both in the IEEE paper "Reinventing EDHOC for the Post-Quantum Era" and in IETF draft-ietf-lake-authkem-edhoc. Like KEMTLS: authenticate with KEMs, keep signatures for long-lived certificates and firmware.

## Production-ready vs experimental

- **Production-ready now:** hybrid X25519+ML-KEM-768 in TLS 1.3 and IKEv2 at gateways;\[16\] ML-DSA and LMS/XMSS firmware verification (wolfBoot ships all three plus hybrid dual signing);\[63\]\[64\] XMSS-protected TPM firmware updates (Infineon OPTIGA TPM SLB 9672, at least 10-year availability);\[65\] PQC-capable HSMs;\[66\] ML-DSA certificates (RFC 9881);\[67\] Ascon; CycloneDX 1.6 CBOM.
- **Maturing:** composite certificates; PQC TPMs (Infineon's next generation "embedding … ML-KEM and ML-DSA");\[68\] masked ML-KEM/ML-DSA on MCUs; PQ-EDHOC and Merkle-tree certificates.
- **Experimental:** PQC in OPC UA, IEC 62351, DNP3, CIP and SecOC profiles; FN-DSA in production; HQC on embedded; automated binary crypto discovery at OT scale; remote root-of-trust renewal.

## Leading players (what they solve, where they stop)

- **Silicon and IP** (Infineon, NXP, ST, Microchip, Silicon Labs, Rambus, Synopsys, Secure-IC, PQShield, PQSecure, Crypto Quantique): accelerators, masked cores, PQC-ready secure elements. *Gap:* cannot rescue the installed base.
- **HSM, PKI and code signing** (Thales, Entrust, Utimaco, Keyfactor, DigiCert, Venafi/CyberArk): Siemens demonstrated PQC software signing with Keyfactor (SPHINCS+, 2023).\[69\] *Gap:* IT-centric; fleet-scale HBS state management is rare.
- **OT visibility** (Dragos, Claroty, Nozomi, Armis, Forescout): *Gap:* inventory devices, not crypto dependencies inside firmware.
- **Embedded TLS and boot** (wolfSSL/wolfBoot, mbedTLS/TF-M, MCUboot, Segger): *Gap:* no fleet-level lifecycle orchestration.
- **Open source:** pqm4, PQClean, liboqs/OQS, libcrux/HACL* (formally verified ML-KEM), SLOTHY (up to 32% ML-DSA and 27% ML-KEM speed-ups on Cortex-M7).\[70\]

**Whitespace:** no one sells a vendor-neutral, safety-aware, offline-capable service for renewing trust anchors and keys across a mixed OT fleet.

---

# Part V — The Future

## 5 years (2026–2031): boundaries and roots

- **Gateways:** hybrid ML-KEM becomes mandatory at gateways, remote access, site links and IDMZs (Thales "Class A").
- **New products** ship with LMS/XMSS or ML-DSA verification, two or more independent root anchors, slots sized for 8–16 KB of signature metadata, and PQC-capable TPMs or secure elements.
- **Procurement is the lever:** "include PQC readiness and crypto-agility requirements in every OT RFP today" (Thales);\[16\] in the US it flows down via the FAR rule and CISA CBOM elements.\[1\]
- **Standards:** protocol bodies publish first PQC key-management profiles (my projection, not yet evidenced).
- **Becoming obsolete:** single-root classical secure boot; lifetime factory IDevIDs; PSK-only remote access; unalarmed hybrid fallback.

## 10 years (2031–2036): the hard middle

- **2035 disallowance** arrives; Class B and C devices need compensating architecture or replacement, and documented risk acceptance becomes routine audit work.\[1\]
- **A second transition may begin:** hybrid retired toward pure PQC, or, if lattices weaken, migration to HQC, SLH-DSA or new signatures.
- **Mandatory capabilities:** remote root renewal; signed CBOMs as procurement evidence; continuous crypto-posture monitoring; HBS signing-state custody.

## 15–20 years (2036–2046): renewable trust as infrastructure

- Trust renewal becomes an operated utility, like time synchronisation or patch distribution.
- Devices carry a "cryptographic constitution": hash-anchored rules for transferring authority to new algorithms.
- **Becoming obsolete:** algorithms as product features; manual certificate management; per-vendor proprietary signing.

## The second migration

SIKE reached NIST's fourth round and was then broken by a classical key-recovery attack: Castryck and Decru (KU Leuven, IACR ePrint 2022/975, July 2022) report that their implementation "breaks SIKEp434… in about ten minutes on a single core." Rainbow fell the same year: Ward Beullens (IBM Research, "Breaking Rainbow Takes a Weekend on a Laptop," CRYPTO 2022) recovered the SL1 secret key "after on average 53 hours (one weekend) of computation time on a standard laptop." Lattices have far more cryptanalysis behind them, but hash-based signatures rest on the most conservative assumption available. **Design principle: anchor long-lived roots in hash-based schemes, use lattices for performance-sensitive sessions, and make the session layer replaceable under authority from the root.**

---

# Part VI — Radical Possibilities: 22 Innovation Hypotheses

Scores are my judgement on a 1–5 scale: N = novelty, P = technical plausibility, I = impact. **[challenges foundation]** marks direct challenges to standard assumptions.

**H1. Hash-anchored "trust constitution" in ROM [challenges foundation]** (N4 P4 I5)
- *Mechanism:* ROM holds hashes of several independent roots (classical, LMS, XMSS, SLH-DSA); a quorum can sign a "succession manifest" that installs a new root and retires an old one.
- *Addresses:* unchangeable fused anchors. *Must validate:* quorum semantics, rollback protection, partial-compromise behaviour. *Barriers:* the ROM verifier must be correct forever. *Value:* turns a replacement event into a software event for silicon vendors and OEMs.

**H2. Gateways as cryptographic proxies for frozen endpoints [challenges "every device implements PQC"]** (N2 P5 I5)
- *Mechanism:* bump-in-the-wire terminates PQC on the WAN side, speaks legacy protocols on a short protected segment. *Barriers:* the last metre stays classical. *Value:* deployable unilaterally by asset owners today.

**H3. Signature-free field devices [challenges "PKI everywhere"]** (N4 P4 I4)
- *Mechanism:* devices authenticate only with KEMs (KEMTLS/PQ-EDHOC style) and symmetric keys; only the root signs firmware. *Addresses:* signing stack (about 45 KB) and side-channel cost. *Barriers:* standards adoption.

**H4. Symmetric-key infrastructure (KDC/Kerberos-style) for closed OT cells [challenges "public key is required"]** (N3 P4 I4)
- *Mechanism:* a hardened, replicated KDC issues short-lived AES keys; PQC protects only the KDC's links and enrolment. Shor does not apply. *Barriers:* KDC is a single point of compromise, needing threshold or HSM protection. *Value:* plants, substations, rail; DNP3-SAv6's symmetric sessions already point this way.\[5\]

**H5. Threshold/MPC custody for stateful HBS signing [challenges "HSM is enough"]** (N4 P3 I4)
- *Mechanism:* LMS state across separated HSMs, consensus before any one-time key index is used. *Addresses:* state reuse. *Value:* makes CNSA 2.0 firmware signing operationally safe.

**H6. Binary crypto lifting with ML/LLM assistance** (N3 P4 I4)
- *Mechanism:* decompile firmware; detect constants (S-boxes, curve parameters, Keccak round constants), call graphs and buffer sizes; output a CBOM with hard-coded size limits flagged. *Barriers:* obfuscation, encrypted images, hallucination (needs symbolic confirmation).

**H7. Cryptographic digital twin** (N3 P4 I4)
- *Mechanism:* a graph linking every key, certificate, root, protocol, buffer limit and outage window; simulates "what breaks if we swap X" and schedules migration within maintenance windows.

**H8. Separating cryptography from the safety function [challenges "crypto change means safety recert"]** (N3 P3 I5)
- *Mechanism:* crypto in an isolated partition or co-processor (TrustZone-M, separate core) with a freedom-from-interference argument, so crypto updates do not touch the SIL image. *Must validate:* assessor (TÜV, exida) acceptance. *Value:* perhaps the biggest single cost lever.

**H9. Delegated verification ("verify-once, attest-many")** (N3 P3 I3)
- A capable gateway verifies a large PQC signature and issues short symmetric MAC tokens for constrained nodes on 802.15.4 and LoRa.

**H10. Merkle-batched fleet updates** (N3 P4 I3)
- One root signature covers a Merkle tree of per-variant manifests; each device receives a log-size proof.

**H11. "Crypto headroom" as a design rule [challenges "agility = algorithm list"]** (N2 P5 I4)
- Specify maximum sizes, not algorithms: every parser, slot and buffer sized for, say, 16 KB signatures and 4 KB keys, tested with fuzzing. Cheap now, priceless later.

**H12. Continuous crypto posture as a managed service [challenges "migration is a project"]** (N3 P4 I5)
- A subscription that continuously inventories, scores, renews and evidences crypto, as EDR did for endpoints; recurring revenue matching recurring transitions.

**H13–H15. Physical-layer key agreement, QKD backbones, and QRNG entropy services** (N1–4 P2–4 I1–2)
- Supplements, not strategies. Channel-reciprocity keys are weak in static plants; QKD still needs PQC authentication and NSA, NCSC and ASD advise against relying on it; verified entropy injection at commissioning is useful hygiene, but any validated TRNG plus DRBG suffices.

**H16. Forward-secure, time-bounded device credentials [challenges "lifetime IDevID"]** (N3 P4 I3)
- Short-lived LDevIDs renewed via KEM-authenticated enrolment; algorithms can change at renewal.

**H17. Formally verified, size-agnostic parsers** (N3 P4 I3)
- ASN.1/CBOR/TLV parsers generated from verified specifications (EverParse-style), with no hard-coded sizes.

**H18. Insurance-priced crypto risk [challenges "compliance drives spend"]** (N3 P3 I4)
- Insurers price CBOM-derived quantum exposure, creating a market deadline independent of regulation.

**H19. Hybrid-strict policy enforcement with downgrade telemetry** (N2 P5 I3)
- Gateways refuse classical-only negotiation and alarm (as Thales demonstrated).

**H20. Cross-vendor "trust escrow" consortium [challenges "OEM owns the root"]** (N4 P2 I5)
- An independent escrow holds secondary roots and can authorise renewal if an OEM exits. *Barriers:* liability, governance, OEM resistance.

**H21. Ascon-based lightweight channels for 8/16-bit legacy MCUs** (N2 P4 I3)
- Retrofit Ascon AEAD plus pre-shared keys distributed by H4: quantum-resistant without public-key operations.

**H22. Deterministic, hash-only verification boot ROMs** (N2 P5 I3)
- ROMs perform only LMS/XMSS/SLH-DSA verification, which needs no secrets, avoiding RNG, floating-point and side-channel issues entirely.

**Ranking (composite):** H1, H12, H8, H2, H4, H3, H6, H7, H5, H20, H11, H16; the rest are supplements.

**What would disprove the core hypotheses:** H1 fails if formal analysis shows quorum succession creates unacceptable rollback or attack surface. H8 fails if assessors refuse freedom-from-interference arguments for crypto partitions. H4 fails if KDC availability cannot meet IEC 61508 diagnostic coverage targets. H6 fails if precision on stripped OT firmware stays below about 80% even with symbolic confirmation.

---

# Part VII — Commercial Opportunities

## Market sizing: the headline numbers do not agree

| Publisher | 2025 base | Forecast | Method note |
|---|---|---|---|
| MarketsandMarkets | USD 0.42 B | USD 2.84 B by 2030 (46.2% CAGR)\[71\] | Top-down/bottom-up from vendor revenues |
| Mordor Intelligence | USD 0.88 B\[72\] | USD 4.60 B by 2030\[72\] | Undisclosed in summary |
| IMARC | USD 470.2 M\[73\] | USD 19.17 B by 2034\[73\] | Undisclosed in summary |
| Grand View Research | USD 1.6 B | USD 20.5 B by 2033\[74\] | Undisclosed in summary |

The fourfold disagreement on the 2025 base shows "PQC market" has no shared definition. None breaks out OT. Use them only as momentum signals.

## Bottom-up OT/embedded estimate (my model; assumptions explicit)

- **OEM firmware-signing and lifecycle platforms:** 1,000–3,000 OEMs shipping signed firmware into industrial, energy, building, medical and automotive-tier markets, at USD 150k–1M per year each: **USD 0.15–3 B per year**.
- **Asset-owner boundary controls and crypto posture:** 10,000–30,000 critical-infrastructure operators with meaningful OT estates, at USD 50k–300k per year: **USD 0.5–9 B per year**, realistically at the low end near-term.
- **Silicon content:** a few dollars per device across hundreds of millions of devices per year, captured by semiconductor incumbents.
- **Synthesis:** a realistic early-2030s OT/embedded software and services opportunity in the **low single-digit USD billions per year**. Disproof test: if the FAR rule, NIS2 transpositions and IEC 62443 revisions fail to reference PQC by 2028, the asset-owner figure collapses toward the low end.

## Who owns the problem, who pays, who influences

- **OEM product security and engineering:** owns firmware signing and roots; driven by CNSA 2.0, the EU Cyber Resilience Act and customer RFPs.
- **Asset owner CISO and OT engineering:** owns boundary and risk; influenced by regulators (NERC CIP, NIS2, TSA pipeline directives), insurers and integrators.
- **System integrators:** deployment gatekeepers. Partner, don't compete.
- **Most urgent sectors:** defence-industrial and federal-adjacent suppliers; electric grid; pipelines and water; rail (ERTMS key management); automotive (OTA signing for 15-year vehicles); medical implants (no update path).

## Product opportunities (software-first)

1. **HBS Signing Custody Service:** stateful LMS/XMSS signing with threshold state, audit trail and CNSA 2.0 evidence; my estimated pricing USD 50k–250k per year per product line. *Moat:* operational correctness.
2. **Boot and Update Kit:** MCUboot, wolfBoot and SUIT integrations with multi-root succession and slot-sizing tools; per-SKU plus royalties.
3. **OT Crypto Twin:** passive and binary discovery, CycloneDX 1.6 CBOM, dependency graph, outage-window scheduling; per site.
4. **Hybrid-Strict Gateway Policy Layer:** policy, downgrade telemetry and evidence on existing firewall and VPN vendors.
5. **Symmetric KDC for OT cells** for Class C fleets.
6. **Assurance evidence packs** for IEC 62443-4-1/4-2 and safety assessors.

**Barriers:** 12–24-month utility sales cycles; certification costs; incumbents bundling PQC "for free" with HSM or PKI renewals; OEM reluctance to share roots.

---

# Part VIII — The Blueprint: The Industrial Trust Plane

## Thesis

Build the **operating layer for cryptographic authority** in long-lived infrastructure: a vendor-neutral system that decides, proves and renews *who may change what* across a fleet, with algorithms as replaceable parts.

## Architecture (five planes)

1. **Root plane (in device):** multi-root, hash-anchored ROM or bootloader verifier (H1, H22) with classical, LMS and SLH-DSA roots and quorum-signed succession manifests; crypto headroom (H11). First on wolfBoot or MCUboot for Cortex-M33/M55 and i.MX-class parts.
2. **Authority plane (cloud/HSM):** threshold-custodied HBS signing (H5); Merkle-batched manifests (H10); succession policy.
3. **Session plane:** hybrid-strict gateways (H2, H19); KEM-authenticated enrolment and short-lived credentials (H3, H16); symmetric KDC for closed cells (H4).
4. **Knowledge plane:** binary crypto lifting plus a cryptographic digital twin (H6, H7) producing signed CBOMs.
5. **Assurance plane:** crypto-partition safety arguments and evidence packs (H8); downgrade and posture telemetry.

## Innovation principles

- Hash for roots, lattices for sessions, symmetric for data.
- Renewal is a feature; immutability belongs to the *rules*, not the keys.
- Never fail unsafe: availability policy is set per boundary.
- Evidence is a product: every action emits auditable proof.

## MVP (12–18 months)

- **For OEMs:** (a) HBS signing custody with state safety; (b) multi-root wolfBoot/MCUboot integration with a succession-manifest specification on two MCU families; (c) a slot and parser headroom analyser.
- **For one utility pilot:** (d) passive CBOM plus binary-lifting report for one substation design.

## Validation plan

1. Formal model of succession (Tamarin/ProVerif) and fuzzing of manifest parsers.
2. Fault-injection and power-loss testing during root rotation.
3. Benchmarks on Cortex-M0+/M4/M33/M7: boot time, flash, RAM.
4. Safety-assessor pre-assessment of the crypto-partition argument.
5. Two OEM design wins and one utility pilot as commercial proof.

## Moat

- Correctness of HBS state custody (failures are catastrophic, so trust compounds).
- An installed base of succession roots: once a device's ROM trusts our manifest format, renewal runs through us.
- Assessor-accepted safety arguments.
- A cross-vendor CBOM and firmware-knowledge graph.

---

# Part IX — The Strategic Verdict

## Genuinely important

Firmware-signing roots and device identity; remote access and gateway boundaries; protocol bodies adding PQC key-management profiles; HBS state management; crypto headroom in every new design.

## Overhyped

QKD for OT; "quantum-safe" telemetry encryption at Level 0/1; top-down market forecasts; treating MCU algorithm performance as the main barrier; one-time "migration projects" sold as if there will be no second transition.

## Deepest unresolved questions

1. How to renew a fused root of trust remotely and safely, with a formal proof.
2. Whether safety assessors will accept crypto isolation from SIL functions.
3. Long-term lattice security margin, and how fast backup families can be deployed.
4. Affordable higher-order side-channel protection for ML-KEM and ML-DSA on cheap MCUs.
5. Reliable binary-level crypto discovery at OT scale.
6. Governance of orphaned devices whose OEM has disappeared.

## Technical opportunity map

| Opportunity | Time to value | Defensibility | Who pays |
|---|---|---|---|
| HBS signing custody | 0–2 yrs | High | OEMs |
| Hybrid-strict gateway policy | 0–2 yrs | Low–medium | Asset owners |
| Crypto twin + binary CBOM | 1–3 yrs | Medium–high | Asset owners, insurers |
| Multi-root succession boot | 2–5 yrs | Very high | Silicon vendors, OEMs |
| Crypto/safety partition assurance | 2–5 yrs | High | Safety OEMs |
| OT symmetric KDC | 2–4 yrs | Medium | Utilities, rail |
| Trust escrow consortium | 5+ yrs | Very high | Industry, regulators |

## Breakthrough roadmap

- **Research first:** formal succession protocols; HBS threshold state; KEM-only industrial handshakes.
- **Prototype next:** multi-root wolfBoot/MCUboot; passive OT CBOM plus binary lifting; hybrid-strict gateway telemetry.
- **Test:** fault injection during rotation; LoRa and 802.15.4 handshake reliability; assessor pre-review.
- **Validate commercially:** OEM design wins tied to CNSA 2.0 and CRA; a utility pilot tied to EU 2030 high-risk deadlines.

## The ultimate strategic thesis

**The single most important unsolved problem is renewing roots of trust in devices that are already deployed.** The industry is solving "which algorithm," which is already answered. It has barely begun on "how does a 30-year device safely transfer authority to algorithms that do not exist yet?" The most compelling opportunity is to make that transfer routine: hash-anchored, quorum-governed root succession in the device, plus a vendor-neutral service that custodies, exercises and proves that authority across fleets. If this works, PQC migration and every later cryptographic migration become operations rather than replacement programmes.

## Caveats

- **Recent policy facts come partly from secondary sources.** Final IR 8547 contents and EO 14412 / M-26-15 details are drawn mainly from the Cloud Security Alliance research note of 30 Oct 2026;\[1\] verify against primary documents.
- **FN-DSA and HQC status is contested.** Sources disagree on whether public drafts of FIPS 206 and the HQC standard are out.
- **Some benchmarks are vendor-measured.** The wolfBoot i.MX95 numbers are vendor-measured; pqm4 has no neutral LMS/XMSS benchmark.
- **Protocol-status findings are not proof of absence.** Members-only drafts (DNP3, IEC) may contain unseen PQC work; automotive and rail coverage was thin.
- **Market model inputs are mine.** OEM counts, operator counts and spend per entity are assumptions, not sourced data.
- **Quantum resource estimates beyond Gidney (2025) are unverified preprints.**

## Sources

1. [NIST IR 8547 Final: Post-Quantum Deadlines Become Vendor Requirements](https://labs.cloudsecurityalliance.org/research/csa-research-note-nist-ir8547-pqc-transition-20261030-csa-st/)
2. [A Comprehensive Formal Security Analysis of OPC UA Vincent Diemunsch](https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-772-diemunsch.pdf)
3. [IEC 62351-9:2023](https://webstore.iec.ch/en/publication/66864)
4. [DNP Users Group](https://www.dnp.org/API/Evotiva-UserFiles/FileActionsServices/DownloadFile?ItemId=5041&ModuleId=9582&TabId=66)
5. <https://www.dnp.org/API/Evotiva-UserFiles/FileActionsServices/DownloadFile?ItemId=5140&ModuleId=9582&TabId=66>
6. [CIP Security Earns IEC 62443-4-2 Certification, Strengthening and Streamlining Cybersecurity for EtherNet/IP Products - ODVA](https://www.odva.org/news/cip-security-earns-iec-62443-4-2-certification-strengthening-and-streamlining-cybersecurity-for-ethernet-ip-products/)
7. [Explanation of Security Overview AUTOSAR FO R24-11 Document Title](https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_EXP_SecurityOverview.pdf)
8. [pqm4/benchmarks.md at master · mupq/pqm4 · GitHub](https://github.com/mupq/pqm4/blob/master/benchmarks.md)
9. [pqm4 benchmarks for post-quantum schemes on Cortex-M4](https://irishquantum.com/blog/pqm4-cortex-m4-benchmarks-post-quantum/)
10. [UAV Traffic Management : A Survey On Communication Security](https://arxiv.org/pdf/2211.05640)
11. [Google researcher estimates RSA-2048 could be broken with under a million qubits · Quantum computing · Quantum Timeline](https://quantumtimeline.org/milestones/2025-gidney-rsa-under-million-qubits/)
12. [How to factor 2048 bit RSA integers with less than a million noisy qubits](https://www.alphaxiv.org/abs/2505.15917)
13. [Quantum computers may crack RSA encryption with fewer qubits than expected](https://phys.org/news/2025-05-quantum-rsa-encryption-qubits.html)
14. [Reading Gidney’s 2025 RSA-2048 resource estimate](https://xdc.network/labs/reading-gidney-rsa-2048/)
15. [Reading the 2025 Gidney result on RSA-2048](https://xdc.network/reading-gidney-rsa-2048)
16. [Post-Quantum Cryptography for ICS Gateways](https://isomer-user-content.by.gov.sg/274/98d2be5d-a8b8-44a6-90bf-5f27de67c0b0/OTCEP_2026_PQC_for_ICS_Gateways_v3.4_final%20V2.pdf)
17. [Post-Quantum Considerations For Operational Technology](https://www.scribd.com/document/830636612/Post-Quantum-Considerations-for-Operational-Technology-508)
18. [NIST IR 8547 Final: What Changed From the Draft](https://postquantum.com/security-pqc/nist-ir-8547-final/)
19. [Specification of Secure Onboard Communication Protocol AUTOSAR FO R20-11](https://www.autosar.org/fileadmin/standards/R20-11/FO/AUTOSAR_PRS_SecOcProtocol.pdf)
20. [Cyber-Security-Maßnahmen für ERTMS aus Sicht der ... - Incyde](https://incyde.com/wp-content/uploads/2024/08/57_72_Koecher_Poschinger.pdf)
21. [Siemens PLC Software: Hardcoded Cryptographic Keys Uncovered](https://claroty.com/team82/research/the-race-to-native-code-execution-in-plcs-using-rce-to-uncover-siemens-simatic-s7-1200-1500-hardcoded-cryptographic-keys)
22. [Evaluating Post-Quantum Cryptography in IoT Networks: Communication, Fragmentation, and Reliability](https://par.nsf.gov/biblio/10715228-evaluating-post-quantum-cryptography-iot-networks-communication-fragmentation-reliability)
23. [Post-Quantum Secure Boot on the NXP i.MX95 Cortex-M7 - wolfSSL](https://www.wolfssl.com/post-quantum-secure-boot-on-the-nxp-i-mx95-cortex-m7/)
24. [Australia: ASD Sets 2030 PQC Deadline](https://qpf.org/australia-asd-pqc-2030-deadline/)
25. [Masking Kyber: First- and Higher-Order Implementations](https://eprint.iacr.org/2021/483.pdf)
26. [Operationalising Post Quantum TLS Automated Configuration Profiling and Hybrid PQC Deployment in Financial Infrastructure](https://arxiv.org/pdf/2605.17955)
27. [NIST Post-Quantum Cryptography Standardization](https://en.wikipedia.org/wiki/NIST_Post-Quantum_Cryptography_Standardization)
28. [FIPS 206 Draft: FN-DSA / FALCON Status](https://quantumsequrity.com/blog/fips-206-draft-deep-dive)
29. [Quantum-Ready FN-DSA (FIPS 206) Nears Draft Approval from NIST](https://www.digicert.com/blog/quantum-ready-fndsa-nears-draft-approval-from-nist)
30. [FN-DSA: Compact Post-Quantum Signatures](https://www.encryptionconsulting.com/fn-dsa-compact-post-quantum-signatures/)
31. [NIST Selects HQC as Fifth Algorithm for Post-Quantum Encryption](https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption)
32. [NIST PQC Standards: FIPS 203, 204, 205 and HQC](https://intellixbom.com/resources/qbom/nist-pqc-standards/)
33. [CSRC Presentations](https://csrc.nist.gov/presentations/2025/fips-207-hqc-kem)
34. [NIST leans toward seed-only keys for HQC in draft FIPS 207 · freenode](https://freenode.net/article/nist-leans-toward-seed-only-keys-for-hqc-in-draft-fips-207)
35. [NIST PQC Standards Guide: FIPS 203, 204, 205](https://www.arcqubit.ai/blog/nist-pqc-standards-guide)
36. [Post-Quantum Cryptography Project Publications](https://csrc.nist.gov/Projects/post-quantum-cryptography/publications)
37. [Architecting the CNSA 2.0 Transition Strategies](https://www.encryptionconsulting.com/cnsa-architectural-strategies/)
38. [PQC Transition Roadmaps & Guidance](https://pqshield.com/pqc-transition-roadmaps-and-guidance/)
39. [What Is CNSA 2.0?](https://www.encryptionconsulting.com/education-center/what-is-cnsa-2-0/)
40. [EU Coordinated Implementation Roadmap for PQC: dates and requirements](https://pqaudit.org/timelines/eu-pqc-roadmap/)
41. [Nothing Breaks: No Single Peer Can Soundly Gate Post-Quantum Delivery](https://arxiv.org/pdf/2609.07849)
42. [ACSC says to stay ahead of the quantum threat](https://www.govtechreview.com.au/content/gov-security/news/acsc-says-to-stay-ahead-of-the-quantum-threat-1479326493)
43. [Post-quantum cryptography: what ASD's 2026, 2028 and 2030 milestones mean for your organisation](https://cybercorp.com.au/latestinsights/10)
44. [ML-DSA Certificates Use X.509, But Aren't Yet For Public TLS.](https://quantumzeitgeist.com/ca-browser-ml-dsa-certificates-use/)
45. [ML-DSA (FIPS 204): Sizes, Certificates and PQC PKI](https://duokey.com/en/resources/ml-dsa-certificates-post-quantum-pki-guide-2026)
46. [A Comprehensive Formal Security Analysis of OPC UA∗ Vincent Diemunsch](https://eprint.iacr.org/2025/148.pdf)
47. [Towards Post-Quantum Security for Cyber-Physical Systems:](https://eprint.iacr.org/2021/1563.pdf)
48. [Towards post-quantum security for cyber-physical systems: : Integrating PQC into industrial M2M communication1: Journal of Computer Security: Vol 30, No 4](https://dl.acm.org/doi/abs/10.3233/JCS-210037)
49. [OPC Unified Architecture - Part 2: Security Model - 4 OPC UA security architecture](https://reference.opcfoundation.org/specs/OPC-10000-2/4)
50. [OPC-10000-2](https://reference.opcfoundation.org/Core/Part2/v105/docs/)
51. [Review on PQC standardization activities Work Package 3 31th March, 2026](https://www.pqc.fi/file/repository/BLimPQC_WP3_review_on_PQC_standardization_activities_31032026.pdf)
52. [IEC 62351-9 Edition 2.0 2023-06 INTERNATIONAL STANDARD NORME INTERNATIONALE](https://cdn.standards.iteh.ai/samples/104224/51917181e4094f3abcc32b59a6928a3a/IEC-62351-9-2023.pdf)
53. [Evaluating Hybrid KEM/DSA for KpqC and NIST PQC on ARM Cortex-M4](https://eprint.iacr.org/2026/1414.pdf)
54. [Benchmarking NIST-Standardised ML-KEM and ML-DSA on ARM Cortex-M0+: Performance, Memory, and Energy on the RP2040](https://arxiv.org/html/2603.19340v5)
55. [First-Order Masked Kyber on ARM Cortex-M4 Report](https://kannwischer.eu/papers/2022_maskedkyber.pdf)
56. [\[PDF\] First-Order Masked Kyber on ARM Cortex-M4](https://www.semanticscholar.org/paper/First-Order-Masked-Kyber-on-ARM-Cortex-M4-Heinz-Kannwischer/06fdfbe9982338c571c177af9da178e9b86c3686)
57. [Merkle Tree Certificate Post-Quantum PKI for Kubernetes and Cloud-Native 5G/B5G Core](https://arxiv.org/pdf/2604.04191)
58. [Hybrid Post-Quantum IKEv2 on Embedded Automotive Platforms: Design, Implementation, and Evaluation](https://doi.org/10.3390/electronics15153340)
59. [(PDF) Enabling Quantum-Resistant EDHOC: Design and Performance Evaluation](https://www.researchgate.net/publication/390155853_Enabling_Quantum-Resistant_EDHOC_Design_and_Performance_Evaluation)
60. [Post-quantum signature schemes - Alin Tomescu](https://alinush.github.io/post-quantum-signatures)
61. [What Is FN-DSA (FALCON, FIPS 206)?](https://www.encryptionconsulting.com/education-center/fn-dsa-fips-206/)
62. [Evaluating Post-Quantum Cryptography in IoT Networks: Communication, Fragmentation, and Reliability](https://www.mdpi.com/1999-5903/18/6/316)
63. [Secure Boot on AMD Versal with wolfBoot - wolfSSL](https://www.wolfssl.com/secure-boot-on-amd-versal-with-wolfboot/)
64. [wolfBoot: Secure Boot now with support for FIPS 204 ML-DSA post-quantum signature algorithm - wolfSSL](https://www.wolfssl.com/wolfboot-secure-boot-now-with-support-for-fips-204-ml-dsa-post-quantum-signature-algorithm/)
65. [Infineon Launches World’s First TPM with a PQC-Protected Firmware Update Mechanism - Embedded Computing Design](https://embeddedcomputing.com/technology/security/software-security/infineon-launches-worlds-first-tpm-with-a-pqc-protected-firmware-update-mechanism)
66. [Securing Cryptography in the Age of Quantum Computing and AI: Threats, Implementations, and Strategic Response](https://arxiv.org/pdf/2603.06969)
67. [RFC 9881: Internet X.509 Public Key Infrastructure -- Algorithm Identifiers for the Module-Lattice-Based Digital Signature Algorithm (ML-DSA)](https://www.rfc-editor.org/info/rfc9881/)
68. [Infineon advances Physical AI security against quantum](https://www.infineon.com/press-release/2026/infxx202606-104)
69. [Software Signing in the Quantum Age Keyfactor Tech Days 2023](https://408597.fs1.hubspotusercontent-na1.net/hubfs/408597/2023-content/tech-days-presentations/Software%20Signing%20in%20the%20Quantum%20Age.pdf)
70. [Enabling Microarchitectural Agility: Taking ML-KEM & ML-DSA from Cortex-M4 to M7 with SLOTHY](https://dl.acm.org/doi/10.1145/3708821.3736210)
71. [Post-Quantum Cryptography (PQC) Market worth \$2.84 billion by 2030](https://www.prnewswire.com/news-releases/post-quantum-cryptography-pqc-market-worth-2-84-billion-by-2030--marketsandmarkets-302572135.html)
72. [Post-Quantum Cryptography Market Size, Share & 2030 Growth Trends Report](https://www.mordorintelligence.com/industry-reports/post-quantum-cryptography-market)
73. [Post-Quantum Cryptography (PQC) Market Size, Share 2034](https://www.imarcgroup.com/post-quantum-cryptography-market)
74. [Post-Quantum Cryptography Market Size Report, 2026-2033](https://www.grandviewresearch.com/industry-analysis/post-quantum-cryptography-market-report)

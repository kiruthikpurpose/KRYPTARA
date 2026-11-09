# STREAM L: Open-source landscape audit (REUSE / WRAP / INTEGRATE-WITH / LEARN-FROM / AVOID)

Audit date: 2026-11-06. Author: Stream L. Scope: existing open-source projects and standards relevant to our project
(locked-flash PQ continuity first stage + authority ledger + staged update + evidence + protocol adapters + fleet planner).

## L.0 Method, evidence labels, and honesty about limits

**How facts were gathered.** Tools available were WebFetch/WebSearch only (the `gh` CLI and GitHub API for the session were blocked per repo, so I could not clone or read source). Three kinds of source were used:
1. GitHub release pages (WebFetch of `github.com/<org>/<repo>/releases`) - latest tag and notes. These pages print dates **without the year** (e.g. "07 Aug"). Where a year is given below as 2026 it is inferred from the "pushed_at" API values, asset timestamps, or page text, and marked (y=2026 inferred). [F-with-caveat]
2. `https://api.github.com/repos/<org>/<repo>` fetched through WebFetch (returned `pushed_at`, licence SPDX, stars, language, archived). The tool summarises through a small model, so numbers are [2nd]-grade transcription of a primary API. Several calls failed ("client_error"); those cells say **unverified**.
3. IETF datatracker pages, project doc pages, vendor blogs (labelled [V]).

**Labels** follow BRIEF.md: [F] primary page/spec; [V] vendor claim; [D] measured in a paper; [I] inference; [H] hypothesis; "unverified" = could not confirm in this session.

**Licence column**: SPDX from the API where it returned one; `NOASSERTION` means GitHub could not pick a single licence (multi-licence repo), not "no licence". Where neither the API nor a page gave a licence I write "licence unverified" rather than recall it.

**Things I could NOT do**: read source code, check CI health, confirm per-repo maintainer lists, count active maintainers, fetch Botan/Mosquitto/Milo/Veraison API data (calls failed), read patents' claims beyond one (patent PDFs mostly returned no text). Treat the L.8 collision check as a **search-limited** result, not clearance.

**Decision vocabulary**
- REUSE = link/vendor the code as a dependency inside our deliverables.
- WRAP = use behind our own stable abstraction so it can be swapped (our crypto-agility principle).
- INTEGRATE-WITH = we interoperate at a defined interface; no code dependency.
- LEARN-FROM = read, borrow design/test vectors, do not depend.
- AVOID = do not depend (reason stated).

### L.0.1 Headline findings (the 8 that matter)

1. **The PQ primitive layer is already served; we should not write primitives.** mlkem-native v2.0.0 and mldsa-native v2.0.0 (both released 07 Aug, y=2026 inferred; Apache-2.0 OR MIT OR ISC) are C90, with HOL-Light/CBMC proofs claimed on their pages [F-page]. PQClean is archived (README, banner dated Aug 4, 2026) and pqm4 is deprecated, to be archived "in or after January 2027" [F]. Both point to the PQ Code Package as the successor. **Decision: REUSE mlkem-native/mldsa-native behind our `pqc_*` abstraction; AVOID PQClean/pqm4 as dependencies (LEARN-FROM for M4 benchmarks).**
2. **No SLH-DSA/LMS/XMSS verifier of comparable assurance exists in the PQCA code package** (not found in this audit; unverified negative). For locked-flash first stage the verifier candidates are: wolfCrypt (GPL-3.0 or commercial: licence risk), TF-PSA-Crypto's LMS (verify path; CVE-2025-49600/49601 fixed per release notes [F]), OpenTitan's ROM SPHINCS+ (hardware-bound), hash-sigs (licence unverified; ACVP branch), liboqs (SPHINCS+ **removed in 0.16.0** per notes [F] - check whether SLH-DSA replaced it). **This is a genuine gap we fill: a small, permissively licensed, formally-checked hash-based verifier (LMS/HSS + XMSS + SLH-DSA) sized for a first stage.**
3. **Nearest prior art to our core is OpenTitan Earl Grey's root-key block and Caliptra's ECC+PQC manifest pairing**, not any "multi-class slot with floor rule". OpenTitan: four P-256 + four SLH-DSA key slots (464 bytes) locked at manufacturing, hybrid scheme, SHA2-256 over the block, per-slot BLANK/PROVISIONED/REVOKED state [F: opentitan.org root_keys doc]. Caliptra: each role has ECC P-384 + one PQC key (MLDSA87 or LMS-SHA192-H15), PQC type fixed by fuse in provisioned lifecycle, both signatures verified [F: Caliptra auth_manifest doc]. **Neither implements a cross-class floor rule across more than two classes, an authority ledger, or exposure-years accounting (not found).** See L.8.
4. **Standards are moving under us, which is an argument for a data-model layer that is algorithm-neutral:** COSE ML-DSA is now **RFC 9964** (Proposed Standard, May 2026) [F: datatracker]; SUIT MTI (`draft-ietf-suit-mti`) is v23 in the RFC Editor queue with no RFC number as of the fetch [F: datatracker]; CoRIM (`draft-ietf-rats-corim`) is v12 in WG Last Call [F]; TCG TPM 2.0 Library Spec v1.85 adds ML-KEM/ML-DSA (per wolfSSL's post dated 2026-05-05) [V]. 
5. **The strongest "do not build" areas:** TUF (python-tuf 7.0.1, Apache-2.0, pushed 2026-11-05), Sigstore/Rekor (v1.5.5 released 21 Oct, asset stamps 2026-10-20), Tessera (v1.0.4, 16 Jul), Veraison (Apache-2.0), CBOMkit/sonar-cryptography (Apache-2.0 own code + Sonar Source-Available third-party). We INTEGRATE-WITH them via adapters.
6. **GPL traps in the stack:** wolfSSL is GPL-3.0 (API) and wolfCOSE is GPLv3 [F]; libiec61850 is GPL-3.0 (API) [F]; U-Boot GPL-2.0 [F]; libmodbus and RAUC are LGPL-2.1 [F]. For firmware shipped in locked flash, GPL-3.0 (anti-tivoization clause) is a distribution-time conflict for many device makers. We must not make GPL code a mandatory dependency (L.9).
7. **OT protocol stacks have essentially no PQ readiness of their own**; PQ for OPC UA/IEC 61850/DNP3/Modbus comes either from the TLS library underneath or from standards bodies (IEC 62351 direction, per one 2026 arXiv paper [2nd]). opendnp3 is **archived** (last push 2022-05-18) [F]. We build adapters, not stack replacements.
8. **Hosting/funding:** the PQ Code Package and Open Quantum Safe are PQCA (Linux Foundation) projects, and PQCA's own announcement says it welcomes proposals including "software for cryptographic agility or PQC migration" [F: LF blog]. That is the most natural host, with an explicit collision risk of scope overlap (L.7).

---

## L.1 Post-quantum crypto implementations

Facts: "release" = latest release page entry; "push" = GitHub API `pushed_at` (UTC). All dates 2026 unless stated.

| Name | What it is | Verified facts (URL) | Status date | Decision | Integration point | Risk |
|---|---|---|---|---|---|---|
| **mlkem-native** | C90 ML-KEM (FIPS 203), PQ Code Package (PQCA) | v2.0.0 released 07 Aug (y inferred); `release/v1.3` gets bugfixes to Feb 2027; API split of error codes (INVALID_PK/SK/PCT_FAIL); older releases licence "Apache-2.0 OR MIT OR ISC" [F] https://github.com/pq-code-package/mlkem-native/releases ; API: Assembly primary language, 259 stars, not archived https://api.github.com/repos/pq-code-package/mlkem-native | push 2026-11-06 | **REUSE (WRAP)** | `pqc_kem_*` backend for evidence-channel and fleet key-wrapping, not for the first-stage verifier (KEM not needed in locked flash) | v2 API break vs v1.3 LTS: pin and track; v2.0.0 release page showed no "Verified" signature badge (prior releases did) - check signing before vendoring |
| **mldsa-native** | C90 ML-DSA (FIPS 204), PQ Code Package | v2.0.0 first stable, 07 Aug; HOL Light proofs of AArch64/x86_64 asm memory safety + constant-time (except rej-sampler); CBMC proofs for C backend; SOUNDNESS.md; experimental restartable/bounded signing hooks [F] https://github.com/pq-code-package/mldsa-native/releases ; API: Standard ML(language field), 116 stars https://api.github.com/repos/pq-code-package/mldsa-native | push 2026-10-26 | **REUSE (WRAP)** | `pqc_sig_verify(ML_DSA_*)` for M-class second-stage verification, authority-ledger signatures; verify-only subset as first-stage candidate if ROM/flash budget allows | Proof scope is the library's claim [V-ish, in-repo]; does not cover our integration or Cortex-M asm (asm backends are AArch64/x86_64 only per page) so M0/M3/M4 use the C path |
| **liboqs** | C algorithm library, OQS (PQCA) | 0.16.0 released 9 Jul: mldsa-native now default for ML-DSA, mlkem-native v1.2.0, HQC enabled by default (spec 20250822), **SPHINCS+ removed**, FrodoKEM reorganised [F] https://github.com/open-quantum-safe/liboqs/releases ; licence not shown on page; API call failed (unverified) | 2026-07-09 | **INTEGRATE-WITH / LEARN-FROM** | Test oracle and cross-check for our KAT harness; algorithm-ID naming | Aggregates many schemes at differing assurance; "prototype/research" posture historically (unverified this session); not sized for MCU. Do not ship in first stage |
| **PQClean** | Clean C reference impls of NIST PQ schemes | **Archived read-only** (banner: archived by owner Aug 4, 2026); README redirects to PQ Code Package; CC0 / per-dir licences [F] https://github.com/PQClean/PQClean | 2026-08-04 | **AVOID** (dependency); LEARN-FROM (Falcon/FN-DSA code credited to Pornin) | none | Retired; contains pre-standard names (Kyber/Dilithium/SPHINCS+) |
| **pqm4** | PQ library + benchmark suite for Cortex-M4 | README: "no longer under active maintenance", archive planned "in or after January 2027", PRs by 30 Nov 2026; points to mlkem-native/mldsa-native; Apache-2.0/CC0 mostly [F] https://github.com/mupq/pqm4 | 2026-11 (notice) | **LEARN-FROM** (benchmark methodology; board list: NUCLEO-L4R5ZI default, 24 MHz to avoid wait states) | Our device-class benchmark harness (E-experiments) | Dying; do not depend |
| **libcrux** | Cryspen formally-verified Rust crypto (hax/F*) | Many crates released 7 Oct (y inferred): libcrux v0.0.6, -sha3 0.0.11, -sha2 0.0.9, -psq 0.0.11, -p384 0.0.1 (first); Apache-2.0; C, 271 stars (API) [F] https://github.com/cryspen/libcrux/releases , https://api.github.com/repos/cryspen/libcrux . ML-KEM/ML-DSA not stated on the releases page (unverified there) | push 2026-11-05 | **LEARN-FROM / INTEGRATE-WITH** (Rust path) | Candidate Rust backend for `pqc_*` in operator-side tooling | All crates 0.0.x: API unstable; verification scope per crate unverified |
| **RustCrypto `ml-kem`, `ml-dsa`, `slh-dsa`** | Pure-Rust PQ crates | Listed in RustCrypto/KEMs and /signatures; repos dual Apache-2.0/MIT; per-crate versions, audits, commit dates **not shown** on the fetched pages [F, partial] https://github.com/RustCrypto/KEMs , https://github.com/RustCrypto/signatures | unverified | **WRAP** for host-side Rust tools; **LEARN-FROM** | Rust verifier in fleet planner / evidence verifier | Audit status unverified; do not rely on constant-time claims without checking |
| **wolfSSL / wolfCrypt** | Embedded TLS+crypto, commercial dual-licence | 5.9.4 dated Sept 25, 2026; ML-KEM/ML-DSA APIs since 5.8.4; SLH-DSA (FIPS 205) added 5.9.0; **GPL-3.0** (API) [F] https://github.com/wolfSSL/wolfssl/releases , https://api.github.com/repos/wolfSSL/wolfssl (2985 stars, push 2026-11-06) | 2026-09-25 | **INTEGRATE-WITH** (optional backend); **AVOID as mandatory dependency** | Optional `pqc_*` provider where a device maker already holds a commercial licence | GPL-3.0 in locked firmware; vendor-controlled roadmap; FIPS-PQ status not shown on page |
| **wolfBoot** | Secure bootloader (wolfSSL) | v2.10.0 released 01 Oct 2026: i.MX RT700 "ML-DSA-87 signed-boot config"; v2.3.0 added ML-DSA and PQ+classical hybrid auth; v2.2.0 native LMS/XMSS; v2.5.0 deprecated third-party LMS/XMSS libs [F] https://github.com/wolfSSL/wolfBoot/releases ; licence/API unverified (API call failed) | 2026-10-01 | **LEARN-FROM; INTEGRATE-WITH** | Closest shipping analogue of "PQ first stage on MCU"; compare image format + key-slot design | Licence unverified (wolfSSL family is GPL/commercial: likely [I]); single-vendor |
| **Mbed TLS / TF-PSA-Crypto** | PSA Crypto reference (Arm→TrustedFirmware.org) | tf-psa-crypto-1.2.0 released 07 Jul; LMS verification in `extras` ("stateful hash implementation currently"); LMS CVEs CVE-2025-49600/-49601 fixed; **no ML-KEM/ML-DSA on the page** [F] https://github.com/Mbed-TLS/TF-PSA-Crypto/releases ; licence/API unverified | 2026-07-07 | **INTEGRATE-WITH / WRAP** | PSA Crypto API as our abstraction target on Zephyr/TF-M parts | PQ coverage lags; LMS had two CVEs in a verifier path: learn from them |
| **OpenSSL** | General TLS/crypto | 3.5 (final 2025-04-08) is LTS to 2030-04-08 and adds ML-KEM, ML-DSA, SLH-DSA [F] https://openssl-library.org/post/2025-04-08-openssl-35-final-release ; latest 4.0.2, 25 Aug (y inferred), Apache-2.0, 31,059 stars, push 2026-10-24 [F] https://github.com/openssl/openssl/releases , https://api.github.com/repos/openssl/openssl | 2026-10-24 | **INTEGRATE-WITH** | Gateway/server-side TLS for adapters (OPC UA/MQTT gateways), CMS tooling | Not for MCU first stage; size |
| **AWS-LC** | libcrypto fork (AWS) | v5.10.0 23 Sep (y inferred); ML-KEM in HPKE (5.9.0); re-imports mlkem-native/mldsa-native (5.6.0); FIPS CASTs for ML-KEM; no FIPS certificate stated on page [F] https://github.com/aws/aws-lc/releases ; 853 stars, push 2026-10-26 (API) | 2026-09-23 | **LEARN-FROM / INTEGRATE-WITH** | Server-side; consumes the same PQCA code, so a pinned PQCA version gives us diversity-free assurance | Not MCU-sized; AWS-driven roadmap |
| **BoringSSL** | Google TLS lib | README: "not intended for general use"; no API/ABI stability guarantees; Apache-2.0 [F] https://github.com/google/boringssl | n/a | **AVOID** as dependency | none | Stability policy incompatible with a decades-long contract |
| **Bouncy Castle (Java)** | Java/C# crypto | bc-java: MIT, 2,711 stars, push 2026-11-05 [F-API] https://api.github.com/repos/bcgit/bc-java ; PQ algorithm list not fetched (unverified) | 2026-11-05 | **INTEGRATE-WITH** | Java-based OT tools (Milo) and CBOM tools | PQ coverage unverified here |
| **Botan** | C++ crypto | Fetch failed; unverified | n/a | unverified | n/a | n/a |
| **hash-sigs (Cisco)** | LMS/HSS reference (RFC 8554) | README: "usable implementation of the LMS" (ACVP branch); 87 commits; 57 stars; licence file present, type not named; API failed [F-partial] https://github.com/cisco/hash-sigs | unverified | **LEARN-FROM** (state mgmt, test vectors) | KAT source for LMS verifier | Licence type unverified; commit date unverified |
| **xmss-reference** | XMSS reference (RFC 8391) | CC0-1.0; last push **2023-10-02**; README: for "cross-validation and experimenting" [F] https://github.com/XMSS/xmss-reference , https://api.github.com/repos/XMSS/xmss-reference | 2023-10-02 | **LEARN-FROM** (KATs only) | cross-check oracle | Dormant; not deployable as is |
| **OpenTitan crypto (ROM/otcrypto)** | Silicon RoT with SPHINCS+/SLH-DSA in mask ROM | Earlgrey-PROD.M6 latest (17 Oct, y inferred): SLH-DSA keyset created, SHA2-128s "pure or pre-hash" signing [F] https://github.com/lowRISC/opentitan/releases ; blog by Jade Philipoom (zeroRISC; year inferred 2024): first chips used SPHINCS+-shake-128s, next tapeout SHA2-128s [2nd] https://gopher-octagon-aya6.squarespace.com/blog/post-quantum-secure-boot-on-opentitan | 2026-10-17 | **LEARN-FROM** (+ INTEGRATE-WITH as a target RoT) | Reference for C5 (silicon-RoT) class; ledger states map | Silicon-bound; ROM cannot be updated (the very constraint we design for) |
| **Trezor / other hardware-wallet PQ** | - | Not verified in this session | n/a | unverified | n/a | n/a |

**L.1 conclusions.**
- DECISION: our `pqc_*` abstraction (stream design elsewhere) takes mlkem-native and mldsa-native as the **default backends**, wolfCrypt/OpenSSL/AWS-LC/libcrux as selectable alternates, giving **implementation diversity** at the code level (atlas intent: avoid single-implementation failure; ties to the single-assumption-safety argument in Atlas 10.3).
- WHY: formal-proof claims in the repos' own pages (HOL Light, CBMC) are the strongest available among C implementations; permissive tri-licence; PQCA stewardship.
- ALTERNATIVES REJECTED: PQClean (archived), pqm4 (deprecated), BoringSSL (no stability), wolfSSL as default (GPL-3.0).
- ASSUMPTIONS: proofs on the pages are accurate and cover the code we vendor [I]; PQCA continues funding (see L.7).
- LIMITS: no hash-based verifier in the PQCA set was confirmed; the first-stage verifier remains our work.
- VALIDATE: pin commit hashes; run ACVP/Wycheproof KATs in our CI; differential test two backends on every release (Experiment placeholder, tie to E-series in Atlas 16).

---

## L.2 Secure boot, bootloaders, RoT, OS

| Name | What it is | Verified facts (URL) | Status date | Decision | Integration point | Risk |
|---|---|---|---|---|---|---|
| **MCUboot** | Mainstream MCU bootloader (Zephyr, Mynewt, others) | v2.4.0 (23 Apr, y inferred): Zephyr compiled-in key + external PSA backend, ECDSA via Mbed TLS, `imgtool` custom-TLV; page names RSA/ECDSA/Ed25519 only; **no PQ mention** [F] https://github.com/mcu-tools/mcuboot/releases . Searches found a MCUboot PR #2707 hit for the query (page blocked; content **unverified**) | 2026-04-23 | **INTEGRATE-WITH** (adapter: our image format as a TLV payload; our first stage in front of MCUboot as stage 2) | Our locked first stage verifies MCUboot's image (or replaces its key-verification step) | No PQ in release notes: our staged-update design must not assume MCUboot internals are PQ-safe |
| **wolfBoot** | see L.1 | v2.10.0 01 Oct 2026; PQ since 2.3.0 | 2026-10-01 | **LEARN-FROM / INTEGRATE-WITH** | image header + hybrid auth reference | GPL/commercial (unverified) |
| **TF-M (Trusted Firmware-M)** | Arm PSA RoT reference for Cortex-M TrustZone | Tag page blocked by robots; **unverified** | n/a | **INTEGRATE-WITH** | PSA Crypto/attestation/ITS API target for C3-C4 class | PQ status unverified |
| **Nordic NSIB / STM32 SBSFU, OEMiRoT** | Vendor immutable bootloaders | STM32CubeL5 repo (ST) exists: description "full STM32Cube package for STM32L5"; licence NOASSERTION; push 2026-08-26 [F-API] https://api.github.com/repos/STMicroelectronics/STM32CubeL5 ; nRF Connect SDK push 2026-11-05, NOASSERTION [F-API] https://api.github.com/repos/nrfconnect/sdk-nrf . PQ status of NSIB/OEMiRoT **unverified** | 2026-08/11 | **INTEGRATE-WITH** (document per-part lock capabilities) | "Locked flash" targets (C1-C3 in Atlas 12) | Vendor-specific lock semantics; assess per part from published evidence (Brief rule 3) |
| **OpenTitan** | Open silicon RoT | see L.1; **Earl Grey root-key partition**: 4 P-256 + 4 SLH-DSA, 464 B, locked at manufacturing; hybrid; SHA2-256 over block verified by ROM; per-slot BLANK/PROVISIONED/REVOKED in an unlocked state partition; key_id = first uint32 of public key [F] https://opentitan.org/book/sw/device/silicon_creator/rom/doc/root_keys.html | 2026-10-17 | **LEARN-FROM (primary)** | Data layout comparison for our key-hash slot design; class C5 | See L.8: nearest prior art |
| **Caliptra** (CHIPS Alliance / OCP) | Open RoT for datacentre SoCs | rom-2.1.3-1 latest, 9 Oct (2026 via asset stamps); ML-DSA software support (rt-1.3.0, 3 Sep), ML-KEM PCTs/KATs, LMS verification marked FIPS non-approved; Apache-2.0, Rust, 172 stars, push 2026-11-06 [F] https://github.com/chipsalliance/caliptra-sw/releases , https://api.github.com/repos/chipsalliance/caliptra-sw ; auth manifest: ECC P-384 + (MLDSA87 or LMS-SHA192-H15), fuse-fixed PQC type; owner manifest 32 slots; SVN anti-rollback [F] https://chipsalliance.github.io/caliptra-web/docs/2.0/firmware/auth_manifest.html | 2026-10-09 | **LEARN-FROM; INTEGRATE-WITH** (evidence formats: DPE ML-DSA hybrid, `GET_ATTESTED_MLDSA87_CSR`) | Attestation/DPE format compatibility; the "PQC type fused" precedent | Datacentre-class, not OT MCU |
| **U-Boot** | Linux-class bootloader | GPL-2.0 (SPDX in API; 5,319 stars, push 2026-11-05 shows NOASSERTION in one call, GPL-2.0 in the other - conflicting tool output; **GPL family either way**) https://api.github.com/repos/u-boot/u-boot | 2026-11-05 | **INTEGRATE-WITH** (Linux-class gateways only) | Gateway-class FIT-image verification adapter | GPL; not for MCU first stage |
| **coreboot** | x86/ARM firmware | GPL-2.0; 2,825 stars; push 2026-11-03 [F-API] https://api.github.com/repos/coreboot/coreboot | 2026-11-03 | **LEARN-FROM** | none | GPL; out of OT MCU scope |
| **Trusted Firmware-A / OP-TEE** | A-profile EL3 / TEE | TF-A GitHub is a read-only mirror, no PQ mention [F] https://github.com/trustedfirmware-a/trusted-firmware-a ; OP-TEE optee_os: NOASSERTION licence, 1,957 stars, push 2026-11-05 [F-API] | 2026-11 | **INTEGRATE-WITH** (class C5 gateways) | TEE-backed evidence signing | PQ unverified |
| **Hubris (Oxide)** | Rust message-passing kernel | MPL-2.0; Rust; 3,646 stars; push 2026-11-05 [F-API] https://api.github.com/repos/oxidecomputer/hubris ; README description "memory-protected, message-passing kernel" [F] | 2026-11-05 | **LEARN-FROM** (architecture; verified-by-construction style) | Reference for isolation of the evidence/adapter tasks | MPL-2.0 file-level copyleft: acceptable but check |
| **Tock** | Rust embedded OS | Tock 2.2 released 06 Jan (year not shown); added ECDSA P-256 signature credentials, process checker/AppID; no PQ [F] https://github.com/tock/tock/releases ; API failed | 2026-01 (y unverified) | **LEARN-FROM** (credential/process checker model) | Staged-update credential policy analogue | PQ absent |
| **Zephyr** | RTOS | 4.4.2 bugfix release 07 Aug (y inferred); no PQC/SUIT mention on the page (page truncated); licence not retrieved (Apache-2.0 per common knowledge: [I]) https://github.com/zephyrproject-rtos/zephyr/releases | 2026-08-07 | **INTEGRATE-WITH** (primary RTOS target) | HAL/driver adapters; MCUboot comes with it | Page truncated: PQ support elsewhere (Mbed TLS/PSA) unverified |
| **RIOT** | IoT OS | LGPL-2.1, 5,835 stars, push 2026-11-05 [F-API] https://api.github.com/repos/RIOT-OS/RIOT | 2026-11-05 | **INTEGRATE-WITH** (optional) | adapters | LGPL link-time obligations in static firmware images |
| **Eclipse ThreadX** | RTOS (ex-Azure RTOS) | MIT; 3,566 stars; push 2026-11-03 [F-API] https://api.github.com/repos/eclipse-threadx/threadx | 2026-11-03 | **INTEGRATE-WITH** | adapters | foundation-hosted; fine |
| **FreeRTOS** | RTOS | API call failed; unverified | n/a | unverified | n/a | n/a |

**L.2 conclusions.**
- DECISION: our first stage is **not** a fork of any of these. It is a minimal, separately licensed, locked stage that can chain-verify into MCUboot / wolfBoot / vendor boot / Linux-class boot (INTEGRATE-WITH). WHY: no mainstream bootloader's release notes in this audit show PQ (MCUboot, Zephyr: none; wolfBoot: yes but GPL/commercial), and upgrading a bootloader in the field is exactly what locked flash forbids. ALTERNATIVES REJECTED: forking MCUboot (PQ absent, large surface); adopting wolfBoot (licence and single-vendor). ASSUMPTIONS: MCUboot lacks PQ at the date checked (the PR #2707 hit is unverified). TRADE-OFF: we maintain a small verifier. LIMITS: Linux-class bootloaders (U-Boot/coreboot) are GPL. VALIDATE: build reference chains first-stage -> MCUboot on Zephyr and first-stage -> wolfBoot in CI.

---

## L.3 Update frameworks and supply chain

| Name | What it is | Verified facts (URL) | Status date | Decision | Integration point | Risk |
|---|---|---|---|---|---|---|
| **IETF SUIT (RFC 9124 arch; manifest RFC 9019 family) + `draft-ietf-suit-mti`** | Firmware-update manifest standards | MTI draft v23 dated 22 Jul 2025, "RFC Ed Queue", no RFC number at fetch; datatracker "last updated" 2026-10-13 [F] https://datatracker.ietf.org/doc/draft-ietf-suit-mti/ ; an older -08 listed ES256, EdDSA, and HSS-LMS (-46) as the sole "Future" profile; the -08 text never says "post-quantum" [F] https://www.ietf.org/archive/id/draft-ietf-suit-mti-08.html | 2026-10-13 | **INTEGRATE-WITH** (our update-evidence manifest carries/derives from SUIT) | Staged update: SUIT envelope as one payload type; our ledger binds to `suit-manifest` digest | MTI lacks ML-DSA at -08; check v23 text before design freeze (not read) |
| **COSE ML-DSA (RFC 9964)** | ML-DSA for COSE/JOSE | RFC 9964, Proposed Standard, May 2026; AKP key type 7; seed-only private keys; HashML-DSA excluded [F] https://datatracker.ietf.org/doc/draft-ietf-cose-dilithium/ | 2026-05 | **INTEGRATE-WITH** | Signature envelope in SUIT/CoRIM/ledger entries | SLH-DSA COSE and ML-KEM COSE status unverified |
| **wolfCOSE** | C CBOR/COSE lib, 2.0.0 | ML-DSA-44/65/87 and HSS/LMS; GPLv3 + commercial; 77 stars [F] https://github.com/wolfSSL/wolfCOSE ; SUIT not mentioned | 2026 | **LEARN-FROM** / AVOID as dependency | COSE encode/decode reference | GPLv3 |
| **suit-tool (Arm)** | Python SUIT manifest generator | Search result states the tool "is being developed at" an Arm GitLab URL; repo ARMmbed/suit-manifest-generator is a pointer; maintenance status **unverified** https://www.github.com/ARMmbed/suit-manifest-generator | unverified | **LEARN-FROM** | test vectors | Possibly stale |
| **TUF / python-tuf** | Update-metadata framework (CNCF) | python-tuf v7.0.1 (01 Sep, y inferred), Apache-2.0, Python, 1,731 stars, push 2026-11-05, no PQ mention [F] https://github.com/theupdateframework/python-tuf/releases , https://api.github.com/repos/theupdateframework/python-tuf | 2026-11-05 | **INTEGRATE-WITH** (role/threshold/expiry model; our ledger is stricter for locked flash) | Repository metadata model for operator-side distribution | Online-signer assumptions and no PQ |
| **go-tuf, Uptane** | TUF variants (Uptane = automotive) | Not fetched; unverified | n/a | LEARN-FROM (Uptane director/image split) unverified | - | - |
| **Mender** | OTA (client) | mender v5.1.0 (12 May, y inferred); QNX preview 09 Jun; licence not on page [F] https://github.com/mendersoftware/mender/releases | 2026-05-12 | **INTEGRATE-WITH** | delivery transport only | no PQ mention |
| **RAUC** | Embedded Linux A/B updater | v1.15.2 (27 Mar, y inferred), CVE-2026-34155 fix; LGPL; OpenSSL 3.5 mention; no PQ mention [F] https://github.com/rauc/rauc/releases | 2026-03-27 | **INTEGRATE-WITH** | Gateway-class delivery; CMS signature layer could carry ML-DSA via OpenSSL 3.5 [I] | LGPL |
| **SWUpdate** | Embedded Linux updater | 2026.05.1 (22 Jun, y inferred); adds WolfSSL provider and PKCS#7; no PQ mention; licence not on page [F] https://github.com/sbabic/swupdate/releases | 2026-06-22 | **INTEGRATE-WITH** | gateway-class | licence unverified |
| **OSTree** | Content-addressed OS delivery | not fetched; unverified | n/a | unverified | - | - |
| **Sigstore / Rekor** | Signing + transparency log | Rekor v1.5.5 (released 21 Oct; asset stamps 2026-10-20), built with Go 1.27.3; v2/tiles not on page [F] https://github.com/sigstore/rekor/releases | 2026-10-21 | **INTEGRATE-WITH** | Publish release-evidence for our own artifacts; ledger-checkpoint witnessing | Classical signatures by default (PQ status unverified) |
| **Trillian-Tessera** | Tile-based transparency log (transparency.dev) | v1.0.4 (16 Jul, y inferred); 1.0.x not pre-release; `tlog-tiles` fsck mentioned [F] https://github.com/transparency-dev/tessera/releases | 2026-07-16 | **REUSE / INTEGRATE-WITH** | Candidate substrate for the authority ledger's *operator-side public log* (not the on-device ledger) | PQ log signatures: unverified; do not build a log from scratch |
| **in-toto, SLSA, SCITT implementations** | Supply-chain attestation formats | Not fetched; IETF SCITT status unverified; CoRIM status below | n/a | INTEGRATE-WITH (unverified) | build-provenance statements bound to firmware hash | - |

**L.3 conclusions.** DECISION: **do not write our own transparency log or metadata framework**; the on-device authority ledger is novel and ours, but its operator-side counterpart rides TUF-style roles + Tessera/Rekor witnesses. WHY: mature, Apache-style projects, active (pushes within days); PQ is the missing layer, and that is a *signature-suite* swap in our envelope. ALTERNATIVES REJECTED: building a bespoke log; Mender/RAUC/SWUpdate as the core (delivery, not authority). ASSUMPTIONS: these projects add PQ signatures eventually [I]. LIMITS: TUF's online-key model does not address offline PQ root with locked flash. VALIDATE: reference deployment publishing ledger checkpoints to a Tessera log in CI.

---

## L.4 Attestation and evidence

| Name | What it is | Verified facts (URL) | Status date | Decision | Integration point | Risk |
|---|---|---|---|---|---|---|
| **Veraison** | Attestation verifier services | Apache-2.0; Provisioning accepts CoRIM payloads (endorsements, trust anchors); PSA, CCA, TPM, Parsec, SEV-SNP; releases empty, "monthly tag" per README; stewardship not on page [F] https://github.com/veraison/services | unverified (API failed) | **INTEGRATE-WITH** (our evidence packages verify through a Veraison scheme plugin) | New scheme plugin for our "continuity evidence" | PQ in verifier unverified |
| **CoRIM (`draft-ietf-rats-corim`)** | Reference-value/endorsement format | v12, WG Last Call, no RFC number; intended Proposed Standard [F] https://datatracker.ietf.org/doc/draft-ietf-rats-corim/ | 2026-11 | **INTEGRATE-WITH (track)** | Carry expected key-class state and ledger state as reference values | Still moving; do not freeze encodings on it |
| **Keylime** | TPM-based remote attestation | Apache-2.0, Python, 573 stars, push 2026-11-01 [F-API] https://api.github.com/repos/keylime/keylime | 2026-11-01 | **INTEGRATE-WITH** (Linux-class gateways only) | gateway attestation | Python/TPM-bound; MCU out of scope |
| **go-tpm** | Go TPM 2.0 library | Apache-2.0, Go, 675 stars, push 2026-10-30 [F-API] https://api.github.com/repos/google/go-tpm | 2026-10-30 | **WRAP** | Operator-side tooling | PQ command set (TPM spec v1.85) support unverified |
| **tpm2-tss** | TCG TSS stack | BSD-2-Clause, C, 913 stars, push 2026-11-03 [F-API] https://api.github.com/repos/tpm2-software/tpm2-tss | 2026-11-03 | **INTEGRATE-WITH** | Linux gateways | PQ (v1.85) unverified |
| **TCG TPM 2.0 Library Spec v1.85** | TPM spec with ML-KEM/ML-DSA | wolfSSL post (dated 2026-05-05) calls v1.85 "newly-published" and lists ML-KEM-512/768/1024 and ML-DSA-44/65/87 [V] https://www.wolfssl.com/post-quantum-cryptography-is-coming-to-wolftpm/ | 2026-05 | **INTEGRATE-WITH** | Anchor for C4-C5 gateway evidence | Vendor-reported; confirm at trustedcomputinggroup.org (not done) |
| **Caliptra DPE** | Device Identifier Composition Engine profile | ML-DSA hybrid mode in DPE (firmware 2.0.2) and attested ML-DSA-87 CSR [F] https://github.com/chipsalliance/caliptra-sw/releases | 2026-10-09 | **LEARN-FROM** | DICE-like layered identity for C5 | datacentre scope |
| **CBOMkit / sonar-cryptography (PQCA)** | Crypto inventory from source | Apache-2.0 own code + Sonar Source-Available third-party; Java (JCA, BC lightweight), Python (pyca), Go (partial); C# in development; emits CycloneDX CBOM spec 1.6 [F] https://github.com/PQCA/sonar-cryptography ; (C/C++ and Rust firmware **not** listed) | 2026 | **INTEGRATE-WITH** (emit our firmware cryptography facts as CBOM 1.6) | Exposure-years input for the fleet planner | **No C/embedded coverage**: gap we fill (CBOM producer for firmware binaries/SBOMs) |
| **CycloneDX CBOM, SPDX, OWASP Dependency-Track** | BOM formats / tracker | CBOM 1.6 confirmed through the sonar-cryptography page; SPDX and Dependency-Track not fetched | unverified | INTEGRATE-WITH | BOM export | - |

**L.4 conclusions.** DECISION: evidence is a **profile** layered on CoRIM/EAT/COSE and consumed by Veraison, not a new attestation architecture. WHY: Veraison already ingests CoRIM and several schemes; CoRIM is in WG Last Call. RISK: CoRIM wire format may change before RFC. TRADE-OFF: we wait on IETF for stability and maintain an adapter. VALIDATE: round-trip our evidence through a Veraison test instance.

---

## L.5 Industrial protocol and OT stacks (with PQ readiness)

PQ readiness column: "None found" = nothing on the pages fetched; **it does not prove absence**.

| Name | What it is | Verified facts (URL) | Status date | PQ readiness | Decision | Integration point | Risk |
|---|---|---|---|---|---|---|---|
| **open62541** | OPC UA C stack | MPL-2.0, C, 3,263 stars, push 2026-10-31 [F-API] https://api.github.com/repos/open62541/open62541 | 2026-10-31 | Search for an OPC Foundation PQ profile returned no relevant primary result; **unverified**; PQ would arrive via the mbedTLS/OpenSSL backend [I] | **INTEGRATE-WITH** | Adapter: ledger/evidence over OPC UA information model; PQ via TLS backend | OPC UA security policies are the gating standard |
| **Eclipse Milo** | OPC UA Java | API failed; unverified | n/a | unverified | INTEGRATE-WITH (unverified) | - | - |
| **libiec61850 (MZ Automation)** | IEC 61850 MMS/GOOSE/SV | GPL-3.0, C, 1,241 stars, push 2026-10-21 [F-API] https://api.github.com/repos/mz-automation/libiec61850 | 2026-10-21 | One 2026 arXiv paper proposes ML-KEM key establishment + Chaskey-12 MACs for IEC 61869-9 SV, validated on two Raspberry Pis; 96 kHz/1-ASDU profile did **not** meet budget [D, paper-level, modest testbed] https://arxiv.org/pdf/2608.22123 . IEC 62351 PQ status: unverified | **INTEGRATE-WITH** (process boundary only) | Adapter by IPC to avoid GPL entanglement | GPL-3.0 |
| **opendnp3** | DNP3 | Apache-2.0 but **archived**, last push 2022-05-18 [F-API] https://api.github.com/repos/dnp3/opendnp3 | 2022-05-18 | None found | **AVOID** | - | Abandoned |
| **libmodbus** | Modbus C lib | LGPL-2.1, 4,283 stars, push 2026-07-02 [F-API] https://api.github.com/repos/stephane/libmodbus | 2026-07-02 | Modbus/TCP has no native security; Modbus/TCP Security uses TLS [I: not verified here] | **INTEGRATE-WITH** | Adapter only | LGPL; no security layer to make PQ |
| **Eclipse Mosquitto / Paho** | MQTT broker/clients | API failed; unverified | n/a | via TLS lib, unverified | INTEGRATE-WITH | evidence transport | - |
| **ChirpStack** | LoRaWAN network server | MIT, Rust, 1,115 stars, push 2026-09-28 [F-API] https://api.github.com/repos/chirpstack/chirpstack | 2026-09-28 | LoRaWAN uses symmetric AES keys (not verified here); PQ relevance is key-provisioning | **INTEGRATE-WITH** | Fleet join/provisioning flow | - |
| **Zeek ICS parsers (ICSNPP), Suricata, Malcolm** | OT network monitoring | API calls failed; unverified | n/a | Detection of PQ TLS handshakes: unverified | INTEGRATE-WITH (unverified) | Passive crypto inventory (exposure input) | - |
| **Eclipse Kuksa, EVerest** | Vehicle/EV charging | EVerest API failed; Kuksa not fetched; unverified | n/a | unverified | unverified | - | - |

**L.5 conclusions.** DECISION: protocol adapters are **thin, out-of-process or link-isolated** bridges; we never fork the stacks. WHY: licences range from MPL to GPL-3.0; one project (opendnp3) is archived; none shows PQ in their own release pages. ALTERNATIVES REJECTED: forking open62541 to add PQ (belongs in the TLS backend / OPC Foundation); embedding libiec61850 (GPL-3.0). LIMITS: I could not verify IEC 62351, OPC UA, DNP3 SAv6, or Modbus Security PQ plans from primary sources in this session; flag as **open question**.

---

## L.6 Verification tooling and ecosystems

| Name | What it is | Verified facts (URL) | Status date | Decision | Integration point | Risk |
|---|---|---|---|---|---|---|
| **HACL\*** | F*-verified C crypto | Apache-2.0, F*, 1,846 stars, push 2026-11-01 [F-API] https://api.github.com/repos/hacl-star/hacl-star | 2026-11-01 | **LEARN-FROM / REUSE** for hash and MAC primitives (SHA-2, SHA-3) in the ledger | Hash core of `ledger_hash` | Toolchain heavy; its PQ coverage unverified |
| **Fiat-crypto** | Rocq-generated field arithmetic | Rocq Prover, 851 stars, push 2026-10-19; licence NOASSERTION [F-API] https://api.github.com/repos/mit-plv/fiat-crypto | 2026-10-19 | **LEARN-FROM** | classical ECC only (our hybrid classical leg) | multi-licence |
| **CBMC** | Bounded model checker for C | C++, 1,162 stars, push 2026-11-05, licence NOASSERTION [F-API] https://api.github.com/repos/diffblue/cbmc ; used by mlkem-native/mldsa-native per their pages | 2026-11-05 | **REUSE (as CI tool)** | Prove memory-safety of first-stage verifier and parser | proof harness effort |
| **Kani** | Rust model checker | Apache-2.0, Rust, 3,647 stars, push 2026-11-03 [F-API] https://api.github.com/repos/model-checking/kani | 2026-11-03 | **REUSE (CI tool)** | Rust verifier/ledger library | scope limits (unsafe/FFI) |
| **SAW / Cryptol (Galois)** | Equivalence checking of C/LLVM vs spec | saw-script BSD-3-Clause, Haskell, 526 stars, push 2026-11-06 [F-API] https://api.github.com/repos/GaloisInc/saw-script | 2026-11-06 | **LEARN-FROM / REUSE (CI)** | spec-vs-implementation for ledger state machine | specialist skills |
| **seL4** | Verified microkernel | 5,858 stars, push 2026-11-05; licence NOASSERTION (multi) [F-API] https://api.github.com/repos/seL4/seL4 | 2026-11-05 | **LEARN-FROM** | class C5 gateway isolation option | not MCU-class |
| **Verus** | Rust verifier | API failed; unverified | n/a | unverified | - | - |
| **Frama-C, Dafny, Apalache/TLC, Isabelle, EverCrypt** | Other verifiers | not fetched; unverified | n/a | unverified | TLA+/Apalache for the ledger protocol model | - |

**L.6 conclusions.** DECISION: formal verification is applied to (a) the **first-stage verifier + ledger state machine in C via CBMC**, (b) host-side Rust via **Kani**, (c) the ledger protocol via **TLA+/Apalache** (tool availability unverified). WHY: mlkem-native/mldsa-native already demonstrate CBMC at this scale for PQ code [F-page]. LIMITS: proofs do not cover hardware lock behaviour; those are assessed per part. VALIDATE: CI fails on proof regression.

---

## L.7 Consortia, standards bodies, funders: host, fund, or collide

| Body | What it is | Verified facts (URL) | Status date | Decision | Role for us | Risk |
|---|---|---|---|---|---|---|
| **PQCA (Linux Foundation)** | Hosts OQS and PQ Code Package; also CBOMkit (sonar-cryptography under PQCA org) | Launched Feb 2024; initial projects OQS + PQ Code Package; invites proposals incl. "software for cryptographic agility or PQC migration" [F] https://www.linuxfoundation.org/blog/a-deep-dive-into-the-post-quantum-cryptography-alliance ; TAC minutes exist for 2026-02-11 https://pqca.github.io/TAC/meeting-minutes/2026/2026-02-11-TAC.html | 2026 | **Primary candidate to HOST** | Host core libraries; contribute verifier upstream | Scope overlap/governance; hosting process not described on page |
| **IETF** (COSE, SUIT, RATS, SCITT, PQUIP) | Standards | RFC 9964 (ML-DSA COSE), SUIT MTI in RFC Ed queue, CoRIM v12 in WGLC [F] (L.3/L.4 URLs) | 2026-10/11 | **INTEGRATE-WITH** | Our profiles are drafted as IETF-compatible profiles | schedule slip |
| **TCG** | TPM spec | v1.85 PQ per vendor post [V] | 2026-05 | INTEGRATE-WITH | gateway attestation | - |
| **OCP / CHIPS Alliance** | Caliptra stewardship | Caliptra repo under chipsalliance [F-API] | 2026-11 | INTEGRATE-WITH | evidence compat | - |
| **Confidential Computing Consortium, LF Edge, Eclipse Foundation, OpenSSF, ETSI QSC, CSA, ISA/IEC 62443, Open Source Firmware Foundation** | Various | My search for these in a PQ-firmware context returned no relevant primary page; statuses **unverified** | n/a | unverified | possible hosts (Eclipse for OT, OpenSSF for supply-chain) [I] | - |
| **NLnet, Sovereign Tech Agency** | Funders | Search returned general pages (NLnet funding rounds; STA/Sovereign Tech Fund; EU Horizon PQC calls) but I fetched none; current PQ-relevant calls **unverified** | n/a | candidate FUNDERS [I] | grant applications | open calls unverified |

DECISION (hosting): approach PQCA first for the cryptographic core; keep the OT-specific profiles (ledger, evidence, fleet planner) separable so they can live in Eclipse/LF Energy-type OT communities if PQCA scope refuses. ALTERNATIVE REJECTED: independent foundation (bus-factor and decades-long continuity risk). ASSUMPTION: PQCA TAC accepts new projects [I]. VALIDATE: submit a scoping proposal; record the answer.

---

## L.8 Collision check (prior art): does anything already do our core?

Our core claims under test: (1) **multi-assumption-class key-hash slots** (e.g., hash-based, lattice, classical) in **locked flash** with a **cross-class floor rule** (a minimum number/class of independent signatures must verify, regardless of which slot set exists); (2) an **authority ledger** (signed, monotonic record of who may authorise what, on device); (3) **exposure-years** (quantitative accounting of key/algorithm exposure over time driving fleet planning).

| Candidate prior art | What it does (verified) | Overlaps | Does not do (as far as verified) | Verdict |
|---|---|---|---|---|
| OpenTitan Earl Grey root keys | 4 P-256 + 4 SLH-DSA keys in locked OTP (464 B); hybrid scheme; SHA2-256 over slots; BLANK/PROVISIONED/REVOKED per slot in unlocked partition [F] | Multi-slot locked store, two classes, revocation state | Cross-class floor rule beyond "hybrid"; >2 classes; ledger; exposure accounting. Doc says no cross-algorithm rule beyond hybrid support [F] | **Closest, partial overlap**: cite and design to be a strict superset |
| Caliptra auth manifest | ECC P-384 + {MLDSA87 or LMS-SHA192-H15}; PQC type fused; both signatures verified; SVN anti-rollback; owner manifest 32 slots [F] | Dual-class pairing, fused algorithm choice | Revocation not described on page; key-hash slots not described on page; ledger; exposure | partial overlap |
| wolfBoot hybrid auth (v2.3.0) | "hybrid authentication that combines one PQC algorithm with ECC or RSA" [F release notes] | AND-composition of two classes | Not shown: slot model in locked flash, floor rule, ledger | partial overlap |
| US 11,593,488 (cryptographic agile bootloader, DARPA HR001121C0115; provisional 2020-10-28) | RoT with two secrets; second bootloader replaces first when first uses deprecated crypto; replacement within an "upgrade window", old bootloader moved to read-only afterwards [F: patent text, partially fetched] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11593488 | **Conceptually adjacent**: crypto agility via staged bootloader replacement; hash/HMAC-based RoT | Multi-class key-hash slot set + floor rule; ledger; exposure-years | adjacent. **Unverified, needs counsel** (claims read only partially; grant status unconfirmed) |
| US 12,147,540 "secure boot event with one of a plurality of candidate PKI authentication key sets" | Title only; PDF returned no text [unverified] | Possibly multiple candidate key sets | all unverified | **unverified, needs counsel** |
| US 10,181,956 "Key revocation", US 8,484,451 "software boot revocation", US 11,100,229 "secure hybrid boot systems" | Titles seen in search; content not read | revocation / hybrid boot | unverified | **unverified, needs counsel** |
| Mbed TLS/TF-PSA-Crypto LMS, hash-sigs, xmss-reference | Primitive verifiers, no policy layer | primitives only | all policy | no overlap |
| TUF/Uptane | Role/threshold/expiry/rollback metadata (TUF: python-tuf 7.0.1) | Threshold + rollback concepts at metadata layer | On-device locked-flash ledger; multi-assumption classes; exposure-years | conceptual cousin (LEARN-FROM) |
| CBOM tooling | Crypto inventory | Inventory input to exposure | exposure-year calc, fleet planner | feeder not competitor |

**Result [I, search-limited]:** I found **no project or document that implements a cross-class floor rule over multiple assumption-class key-hash slots in locked flash, an on-device authority ledger, or exposure-years accounting**. This is absence-of-evidence from roughly a dozen searches and ~100 page fetches; it is **not** clearance. Patents were not read beyond one document. **Unverified, needs counsel:** freedom-to-operate and any patents in the families above. No legal advice is given.

Recommended collision mitigations: (a) publish our design openly (defensive publication) after counsel review; (b) cite OpenTitan and Caliptra explicitly as prior art in the spec; (c) open a conversation with OpenTitan/zeroRISC and Caliptra maintainers about whether a floor-rule profile fits their root-key formats; (d) run a proper patent search (CPC H04L9/32, G06F21/57) by a professional.

---

## L.9 Deliberate AVOIDs

| Item | Reason | Evidence | Substitute |
|---|---|---|---|
| PQClean as dependency | Archived read-only | README/banner 2026-08-04 [F] | mlkem-native, mldsa-native |
| pqm4 as dependency | Deprecated, archive planned Jan 2027 | README notice [F] | PQCA code, own harness |
| opendnp3 | Archived, last push 2022-05-18 | API [F] | thin DNP3 adapter on a maintained stack (unverified candidate) |
| xmss-reference in firmware | Reference/experimental, dormant since 2023-10-02 | README + API [F] | KATs only; own verifier |
| BoringSSL | No API/ABI stability, "not intended for general use" | README [F] | OpenSSL/AWS-LC at server side |
| wolfSSL/wolfCOSE as *mandatory* dependency | GPL-3.0 (wolfSSL 5.8.2 moved to GPLv3; wolfCOSE GPLv3) | release notes, README [F] | PSA abstraction; optional provider |
| libiec61850 linked in-process | GPL-3.0 | API [F] | out-of-process adapter |
| U-Boot/coreboot in first stage | GPL-2.0, wrong class | API [F] | Linux-class adapters only |
| liboqs in firmware | Research aggregator, SPHINCS+ removed in 0.16.0, not MCU-sized | release notes [F] | test oracle only |
| Unverifiable vendor claims | e.g., "FIPS-PQ validated", "formally verified" without scope | wolfSSL/Caliptra pages give none | require scope docs + our CI proofs |
| Vendor-locked update stacks as authority root | Mender/Nordic/ST flows hold keys in vendor clouds (general risk) [I] | not verified per vendor | our ledger |

---

## L.10 What this audit implies for the build (reuse map)

| Our component | Reuse / integrate | Own (gap) |
|---|---|---|
| PQ primitives | mlkem-native, mldsa-native (REUSE/WRAP); wolfCrypt/OpenSSL/AWS-LC/libcrux as alt backends | hash-based verifier (LMS/HSS, XMSS, SLH-DSA) first-stage sized, permissive, CBMC-proved |
| Crypto abstraction | PSA Crypto API alignment (TF-PSA-Crypto) | `pqc_*` / `suite_id` registry |
| First stage | none directly; OpenTitan/Caliptra as data-layout prior art | key-hash slot store, floor rule, ledger |
| Update | SUIT, COSE (RFC 9964), TUF roles, MCUboot/wolfBoot chain | staged-update state machine, evidence package |
| Evidence | CoRIM/EAT, Veraison, Tessera/Rekor | OT evidence profile; ledger checkpoint format |
| Inventory | CycloneDX CBOM 1.6, sonar-cryptography | firmware/binary CBOM producer, exposure-years calculator |
| Protocol adapters | open62541, libmodbus, ChirpStack, (libiec61850 out-of-process) | adapter SPI, PQ-gap shims |
| Verification | CBMC, Kani, SAW, TLA+/Apalache | proofs for our modules |

## L.11 Atlas claims checked

- None of the Atlas's statements were directly contradicted by this audit. Two facts the Atlas author should re-check against this memo: (1) **PQClean/pqm4 status** (both retired/deprecated in 2026); (2) **liboqs removed SPHINCS+** in 0.16.0. If the Atlas lists either as a recommended dependency, update it. (I did not search the Atlas text for these terms.)

## L.12 Open questions

1. Is there a PQ profile for OPC UA, IEC 62351 (-3/-6/-9), DNP3-SA, Modbus Security? (Not verified from primary sources.)
2. Does `draft-ietf-suit-mti` v23 include ML-DSA/SLH-DSA profiles? (Only -08 was read.)
3. What is MCUboot PR #2707 about? (Page blocked.)
4. Do TF-M, Nordic NSIB, STM32 OEMiRoT have PQ roadmaps and what lock features per part?
5. Licences for wolfBoot, TF-PSA-Crypto, hash-sigs, Mender, SWUpdate, Zephyr not retrieved.
6. Patent landscape (US 12,147,540; 10,181,956; 8,484,451; 11,100,229): needs counsel.
7. PQCA hosting process and TAC appetite; NLnet/STA current open calls.
8. Veraison, Botan, Mosquitto, Milo, Verus, FreeRTOS, go-tuf, Uptane, OSTree, in-toto, SCITT impls: not verified.

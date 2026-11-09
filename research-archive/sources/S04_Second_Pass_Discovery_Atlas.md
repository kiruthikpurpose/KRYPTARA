# Second-Pass Discovery Atlas: OT and Embedded Post-Quantum Security, Re-examined

The previous work bet on new silicon and a new kernel to carry trust through algorithm changes. This pass finds that bet aimed at the wrong bottleneck. Industrial fleets mostly fail to install updates that already exist. Many shipping MCUs can already host a hash-based, PQ-capable immutable first stage in locked flash. And the most dangerous unaddressed exposures are classical "side doors" around secure boot: debug unlock, ownership transfer, factory provisioning and engineering workstations. Build first: an open continuity first stage for existing MCUs, PQ-capable ownership vouchers and debug credentials, and update staging aligned to maintenance windows — not an Authority Continuity Kernel in new ROM.

## TL;DR

- **The thesis survives but moves layer.** The real bottleneck is update adoption plus classical authorisation paths that bypass secure boot, not the immutable ROM verifier. In "The Wretched State of OT Firmware Patching", aDolus CTO Eric Byres analysed Microsoft customer PLC data: "60% were running ancient firmware versions with 8 or more exploitable CVEs… updates have been available for over 10 years!" Silicon Labs, NXP and STM32 debug-unlock credentials are classical signatures granting full device access.\[1\]\[2\]\[3\]
- **Several load-bearing numbers in the previous work were wrong, and the corrections change the architecture.**
  - The ≈42 ms boot estimate paired the LM-OTS W4 cycle count with the 1,452 B W8 signature. A W8 verify is ≈23 M cycles, ≈363 ms at 64 MHz in software.
  - Linear pre-rotation saves 1.5–3×, not 10×.
  - NIST draft SP 800-230 (Quynh Dang and Dustin Moody; comments 13 Apr–12 Jun 2026) adds six SLH-DSA sets for firmware signing with "a strict limit of 2^24 signatures per signing key". That removes most of the case for stateful LMS root custody.
- **Re-ranked recommendation, built on existing standards:**
  1. An open locked-flash continuity first stage with dual-class key slots.
  2. PQ-capable FIDO Device Onboard ownership vouchers and debug credentials.
  3. Symmetric-first process-bus keying.
  4. Fleet crypto-state evidence tied to the CRA and India's DST timelines.

  New-ROM licensing, the custodian utility and the time-free layer drop to research status.

---

## 1. Executive synthesis: what changed in our understanding

**What survives [I]:**
- PQ migration in OT is an authority-continuity problem.
- Hash functions are the conservative common denominator.
- Verification, not signing, belongs on constrained endpoints.
- The process bus stays symmetric.
- The OEM/integrator/operator responsibility gap is real.

**What changed, in order of consequence:**

1. **The binding constraint is update adoption.**
   - Eric Byres of aDolus (vendor, Oct 2023) analysed Microsoft customer PLC data: "60% were running ancient firmware versions with 8 or more exploitable CVEs… updates have been available for over 10 years!" Updating would raise CVE-free devices "from 4% to 40%" and cut devices with more than eight CVEs "down to only 18%".
   - SANS ICS/OT Cybersecurity Survey: 2023's Challenges (700+ responses): "Fewer than 30% of facilities pre-test and apply vendor-validated patches on a defined schedule, and only 15% apply patches during routine maintenance windows."
   - The previous work modelled the update as an attack surface, never as the thing that does not happen.
2. **Maker-defined immutable first stages already exist.**
   - Nordic's nRF Secure Immutable Bootloader (NSIB) runs from write-protected flash. It stores only hashes of provisioned public keys (in OTP on nRF91/nRF5340). Using a higher-index key permanently invalidates lower ones — deployed prior art for a monotonic sunset.\[4\]\[5\]\[6\]\[7\]
   - ST's OEMiRoT combines unique boot entry, write protection, RDP Level 2 and HDP so that user-flash code is immutable.\[8\]\[9\]
   - A PQ-capable hash-only first stage can therefore ship on many existing parts without a new mask ROM.
3. **Classical side doors were under-weighted.** Each of the following gives total control to a quantum-capable forger without touching the boot chain:
   - Silicon Labs Series 2 debug unlock signs with ECDSA-P256-SHA256.\[2\]
   - NXP RW61x debug credentials are signed by RoT keys.\[1\]
   - OpenTitan's ownership unlock/activate keys are ECDSA P-256, with inline signatures "ECDSA-only".\[10\]
   - FIDO Device Onboard (FDO) ownership vouchers use SECP256R1/SECP384R1.\[11\]
4. **Stateful hash signatures are no longer the only conservative firmware option.**
   - NIST SP 800-230 ipd (Quynh Dang and Dustin Moody; comments open 13 Apr–12 Jun 2026) adds six SLH-DSA sets at levels 1, 3 and 5. They carry "a strict limit of 2^24 signatures per signing key" and are "not approved for general-purpose use". They are tailored to software, firmware and certificate signing.
   - For comparison, the smallest FIPS 205 signatures are 7,856, 16,224 and 29,792 B.
   - Caveat: NSA CNSA 2.0 still names LMS/XMSS for national-security firmware, and its v2.1 excludes HSS and XMSS^MT.\[12\]\[13\]
5. **Arithmetic corrections** (Section 3) change rankings.
6. **India makes the pressure concrete.**
   - The DST Task Force roadmap (draft Feb 2026; final May 2026 per secondary sources) sets critical information infrastructure (CII) milestones: foundations 2027, priority migration 2028, completion 2029.\[14\]
   - It names power, telecom and ONGC as urgent adopters.\[15\]
   - It recommends containing "classical-only systems within controlled enclaves where immediate migration is not feasible".\[16\] Against 15–30-year OT assets, enclave containment becomes the default for most installed OT.

**The hidden assumption that changed most:** that the cryptographic root is the scarcest resource. The scarcest resources are maintenance windows, people who understand the device, and authorisation paths nobody inventoried.

---

## 2. Complete audit of the previous work

### 2.1 Research trail

**Research questions:**
- Q1: Are the cited facts current?
- Q2: Is the arithmetic consistent?
- Q3: Does the ACK require new ROM?
- Q4: Which classical paths bypass it?
- Q5: What alternatives to stateful hash-based signatures emerged in 2026?
- Q6: What do operators actually do with updates, and what does downtime cost?
- Q7: What do the US, EU and India now require?

**Streams:**
- S1: policy and standards.
- S2: silicon and boot.
- S3: benchmarks.
- S4: lifecycle, ownership and debug.
- S5: economics (one delegated sub-investigation).
- S6: adversarial reconciliation (analytical).

**Rounds:** reconstruction → verification searches → arithmetic challenge → redesign → independent review.

**Scale, honestly:**
- 18 web searches, two fetches and one delegated investigation.
- ≈70 sources touched, ≈40 decisive. That is far below the 500–600 invited.
- Claims not rechecked are marked "inherited".

**Labels:**
- [F] primary fact or standard
- [2nd] secondary report of a fact
- [V] vendor claim
- [D] demonstrated result
- [E] estimate with arithmetic
- [I] inference
- [H] hypothesis

### 2.2 Traceability (condensed)

| Problem | Prior root cause | Assumption | Prior solution | Evidence now | Unresolved risk |
|---|---|---|---|---|---|
| P1/P2/P8 algorithm-bound anchors | R1 immutable silicon | New ROM required | ACK in OTP/ROM | Locked-flash first stages exist (NSIB, OEMiRoT) [F] | Flash locks weaker than ROM against fault injection [I] |
| P3 LMS state reuse | R6 | Stateful HBS needed for roots | LMS custody | SP 800-230 limited-use SLH-DSA [F, draft] | CNSA 2.0 still names LMS/XMSS |
| P15/P26/P27 time, revocation | R2 | Need a time-free layer | Counter epochs | NSIB key-index floor ships [F] | Freeze attacks undetectable offline |
| P23/P31 orphaned fleets | R3 | New custodian utility needed | Threshold + custodian | FDO vouchers already move ownership off-device [F];\[17\]\[18\] no demand evidence | Concentration, legal risk |
| P4/P10/P17–P20 endpoint PK work | R4 | Symmetric-first best | KDC/GDOI-PQ | IEC 62351-9 GDOI [inherited] | KDC concentration |
| P28–P30 safety | R5 | Crypto cell arguable | Crypto cell | No assessor evidence | Acceptance unknown |
| P31–P35 visibility | R7 | Evidence creates demand | Passport, CBOM | CRA reporting live 11 Sep 2026 [2nd]; India mandates inventories [2nd]\[19\] | Demand unproven |
| **Missing:** update non-adoption | — | Signed updates get installed | — | aDolus 60%; SANS <30% | **Largest gap** |
| **Missing:** debug/ownership side doors | — | Secure boot is the authority chain | — | Silicon Labs, NXP, ST, OpenTitan docs [F]\[1\]\[2\]\[3\] | **Second-largest gap** |

### 2.3 Evidence register (rechecked claims)

| Claim | Source, date | Status |
|---|---|---|
| IR 8547 final: quantum-vulnerable PK deprecated after 2030, disallowed after 2035, at all approved strengths | PostQuantum.com analysis, 28 Oct 2026 [2nd] | Supported; NIST PDF not fetched. pqcmandates.com gives contradictory dates and is rejected\[20\] |
| EO 14412: PQC key establishment for HVAs by 31 Dec 2030, signatures by 31 Dec 2031; OMB M-26-15 plans in 120 days | arXiv 2609.26225; Quantum Computing Report [2nd] | EO number now corroborated by two secondaries\[21\]\[22\] |
| CRA: support ≥5 yr (Art 13(8)); updates available ≥10 yr (Art 13(9)); reporting 11 Sep 2026; full 11 Dec 2027 | BSI; Hunton; explainers | Supported. **Refined:** Article 14 reporting covers products already on the market\[23\]\[24\]\[25\] |
| Google ECDLP-256: ≤1,200 logical/90M Toffoli or ≤1,450/70M; <500k physical; minutes; ZK proof | Google Quantum AI, 30 Mar 2026 [F] | Supported\[26\]\[27\] |
| Gidney, Alice & Bob estimates; SP 800-208 rules | inherited | Not rechecked |
| SP 800-230 ipd: six SLH-DSA sets, 2^24 signatures/key | NIST CSRC, 13 Apr 2026 [F] | New; comments closed 12 Jun 2026\[28\]\[29\] |
| CNSA 2.0: firmware prefer 2025, exclusive 2030; v2.1 excludes HSS/XMSS^MT; "Starting in 2027, no new product for NSS should have a burned-in root of trust relying on a non-QR primitive"\[12\]\[13\] | PostQuantum.com; Quantum Sentinel quoting NSA FAQ [2nd] | Supported; secondaries conflict on ML-DSA for firmware\[13\]\[30\] |
| Campos LMS verify 2,658,884 cycles, ~1,044 B stack | IACR ePrint 2020/470, Table 10 [D] | Supported. "w=16" is Winternitz value 16 = LM-OTS W4. W8 (w=256), h=5 = 23,252,036 cycles\[31\] |
| SLotH: SLH-DSA-SHAKE-128s verify 179,603 cycles; Cortex-M4 software Keccak ≈12,000, SHA2-256 ≈3,000 cycles per call | Saarinen, NIST PQC conference 2024 [D] | New\[32\]\[33\] |
| MEC175xB "embedded immutable PQC" (ML-KEM, ML-DSA, LMS verify)\[34\] | Microchip, May 2025 [V] | Vendor claim stands, but it is a notebook/desktop/data-centre embedded controller, not OT evidence\[35\] |
| OpenTitan ROM PQ | OpenTitan docs; issue #30765 [F] | **Conflict:** docs say ROM supports ML-DSA-87 via OTBN; the RFC lists gaps (keys don't fit OTP slots, ownership ECDSA-only) and proposes ML-DSA-87 + P-384 hybrid. Treat as in progress\[10\]\[36\] |
| Adams Bridge leakage | Saarinen (May 2025); Karabulut & Azarderakhsh, ETSI (Jun 2026); project TVLA docs [D] | Supported: CPA on Oct 2024 release with 10,000 traces; own TVLA shows PWM leaking from ~5K traces with masking off; INTT passes 1M traces with masking on\[37\]\[38\]\[39\]\[40\] |
| TPM PQ | TCG TPM 2.0 Library v1.85, Mar 2026 (ML-KEM EK, ML-DSA AK) [F] | New TPMs only; installed TPMs stay classical\[41\]\[42\] |
| Composite ML-DSA | draft-ietf-lamps-pq-composite-sigs-19 in RFC Editor queue; EUF-CMA not SUF-CMA [F]\[43\]\[44\] | RFC 9881, 9909, 9964 published\[44\]\[45\] |
| "OPC UA has no PQ policy" | ShieldWorkz on 1.05.07 ECC; Paul et al. research [2nd] | No PQ policy found; OPC Foundation primary not checked\[46\] |
| India roadmap | DST report; ORF; PostQuantum.com | CII 2027/2028/2029; enclaves; labs by Dec 2026\[14\]\[16\]\[47\] |
| RP2040 ML-DSA figures | arXiv 2603.19340 [D] | **Conflict:** snippet gives ML-DSA memory 8.4–8.9 KB vs inherited 50.6 KB signing stack; unresolved\[48\] |

---

## 3. Previous Work Challenge Register

| # | Prior finding | Classification | Reason |
|---|---|---|---|
| C1 | Migration is authority continuity | Strongly supported | Matches CNSA 2.0 root-of-trust rule\[13\] |
| C2 | ROM verifier is "the true bottleneck" | Questionable assumption | Locked-flash stages exist; adoption is the bottleneck |
| C3 | ACK needs new ROMs ~2028 | Potentially incorrect | NSIB, OEMiRoT today [F] |
| C4 | Existing-ROM ACK variant | In conflict with evidence | If ROM-verified code is remotely replaceable, a classical forger replaces it; if write-locked, the lock, not the signature, provides security |
| C5 | Boot ≈42 ms with 1,452 B LMS | Potentially incorrect | 42 ms is W4 (2,508 B); W8 ≈363 ms software |
| C6 | "LMS + escrow" survives lattice break as two families | Missing dimension | Hash-based escrow shares one assumption class; all leaves depend on SHA-256 |
| C7 | Pre-rotation ≈10× | Potentially incorrect | 1.5–3× linear; 29× only with Merkle commitment |
| C8 | Campos "w=16" wrong | Refined | Winternitz 16 = W4; cycles valid |
| C9 | Stateful LMS for roots | Redesign | SP 800-230; keep LMS only where CNSA binds |
| C10 | Symmetric-first fabric | Strongly supported | 208–250 µs SV budget |
| C11 | Time-free counter validity | Supported but incomplete | Index floors ship; freeze detection unsolved |
| C12 | Threshold + neutral custodian | Not validated | No pull found; FDO vouchers exist |
| C13 | Crypto cell | Not validated | No assessor evidence |
| C14 | Passive CBOM | Will be absorbed | Incumbents parse OT protocols |
| C15 | Market $0.4–1.9B | Arithmetic fixed | $113.5M–$565M ÷ 0.30 = $0.38B–$1.88B; 10% = $38M–$188M; inputs unverified |
| C16 | MEC175xB/MCX A5/STM32G5 prove PQ ROM readiness | Questionable | MEC175xB is a PC/data-centre EC;\[35\] others not rechecked\[35\] |
| C17 | Threshold ML-DSA practical | Not validated | Multisignature meets OT goal without it |
| C18 | Top-20 ranking | Discard and rebuild | No sensitivity; inputs corrected |
| C19 | Seven-part portfolio complete | Missing dimension | Omits adoption, debug, provisioning, enclaves |
| C20 | TLS 1.3 downgrade limits | Strongly supported | CVE-2026-2673 pattern |
| C21 | OPC UA has no PQ policy | Not sufficiently validated | Single-practitioner basis |
| C22 | Hash engine as universal accelerator | Expand substantially | SLotH: ~two orders of magnitude\[33\] |

### Corrected arithmetic

**(a) Boot time [E].**
- Campos measured LMS SHA-256 verification at:
  - 2,658,884 cycles with Winternitz 16 (W4), h=10;\[31\]
  - 23,252,036 cycles with Winternitz 256 (W8), h=5.\[31\]
- At 64 MHz that is 2.66M/64M = 41.5 ms (W4, 2,508 B signature) and 23.25M/64M = 363 ms (W8, 1,452 B).
- With hardware SHA-256 at an assumed ~100 cycles per compression instead of ≈3,000, W8 becomes ≈23.25M × 100/3,000 ≈ 0.8M cycles ≈ 12 ms. This assumes hashing dominates the cost.
- **Rule:** use W4 without a hash engine; W8 with one.

**(b) Catch-up after N=10 missed rotations [E].**
- A key set is 5 × 1,952 + 200 = 9,960 B.
- A t=3 signature bundle is 3 × 3,309 = 9,927 B.

| Scheme | Bytes/step | N=10 total | vs TUF (298,140 B) |
|---|---|---|---|
| TUF walk | 29,814 | 298,140 | 1.0× |
| KERI-style pre-rotation | 19,887 | 198,870 | 1.5× |
| Pure hash-chain | 9,960 | 99,600 | 3.0× |
| Merkle over K=64 future sets | 9,960 + 6×32 | 10,152 | 29.4× |

- Only the Merkle variant gives a large saving. It requires keeping 64 pre-generated key sets secret for decades, and fixes their families at genesis.
- The previous E6 pass threshold (≥5×) **fails** for the scheme as specified.

**(c) Family independence [I].**
- Let A(k) be the set of assumptions key k depends on:
  - ML-DSA → {MLWE/MSIS, SHAKE}
  - SLH-DSA-SHAKE → {Keccak}
  - LMS-SHA256 → {SHA-256}
  - ECDSA → {ECDLP, SHA-2}
- A transition rule is **single-assumption-safe** if no single assumption's failure leaves an authorising quorum, unless that quorum spans at least two disjoint assumption sets.
- "LMS + SHA-256 escrow" fails this test after a SHA-256 break.
- **Minimum robust set:** {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256}, held by at least two organisations.

---

## 4. Additional problem hypotheses (55)

[F] documented; [I] inferred; [H] plausible, unverified. All are distinct from P1–P35.

| ID | Problem | Basis |
|---|---|---|
| N1 | Classical debug-unlock tokens give full access post-CRQC\[2\]\[49\] | Silicon Labs AN1190 [F] |
| N2 | Debug certificates chain to RoT keys; RoT break opens debug fleet-wide unless UUID-bound\[1\] | NXP AN13814 [F] |
| N3 | RMA lifecycle authorisations outlive product support\[50\] | Infineon TRAVEO RMA [F]; [I] |
| N4 | RDP Level 2 is permanent, blocking RMA and tempting weaker locks | ST [F]; [I]\[51\] |
| N5 | Ownership-transfer messages signed with ECDSA | OpenTitan [F]\[10\] |
| N6 | FDO vouchers are classical and stored off-device for years: harvest-now-forge-later on ownership\[11\] | FDO spec [F]; [I] |
| N7 | Whoever holds voucher files at OEM exit controls onboarding | [I] |
| N8 | Contract-manufacturer key injection under classical wrapping | [H] |
| N9 | Firmware-encryption keys wrapped with RSA/ECDH are harvestable | [I] |
| N10 | Fleet-wide shared symmetric keys: one extraction compromises all | [I] |
| N11 | DICE/IDevID identity certificates on ECDSA allow impersonation | [I] |
| N12 | Installed TPMs and secure elements can't gain PQ | TCG v1.85 [F]; [I]\[42\] |
| N13 | Patches available >10 years remain uninstalled | aDolus [V]\[52\] |
| N14 | Annual or biannual patch windows collide with emergency transitions | aDolus [V]; SANS\[52\] |
| N15 | 25–34% of OT advisories ship with no patch | Dragos Year in Review [V]: 34% (2022); 28% of 531 advisories (2023); 26% of 606 advisories (2024 data, 18% with neither patch nor mitigation); "25 percent of advisories had no patch or mitigation" (2025) |
| N16 | Feature-licence signatures forgeable | [H] |
| N17 | Relay setting files and SIS logic unsigned or classically signed | [I] |
| N18 | Workstations hold signing authority with weak custody | Armis press release, June 2023 [V]: "Fifty-six percent of engineering workstations have at least one unpatched critical severity [CVE] and 16% are susceptible to at least one weaponized CVE" |
| N19 | Vendor remote-access portals sit outside migration plans | [H] |
| N20 | A bug in a locked first stage has no fix path | [I] |
| N21 | Option-byte locks are vulnerable to fault injection | [I] |
| N22 | Monotonic floors can be burned by anyone holding a valid higher-index image | NSIB [F]; [I]\[6\] |
| N23 | Spares at index k can't boot images at k+3 without catch-up | [I] |
| N24 | Composite signatures are EUF-CMA only (malleability)\[43\] | IETF draft [F] |
| N25 | Devices pinning draft OIDs become orphaned | [I] |
| N26 | PQ accelerators ship partially masked\[37\]\[38\] | Adams Bridge [D]\[40\]\[53\] |
| N27 | Benchmark inconsistency misleads procurement | arXiv 2603.19340 [D] |
| N28 | CRA reporting covers legacy products; fixing duty doesn't | [I] |
| N29 | CRA 5-year support vs 20–40-year assets | [F]/[I]\[54\] |
| N30 | India's 2029 date forces de facto unstandardised enclaves\[14\]\[16\] | DST [2nd]; [I] |
| N31 | Incompatible "done" definitions across regimes | [I] |
| N32 | Owners can't verify OEM PQ claims until labs exist\[47\]\[55\] | DST [2nd] |
| N33 | Downtime cost dwarfs visit cost, so crypto work waits for planned outages | ABB, S&C [V]; [I]\[56\]\[57\] |
| N34 | No substation downtime benchmark | [I] |
| N35 | Insurers lack crypto-state loss data | [H] |
| N36 | Refurbished OT gear carries prior identity or unlocked debug | [H] |
| N37 | Decommissioned certificates stay in trust lists | [I] |
| N38 | OPC UA AutoAccept and SecurityMode None make PQ policy moot | ShieldWorkz/Trout [V]\[58\] |
| N39 | Engineering archives restore old key indices | [I] |
| N40 | Merkle-committed future keys must stay secret 20+ years | [I] |
| N41 | A bankrupt threshold signer freezes a fleet | [I] |
| N42 | Unauthenticated PTP undermines ordering | [H] |
| N43 | KDC and enclave gateways are fleet-wide targets | [I] |
| N44 | Agility configuration enables downgrade | CVE-2026-2673 [inherited] |
| N45 | Strict hybrid pinning breaks interop, so operators disable security | [I] |
| N46 | Monitoring taps become privileged positions | [I] |
| N47 | AI configuration tools bypass signing quorums | [H] |
| N48 | Recertification bundles delay crypto updates | [I] |
| N49 | Mid-support algorithm sunsets are unpriced in contracts | [I] |
| N50 | Devices can't state which keys they trust | [I] |
| N51 | LMS state can't migrate between HSM vendors | [I] |
| N52 | Facility M&A omits authority diligence | [H] |
| N53 | Spare-parts brokers resell stale-root devices | [H] |
| N54 | ZK-proof-only estimates limit independent timeline checks | Google [F]\[59\] |
| N55 | PQ RoT silicon is data-centre-first; OT MCUs lag | [I] |

More candidates (fuse ageing, flash retention) lacked evidence and were folded into N20/N21.

---

## 5. Hidden lifecycle, state, human and economic problems

**Lifecycle.** At least five classical side doors exist outside secure boot:
- debug (N1–N2);
- RMA (N3);
- ownership (N5–N7);
- provisioning (N8);
- configuration (N17).

A CRQC attacker uses whichever is cheapest.

**State.** Monotonic floors already ship. The overlooked risk is that they can be burned against the owner (N22). So raising a floor must need stronger authorisation than booting.

**Human.**
- Patching happens in annual or biannual windows (aDolus). Only 15% of facilities patch in routine windows, per SANS's 2023 survey of 700+ respondents.
- Key knowledge leaves with integrator staff.
- "Don't update" is rational given the downtime cost. ABB's "Value of Reliability" survey (Sapio Research, July 2023, 3,215 respondents) reports a median of $124,669 per hour of unplanned downtime (about $103,000 in the US). "More than two-thirds" of respondents have an unplanned outage at least monthly [V].

**Economic.** Visit costs are small. S&C Electric's GridTalk (March 2017) reports that "Many utilities take an ultra-conservative guess, claiming truck rolls each average $250 to $500" [V]. TSIA's figure of ~$1,000 is quoted by a vendor blog. The problem is schedule risk, not labour.

---

## 6. Findings from the ten stakeholder perspectives

| Perspective | Unique discovery | Would reject | Main conflict |
|---|---|---|---|
| Operator | Crypto must ride existing windows; "explain what changed" | New outages, vendor cloud, new skills | Cryptographer's fast deprecation |
| Embedded engineer | Hash hardware decides feasibility (M4 SHA2 ≈3,000; Keccak ≈12,000 cycles/call) | ML-DSA signing on M0+ | Purist\[32\] |
| Cryptographer | Single-assumption-safe rule; composite is EUF-CMA only | SHA-256 monoculture | Minimalist |
| Attacker | Cheapest path is debug or voucher; floors can be burned | — | Operator convenience |
| OEM | First stage is a firmware deliverable; CRA 5 years caps promises | Kernel tied to one MCU vendor | Operator's 30-year wish |
| Integrator | FDO is the only standard ownership chain | Competitor-owned root-of-roots | Custodian model |
| Safety engineer | Crypto failure must keep last-known-good running | Fail-secure boot in SIS | Auditor |
| Economist | Value = avoided unplanned downtime + compliance evidence | Per-device subscriptions | Entrepreneur |
| Standards researcher | Reuse FDO, RFC 9881/9909, TCG v1.85, SP 800-230 | New proprietary formats | Inventor |
| Future designer | Every device: SHA-2+SHA-3, locked stage with ≥3 key-hash slots over ≥2 classes, PQ debug and vouchers | Single-algorithm ROMs | — |

---

## 7. Problem-to-Intervention-Level Matrix

●● = best leverage per burden; ● = useful; ○ = poor; — = not applicable.

| Problem | Crypto | Silicon | Firmware | Protocol | Topology | Authority | Lifecycle | Procedure | Procurement | Standards | Eliminate requirement |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Algorithm-bound anchors | ● | ● | **●●** locked stage | — | — | ● | ● | — | ● | ● | — |
| Update non-adoption | ○ | ○ | ● A/B | ● | ● | ○ | **●●** | **●●** window staging | ● | ○ | ● stable first stage |
| Debug/RMA | ● | ● | ● | — | — | ● UUID | **●●** | ● | **●●** | ● | **●●** no field debug |
| Ownership | ● | — | ● | ● FDO | — | **●●** | ● | ● | ● | **●●** FDO-PQ | — |
| Large signatures | ● SP 800-230 | **●●** hash engine | ● | ● | ● | — | — | — | — | ● | ● verify once |
| Offline revocation | ○ | — | ● | — | ● | ● | ● | ● | — | — | **●●** no remote path |
| Process bus | — | — | — | ● | **●●** enclave | — | — | — | — | ● | **●●** keep MACs |
| Orphaned fleets | — | — | ● | ● | — | ● | ● | ● | **●●** escrow | ● | — |
| Legacy un-updatable | ○ | ○ | ○ | ● | **●●** enclave | — | ● | ● | ● | — | — |
| Config authority | ● | — | ● | ● | ● | **●●** quorum | ● | ● | — | — | — |

**Highest leverage:** procedure and lifecycle changes, procurement clauses, and one firmware artefact.

---

## 8. Opportunities for eliminating complexity

1. **Eliminate new ROM.** Use a locked-flash first stage.
   - Removes: the mask-ROM dependency and licensing.
   - Adds: reliance on lock integrity.
2. **Eliminate stateful root custody.** Use SP 800-230 SLH-DSA once final, keeping LMS only under CNSA 2.0.
   - Removes: index reservation and catastrophic state reuse.
   - Adds: larger signatures and slower verification without a hash engine. A post on X by @conduition_io, not NIST, puts the smallest draft set at 3,856 B. bc-java issue #2402 lists the 192-24 set at 7,752 B and the 256-24 set at 14,944 B.
3. **Eliminate threshold cryptography.** Use multisignatures (≈9.9 KB for three ML-DSA-65 signatures).
4. **Eliminate the time-free layer as a product.** Index floors already ship.
5. **Eliminate field debug.** Disable it after commissioning and handle RMA by board swap. This removes N1–N3.
6. **Eliminate per-device PQ for un-updatable assets.** Use enclave containment instead.
7. **Eliminate a custom passport format.** Use CycloneDX CBOM plus TCG/IETF attestation.

---

## 9. Second- and third-order consequences

```
Locked first stage ──► no silicon dependency
   ├─► first-stage bug unfixable (N20) ──► formal verification of ~13 KB
   └─► RDP2 blocks RMA (N4) ──► weaker lock shipped ──► side door reopens
                                  └─► mitigation: board-swap RMA + PQ debug cert
FDO-PQ vouchers ──► orphan recovery without custodian
   ├─► voucher files become crown jewels (N7) ──► escrow vouchers, not keys
   └─► M&A diligence must include vouchers (N52)
Enclave containment ──► fast compliance (India 2029)
   ├─► gateway concentration (N43)
   └─► "temporary" enclaves become permanent; inside never migrates
Symmetric fabric ──► process bus untouched
   └─► KDC compromise fleet-wide ──► per-device key diversification (N10)
Window staging ──► adoption without downtime
   └─► attackers learn windows ──► staged artefacts signed and attested
```

- **Complexity transfer:** the redesign moves complexity into contracts and existing standards that already have owners. The custodian would have created a new organisation.
- **Lock-in:** a locked stage is lock-in by design. Mitigate with ≥3 slots across ≥2 assumption classes and an open reference.
- **Monoculture:** a shared open stage spreads one bug everywhere. Mitigate with formal verification and two independent implementations.

---

## 10. New Technology Discovery Register

| Technology | Origin | Mechanism | OT use | Evidence | Adaptation | Limitation |
|---|---|---|---|---|---|---|
| Locked-flash immutable boot (NSIB, OEMiRoT/HDP) | IoT boot | Write-protect + readout lock + hide-after-boot | PQ first stage without ROM | [F] | Add LMS/SLH-DSA + multi-class slots | Fault injection\[60\] |
| Monotonic key-index invalidation | Key decommissioning | Using key i revokes < i | Sunset latch exists | [F] | Stronger auth to advance | Burn attack\[7\] |
| SP 800-230 SLH-DSA | Firmware/cert signing | Few-time-tuned hypertree | Stateless roots | [F] draft | Await final; benchmark | Not CNSA\[29\] |
| SLotH hash unit | RoT boot | In-unit padding/iteration | Cheap SLH-DSA/LMS verify | [D] | MCU security subsystems | 63–155 kGE\[33\] |
| FIDO Device Onboard | IoT onboarding | Off-device voucher chain, late binding\[17\]\[18\] | Ownership transfer, orphan recovery | [F] | PQ signature profile | OT adoption unproven |
| Arm ADAC / vendor debug auth | Secure debug | Lifecycle-scoped cert-chain unlock\[61\] | Close debug door | [F] | PQ certs | Physical ports |
| TCG TPM v1.85 | Attestation | ML-KEM EK, ML-DSA AK | Gateway/EWS identity | [F] | Use in gateways | Not in MCUs\[42\] |
| Composite ML-DSA | PKIX | AND of two signatures\[62\] | Transitional certs | [F] draft | Avoid draft OIDs | EUF-CMA only |
| RTL masking analysis | Hardware SCA | Detect share convergence | PQ IP acceptance | [D] | Apply to MCU IP | Pre-silicon only\[63\] |
| CycloneDX CBOM | Supply chain | Crypto inventory | Fleet evidence | inherited | OT parsers | Absorbed by incumbents |
| SDLS symmetric keys | Spacecraft | Pre-shared hierarchy | Disconnected assets | inherited | — | Key distribution |

---

## 11. Alternatives to the leading approaches

| Objective | Previous | Alternative | Alternative wins when | Previous wins when |
|---|---|---|---|---|
| Boot survives algorithm break | ACK in new ROM/OTP | Locked first stage, ≥3 slots, ≥2 classes | Lockable MCUs exist | No lockable flash; high physical threat |
| Root signing | Stateful LMS + custody | SP 800-230 SLH-DSA | Commercial OT | CNSA 2.0 systems |
| Ownership | Threshold + custodian | FDO-PQ + contractual voucher escrow | Multi-OEM fleets | Single strong operator |
| Offline revocation | Counter layer | Index floor + enclave | Disconnected assets | — |
| Legacy | Gateway + passport | Enclave + replacement schedule | Un-updatable assets | — |
| Catch-up | Linear pre-rotation | Merkle future sets, or plain TUF | Long-offline | Future-key secrecy untenable |
| Debug | — | Disable; PQ debug certs | Production units | Lab/RMA units |
| Adoption | — | Window-aligned signed staging | Everywhere | — |

---

## 12. The competing architecture debate

- **A — Purist.**
  - Problem: side doors.
  - Prefers: slots for ML-DSA + SLH-DSA-SHAKE + LMS-SHA-256; the single-assumption rule; PQ debug and vouchers.
  - Attacks B: "one hash is a monoculture."
  - Weakness: cost on M0+.
  - Changes mind if SP 800-230 verify on a hash-engine MCU exceeds 100 ms.
- **B — Minimalist.**
  - Problem: RAM and boot time.
  - Prefers: one hash verifier in the first stage; ML-DSA only in the updatable second stage.
  - Attacks A: "three verifiers are three bug surfaces."
  - Changes mind on a structural attack on SHA-256 or SHAKE.
- **C — Pragmatist.**
  - Problem: non-adoption.
  - Prefers: window staging, enclaves, replacement plans.
  - Attacks all: "nothing helps if updates sit uninstalled."
  - Weakness: leaves HNDL-to-authority open.
  - Changes mind if pilots show >80% remote adoption without downtime.
- **D — Distributed systems.**
  - Problem: divergent trust state.
  - Prefers: floors, signed state digests, gossip of the highest floor.
  - Attacks C: "enclaves diverge silently."
  - Weakness: protocol surface.
- **E — Hardware.**
  - Problem: flash locks are weaker than ROM; no hash engine.
  - Prefers: SHA-2+SHA-3 engines and OTP key-hash slots via procurement.
  - Attacks B: "software W8 takes 363 ms."
  - Changes mind if fault tests show locks hold.
- **F — Safety.**
  - Problem: recertification bundling.
  - Prefers: crypto confined to boot/update; failures degrade privileges, never safety functions; last-known-good retained.
  - Attacks A: fail-closed in an SIS is a hazard.
- **G — Auditor.**
  - Problem: unverifiable claims.
  - Prefers: independent labs (India Tier-1/2),\[47\] TVLA requirements, benchmark methodology.
- **H — Entrepreneur.**
  - Problem: no quantum budget line.
  - Prefers: sell compliance evidence and adoption tooling; PQ comes as a by-product.
  - Changes mind on a paid pilot.

**Convergence:**
- **Agreement:** a hash-based locked first stage, closed side doors, and a symmetric process bus.
- **Unavoidable trade-off:** diversity (A) versus surface (B). Resolve with diversity in slots and assumption classes, one formally verified verifier per class.
- **Clearly superior point:** C's adoption argument.
- **Class-dependent:** hash engines for new designs, enclaves for legacy.
- **Unresolved:** custodian acceptance and assessor acceptance.

---

## 13. Redesigned minimal and high-assurance architectures

### 13.1 Continuity First Stage (replaces ACK)

**Minimal (MV-1):**
- A locked first stage of ≈13 KB (inherited verifier figure 12,864 B).
- One hash verifier: LMS W4 (2,508 B; ≈42 ms at 64 MHz in software), or SLH-DSA-few once final.
- Three key-hash slots (96 B) and an index floor.
- Advancing the floor needs a signature from a different slot.
- No time, no network.

**High-assurance (HA-1):**
- Hardware SHA-2/SHA-3.
- Slots spanning {LMS-SHA-256, SLH-DSA-SHAKE, ML-DSA-65 verified in the second stage}.
- Single-assumption-safe rule.
- A/B second stages plus last-known-good.
- TLA+-verified state machine and a lock fault-injection campaign.
- UUID-bound PQ debug credentials, with debug disabled after commissioning.

```
[Reset] → [Locked first stage: hash verifier + 3 key-hash slots + floor]
             │ verify (LMS/SLH-DSA)        trust boundary: write-locked flash
             ▼
       [Second stage A | B] ─ ML-DSA/hybrid, protocol PQ
             │ fail → other slot → fail → last-known-good (keep running)
             ▼
       [Application]
Authority: slot1 OEM, slot2 OEM alt-class, slot3 operator/escrow
Floor advance: signature from slot ≠ current
Recovery: board swap (debug disabled)
```

**Compared with the ACK:**
- Removes: new ROM, the sunset fuse, the OTP Merkle manifest and licensing.
- Adds: reliance on lock integrity.

### 13.2 Ownership Continuity (replaces threshold custodian)

- **Minimal:** FDO vouchers with an ML-DSA or SLH-DSA profile, escrowed by contract with the operator. Slot 3 holds the operator's key hash.
- **High-assurance:**
  - Dual-class voucher signatures.
  - An OEM-exit trigger in the contract (end of CRA support, or insolvency).
  - A transfer log witnessed by two parties.

```
OEM ─signs─► Voucher ─► Distributor ─► Integrator ─► Operator  (off-device)
OEM exit: voucher chain + escrow release ─► rewrite slot3 via floor rule
```

### 13.3 Symmetric Process-Bus Fabric (kept)

- **Minimal:**
  - ML-KEM-768 enrolment at commissioning.
  - KDC inside the enclave.
  - Unchanged IEC 62351-6 MACs.
  - Per-device key diversification.
- **High-assurance:** replicated KDC with t-of-n unlock, TPM v1.85 identity, and a GDOI-PQ profile.

### 13.4 Enclave Containment (new)

- **Minimal:** a PQ-terminating gateway, a passive inventory, and a dated replacement plan.
- **High-assurance:** two gateways from different vendors, TPM identity, signed configuration and witnessed logs.

**Essential vs optional:**
- **Essential:** the locked hash first stage, ≥3 slots, the floor rule, closed debug, PQ vouchers, symmetric bus and enclaves.
- **Optional:** threshold crypto, custodians, pre-rotation, a time layer, insurance pricing.

---

## 14. Real-world deployment scenarios

| Scenario | Architecture | Key steps | Failure points | Remaining risk |
|---|---|---|---|---|
| A New device | HA-1 + FDO-PQ + PQ debug | Choose lockable MCU with hash engine; provision 3 key hashes; disable debug at commissioning; ship voucher | CM key injection (N8) | Lock faults |
| B Unmodifiable device | Enclave | Inventory; segment; PQ gateway; schedule replacement | Gateway concentration | No device-level guarantee |
| C Mixed-vendor | Zone enclaves + CBOM + FDO where supported | Map authority incl. debug and EWS; per-class controls | Integrator handover | Divergent state |
| D Long-disconnected | MV-1 W4; Merkle future keys if needed | Pre-commit; update at visits | Freeze attack | Future-key secrecy |
| E OEM gone | Voucher escrow → slot 3 | Present chain; advance floor | Voucher lost | Without slot 3: replace |
| F Emergency break | Floor advance via other-class slot | Sign with SLH-DSA/LMS; stage next window or emergency window | $124,669/h median downtime (ABB 2023 survey [V]) | Single-class assets |
| G Fleet transition | Window staging | Inventory → lab rehearsal → staged → signed state reports | Non-adoption | 1–2 window cycles |

**Survives deployment:** locked stage, enclaves, staging, debug closure, vouchers.

**Paper-only:** custodian, threshold ML-DSA, time layer, insurance pricing.

---

## 15. Economic and commercial analysis

**Who is who:**
- The operator experiences the problem and owns the asset.
- The OEM controls the technical decision.
- The operator's maintenance budget pays.
- Liability is split by the CRA: OEM during support, operator after.
- The integrator implements.
- Plant engineering and procurement can block.

**Model for a 10,000-device fleet [E].** Assumptions:
- 20 devices per visit.
- Full visit $1,000; planned-window marginal cost 25% of that.
- 33% of emergency visits need a second trip (Aberdeen, via a vendor blog).\[64\]
- r = remotely updatable share. No source measures r, so it is varied.

| r | Visits | Planned ($250/visit) | Emergency ($1,000 × 1.33) |
|---|---|---|---|
| 0.1 | 450 | $112,500 | $598,500 |
| 0.4 | 300 | $75,000 | $399,000 |
| 0.7 | 150 | $37,500 | $199,500 |

**Downtime sensitivity:**
- If each emergency visit at r = 0.1 causes one hour at ABB's survey median ($124,669, rounded here to $125,000): 450 × $125,000 = $56.25M.
- If only 5% of visits do: $2.81M.

**Reason to act early:** converting emergency work into planned-window work is worth roughly $2.8M–$56M per 10,000 devices, against $0.04M–$0.11M for planned visits. Downtime figures are vendor-sponsored and plant-oriented.

**Market (inherited, corrected):** $0.38B–$1.88B global; $38M–$188M for a 10% vendor. Not for fundraising.

**Business models, ranked by fit:**
1. Open first-stage reference plus a paid porting and assurance service.
2. Compliance-evidence product (CRA Article 14, India CII inventories).
3. Window-aligned migration engineering.
4. Procurement-clause libraries and test-lab services.

Weak fits: per-device subscriptions and a custodian utility.

**Value without quantum concern:** firmware governance, update adoption, OEM-exit protection, compliance evidence.

---

## 16. The strongest practical starting points

| Entry | Smallest prototype | Standalone value | Credibility evidence | Next |
|---|---|---|---|---|
| Continuity first stage | wolfBoot/MCUboot-derived locked stage on STM32U5/H5 and nRF5340, LMS W4, 3 slots | OEM "PQ-ready boot" claim | Boot time, fault tests, TLA+ | 5 families; SLH-DSA-few |
| Side-door audit kit | Checklist + scripts mapping debug, lifecycle, ownership, provisioning per part | Real authority map | Audit of 10 MCU families | PQ debug profile |
| FDO-PQ voucher | PQ entries in open FDO | OEM-exit continuity | 2-OEM interop | FIDO contribution |
| Window staging | Signed staging + state report on lab fleet | Adoption | Pilot adoption rate | Product |

**Roadmap A (0–9 months):**
- Build the audit kit and first-stage prototype; run E-A1 to E-A4.
- **Gate:** if fewer than 50% of MCU families are lockable, pivot to silicon procurement asks.

**Roadmap B (9–24 months):**
- Open release with formal verification.
- FDO-PQ contribution.
- Evidence product.
- Indian power/telecom CII pilots.
- **Gate:** one paid pilot. Abandon the evidence product if incumbents ship it first.

**Roadmap C (2–10 years):**
- Procurement standard text: hash engine, ≥3 slots over ≥2 classes, PQ debug and vouchers, no field debug.
- Submissions to IEC 62443-4-2 and national lab criteria.
- **Gate:** two OEM adopters.

---

## 17. Prioritised experiments

| ID | Question | Experiment | Cost | Support / disprove | Decision |
|---|---|---|---|---|---|
| E-A1 | Share of industrial MCU families with lockable first stage | Desk survey: ST, NXP, Renesas, Microchip, TI, Infineon, Nordic, Silicon Labs, Espressif, GigaDevice | 2 weeks | ≥50% / <30% | New ROM or not |
| E-A2 | Verify cost of LMS W4/W8, SP 800-230, ML-DSA-44 on M0+/M33 ± HW SHA | Owned boards | 4 weeks | ≤100 ms / >300 ms | Algorithm |
| E-A3 | Which authorisation paths are classical | Docs + lab | 3 weeks | — | Clauses |
| E-A4 | Can option-byte locks be faulted | Voltage/EM glitching on owned parts | 6 weeks | Hold / fail | Flash vs ROM |
| E-B1 | Real remote-update adoption | Read-only measurement at consenting operator | 3 months | — | Priority |
| E-B2 | Single-assumption rule | TLA+/Tamarin | 6 weeks | No path / counterexample | Slots |
| E-B3 | FDO-PQ interop | Open FDO + PQ | 8 weeks | Works / size breaks | Standard |
| E-B4 | Floor-burn attack | NSIB-style lab demo | 2 weeks | Exploitable / not | Floor rule |
| E-C1 | Assessor acceptance | Interviews with two bodies | 2 months | Accept / reject | Safety |
| E-C2 | Independent review | Third-party audit | Budget | — | Release |

**Highest information value:** E-A1. It is cheap and decides the whole silicon-ROM strand.

All experiments run on owned or authorised equipment only.

---

## 18. Independent challenge-board findings

- **Main misunderstanding:** that the root is the bottleneck. Adoption and side doors are.
- **Main unsolved problem:** installed devices with classical-only immutable verifiers and no lock. Only containment and replacement help them.
- **Impressive but commercially irrelevant:** ACK ROM licensing; threshold ML-DSA succession.
- **Attractive but technically weak:** unverified "PQ-ready" labels; attestation-priced insurance.
- **Unnecessary components:** OTP Merkle manifest, sunset latch, custodian, time layer.
- **Concentration risks:** the KDC, enclave gateways, and any root-of-roots.
- **Overemphasised:** offline revocation, time, pre-rotation.
- **Underemphasised:** debug/RMA, vouchers, factory provisioning, adoption.
- **Existing tech doing more than recognised:** NSIB/OEMiRoT, FDO, TPM v1.85, SP 800-230.
- **Strongest argument against the lead:** fault injection can bypass flash locks, and first-stage bugs are permanent.
- **Abandonment evidence:** E-A4 shows a reliable bypass, or E-A1 shows few lockable families.
- **Overworked assumptions:** that operators update when it is cheap; that SP 800-230 finalises as drafted.
- **Operator objection:** any new outage or cloud dependency.
- **Cryptographer objection:** treating SHA-2 and SHA-3 as fully independent.
- **15-year liability:** the open first stage needs a maintainer foundation.
- **Vendor disappears:** survivable only if slot 3 is provisioned at manufacture.
- **Obsolescence:** three slots give one generation of headroom, not unlimited headroom.

---

## 19. Revised rankings

**Criteria:** security gain, deployability on existing silicon, burden removed, evidence and pull. Tested under security-heavy (40/20/15/15/10) and deployability-heavy (20/35/20/15/10) weightings.

| Rank | Invention | Prior rank | Robust to weights? |
|---|---|---|---|
| 1 | Locked continuity first stage (dual-class slots, floor rule) | 1, 3 | Yes |
| 2 | Side-door closure: PQ debug, field-debug disable, lifecycle audit | new | Yes |
| 3 | Symmetric process-bus fabric with diversification | 2 | Yes |
| 4 | FDO-PQ vouchers with contractual escrow | replaces 5, 6 | Yes |
| 5 | Window-aligned staging with signed state reports | new | Yes |
| 6 | Enclave containment + replacement schedule | 20 | Security-heavy: 7 |
| 7 | Fleet crypto-state evidence | 10, 15 | No |
| 8 | Workstation signing quorum | 13 | No |
| 9 | Hash-engine procurement requirement | 11 | Security-heavy: 6 |
| 10 | Merkle-committed future keys | 9 | No |
| — | Custodian utility; threshold ML-DSA; time layer; insurance | 4–6 | Research only |

---

## 20. Most important unanswered questions

| Question | Importance | Uncertainty | Could change architecture? |
|---|---|---|---|
| Lockable first-stage share | Very high | Medium | Yes |
| Lock fault resistance | Very high | High | Yes |
| Real OT remote-update adoption (no survey measures it) | Very high | High | Yes |
| Final SP 800-230 parameters and MCU verify cost | High | Medium | Yes |
| CNSA acceptance of SLH-DSA for firmware | Medium | Medium | Defence OT |
| OPC UA PQ policy roadmap | Medium | High | Protocol plans |
| Assessor acceptance of crypto confinement | High | High | Safety design |
| Substation downtime cost | Medium | High | Business case |
| Contract-manufacturer key-injection crypto | High | High | Provisioning |
| MCU-class PQ IP side-channel maturity | High | Medium | Silicon choice |

---

## 21. Next-stage roadmap

| Window | Engineering | Research | Commercial | Gate |
|---|---|---|---|---|
| 0–3 mo | Audit kit; E-A1; E-A3 | E-A2 | Interview 5 OEMs, 5 operators incl. Indian CII | ≥50% lockable |
| 3–9 mo | Prototype on 2 families; TLA+ | E-A4; E-B4 | Draft clauses | Locks hold; ≤100 ms |
| 9–18 mo | Open release; FDO-PQ; staging pilot | E-B1 | Paid pilot | One paying pilot |
| 18–36 mo | 5 families; second implementation | SP 800-230 final | Evidence product; FIDO/IEC submissions | Two OEMs |

---

## Tables A–G

**Table A — What we thought vs what we now understand**

| Previous belief | Now | Status |
|---|---|---|
| ROM verifier is the bottleneck | Adoption and side doors are | Rejected |
| ACK needs new ROM | Locked flash suffices on many parts | Rejected pending E-A1 |
| ≈42 ms with 1,452 B signature | 42 ms needs W4; W8 ≈363 ms | Refined |
| Pre-rotation ≈10× | 1.5–3×; 29× Merkle | Refined |
| LMS + escrow = two families | Need disjoint assumption classes | Refined |
| LMS custody is a business | SP 800-230 erodes it | Rejected for commercial OT |
| Symmetric-first fabric | Unchanged | Survived |
| Time-free validity is an invention | Floors already ship | Refined |
| Custodian defensible | No demand evidence | Downgraded |
| MEC175xB shows OT PQ silicon | PC/data-centre EC | Rejected as evidence |
| CRA excludes legacy | Reporting covers legacy | Refined\[25\]\[65\] |

**Table B — Problems solved by one architectural intervention**

| Intervention | Problems |
|---|---|
| Locked stage + dual-class slots + floor rule | P1, P2, P8, P11, P12, P24, P26, N23 |
| No field debug + PQ debug creds | N1, N2, N3, N36 |
| FDO-PQ + escrow clauses | P23, P31, N5, N6, N7, N52, N53 |
| Enclave containment | P16, P21, N12, N30, N38 |
| Window staging | N13, N14, N33, N48, P28 |

**Table C — Complexity removed vs introduced**

| Design | Components | Trust relationships | Dependencies | Resources | Maintenance |
|---|---|---|---|---|---|
| Previous ACK | ROM + OTP manifest + latch + escrow | 4–5 | MCU vendor ROM | 32 B OTP + fuses | Licence |
| MV-1 first stage | Locked stage + 3 hashes | 3 | Lock integrity | ~12.9 KB flash, 96 B | Open project |
| Threshold custodian | Utility + signers | 3+ orgs | Legal, liveness | — | High |
| FDO-PQ | Voucher files | Chain | FDO | KB-scale | Low |

**Table D — Strongest competing approaches**

| Problem | Approach 1 | Approach 2 | Guarantee difference |
|---|---|---|---|
| Boot trust | Mask-ROM PQ verifier | Locked-flash stage | ROM resists faults; flash ships now |
| Root signatures | LMS | SLH-DSA-few | LMS smaller; SLH-DSA no state catastrophe |
| Ownership | Threshold custodian | FDO-PQ voucher | Custodian adds liveness risk; voucher simpler |
| Legacy | Gateway + passport | Enclave + replacement | Enclave honest about limits |

**Table E — Long-term lifecycle risks** (assumes CRQC plausible 2030–2040, 5-year CRA support, 25-year assets)

| Architecture | 5 yr | 10 yr | 20 yr | 40 yr |
|---|---|---|---|---|
| Classical legacy | Containable | Side doors forgeable if CRQC | Replace | — |
| First stage | Fine | One floor advance | Slot exhaustion possible | Replace; hash conservatism helps |
| Symmetric fabric | Fine | KDC refresh | Platform replaced | Protocol replaced |
| FDO-PQ | Fine | OEM exits: vouchers used | Format migration | Unknown |
| Enclave | Fine | Boundary refresh | Becomes permanent risk | — |

**Table F — Research priorities (1–5)**

| Question | Importance | Uncertainty | Info value | Changes architecture | Total |
|---|---|---|---|---|---|
| E-A1 lockable share | 5 | 3 | 5 | 5 | 18 |
| E-A4 lock faults | 5 | 4 | 4 | 5 | 18 |
| E-B1 adoption | 5 | 5 | 4 | 3 | 17 |
| E-A3 side doors | 5 | 3 | 4 | 4 | 16 |
| E-A2 benchmarks | 4 | 3 | 4 | 4 | 15 |
| E-C1 assessors | 4 | 5 | 3 | 3 | 15 |

**Table G — New opportunity map**

| Type | Opportunity |
|---|---|
| Technology | Locked hash first stage; SLH-DSA-few; hash engines |
| Product | Side-door audit kit; evidence product; window staging |
| Infrastructure | Open first-stage foundation; FDO-PQ profile |
| Research | Single-assumption-safe rules; lock fault resistance; floor-burn defence |
| Commercial entry | OEM porting/assurance; India CII pilots; test-lab services |

---

## Caveats

- **Coverage:** far below the 500–600 sources invited. Unrechecked items include quantum estimates beyond Google's, threshold ML-DSA results, TI/NXP/ST PQ ROM claims, IEC 62351 details and the OPC UA roadmap.
- **Secondary sourcing:** IR 8547 final and EO 14412 rest on secondary reports.
- **Vendor-sponsored data:** the economic figures come from Siemens, ABB, Dragos, Claroty, Armis and aDolus. No survey measures remote updatability.
- **Draft standard:** SP 800-230 may change before it is final.
- **Estimate:** hardware-SHA boot scaling assumes hash-dominated cost.

## Sources

1. [AN13814 Debug Authentication on RW61x Rev. 4.0 — 14 November 2024](https://www.nxp.com/docs/en/application-note/AN13814.pdf)
2. [05 Debug Unlock](https://docs.silabs.com/iot-security/1.2.3/series2-secure-debug/05-debug-unlock)
3. [Security:Debug Authentication - stm32mcu - ST wiki](https://wiki.st.com/stm32mcu/wiki/Security:Debug_Authentication)
4. [nRF Secure Immutable Bootloader — nRF Connect SDK 3.4.99 documentation](https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/samples/bootloader/README.html)
5. [sdk-nrf/samples/bootloader/README.rst at main · nrfconnect/sdk-nrf · GitHub](https://github.com/nrfconnect/sdk-nrf/blob/main/samples/bootloader/README.rst)
6. [nRF Secure Immutable Bootloader — nRF Connect SDK 1.6.1 documentation](https://nrfconnectdocs.nordicsemi.com/ncs/1.6.1/nrf/samples/bootloader/README.html)
7. [Immutable bootloader — nRF Connect SDK 1.3.2 documentation](https://nrfconnectdocs.nordicsemi.com/ncs/1.3.2/nrf/samples/bootloader/README.html)
8. [Security:OEMiRoT for STM32C5 - stm32mcu - ST wiki](https://wiki.st.com/stm32mcu/wiki/Security:OEMiRoT_for_STM32C5)
9. [How can we achieve a Root of Trust feature for insecure 32-bit ARM microcontrollers?](https://community.st.com/t5/stm32-mcus-security/how-can-we-achieve-a-root-of-trust-feature-for-insecure-32-bit/td-p/135157)
10. [\[RFC\] CNSA 2.0 Compliance Rooted in the ROM · Issue #30765 · lowRISC/opentitan · GitHub](https://github.com/lowRISC/opentitan/issues/30765)
11. [FIDO Device Onboard Specification](https://fidoalliance.org/specs/FDO/FIDO-Device-Onboard-WD-v2.0-20250617/FIDO-Device-Onboard-WD-v2.0-20250617.html)
12. [NSA Updates CNSA 2.0 After NIST Finalizes PQC Standards](https://postquantum.com/security-pqc/nsa-cnsa-2-0-faq-v2-1-update/)
13. [CNSA 2.0 and the 1 January 2027 Deadline: What NSA’s Rules Require, and What They Don’t](https://quantumsentinel.uk/cnsa-2-0-1-january-2027-deadline/)
14. [Post-Quantum Cryptography Migration: The 2026 to 2035 Deadline Map](https://www.depthgrid.in/2026/10/post-quantum-cryptography-migration-deadlines.html)
15. [Report on Quantum-Safe Ecosystem in India Government of India](https://dst.gov.in/sites/default/files/Quantum-Safe-Ecosystem-in-India.pdf)
16. [India’s Post-Quantum Cryptography Migration Roadmap](https://www.orfonline.org/expert-speak/india-s-post-quantum-cryptography-migration-roadmap)
17. [FIDO device onboarding integrated into IoT identity access management - Embedded](https://www.embedded.com/fido-device-onboarding-integrated-into-iot-identity-access-management/)
18. [FIDO Device Onboard (FDO) Overview](https://fidoalliance.org/device-onboarding-overview/)
19. [India Reveals National Plan for Quantum-Safe Security](https://thequantuminsider.com/2026/02/09/india-reveals-national-plan-for-quantum-safe-security/)
20. [NIST IR 8547 Final: What Changed From the Draft](https://postquantum.com/security-pqc/nist-ir-8547-final/)
21. [NIST Releases Final IR 8547 Establishing Definitive Post-Quantum Cryptography Transition Timeline and Deprecation Schedules - Quantum Computing Report](https://quantumcomputingreport.com/nist-releases-final-ir-8547-establishing-definitive-post-quantum-cryptography-transition-timeline-and-deprecation-schedules/)
22. [Quantum-Ready Secure WAN: A Risk Assessment and Migration Framework](https://arxiv.org/pdf/2609.26225)
23. [Cyber Resilience Act: EU CRA Requirements](https://www.bdemerson.com/article/cyber-resilience-act)
24. [The Cyber Resilience Act Explained: Scope, Classes & Deadlines · cyberresilienceact.eu](https://www.cyberresilienceact.eu/explained.html)
25. [EU Cyber Resilience Act (CRA): What It Is, Timeline and Requirements for Hardware and Software Makers](https://truvocyber.com/blog/cyber-resilience-act)
26. [Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities:](https://quantumai.google/static/site-assets/downloads/cryptocurrency-whitepaper.pdf)
27. [Google: Quantum resources required to break elliptic-curve cryptography are significantly lower than previously expecte…](https://www.techflowpost.com/en-US/newsletter/118524)
28. [NIST Releases Draft SP 800-230](https://csrc.nist.gov/News/2026/nist-releases-draft-sp-800-230)
29. [NIST Special Publication (SP) 800-230 (Draft), Additional SLH-DSA Parameter Sets for Limited Signature Use Cases](https://csrc.nist.gov/pubs/sp/800/230/ipd)
30. [Preparing for CNSA 2.0: What It Means for Your Code Signing Strategy](https://www.encryptionconsulting.com/preparing-for-cnsa-2/)
31. [LMS vs XMSS: Comparison of Stateful Hash-Based Signature Schemes on ARM Cortex-M4 - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334983/)
32. [Accelerating SLH-DSA by Two Orders of Magnitude with a Single Hash Unit](https://link.springer.com/chapter/10.1007/978-3-031-68376-3_9)
33. [Accelerating SLH-DSA by Two Orders of Magnitude with a Single Hash Unit](https://dl.acm.org/doi/10.1007/978-3-031-68376-3_9)
34. [Microchip Brings Hardware Quantum Resistance to Embedded Controllers :: Microchip Technology Incorporated (MCHP)](https://ir.microchip.com/news-events/press-releases/detail/1312/microchip-brings-hardware-quantum-resistance-to-embedded-controllers)
35. [MEC175xB Embedded Controllers](https://microchip.com/en-us/products/embedded-controllers/notebook-desktop/mec175xb)
36. [Secure Boot - OpenTitan Documentation](https://docs.opentitan.org/doc/security/specs/secure_boot/)
37. [PQC Implementations Still Leak: SCA and FI Risks in Dilithium & Kyber](https://www.keysight.com/blogs/en/tech/nwvs/2025/11/11/pqc-implementations-still-leak-sca-and-fi-risks-in-dilithium-and-kyber)
38. [adams-bridge/docs/AdamsBridgeSCA.md at main · chipsalliance/adams-bridge · GitHub](https://github.com/chipsalliance/adams-bridge/blob/main/docs/AdamsBridgeSCA.md)
39. [Why “Adams Bridge” Leaks: Attacking a PQC Root-of-Trust](https://mjos.fi/doc/20250530-hardwear-abr.pdf)
40. [© ETSI 2026. All rights reserved. Speaker’s company logo 06/18/2026](https://www.etsi.org/wp-content/uploads/S33_PQSecure_Azarderakhsh.pdf)
41. [Trusted Platform Module (TPM)](https://www.ebsco.com/research-starters/engineering/trusted-platform-module-tpm/)
42. [New computing specification implements PQC measures to protect users from quantum attacks](https://trustedcomputinggroup.org/new-computing-specification-implements-pqc-measures-to-protect-users-from-quantum-attacks/)
43. [Composite Module-Lattice-Based Digital Signature Algorithm (ML-DSA) for use in X.509 Public Key Infrastructure](https://datatracker.ietf.org/doc/html/draft-ietf-lamps-pq-composite-sigs)
44. [ML-DSA (FIPS 204): Sizes, Certificates and PQC PKI](https://duokey.com/en/resources/ml-dsa-certificates-post-quantum-pki-guide-2026)
45. [Document Search](https://datatracker.ietf.org/doc/search?name=ML-DSA&sort=&rfcs=on&activedrafts=on&by=group&group=)
46. [Securing OPC UA: Certificates, Policies and Common Misconfigurations (2026 Update)](https://shieldworkz.com/blogs/securing-opc-ua-certificates-policies-and-common-misconfigurations-2026-update)
47. [India PQC Migration Roadmap — DST Task Force & NQM Deadlines](https://kavachq.in/india-roadmap)
48. [1 Benchmarking NIST-Standardised ML-KEM and ML-DSA on ARM Cortex-M0+: Latency,](https://arxiv.org/pdf/2603.19340)
49. [AN1190: Series 2 Secure Debug](https://www.silabs.com/documents/public/application-notes/an1190-efr32-secure-debug.pdf)
50. [Secure Microcontrollers - Migrate a TRAVEO™ T2G device to the SECURE lifecycle stage - Knowledge Base Articles - Infineon Developer Community](https://community.infineon.com/t5/Knowledge-Base-Articles/Secure-Microcontrollers-Migrate-a-TRAVEO-T2G-device-to-the-SECURE-lifecycle/ta-p/333987)
51. [Hello and welcome to this presentation of the STM32 ...](https://www.st.com/content/ccc/resource/training/technical/product_training/group1/72/e7/22/68/9d/e3/43/f7/STM32L5-Security-Memories_Protections_MEMPROTECT/files/STM32L5-Security-Memories_Protections_MEMPROTECT.pdf/_jcr_content/translations/en.STM32L5-Security-Memories_Protections_MEMPROTECT.pdf)
52. [The Wretched State of OT Firmware Patching](https://blog.adolus.com/the-wretched-state-of-ot-firmware-patching)
53. [Partial NTT Masking in PQC Hardware: A Security Margin Analysis](https://arxiv.org/pdf/2604.03813)
54. [BSI - Cyber Resilience Act](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Cyber_Resilience_Act/cyber_resilience_act_node.html)
55. [India’s Task Force Releases Quantum‑Safe Roadmap with 2027–2029 Migration Timeline for CII](https://postquantum.com/security-pqc/indias-quantum-safe-roadmap/)
56. [The Real Cost of a Truck Roll](https://www.sandc.com/en/gridtalk/2017/march/20/the-real-cost-of-a-truck-roll)
57. [ABB survey reveals unplanned downtime costs \$125,000 per hour](https://new.abb.com/news/detail/107660/abb-survey-reveals-unplanned-downtime-costs-125-000-per-hour)
58. [OPC UA Security: A Practical Guide for OT Engineers](https://www.trout.software/resources/securing-opc-ua)
59. [Google Just Made Quantum Computing's Threat to Encryption 20x Worse](https://lockeidentity.com/blog/cybersecurity/google-quantum-encryption-2029/)
60. [RDP, WRP, PCROP and HDP on STM32](https://www.openstm32.org/article3-RDP-WRP-PCROP-and-HDP-on-STM32)
61. [Authenticated Debug Access Control 1.0 Architecture & Technology Group](https://documentation-service.arm.com/static/628bad10e3c4322a76af60ef)
62. [Blog - Hybrid Post-Quantum Certificates: Why Your First PQC Migrati...](https://evertrust.io/blog/hybrid-post-quantum-certificates/)
63. [Machine-Checked Cardinality Bounds for Masked Barrett Reduction: A 1-Bit Side-Channel Leakage Barrier in Post-Quantum Cryptographic Hardware](https://arxiv.org/pdf/2604.24670)
64. [Reduce Truck Roll Costs Using Remote Assist Software - Help Lightning](https://helplightning.com/blog/reduce-truck-roll-costs/)
65. [Cyber Resilience Act: duties and deadlines for manufacturers](https://oswald.technology/en/insights/cyber-resilience-act/)

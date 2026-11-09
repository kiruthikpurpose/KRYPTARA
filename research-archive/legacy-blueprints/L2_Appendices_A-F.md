# Appendices A–F: the full stream memos

Unedited working memos from the six design streams, concatenated. The master blueprint prevails where they disagree. Appendix order: A requirements, B architecture, C cryptography, D embedded, E fleet and protocols, F open-source landscape.


---

<!-- Appendix A -->
# APPENDIX A

# Stream R: Requirements Baseline and Traceability

Principal requirements/systems engineering memo. Source: *OT-Embedded-PQC-Atlas-2nd-Edition.md* (Parts 3, 4, 8, 10.3, 11, 12, 13, 17.2, 18, 19; Part 6.6 for counters). Evidence labels follow the BRIEF: [F] fact, [D] measured in a paper, [C] computed here, [E] estimate with arithmetic, [I] inference, [H] hypothesis.

All numbers in requirements are derived from atlas figures, with the arithmetic shown in R.4.0. No new external source was introduced; where a requirement cites an external regime (CRA, IR 8547, CNSA 2.0, IEC 61508, IEC 62443) it does so only as the atlas does, and no clause numbers are asserted.

## R.0 How to read this baseline

- **IDs.** `UC-nn` use cases, `SP-nn` security properties, `FR-<area>-nn` functional requirements, `NFR-<kind>-nn` non-functional requirements, `ADV-x` adversary classes, `CA-x` capability areas, `RD-n` requirement-level decisions, `M0..M5` milestones.
- **Verification codes.** T test, A analysis, P formal proof/model check, I inspection, D demonstration (exercise on a rig or tabletop).
- **Priority.** MUST (baseline cannot be called complete without it), SHOULD (expected unless a recorded waiver), MAY (hook or option; supports research strands).
- **Milestones (suggestion, [H]).**

| MS | Name | Content |
|---|---|---|
| M0 | Foundations | Formats and registry rules, assumption table, policy compiler, surface-map schema, counter audit, claims register, reproducible models |
| M1 | Continuity core | MV-1 first stage, verifier library, floor and journal, host harness, minimal quorum signing, power-cut harness |
| M2 | Authority closure | Lifecycle and side-door closure, PQ vouchers, symmetric fabric, provisioning, catch-up, enrolment, state reports |
| M3 | Fleet operations | Staging and orchestration, evidence and CBOM, enclave profile, planning, drills, protocol profiles |
| M4 | High assurance | HA-1 verification, dual implementations, conformance suite, certification evidence, independent review |
| M5 | Long horizon | Research hooks (future-key custody, ENF/remanence inputs, ratchets, insurer export) |

## R.0.1 Requirement-level decisions

Decisions that shape the baseline are recorded here once; individual requirements cite them.

**RD-1. Devices verify; hosts sign.**
- DECISION: Device builds contain no signing code (FR-CRY-04, FR-SIG-01); signing runs in HSM-backed host services.
- WHY: Verification is cheap and deterministic (ML-DSA-44 verify 44.0 ms vs ECDSA P-256 321 ms on RP2040 [D]); signing has a long tail (mean 158.9 ms, p99 584.2 ms [D]) and is a key-extraction risk on exposed devices (atlas 2.6).
- ALTERNATIVES REJECTED: on-device ML-DSA signing on controllers (p99 584 ms against a ~100 ms deadline is 5.8x over [C]; side-channel exposure per atlas 2.6).
- ASSUMPTIONS: Report signing, where required, uses a scheme whose signing cost fits the device (atlas allows C2+ signed reports; mechanism unspecified).
- TRADE-OFFS: C0/C1 cannot report themselves; passive inference or gateway witness is weaker (FR-EVD-05).
- LIMITS: A device that must sign (state reports) reintroduces a signing path; FR-EVD-01 therefore says "devices capable of signing".
- VALIDATION: E-A2 benchmarks, E10 timing study.

**RD-2. Single-assumption safety is stated as a hitting-set condition, not as "two families".**
- DECISION: SP-01 is `for every assumption a, no accepted quorum is contained in {k : a in A(k)}`; checked by FR-AUT-03.
- WHY: The atlas's prose form ("pairwise disjoint in at least two members", 10.3) is a sufficient special case; the hitting-set form also handles keys with several assumptions (ECDSA depends on {ECDLP, SHA-2}) and extends to organisation and implementation as assumptions (E-N3 lists hash, lattice, code, implementation, organisation). [I, restatement; the 19x figure is from atlas M2 [C] and is not re-derived here]
- ALTERNATIVES REJECTED: plain k-of-n over distinct algorithm names (fails with one Keccak failure, correction #21); counting algorithms instead of assumptions (correction #22).
- ASSUMPTIONS: A(.) is correct; SHA-2 vs SHA-3 independence is a judgement and is declared in the table, not hidden (atlas residual caveat).
- TRADE-OFFS: roughly half a percentage point of honest availability in the atlas model [C].
- LIMITS: Independence of SHA-2 and SHA-3 may be discounted by reviewers; the table makes that explicit and k>1 analysis is available.
- VALIDATION: E-B2 (TLA+/Tamarin), E-N3 (checker finds shared assumptions).

**RD-3. Time may tighten, never grant.**
- DECISION: SP-08, FR-TIM-01/04; authority uses counters and coarse epochs.
- WHY: Offline devices have no trustworthy clock; cheap crystals drift ~10.5 min per year at 20 ppm (20e-6 x 31,557,600 s = 631 s [C]); governed grid clocks deviated by minutes in 2018 (atlas N59).
- ALTERNATIVES REJECTED: calendar-validity certificates (P27 cliff); a time-free-validity product (demoted to research in the atlas).
- ASSUMPTIONS: Epochs of at least one month absorb a 10-year drift of about 105 min [C].
- TRADE-OFFS: coarser expiry semantics than operators may expect.
- LIMITS: freeze attacks are undetectable (limit 3.4#1); only bounded.
- VALIDATION: E3 offline simulation, E-N2.

**RD-4. First-stage resource budgets.**
- DECISION: NFR-MEM-01 caps MV-1 at 16,384 B flash and 2,048 B stack; NFR-LAT-01 caps LMS-W4 verify at 60 ms @64 MHz.
- WHY: demonstrated LMS verifier plus library is 12,864 B; 16,384 / 12,864 = 1.27x headroom [C]. LMS verify stack was measured at 1,044 B (Campos) and 1,580 B (nRF52840) [D]; 2,048 / 1,580 = 1.30x [C]. W4 verify is 2,658,884 cycles / 64 MHz = 41.5 ms [E]; 60 / 41.5 = 1.44x margin.
- ALTERNATIVES REJECTED: no explicit budget (invites creep, violates germline minimalism); tighter 13 KB cap (leaves no room for the journal and self-check).
- ASSUMPTIONS: budgets are for the MV-1 profile; HA-1 (two hash waists, state machine) may exceed them and SHALL publish its own budget.
- TRADE-OFFS: a budget may exclude a hardware port with a poor compiler.
- LIMITS: figures are atlas-derived, not remeasured here. E-A2 must confirm.
- VALIDATION: CI size gates (FR-CRY-12), E-A2.

**RD-5. Status taxonomy for the traceability matrix.** Four statuses plus one honesty status, used in R.5: COVERED, PARTIAL, OUT_OF_SCOPE, RESEARCH, UNITEMISED (atlas never itemises the problem). "COVERED" means software requirements address the problem and the residual is implementation and validation risk only; "PARTIAL" means software mitigates but the residual needs silicon, policy, contract or physics, named in the row.


# R.1 Stakeholder and actor model

## R.1.1 Stakeholders

Drawn from atlas 14.1 (who experiences, owns, controls, pays, implements, maintains, blocks). The central coordination failure is that the party with technical control (OEM) is not the party with long-term risk (operator) [I].

| ID | Stakeholder | Interest | Controls | Key needs from the baseline | Main use cases |
|---|---|---|---|---|---|
| SH-1 | Device maker (OEM) | Ship devices that survive 25-40 years, meet CRA | Firmware, release keys, algorithm choice | Small verifier, portable library, certification artefacts, no forced recertification for crypto change | UC-01,03,06,07,08,12 |
| SH-2 | Silicon vendor | Sell parts; avoid ROM respins | Lock semantics, ROM, hash engines, lifecycle fuses | A profile that works on lockable parts today; documented hardware-evidence form | UC-01,36 |
| SH-3 | Contract manufacturer | Efficient line | Factory key injection, provisioning line | Simple injection protocol, no fleet secrets, co-signed log | UC-02 |
| SH-4 | System integrator | Commission and hand over | Configuration, workstations, zone design | Surface maps, quorum workflow, handover evidence | UC-13,14,21 |
| SH-5 | Operator / asset owner | Availability first, then security | Windows, budget, ownership post-support | Staged transitions, evidence, exit from OEM, dated enclaves | UC-06,09,13,15,25 |
| SH-6 | Regulator / standards body | Demonstrable posture, deadlines | Regime definitions of "done" | Evidence mapped to regime; exposure-years | UC-25,26 |
| SH-7 | Auditor / assessor (security and functional safety) | Verify claims | Acceptance of crypto confinement | Conformance suite, traceability, safety-case artefacts | UC-26,30 |
| SH-8 | HSM / key custodian | Protect signing keys | Quorum signing, stateful state | Index reservation, portability path | UC-31,32 |
| SH-9 | Escrow agent and witnesses | Neutral custody | Voucher files, heartbeat evidence | Reference verifier, witnessed publication | UC-09,11,30 |
| SH-10 | Maintainer community / foundation | Keep the project alive for decades | Releases, registries | Governance independent of any vendor | all |
| SH-11 | Insurer, broker, spare-parts reseller | Price risk, resell hardware | Indirect | Receipts, posture export | UC-19 |
| SH-12 | Field technician | Execute visits | Presence token, catch-up | Simple offline procedures | UC-15,16 |

## R.1.2 Adversary classes

The atlas's two adversaries of the lock (Part 8.1) are extended with the classes the problem tables imply. Each security property in R.3 names the classes it assumes.

| ID | Class | Capability assumed | Does NOT assume | Atlas anchors |
|---|---|---|---|---|
| ADV-R | Remote fleet-scale forger | Forges classical signatures once a CRQC exists; pushes forged artefacts to many devices; cannot rewrite write-locked flash by signature | Physical access | R1, N1-N6, Part 8.1 |
| ADV-H | Harvest-now passive recorder | Records key-delivery sessions and signed artefacts today; decrypts/forges later | Active interference today | N9, 2.1 |
| ADV-L | Local physical attacker | Holds one device (stolen spare, returned board, field unit); may defeat protections on some part families | Fleet-wide secrets being present on that device (design goal) | N21, N70, Part 8 |
| ADV-I | Insider | One OEM employee, CM operator, integrator engineer or operator staff with legitimate access; a full quorum colluding is possible but must be detected (limit 3.4#3) | Unlimited collusion prevented | N18, N47, N8 |
| ADV-S | Supply-chain adversary | Contract manufacturer, distributor, refurbisher, spares broker, toolchain/compiler, dependency | Control of the HSM quorum | N8, N36, N53, N71 |
| ADV-C | Cryptanalytic surprise | One mathematical assumption or one implementation fails suddenly (SIKE, Rainbow, KyberSlash, Clangover class) | More than k simultaneous failures (k parameterised, default 1) | 2.6, N58, N71 |
| ADV-W | Active network adversary | Withholds, replays, reorders or freezes updates; steers negotiation | Breaking symmetric primitives | N44, 3.4#1 |
| ADV-T | Time manipulator | Spoofs or biases individual time sources | Spoofing all independent cues | N42, N59 |
| ADV-A | Automation bypass | Uses an automated or AI agent holding tokens to satisfy approvals | Compromise of human token custody | N47 |
| ADV-F | Non-malicious failure | OEM exit, bankruptcy, M&A, operator error, defective update, 3G-type infrastructure sunset, counter wrap | Intent | N41, N62, N63, N56, N67 |

## R.1.3 Actors (as used in use cases)

| Actor | Class | Notes |
|---|---|---|
| Device | C0-C3 | C0 inert, C1 symmetric-only, C2 verify-capable controller, C3 safety-critical |
| Gateway / KDC / workstation / historian | C4 | Concentrators; must not become single points of fleet trust |
| Signing authority (HSM, voucher holder, debug issuer) | C5 | Multi-class quorum; offline or witnessed transfer |
| Orchestrator, planner, evidence service | Host tooling | Not an app or dashboard: libraries and services that integrators embed |

Class definitions and the five anti-weak-path invariants are from atlas 12.1-12.2; SP-23 states them as a property.


# R.2 Use cases

Scenario letters refer to atlas Part 13 (A new device, B old device, C mixed-vendor facility, D long-disconnected, E OEM disappears, F emergency event, G planned fleet transition). Each use case lists the requirements that realise it; success criteria are observable.

| ID | Title | Actors | Precondition | Flow | Success criteria | Atlas tie | Requirements |
|---|---|---|---|---|---|---|---|
| UC-01 | Design a new device with a continuity first stage | Device maker, silicon vendor | MCU with lockable flash and SHA engine selected; surface map started | 1 Fill surface map and hardware-evidence entry. 2 Choose profile (MV-1/HA-1). 3 Compile policy; compiler proves single-assumption safety. 4 Build first stage and second stage. 5 Run power-cut and conformance suites. | Signed build with passing proof, test and CBOM entries | Scenario A; I-1, I-4 | FR-LC-01,FR-LC-02,FR-AUT-03,FR-FS-01,FR-FS-02,FR-FS-15,FR-ASR-03,FR-EVD-03 |
| UC-02 | Factory provisioning at a contract manufacturer | Contract manufacturer, device maker | Per-device keys generated in OEM HSM; line has KEM-capable fixture | 1 Device UUID read. 2 KEM-wrapped key injected. 3 Slot hashes and floor=0 burned, lock enabled. 4 CM and OEM co-sign provisioning log. | No fleet secret on line; log verifiable; lock attested | Scenario A; N8, N10 | FR-LC-07,FR-FS-02,FR-FS-03,FR-CRY-17,FR-KEY-02 |
| UC-03 | Boot with a valid release | Device | Device provisioned; image signed in one valid class | 1 Reset. 2 First stage verifies second stage vs slot hashes. 3 Floor check. 4 Run. | Boot completes offline without time within latency budget | Scenario A; P8, R1 | FR-FS-01,FR-FS-11,NFR-LAT-01,NFR-OFF-01 |
| UC-04 | Boot failure degrades stepwise to last-known-good | Device, operator | Image A corrupted and image B invalid | 1 A fails. 2 B fails. 3 LKG boots and keeps process running. 4 State report flags degraded mode. | Control function continues; no brick | Part 5 law 8; P30 | FR-FS-06,FR-UPD-17,NFR-SAFE-01,FR-EVD-01 |
| UC-05 | Power cut during floor advance | Device | Quorum-signed floor advance in progress | 1 Journal commit. 2 Power lost between commit and burn. 3 Reboot replays journal. | Post- or pre-state; bootable; floor never decreased | Part 11.1 invariants (b),(c); N22 | FR-FS-05,FR-FS-07,FR-ASR-03,FR-FS-10 |
| UC-06 | Planned fleet-wide algorithm transition (molting) | Operator, device maker, integrator | Inventory and policy exist; bundles signed in both classes | 1 Rehearse on replica. 2 Canary site. 3 Stage dormant. 4 Activate over one/two window cycles. 5 Shadow-sign for >=1 cycle. 6 Shed old class by disjoint quorum. 7 Harden. 8 Collect state reports. | Completion evidenced by reports; exposure-years reduced | Scenario G; N13, N14, I-16 | FR-AUT-09,FR-UPD-01,FR-UPD-02,FR-UPD-06,FR-UPD-13,FR-UPD-10,FR-EVD-01,FR-EVD-08,FR-SIG-02 |
| UC-07 | Emergency response to a lattice break or class compromise | Operator, device maker, HSM operators | One class declared suspected or broken | 1 Declare suspected state. 2 Sign floor advance with surviving class under disjoint quorum. 3 Stage bundle. 4 Activate in next/emergency window with persister fraction. 5 Collect reports; halt on adverse signals. | Attacker with the failed class cannot advance authority; no fleet-wide outage | Scenario F; N62, I-33 | FR-CRY-15,FR-AUT-06,FR-UPD-06,FR-UPD-07,FR-EVD-01,FR-SIG-02 |
| UC-08 | Annual slot drill | Operator, device maker | Alternate class not yet exercised in the current cycle | 1 Choose drill class. 2 Sign release in alternate class only. 3 Verify in a window. 4 Report result. | Alternate path proved before emergency | Part 11.1; N57, I-13 | FR-UPD-15,FR-EVD-01,FR-SIG-02 |
| UC-09 | OEM disappears and operator re-owns fleet (with slot 3) | Operator, escrow agent, witnesses | Slot 3 provisioned; heartbeat history; voucher escrow | 1 Heartbeat missed N times. 2 Witnessed trigger evaluation. 3 Escrow release of vouchers. 4 REPLACE_SLOT3 via floor rule. 5 Operator signs images. | Operator authority without OEM; no device replaced | Scenario E; P23, N7, I-17 | FR-OWN-03,FR-OWN-04,FR-OWN-02,FR-FS-13,FR-AUT-10 |
| UC-10 | OEM disappears with no slot 3 | Operator | Fleet shipped without slot 3 | 1 Inventory flags queenless. 2 Cost report produced. 3 Enclave plus replacement plan. | Honest outcome: no cryptographic path; containment and replacement dated | Scenario E; Part 11.4 | FR-OWN-09,FR-FS-13,FR-ENC-01,FR-ENC-09 |
| UC-11 | Competing successors | Operator, OEM acquirer, escrow claimant | Two valid-looking claims | 1 Signed objections attached. 2 Irreversible steps held. 3 Hold bound reached; escalate. 4 Deterministic tie-break. | No split fleet | Scenario E; N67, I-18 | FR-AUT-10,FR-OWN-06 |
| UC-12 | Supersedure before CRA end | OEM, operator | OEM still operating; support ending | 1 OEM signs transfer to slot 3. 2 Voucher chain updated. 3 Heartbeat obligations handed over. | Planned hand-over | Part 11.4; N29, N49 | FR-OWN-05,FR-FS-13,FR-OWN-01 |
| UC-13 | Retrofit an old device that cannot be modified | Operator, integrator | C0/C1 device, no update path | 1 Inventory and classify. 2 Segment. 3 PQ gateway. 4 Disable remote firmware paths. 5 Sign exit epoch and replacement date. | Link protected; exit measurable | Scenario B; N30, I-9 | FR-ENC-01,FR-ENC-02,FR-ENC-07,FR-ENC-09,FR-MIG-01,FR-MIG-06 |
| UC-14 | Mixed-vendor facility authority audit | Integrator, operator | Multiple vendors on site | 1 Collect surface maps per vendor. 2 Assign classes. 3 Compute exposure. 4 Place zone boundaries at C4. 5 Produce CBOM. 6 Enable workstation quorum. | All six chains classified; residual classical list | Scenario C; R9, N69 | FR-LC-01,FR-MIG-01,FR-MIG-04,FR-EVD-03,FR-SIG-06,FR-ENC-07 |
| UC-15 | Long-disconnected installation maintenance visit | Technician, operator | Device offline for years | 1 Technician token verified. 2 Catch-up bundle applied. 3 Epoch entrainment. 4 State report. | Device reaches current floor; staleness never stopped safety function | Scenario D; P22, N40 | FR-LC-14,FR-TIM-12,FR-TIM-05,FR-TIM-04,NFR-OFF-02 |
| UC-16 | Spare activation at installation | Integrator, operator | Spare on shelf with only first stage | 1 Voucher presented. 2 Current bundle applied. 3 Identity issued. | Spare never held stale authority | P24, N23, N53, I-5 | FR-LC-13,FR-LC-14,FR-OWN-01 |
| UC-17 | Debug during commissioning, closed in field | Device maker, integrator | TEST state | 1 UUID-bound PQ debug credential issued by separate issuer. 2 Debug used. 3 PROD commissioning disables debug. 4 State report confirms. | Field debug closed fleet-wide | N1, N2; Part 11.2 | FR-LC-03,FR-LC-04,FR-SIG-12,FR-EVD-01 |
| UC-18 | RMA by board swap | Operator, device maker | Faulty device | 1 Device returned. 2 Decommission receipt signed. 3 Replacement shipped with fresh identity. | No debug reopened | N3, N4 | FR-LC-05,FR-LC-11,FR-LC-12 |
| UC-19 | Decommission and resale of equipment | Operator, broker | Device end of life | 1 Keys destroyed. 2 Signed receipt logged. 3 Trust lists updated. 4 Buyer verifies receipt before commissioning. | No stale identity carried | N36, N37, N53, I-6 | FR-LC-11,FR-LC-15,FR-LC-12 |
| UC-20 | Facility sale or split (swarming) | Seller, buyer, escrow | Sub-fleet defined | 1 Authority-holdings report. 2 Swarm voucher transfers sub-fleet. 3 Witnessed log. | Authority transferred without orphaning | N52 | FR-OWN-06,FR-OWN-07,FR-OWN-08 |
| UC-21 | Settings and safety-logic change through workstation quorum | Engineer, reviewer, relay | Quorum tokens issued | 1 Engineer signs settings. 2 Reviewer co-signs. 3 Relay or gateway verifies. | Single compromised workstation cannot alter protection | N17, N18, N47 | FR-SIG-06,FR-AUT-14,FR-ENC-05,FR-AUT-11 |
| UC-22 | AI assistant proposes configuration | Engineer, AI assistant | Assistant integrated in engineering tool | 1 Assistant drafts change. 2 Human-attributable signature required. 3 Quorum evaluated. | Automation cannot satisfy quorum alone | N47 | FR-AUT-14,FR-SIG-06 |
| UC-23 | Process-bus enrolment and rekey | Commissioning engineer, KDC | IED with ML-KEM capability | 1 KEM decapsulation once. 2 Per-device KEK derived. 3 Group keys delivered via GDOI-like epoch. 4 MACs unchanged. | Data path unchanged; no fleet key | P19, P20; Part 11.3 | FR-CRY-17,FR-KEY-01,FR-KEY-02,FR-KEY-04,NFR-LAT-05 |
| UC-24 | KDC compromise containment | Security operator | KDC zone breach suspected | 1 Scope limited by zone. 2 Rotate KEKs from HSM. 3 Re-enrol affected zone only. | Blast radius = one zone | N43, N10 | FR-KEY-03,FR-KEY-02,FR-KEY-07,FR-KEY-08 |
| UC-25 | Fleet crypto-state evidence for a regulator | Operator, auditor, regulator | Devices report; passive taps | 1 Collect state reports. 2 Infer silent devices. 3 Generate CBOM. 4 Map to regime. 5 Compute exposure-years. | Auditor can verify evidence | Part 11.7; P32-P35, N31 | FR-EVD-01,FR-EVD-03,FR-EVD-05,FR-EVD-08,FR-EVD-09 |
| UC-26 | Verify OEM PQ claim before purchase | Operator, auditor | Procurement stage | 1 Request conformance report. 2 Run public suite. 3 Check hardware evidence register. | Claim verified or refuted | N32, I-10 | FR-EVD-15,FR-ASR-02,FR-LC-02,FR-MIG-07 |
| UC-27 | Inventory-less migration (acquaintance rule) | Operator | No trust inventory | 1 Sample devices. 2 Select a peer each trusts or talks to. 3 Migrate that peer. 4 Iterate. | Hubs reached with partial knowledge | I-20; Part 12.4 | FR-MIG-03,FR-MIG-02 |
| UC-28 | Ordered migration by class | Operator | Inventory complete | 1 Rank C5 then C4 then C3-C1. 2 Compute blast radius per step. 3 Execute with spindle gating. | Worst-case blast radius falls fast | Scenario G; M1 | FR-MIG-03,FR-UPD-08,FR-UPD-09 |
| UC-29 | Irreversible classical sunset with stragglers | Operator | Readiness reports collected | 1 Gate on all dependents ready. 2 Bounded hold. 3 Escalate. 4 Sunset. 5 Straggler registry routes residuals. | No silent cliff | N72, N64, I-27 | FR-UPD-08,FR-UPD-09,FR-ENC-02 |
| UC-30 | Voucher audit in 2055 | Auditor, court | Evidence archived since 2027 | 1 Fetch evidence record. 2 Renewal chain verified. 3 Reference verifier run. | Voucher provable decades later | N60, I-29 | FR-EVD-10,FR-EVD-14,FR-OWN-02,FR-GOV-03 |
| UC-31 | Release signing with LMS state | Release engineer, HSM | Key with 2^10 leaves | 1 Reserve index. 2 Sign. 3 Persist atomically. 4 Budget alert. | No index reuse across failover | P3, N51 | FR-SIG-03,FR-SIG-04,FR-SIG-01,FR-SIG-11 |
| UC-32 | HSM vendor migration | Key custodian | Vendor end-of-life | 1 Attested export if allowed else re-root via molting. 2 Ceremony record. | State not cloned | N51 | FR-SIG-05,FR-AUT-09,FR-SIG-07 |
| UC-33 | Counter-wrap audit before release | Device maker | Candidate design | 1 Fill counter register. 2 Tool checks 2x margin. 3 Fail build if not. | No counter runs out within life | N56 | FR-TIM-06,FR-TIM-07,NFR-FLASH-02 |
| UC-34 | Floor-burn attack attempt | Attacker, device | Attacker holds valid high-index image | 1 Presents image. 2 Floor rule requires different-slot quorum. 3 Rejected, anergy recorded. | Owner not locked out | N22 | FR-AUT-06,FR-AUT-08,FR-AUT-05 |
| UC-35 | Forged revocation to brick fleet | Attacker | Attacker can forge a classical revocation | 1 Revocation targets live authority. 2 Structurally invalid. | Fleet not bricked | Part 11.2 PAM rule | FR-AUT-07,FR-AUT-05 |
| UC-36 | Opened device does not yield fleet authority | Local attacker | Stolen device | 1 Device opened. 2 Only public hashes and its own keys recoverable. 3 Other devices unaffected. | Blast radius = 1 device | Part 8.3; N70, N21 | FR-FS-04,FR-KEY-02,FR-LC-03,FR-LC-02 |
| UC-37 | Policy testing before signing | Policy author | Draft policy | 1 Compile. 2 Replay planned operations. 3 Reject if any legitimate op refused. | Policy that blocks owner is never shipped | I-22; N66 | FR-AUT-03,FR-AUT-12,FR-AUT-04 |
| UC-38 | Jurisdiction-constrained operation | Operator in restricted jurisdiction | Remote operation limited by law | 1 Remote paths disabled. 2 Local quorum workflow used. 3 Audit trail kept. | Compliance with remote-ops constraint | N65 | FR-ENC-08,FR-LC-10 |
| UC-39 | Downgrade attempt | Network attacker | Peer negotiation | 1 Attacker steers to weaker group. 2 Policy minimum refuses. 3 Event logged. | No silent downgrade | N44, N45 | FR-CRY-14,FR-CRY-13,FR-AUT-13 |
| UC-40 | Unpatchable device with no vendor fix | Operator | Advisory without patch | 1 Compensating-control bundle. 2 Exit epoch signed. 3 Reported. | Mitigated and dated | N15 | FR-UPD-12,FR-ENC-02 |
| UC-41 | Window-aligned dormant activation | Operator, plant | Bundle staged | 1 Presence token plus signature. 2 Randomised offset. 3 Report countersigned. | Change lands in planned window | N14, N33, I-3 | FR-UPD-02,FR-UPD-03,FR-UPD-04,FR-UPD-10 |

# R.3 Security properties

Adversary classes are defined in R.1.2. Each property is stated so that it can be checked (proof, model check, test or inspection).

| ID | Name | Statement | Adversary model | Realised by | Validation |
|---|---|---|---|---|---|
| SP-01 | Single-assumption authority safety | Let A(k) be the assumption set of key k and P the family of accepted quorums. For every assumption a, no Q in P SHALL be a subset of {k : a in A(k)}; equivalently every accepted quorum contains, for each a, at least one key not depending on a. Applies to floor advance, slot replace, lifecycle, ownership, live-authority revocation, escrow release. Generalised to any k simultaneous failures by parameter. | ADV-C (one assumption fails, incl. hash, lattice, implementation, organisation) and ADV-R | FR-AUT-02,FR-AUT-03,FR-FS-12 | Hitting-set enumeration; TLA+ invariant; counterexample corpus (e.g. {ML-DSA, SLH-DSA-SHAKE} must fail) |
| SP-02 | Floor monotonicity and floor-burn resistance | The floor value SHALL never decrease; it SHALL advance only by a quorum including a signature from a slot other than the retired slot; a holder of a single valid higher-index image SHALL NOT be able to advance it. | ADV-R, ADV-I (holder of one key), ADV-L | FR-AUT-06,FR-FS-05,FR-UPD-14 | Proof (invariant c); lab test E-B4 |
| SP-03 | Power-cut safety | For any prefix of any state transition interrupted by power loss, the post-reboot state SHALL equal the pre- or post-state and a verified image SHALL boot. | Non-malicious plus ADV-L (power glitching only as environmental fault, not technique) | FR-FS-07,FR-FS-05,FR-UPD-17 | Proof (invariant b); 100,000 randomised cuts (E1) |
| SP-04 | Fleet blast-radius bound | Compromise of one device SHALL yield no secret usable to authorise or authenticate any other device; for a C4 node the exposed set SHALL be bounded by its declared zone; first stage holds only public hashes. | ADV-L, ADV-I | FR-FS-04,FR-KEY-02,FR-KEY-03,FR-KEY-07,FR-LC-03,FR-ENC-03 | Architecture review (E-A4 revised); secret-inventory inspection; KDF context tests |
| SP-05 | Boot versus re-authorise separation | Booting SHALL require one valid class; any authority change SHALL require a disjoint-quorum; re-ownership SHALL additionally require presence evidence. | ADV-R | FR-AUT-05,FR-LC-16 | Proof; negative tests per action type |
| SP-06 | Revocation cannot target live authority | A revocation whose target set intersects the current authority set SHALL be rejected unless escrow class plus presence evidence are present. | ADV-R (forged revocation as denial of service) | FR-AUT-07 | Proof; fuzzing of revocation records |
| SP-07 | Evidence verifiability horizon | A stored evidence record SHALL remain verifiable for H years (declared; default asset life plus 10 years) provided renewal occurs at least once before each algorithm's declared validity end minus margin, without the issuer's existence and with an archived reference verifier. | Time (algorithm decay), ADV-C, institutional failure | FR-EVD-10,FR-EVD-14,FR-OWN-02,FR-GOV-03 | Renewal rehearsal; verify oldest archive with newest verifier annually |
| SP-08 | Staleness never grants authority nor stops safety | Elapsed time or staleness SHALL only reduce privileges (senescence); it SHALL never grant authority and never inhibit a safety function. | ADV-T (clock manipulator), ADV-W (freeze) | FR-TIM-04,FR-TIM-05,FR-TIM-01 | Proof; E3 offline simulation |
| SP-09 | No single time source decides | No security decision SHALL depend on a single time cue; calendar time SHALL not be a root of authority. | ADV-T | FR-TIM-03,FR-TIM-08,FR-TIM-09 | Fusion-window tests with single-source spoofing |
| SP-10 | Fail operational | A security mechanism fault, misfire or autoimmune rejection on a C3 device SHALL leave the control function running on LKG. | Non-malicious, ADV-R as trigger of misfire | FR-FS-06,NFR-SAFE-01,FR-UPD-17 | Fault-tolerance analysis; fault-injection of verifier outcomes |
| SP-11 | Non-restorable security state | No backup, restore, re-flash or clone path SHALL decrease the floor or reuse a one-time index; a deliberate reset SHALL need the strongest authority, presence and an indelible record. | ADV-I, ADV-L, operational error | FR-FS-05,FR-SIG-03,FR-AUT-05 | Model check; restore-attack tests |
| SP-12 | One-time key uniqueness | No stateful signing index SHALL be used for two messages, including across HSM failover. | ADV-I (cloning), operational error | FR-SIG-03,FR-SIG-04 | Failover chaos tests; proof of persistence protocol |
| SP-13 | Downgrade resistance | A negotiated or configured algorithm policy SHALL never fall below the signed minimum; agility changes are authority actions. | ADV-R, ADV-W | FR-CRY-14,FR-AUT-13,FR-CRY-13 | Negotiation fuzzing; downgrade test vectors |
| SP-14 | Debug and lifecycle closure | No path SHALL open general debug on a PROD device without disjoint quorum, presence and per-device binding; reverse transitions SHALL never reopen general debug. | ADV-R, ADV-I, ADV-S | FR-LC-03,FR-LC-04,FR-LC-05,FR-LC-06 | Lifecycle model check; credential-binding negative tests |
| SP-15 | Provisioning integrity | No secret shared across devices SHALL exist at any provisioning step; every injection SHALL be logged with CM and OEM co-signatures. | ADV-S, ADV-I | FR-LC-07,FR-KEY-02 | Provisioning audit; log verification |
| SP-16 | Rollout safety | No fleet-wide simultaneous activation SHALL occur; activation SHALL halt automatically on adverse signals; a persister fraction SHALL remain on LKG during emergencies. | Non-malicious (defective update), ADV-R (malicious bundle) | FR-UPD-06,FR-UPD-07,FR-UPD-08 | Orchestrator simulation with injected defects |
| SP-17 | Succession safety | No irreversible succession step SHALL execute while a valid objection stands; hold SHALL be bounded; tie-break SHALL be deterministic; escrow release SHALL be witnessed. | ADV-I (stalling), organisational failure, ADV-R | FR-AUT-10,FR-OWN-04 | Model check; stall-attack scenarios |
| SP-18 | Authority-change auditability | Every authority action SHALL leave a signed, ordered record bound to device state; collusion by a full quorum SHALL be detectable afterwards and bounded by scope and rate. | ADV-I (collusion) | FR-AUT-11,FR-EVD-01,FR-EVD-07,FR-EVD-12 | Audit replay; log tamper tests |
| SP-19 | HNDL-resistant key delivery | No long-term symmetric key or firmware-encryption key SHALL be delivered protected only by classical public-key exchange. | ADV-H (harvest now), ADV-R | FR-CRY-17,FR-CRY-18,FR-KEY-10 | Protocol inspection; capture-replay test |
| SP-20 | Verifier implementation diversity | Two independent verifier implementations SHALL agree on every test vector and fuzz input; disagreement SHALL fail the release. | ADV-C (implementation break), ADV-S (toolchain) | FR-FS-09,FR-CRY-11,FR-CRY-06 | Differential testing; binary-level constant-time checks |
| SP-21 | Locked-stage integrity | After lock, no software path (including updates and lifecycle transitions) SHALL rewrite the first stage. | ADV-R | FR-FS-03,FR-FS-10 | Inspection; model check; lock-status attestation |
| SP-22 | Exercised-path liveness | Each declared authority path (alternate class, slot 3, voucher chain, escrow release) SHALL have been exercised successfully within its declared drill interval or SHALL be flagged. | Decay (R10) | FR-UPD-15,FR-UPD-16,FR-EVD-01 | Drill pilot E-N1; flags in report |
| SP-23 | Anti-weak-path invariants | No lower class SHALL hold authority over a higher class; below C4 every symmetric key SHALL be unique per device; C0/C1 SHALL sit inside C4 boundaries; C5 keys SHALL not be online-reachable from C4 networks; promotion only by replacement or quorum. | ADV-I, ADV-R | FR-AUT-15,FR-ENC-07,FR-KEY-07 | Policy compiler checks; network model check |
| SP-24 | Automation cannot satisfy a quorum | No quorum SHALL be satisfiable solely by automated or AI-initiated signatures. | ADV-A (automation bypass) | FR-AUT-14,FR-SIG-06 | Negative tests; attribution audit |
| SP-25 | Safety separated from cryptography | Safety-function code and its timing SHALL not depend on cryptographic internals; replacing the crypto component SHALL not change the safety-function binary or WCET. | Non-malicious | FR-KEY-06,FR-UPD-05,NFR-DET-02 | Interface inspection; WCET before/after |
| SP-26 | Counter budget adequacy | Every counter, time field and signature budget SHALL have capacity at least twice (asset life times consumption rate). | Time | FR-TIM-07,FR-SIG-04,NFR-FLASH-02 | Build-time capacity check (E-N7) |
| SP-27 | Decommission completeness | A decommissioned device SHALL not be reprovisionable or resaleable before a signed receipt is logged and trust-list removal propagated. | ADV-S (refurbisher/broker) | FR-LC-11,FR-LC-12,FR-LC-15 | Process audit; receipt-gate tests |

# R.4 Functional and non-functional requirements

## R.4.0 Derivation of numeric requirements [C/E]

| Quantity | Arithmetic | Result | Used by |
|---|---|---|---|
| LMS-W4 verify, software, 64 MHz | 2,658,884 cycles / 64e6 | 41.5 ms (Campos et al. cycles [D]) | NFR-LAT-01 (budget 60 ms = 1.44x) |
| Image hashing 1 MiB, software | 1 MiB / 64 B = 16,384 compressions x ~3,000 cycles = 49.2 M cycles / 64e6 | 768 ms (cycles per call from atlas 2.4, [E]) | NFR-LAT-04 |
| Same with hardware SHA at ~100 cycles | 16,384 x 100 = 1.64 M cycles / 64e6 | 25.6 ms [E] | FR-FS-15, NFR-LAT-04 |
| First-stage flash | 12,864 B demonstrated x 1.27 | 16,384 B | NFR-MEM-01 |
| Slot storage | 3 x 32 B | 96 B | FR-FS-02, NFR-FLASH-01 |
| Process-bus frame budget | 1e6 us / 4,800 and / 4,000 | 208.3 us and 250 us | NFR-LAT-05 |
| Oscillator drift at 20 ppm | 20e-6 x 31,557,600 s | 631 s = 10.5 min/yr; 105 min over 10 yr | FR-TIM-02 |
| LMS h=10 capacity vs root signing | 1,024 signatures; 2 x 40 yr x 12/yr = 960 (fits); 2 x 40 x 52/yr = 4,160 (does not fit) | root signing monthly fits h=10; weekly does not | FR-SIG-04, FR-TIM-07 |
| Signed 32-bit time horizon | 2^31 s = 68.0 yr from 1970 | 19 Jan 2038 | FR-TIM-06 |
| Watchdog conflict | ML-DSA-44 signing p99 584.2 ms / ~100 ms deadline | 5.8x over | NFR-DET-02 |
| Catch-up size, sequential | 10 yr x 1 floor advance/yr x 2,508 B (LMS-W4 signature) | about 25 KB; Merkle option shrinks (atlas 29x [C]) | FR-LC-14, NFR-OFF-02 |


## R.4.FR-AUT Authority and policy model

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-AUT-01 | The policy model SHALL represent every state-changing authority action (floor advance, slot replace, lifecycle transition, ownership transfer, revocation, debug unlock, configuration/safety-logic change, enclave exception, escrow release) as a typed action with an explicitly declared required quorum; no action type SHALL exist without a declared quorum. | I+T | MUST | M0 | R3, R9, N5, N6, N17, N22 |
| FR-AUT-02 | The library SHALL ship a signed, versioned, machine-readable assumption table A(k) mapping every algorithm, parameter set, implementation and holding organisation to the hardness/organisational assumptions it depends on (at minimum: MLWE/MSIS, SHA-2, SHA-3/Keccak, ECDLP, implementation lineage, holder organisation). | I | MUST | M0 | N58, P1, R1 |
| FR-AUT-03 | A policy compiler SHALL reject any policy in which the simultaneous failure of any single assumption in A(.) lets the forged key set satisfy any accepted quorum (single-assumption safety, SP-01); the check SHALL be parameterised for k simultaneous failures (default k=1) and SHALL emit a counterexample (assumption, key set) on rejection. | T+A | MUST | M0 | N58, P1, R1, I-4, I-19 |
| FR-AUT-04 | The policy compiler SHALL report, for each accepted policy, honest-availability under declared per-holder availability and SHALL flag any quorum whose liveness depends on a single organisation. | A | SHOULD | M1 | N41, R3, N67 |
| FR-AUT-05 | The authority model SHALL implement graded authority: boot requires one valid class; any authority change requires a disjoint-quorum; re-ownership additionally requires physical-presence evidence. | P+T | MUST | M1 | N22, N5, N6, R9, I-2 |
| FR-AUT-06 | The floor-advance rule SHALL require a valid signature from a slot different from the slot being retired, plus satisfaction of FR-AUT-03's compiled quorum; a validly signed higher-index image alone SHALL NOT advance the floor. | P+T | MUST | M1 | N22, R6, I-2 |
| FR-AUT-07 | A revocation or blocklist record whose target set intersects the device's current authority set SHALL be structurally invalid unless it carries the escrow class and presence evidence (PAM rule). | P+T | MUST | M1 | N22, N44, I-15 |
| FR-AUT-08 | Repeated validly signed authority-change attempts lacking the required second class SHALL demote the presenting key to boot-only (anergy), SHALL record the event, and SHALL be restorable only by a satisfying quorum; the demotion rate SHALL be bounded so it cannot lock out the legitimate OEM faster than quorum restoration. | P+T | SHOULD | M2 | N22, N66, I-14 |
| FR-AUT-09 | Every algorithm-class transition SHALL execute as the molting state machine (provision alongside, shadow-sign, hide, shed under disjoint quorum, harden for E epochs) with no phase skippable and no phase leaving the device without at least one verified class. | P+T | MUST | M2 | P1, P2, P12, R1, R10, I-16 |
| FR-AUT-10 | Competing successor claims SHALL be arbitrated by signed objections; no irreversible step SHALL execute while an objection is unresolved; after a bounded, policy-declared hold the case SHALL escalate and then be resolved by a deterministic tie-break rule. | P+T | MUST | M2 | N67, N41, R3, I-18 |
| FR-AUT-11 | Each authority key SHALL carry a declared scope (action types, device set) and rate limit enforced by the verifier or policy evaluator; scope-exceeding or rate-exceeding actions SHALL be rejected and logged. | T | SHOULD | M2 | N43, N47, N18 |
| FR-AUT-12 | Before a policy is signed, the toolchain SHALL replay a declared corpus of planned legitimate operations (next floor advances, RMA, ownership transfer, spare activation, drills) against it and SHALL reject the policy if any is refused (thymic test). | T | SHOULD | M2 | N66, N61, N49, I-22 |
| FR-AUT-13 | Changes to algorithm-agility configuration (enabled suites, minimum groups, pinning mode) SHALL be authority actions under FR-AUT-01 and SHALL NOT be settable by unauthenticated management paths. | T | MUST | M1 | N44, N45, R9 |
| FR-AUT-14 | Every authority action initiated by automation (including AI configuration assistants) SHALL require at least one human-attributable quorum signature recorded with the actor identity; automation-only quorums SHALL be rejected by policy. | T+I | MUST | M2 | N47, N18 |
| FR-AUT-15 | The policy compiler SHALL enforce the class anti-weak-path invariants (dominance, diversification, boundary, authority isolation, promotion) and SHALL reject policies granting a lower class (C0-C4) authority over a higher class or granting C5 keys online reachability from C4 networks. | A+T | MUST | M2 | N10, N43, N46, R4 |

## R.4.FR-FS Continuity first stage

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-FS-01 | The first stage SHALL verify the second stage using a hash-based signature scheme: LMS-SHA-256 W4 in the MV-1 profile; SHA-2 and SHA-3 based schemes (LMS-SHA-256, SLH-DSA-SHAKE; SP 800-230 sets when final) in the HA-1 profile; ML-DSA-65 verification occurs in the updatable second stage under the slot's key hash. | T+P | MUST | M1 | P1, P2, P8, R1 |
| FR-FS-02 | The first stage SHALL hold at least three 32-byte key-hash slots (96 B), spanning at least two disjoint assumption classes in HA-1, with one slot reserved for the eventual owner (operator/escrow) and provisioned at manufacture. | I+T | MUST | M1 | P1, P23, N7, R3 |
| FR-FS-03 | The product SHALL enable the part's flash/boot lock over the first stage before shipment; the first stage SHALL expose a lock-status attestation and SHALL contain no code path that unlocks or rewrites itself. | T+I | MUST | M1 | P8, P16, R1, N21 |
| FR-FS-04 | The first stage SHALL store no secret key material; its only persistent cryptographic content SHALL be public-key hashes, policy commitment hashes and counters. | I+A | MUST | M1 | N21, N70, N10 |
| FR-FS-05 | The floor SHALL be held in redundant, non-restorable monotonic storage with a write-ahead journal; ADVANCE_FLOOR SHALL commit the journal before burning the floor, and no restore, backup or re-flash path SHALL lower it. | P+T | MUST | M1 | N22, N39, P25, R6 |
| FR-FS-06 | Boot failure of image A SHALL fall to image B, then to a last-known-good (LKG) image that keeps the controlled process running; a BRICK_GUARD state SHALL prevent any transition that leaves no verified image. | T+P | MUST | M1 | P16, P30, R5, N20 |
| FR-FS-07 | Every state transition (ADVANCE_FLOOR, REPLACE_SLOT, image switch, journal replay) SHALL be atomic with respect to power loss: after a cut at any point the device SHALL be in the pre- or post-transition state and SHALL boot a verified image. | P+T | MUST | M1 | N20, P25, R6 |
| FR-FS-08 | Nothing that can live in the updatable second stage SHALL be placed in the first stage; the first-stage code size SHALL meet NFR-MEM-01. | I | MUST | M1 | N20, P9, P10 |
| FR-FS-09 | The verifier core SHALL have two independently written implementations (distinct teams and, where practicable, languages) and a differential test that runs on every build and every KAT/fuzz corpus. | T | MUST | M4 | N20, N71, N26 |
| FR-FS-10 | The first-stage state machine SHALL be formally modelled (TLA+ or equivalent) with proofs of invariants: no single-class key reaches ADVANCE_FLOOR; a power cut at any step leaves a bootable image; the floor never decreases; and the verifier core SHALL be proved free of runtime errors. | P | MUST | M4 | N20, N58, P16, R1 |
| FR-FS-11 | The first stage SHALL NOT require wall-clock time, network access or any external service to boot or verify. | T+I | MUST | M1 | P15, R2, P26 |
| FR-FS-12 | In HA-1 the first stage SHALL evaluate the compiled disjoint-quorum policy (committed by hash in the locked stage) on every ADVANCE_FLOOR, REPLACE_SLOT and lifecycle transition. | P+T | MUST | M4 | N58, N22, P2 |
| FR-FS-13 | REPLACE_SLOT3(owner) SHALL require the ownership voucher chain plus a signature from slot 1 or slot 2 under the floor rule, and SHALL be unavailable if slot 3 was never provisioned (such devices SHALL report 'queenless' status). | T+P | MUST | M2 | N7, N41, P23, R3 |
| FR-FS-14 | For parts that cannot lock a maker-defined first stage, the library SHALL provide a documented ANCHOR-WEAK profile, SHALL label such devices in state reports and CBOM, and SHALL NOT assert fleet-continuity guarantees for them. | I | MUST | M1 | P8, P11, P16, N55, R1 |
| FR-FS-15 | The first stage SHALL select the LMS parameter profile by capability: W4 where no hash engine is present, W8 where a hardware SHA engine is present, as a build-time configuration verified by the policy compiler. | T | SHOULD | M1 | P10, N27 |
| FR-FS-16 | The first stage SHALL self-check the integrity of its slot store and policy commitment at every boot and SHALL fail safe (LKG, report) on mismatch. | T | SHOULD | M1 | N20, R6 |
| FR-FS-17 | Revocation storage and anti-rollback storage SHALL be physically and logically separate banks. | I | SHOULD | M1 | R6, N22 |
| FR-FS-18 | The verifier SHALL use a hash-engine abstraction (FR-CRY-09) and SHALL support hash engines that stream so that image hashing cost is separable from signature verification cost. | T | SHOULD | M1 | P11, N55 |

## R.4.FR-CRY Crypto abstraction and implementations

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-CRY-01 | The algorithm registry SHALL identify every algorithm and parameter set by a stable library-owned numeric identifier with an immutable status history; persistent formats SHALL NOT embed provisional/draft OIDs except via an alias table that can be updated without reformatting stored artefacts. | I+T | MUST | M0 | N25, N24, P12 |
| FR-CRY-02 | Each registry entry SHALL declare its assumption set (feeding FR-AUT-02), key/signature sizes, statefulness, malleability class, and whether it is approved, draft, deprecated or suspected. | I | MUST | M0 | N58, N24 |
| FR-CRY-03 | The library SHALL provide verification for LMS (SHA-256 and SHAKE parameter sets), ML-DSA-44/65/87, SLH-DSA (FIPS 205; SP 800-230 sets once final), and decapsulation for ML-KEM-768/1024, plus FN-DSA verification once FIPS 206 is final, and the hybrid X25519MLKEM768 group. | T | MUST | M1 | P1, P4, R4 |
| FR-CRY-04 | Device (verify-only) builds SHALL exclude all signing code at compile time; signing primitives SHALL exist only in the host/HSM build profile. | I+T | MUST | M1 | P4, P29, R4, R5 |
| FR-CRY-05 | All secret-handling code paths SHALL be free of secret-dependent branches and memory addressing, and SHALL be tested with a constant-time checker on each supported compiler/target combination. | T+A | MUST | M1 | N71, N26 |
| FR-CRY-06 | The CI pipeline SHALL verify constant-time properties at binary level (post-compilation) for every released artefact, not only at source level. | T | MUST | M3 | N71, N26 |
| FR-CRY-07 | Host-side ML-DSA signing SHALL be deployed only inside hardened modules and SHALL randomise or mask rejection-loop timing so iteration count is not observable by an unprivileged observer. | A+T | SHOULD | M3 | N26, P29 |
| FR-CRY-08 | The API SHALL expose a signature malleability class (EUF-CMA vs SUF-CMA) and SHALL NOT deduplicate or key records by raw signature bytes of EUF-CMA-only composites. | I+T | MUST | M1 | N24 |
| FR-CRY-09 | A hash-engine HAL SHALL select hardware SHA-2/SHA-3 where present, fall back to constant-time software, and produce identical outputs verified by KAT. | T | MUST | M1 | P11, N55, N27 |
| FR-CRY-10 | A benchmark harness SHALL reproduce cycles, stack, RAM and flash per primitive and parameter set on named boards, and every published figure SHALL carry its parameter set, toolchain and evidence label. | T+I | MUST | M1 | N27, N73, P10 |
| FR-CRY-11 | Every primitive SHALL pass known-answer tests from the published standards' vectors and a differential test against at least one independent implementation. | T | MUST | M1 | N71, N27 |
| FR-CRY-12 | Per-primitive RAM/stack/flash budgets SHALL be published per target and enforced as CI regression gates. | T | MUST | M1 | P10, N27 |
| FR-CRY-13 | Hybrid-strict policy SHALL be a declarable per-peer-set mode with explicit fallback behaviour, a signed expiry epoch for any fallback exception, and reporting of peers that required fallback. | T | SHOULD | M3 | N45, N44, N57 |
| FR-CRY-14 | Negotiation SHALL refuse any suite weaker than the policy-declared minimum, and SHALL log attempted downgrades; defaults SHALL NOT silently select a weaker group than configured. | T | MUST | M2 | N44 |
| FR-CRY-15 | The policy layer SHALL support an operator-declared 'suspected' state for an algorithm or implementation (unconfirmed break), which blocks shedding of other classes, triggers shadow verification through the alternate class, and is reported in state evidence. | T | SHOULD | M3 | P1, N58, N54 |
| FR-CRY-16 | Verifiers SHOULD apply fault-tolerance countermeasures (redundant comparison of the accept decision, checked branch conditions) selectable per part profile. | T+A | SHOULD | M4 | N21, N70, N26 |
| FR-CRY-17 | Enrolment SHALL use ML-KEM decapsulation exactly once per device per key-hierarchy epoch, deriving a per-device KEK through a standard KDF bound to device UUID and class. | T | MUST | M2 | P4, P17, R4, N9 |
| FR-CRY-18 | Firmware-encryption key wrapping SHALL use a post-quantum KEM (hybrid permitted); classical-only wrapping of firmware keys SHALL be rejected by policy. | T | SHOULD | M2 | N9 |
| FR-CRY-19 | Constrained-link profiles SHALL support offline (non-air) key provisioning and fragmentation-aware transports so no large public-key object is required over LoRaWAN-class links. | T | SHOULD | M3 | P18, R4 |

## R.4.FR-SIG Signing infrastructure

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-SIG-01 | Release, voucher and debug-credential signing SHALL occur only in HSM-backed signing services under quorum; the library SHALL provide no code path to sign on constrained devices. | I+T | MUST | M1 | P4, N18, R4, R6 |
| FR-SIG-02 | A quorum signing coordinator SHALL produce dual-class (shadow-signed) signatures for each release during molting, with members drawn from disjoint assumption classes per FR-AUT-03. | T | MUST | M2 | N41, N58, I-16 |
| FR-SIG-03 | Stateful-key signing SHALL use index reservation with atomic persistence; a one-time index SHALL never be used twice, including across HSM failover, crash recovery and backup restore. | P+T | MUST | M1 | P3, N51, R6 |
| FR-SIG-04 | The signing service SHALL track remaining signature budget per key (2^h for LMS; the limit for SP 800-230 sets), warn at configured thresholds (default 50% and 20%) and refuse beyond capacity. | T | MUST | M1 | N56, P3 |
| FR-SIG-05 | A documented, attested procedure SHALL exist for moving stateful-key custody between HSM vendors or for re-rooting to a fresh key via FR-AUT-09 when export is unavailable. | I+D | SHOULD | M3 | N51, R6 |
| FR-SIG-06 | Configuration, protection-setting and safety-logic artefacts SHALL be signed by an m-of-n workstation quorum with keys in tokens or TPM; devices that can verify SHALL verify, and others SHALL be checked at the gateway against a signed manifest. | T | MUST | M2 | N17, N18, N47, R9 |
| FR-SIG-07 | Signing ceremonies SHALL be scripted, produce a signed ceremony record, and be rehearsable on a non-production key hierarchy. | D+I | SHOULD | M3 | N61, R10 |
| FR-SIG-08 | Signed artefacts (images, bundles, vouchers, policies) SHALL use a self-describing manifest carrying algorithm ids, floor, class tags, epoch validity, and a structured human-readable change diff. | I+T | MUST | M1 | I-12, N25, N31, P12 |
| FR-SIG-09 | Artefacts SHOULD support offline-verifiable witness cosignatures with at least one post-quantum cosignature class. | T | SHOULD | M4 | N68 |
| FR-SIG-10 | Release builds SHALL be reproducible and accompanied by SBOM and CBOM; two independent rebuilds SHALL yield identical hashes. | T | MUST | M3 | N71, N32, P33 |
| FR-SIG-11 | No single human SHALL be able to release signed artefacts or change signing-policy; all release approvals SHALL be dual-controlled and logged. | I+D | MUST | M1 | N18, R9 |
| FR-SIG-12 | Debug-credential issuance keys SHALL be distinct from release and RoT keys and held in a separate quorum. | I | MUST | M2 | N2, N1 |

## R.4.FR-LC Lifecycle, side doors and provisioning

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-LC-01 | The library SHALL define and validate an Authorisation Surface Map schema listing, per part and product, every path able to change code, keys, owner, debug state, lifecycle or configuration, with algorithm, key holder, binding (per-device or fleet) and classical/PQ flag, and SHALL compute an exposure score. | T+I | MUST | M0 | R9, N1, N2, N3, N4, N5, N6, N8, N9, N11, N16, N17, N18, N19, I-1 |
| FR-LC-02 | A per-part hardware evidence register SHALL record independent certification scheme/level/scope, protection across lifecycle states, documented countermeasures and public field history, and SHALL link to CBOM entries and affected-device queries. | I | MUST | M2 | N70, N21, N55, N26, N4 |
| FR-LC-03 | Debug credentials SHALL be PQ-signed and bound to the device UUID (and optionally lifecycle state); a credential valid for one device SHALL fail on every other device. | T | MUST | M2 | N1, N2 |
| FR-LC-04 | The lifecycle model SHALL define TEST, PROD, RMA and DECOMMISSIONED states; field debug SHALL be disabled on entering PROD commissioning; every transition SHALL be an authority action under FR-AUT-01. | P+T | MUST | M2 | N1, N3, N4, R9 |
| FR-LC-05 | No reverse lifecycle transition (RMA, factory reset, re-provision) SHALL reopen general debug access; the supported repair path SHALL be board replacement with decommissioning receipt. | P+T | MUST | M2 | N3, N4, R9 |
| FR-LC-06 | RMA/lifecycle authorisations SHALL be per-device, SHALL be revocable by floor advance, and SHALL NOT remain valid after the product's declared support-end epoch counter is passed. | T | SHOULD | M2 | N3, R9 |
| FR-LC-07 | Factory provisioning SHALL use KEM-wrapped per-device key injection; no fleet-shared secret SHALL be provisioned; the provisioning log SHALL be co-signed by the contract manufacturer and the OEM. | T+I | MUST | M2 | N8, N10, R9 |
| FR-LC-08 | Device identity credentials (IDevID/DICE-style) SHALL be issued with PQ or hash-based signatures, in dual-class form where the verifier population requires it. | T | MUST | M2 | N11, N12 |
| FR-LC-09 | Feature-licence and activation tokens SHALL be PQ-signed and bound per device. | T | SHOULD | M3 | N16 |
| FR-LC-10 | Vendor remote-access portals SHALL be modelled as authority paths in the surface map; the library SHALL provide a quorum-gated, out-of-band-confirmed session-authorisation profile, and SHALL support operating modes that disable remote paths entirely. | T+I | MUST | M3 | N19, N65, R9 |
| FR-LC-11 | Decommissioning SHALL produce a signed receipt (UUID, floor, keys destroyed, trust-list removals) that SHALL be logged before the device may be reprovisioned or resold. | T+I | MUST | M2 | N36, N37, N53, I-6 |
| FR-LC-12 | Refurbish/re-commission SHALL wipe prior identity, verify first-stage lock and debug-closed state at intake, and issue a fresh identity only under presence evidence. | T | MUST | M3 | N36, N53 |
| FR-LC-13 | Spare devices SHALL be able to ship with only the first stage and slot hashes and SHALL accept application image and ownership only at installation via voucher and current bundle (dormancy). | T | SHOULD | M3 | P24, N23, N53, I-5 |
| FR-LC-14 | A catch-up bundle format SHALL let a device at floor k reach the current floor in bounded bytes, using sequential chain proofs and, optionally, Merkle-committed future sets; the format SHALL state size per step. | T | MUST | M2 | P22, N23 |
| FR-LC-15 | Trust lists SHALL support removal on decommissioning receipt, and consumers SHALL reject certificates of decommissioned UUIDs. | T | MUST | M3 | N37, N36 |
| FR-LC-16 | A site-local physical-presence token SHALL be defined as an authority input subject to FR-AUT-05 itself (a token alone SHALL NOT grant any authority). | P+T | MUST | M2 | I-2, I-3, R9 |
| FR-LC-17 | The library MAY support Merkle-committed future key sets with custody split across organisations in different assumption classes. | A | MAY | M5 | N40, P22, I-11 |

## R.4.FR-OWN Ownership and succession

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-OWN-01 | The library SHALL support an FDO-compatible ownership voucher profile signed with ML-DSA or SLH-DSA (dual-class optional), including size handling for voucher chains. | T+D | MUST | M2 | N5, N6 |
| FR-OWN-02 | Voucher escrow SHALL archive voucher files together with a reference verifier, format specification and signing-algorithm identifiers sufficient to verify them without the issuer. | I+D | MUST | M2 | N7, N60 |
| FR-OWN-03 | The library SHALL define an OEM heartbeat artefact (PQ-signed liveness statement), a publisher, a verifier and an absence-evidence record for witnessed publication. | T | SHOULD | M3 | P13, P23, N41, I-17 |
| FR-OWN-04 | Escrow-trigger evaluation SHALL be an off-device, witnessed, contract-parameterised process (missed heartbeats, unfixed critical CVE window); devices SHALL never implement the trigger via an internal timer. | I+T | MUST | M3 | P23, P31, N49, P13 |
| FR-OWN-05 | Supersedure SHALL be supported as an OEM-signed hand-over of authority to slot 3, executable while the OEM exists and before CRA-support end. | T | MUST | M2 | P23, N49, N29, R3 |
| FR-OWN-06 | A 'swarm' voucher operation SHALL transfer authority over a named sub-fleet (facility sale/split) with witnessed transfer log. | T | SHOULD | M3 | N52, N67 |
| FR-OWN-07 | An authority-holdings report SHALL enumerate, per facility or sub-fleet, signing keys, vouchers, debug credentials, remote portals and workstation custodians to support M&A diligence. | T+D | SHOULD | M3 | N52, N19, N18 |
| FR-OWN-08 | Ownership transfer messages (OpenTitan-style) SHALL be signed with PQ or dual-class signatures. | T | MUST | M2 | N5 |
| FR-OWN-09 | Fleet inventory SHALL flag every device lacking a provisioned slot 3 ('queenless') and produce the replacement-or-enclave cost report. | T | MUST | M3 | P23, P13, R3 |

## R.4.FR-KEY Key distribution and symmetric fabric

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-KEY-01 | Process-bus and field-bus data paths SHALL remain symmetric (existing MAC/AES-GMAC formats); public-key operations SHALL occur only at enrolment and authority changes. | A+T | MUST | M2 | P19, P4, R4 |
| FR-KEY-02 | The KDC SHALL derive per-device keys by diversification so that no key is shared across devices; the diversification key SHALL reside only in C4/C5 HSMs. | T+I | MUST | M2 | N10, N43, P20, R4 |
| FR-KEY-03 | The KDC SHALL support replication with t-of-n unlock, HSM-held KEKs and per-zone scoping, with island sites runnable on KDC replicas. | T | SHOULD | M3 | N43, N46 |
| FR-KEY-04 | Group keys SHALL be distributed per GDOI-style rekey with short epochs and membership bound to per-device identity; a PQ-capable profile SHALL be specified for standardisation. | T+D | SHOULD | M3 | P20, P19, N10 |
| FR-KEY-05 | Missed group rekeys SHALL be recoverable using a counter floor without per-device manual intervention. | T | SHOULD | M3 | P20, P22 |
| FR-KEY-06 | Safety-function code SHALL interact with cryptography through a narrow, stable interface so that cryptographic components can be replaced without altering safety-function code or its timing envelope. | I+A | MUST | M2 | R5, P28, P29 |
| FR-KEY-07 | Key derivation SHALL include class, device UUID and epoch in context; keys SHALL be unusable across classes. | T | MUST | M2 | N10, R4 |
| FR-KEY-08 | Fleet evidence SHALL flag devices or accounts holding or having used keys or group memberships beyond their role (camouflage detection). | T | SHOULD | M4 | N10, N43, I-28 |
| FR-KEY-09 | The library MAY provide ratcheted symmetric authority for disconnected assets (SDLS-style). | A | MAY | M5 | P26, P22, I-31 |
| FR-KEY-10 | The enrolment of class-C1 devices SHALL be possible physically (technician) or via a KEM through a gateway without public-key work on the device beyond a single decapsulation or none. | T | MUST | M2 | P4, P17, R4, P18 |

## R.4.FR-UPD Update, staging and activation

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-UPD-01 | The transition-bundle format SHALL be signed, self-describing, stageable dormant, and verifiable offline. | T | MUST | M2 | N13, N14, R8 |
| FR-UPD-02 | Devices SHALL stage verified bundles in the inactive A/B slot without activation, and activation SHALL require the conditions declared in the bundle. | T | MUST | M2 | R8, N14, N33 |
| FR-UPD-03 | Activation SHALL require a site-local presence token and an authority signature (two-key activation), SHOULD randomise activation offset inside the window, and SHALL emit a report countersignable by a second observer. | T | SHOULD | M3 | I-3, I-8, N14 |
| FR-UPD-04 | After each activation the device SHALL emit a signed state report per FR-EVD-01 within a declared time bound after activation. | T | MUST | M3 | R7, P32, N50 |
| FR-UPD-05 | A crypto-only update lane SHALL separate the cryptographic component into an independently updatable module with stable interface, so crypto changes do not bundle with functional changes. | I+D | MUST | M3 | N48, P28, R5, I-7 |
| FR-UPD-06 | The orchestrator SHALL stage activation by site, class and cohort, SHALL halt automatically on adverse signals (failed state reports, error-rate thresholds), and SHALL never perform global simultaneous activation. | T | MUST | M3 | N62, R8 |
| FR-UPD-07 | During emergency rollouts the orchestrator SHALL hold a configurable persister fraction on LKG until the new state is verified and SHALL apply tightened enclave controls to persisters. | T | SHOULD | M3 | N62, I-33 |
| FR-UPD-08 | The orchestrator SHALL gate every irreversible fleet step (classical sunset, class retirement) on readiness of all dependent participants, with a bounded hold followed by escalation to human review (spindle gating). | T | MUST | M3 | N72, N64, I-27 |
| FR-UPD-09 | After every irreversible step the orchestrator SHALL maintain a straggler registry with per-device routing to enclave or visit. | T | MUST | M3 | N72, P16 |
| FR-UPD-10 | A window-calendar model SHALL represent planned and emergency windows per site and map bundles to windows, with two-process gating (accumulated pressure meets allowed gate). | T | SHOULD | M3 | N14, N33, R8, R10 |
| FR-UPD-11 | The tooling SHALL provide a read-only adoption measurement mode producing anonymised update-adoption and downtime metrics. | D | SHOULD | M3 | N13, N34 |
| FR-UPD-12 | Where no vendor patch exists, the orchestrator SHALL support compensating-control bundles (enclave rules, disabled paths) with owner-signed exit epochs. | T | SHOULD | M4 | N15, N13 |
| FR-UPD-13 | A rehearsal facility SHALL replay a bundle and policy against a modelled or emulated lab replica before activation. | D | SHOULD | M3 | N62, N61, N48 |
| FR-UPD-14 | Rollback below the floor SHALL be refused; any signed emergency downgrade SHALL be an authority action with quorum and presence. | P+T | MUST | M1 | R6, N22 |
| FR-UPD-15 | A slot-drill framework SHALL verify a release through the alternate class alone at least annually (configurable), report success/failure, and rotate classes across drills. | T+D | MUST | M3 | N57, N64, R10, I-13 |
| FR-UPD-16 | The tooling SHALL provide full-transition rehearsal packages (not only slot drills) schedulable at an interval such that each engineer participates at least twice in a career. | D | SHOULD | M4 | N61, R10, I-30 |
| FR-UPD-17 | An update SHALL never leave the device without a verified LKG image; a failed activation SHALL revert automatically. | T+P | MUST | M1 | N62, P30, R5 |

## R.4.FR-TIM Time, epochs and counters

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-TIM-01 | Device-side authority decisions SHALL use counters and epochs, never calendar time. | I+T | MUST | M1 | R2, P15, P27 |
| FR-TIM-02 | Validity SHALL be expressed in coarse epochs of at least one month, sized to the declared oscillator drift bound; each device SHALL record the bound used. | A+T | MUST | M2 | R2, P15, P22 |
| FR-TIM-03 | A zeitgeber library SHALL ingest independent time cues, label each with what it can prove (not-before, not-after, rate), and fuse them with plausibility windows so that no single source decides. | T+A | SHOULD | M3 | I-23, N42, N59 |
| FR-TIM-04 | Time SHALL never grant authority; staleness SHALL only reduce privileges and SHALL never halt a safety function. | P+T | MUST | M1 | P15, P27, R2 |
| FR-TIM-05 | A defined senescent state SHALL retain control function, refuse authority changes, and be announced in every report. | T | MUST | M2 | I-34, P26, R2 |
| FR-TIM-06 | No persisted format or API SHALL use 32-bit signed time; time and counters SHALL be wrap-safe for the asset life. | I+T | MUST | M0 | N56, R11 |
| FR-TIM-07 | A counter-capacity register SHALL list every counter, time field and signature budget with capacity, consumption rate and asset life, and the build SHALL fail if capacity is less than twice life consumption. | A+T | MUST | M0 | N56, R11, P3 |
| FR-TIM-08 | Unauthenticated PTP or other unauthenticated time SHALL NOT feed any security policy decision. | T+I | MUST | M2 | N42 |
| FR-TIM-09 | Grid-cycle or ENF-derived inputs, if used, SHALL be plausibility inputs only and SHALL tolerate deviations of at least several minutes and islanding. | A+T | SHOULD | M5 | N59, I-24, I-25 |
| FR-TIM-10 | Certificate and credential handling SHALL support 'no well-defined expiry' encodings with issuer duty documented, and SHALL not fail closed on calendar expiry alone for safety functions. | T | MUST | M2 | P27, R2 |
| FR-TIM-11 | Offline revocation SHALL be achieved through floor/counter advancement and signed bundles carried at visits, not through fetched CRLs. | T | MUST | M2 | P26, R2 |
| FR-TIM-12 | A technician freshness token SHALL provide a signed not-before bound for visits to long-disconnected assets. | T | SHOULD | M3 | P26, P22, I-23 |
| FR-TIM-13 | The library MAY support SRAM-remanence power-off timers as one labelled zeitgeber input. | A | MAY | M5 | I-26 |

## R.4.FR-EVD Evidence, observability and reporting

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-EVD-01 | Devices capable of signing SHALL emit a signed state report carrying floor, active slots and classes, image hash, policy hash, lifecycle state, senescence flag, anchor profile and hardware-evidence reference. | T | MUST | M2 | P32, N50, R7 |
| FR-EVD-02 | Every state report SHALL carry a structured, human-readable delta from the previous report. | T | MUST | M3 | I-12, N50 |
| FR-EVD-03 | The tooling SHALL generate CycloneDX CBOM from state reports, inventories and surface maps, including per-part hardware evidence. | T | MUST | M3 | P33, N50, N70, R7 |
| FR-EVD-04 | Reports SHALL map to TCG/IETF RATS attestation formats where the platform provides them, including TPM 2.0 v1.85 ML-KEM/ML-DSA identity where available. | T | SHOULD | M4 | N12, N50 |
| FR-EVD-05 | Passive inference parsers SHALL derive crypto state for silent devices from OPC UA, TLS/DTLS, IKE and GDOI observations with a measured accuracy target of at least 95% on a labelled corpus. | T | SHOULD | M4 | N50, N38, P32 |
| FR-EVD-06 | An OPC UA configuration linter SHALL flag AutoAccept and SecurityMode=None. | T | MUST | M3 | N38 |
| FR-EVD-07 | Alerts SHALL key on danger signals (authority-changing events, safety-logic signature changes, out-of-window state changes) rather than novelty. | T | SHOULD | M4 | N46, N66, R7 |
| FR-EVD-08 | The tooling SHALL compute exposure-years per the M5 model and report it as the primary programme metric alongside percentage migrated. | T+A | MUST | M3 | P34, P33, R7, N35, I-21 |
| FR-EVD-09 | The tooling SHALL export evidence mapped to named regimes (CRA Art. 14, NIST IR 8547, CNSA 2.0, India CII inventory) with each regime's own 'done' definition stated explicitly. | I+D | SHOULD | M4 | N31, N28, N29, N30, P35 |
| FR-EVD-10 | Vouchers, receipts, transition logs and state reports SHALL be archived as evidence records with RFC 4998-style timestamp and hash-tree renewal performed before algorithm validity ends. | T+D | MUST | M3 | N60, I-29 |
| FR-EVD-11 | Fleet slot-set commitment hashes SHALL be publishable to widely witnessed media with verification instructions. | D | SHOULD | M4 | N60, N68 |
| FR-EVD-12 | Transparency-log and witness components SHALL use post-quantum or dual-class cosignatures from day one. | T | SHOULD | M4 | N68 |
| FR-EVD-13 | Monitoring taps SHALL be read-only, SHALL hold no authority keys, and SHALL be enumerated in the surface map. | I+T | MUST | M3 | N46 |
| FR-EVD-14 | Evidence archives SHALL include reference verifiers and format specs, versioned and hash-pinned. | I | MUST | M3 | N60, R10 |
| FR-EVD-15 | Conformance claims SHALL be machine-checkable against the public test suite so owners can verify OEM post-quantum claims. | T | MUST | M4 | N32, N27 |
| FR-EVD-16 | The tooling MAY export anonymised crypto-state posture for insurer/loss-data use. | D | MAY | M5 | N35, P35 |

## R.4.FR-ENC Enclave and legacy containment

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-ENC-01 | The library SHALL provide an enclave gateway profile (PQ-terminating boundary, passive inventory, signed configuration) for C0/C1 devices. | T+D | MUST | M3 | P16, N12, N63 |
| FR-ENC-02 | Every legacy exception SHALL carry an owner-signed exit epoch; the gateway SHALL surface alarms as it approaches and SHALL require quorum re-authorisation to extend it. | T | MUST | M3 | N30, N63, I-9 |
| FR-ENC-03 | Enclaves SHALL be sectorable, with independent boundary keys per sector so that one boundary failure exposes one sector. | A+T | SHOULD | M4 | N43, N30 |
| FR-ENC-04 | The gateway profile SHALL support dual-vendor deployment with interop tests. | T | SHOULD | M4 | N43 |
| FR-ENC-05 | Gateway configuration SHALL be signed under FR-SIG-06 and gateway logs SHALL be witnessed. | T | MUST | M3 | N43, N46 |
| FR-ENC-06 | The library MAY ingest design-derived physical invariants as a second signal for commands and reports inside enclaves. | D | MAY | M5 | I-32, P16 |
| FR-ENC-07 | The boundary rule SHALL be machine-checkable: every C0/C1 device SHALL be inside a zone whose boundary is C4, crossing via PQ-protected channels. | A | MUST | M3 | N30, R4 |
| FR-ENC-08 | Operating modes for jurisdictional constraints on remote operation SHALL be configurable and auditable. | T+I | MUST | M3 | N65, N19 |
| FR-ENC-09 | The inventory SHALL carry a dated replacement plan with budget line per enclosed device. | I | SHOULD | M3 | N30, N49, P16 |

## R.4.FR-MIG Fleet planning and migration orchestration

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-MIG-01 | The inventory model SHALL assign each device a class C0-C5 and record authority holdings per chain. | T+I | MUST | M3 | R7, P32, P33 |
| FR-MIG-02 | The tooling SHALL build a trust graph from inventory and passive observation. | T | MUST | M3 | R7, N50 |
| FR-MIG-03 | The ordering engine SHALL compute migration order by class (C5 first), hubs first, blast-radius per step, and the acquaintance rule when inventory is incomplete. | T+A | MUST | M3 | I-20, N69, R7 |
| FR-MIG-04 | The planner SHALL refuse to label a migration complete unless all six authority chains are classified and the residual classical channels are listed. | T | MUST | M3 | N69, R9, N31 |
| FR-MIG-05 | The planner SHALL compute what a replacement budget buys in exposure-years. | A | SHOULD | M3 | P34, N29, R7 |
| FR-MIG-06 | The tooling SHALL report the unrescuable set (classical-only immutable verifier, no lockable stage, no presence access). | T | MUST | M3 | P16, N12, N55 |
| FR-MIG-07 | A procurement-profile generator SHALL emit clauses (hash engine, three or more slots over two or more classes, PQ debug and vouchers, no field debug, certification evidence). | I | SHOULD | M3 | N55, N27, N32 |
| FR-MIG-08 | Migration experiments (models M1-M7) SHALL be reproducible from the repository with fixed seeds and published parameters. | T | MUST | M0 | N73, N27 |
| FR-MIG-09 | Existing fleets SHALL be transitionable via the molting orchestration without requiring device replacement where class permits. | D | SHOULD | M4 | P1, P12, R1 |

## R.4.FR-ASR Assurance and verification

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-ASR-01 | Formal models SHALL live in the repository with CI model-checking on every change. | P | MUST | M1 | N20, N58, R10 |
| FR-ASR-02 | A neutral conformance suite SHALL test first stages, vouchers, debug credentials and bundles. | T | MUST | M4 | N32, N27, I-10 |
| FR-ASR-03 | A power-loss harness SHALL run at least 100,000 randomised boots/transitions per release. | T | MUST | M1 | N20, P25, R6 |
| FR-ASR-04 | The project SHALL expose fault-injection and side-channel evaluation hooks so independent labs can run campaigns; the project itself SHALL NOT publish attack procedures. | I | SHOULD | M4 | N21, N70, N26 |
| FR-ASR-05 | Benchmarks SHALL be published with evidence labels, parameter sets and toolchains. | I | MUST | M1 | N27, N73 |
| FR-ASR-06 | A claims register SHALL record every security and performance claim with an evidence label and test link. | I | MUST | M0 | N73, N32 |
| FR-ASR-07 | Independent third-party review SHALL precede declaring the first stage stable. | I | MUST | M4 | N20, R1 |
| FR-ASR-08 | The project SHALL supply safety-case artefacts demonstrating crypto confinement (separation, timing envelope, failure modes) reusable by assessors. | I | SHOULD | M4 | N48, P28, R5 |
| FR-ASR-09 | WCET analysis SHALL accompany each device-side primitive on supported targets. | A | MUST | M2 | P29, R5 |
| FR-ASR-10 | All parsers SHALL be bounded and continuously fuzzed. | T | MUST | M1 | N20, N71 |
| FR-ASR-11 | Supply-chain controls (dependency pinning, toolchain provenance, signed releases) SHALL be implemented. | I | MUST | M1 | N71, R9 |

## R.4.FR-GOV Governance, formats and long-term stewardship

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-GOV-01 | Wire and storage formats SHALL be versioned, self-describing, forward-compatible for non-critical fields and reject unknown critical fields. | T+I | MUST | M0 | P12, N25, N60 |
| FR-GOV-02 | Format identifiers and registry entries SHALL never be reused or silently redefined. | I | MUST | M0 | N25, P12 |
| FR-GOV-03 | Specifications SHALL be archived in plain text with multiple independent encodings and reference implementations. | I | MUST | M2 | N60, R10 |
| FR-GOV-04 | The project SHALL be under an open licence with patent grant and maintainer governance that survives any single organisation. | I | SHOULD | M0 | R3, N41 |
| FR-GOV-05 | Every module SHALL declare which requirement IDs it implements. | I | SHOULD | M1 | N73 |

## R.4.FR-PRO Protocol profiles

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| FR-PRO-01 | TLS 1.3 hybrid profile (X25519MLKEM768) SHALL handle ClientHellos exceeding one MTU and be tested through representative OT firewalls. | T | MUST | M3 | P18, N44, N45 |
| FR-PRO-02 | IKEv2 profile SHALL place PQ key exchange in IKE_INTERMEDIATE with multiple key exchanges per the published RFCs. | T | MUST | M3 | P18 |
| FR-PRO-03 | The OPC UA profile SHALL document the application-layer fallback pending a standard PQ policy, SHALL flag non-secure modes, and SHALL track standardisation. | I+T | SHOULD | M4 | N38, N31 |
| FR-PRO-04 | DNP3-SA, SecOC, LoRaWAN, GOOSE/SV profiles SHALL cover only key delivery and rekey, leaving data-path formats unchanged. | I | MUST | M3 | P19, P17, R4 |
| FR-PRO-05 | The project SHOULD contribute PQ profiles (GDOI-PQ, FDO-PQ) to the relevant standards bodies. | I | SHOULD | M4 | N31, N6, P20 |

## R.4.NFR Non-functional requirements

| ID | Requirement | Ver | Pri | MS | Traces |
|---|---|---|---|---|---|
| NFR-MEM-01 | The MV-1 first stage SHALL fit in 16,384 B of flash (code, constants, verifier) and its static stack SHALL not exceed 2,048 B; both measured per target. | T | MUST | M1 | P9, P10, N20 |
| NFR-MEM-02 | The updatable second stage SHALL publish ML-DSA-44/65 verify RAM per target; target for M33-class is at most 16 KiB RAM pending E-A2 measurement. | T | SHOULD | M2 | P10, N27 |
| NFR-MEM-03 | ML-KEM-768 decapsulation SHALL not exceed 16 KiB stack on Cortex-M0+. | T | MUST | M2 | P10, P4 |
| NFR-MEM-04 | The first stage and verifier SHALL use no dynamic allocation; all buffers SHALL be statically bounded. | I | MUST | M1 | N20, N71 |
| NFR-FLASH-01 | Slot, policy-hash and floor/journal storage SHALL occupy at most two erase sectors plus 96 B of slot data in the MV-1 profile. | I | MUST | M1 | P9, R6 |
| NFR-FLASH-02 | Flash wear from journal and counters SHALL be computed over the asset life with a 2x margin. | A | MUST | M1 | N56, R6 |
| NFR-LAT-01 | LMS-SHA-256 W4 signature verification SHALL complete within 60 ms at 64 MHz Cortex-M4 in software, excluding image hashing. | T | MUST | M1 | P4, P11, N27 |
| NFR-LAT-02 | ML-DSA-44 verification SHALL complete within 100 ms on M0+-class parts at the benchmark's declared reference clock (measured 44.0 ms on RP2040 [D]; threshold from E-A2 decision gate). | T | SHOULD | M2 | P4, N73 |
| NFR-LAT-03 | ML-KEM-768 decapsulation SHALL complete within 50 ms on M0+-class parts. | T | MUST | M2 | P4 |
| NFR-LAT-04 | Boot-time budget SHALL be declared per profile with image-hash time reported separately and scaled by image size. | A+T | MUST | M1 | P11, N55 |
| NFR-LAT-05 | No public-key operation SHALL execute within a Sampled Values or GOOSE frame path; per-frame budget is 208-250 us at 4,800-4,000 frames/s. | A+T | MUST | M2 | P19, R4 |
| NFR-LAT-06 | Group rekey SHALL complete within 1 s per group without disturbing data-path latency. | T | SHOULD | M3 | P20, P19 |
| NFR-DET-01 | Verification and decapsulation execution time SHALL be independent of secret data and have a bounded, analysable WCET. | A+T | MUST | M2 | P29, N71 |
| NFR-DET-02 | On C3 devices, cryptographic operations SHALL NOT run in the control loop; ML-DSA signing SHALL be forbidden on C3 given 584 ms p99 against ~100 ms deadlines. | A+I | MUST | M2 | P29, R5, P28 |
| NFR-DET-03 | Release artefacts SHALL be bit-reproducible. | T | MUST | M3 | N71, N32 |
| NFR-PWR-01 | Per-operation energy SHALL be published; C1 battery devices SHALL perform no public-key operations except enrolment. | T+I | SHOULD | M3 | R4, P4 |
| NFR-PWR-02 | Power loss at any instruction SHALL be tolerated (SP-03) with at least 100,000 randomised cut tests per release. | T | MUST | M1 | N20, P25 |
| NFR-PORT-01 | The device-side core SHALL be portable freestanding C (no OS or libc dependency beyond declared intrinsics) behind a HAL; memory-safe implementations MAY exist with C ABI. | I | MUST | M1 | N55, P11, N20 |
| NFR-PORT-02 | CI SHALL cover Cortex-M0+, M4, M33, RISC-V 32-bit and a host target, with at least two compiler families. | T | MUST | M1 | N71, N55 |
| NFR-PORT-03 | The code SHALL be free of undefined behaviour and endian/alignment assumptions, verified by sanitizers and static analysis. | T | MUST | M1 | N71, N20 |
| NFR-API-01 | Public APIs SHALL follow semantic versioning with a minimum deprecation period; first-stage-facing formats SHALL be frozen once released. | I | MUST | M2 | P12, N25 |
| NFR-API-02 | Storage and wire formats SHALL remain readable by later releases for the declared device lifetime. | T | MUST | M2 | N60, P12 |
| NFR-OFF-01 | All device-side verification SHALL operate fully offline with no network or time source. | T | MUST | M1 | P15, P26, R2 |
| NFR-OFF-02 | A device offline for 10 years SHALL accept a valid catch-up bundle within a declared bundle-size bound. | T+A | MUST | M2 | P22, N23, N56 |
| NFR-LIFE-01 | Design life SHALL be at least 40 years: counters at least 2x margin, formats legible for 50 years, algorithm replaceable above the first stage. | A | MUST | M0 | N56, R11, P11 |
| NFR-LIFE-02 | No verification SHALL depend on a vendor-operated service existing. | I | MUST | M1 | R3, N41, N63 |
| NFR-LIFE-03 | The second stage SHALL be replaceable in the field with algorithms not known at the first stage's build. | T | MUST | M2 | P1, P12, R1 |
| NFR-CERT-01 | Code SHALL follow a published coding standard, be static-analysis clean, and carry requirements-to-code-to-test traceability to enable assessment under functional-safety and security-assurance schemes (candidate targets [I]: IEC 61508, IEC 62443, Common Criteria). | I | MUST | M4 | P28, N48, R5 |
| NFR-CERT-02 | The cryptographic component SHALL be separable with a stable interface for independent assessment. | I | MUST | M3 | N48, P28, R5 |
| NFR-CERT-03 | First-stage control flow SHALL be statically analysable with bounded loops and bounded cyclomatic complexity. | A | SHOULD | M4 | N20, P28 |
| NFR-SAFE-01 | A security fault SHALL never inhibit a safety function; every safe-misfire path SHALL fail operational. | A+T | MUST | M2 | P30, N66, R5 |
| NFR-SEC-01 | Device-side parsers SHALL reject malformed input without state change and with bounded resource use. | T | MUST | M1 | N20, N71 |
| NFR-OPS-01 | Operator-facing outputs SHALL be human-readable and machine-readable with equivalent content. | I | SHOULD | M3 | I-12, R7 |
| NFR-OPS-02 | The orchestrator SHOULD scale to at least one million devices per fleet using cohort staging. | T | SHOULD | M3 | N62, R8 |
| NFR-INT-01 | The project SHALL not change IEC 62351-6 or existing field-bus frame formats. | I | MUST | M2 | P19, N31 |
| NFR-DOC-01 | Every document SHALL attach evidence labels per claim. | I | MUST | M0 | N73 |

## R.4.Z Requirement counts

| Priority | FR | NFR |
|---|---|---|
| MUST | 125 | 29 |
| SHOULD | 55 | 7 |
| MAY | 5 | 0 |

| Milestone | Requirements |
|---|---|
| M0 | 15 |
| M1 | 55 |
| M2 | 56 |
| M3 | 63 |
| M4 | 26 |
| M5 | 6 |

# R.5 Traceability matrix

Status definitions (RD-5): **COVERED** software requirements address the problem, residual is implementation/validation risk. **PARTIAL** software mitigates; the residual is named (SILICON, POLICY, CONTRACT, PHYSICS, MARKET, DATA). **OUT_OF_SCOPE** no software requirement can reduce the problem; enabling requirements, if any, only produce evidence. **RESEARCH** depends on unvalidated research; only MAY hooks exist. **UNITEMISED** the atlas (2nd ed.) never names the problem, it lists only the range P1-P35; the row is mapped through its neighbouring root-cause proxies and needs the original list from the atlas author.

Requirement IDs are computed from the Traces column of R.4 (reverse index), so the matrix cannot drift from the requirements.

## R.5.1 Coverage statistics (computed by code/R/gen.py)

| Group | n | COVERED | PARTIAL | OUT_OF_SCOPE | RESEARCH | UNITEMISED |
|---|---|---|---|---|---|---|
| P (P1-P35) | 35 | 21 | 9 | 0 | 0 | 5 |
| N (N1-N73) | 73 | 34 | 32 | 5 | 2 | 0 |
| R (R1-R11) | 11 | 4 | 7 | 0 | 0 | 0 |
| All | 119 | 59 | 48 | 5 | 2 | 5 |

For the 108 problems only (P+N, excluding R): COVERED 55 (50.9%), PARTIAL 41 (38.0%), OUT_OF_SCOPE 5 (4.6%), RESEARCH 2 (1.9%), UNITEMISED 5 (4.6%). 
Software-addressed (COVERED+PARTIAL): 96 of 108 = 88.9%.

Residual-type tags among PARTIAL rows (a row may carry several): POLICY 25, PHYSICS 11, SILICON 10, CONTRACT 6, MARKET 4.

Requirement-side checks: 221 requirements; every requirement traces to at least one atlas ID (validated); every COVERED/PARTIAL row has at least one requirement (validated); 89 requirements are cross-cutting or enabling and not directly cited by a use case or security property; they remain traced to atlas IDs (FR-AUT-01, FR-FS-08, FR-FS-14, FR-FS-16, FR-FS-17, FR-FS-18, FR-CRY-01, FR-CRY-02, FR-CRY-03, FR-CRY-04, FR-CRY-05, FR-CRY-07, FR-CRY-08, FR-CRY-09, FR-CRY-10, FR-CRY-12, FR-CRY-16, FR-CRY-19, FR-SIG-08, FR-SIG-09, FR-SIG-10, FR-LC-08, FR-LC-09, FR-LC-17, FR-KEY-05, FR-KEY-09, FR-UPD-11, FR-TIM-02, FR-TIM-10, FR-TIM-11, FR-TIM-13, FR-EVD-02, FR-EVD-04, FR-EVD-06, FR-EVD-11, FR-EVD-13, FR-EVD-16, FR-ENC-04, FR-ENC-06, FR-MIG-05, FR-MIG-08, FR-MIG-09, FR-ASR-01, FR-ASR-04, FR-ASR-05, FR-ASR-06, FR-ASR-07, FR-ASR-08, FR-ASR-09, FR-ASR-10, FR-ASR-11, FR-GOV-01, FR-GOV-02, FR-GOV-04, FR-GOV-05, FR-PRO-01, FR-PRO-02, FR-PRO-03, FR-PRO-04, FR-PRO-05, NFR-MEM-01, NFR-MEM-02, NFR-MEM-03, NFR-MEM-04, NFR-FLASH-01, NFR-LAT-02, NFR-LAT-03, NFR-LAT-04, NFR-LAT-06, NFR-DET-01, NFR-DET-03, NFR-PWR-01, NFR-PWR-02, NFR-PORT-01, NFR-PORT-02, NFR-PORT-03, NFR-API-01, NFR-API-02, NFR-LIFE-01, NFR-LIFE-02, NFR-LIFE-03, NFR-CERT-01, NFR-CERT-02, NFR-CERT-03, NFR-SEC-01, NFR-OPS-01, NFR-OPS-02, NFR-INT-01, NFR-DOC-01); ideas I-1..I-34 without any requirement: none.

## R.5.2 Matrix

| ID | Problem | Status | Requirements | Residual / note |
|---|---|---|---|---|
| P1 | Algorithm monoculture | COVERED | FR-AUT-02, FR-AUT-03, FR-AUT-09, FR-FS-01, FR-FS-02, FR-CRY-03, FR-CRY-15, FR-MIG-09, NFR-LIFE-03 | Multi-class slots, disjoint-quorum rule |
| P2 | HNDL-to-authority | COVERED | FR-AUT-09, FR-FS-01, FR-FS-12 | Hash-anchored locked stage; PQ authority actions |
| P3 | Stateful-signature (LMS) index reuse | COVERED | FR-SIG-03, FR-SIG-04, FR-TIM-07 | Index reservation, budgets, non-clone custody |
| P4 | Public-key work on every endpoint | COVERED | FR-CRY-03, FR-CRY-04, FR-CRY-17, FR-SIG-01, FR-KEY-01, FR-KEY-10, NFR-MEM-03, NFR-LAT-01, NFR-LAT-02, NFR-LAT-03, NFR-PWR-01 | Verify-only builds, enrolment-once KEM |
| P5 | (not itemised in atlas ed.2) | UNITEMISED | via proxies R1, R4 | Atlas gives only the range; mapped to root-cause R1/R4 proxies |
| P6 | (not itemised in atlas ed.2) | UNITEMISED | via proxies R1, R4 | As P5 |
| P7 | (not itemised in atlas ed.2) | UNITEMISED | via proxies R1, R4 | As P5 |
| P8 | Frozen ROM | PARTIAL | FR-FS-01, FR-FS-03, FR-FS-14 | Locked flash stage where lockable; ANCHOR-WEAK label elsewhere. Residual: SILICON (ROM unchangeable) |
| P9 | Scarce OTP | COVERED | FR-FS-08, NFR-MEM-01, NFR-FLASH-01 | 96 B of slot hashes in locked flash instead of OTP |
| P10 | RAM limits | COVERED | FR-FS-08, FR-FS-15, FR-CRY-10, FR-CRY-12, NFR-MEM-01, NFR-MEM-02, NFR-MEM-03 | Per-primitive budgets and CI gates |
| P11 | Silicon cadence vs asset life | PARTIAL | FR-FS-14, FR-FS-18, FR-CRY-09, NFR-LAT-01, NFR-LAT-04, NFR-PORT-01, NFR-LIFE-01 | Locked stage and updatable second stage sidestep it. Residual: SILICON |
| P12 | Single-format boot chain | COVERED | FR-AUT-09, FR-CRY-01, FR-SIG-08, FR-MIG-09, FR-GOV-01, FR-GOV-02, NFR-API-01, NFR-API-02, NFR-LIFE-03 | Self-describing formats, second stage replaceable, molting |
| P13 | Authority tied to one OEM (R3 cluster) | PARTIAL | FR-OWN-03, FR-OWN-04, FR-OWN-09 | Slot 3, escrow, heartbeat. Residual: CONTRACT |
| P14 | (not itemised in atlas ed.2) | UNITEMISED | via proxies R2, R3 | Between R3 and R2 clusters; mapped to R2/R3 proxies |
| P15 | Validity tied to wall-clock (R2 cluster) | COVERED | FR-FS-11, FR-TIM-01, FR-TIM-02, FR-TIM-04, NFR-OFF-01 | Counters and epochs; offline operation |
| P16 | Never-updatable devices | PARTIAL | FR-FS-03, FR-FS-06, FR-FS-10, FR-FS-14, FR-UPD-09, FR-ENC-01, FR-ENC-06, FR-ENC-09, FR-MIG-06 | Enclave, dated exit, unrescuable-set report. Residual: PHYSICS (no lockable stage) and replacement budget |
| P17 | Public-key handshake cost at endpoint (R4 cluster) | COVERED | FR-CRY-17, FR-KEY-10, FR-PRO-04 | Enrolment-once, gateway-mediated enrolment |
| P18 | Fragmentation / large objects | COVERED | FR-CRY-19, FR-KEY-10, FR-PRO-01, FR-PRO-02 | IKE_INTERMEDIATE, split ClientHello, offline provisioning |
| P19 | Process bus real-time budget | COVERED | FR-KEY-01, FR-KEY-04, FR-PRO-04, NFR-LAT-05, NFR-LAT-06, NFR-INT-01 | Symmetric data path unchanged |
| P20 | Group key distribution | COVERED | FR-KEY-02, FR-KEY-04, FR-KEY-05, FR-PRO-05, NFR-LAT-06 | GDOI-style short epochs, diversified identity |
| P21 | (not itemised in atlas ed.2) | UNITEMISED | via proxies R4, R2 | Between R4 and R2 clusters; mapped to R4/R2 proxies |
| P22 | Catch-up after long offline | COVERED | FR-LC-14, FR-LC-17, FR-KEY-05, FR-KEY-09, FR-TIM-02, FR-TIM-12, NFR-OFF-02 | Catch-up bundles, optional Merkle sets |
| P23 | Orphaned fleets | PARTIAL | FR-FS-02, FR-FS-13, FR-OWN-03, FR-OWN-04, FR-OWN-05, FR-OWN-09 | Slot 3, voucher escrow, heartbeat. Residual: CONTRACT (enforceability E5) |
| P24 | Stale spares | COVERED | FR-LC-13 | Dormant spares, activation at installation |
| P25 | Backups rewind state | COVERED | FR-FS-05, FR-FS-07, FR-ASR-03, NFR-PWR-02 | Non-restorable floor; index uniqueness |
| P26 | Offline revocation | COVERED | FR-FS-11, FR-KEY-09, FR-TIM-05, FR-TIM-11, FR-TIM-12, NFR-OFF-01 | Floor/counter-based revocation via visits |
| P27 | Expiry as authority cliff | COVERED | FR-TIM-01, FR-TIM-04, FR-TIM-10 | No calendar authority; no-expiry encodings |
| P28 | Recertification burden | PARTIAL | FR-KEY-06, FR-UPD-05, FR-ASR-08, NFR-DET-02, NFR-CERT-01, NFR-CERT-02, NFR-CERT-03 | Crypto-only lane and safety-case artefacts. Residual: POLICY (assessor acceptance, E-C1) |
| P29 | Watchdog vs signing latency | COVERED | FR-CRY-04, FR-CRY-07, FR-KEY-06, FR-ASR-09, NFR-DET-01, NFR-DET-02 | No signing on C3; WCET analysis |
| P30 | Fail-safe vs fail-secure | COVERED | FR-FS-06, FR-UPD-17, NFR-SAFE-01 | LKG, fail operational |
| P31 | Responsibility gap | PARTIAL | FR-OWN-04 | Trigger evidence and holdings report. Residual: POLICY/CONTRACT (liability allocation) |
| P32 | Devices cannot state what they trust (R7 cluster) | COVERED | FR-UPD-04, FR-EVD-01, FR-EVD-05, FR-MIG-01 | Signed state reports |
| P33 | No party paid to know (R7 cluster) | PARTIAL | FR-SIG-10, FR-EVD-03, FR-EVD-08, FR-MIG-01 | CBOM and exposure-years supply evidence. Residual: MARKET (incentives) |
| P34 | Progress measured wrongly (R7 cluster) | COVERED | FR-EVD-08, FR-MIG-05 | Exposure-years metric |
| P35 | Incompatible regulatory evidence (R7 cluster) | PARTIAL | FR-EVD-09, FR-EVD-16 | Regime exporter. Residual: POLICY |
| N1 | Classical debug-unlock tokens | COVERED | FR-SIG-12, FR-LC-01, FR-LC-03, FR-LC-04 | UUID-bound PQ debug credentials |
| N2 | Debug certs chain to RoT keys | COVERED | FR-SIG-12, FR-LC-01, FR-LC-03 | Separate issuer, UUID binding |
| N3 | RMA authorisations outlive support | COVERED | FR-LC-01, FR-LC-04, FR-LC-05, FR-LC-06 | Per-device, floor-revocable |
| N4 | RDP L2 permanence tempts weak locks | PARTIAL | FR-LC-01, FR-LC-02, FR-LC-04, FR-LC-05 | Board-swap RMA profile. Residual: SILICON (lock semantics) |
| N5 | Ownership-transfer messages classical | COVERED | FR-AUT-01, FR-AUT-05, FR-LC-01, FR-OWN-01, FR-OWN-08 | PQ/dual-class transfer messages |
| N6 | FDO vouchers classical | COVERED | FR-AUT-01, FR-AUT-05, FR-LC-01, FR-OWN-01, FR-PRO-05 | PQ voucher profile |
| N7 | Voucher holder controls onboarding | PARTIAL | FR-FS-02, FR-FS-13, FR-OWN-02 | Escrow with reference verifier. Residual: CONTRACT |
| N8 | CM key injection | PARTIAL | FR-LC-01, FR-LC-07 | KEM-wrapped per-device injection, co-signed log. Residual: PHYSICS/POLICY (physical line security) |
| N9 | Firmware-key wrap harvestable | COVERED | FR-CRY-17, FR-CRY-18, FR-LC-01 | PQ KEM wrapping |
| N10 | Fleet-shared symmetric key | COVERED | FR-AUT-15, FR-FS-04, FR-LC-07, FR-KEY-02, FR-KEY-04, FR-KEY-07, FR-KEY-08 | Per-device diversification |
| N11 | DICE/IDevID classical identity | COVERED | FR-LC-01, FR-LC-08 | PQ/hash-based identity issuance |
| N12 | Installed TPM/SE cannot gain PQ | OUT_OF_SCOPE | FR-LC-08, FR-EVD-04, FR-ENC-01, FR-MIG-06 | SILICON: installed parts cannot be upgraded by software. Software only reports the set (FR-MIG-06) and offers containment |
| N13 | Patches uninstalled 10+ years | PARTIAL | FR-UPD-01, FR-UPD-11, FR-UPD-12 | Staging, adoption measurement. Residual: POLICY (operator behaviour) |
| N14 | Windows collide with emergencies | PARTIAL | FR-UPD-01, FR-UPD-02, FR-UPD-03, FR-UPD-10 | Dormant staging, window model. Residual: PHYSICS (plant outage constraints) |
| N15 | Advisories without patch | PARTIAL | FR-UPD-12 | Compensating-control bundles. Residual: MARKET (vendor fixes) |
| N16 | Licence signatures forgeable | COVERED | FR-LC-01, FR-LC-09 | PQ per-device licence tokens |
| N17 | Relay settings / SIS logic unsigned | COVERED | FR-AUT-01, FR-SIG-06, FR-LC-01 | Workstation quorum, device/gateway verification |
| N18 | Workstations hold signing authority | PARTIAL | FR-AUT-11, FR-AUT-14, FR-SIG-01, FR-SIG-06, FR-SIG-11, FR-LC-01, FR-OWN-07 | Quorum, dual control. Residual: POLICY (host hardening and patching) |
| N19 | Vendor remote-access portals | PARTIAL | FR-LC-01, FR-LC-10, FR-OWN-07, FR-ENC-08 | Quorum-gated sessions, disable modes. Residual: POLICY |
| N20 | No fix path for first-stage bug | PARTIAL | FR-FS-06, FR-FS-07, FR-FS-08, FR-FS-09, FR-FS-10, FR-FS-16, FR-ASR-01, FR-ASR-03, FR-ASR-07, FR-ASR-10, NFR-MEM-01, NFR-MEM-04, NFR-PWR-02, NFR-PORT-01, NFR-PORT-03, NFR-CERT-03, NFR-SEC-01 | Minimality, verification, dual implementation. Residual: PHYSICS/information-theoretic (no fix path by design) |
| N21 | Flash lock vs physical attacker | PARTIAL | FR-FS-03, FR-FS-04, FR-CRY-16, FR-LC-02, FR-ASR-04 | Public-only stage, per-device keys, hardware register. Residual: PHYSICS/SILICON |
| N22 | Floor burn against owner | COVERED | FR-AUT-01, FR-AUT-05, FR-AUT-06, FR-AUT-07, FR-AUT-08, FR-FS-05, FR-FS-12, FR-FS-17, FR-UPD-14 | Cross-slot floor rule |
| N23 | Spare at index k cannot boot k+3 | COVERED | FR-LC-13, FR-LC-14, NFR-OFF-02 | Catch-up bundles |
| N24 | Composite signatures EUF-CMA only | COVERED | FR-CRY-01, FR-CRY-02, FR-CRY-08 | Malleability class, no dedupe by bytes |
| N25 | Draft OIDs orphan devices | COVERED | FR-CRY-01, FR-SIG-08, FR-GOV-01, FR-GOV-02, NFR-API-01 | Library-owned ids, alias table |
| N26 | PQ accelerators partially masked | PARTIAL | FR-FS-09, FR-CRY-05, FR-CRY-06, FR-CRY-07, FR-CRY-16, FR-LC-02, FR-ASR-04 | Hardware evidence register, fault hooks. Residual: SILICON |
| N27 | Inconsistent benchmarks | COVERED | FR-FS-15, FR-CRY-09, FR-CRY-10, FR-CRY-11, FR-CRY-12, FR-EVD-15, FR-MIG-07, FR-MIG-08, FR-ASR-02, FR-ASR-05, NFR-MEM-02, NFR-LAT-01 | Neutral harness, parameter-attached figures |
| N28 | CRA reporting covers legacy, fix duty does not | PARTIAL | FR-EVD-09 | Evidence export. Residual: POLICY |
| N29 | 5-year support vs 20-40-year assets | PARTIAL | FR-OWN-05, FR-EVD-09, FR-MIG-05 | Supersedure, exposure planning. Residual: POLICY |
| N30 | India 2029 de facto enclaves | PARTIAL | FR-EVD-09, FR-ENC-02, FR-ENC-03, FR-ENC-07, FR-ENC-09 | Enclave profile, exit clocks. Residual: POLICY (standardisation) |
| N31 | Each regime defines done differently | PARTIAL | FR-SIG-08, FR-EVD-09, FR-MIG-04, FR-PRO-03, FR-PRO-05, NFR-INT-01 | Explicit per-regime done definitions. Residual: POLICY |
| N32 | Owners cannot verify OEM claims | PARTIAL | FR-SIG-10, FR-EVD-15, FR-MIG-07, FR-ASR-02, FR-ASR-06, NFR-DET-03 | Conformance suite and claims register. Residual: POLICY (accredited labs) |
| N33 | Downtime cost dwarfs labour | OUT_OF_SCOPE | FR-UPD-02, FR-UPD-10 | MARKET/PHYSICS: cost of plant downtime is not reducible by software; staging only aligns to existing windows |
| N34 | No public substation downtime benchmark | OUT_OF_SCOPE | FR-UPD-11 | DATA/POLICY: needs operator-supplied data; read-only metrics mode (FR-UPD-11) only enables collection |
| N35 | Insurers lack crypto-state loss data | RESEARCH | FR-EVD-08, FR-EVD-16 | Attestation-priced insurance demoted to research in atlas; MAY export only |
| N36 | Refurbished gear carries identity | COVERED | FR-LC-11, FR-LC-12, FR-LC-15 | Intake wipe, receipts |
| N37 | Decommissioned certs remain trusted | COVERED | FR-LC-11, FR-LC-15 | Trust-list removal on receipt |
| N38 | OPC UA AutoAccept / None | PARTIAL | FR-EVD-05, FR-EVD-06, FR-PRO-03 | Linter, passive inference. Residual: POLICY (operator configuration) |
| N39 | Restored archives bring back old indices | COVERED | FR-FS-05 | Non-restorable floor |
| N40 | Merkle future keys secret for 20+ years | RESEARCH | FR-LC-17 | Split custody (I-11) unvalidated; MAY requirement only |
| N41 | Bankrupt signer freezes fleet | PARTIAL | FR-AUT-04, FR-AUT-10, FR-FS-13, FR-SIG-02, FR-OWN-03, FR-GOV-04, NFR-LIFE-02 | Slot 3, liveness analysis. Residual: CONTRACT |
| N42 | Unauthenticated PTP | COVERED | FR-TIM-03, FR-TIM-08 | Not used for policy; zeitgeber fusion |
| N43 | KDC/gateways fleet-wide targets | PARTIAL | FR-AUT-11, FR-AUT-15, FR-KEY-02, FR-KEY-03, FR-KEY-08, FR-ENC-03, FR-ENC-04, FR-ENC-05 | Zoning, replication, sectoring. Residual: PHYSICS (concentration inherent) |
| N44 | Agility enables downgrade | COVERED | FR-AUT-07, FR-AUT-13, FR-CRY-13, FR-CRY-14, FR-PRO-01 | Minimum-suite enforcement, signed agility config |
| N45 | Strict pinning breaks interop | PARTIAL | FR-AUT-13, FR-CRY-13, FR-PRO-01 | Declarable fallback with expiry. Residual: POLICY (peer capability) |
| N46 | Taps are privileged positions | COVERED | FR-AUT-15, FR-KEY-03, FR-EVD-07, FR-EVD-13, FR-ENC-05 | Read-only, keyless taps |
| N47 | AI assistants bypass quorums | PARTIAL | FR-AUT-11, FR-AUT-14, FR-SIG-06 | Human-attributable signature rule. Residual: POLICY (token custody) |
| N48 | Crypto bundled with recertification | PARTIAL | FR-UPD-05, FR-UPD-13, FR-ASR-08, NFR-CERT-01, NFR-CERT-02 | Crypto-only lane. Residual: POLICY (assessors) |
| N49 | Mid-support sunsets unpriced | OUT_OF_SCOPE | FR-AUT-12, FR-OWN-04, FR-OWN-05, FR-ENC-09 | CONTRACT: pricing is commercial; software supplies supersedure and exit evidence only |
| N50 | Devices cannot state trusted keys | COVERED | FR-UPD-04, FR-EVD-01, FR-EVD-02, FR-EVD-03, FR-EVD-04, FR-EVD-05, FR-MIG-02 | State reports, CBOM |
| N51 | LMS state not portable between HSMs | PARTIAL | FR-SIG-03, FR-SIG-05 | Documented re-rooting path. Residual: SILICON/STANDARD (HSM export) |
| N52 | M&A omits authority diligence | PARTIAL | FR-OWN-06, FR-OWN-07 | Holdings report. Residual: POLICY (diligence practice) |
| N53 | Spare brokers resell stale roots | COVERED | FR-LC-11, FR-LC-12, FR-LC-13 | Dormant spares, receipts |
| N54 | Zero-knowledge-only resource estimates | OUT_OF_SCOPE | FR-CRY-15 | PHYSICS/SCIENCE: independent verification of quantum estimates is outside software; policy accepts declared horizons |
| N55 | OT silicon lags | PARTIAL | FR-FS-14, FR-FS-18, FR-CRY-09, FR-LC-02, FR-MIG-06, FR-MIG-07, NFR-LAT-04, NFR-PORT-01, NFR-PORT-02 | Locked-stage path on existing parts, procurement profile. Residual: SILICON/MARKET |
| N56 | Counter and time overflow | COVERED | FR-SIG-04, FR-TIM-06, FR-TIM-07, NFR-FLASH-02, NFR-OFF-02, NFR-LIFE-01 | Wrap-safe formats, capacity register |
| N57 | Agility atrophy | COVERED | FR-CRY-13, FR-UPD-15 | Slot drills |
| N58 | Hash waist | COVERED | FR-AUT-02, FR-AUT-03, FR-FS-10, FR-FS-12, FR-CRY-02, FR-CRY-15, FR-SIG-02, FR-ASR-01 | Assumption table, disjoint-quorum compiler |
| N59 | Governed natural clocks | COVERED | FR-TIM-03, FR-TIM-09 | Plausibility-only use |
| N60 | Evidence/reader obsolescence | COVERED | FR-OWN-02, FR-EVD-10, FR-EVD-11, FR-EVD-14, FR-GOV-01, FR-GOV-03, NFR-API-02 | Evidence renewal, archived verifiers |
| N61 | Skill extinction | PARTIAL | FR-AUT-12, FR-SIG-07, FR-UPD-13, FR-UPD-16 | Rehearsal packages. Residual: POLICY (organisational discipline) |
| N62 | Security updates as outages | COVERED | FR-UPD-06, FR-UPD-07, FR-UPD-13, FR-UPD-17, NFR-OPS-02 | Cohorts, halt, persisters |
| N63 | Infrastructure sunsets | PARTIAL | FR-ENC-01, FR-ENC-02, NFR-LIFE-02 | Offline-first design, enclave exits. Residual: PHYSICS (external networks) |
| N64 | Untested rollover automation | COVERED | FR-UPD-08, FR-UPD-15 | Drills, spindle gating |
| N65 | Jurisdictional limits on remote operation | PARTIAL | FR-LC-10, FR-ENC-08 | Configurable modes. Residual: POLICY (law) |
| N66 | Defence autoimmunity | PARTIAL | FR-AUT-08, FR-AUT-12, FR-EVD-07, NFR-SAFE-01 | Thymic tests, fail operational. Residual: PHYSICS (base rate) |
| N67 | Competing successor authorities | COVERED | FR-AUT-04, FR-AUT-10, FR-OWN-06 | Objections, tie-break |
| N68 | Classical transparency layers | COVERED | FR-SIG-09, FR-EVD-11, FR-EVD-12 | PQ cosignatures |
| N69 | Attackers move to weakest channel | PARTIAL | FR-MIG-03, FR-MIG-04 | Six-chain completeness gate. Residual: POLICY (actually closing old channels) |
| N70 | Physical defeat of old MCU protections | PARTIAL | FR-FS-04, FR-CRY-16, FR-LC-02, FR-EVD-03, FR-ASR-04 | Blast-radius bound, evidence register. Residual: SILICON/PHYSICS |
| N71 | Compiler-introduced side channels | COVERED | FR-FS-09, FR-CRY-05, FR-CRY-06, FR-CRY-11, FR-SIG-10, FR-ASR-10, FR-ASR-11, NFR-MEM-04, NFR-DET-01, NFR-DET-03, NFR-PORT-02, NFR-PORT-03, NFR-SEC-01 | Binary-level checks |
| N72 | Stragglers after irreversible steps | PARTIAL | FR-UPD-08, FR-UPD-09 | Straggler registry. Residual: PHYSICS/POLICY (some devices unreachable) |
| N73 | Folklore as evidence | COVERED | FR-CRY-10, FR-MIG-08, FR-ASR-05, FR-ASR-06, FR-GOV-05, NFR-LAT-02, NFR-DOC-01 | Claims register, evidence labels |
| R1 | Algorithm-bound immutable anchors | PARTIAL | FR-AUT-02, FR-AUT-03, FR-AUT-09, FR-FS-01, FR-FS-03, FR-FS-10, FR-FS-14, FR-MIG-09, FR-ASR-07, NFR-LIFE-03 | Locked stage; residual SILICON for non-lockable parts |
| R2 | Validity tied to wall-clock time | COVERED | FR-FS-11, FR-TIM-01, FR-TIM-02, FR-TIM-04, FR-TIM-05, FR-TIM-10, FR-TIM-11, NFR-OFF-01 | Epoch/counter design |
| R3 | Authority tied to one organisation | PARTIAL | FR-AUT-01, FR-AUT-04, FR-AUT-10, FR-FS-02, FR-FS-13, FR-OWN-05, FR-OWN-09, FR-GOV-04, NFR-LIFE-02 | Slot 3, escrow; residual CONTRACT |
| R4 | Public-key work at every endpoint | COVERED | FR-AUT-15, FR-CRY-03, FR-CRY-04, FR-CRY-17, FR-CRY-19, FR-SIG-01, FR-KEY-01, FR-KEY-02, FR-KEY-07, FR-KEY-10, FR-ENC-07, FR-PRO-04, NFR-LAT-05, NFR-PWR-01 | Class model, symmetric fabric |
| R5 | Crypto co-located with safety | PARTIAL | FR-FS-06, FR-CRY-04, FR-KEY-06, FR-UPD-05, FR-UPD-17, FR-ASR-08, FR-ASR-09, NFR-DET-02, NFR-CERT-01, NFR-CERT-02, NFR-SAFE-01 | Separation and crypto-only lane; residual POLICY (certification) |
| R6 | Copyable or rewindable state | COVERED | FR-AUT-06, FR-FS-05, FR-FS-07, FR-FS-16, FR-FS-17, FR-SIG-01, FR-SIG-03, FR-SIG-05, FR-UPD-14, FR-ASR-03, NFR-FLASH-01, NFR-FLASH-02 | Non-restorable state, one-time uniqueness |
| R7 | Invisible state, misaligned incentives | PARTIAL | FR-UPD-04, FR-EVD-01, FR-EVD-03, FR-EVD-07, FR-EVD-08, FR-MIG-01, FR-MIG-02, FR-MIG-03, FR-MIG-05, NFR-OPS-01 | Evidence and metrics; residual MARKET |
| R8 | Change does not get installed | PARTIAL | FR-UPD-01, FR-UPD-02, FR-UPD-06, FR-UPD-10, NFR-OPS-02 | Staging; residual POLICY/operations |
| R9 | Uninventoried authorisation paths | PARTIAL | FR-AUT-01, FR-AUT-05, FR-AUT-13, FR-SIG-06, FR-SIG-11, FR-LC-01, FR-LC-04, FR-LC-05, FR-LC-06, FR-LC-07, FR-LC-10, FR-LC-16, FR-MIG-04, FR-ASR-11 | Surface map and closures; residual POLICY/SILICON |
| R10 | Unexercised capabilities decay | COVERED | FR-AUT-09, FR-SIG-07, FR-UPD-10, FR-UPD-15, FR-UPD-16, FR-EVD-14, FR-ASR-01, FR-GOV-03 | Drills, rehearsal, evidence of exercise |
| R11 | The ground moves | PARTIAL | FR-TIM-06, FR-TIM-07, NFR-LIFE-01 | Capacity checks and offline design; residual PHYSICS/POLICY |

## R.5.3 Idea coverage (atlas Part 18)

| Idea | Requirements |
|---|---|
| I-1 | FR-LC-01 |
| I-2 | FR-AUT-05, FR-AUT-06, FR-LC-16 |
| I-3 | FR-LC-16, FR-UPD-03 |
| I-4 | FR-AUT-03 |
| I-5 | FR-LC-13 |
| I-6 | FR-LC-11 |
| I-7 | FR-UPD-05 |
| I-8 | FR-UPD-03 |
| I-9 | FR-ENC-02 |
| I-10 | FR-ASR-02 |
| I-11 | FR-LC-17 |
| I-12 | FR-SIG-08, FR-EVD-02, NFR-OPS-01 |
| I-13 | FR-UPD-15 |
| I-14 | FR-AUT-08 |
| I-15 | FR-AUT-07 |
| I-16 | FR-AUT-09, FR-SIG-02 |
| I-17 | FR-OWN-03 |
| I-18 | FR-AUT-10 |
| I-19 | FR-AUT-03 |
| I-20 | FR-MIG-03 |
| I-21 | FR-EVD-08 |
| I-22 | FR-AUT-12 |
| I-23 | FR-TIM-03, FR-TIM-12 |
| I-24 | FR-TIM-09 |
| I-25 | FR-TIM-09 |
| I-26 | FR-TIM-13 |
| I-27 | FR-UPD-08 |
| I-28 | FR-KEY-08 |
| I-29 | FR-EVD-10 |
| I-30 | FR-UPD-16 |
| I-31 | FR-KEY-09 |
| I-32 | FR-ENC-06 |
| I-33 | FR-UPD-07 |
| I-34 | FR-TIM-05 |

# R.6 Capability list (input to module architects)

A capability area groups requirements that a downstream stream can turn into one or more modules. Counts are computed from the requirement list.

| Area | Capability | Requirement groups | #Req (MUST) | Scope |
|---|---|---|---|---|
| CA-01 | Authority policy and quorum engine | FR-AUT | 15 (11) | Policy model, assumption table, disjoint-quorum compiler, graded authority, molting, successor arbitration |
| CA-02 | Continuity first stage | FR-FS | 18 (14) | Locked verifier, slots, floor, journal, LKG, formal model |
| CA-03 | Crypto abstraction and implementations | FR-CRY | 19 (13) | Algorithm registry, PQ verify/KEM, hash HAL, constant-time, hybrid/downgrade policy |
| CA-04 | Signing infrastructure and artefact formats | FR-SIG | 12 (9) | HSM quorum service, stateful-key custody, manifests, workstation quorum, reproducible releases |
| CA-05 | Lifecycle, side doors and provisioning | FR-LC | 17 (13) | Surface map, hardware evidence register, debug/lifecycle, factory injection, decommissioning, catch-up |
| CA-06 | Ownership and succession | FR-OWN | 9 (6) | FDO-PQ vouchers, escrow, heartbeat, supersedure, swarming |
| CA-07 | Key distribution and symmetric fabric | FR-KEY | 10 (5) | Enrolment, KDC, diversification, group keys, safety/crypto separation |
| CA-08 | Update, staging and rollout orchestration | FR-UPD | 17 (10) | Bundles, dormant staging, cohorts, persisters, spindle gating, drills |
| CA-09 | Time, epochs and counters | FR-TIM | 13 (9) | Epoch model, zeitgeber fusion, senescence, capacity register |
| CA-10 | Evidence and observability | FR-EVD | 16 (9) | State reports, CBOM, attestation, passive inference, exposure-years, evidence renewal, witnesses |
| CA-11 | Enclave and legacy containment | FR-ENC | 9 (5) | Gateway profile, exit clocks, sectoring, jurisdiction modes |
| CA-12 | Fleet planning and migration | FR-MIG | 9 (6) | Inventory, trust graph, ordering, unrescuable set, procurement profiles, models |
| CA-13 | Assurance and verification | FR-ASR | 11 (9) | Formal models, conformance suite, power-loss harness, fuzzing, claims register |
| CA-14 | Governance and format stewardship | FR-GOV | 5 (3) | Format versioning, registries, archives, licence and governance |
| CA-15 | Protocol profiles | FR-PRO | 5 (3) | TLS/IKE/OPC UA/field-bus key-delivery profiles, standards contributions |
| CA-16 | Non-functional envelope | NFR | 36 (29) | Budgets, determinism, portability, lifetime, certification-friendliness |


**Cross-cutting rules for architects [I].**
1. CA-02 (first stage) and CA-01 (policy) are the only capabilities that are germline: anything that can live in CA-03 or above SHALL (FR-FS-08).
2. CA-03 (crypto) is shared by device and host builds; signing symbols compile only into host profiles (FR-CRY-04).
3. CA-12 (assurance) is not optional tooling: it carries SP-01, SP-03 and SP-20 evidence.
4. Every capability exposes a stable, versioned format boundary (FR-GOV-01) so modules can be replaced over decades.


# R.7 Explicit non-goals

The baseline deliberately does not require the following. Each is tied to a rejection in the atlas or to the BRIEF.

| # | Non-goal | Reason | Atlas basis |
|---|---|---|---|
| NG-1 | A product, brand, dashboard or SaaS | The mission is libraries, abstractions, protocols, data models, verification and tooling | BRIEF |
| NG-2 | New mask ROM or a kernel licensed into silicon | Demoted: locked-flash first stages ship today | Part 0 finding 2; correction #14 |
| NG-3 | A neutral custodian utility, threshold ML-DSA succession, a time-free validity product, sector root-of-roots | Demoted to research or paper-only | Part 4.4 tier 4; Part 13 verdict |
| NG-4 | Per-frame public-key authentication on the process bus | Infeasible in 208-250 us for any scheme | Part 2.5 |
| NG-5 | Cryptographic rescue of the unrescuable set | Information-theoretic limit; only presence, containment or replacement helps | Part 3.4#5 |
| NG-6 | Detecting withheld updates without an external freshness signal | Freeze limit | Part 3.4#1 |
| NG-7 | Preventing a colluding full quorum | Only detect and bound | Part 3.4#3 |
| NG-8 | Physical or invasive attack procedures, fault-injection recipes, or parameters | Safety rule; the project exposes hooks for independent labs only | BRIEF rule 3; FR-ASR-04 |
| NG-9 | Defeating a local physical attacker on every part | Depends on the part; design bounds harm to one device | Part 8.1, 8.3 |
| NG-10 | Replacing IEC 62351-6 or field-bus frame formats | Data path stays as is | NFR-INT-01 |
| NG-11 | Dynamically adaptive behaviour inside C3 | Safety cases need predictability; only floor advances and policy tightening are adaptive | Part 12.3 |
| NG-12 | Adopting PUFs as stand-alone authentication, or DNA/glass storage media | PUFs only as key derivation; medium is not the binding constraint | Parts 8.6-8.7 |
| NG-13 | Pricing, insurance products, legal liability allocation | Commercial and legal; software provides evidence | N35, N49, P31 |
| NG-14 | Setting national policy or accrediting labs | Policy and institutions | N30, N32 |
| NG-15 | General IT PQC migration (web, email, PKI for people) | Scope is OT and embedded | Mission |
| NG-16 | Negative-selection anomaly detection copied from immunology | Underperforms in evidence; only structural patterns are borrowed | Part 5.8 #1 |
| NG-17 | Choosing winners among HSM vendors or silicon vendors | Vendor-neutral | Mission |


# R.8 Open questions and notes on the atlas

1. **P5, P6, P7, P14, P21 are never named** in the 2nd edition; only the range P1-P35 and some cluster mentions exist. Ten more (P13, P15, P17, P32-P35 and others) are named only by root-cause cluster. The matrix therefore maps them by cluster (RD-5). Action: obtain the original P-list.
2. The atlas's 10.3 phrase "pairwise disjoint in at least two members" is imprecise for keys with several assumptions; SP-01 restates it as a hitting-set condition (RD-2).
3. ML-DSA-44 signing stack: 44.8 KB vs 8.4-8.9 KB remains unresolved (correction #20); no requirement fixes a figure, NFR-MEM-02 defers to E-A2.
4. Enforceability of trigger-based escrow release (I-17, E5) is a legal question; FR-OWN-04 keeps it off-device so the software does not depend on the answer.
5. FR-EVD-01 requires signed reports from signing-capable devices, yet RD-1 forbids signing on controllers; the reconciling mechanism (e.g. hash-based one-time report keys or gateway witness) is for the architecture stream.
6. Figures in R.4.0 reuse atlas numbers and were not re-measured on hardware.

---

<!-- Appendix B -->
# APPENDIX B

# STREAM A: Overall system architecture

Scope: first-principles architecture of one modular, extensible, open-source library ecosystem for OT / embedded post-quantum (PQ) authority and update security. No project name is used; the placeholder C prefix `ac_` ("authority core") and Rust crate prefix `ac-` are descriptive and replaceable.

Evidence labels follow the brief: [F] [2nd] [V] [D] [C] [E] [I] [H] [S]. Scratch code that produced every [C] number below is in `/home/claude/atlas2/blueprint/code/A/` (`matrix.py`, `quorum.py`, `ac_layouts.h` + `chk.c`, `cbor_size.py`). Layout sizes were compiled with `gcc -std=c11` and `_Static_assert`; they are measured, not estimated.

Web checks made this session (all others are atlas-derived or unverified):
- NIST announced an initial public draft of SP 800-230 (additional SLH-DSA parameter sets for limited-signature use) in April 2026 (nist.gov and csrc.nist.gov news pages in search results). Still a draft. [F, draft]
- The IETF COSE ML-DSA draft (`draft-ietf-cose-dilithium`) had reached revision -11, and an SLH-DSA COSE draft (`draft-ietf-cose-sphincs-plus-06`) existed, in search results. Neither is verified as an RFC here. [2nd]
- IETF SUIT manifest and architecture documents exist (SUIT drafts and RFC 9019 JSON seen in search results). Exact RFC numbers other than 9019 are unverified. [2nd]
- Ferrocene (qualified Rust toolchain) exists and is marketed for safety certification (ferrous-systems.com and the GitHub page in results). Which standards and levels it is qualified for was not read here: unverified.
- Kani is used for Rust standard-library verification (a `verify-rust-std` repository appeared in results). Suitability for this project is [I].

---

## A.0 Summary of the architecture in one page

**The architecture is an hourglass whose waist is a pure, byte-oriented "authority transition" interface, with a doubled, tiny, no-dependency core under it and pluggable adapters on both sides.** [H, selected in A.1]

1. **Core.** A deterministic function `step(state, message) -> (state', effects)`. It has no I/O, no allocation, no clock, no libc and no crypto code of its own. It owns exactly four things: the authority record, the key-hash slots, the floor/epoch counters and the disjoint-quorum rule. It is the only code that decides an irreversible change. It exists in two builds from one source: `core-min` (locked first stage, about 3 KB [E]) and `core-full` (updatable second stage, policy and staging).
2. **Waist.** Three narrow, versioned, language-independent surfaces, all built from bytes and fixed little-endian records: **W1** `ac_step` (messages in, intents out), **W2** the crypto provider table, **W3** the platform table (non-volatile storage, monotonic counters, entropy, a *hint* clock). Everything above (formats, protocols, tools) and below (silicon, RTOS, HSM) talks to the core only through these.
3. **Key invariants made structural** (each is a compile-time or load-time check, not a convention):
   - *Only the locked stage mutates authority.* A compromised second stage cannot burn a floor or replace a slot; it can only stage a proposal that the locked stage re-verifies at next reset.
   - *Single-assumption safety.* An irreversible action needs signatures from at least two members whose assumption sets are pairwise disjoint, and **each of those members must be verified in a layer whose own authenticity does not depend on another member** (new "verification-locality rule", A.1.5, a refinement of atlas 10.3).
   - *Policy can only tighten.* Signed policy documents are data that may narrow what the compiled core permits and can never widen it.
4. **Two encodings, one meaning.** Device-resident and locked-stage records are fixed-layout little-endian structs (parsable in a few dozen lines, no ambiguity). Everything exchanged or archived (policy, bundle manifests, state reports) is deterministic CBOR in COSE envelopes, with the locked-stage-relevant part embedded as a fixed binary projection (`ac_tx_t`) whose digest the CBOR commits to.
5. **Extension without touching the core.** Algorithms, protocols, hardware ports and policy rules enter only through registries, provider tables and signed policy data. Stability tiers T0-T3 with a decades-long read-compatibility promise for T0 formats.

Atlas claim that needs correction (detail in A.1.5 and A.10): the atlas slot set {ML-DSA, SLH-DSA-SHAKE, LMS-SHA-256} with quorum {ML-DSA, LMS} is single-assumption-safe only if ML-DSA is verified in the locked stage. When ML-DSA is verified in the second stage, which the atlas HA-1 describes, a SHA-256 break can forge the LMS signature, and through it the second stage, and through it the ML-DSA verdict. This is [I], inference from the layering; it should be modelled in TLA+ (A.10).

---

## A.1 Competing architectures, criteria, scoring and selection

### A.1.1 The seven candidates

Candidates A1-A6 were defined to be genuinely different in where authority semantics live and where the trust boundary sits. S is the refined winner and is scored separately (and flagged as benefitting from hindsight).

| ID | Architecture | Where authority semantics live | What is the "narrow part" | Closest prior art (label) |
|---|---|---|---|---|
| A1 | **Monolithic PQ boot + update stack**: extend a bootloader with PQ verification, A/B slots, rollback counter, one codebase, configuration by Kconfig | In the bootloader's update logic, implicit | None; the bootloader is the product | MCUboot, wolfBoot, Nordic NSIB, ST OEMiRoT (atlas 11.1 prior art [F]) |
| A2 | **Policy-engine-centric**: an interpreter (Cedar/OPA/Rego-like, or signed bytecode) on every device decides everything, including boot and updates | In signed policy programs | The policy language | OPA/Cedar style authorisation [I]; X.509 name constraints as a degenerate case |
| A3 | **Authority-ledger state-machine core + pluggable adapters**: a small deterministic state machine owns authority, slots, floors, epochs and an append-only transition ledger; adapters feed it events | In the state machine | The transition function | Certificate-transparency-style logs, TUF root rotation as a state machine [I] |
| A4 | **Layered hourglass with a thin verification waist**: waist is `verify(manifest, anchor) -> ok`; authority semantics, policy and floors are left to layers above | In layers above the waist | The verify interface | TUF/SUIT-style "verify metadata" interfaces, X.509 path validation [I] |
| A5 | **Microkernel / capability style**: partitions with capabilities for "sign", "burn counter", "unlock debug"; authority is capability possession and delegation | In the capability graph | The kernel and capability ABI | TF-M/PSA partitions, seL4-style capabilities [I] |
| A6 | **Protocol-gateway-centric**: leave devices alone, terminate PQ at gateways/enclaves, sign and manage centrally | In gateway and fleet services | The gateway | Atlas 11.6 containment generalised |
| S | **Synthesis**: A3's authority core placed inside A4's hourglass layering, with A5-style isolation as an optional deployment profile and A6 reserved for C0/C1 | Core + signed policy that may only tighten | The waist: `ac_step` + provider and platform tables | New combination [H] |

### A.1.2 Criteria and weights

Weights are a judgement [H], justified from the atlas: longevity and security dominate because the atlas's central finding is that long-lived devices cannot safely accept change (Part 0; R1, R10, R11).

| Criterion | Weight | Why this weight | What a 5 means |
|---|---|---|---|
| Security (single-assumption safety, blast radius, side-door closure R9) | 18 | Atlas Part 0: the exposure is authority | Authority actions structurally need disjoint quorums; one compromised layer cannot change authority |
| TCB size | 12 | Immutable code cannot be fixed (N20) | Irreversible-decision code is under ~5 KB and formally checkable |
| Flash / RAM | 8 | C1/C2 parts; first stage about 13 KB in the atlas | Fits the MV-1 budget with margin |
| Certifiability (IEC 61508/62443/CC-style evidence) | 10 | R5, recertification cost (N48) | Small, deterministic, traceable, crypto separable from safety code |
| Extensibility | 10 | New algorithms/protocols appear every few years | New algorithm without touching decision code |
| Portability | 8 | 25-40 year, multi-vendor fleets | Same core on bare metal, RTOS, Linux, HSM firmware |
| Migration cost (for adopters from today's stacks) | 8 | R8: change does not get installed | Adoptable incrementally on top of MCUboot/SUIT/TUF-like stacks |
| Decades-longevity | 18 | R10, R11; 25-40 years assets | Frozen formats, read-compat promise, no dependency on any institution or toolchain |
| Developer comprehension | 8 | Maintainers rotate over decades | A new engineer can read the decision code in a day |
| **Total** | **100** | | |

### A.1.3 Scores (1-5, higher is better) and rationale

All cell scores are [H] judgements; the reasoning for the cells that decide the outcome is given after the table.

| Criterion (weight) | A1 | A2 | A3 | A4 | A5 | A6 | S |
|---|---|---|---|---|---|---|---|
| Security (18) | 3 | 2 | 5 | 4 | 4 | 2 | 5 |
| TCB size (12) | 2 | 1 | 4 | 4 | 2 | 3 | 4 |
| Flash/RAM (8) | 4 | 2 | 4 | 5 | 2 | 5 | 4 |
| Certifiability (10) | 2 | 2 | 4 | 4 | 3 | 3 | 5 |
| Extensibility (10) | 2 | 5 | 4 | 4 | 3 | 3 | 5 |
| Portability (8) | 3 | 3 | 4 | 5 | 2 | 4 | 5 |
| Migration cost (8) | 4 | 2 | 3 | 4 | 2 | 5 | 3 |
| Longevity (18) | 2 | 3 | 5 | 4 | 3 | 2 | 5 |
| Comprehension (8) | 4 | 2 | 3 | 4 | 2 | 4 | 3 |
| **Weighted score [C]** | **2.74** | **2.44** | **4.20** | **4.16** | **2.74** | **3.12** | **4.48** |

Rationale for the cells that matter:
- **A1 security 3, longevity 2.** Authority logic is interleaved with image handling, so a bug in image parsing sits in the same trust domain as floor burning; the algorithm set is a compile-time property, which is exactly R1 re-created in a bootloader. Strength: lowest migration cost (4).
- **A2 TCB 1, certifiability 2.** An interpreter on the irreversible path is a large, hard-to-verify TCB; a policy bug is a fleet-wide authority bug. Strength: extensibility 5. Rejected as the *core*, kept as *data* (S: a non-Turing-complete decision table that can only tighten).
- **A3 vs A4 (the real contest).** A3 gets security 5 and longevity 5 because the authority semantics (floor, quorum, PAM rule, molting) are inside a small checkable machine. A4 scores better on portability, flash and migration because a verify-only waist is what existing stacks already have, but it leaves the authority semantics to every integrator, which is where atlas R9 and R10 live (N1-N8 side doors; N57 agility atrophy). A4 with no authority semantics repeats TUF's strength (metadata verification) without the atlas's laws 2, 5, 9 and 12.
- **A5 TCB 2, flash 2, portability 2.** It requires MPU/TrustZone-class isolation that C0-C2 parts often lack, and a capability kernel is itself a large TCB. Retained as an *optional deployment profile* (crypto partition on C3, KDC on C4).
- **A6 security 2, longevity 2.** It does not fix R1 for any updatable device and "temporary" enclaves become permanent (atlas 11.6, 11.10). Retained for C0/C1 only, with a dated exit.
- **S.** A3's core with A4's layering. Certifiability and extensibility rise to 5 because (a) the core is a pure function with a closed input alphabet and (b) all growth goes through registries and data. Migration 3 and comprehension 3 are deliberately not raised: S requires adopters to put an authority core under their existing updater, and a reader must learn the model (slots, floors, quorums) before reading the code.

### A.1.4 Sensitivity analysis [C]

| Test | Result |
|---|---|
| Weight sets: security-first (30/15/5/10/5/5/5/20/5), certification-first, ecosystem-first, uniform | S ranks first in all four (4.60, 4.47, 4.40, 4.33); A3 or A4 second |
| Cost/migration-first (migration 25, flash 15, comprehension 10, security 10) | **A4 wins (4.25) over S (4.07)** |
| One-at-a-time: each weight scaled by 0.5 and 1.5 (18 runs) | S first in 18 of 18 |
| 100,000 random weight vectors (symmetric Dirichlet) | S wins 65.6%, A4 33.7%, A6 0.7%, all others 0% |
| Same, excluding S | A4 80.7%, A3 18.5%, A6 0.7% |
| 20,000 runs perturbing every cell by -1/0/0/+1 | S 60.8%, A4 21.6%, A3 17.7% |
| Pessimistic S (migration 2, comprehension 2) | S 4.32 vs A4 4.16: still ahead |

Reading: S's lead is robust to weights, but **A4 is a strong, cheaper competitor and wins when adoption cost dominates**. That tells us how to sequence delivery: ship the A4 layering first (A.7 milestones), and let the authority core be the addition that adopters opt into per device class. A3 alone never wins over A4 plus A3, so the synthesis is not an artefact of tuning. Limitation: all scores are judgements by one reviewer; the experiment that would falsify them is an adopter study (E-A1 style) comparing integration effort of S against A4 on two real bootloaders [H].

### A.1.5 Decision D-A1: select S, with two refinements the scoring exposed

**DECISION.** Adopt S: hourglass layering, waist = `ac_step` plus the provider and platform tables, a doubled core that is split into `core-min` (locked) and `core-full` (updatable). Refinements:

1. **Only the locked stage mutates authority** ("single mutator rule"). `core-full` can validate, stage and propose; the irreversible commit (journal append, counter burn, slot state change) is done by `core-min` at next reset after it re-verifies the signatures itself.
2. **Verification-locality rule.** For every irreversible action the policy names a quorum with at least `d >= 2` pairwise assumption-disjoint members, and every one of those members must have its signature verified by code that is authenticated *without* relying on any other member's assumption. Concretely in MV-1/HA-1 this limits irreversible quorums to classes the locked stage can verify (hash-based: LMS-SHA-256 / SLH-DSA-SHA2 for the SHA-2 waist; SLH-DSA-SHAKE / XMSS-SHAKE for the Keccak waist). ML-DSA, verified in `stage2`, may be a *third*, additive factor and the primary class for image acceptance and non-irreversible actions, but it cannot be one of the two disjoint members unless the port can afford an ML-DSA verifier in the locked stage.

**WHY.** (1) Atlas law 12 (small, conserved, doubled core) and N20 (unfixable first-stage bug): the smaller the thing that can do irreversible things, the less there is to get wrong. It also removes a whole class of "compromised second stage burns the floor" attacks (R6, R9). (2) Derivation [I]: let `verify_ML` run in stage2 and `stage2` be authenticated by LMS-SHA-256 under slot 1. A SHA-256 failure lets the attacker forge slot 1's signature, hence the second stage, hence the ML-DSA verdict; both quorum members fall to one assumption. Delegated verification collapses the independence that the disjoint-quorum rule is meant to buy.

**ALTERNATIVES REJECTED.** (a) Core only in the second stage: shrinks first stage but any second-stage compromise yields authority change. (b) Everything in the locked stage: cannot be updated and cannot fit ML-DSA on C1/C2 [I]. (c) Trust the second stage's verdict but require it to be authenticated by a quorum itself: that makes every image update a quorum operation, breaking law 2's "boot with one class".

**ASSUMPTIONS.** Part provides lockable flash for about 16 KB (atlas E-A1 survey outcome; if <30% do, the atlas says the new-ROM argument returns); a hash-based verifier for the second waist (SHAKE) fits the HA-1 first stage (unverified size; budget in A.1.6).

**TRADE-OFFS.** Floor advances and slot changes take effect only at reset (acceptable: they ride maintenance windows, atlas 11.5). Lattice diversity is not usable for the two irreversible-quorum members on small parts.

**LIMITS.** Does not protect against a local physical attacker (atlas Part 8); the design limits harm by keeping only public hashes in the first stage. If SHA-2 and SHA-3 are both broken, no hash-based quorum survives.

**HOW WE VALIDATE.** TLA+ (or equivalent) model of `core-min` plus the layering, with the attacker able to forge any key whose assumption set contains one chosen atom; invariants: (a) no single atom failure reaches COMMIT of ADVANCE_FLOOR/REPLACE_SLOT/LIFECYCLE; (b) floor never decreases; (c) power cut at any step leaves a bootable image. Executable cross-check: `/code/A/quorum.py` already enumerates the slot set and confirms (A.1.7).

### A.1.6 Budget for the locked stage (arithmetic)

| Component | Size | Label |
|---|---|---|
| LMS verifier + SHA-256 + glue (atlas "demonstrated") | 12,864 B | [D] atlas 11.1 |
| `core-min`: slot compare, quorum check, floor/journal, record decode | about 3,000 B (about 1,500 C lines at ~2 B/line, wide error bars) | [E] |
| **MV-1 total** | **about 15.9 KB, rounded up to a 16 KB region budget** | [E] |
| Add SLH-DSA-SHAKE verifier + Keccak for HA-1 | unverified; plan 8-16 KB, so HA-1 region 32 KB | [E, low confidence] |
| RAM: LMS stack 1-1.6 KB (atlas) + authority 176 B + floor 32 B + 3 slots 144 B + journal scratch 96 B + tx 104 B (+ signature buffer from flash-resident bundle read in place) | about 2.2 KB; budget 4 KB | [E] |

Note the atlas states 13 KB for the first stage; the 16 KB here is 13 KB plus the core logic the atlas did not size. Flag for the merge agent.

### A.1.7 Executable check of the quorum rule [C]

`quorum.py` encodes assumption masks (H_SHA2, H_KECCAK, LATTICE, DLOG_EC, FACTOR) and tests the rule "accepted set contains >=2 pairwise-disjoint members":

| Signer set | Valid under disjoint rule | Note |
|---|---|---|
| {ML-DSA, SLH-SHAKE} | no | share Keccak |
| {ML-DSA, LMS-SHA256} | yes | disjoint |
| {SLH-SHAKE, LMS-SHA256} | yes | disjoint |
| all three | yes | contains a disjoint pair |

Single-failure test: a plain "any 2 of 3" rule is **unsafe** (Keccak failure forges ML-DSA and SLH-SHAKE: the tool returns `(False, bit=Keccak)`); the disjoint rule is **safe** `(True)`. A degenerate slot set {ML-DSA, SLH-SHAKE} passes the safety test *vacuously* because no valid quorum exists, so the policy linter needs two checks (safety **and** liveness: at least one valid quorum exists and honest availability is above a floor). This reproduces atlas M2/10.3 qualitatively; the 19x probability figure is the atlas's model M2 and was not re-derived here.

---

## A.2 Layered module map

### A.2.1 Classification rules

| Class | Definition | Example |
|---|---|---|
| **Core** | Decides irreversible state; depends on nothing | `ac-core` |
| **Independent library** | Useful alone, no knowledge of the core, own KATs and release cycle | `ac-lms`, `ac-sha2`, `ac-keccak`, `ac-mlkem`, `ac-cbor-det` |
| **Shared infrastructure** | Used by many modules, no policy | `ac-codec` (fixed records), `ac-registry` (IDs), `ac-ct` (constant-time helpers), `ac-test-vectors` |
| **Optional module** | Depends on core, can be omitted per class | `ac-stage` (update staging), `ac-report`, `ac-enrol`, `ac-timewin`, `ac-debugauth`, `ac-lifecycle` |
| **Isolated for security** | Runs in a separate protection domain or device | locked first stage, C3 crypto partition, HSM signer, KDC, escrow tooling |
| **Isolated for reliability / certification** | Kept out of the safety image | PQ crypto services on C3 (R5); `ac-core` is linked, not merged, into safety code |
| **Host-side tooling** | Never on a device; std, large dependencies allowed | `ac-policyc`, `ac-bundle`, `ac-fleetverify`, `ac-sim`, `ac-cbom` |

### A.2.2 Dependency rules (enforced mechanically)

1. **Layer DAG, no cycles.** Layers L0 < L1 < L2 < L3 < L4; a module may depend only on lower layers. Enforced by a build-time include/link-graph check (`tools/depcheck`, fails CI).
2. **Core depends on nothing**: no libc, no allocator, no other module; only `<stdint.h>`, `<stddef.h>`, `<stdbool.h>` under `-ffreestanding -nostdlib`. CI check: `nm` of the core object shows zero undefined symbols; all providers come via tables.
3. **Dependencies point toward stability.** A module may depend only on something at least as stable (tier-wise, A.5.2). T0 (waist, records) depends on nothing above T0.
4. **No dynamic loading, no reflection, no function pointers set at runtime in the locked stage.** Provider tables are `const` and linked.
5. **Crypto libraries know nothing of authority**; the core knows nothing of algorithm internals (only IDs and masks).
6. **Optional means removable**: every L3 module has a no-op link stub so a C1 build links with zero optional modules; module presence is declared in the build profile (A.6).

### A.2.3 Component diagram

```
 L4  host / authority side (std, large deps, never on a locked device)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ ac-policyc  ac-bundle  ac-quorumlint  ac-fleetverify  ac-voucher(FDO adapter) │
 │ ac-escrow   ac-sim/twin  ac-cbom  ac-ceremony(HSM)   ac-conformance           │
 └──────────────────────────────▲────────────────────────────────────────────────┘
                                │ uses canonical bytes (CBOR/COSE, fixed records)
 L3  optional device modules (core-full domain)                      
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ ac-stage  ac-report  ac-enrol  ac-timewin  ac-debugauth  ac-lifecycle  ac-gdoi │
 │ ac-protocols (TLS/DTLS/IKE/OPC-UA/DNP3-SA/62351 glue: *consumers* of policy)  │
 └──────────────────────────────▲────────────────────────────────────────────────┘
 L2  formats and stores (no crypto, no policy)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ ac-cbor-det  ac-cose  ac-suit-glue  ac-codec (fixed records)  ac-journal      │
 └──────────────────────────────▲────────────────────────────────────────────────┘
══════════════════════════ WAIST (T0, frozen) ═══════════════════════════════════
 W1 ac_step()  ◄── messages (bytes) in / intents out ──►  W2 provider table  W3 platform table
 L0  ac-core  (core-min: locked stage │ core-full: stage 2)    depends on nothing
══════════════════════════════════════════════════════════════════════════════════
 L1  providers (independent libraries, each behind W2)       L1  ports (behind W3)
 ┌───────────────────────────────┐                            ┌────────────────────────────┐
 │ ac-sha2 ac-keccak ac-lms      │                            │ nv: flash-journal, RPMB,   │
 │ ac-slhdsa ac-mldsa ac-mlkem   │                            │     SE; counters: fuse/OTP,│
 │ ac-hmac ac-aead ac-hwsha(hw)  │                            │     SE, locked-flash;      │
 │ ac-ecdsa-legacy (verify only) │                            │ entropy; clock hint; boot  │
 └───────────────────────────────┘                            │ target; Zephyr/ESP/Linux...│
                                                              └────────────────────────────┘
```
Note on placement: providers and ports sit *below* the waist (they implement tables the core calls); formats, services and tools sit *above* it (they produce and consume the core's byte messages). Both are arranged so the only thing they share is the waist.

### A.2.4 Trust-boundary diagram

```mermaid
flowchart TB
  subgraph FACT[Factory / CM - C5-adjacent]
    PH[Provisioning HSM: slot hashes, UUID, voucher header]
  end
  subgraph AUTH[Authority domain - C5, offline/witnessed]
    HSM1[HSM class A: LMS/SLH-SHA2]
    HSM2[HSM class B: SLH-SHAKE]
    HSM3[Operator/escrow HSM]
  end
  subgraph CONC[Concentrator zone - C4]
    GW[Gateway / KDC / update server / workstation]
  end
  subgraph DEV[Device]
    subgraph LOCK[Locked flash: TRUST ANCHOR = write-lock]
      CM[core-min + hash verifiers + slot hashes + floor]
    end
    subgraph S2[Stage 2 A/B: authenticated, updatable]
      CF[core-full + ac-stage + ac-report + providers PQ]
    end
    subgraph APP[Application / safety image: C3 isolates crypto]
      APPX[control logic]
    end
  end
  PH -->|public hashes only| CM
  AUTH -->|signed bundles, offline carry| GW
  GW -->|staged bundle (bytes)| CF
  CF -->|proposal ac_tx| CM
  CM -->|verify stage2 + commit| S2
  S2 -->|boot target| APPX
  CF -->|signed state report| GW
```
Boundaries and what crosses them: (1) factory to locked stage: public hashes only (law: one opened device yields no fleet authority); (2) authority domain to concentrators: signed bytes only, never keys (invariant "authority isolation", atlas 12.2 #4); (3) concentrator to `core-full`: untrusted bytes, validated before use; (4) `core-full` to `core-min`: a fixed-size proposal the locked stage fully re-verifies; (5) stage 2 to application: boot target only, and on C3 no public-key operation executes in the control partition (R5).

### A.2.5 Decision D-A2: modularisation and layering

**DECISION.** Modules and rules as in A.2.1-A.2.4; waist is T0 and consists of W1-W3.
**WHY.** Atlas laws 12 and 4: small conserved core, weak linkage through self-describing manifests; R4/R5 (crypto not on every endpoint, not co-located with safety). The classification lets C1 builds exclude everything but providers and a symmetric MAC, and C3 builds isolate crypto.
**ALTERNATIVES REJECTED.** (a) One library "everything": violates TCB and certifiability goals. (b) A plugin ABI with dynamic loading: a runtime-extensible TCB is the opposite of the invariants. (c) Splitting the core into per-feature micro-libraries: more interfaces, more ABI to freeze, little gain.
**ASSUMPTIONS.** Integrators accept a link-time-composed system; Linux-class devices may use shared objects above the waist but never below.
**TRADE-OFFS.** Link-time composition means any extension is a rebuild and re-release of stage 2 (fine: stage 2 is updatable). The locked stage never changes.
**LIMITS.** Optional modules multiply the combinations to test; mitigated by profile presets (A.6).
**HOW WE VALIDATE.** `depcheck` in CI; symbol audit of core; a conformance suite (`ac-conformance`) that runs the same vectors against every provider, port and both core implementations.

---

## A.3 Core data models (byte-level)

### A.3.1 Conventions and versioning rules

| Rule | Statement | Why |
|---|---|---|
| Two encodings | Device-resident and locked-stage records: fixed layout, little-endian, no padding (packed, all sizes compile-time asserted). Exchanged/archived objects: deterministic CBOR (core deterministic encoding of RFC 8949, not re-fetched this session) inside COSE | A fixed layout can be parsed by a 30-line verifier; CBOR gives schema evolution and tooling for objects the locked stage never parses |
| Record header | Every fixed record starts with `ac_rec_hdr` (8 B): `u16 type, u8 fmt_major, u8 fmt_minor, u16 len, u16 flags` | Self-describing, so records survive ports and decades |
| Major version | Change means incompatible; a reader seeing an unknown major returns `AC_E_VERSION` and **never guesses** | Fail-closed on authority data |
| Minor version | Fields may only be appended; `len` says how many bytes are present; readers ignore trailing bytes they do not know, but CRC/digests cover them | Forward compatibility |
| Critical flags | `flags` bit 15 = "critical extension present": a reader that does not understand the extension must reject | Same intent as X.509 critical extensions |
| CBOR map keys | Non-negative integer keys unknown to a reader: reject (critical). Negative integer keys unknown: ignore (non-critical) | Extension without silent semantics change |
| Domain separation | Signed content is `TBS = ctx_label || fmt_version || canonical_bytes` with labels like `"ac/tx/1"`, `"ac/policy/1"`, `"ac/report/1"` | Prevents cross-protocol replay |
| Digests | Evidence-grade digests are **dual**: `SHA-256(x) || SHAKE256(x, 32)` (64 B). Concatenation is at least as collision- and preimage-resistant as the stronger component | Two waists even in the history chain [I] |
| Integrity vs authenticity | `crc32` fields detect bit-rot only; they are never security fields | Avoid misuse |
| Counters | Every counter declares capacity, rate and asset life; policy lint requires `capacity >= 2 x (life x rate + emergency reserve)` (A.3.4) | R10/R11, atlas 6.6 |

### A.3.2 Algorithm descriptor `ac_alg_desc` (16 B, measured)

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0 | 2 | `alg_id` | Registry ID (A.5.1) |
| 2 | 1 | `role` | 1 sig, 2 hash, 3 kem, 4 mac, 5 aead, 6 kdf |
| 3 | 1 | `tier` | 0 experimental, 1 provisional, 2 standard, 3 deprecated, 4 prohibited (policy-controlled, A.5.2) |
| 4 | 4 | `assumption_mask` | Bit set of hardness assumptions (A.3.3) |
| 8 | 2 | `pubkey_len` | bytes |
| 10 | 2 | `sig_or_ct_len` | bytes |
| 12 | 2 | `flags` | bit0 stateful (index reuse hazard); bit1 verifiable-in-locked-stage; bit2 composite (v2); bit3 hardware-backed |
| 14 | 2 | `rsvd` | zero |

Policy lint reads `bit0` to demand index-reservation HSM custody (LMS) and `bit1` to enforce the verification-locality rule.

### A.3.3 Assumption-class set (32-bit mask)

| Bit | Atom | Which standard algorithms carry it (atlas 10.3, [I] on exact lists) |
|---|---|---|
| 0 | H_SHA2 | LMS-SHA-256, SLH-DSA-SHA2, ECDSA (hash), HMAC-SHA-256 |
| 1 | H_KECCAK | SLH-DSA-SHAKE, ML-DSA (SHAKE), ML-KEM (SHA-3/SHAKE) |
| 2 | LATTICE_MODULE | ML-DSA, ML-KEM (MLWE/MSIS) |
| 3 | DLOG_EC | ECDSA, Ed25519, ECDH |
| 4 | FACTORING | RSA |
| 5 | CODE_BASED | HQC, McEliece (future) |
| 6 | HASH_TREE_STRUCT | stateful hash-tree structure risk (LMS/XMSS state discipline) |
| 7-15 | reserved standard atoms | added by registry process |
| 16-30 | vendor/private atoms | never assumed disjoint from anything standard |
| 31 | UNKNOWN | **treated as intersecting every other mask** |

Rule: the intersection of two masks nonempty means "not independent". An unknown or vendor atom is conservative. A hybrid-AND key currently carries the *union* of its parts (safe but pessimistic); a v2 `composite` flag with kill-set semantics would credit AND-hybrids (forward-compat slot reserved in `flags` bit 2).

### A.3.4 Key-hash slot `ac_slot` (48 B, measured)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | `alg_id` |
| 2 | 1 | `hash_alg` (1 SHA-256, 2 SHAKE256-256) |
| 3 | 1 | `state` (0 EMPTY, 1 ACTIVE, 2 SHADOW, 3 HIDDEN, 4 RETIRED, 5 PENDING) |
| 4 | 4 | `assumption_mask` |
| 8 | 32 | `key_hash` = H(canonical public-key encoding with domain label) |
| 40 | 4 | `activation_floor` |
| 44 | 1 | `group` (owner group: 1 OEM, 2 operator, 3 escrow, ...) |
| 45 | 3 | `rsvd` |

Storage: MV-1 stores only 3 x 32 = 96 B of raw hashes plus compile-time descriptors (atlas figure); the full form is 3 x 48 = 144 B, HA-1 up to 8 slots = 384 B. `state` encodes the molting protocol (provision alongside = PENDING/SHADOW, hide = HIDDEN, shed = RETIRED). `group` lets the quorum rule count owner diversity (needed for OEM exit, A.9.4).

### A.3.5 Floor / epoch counter record `ac_floor_rec` (32 B, measured)

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | header (`type = FLOOR`) |
| 8 | 4 | `floor_idx` (minimum acceptable image security version) |
| 12 | 4 | `authority_epoch` (increments on every authority change: floor advance, slot change, lifecycle) |
| 16 | 4 | `journal_seq` |
| 20 | 8 | `last_tx8` (first 8 B of the last accepted transition digest) |
| 28 | 4 | `crc32` |

Storage: two copies (A/B) plus journal (A.3.6) in locked-write flash; where available, a hardware monotonic backing (OTP/fuse unary, secure-element or RPMB counter) holds a *shadow* `floor_idx` so a flash restore cannot rewind it. Budget arithmetic [E]: 25-year life, 1 planned advance/year + 4 emergency reserve = 29 advances; with 2x margin 58 steps. A 32-bit unary fuse field covers only 32 < 58, so the design uses fuses for the coarse floor and the flash journal for fine steps, and the lint refuses a profile whose backing store cannot meet the 2x margin. Any reset path (rewinding a counter or restoring a signer) is an authority action requiring the highest quorum plus physical-presence evidence (atlas pattern 18) and is recorded in the ledger.

### A.3.6 Authority record `ac_authority` (176 B, measured) and ledger journal

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | header (`type = AUTHORITY`) |
| 8 | 16 | `device_uuid` |
| 24 | 1 | `dev_class` (0..5 = C0..C5) |
| 25 | 1 | `lifecycle` (0 TEST, 1 PROVISIONED, 2 PROD, 3 RMA, 4 DECOMMISSIONED) |
| 26 | 1 | `slot_count` |
| 27 | 1 | `quorum_rule_id` (compiled rule: 1 = d2 disjoint) |
| 28 | 4 | `authority_epoch` (mirror) |
| 32 | 4 | `floor_idx` (mirror) |
| 36 | 4 | `flags` (bit0 debug-disabled, bit1 senescent, bit2 anergic-class set, bit3 exit-mode) |
| 40 | 32 | `policy_hash` (active policy) |
| 72 | 32 | `slots_digest` (hash of slot array) |
| 104 | 64 | `ledger_head` (dual hash chain head) |
| 168 | 4 | `crc32` |
| 172 | 4 | `rsvd0` |

Ledger journal entry `ac_journal` (96 B, measured): header 8, `seq` 4, `action` 1, `n_sigs` 1, `rsvd` 2, `new_floor` 4, `new_epoch` 4, `tx_digest` 64 (dual), `commit_marker` 8. Commit protocol (power-fail safe): write entry without marker, verify read-back, write marker, then update A/B records, then burn hardware counter; recovery replays idempotently (invariant (b)). Appended entries form the on-device "ordered memory" that atlas I-12 and pattern 18 call for.

### A.3.7 Transition projection `ac_tx` (104 B, measured)

The only authority-change object the locked stage parses.

| Offset | Size | Field |
|---|---|---|
| 0 | 8 | header (`type = TX`) |
| 8 | 1 | `action` (1 ADVANCE_FLOOR, 2 ADD_SLOT, 3 REPLACE_SLOT, 4 LIFECYCLE, 5 REVOKE, 6 COUNTER_RESET, 7 REPLACE_OWNER_GROUP) |
| 9 | 1 | `n_sigs` |
| 10 | 2 | `rsvd` |
| 12 | 16 | `target_hash16` (device UUID or cohort selector hash; prevents cross-device replay) |
| 28 | 4 | `new_floor` |
| 32 | 4 | `new_epoch` |
| 36 | 4 | `expect_epoch` (anti-replay: must equal the device's current epoch) |
| 40 | 64 | `manifest_digest` (dual digest of the CBOR bundle manifest, binding all metadata) |

Followed by `n_sigs` entries `{u8 slot_idx, u16 alg_id, u16 sig_len, sig bytes}` signed over `TBS("ac/tx/1" || tx)`. The **PAM rule** is structural here: a `REVOKE` whose target `key_hash` matches any ACTIVE/SHADOW slot is invalid unless it carries the escrow group's signature **and** a `presence` flag in the manifest (atlas pattern 5).

### A.3.8 Signed state report (deterministic CBOR; measured example)

COSE envelope `COSE_Sign1` (device attestation key) for C2+, or `COSE_Mac0` (diversified symmetric key, tag 32 B) for C1/constrained devices (R4: no public-key work on endpoints that cannot afford it).

| Key | Field | Notes |
|---|---|---|
| 1 | `fmt` | 1 |
| 2 | `device_uuid` (16 B) | |
| 3 | `nonce` (16 B) | verifier-supplied freshness; if absent, `boot_count` + `report_seq` |
| 4 | `dev_class` | 0..5 |
| 5 | `lifecycle` | |
| 6 | `floor_idx` | |
| 7 | `authority_epoch` | |
| 8 | `slots[]` | per slot `[idx, alg_id, state, group, key_hash]` |
| 9 | `image_hash` (32 B) | active image |
| 10 | `policy_hash` (32 B) | |
| 11 | `ledger_head` (64 B) | |
| 12 | `time_window` | `{earliest_epoch, latest_epoch, source_mask}`; window, not a point (atlas 6.5) |
| 13 | `budgets[]` | `[counter_id, capacity, used]` (exposure of counters before they run out) |
| 14 | `last_drill_epoch` | slot drill (I-13) |
| 15 | `flags` | senescent, anergic, exit-mode |
| 16 | `staged[]` | hashes of staged bundles |

Measured with `cbor_size.py` (3 slots, realistic integer widths, all hashes present): **340 B payload**. Add signature: COSE_Mac0 tag 32 B -> about 400 B total [E]; with an ML-DSA-65 attestation signature of 3,309 B (FIPS 204 parameter, not re-fetched; unverified) about 3.7 KB [E]. For a LoRaWAN-class link the report is not sent raw: a 16 B truncated tag over a 64 B digest is sent instead and the full report fetched on demand [H].

### A.3.9 Transition bundle manifest (deterministic CBOR; measured example)

| Key | Field | Notes |
|---|---|---|
| 1 | `fmt` | |
| 2 | `bundle_id` (16 B) | |
| 3 | `kind` | 1 FIRMWARE, 2 AUTHORITY_ONLY, 3 POLICY, 4 ALG_TABLE, 5 COMBINED (**forbidden by default**: crypto-only changes are kept separate from functional ones, atlas N48) |
| 4 | `target` | `{class_mask, hw_family_ids[], selector}` |
| 5 | `from` | `{min_floor, min_epoch, prior_image_hash}` |
| 6 | `to` | `{new_floor, new_epoch, slot_ops[]}` |
| 7 | `payloads[]` | `{dual_digest, size, uri or SUIT manifest ref}` |
| 8 | `staging` | `{earliest_activation_epoch (coarse month index), cohort, persister_ppm, halt_ref}` |
| 9 | `rationale` | human-readable text, <= 256 B, signed (atlas I-12) |
| 10 | `assumption_decl` | mask of the assumption classes the signers claim; linted against policy |
| -n | non-critical extensions | |
| tx_bin | embedded `ac_tx` bytes | the locked-stage projection |

Measured example manifest: **300 B** without signatures. A quorum {LMS-SHA-256 W4 n=32 (2,508 B, atlas) + SLH-DSA-SHAKE (about 7.9 KB for the -128s set, FIPS 205 value, unverified)} adds about 10.4 KB, a hash-pair bundle of about 10.8 KB [E]; replacing the second member with an ML-DSA-65 signature (3,309 B) gives about 6.2 KB [E] for stage-2-only actions. For firmware, the payload manifest is a SUIT manifest wherever the target already speaks SUIT; this envelope adds only the authority metadata.

### A.3.10 Policy document (deterministic CBOR, signed by quorum)

| Key | Field | Notes |
|---|---|---|
| 1 | `fmt`, 2 `policy_id`, 3 `version`, 4 `min_authority_epoch` | |
| 5 | `applies_to` | class mask, hw families |
| 6 | `alg_table[]` | allowed `alg_id`, `tier`, `valid_until_epoch` (coarse) |
| 7 | `rules[]` | `{action, t, d, required_groups[], locus: LOCKED/STAGE2, hold_boots, objection_window}` |
| 8 | `revocation` | PAM rule parameters |
| 9 | `staging_rules` | cohorting, persister_ppm, halt conditions |
| 10 | `time_rules` | drift bound ppm, staleness epochs (can only restrict) |
| 11 | `counters[]` | `{id, capacity, rate, life, margin}` |
| 12 | `degrade_ladder` | normal -> LKG -> safe minimal -> senescent |

**The policy is data with a closed grammar, not code**: no loops, no conditionals beyond `rules[]` matching on enumerated fields. The core's own compiled minimum (rule 1 = `d >= 2` pairwise disjoint, `t >= 2`, locus LOCKED for irreversible actions) can only be tightened (`t`, `d` up, more groups, longer holds), never loosened; the loader rejects a loosening policy as `AC_E_QUORUM`.

### A.3.11 Decision D-A3: dual encoding, fixed records plus deterministic CBOR

**DECISION.** Fixed records for the locked stage and NV state; deterministic CBOR + COSE for everything exchanged; one binary projection `ac_tx` linking them.
**WHY.** R1/N20: the locked stage must have a trivially auditable parser (atlas law 12). Evidence and policy must evolve for decades (R10) and interoperate with SUIT/COSE/RATS/CBOM tooling (R7). The projection avoids CBOR in the TCB while keeping rich metadata signed (via `manifest_digest`).
**ALTERNATIVES REJECTED.** (a) CBOR everywhere: the locked stage would need a CBOR parser (attack surface in immutable code). (b) Fixed records everywhere: no evolvability for policy and reports; tool ecosystem lost. (c) ASN.1/DER: larger, historically parser-bug-prone [I]. (d) Protobuf/CBOR-without-determinism: signatures over non-canonical bytes.
**ASSUMPTIONS.** COSE PQ algorithm registrations will be completed in the IETF drafts; until then PQ algorithms use private-use COSE IDs and the `alg_id` registry here is authoritative (flag: COSE ML-DSA draft at -11, unverified final).
**TRADE-OFFS.** Two encodings mean two decoders and a consistency obligation; mitigated by generating both from one schema (A.7) and testing round-trip.
**LIMITS.** Little-endian fixed layouts are fine for the Arm/RISC-V targets in scope; a big-endian port converts at the port boundary.
**HOW WE VALIDATE.** Generated codecs plus property tests (decode(encode(x)) = x; non-canonical inputs rejected); `_Static_assert` sizes (done: all six layouts compile and match); fuzzing of decoders; cross-implementation vector exchange between the C and Rust codecs.

---

## A.4 Information and authority flow, failure propagation, recovery

### A.4.1 Information flow and authority flow

| Flow | From -> to | Carries | Authority rule |
|---|---|---|---|
| F1 provisioning | Factory HSM -> locked stage | public key hashes, UUID, voucher header | one-way, public only; log co-signed by CM and OEM (N8) |
| F2 authority bundles | C5 HSMs -> C4 distribution -> `core-full` | signed `ac_tx` + manifest | signatures in disjoint classes; offline carry allowed |
| F3 firmware | C4 -> `ac-stage` -> inactive A/B slot | payloads + SUIT | staged dormant; verified in stage 2 and locked stage |
| F4 commit | `core-full` -> `core-min` | `ac_tx` proposal | locked stage re-verifies, appends journal, burns counter |
| F5 evidence | device -> C4/C5 | state report | verified against ledger; deviations raise alarms (danger-based alerting, atlas 11.7) |
| F6 keys | KDC (C4) -> devices | per-device diversified keys | wrapped by the ML-KEM enrolment KEK |
| F7 time cues | cues -> `ac-timewin` | window updates | may only tighten, never grant (atlas 6.5 rule 3) |

Authority never flows downward by configuration (promotion rule, atlas 12.2 #5); it flows only through signed `ac_tx`.

### A.4.2 FMEA (severity S1 low to S5 fleet-wide authority loss)

| # | Component / failure | Effect | S | Detection | Containment | Recovery path |
|---|---|---|---|---|---|---|
| 1 | Locked stage verifier bug (N20) | Wrong accept or reject of images/tx | 5 | Differential test of two implementations; fleet reports with anomalous ledger | None in place: stage immutable | Doubled implementation reduces odds; board swap; enclave containment |
| 2 | `core-min` quorum logic bug | Irreversible action wrongly allowed | 5 | TLA+ model, fuzzing, two-impl differential | Policy can only tighten (A.3.10) | Same as 1; a second quorum check at stage 2 raises alarm but cannot block |
| 3 | Single hash waist broken (SHA-2 or Keccak) | Forgeable keys in that class | 4 | Cryptanalytic news; none on-device | Disjoint-quorum rule: no single class suffices | Molt: shed that class under a quorum of the other two (A.9.3) |
| 4 | Second stage compromised | Arbitrary stage-2 behaviour | 4 | Locked stage re-verifies on each boot; report mismatch | Single-mutator rule: cannot burn floor or change slots | Floor advance via locked stage; A/B rollback to LKG |
| 5 | Power loss during commit | Partial journal | 3 | Marker absent at boot | Journal-first protocol; idempotent replay | Recovery step in `ac_recover()` |
| 6 | NV store corruption (bit-rot) | Authority record invalid | 4 | crc + A/B + dual hash chain | Two copies + hardware shadow | Rebuild from journal; else LKG with senescent flag |
| 7 | Counter wrap / budget exhausted (R11) | Cannot advance floor | 4 | `budgets[]` in reports, lint at build | 2x margin rule | Reset path = top quorum + presence; else replacement |
| 8 | Restore from backup (R6) | Floor rewound | 5 | Hardware shadow mismatch | Counter backed by hardware where available; else locked journal | Treat as COUNTER_RESET attempt; require authority |
| 9 | Provider returns wrong result (HW SHA fault) | False verify | 4 | Known-answer self-test at init; dual-provider mode for HA-1 | Core fails closed on authority actions, open on run | Fall back to software provider |
| 10 | Policy doc malformed or loosening | Wrong rules | 3 | Loader rejects | Closed grammar, tighten-only | Previous policy stays active |
| 11 | OEM exit with no slot 3 (N41, N7) | Fleet orphaned | 4 | Fleet inventory (`slots[]`) | Requirement in procurement profile; lint refuses profiles without slot 3 | Replacement; "hopelessly queenless" report |
| 12 | Clock wrong (R2, R11) | Staleness misjudged | 2 | Window sanity against other cues | Time can only reduce privileges | Technician token narrows window |
| 13 | Update bricks fleet (CrowdStrike-class) | Mass outage | 5 | Staged cohorts, halt signals | Persisters, no simultaneous activation, LKG | Auto halt, LKG boot |
| 14 | HSM key loss / LMS state loss | Cannot sign in class | 4 | Slot drill failure | Disjoint classes; third slot | Quorum of remaining disjoint classes |
| 15 | LMS index reuse (R6) | Forgery by reuse | 4 | HSM index log, transparency | Index reservation, SLH-DSA preferred when final | Shed class; molt |
| 16 | Attacker holds one device (Part 8) | Local extraction | 2 (fleet) / 5 (device) | Out of scope | First stage holds only public hashes; per-device keys | Replace device; revoke its UUID-bound credentials |
| 17 | Attestation key compromised | Forged reports | 2 | Ledger cross-check | Report is evidence, not authority | Rotate attestation key by tx |
| 18 | Conflicting successors (N49-style) | Split ownership | 4 | Stop-signal objections | No irreversible step during open objection | Escalated tie-break (A.9.4) |
| 19 | Registry / tool bug in `ac-policyc` | Bad policy signed | 4 | Lint, dry-run in `ac-sim` | Dual review, dry-run on twin | Staged cohorts, persister |
| 20 | Boot failure of both A/B | No second stage | 3 | Boot counter | Last-known-good keeps running | Offline recovery (A.9.5) |

### A.4.3 Recovery paths (ordered, least to most disruptive)

1. Automatic: A/B fallback, then last-known-good image, which runs the process in a restricted-authority state (senescent flag, no authority changes accepted).
2. Staged re-try: re-download and re-verify a bundle; halt-and-hold cohorts.
3. Authority recovery by disjoint quorum: floor re-advance, slot replacement, molting.
4. Offline recovery with physical presence: signed technician token plus media (A.9.5).
5. Board swap or device replacement (field debug is disabled, atlas 11.2).
6. Enclave containment with dated exit for devices with no remaining authority path.

### A.4.4 Decision D-A4: failure semantics, fail-closed for authority, fail-operational for control

**DECISION.** `ac_step` may refuse any *authority* request; it never halts, resets or degrades the *control* function: the boot policy picks LKG. Staleness only restricts privileges.
**WHY.** Atlas 5.8 #2: nature optimises populations; a protection relay may not be sacrificed (P30 fail-safe vs fail-secure, R5). Atlas law 8: degrade in steps.
**ALTERNATIVES REJECTED.** Fail-closed on everything (brick on bad update: contradicts safety); fail-open on authority (trivial forgery).
**ASSUMPTIONS.** There is always a last-known-good image that the locked stage can verify with the currently active key set.
**TRADE-OFFS.** A device running LKG with stale authority is knowingly degraded; it reports so.
**LIMITS.** If the safety case demands a different action on authentication failure (fail-safe stop), the integrator sets it in the port's boot hook, and it is outside the core by design.
**HOW WE VALIDATE.** Fault-injection in `ac-sim` (power cuts at every intent boundary, provider faults, NV corruption), property: boot target always defined and never worse than LKG.

---

## A.5 Extension mechanisms

### A.5.1 Registries and where each kind of extension enters

| Extension | Entry point | Touches core? | Touches locked stage? |
|---|---|---|---|
| New signature/KEM/hash algorithm | New `ac-<alg>` library behind W2 + one line in the alg registry + descriptor with mask | No (core sees ID + mask) | No, unless the algorithm is to be an irreversible-quorum member (then stage must contain a verifier: only possible on a new device generation) |
| New protocol (TLS/DTLS/IKE/OPC UA/DNP3-SA/IEC 62351) | L3 `ac-protocols/<name>` consuming policy and `ac-enrol` outputs | No | No |
| New hardware port | Implement W3 tables (and optional hardware W2 providers) in `ports/<vendor>/<part>` | No | Only the port glue in the first stage build |
| New policy rule | Signed policy data in the closed grammar (A.3.10) | No | No (tighten-only) |
| New record field | Append in a minor version, or a negative CBOR key | No | No |
| New action type | New `action` code in `ac_tx` (major or minor?) | **Yes** for core-min if it needs irreversible handling | Yes: therefore actions are designed once (A.3.7 set) and new ones are added only via a major waist version |
| New transport or storage backing | W3 implementation | No | Port glue only |

Registry rules: `alg_id` u16 space: 0x0000-0x00FF core-defined and frozen; 0x0100-0x7FFF public registry (a plain Markdown+CBOR table in the repository, reviewed, never reassigned); 0x8000-0xFFFE vendor/private (never usable in policies applying to more than one vendor without a declaration); 0xFFFF reserved. IDs are never reused (R10: N25 draft-OID lesson [atlas]).

### A.5.2 Stability tiers and deprecation policy over decades

| Tier | Applies to | Promise |
|---|---|---|
| **T0 frozen** | Waist W1-W3 signatures, the fixed records of A.3 (formats v1), `ac_tx`, status codes | Never changes incompatibly. Read-compatibility promised for the life of the project; evolution only by appended minor fields. A major bump is a new waist (`ac_step_v2`) that coexists with v1 for at least one asset life [H: 25 years] |
| **T1 stable** | Provider ABI contract details, L2 formats, core-full services | Semantic versioning; deprecation announced >= 2 major releases / 3 years in advance; removal only from default build, never from the `compat` archive |
| **T2 provisional** | New algorithms (e.g. before final standards), new modules | May change in a minor release; may live at most 3 years provisional before promotion or removal |
| **T3 experimental** | Research code | No promise; excluded from default builds and from conformance claims |

Deprecation process: (1) tier `deprecated` is set in the **algorithm table of a signed policy**, not only in code; (2) a policy flag `warn_epoch` and `deny_epoch` give a coarse, month-granularity schedule; (3) `ac-compat-vN` packages keep read/verify paths for retired formats so old archives, vouchers and evidence stay verifiable (RFC 4998-style renewal for evidence, atlas 11.7); (4) *exercise requirement*: every T1/T2 extension point must be exercised in CI at least once per release and every slot class at least once a year in the field (slot drills; atlas I-13, R10).

### A.5.3 Decision D-A5: closed core, open registries

**DECISION.** The core cannot be extended in the field; the system is extended around it, by registries, tables and data.
**WHY.** Atlas laws 12 and 11 (restrain defenders), R10 (agility atrophy: unused agility rots, so make the agility paths ones that are exercised constantly, i.e. data and providers). Every plug-in point inside the TCB multiplies attack surface (A2/A5 loss in the matrix).
**ALTERNATIVES REJECTED.** (a) Plug-in modules with dynamic loading into the core (matrix A5): TCB growth; (b) Scripting for policy (A2): unbounded; (c) No extensibility at all: R1 re-created.
**ASSUMPTIONS.** Most future change is new algorithms, new protocols, new ports and tighter policy, not new authority actions (atlas 18 ideas and 11 lists a stable set).
**TRADE-OFFS.** Adding a new authority action is expensive on purpose.
**LIMITS.** Cannot add a new irreversible-quorum algorithm to already-shipped locked stages: three slots give "one generation of headroom, not infinite agility" (atlas 11.1).
**HOW WE VALIDATE.** "Extension drill" in CI: add a toy algorithm (e.g. a test-only hash-based scheme) purely through registry + provider, run the full conformance suite, and verify the core object is byte-identical before and after (reproducible build hash check).

---

## A.6 Configuration model

### A.6.1 Two tiers: build profile and signed policy

| Tier | Form | Changes when | Authority |
|---|---|---|---|
| **Build profile** (`profile.cddl` -> `profile.cbor`) | Declarative file selecting modules, algorithm set, class, storage backings, budgets; compiled into the image and reflected in the report | Each firmware build | Developer, reviewed; **checked by `ac-profilelint`** |
| **Signed policy** (A.3.10) | CBOR, signed under quorum | In the field | Authority quorum; tighten-only against the compiled minimum |

There is no third tier of free-form configuration. The linter checks: slot set single-assumption-safe **and live** (A.1.7), verification locality (A.1.5), counter budgets (A.3.1), no stateful key without HSM index custody, PAM rule enabled, debug-disable after commissioning, class dominance and diversification invariants (atlas 12.2), no C0/C1 holding authority.

### A.6.2 Device-class presets (atlas 12)

| Class | Required modules | Optional | Forbidden | Storage/crypto budget (design target, [E]) |
|---|---|---|---|---|
| **C0** inert | none (inventory entry only) | `ac-cbom` record on gateway | any authority | none |
| **C1** symmetric-only | `ac-hmac`, `ac-codec`; `ac-enrol` (KEM or physical) if updatable | hash-verified update (`ac-lms` verify) | signing; shared fleet key (diversified key mandatory) | RAM <= 4 KB, flash for verify <= 16 KB when updatable |
| **C2** verify-capable | `core-min`+`core-full`, `ac-lms`, `ac-sha2`, `ac-report`, `ac-stage` | `ac-slhdsa`, `ac-mldsa`, `ac-timewin`, `ac-debugauth` | field debug; holding signing keys | locked stage 16 KB (MV-1) or 32 KB (HA-1) |
| **C3** safety-critical | C2 + crypto partition, LKG, quorum-signed settings | hardware SHA | public-key operations in control loop; adaptive behaviour | as C2 + partition overhead |
| **C4** concentrators | full PQ protocol stacks, TPM v1.85 identity, dual-vendor | KDC, update server | single point of fleet trust | host-class |
| **C5** authorities | `ac-ceremony`, HSM drivers, `ac-voucher`, transparency log client | | single-class signing | HSM-class |

Class is a field of `ac_authority` and of the profile; the *promotion rule* (class changes only by replacement or quorum-signed re-commissioning) is enforced by the `LIFECYCLE` action requiring a quorum.

### A.6.3 Decision D-A6: declarative, signed, tighten-only configuration

**DECISION.** Two tiers (compiled profile, signed policy), declarative CDDL schemas, a linter that fails CI.
**WHY.** R7 (invisible state: configuration is what the device reports), R9 (side doors often arise from implicit config), atlas law 11. Declarative form allows formal checking (atlas I-4: automatable hitting-set check).
**ALTERNATIVES REJECTED.** Kconfig-only (not signed, not field-changeable); a configuration language with logic (A2); per-device manual configuration (does not scale to 25-year fleets).
**ASSUMPTIONS.** Operators will not write policy by hand; `ac-policyc` compiles from a small human-readable source.
**TRADE-OFFS.** Rigid grammar: some exotic operator wishes require a new T1 minor release.
**LIMITS.** The linter proves properties of the declared policy, not of the real world (a wrong assumption mask is not detectable by the tool).
**HOW WE VALIDATE.** Mutation testing of the linter (seed unsafe policies: shared-assumption quorum, missing slot 3, loosening rule, counter underflow) and expect rejection of each; adversarial review of the assumption-mask registry by cryptographers (atlas 10.3 caveat: SHA-2/SHA-3 independence is a judgement).

---

## A.7 Repository, build and language strategy

### A.7.1 Monorepo layout

```
/spec/                 normative: records (CDDL + byte tables), state machine (TLA+), registries, test vectors
/core/                 ac-core (C11 freestanding) + rust twin (ac-core-rs) + ACSL/Kani proofs
/providers/            one dir per algorithm library (ac-sha2, ac-keccak, ac-lms, ac-slhdsa, ac-mldsa, ac-mlkem, ac-hmac ...)
/codec/                ac-codec (generated from /spec), ac-cbor-det, ac-cose, ac-suit-glue, ac-journal
/modules/              ac-stage, ac-report, ac-enrol, ac-timewin, ac-debugauth, ac-lifecycle, ac-gdoi
/protocols/            consumers: tls-dtls, ikev2, opcua, dnp3sa, iec62351, lorawan ...
/ports/                per-vendor/part: nrf, stm32, nxp, esp32, riscv, linux, hsm-sim ...  (W3 + hw providers)
/tools/                ac-policyc, ac-bundle, ac-quorumlint, ac-profilelint, ac-fleetverify, ac-voucher, ac-escrow, ac-ceremony, ac-cbom, ac-sim, depcheck
/conformance/          cross-implementation vectors, differential harnesses, fault-injection scenarios
/profiles/             class presets C0-C5 + reference product profiles
/docs/                 decisions (ADRs), threat models, assurance case skeletons
/third_party/          vendored, hash-pinned, minimal (reference crypto implementations only)
```
**Governance rule**: `/spec` is the source of truth; code is generated or tested against it; a divergence is a bug in code unless the spec is amended by an ADR.

### A.7.2 Build system and dependency management

| Aspect | Choice | Reason |
|---|---|---|
| C/embedded | **CMake** with toolchain files and presets; exported packages; no Bazel | Dominant in vendor SDKs and RTOSes such as Zephyr [I]; adopters can `add_subdirectory` the library in their own build |
| Rust | **Cargo workspace** (`no_std` crates + host std crates), `cargo vendor` offline | Native; Rust crates are twins or host tooling |
| Orchestration | Small POSIX script + CTest; no custom DSL | Must be readable in 2050 [H] |
| Reproducibility | Pinned container image digest; `SOURCE_DATE_EPOCH`; build twice and compare hashes in CI | Evidence (R7); verifiable binaries for certification |
| Dependencies | **Zero third-party dependencies in `core` and `core-min`**; providers vendored in `/third_party` with hash manifests; `cargo deny` and a license check on host crates; SBOM (CycloneDX) per release | Supply-chain limits (atlas 18 side doors; R9) |
| Releases | Signed tags, release signing with the project's own multi-class quorum (dogfooding) | Credibility; exercises the mechanism (R10) |

### A.7.3 Language strategy by layer

| Layer | Language | Why | Constraints |
|---|---|---|---|
| `core-min` / `core` (L0) | **C11 freestanding as the primary shipped artefact, with an independent Rust `no_std` twin** | C compilers exist for every MCU and every qualified toolchain; independent second implementation required by atlas (HA-1: "independent second implementation of the verifier") and gives differential testing | C: MISRA C (current edition at project start) as the coding standard with documented deviations; CERT C rules; no dynamic allocation, no recursion, bounded loops, no function pointers outside const tables; ACSL contracts on `ac_step` for Frama-C/WP [I: tool chosen by suitability, not verified for this code]. Rust twin: `#![no_std]`, `#![forbid(unsafe_code)]`, Kani proofs for bounds and panic-freedom [I] |
| Providers (L1) | C (portable reference), optional Rust `no_std`, optional verified-extraction code where available (e.g. HACL*-style generated C, [I] not verified here) | Cryptography has a rich verified-implementation ecosystem; reuse beats rewrite | Constant-time discipline; known-answer tests at init; no secret-dependent branches in sign/decap paths |
| Codecs (L2) | Generated from `/spec` (CDDL + tables) into C and Rust | One schema, two encoders, drift impossible | Bounded recursion depth, max sizes as constants |
| Modules (L3) | C for device modules; Rust where the platform has a Rust toolchain | Match the platform | Same ABI |
| Tools (L4) | **Rust** (std) | Memory safety for parsers that handle hostile input; strong CLI ecosystem | `forbid(unsafe_code)` except FFI shims |
| Spec / model | TLA+ (state machine), CDDL (formats), Python reference model | Executable specification, independent of both implementations | |

Why not a verified-extraction language for the core now: a Coq/F*/Dafny-to-C route gives the strongest assurance but ties the project to a niche toolchain for decades and to rare maintainer skills (R10: skill extinction, N61); the chosen path (executable spec + TLA+ + two independent implementations + deductive proof on the small `ac_step`) keeps verified-extraction as a **future refinement** that does not change the T0 interface [H].

### A.7.4 Decision D-A7: monorepo, CMake+Cargo, C core with Rust twin

**DECISION.** As in A.7.1-A.7.3.
**WHY.** Atlas law 12 (doubled core), R10 (skills), R7 (evidence). A monorepo keeps spec, vectors, code and tests atomically consistent for decades; a single repo is also easier to hand over to a foundation (atlas 11.1 "needs a maintainer foundation").
**ALTERNATIVES REJECTED.** (a) Rust-only: excludes many qualified C toolchains and adopter ecosystems, and the first stage on legacy MCUs is C-first today [I]. (b) C-only: loses memory safety for host tooling and the second independent implementation's benefits. (c) Polyrepo: version skew between spec and code. (d) Bazel/Nix as primary: steeper adoption curve and longevity risk.
**ASSUMPTIONS.** Toolchains for C11 remain available for the target lifetime; Rust `no_std` embedded support keeps maturing (Ferrocene exists as a qualified toolchain per its project pages; the exact qualification scope is unverified here).
**TRADE-OFFS.** Doubling the core costs development effort and requires discipline to keep implementations independent (separate authors, separate code review, shared only the spec).
**LIMITS.** Two implementations can share a spec-level mistake; hence the model checking (A.1.5).
**HOW WE VALIDATE.** Differential fuzzing C vs Rust over `ac_step`; coverage targets (MC/DC for core-min as a goal [H]); binary-size budget gate (16 KB MV-1) in CI; reproducible build check.

### A.7.5 Delivery sequence (informed by A.1.4)

1. **M0** spec + vectors + Python reference model + quorum lint (usable without any device code).
2. **M1** the A4 layering: provider table, codecs, `ac-stage`/`ac-report` on top of an existing updater (MCUboot-style hook), so adoption cost is low.
3. **M2** `core-full` + policy + signed reports.
4. **M3** `core-min` in the locked first stage for two reference parts, TLA+ proof, fault-injection campaign (atlas HA-1).
5. **M4** HA-1: second hash waist, dual verification, two-implementation differential.

---

## A.8 Representative API sketches

### A.8.1 Error model and ownership rules

| Rule | Statement |
|---|---|
| Status codes | `int32_t ac_status_t`: 0 = OK, negative = error. Codes are stable T0, never reused. No `errno`, no exceptions, no panics (Rust: `Result`, panic-free proven by Kani target) |
| Totality | Every function returns for every input; invalid input yields a defined error, never undefined behaviour |
| Fail direction | Authority requests fail closed; the caller decides the control-plane fallback (A.4.4) |
| Ownership | Caller owns all buffers; the core borrows for the duration of one call and **retains no pointers**. Output buffers are caller-provided with explicit capacity; short buffers return `AC_E_RANGE` with the required size |
| Context | `ac_ctx_t` is opaque, caller-allocated (`ac_ctx_size()` bytes, aligned to `AC_CTX_ALIGN`); no globals |
| Secrets | The core holds none (public data only). Providers that hold secrets wipe them (`ac_wipe`) on every exit path |
| Concurrency | A context is single-threaded; callers serialise. No hidden threads |
| Side effects | The core performs none. It emits **intents** which the platform executes in order and acknowledges; unacknowledged intents are replayed idempotently by `ac_recover()` |
| ABI versioning | `ac_abi_version()` returns `(major<<16)|minor`; callers check at init |

### A.8.2 C ABI (waist W1, W2, W3)

```c
/* ac_waist.h : T0 frozen. Freestanding: needs only <stdint.h>, <stddef.h>. */
#include <stdint.h>
#include <stddef.h>

#define AC_ABI_MAJOR 1
#define AC_ABI_MINOR 0

typedef int32_t ac_status_t;
enum {
  AC_OK = 0,
  AC_E_FORMAT = -1,      /* malformed bytes */
  AC_E_VERSION = -2,     /* unknown major, or unknown critical field */
  AC_E_SIG = -3,         /* signature invalid */
  AC_E_QUORUM = -4,      /* signer set does not satisfy the (compiled or signed) rule */
  AC_E_FLOOR = -5,       /* would lower or skip the floor, or expect_epoch mismatch */
  AC_E_STATE = -6,       /* action not allowed in current lifecycle */
  AC_E_PROVIDER = -7,    /* algorithm unavailable or self-test failed */
  AC_E_NV = -8,          /* storage error */
  AC_E_BUDGET = -9,      /* counter capacity/margin violated */
  AC_E_PAM = -10,        /* revocation targets live authority */
  AC_E_RANGE = -11,      /* output buffer too small; *needed set */
  AC_E_HOLD = -12,       /* hold-down or objection window open */
  AC_E_UNSUPPORTED = -13
};

/* ---- W2: crypto provider table (const, linked, no runtime registration in locked stage) ---- */
typedef struct {
  uint16_t alg_id;
  uint32_t assumption_mask;
  uint16_t flags;                      /* bit1: verifiable in locked stage */
  ac_status_t (*verify)(const uint8_t *pk, size_t pk_len,
                        const uint8_t *msg, size_t msg_len,
                        const uint8_t *sig, size_t sig_len);   /* OK or AC_E_SIG */
} ac_sig_ops_t;

typedef struct {
  uint8_t hash_alg;                    /* 1 SHA-256, 2 SHAKE256-256 */
  ac_status_t (*digest)(const uint8_t *const *parts, const size_t *lens, size_t n, uint8_t out[32]);
} ac_hash_ops_t;

typedef struct {
  const ac_sig_ops_t  *sig;  size_t n_sig;
  const ac_hash_ops_t *hash; size_t n_hash;
} ac_prim_t;

/* ---- W3: platform table ---- */
typedef struct {
  ac_status_t (*nv_read)(uint32_t region, uint32_t off, uint8_t *buf, size_t len);
  ac_status_t (*nv_append_atomic)(uint32_t region, const uint8_t *rec, size_t len); /* all-or-nothing */
  ac_status_t (*ctr_read)(uint32_t id, uint64_t *v);
  ac_status_t (*ctr_advance_to)(uint32_t id, uint64_t v);   /* MUST never decrease; no decrement entry exists */
  uint64_t    (*ctr_capacity)(uint32_t id);
  ac_status_t (*entropy)(uint8_t *buf, size_t len);
  int64_t     (*clock_hint_epoch)(void);                    /* untrusted hint; may return -1 */
} ac_platform_t;

/* ---- W1: the waist ---- */
typedef struct ac_ctx ac_ctx_t;                  /* opaque */
size_t   ac_ctx_size(void);
uint32_t ac_abi_version(void);

ac_status_t ac_init(ac_ctx_t *ctx, const ac_prim_t *prim, const ac_platform_t *plat);
ac_status_t ac_recover(ac_ctx_t *ctx);           /* idempotent journal replay after reset */

typedef enum { AC_MSG_VERIFY_IMAGE = 1, AC_MSG_PROPOSE_TX = 2, AC_MSG_COMMIT_PENDING = 3,
               AC_MSG_LOAD_POLICY = 4, AC_MSG_QUERY_STATE = 5, AC_MSG_BUILD_REPORT = 6 } ac_msg_kind_t;

typedef struct { ac_msg_kind_t kind; const uint8_t *data; size_t len; } ac_msg_t;

typedef enum { AC_INT_JOURNAL_APPEND = 1, AC_INT_NV_WRITE = 2, AC_INT_COUNTER_BURN = 3,
               AC_INT_SET_BOOT_TARGET = 4, AC_INT_EMIT = 5, AC_INT_REQUEST_RESET = 6 } ac_intent_kind_t;
typedef struct { ac_intent_kind_t kind; uint32_t seq; const uint8_t *data; size_t len; } ac_intent_t;

typedef struct {                                  /* caller-provided, fixed capacity */
  ac_intent_t *items; size_t cap; size_t n;
  uint8_t *scratch; size_t scratch_cap;           /* intents' data point in here */
} ac_effects_t;

/* Pure with respect to everything except ctx: performs no I/O. */
ac_status_t ac_step(ac_ctx_t *ctx, const ac_msg_t *in, ac_effects_t *out, size_t *needed);
ac_status_t ac_ack(ac_ctx_t *ctx, uint32_t seq);  /* platform confirms an intent executed */
```
Compile-time guard in the locked build: only `AC_MSG_VERIFY_IMAGE`, `AC_MSG_COMMIT_PENDING` and `AC_MSG_QUERY_STATE` are compiled in (`core-min`); the rest are `core-full`. A message kind compiled out returns `AC_E_UNSUPPORTED`, not undefined behaviour.

### A.8.3 Rust trait sketch (twin and tooling)

```rust
#![no_std]
pub enum Status { Format, Version, Sig, Quorum, Floor, State, Provider, Nv, Budget, Pam, Range { needed: usize }, Hold, Unsupported }

pub trait Prim {
    fn hash(&self, alg: HashAlg, parts: &[&[u8]], out: &mut [u8; 32]) -> Result<(), Status>;
    fn verify(&self, alg: AlgId, pk: &[u8], msg: &[u8], sig: &[u8]) -> Result<(), Status>;
    fn descriptor(&self, alg: AlgId) -> Option<AlgDesc>;        // mask + flags
}
pub trait NvStore {
    fn read(&self, region: u32, off: u32, buf: &mut [u8]) -> Result<(), Status>;
    fn append_atomic(&mut self, region: u32, rec: &[u8]) -> Result<(), Status>;
}
pub trait MonotonicCounter {
    fn read(&self, id: u32) -> Result<u64, Status>;
    /// Must never decrease; there is deliberately no `set` or `decrement`.
    fn advance_to(&mut self, id: u32, v: u64) -> Result<(), Status>;
    fn capacity(&self, id: u32) -> u64;
}
pub trait Platform: NvStore + MonotonicCounter {
    fn entropy(&mut self, buf: &mut [u8]) -> Result<(), Status>;
    fn clock_hint_epoch(&self) -> Option<i64>;                   // hint only
}
pub trait EffectSink {                                           // caller-implemented
    fn push(&mut self, i: Intent<'_>) -> Result<(), Status>;
}

pub struct Core<P: Prim, H: Platform> { /* fixed-size arrays, no heap */ prim: P, plat: H }
impl<P: Prim, H: Platform> Core<P, H> {
    pub fn step(&mut self, msg: Msg<'_>, fx: &mut impl EffectSink) -> Result<Decision, Status>;
    pub fn recover(&mut self) -> Result<(), Status>;
}
```
Design points: the absence of `set`/`decrement` in `MonotonicCounter` is the Rust expression of "reset is the cancer path" (atlas pattern 18); `Range{needed}` carries the required size so callers never loop-guess; both languages return the same numeric codes through the C ABI shim.

### A.8.4 Decision D-A8: intent-based, byte-message waist

**DECISION.** The waist is `ac_step(msg) -> intents`, with caller-executed, acknowledged intents; no callbacks that perform authority effects.
**WHY.** A pure function with explicit effects is the property that makes deductive proof and model checking tractable and keeps the core free of I/O and OS assumptions (matrix: TCB, certifiability, portability). Byte messages give a language-independent, serialisable ABI that can be frozen for decades (R10) and that can be replayed in the simulator.
**ALTERNATIVES REJECTED.** (a) Rich struct-passing C API: layout/ABI fragility over decades. (b) Callback-heavy API where the core calls into NV and counters directly: effects interleaved with logic, harder to prove power-fail safety. (c) Message-bus/RPC runtime in the TCB: unnecessary.
**ASSUMPTIONS.** Platform can execute intents in order and acknowledge them; if power fails between intents the journal makes replay safe.
**TRADE-OFFS.** Slightly more glue code in every port; one extra round per transition.
**LIMITS.** The waist cannot express streaming/large-object verification: image verification passes digests computed by the caller (the caller hashes the image; the core verifies the signature over the digest and compares). A caller that lies about the digest is the stage-2 case handled by the locked stage's own hashing at boot.
**HOW WE VALIDATE.** Property tests on replay (kill after each intent); model-based testing against the TLA+ model; ABI snapshot tests (`abidiff`-style) in CI refusing any T0 change.

---

## A.9 Sequence diagrams

### A.9.1 First boot and enrolment

```mermaid
sequenceDiagram
  autonumber
  participant CM as Factory/CM + provisioning HSM
  participant D as Device (TEST lifecycle)
  participant L as Locked stage (core-min)
  participant S as Stage 2 (core-full)
  participant K as KDC / gateway (C4)
  participant O as Operator (voucher chain)
  CM->>D: public slot hashes (class A, class B, slot 3), UUID, voucher header (OEM dual-class signed)
  CM->>CM: co-signed provisioning log (CM + OEM)
  D->>L: lock write-protect on first stage; lifecycle TEST -> PROVISIONED (quorum tx pre-signed, A.9.1 note)
  L-->>D: authority record + floor 0 + ledger genesis (dual hash)
  Note over D,K: shipped; field debug disabled at PROD
  D->>L: first power-on: verify stage 2 (class A hash-based)
  L->>S: boot target (stage 2)
  S->>K: ML-KEM-768 enrolment (encapsulate to KDC key, once)
  K-->>S: wrapped per-device KEK (diversified)
  S->>O: signed state report #1 (slots, floor, ledger head, time window)
  O->>S: voucher chain extension, slot-3 owner (A.9.4 for details), lifecycle PROVISIONED -> PROD (quorum tx)
  S->>L: propose ac_tx(LIFECYCLE) ; locked stage verifies and commits at next reset
  L-->>S: reset, commit, report #2 (lifecycle PROD, debug-disabled flag set)
```
Note: the factory has no private keys on the device side; the device only ever receives hashes (Part 8 principle). The lifecycle transition at factory is authorised by a quorum pre-signed by the OEM authority domain, so that the factory cannot unilaterally move a device to PROD.

### A.9.2 Signed update with staging

```mermaid
sequenceDiagram
  autonumber
  participant A as Authority (C5 HSMs, classes A+B)
  participant D as Distribution (C4)
  participant S as Stage 2 (core-full + ac-stage)
  participant L as Locked stage (core-min)
  A->>D: bundle: manifest + SUIT/payload digests + ac_tx + signatures
  D->>S: deliver bytes (any channel, any time)
  S->>S: validate formats, policy, signatures (stage-2 providers incl. ML-DSA), PAM rule
  S->>S: stage payload dormant in inactive A/B slot; record staged[] hash
  Note over S: waits for window: activation requires coarse epoch gate AND maintenance window gate
  S->>L: window event: AC_MSG_PROPOSE_TX / activation request (digest of staged image)
  L->>L: re-verify tx signatures (locked-stage classes), expect_epoch, floor, hold rules
  L->>L: journal append, then counter burn (if floor changes), then set boot target B
  L->>S: boot image B (A retained as LKG)
  S->>D: signed state report (floor, slots, image hash, policy hash, time window)
  D-->>A: reports aggregated; cohort halt condition evaluated; next cohort released
```
Cohorts: the manifest's `staging.cohort` and `persister_ppm` hold a defined fraction on LKG until the field state is proven (atlas 11.5). No global simultaneous activation.

### A.9.3 Floor advance with a disjoint quorum (shedding a class, "molt")

```mermaid
sequenceDiagram
  autonumber
  participant X as Auth class A (LMS-SHA256, SHA-2 waist)
  participant Y as Auth class B (SLH-DSA-SHAKE, Keccak waist)
  participant D as Distribution
  participant S as Stage 2
  participant L as Locked stage
  Note over X,Y: Precondition: new slot provisioned SHADOW earlier (molting step 1-2); annual slot drill passed
  X->>D: sign ac_tx(ADVANCE_FLOOR 7->8, retire slot class-X-old) under slot class A
  Y->>D: sign same ac_tx under slot class B   (retired slot may not co-sign its own retirement)
  D->>S: ac_tx + 2 signatures + manifest
  S->>S: lint locally: masks disjoint (SHA2 vs KECCAK), locus LOCKED for both, expect_epoch matches
  S->>L: propose
  L->>L: verify sig1 with slot A hash-verifier, sig2 with slot B hash-verifier
  L->>L: check disjointness from slot masks; check retired slot != signer set requirement
  L->>L: hold: boots_since_propose >= hold_boots AND second channel confirmation (kinetic hold-down)
  L->>L: journal append, hardware counter burn, update A/B records, ledger_head update
  L-->>S: new epoch, new floor; images below floor refused
  S-->>D: report with ledger head; absence of report within window raises alarm
```
If only one class signs, the request is **anergic**: logged, the key put in boot-only trust until a quorum restores it (atlas pattern 1); nothing irreversible occurs.

### A.9.4 OEM exit and slot-3 replacement

Constraint found while designing (flag): atlas 11.1's `REPLACE_SLOT3` needs "a slot-1 or slot-2 signature", but after an OEM exit slots 1-2 cannot sign. The design below pre-commits OEM authorisation at manufacture (voucher header) and makes the *successor group's own diversity* the safety bound.

```mermaid
sequenceDiagram
  autonumber
  participant OEM as OEM (gone or silent)
  participant E as Escrow agent (witnessed)
  participant W as Witnesses
  participant N as New owner (operator group, two disjoint classes)
  participant S as Stage 2
  participant L as Locked stage
  OEM-->>W: signed quarterly heartbeat (stops)
  W->>E: N missed heartbeats or no fix within M days of a critical CVE (contractual trigger, not a device timer)
  E->>N: release voucher files (header = OEM dual-class, pre-signed at manufacture; chain of owner links)
  N->>N: extend chain: owner(slot3 group) -> new owner; both classes sign link (single-assumption safe inside owner group)
  N->>S: ac_tx(REPLACE_OWNER_GROUP) + voucher chain digest + objection window T_obj
  S->>S: publish proposal to witnesses; collect objections (stop signals)
  Note over S: any signed objection from a conflicting claimant halts the irreversible step; deterministic tie-break after escalation
  S->>L: propose after window; L enforces hold_boots and second-channel confirmation
  L->>L: verify header (OEM dual-class sigs vs slots 1,2 hashes), chain links (current slot-3 group), new group disjoint classes, chain length > slot3_gen
  L->>L: journal, set exit-mode flag, replace slot-3 group hashes, epoch++
  L-->>S: report: exit-mode, new group hashes, ledger head
```
Safety bound ("successor diversity" [I]): after the OEM can no longer sign, the strongest authority this device can have equals the diversity of the successor owner group. With MV-1's three slots (slot 3 single-class) an exit leaves the device exposed to a single-assumption failure of slot 3's class; HA-1 (four or more slots: owner group of two disjoint classes) keeps single-assumption safety. This is a concrete procurement requirement: buy HA-1-capable slot layouts if OEM-exit independence matters. The `chain length > slot3_gen` counter prevents rollback to an earlier owner.

### A.9.5 Offline recovery

```mermaid
sequenceDiagram
  autonumber
  participant T as Technician (present, with signed token + media)
  participant A as Authority (offline, C5)
  participant D as Device (both A/B stage-2 failed, running LKG)
  participant L as Locked stage
  A->>T: media: recovery bundle (stage-2 image, ac_tx for floor/slot if needed) + technician freshness token (signed, coarse epoch)
  T->>D: connect local interface (field debug stays disabled)
  D->>L: boot counter exceeded: locked stage enters recovery mode (no network, no time dependency)
  L->>L: accept only: stage-2 image signed by one active class (boot rule) and, if authority change is needed, a disjoint quorum tx
  L->>L: token narrows time window only (cannot grant authority); presence flag for COUNTER_RESET class actions
  L->>D: install, boot new stage 2, retain LKG
  D-->>T: signed report (ledger head, journal entries, recovery recorded)
  T-->>A: return report; authority audits the ledger entry
```
If the locked stage itself is faulty (FMEA #1), the path ends in board swap; this is why N20 needs the doubled implementation before the first device ships.

### A.9.6 Decision D-A9: reset-time commit with kinetic hold-down

**DECISION.** Irreversible commits happen in the locked stage at reset, after (a) re-verification, (b) a hold of `hold_boots` boots, (c) second-channel confirmation when policy asks, (d) an objection window for ownership actions. Holds count **boots (order)**, not wall-clock time.
**WHY.** Atlas laws 2 and 3 (two independent signals; staged accuracy; reset on doubt), M3 (staged hold-down: forger success `(1-d)^N`), and the time chapter: time may never grant authority, only order and elapsed oscillator bounds exist (atlas 6). Boot counts are available on every device and cannot be set by a time cue.
**ALTERNATIVES REJECTED.** Wall-clock hold timers (attackable and wrong in the cold-cabinet case, 6.2); immediate commit (no proofreading stage); network-attested hold (needs liveness).
**ASSUMPTIONS.** Devices reboot at least occasionally in the planned maintenance windows; a device that never reboots simply never commits (safe).
**TRADE-OFFS.** Slower authority change; emergency changes need a pre-agreed shortened policy hold signed in advance.
**LIMITS.** An attacker who controls reboots of a device and holds a forged quorum still wins that device after the hold; the hold only buys detection time across the fleet.
**HOW WE VALIDATE.** Atlas M3 reproduction with `d` varying; simulation of window alignment (`ac-sim`) with real maintenance calendars; red-team drill on the second-channel step.

---

## A.10 Self red-team

| # | Attack on the chosen design | Honest assessment | Response / residual |
|---|---|---|---|
| 1 | **The hourglass waist is wrong and ossifies.** Frozen T0 interfaces last 30 years; a wrong choice is permanent | Real. The waist is deliberately small and byte-oriented, but action codes and intent kinds will be wrong in places | `ac_step_v2` coexistence, `fmt_major` bumps; run an external design review and implement on three unrelated ports before freezing (T0 only after M3) |
| 2 | **The assumption-mask registry encodes judgements** (SHA-2 vs SHA-3 independence; ML-DSA's real dependence) | Atlas itself notes a cryptographer would discount independence somewhat | Masks are in signed policy/alg tables, so they can be corrected without touching the core; the linter reports sensitivity to merging SHA2/KECCAK atoms |
| 3 | **Verification-locality rule (D-A1) kills the lattice class as an irreversible-quorum member on small parts**, so the program degenerates into hash-only diversity | True for MV-1/HA-1. This limits the benefit of lattice schemes to stage-2 actions | If flash allows an ML-DSA verifier in the locked stage (C2+ large parts), use it. Needs an E-experiment: measure ML-DSA verify footprint in a locked stage on two parts |
| 4 | **The locked stage is not locked** (parts differ; Part 8) | Every claim of "only the locked stage mutates authority" is conditional on the lock | Per-part assessment (Stream on hardware); design limits harm: public hashes only |
| 5 | **Core-min is still a single point of fleet-wide failure** (FMEA 1-2) | True. Doubling reduces independent bug probability only if the implementations are truly independent | Separate authors, clean-room twin, mutation testing, TLA+; honest limit stated in every assurance claim |
| 6 | **Dual encoding doubles parsing risk and tooling** | Real; CBOR parsers are common attack surfaces | CBOR never in the locked stage; generated codecs; bounded decoder with fuzzing; fixed projection `ac_tx` |
| 7 | **Hold-down by boot counts is gameable**: attacker with physical or remote reboot control can run N boots | Yes, it only buys a window for the fleet to detect | Used together with second-channel confirmation and objection window; hold is not a primary security control |
| 8 | **Two-implementation C/Rust doubles cost and may be cut under budget pressure** | Likely in practice | It is a release gate for `core-min` (HA-1), explicitly: no gate, no HA-1 claim; MV-1 may ship with one implementation plus differential fuzz against the Python reference model |
| 9 | **S is more complex than A4; adopters may just take A4 and ignore the core** | Plausible (matrix says A4 wins under migration-cost-first weighting) | M1 delivers A4 layering first; the core is introduced device class by device class |
| 10 | **Atlas 11.1 REPLACE_SLOT3 is infeasible after OEM exit**; the fix introduces owner groups and a "successor diversity" bound | A genuine design change, not just an elaboration | Needs TLA+ treatment and a legal/contract review by the policy stream |
| 11 | **Policy "tighten-only" can brick fleets** (restrictive policy accepted, then no valid quorum is ever possible) | True; this is the fail-closed liveness hazard | Linter liveness check; a policy must carry the previous valid quorum for rollback; staged cohorts |
| 12 | **Time-free design leaves staleness unmanaged** | Time can only restrict; a device offline for 20 years restricts itself without anyone noticing | Reports show window and budgets; operator tooling alerts on silent devices (evidence stream) |
| 13 | **Regulatory/certification friction**: dual-class signatures and hash-based schemes may conflict with some mandates (e.g. CNSA 2.0 requires LMS/XMSS for firmware per atlas; SP 800-230 still draft) | Standards are moving | `alg_table` in signed policy and tier flags allow swapping; keep an LMS profile as the MV-1 default as the atlas recommends |
| 14 | **Scores are one reviewer's judgement** | Yes | Sensitivity table in A.1.4 shows robustness; adopter study as falsifier |

### A.10.1 Open questions for merging agents

1. Locked-stage ML-DSA verifier footprint on two reference parts (decides how often lattice participates in irreversible quorums).
2. TLA+ treatment of the verification-locality rule and of the exit-mode path (A.9.4).
3. HA-1 SLH-DSA-SHAKE verifier size in the locked stage (A.1.6 estimate is unverified).
4. Whether the 16 KB MV-1 budget reconciles with the atlas 13 KB figure (A.1.6).
5. Legal structure for the escrow trigger and heartbeat (hand to the policy/ecosystem stream).
6. Hardware stream: which parts offer a lock strong enough for "only the locked stage mutates authority" and a hardware monotonic backing for the floor shadow.

### A.10.2 Traceability summary (decisions to atlas problems)

| Decision | Primary atlas IDs |
|---|---|
| D-A1 hourglass + core + single-mutator + verification locality | R1, R6, R9, N20, laws 2, 4, 12; 10.3; 11.1 |
| D-A2 layering, classification | R4, R5, laws 4, 12; 12.2 |
| D-A3 dual encoding, versioning | R7, R10, N25, N48; 6.6 |
| D-A4 failure semantics | R5, P30, law 8; 5.8 #2 |
| D-A5 closed core, open registries | R10, N57, N61; laws 11, 12 |
| D-A6 configuration | R7, R9, laws 11; I-4, I-12 |
| D-A7 repo/language | R10, N61, N20; HA-1 second implementation |
| D-A8 intent-based waist | R5, R10; M3 |
| D-A9 reset-time commit, hold-down | R2, R11, R6; laws 2, 3, 9; M3; 6.5 |

---

<!-- Appendix C -->
# APPENDIX C

# STREAM B: Cryptographic layer (lead cryptographer + crypto library engineer)

Date of verification: 2026-11-06. Evidence labels per BRIEF. Scratch code: `/home/claude/atlas2/blueprint/code/B/dq.py` (quorum checker), `/home/claude/atlas2/blueprint/code/B/nums.py` (size, time and counter arithmetic). Both were run in this session; their outputs are quoted below as [C].

Verification limits, stated once. Several primary hosts (nvlpubs PDFs via curl, media.defense.gov, csrc FIPS 206/207 pages) were blocked or unreachable. WebFetch summarises pages with a small model, so any figure marked "[F via fetch]" was read from a primary page but has not been re-read from the PDF. A rate limit cut off the last batch of checks (Mbed TLS releases, KyberSlash and Masking-Kyber abstracts, Botan, MCUboot/Zephyr). Those items are marked "unverified".

---

## B.0 Standards status as of 2026-11-06 (verified where marked)

| Item | Status found | Evidence |
|---|---|---|
| FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA | Final since August 2024 | [F] csrc.nist.gov/projects/post-quantum-cryptography (page updated 2026-10-27) |
| FIPS 206 FN-DSA | **Not final.** The IETF drafts of Nov 2026 and May 2026 say "expected late 2026 / early 2027" and "forthcoming". NIST said in Aug 2025 that the draft was submitted up the chain. I found no evidence of a published initial public draft. | [F] draft-ietf-cose-falcon-05 (2026-11-01); [F] draft-ietf-lamps-fn-dsa-certificates-00 (2026-05-20); [F] pqc-forum post, Aug 2025 |
| HQC (FIPS 207) | Draft not yet released as of an Aug 2026 report. NIST leans to a seed-only private key format. | [2nd] freenode.net article, 2026-08-03; [2nd] securityweek (draft planned early 2026, final 2027), so the schedule has slipped |
| SP 800-208 (LMS/HSS, XMSS/XMSS^MT) | Final. NIST says not for general use, suited to firmware and software signing. | [F] NIST IR 8547 final text (via fetch) |
| SP 800-230 (additional SLH-DSA sets) | **Initial public draft, 2026-04-13. Comments closed 2026-06-12.** Six sets, hard limit of 2^24 signatures per key, "not approved for general-purpose use". Still draft. | [F] csrc.nist.gov/pubs/sp/800/230/ipd |
| NIST IR 8547 | **Final, 2026-10-27.** Quantum-vulnerable signatures and key establishment are deprecated after 2030 and disallowed after 2035. Federal high-impact systems must move to PQ key establishment by 2030-12-31 and PQ signatures by 2031-12-31, per EO 14412 and OMB M-26-15 (names as quoted by the page). Hybrid is "typically temporary". | [F via fetch] csrc.nist.gov/pubs/ir/8547/final and the PDF |
| CNSA 2.0 | Only ML-KEM-1024 and ML-DSA-87. HashML-DSA prohibited. **SLH-DSA excluded from NSS.** FN-DSA not added. LMS and XMSS (single-tree only, no HSS or XMSS^MT) preferred for firmware roots of trust. Dates: new acquisitions 2027-01-01, phase-out 2030-12-31, mandatory 2031-12-31. | [2nd] postquantum.com FAQ v2.1 summary; the NSA PDF was unreachable |
| IETF X.509 | RFC 9881 (ML-DSA, Oct 2025), RFC 9909 (SLH-DSA, Dec 2025), RFC 9935 (ML-KEM, Mar 2026), RFC 9802 (HSS/XMSS, Jun 2025). FN-DSA certificates is a WG draft (-00). | [F] rfc-editor.org subject index |
| IETF CMS | RFC 9882 (ML-DSA), RFC 9814 (SLH-DSA, Jul 2025). KEM-in-CMS (ML-KEM) was in the RFC Editor queue in March 2026. | [F] IETF 125 LAMPS agenda; rfc-editor |
| Composite signatures and KEMs | Composite ML-DSA (`pq-composite-sigs-19`) is in the RFC Editor queue. Composite ML-KEM (`-23`, 2026-10-14) is in the RFC Editor queue. Neither is an RFC. | [F] datatracker |
| COSE/JOSE | **RFC 9964** (May 2026): ML-DSA-44/65/87 = -48/-49/-50, AKP key type = 7. SLH-DSA (`cose-sphincs-plus-10`): -51 and -52 requested, **only the 128s sets listed**. FN-DSA (`cose-falcon-05`): -54 and -55 requested. | [F] rfc-editor RFC 9964; [F] datatracker drafts |
| LMS extras | RFC 9858 (Oct 2025, informational/CFRG) adds SHA-256/192, SHAKE256/256 and SHAKE256/192 sets. Its security argument rests on preimage and second-preimage resistance. | [F via fetch] RFC 9858 |
| TLS | RFC 10024 (Aug 2026): X25519MLKEM768 = 0x11EC (4588). Pure ML-KEM groups (`draft-ietf-tls-mlkem-11`, Informational) are in the RFC Editor queue, with no consensus on recommendation. | [F] datatracker |
| SUIT | `draft-ietf-suit-mti-23` (Jul 2025, expired Jan 2026) lists HSS-LMS as MTI and no ML-DSA or SLH-DSA profile. I found no SUIT PQ draft by search. **Gap.** | [F] datatracker; search result [I] |
| X-Wing | Individual independent submission `-11` (2026-09-23), not a WG or RFC. | [F] datatracker |
| ACVP | Spec drafts exist for ML-KEM, ML-DSA, SLH-DSA and LMS. **No XMSS entry.** | [F] pages.nist.gov/ACVP |
| CMVP | Certificate #5523 (Chainguard FIPS Provider for OpenSSL, FIPS 140-3 Level 1, active, sunset 2031-09-14) lists ML-KEM, ML-DSA and SLH-DSA with CAVP certificates. I have not seen a validated LMS entry. | [F via fetch] csrc cert 5523 |
| FIPS 140-3 IG | IG 10.3.A has self-test requirements for ML-KEM (#15), ML-DSA (#16), SLH-DSA (#17): CASTs and pairwise consistency tests. | [2nd] SafeLogic blog, Aug 2024 |

Consequence for the build: **the ABI must carry algorithm identity as "(standard, parameter set, profile)", not as a bare name.** FN-DSA, HQC and the SP 800-230 sets are not final, and the COSE and X.509 identifiers for them are TBD. Those algorithms get registry status `PROPOSED`, which cannot be used to authorise anything. A registry rule (B.1.5) enforces this.

---

## B.1 Algorithm abstraction: the registry

### B.1.1 Decision

**DECISION.** Every algorithm is an immutable, content-addressed descriptor in an append-only registry. The descriptor never changes. Everything that changes over time (lifecycle status, deprecation, assumption-class corrections) is a separate signed *status record* that references the descriptor hash.

**WHY.** The atlas's R10 and N57 (agility atrophy) and N25 (draft OIDs) come from mutable "supported algorithm" lists. Immutable descriptors let a device, an auditor and a CBOM tool agree on what "ML-DSA-65 / pure / hedged" meant in 2026 even in 2046. [I]

**ALTERNATIVES REJECTED.**
- A mutable enum in a header, as in liboqs `OQS_SIG_alg_*` strings and OpenSSL NIDs. These change meaning between releases.
- Using IANA, COSE or OID numbers as the identity. They are assigned late, and two of them (COSE SLH-DSA, FN-DSA) are still TBD.

**ASSUMPTIONS.** Descriptors are small enough to live in `.rodata`.

**TRADE-OFFS.** A second lookup (descriptor id to status) on every use. Mitigated by compiling the status table into the image.

**LIMITS.** The registry cannot make a bad assumption classification good (see B.1.3).

**HOW WE VALIDATE.** The registry is a generated artefact with a schema, a golden hash per entry, and a CI check that no entry's bytes changed.

### B.1.2 Descriptor layout (flash form, 32 bytes, little-endian)

```c
typedef struct pq_alg_desc {            /* const, in .rodata, content hash = SHA-256 of canonical CBOR form */
    uint16_t alg_id;        /* 2  stable forever, never reused. Allocation is by this project, not IANA */
    uint8_t  kind;          /* 1  KEM, SIG, SIG_STATEFUL, XOF, HASH, MAC, AEAD, KDF, COMBINER */
    uint8_t  profile;       /* 1  pure | prehash | hedged | deterministic | hybrid-AND | hybrid-OR(forbidden for authority) */
    uint16_t pk_bytes;      /* 2  fits u16: max 2592 (ML-DSA-87) .. 49856 is sig */
    uint16_t sk_bytes;      /* 2  stored form (seed form where defined) */
    uint16_t out_bytes;     /* 2  signature, or ciphertext for KEMs */
    uint8_t  ss_bytes;      /* 1  shared secret (KEM) or 0 */
    uint8_t  nist_cat;      /* 1  1,3,5 or 0 */
    uint32_t assump_bits;   /* 4  bitmask over the registry's assumption atoms (B.1.3) */
    uint32_t prop_bits;     /* 4  property-level tags (B.1.3, level 1) */
    uint16_t state_class;   /* 2  0 stateless | 1 stateful-tree (LMS/XMSS) | 2 limited-use (SP 800-230) */
    uint8_t  sc_profile;    /* 1  side-channel profile code (B.7) */
    uint8_t  verify_scratch_class; /* 1 index into static scratch table (B.4) */
    uint32_t std_ref;       /* 4  index into the standards table: FIPS 204, RFC 8554, ... */
    uint16_t max_uses_log2; /* 2  0 = unlimited; 24 for SP 800-230 sets; tree height for LMS */
} pq_alg_desc_t;            /* 34 B packed; pad or drop max_uses to reach 32 */
```
Arithmetic: 2+1+1+2+2+2+1+1+4+4+2+1+1+4+2 = 30 B before alignment, 32 B padded. Sixteen algorithms cost 512 B of flash. [C]

**Status record (separate, signed, append-only).** `{alg_id, desc_hash[32], status, effective_epoch, reason_code, supersedes}` under the same quorum rule as any authority change. Lifecycle states, ordered:

`PROPOSED` (draft standard; never authorises) then `ADMITTED` (final standard; verify and encrypt allowed; may take part in quorums only if its assumption atoms are declared) then `RECOMMENDED` then `LEGACY_VERIFY` (verify only, no new signing) then `DENIED`.

Rules:
- Transitions are monotone except `ADMITTED` to `RECOMMENDED`.
- `DENIED` is permanent for that descriptor. A fixed version gets a new `alg_id`.

### B.1.3 How to encode "assumption classes" defensibly

**What is a real independent assumption and what is not.** The atlas (10.3) counts SHA-2 and Keccak as the only two waists. I agree with that as a conservative rule, and add three refinements.

**(1) Two levels of encoding.**
- *Level 0, the rule input.* Coarse "waist" atoms. These are the only atoms the quorum rule may use by default. Merkle-Damgård hashes (SHA-256, SHA-512, SHA-384, SHA-512/256) form one atom `SHA2`, because they share a design lineage and a compression-function style. Keccak (SHA-3, SHAKE, cSHAKE, KMAC) forms `KECCAK`.
- *Level 1, the property tags.* They record which hash property the scheme needs: collision resistance (CR), second-preimage resistance (SPR), preimage resistance (PRE), PRF behaviour, or random-oracle (RO) modelling. They are used to rank risk, not to loosen the rule.

Why tags matter, with sources:
- Hash-based signatures (LMS, XMSS, SLH-DSA) rest on SPR/PRE-style properties and not on collision resistance. RFC 9858 says so for LMS. [F via fetch]
- ML-DSA uses SHAKE256 as H for the message representative and the commitment hash, and SHAKE128 for matrix expansion (FIPS 204 §3.7 as extracted). [F via fetch; the step-by-step mapping is my reading of the standard, [I]]
- ML-DSA is a hash-and-sign construction in the Fiat-Shamir style. A collision attack on the hash that binds the message gives a substitute-message forgery, and its QROM proof models the XOF as a random oracle. [I]
- So a SHA-256 *collision* result of the SHA-1 kind (hits ECDSA/Ed25519 and certificates) would not touch LMS-SHA256 or SLH-DSA-SHA2. A *preimage* break would. The Level-0 rule stays conservative: it treats any SHA2 failure as taking out every SHA2-tagged key.

**(2) Is ML-DSA "really SHAKE-dependent in a way that matters"? Yes, for the quorum rule.** Every hash and sampler call in ML-DSA is SHAKE (FIPS 204 §3.7 [F via fetch]); I know of no SHA-2 use in pure ML-DSA. A practical break of SHAKE256 collision or preimage resistance, or a structural distinguisher on Keccak-f, would hit ML-DSA and SLH-DSA-SHAKE together. It would also hit ML-KEM (H = SHA3-256, G = SHA3-512, J and PRF = SHAKE256, XOF = SHAKE128 per FIPS 203 §4.1 [F via fetch]). The atlas conclusion stands: ML-DSA and SLH-DSA-SHAKE share `KECCAK`, so a quorum of those two is not single-assumption-safe. My run reproduces this: the pair (ML-DSA, SLH-DSA-SHAKE) has cover number 1. [C: `dq.py`]

**(3) SLH-DSA-SHA2 vs SHAKE, LMS and XMSS.**
- SLH-DSA-SHA2 at category 1 uses SHA-256 only. At categories 3 and 5 it also uses SHA-512 for H and T_l; both are `SHA2`. [I from FIPS 205 structure, not re-fetched]
- SLH-DSA-SHAKE is `KECCAK` only.
- LMS and XMSS exist in both flavours: LMS-SHA256 (RFC 8554), plus SHA-256/192, SHAKE256/256 and SHAKE256/192 (RFC 9858 [F via fetch]). **So "LMS" does not by itself mean SHA-2.** The descriptor must carry the hash. This matters for B.2: LMS-SHAKE is a `KECCAK` key.

**(4) Other atoms.**

| Atom | Keys that depend on it | Independent of others? |
|---|---|---|
| `SHA2` | LMS/XMSS-SHA2, SLH-DSA-SHA2, Ed25519 (SHA-512), ECDSA with SHA-2, HMAC-SHA2 | Own atom |
| `KECCAK` | ML-DSA, ML-KEM, SLH-DSA-SHAKE, LMS-SHAKE, FN-DSA (Falcon uses SHAKE256 [I]), X-Wing combiner | Own atom |
| `MLWE_MSIS` | ML-DSA, ML-KEM | Lattice family |
| `NTRU_SIS` | FN-DSA | **Treated as correlated with `MLWE_MSIS`** through a shared `LATTICE_REDUCTION` atom (both fall to better lattice-reduction algorithms). Keys carry both atoms. [I] |
| `ECDLP`, `DLP`, `FACTORING` | ECDSA, Ed25519, X25519, RSA | **One atom `SHOR`**: a CRQC kills all of them together. RSA and ECC are not independent. [I] |
| `CODE_BASED` | HQC, Classic McEliece (KEM only) | Independent of lattice and hash |
| `SYM_BLOCK` | AES-based AEAD and KW | Not an authority-quorum atom |

**(5) Things that are not assumptions but must be separate dimensions.**
- *Implementation common mode.* Same library, same compiler, same HSM firmware. This is a "build diversity" tag on the signing path, outside the assumption rule. The atlas's Knight-Leveson point applies. [I]
- *Holder independence.* Different organisations or HSMs (key theft is not an assumption failure). The checker handles it with a theft budget t (B.2).
- *Epoch profile.* The probability or status of `SHOR` differs before and after a CRQC. The registry stores an `epoch_profile` per atom, and the checker is run once per profile (B.2.5).

**What must not be claimed [I].** Independence between `SHA2` and `KECCAK` is a judgement. They are different constructions studied by one community. The rule therefore ships with a *merged-waist stress test*: re-run the checker with `SHA2 = KECCAK` and report what survives. Under the merged model nothing hash-and-lattice survives, which is why the physical-presence/escrow element of the atlas PAM rule matters (B.2.6).

**New third waist?** Code-based signatures do not exist as standards. The NIST on-ramp signature candidates (multivariate, isogeny, etc.) are not standardised, and my fetch of the NIST page gave no round or dates. Policy: such atoms may be registered as `PROPOSED` and cannot count toward an authority quorum until a final standard exists. [I]

### B.1.4 Hybrid composition in the registry

A composite key is a registry entry of `profile = hybrid-AND`. Its compromise condition is a *monotone formula*, not a union of atoms:
- A single key `k` fails if **any** atom in A(k) fails.
- An AND-composite (both signatures must verify) is forgeable only if **both** components are forgeable.
- An OR-hybrid ("either verifies") is forgeable if either is. It is **forbidden for authority**.

The descriptor therefore stores a list of component descriptors and a combiner mode, and the checker computes the minimal failing atom sets. Output from `dq.py` [C]:

```
composite ML-DSA ^ Ed25519 min failing sets: {ECDLP,KECCAK} {ECDLP,MLWE} {KECCAK,SHA2} {MLWE,SHA2}
OR-accept hybrid min failing sets:         {ECDLP} {KECCAK} {MLWE} {SHA2}     (cover number 1)
post-CRQC composite (ECDLP already failed): {KECCAK} {MLWE}                  (degrades to its PQ half)
```

This shows three things:
1. An AND-composite is, by itself, two-failure-safe *in the pre-CRQC epoch*, but the safety comes from the classical half, which a CRQC removes.
2. Post-CRQC the composite is exactly as strong as ML-DSA alone, so it cannot substitute for a hash-based slot.
3. The OR-hybrid is worse than either component.

### B.1.5 Registry invariants (enforced by tooling)

1. Only `ADMITTED` or higher algorithms may appear in an authority quorum.
2. Every descriptor lists its atoms. A missing atom is a registry error.
3. A `PROPOSED` algorithm may be used in shadow-sign (observe-only) mode, per the molting protocol.
4. `max_uses_log2 != 0` forces the stateful-signing path (B.5).

---

## B.2 The disjoint-quorum rule, formalised

### B.2.1 Definitions

- `Σ`: finite set of atoms (B.1.3 Level 0).
- `K`: finite set of keys (slots). Each key `k` has a monotone compromise predicate `φ_k(F)` over `F ⊆ Σ`: true iff an adversary who can break exactly the atoms in `F` can forge under `k`. For a plain key, `φ_k(F) = (F ∩ A(k) ≠ ∅)`. For an AND-composite, `φ = φ_{k1} ∧ φ_{k2}`.
- A *signer set* `S ⊆ K` is the set of distinct keys whose signatures over a single, domain-separated authority message are presented.
- *Assumption-cover number* `κ(S, t)`: the smallest `|F|` such that, after the adversary additionally steals up to `t` keys of its choice, every member of `S` is forgeable. Formally `κ(S,t) = min{ |F| : |{k ∈ S : ¬φ_k(F)}| ≤ t }`.
- A policy `P` is a set of accepted signer sets plus rules for anti-replay and the floor. `P` is **(f, t)-safe** iff every `S ∈ P` has `κ(S, t) ≥ f + 1`.

**The atlas rule.** The atlas states the 10.3 rule as "pairwise disjoint in at least two members". That wording is sufficient but not exact. The exact single-failure condition is `∩_{k∈S} A(k) = ∅` (for plain keys, `t = 0`, `f = 1`). The pairwise form is a special case that also gives `κ = |S|`.

**DECISION.** The project defines "disjoint quorum" as **(f=1, t=0)-safety with an explicit holder rule**, i.e. `κ(S,0) ≥ 2`. The pairwise-disjoint form is a *profile* for high assurance (HA-1). The holder rule is that members must belong to different custody domains. A policy may additionally demand `(f=1, t=1)`.

**WHY.** `κ ≥ 2` is precisely what M2 simulates: no single atom failure yields a quorum. It is also checkable by brute force in microseconds, on host tools.

**ALTERNATIVES REJECTED.**
- Plain threshold (2-of-3). Fails the test: `dq.py` shows ML-DSA + SLH-DSA-SHAKE has `κ = 1`. [C]
- Pairwise-disjoint only. Rejects safe 3-signer sets whose pairs overlap.
- Probabilistic acceptance ("sum of failure probabilities below x"). Not auditable offline, and it needs numbers nobody can defend.

### B.2.2 Checker algorithm

```python
# dq.py (excerpt; whole file in code/B/dq.py)
def cover_number(keys, S, theft=0, amax=6):
    at = atoms({k: keys[k] for k in S})
    for a in range(0, amax+1):
        for F in itertools.combinations(at, a):          # F = set of failed atoms
            F = frozenset(F)
            rest = [k for k in S if not broken(keys[k], F)]   # keys still honest
            if len(rest) <= theft: return a                   # adversary steals the rest
    return 99
def accepted_sets(keys, slots, f, t=0, minsize=2):
    return [S for m in range(minsize, len(slots)+1)
              for S in itertools.combinations(slots, m) if cover_number(keys, S, t) > f]
```

Complexity: `|Σ|` is under 10 and `|K|` under 8 in any realistic deployment, so the loop runs over under 2^10 atom subsets per signer set. This is a host-side policy-compile step. **Devices never run it.** They receive its output as an `accept_table`.

**Device-side form.** For `n ≤ 4` slots, `accept_table` is a bitmap over the `2^n` subsets: 16 bits for 4 slots. The first stage evaluates "signature set bitmask → table lookup". The table lives in the locked stage, or in a signed policy that is *monotone-tightening only* (it may clear bits, never set them). This stops a forger of a later policy from loosening the rule.

### B.2.3 Results [C: `dq.py`; `models/quorum.py` re-run]

For the atlas slot set {ML-DSA, LMS-SHA256, SLH-DSA-SHAKE}:

| Signer set | Cover number κ | Accepted at f=1 |
|---|---|---|
| ML-DSA + LMS-SHA256 | 2 | yes |
| LMS-SHA256 + SLH-DSA-SHAKE | 2 | yes |
| ML-DSA + SLH-DSA-SHAKE | **1** (Keccak) | **no** |
| all three | 2 | yes (but see t=1 below) |

I re-ran `models/quorum.py`:
- Plain 2-of-3: attacker P = 0.005249, honest availability 0.99475.
- Disjoint: attacker P = 0.000274, honest availability 0.99002.
- Ratio 0.005249 / 0.000274 = 19.2. This matches the atlas's "about 19-fold" (the atlas text's "0.52% and 0.027%" are the same numbers rounded). [C]

**Finding F-B1 (atlas gap): every accepted pair contains LMS.** With the three-slot set, both disjoint pairs include LMS-SHA256. LMS is stateful, hard to back up, and has a finite leaf budget. M2's "honest availability" counts only assumption failures; operational loss of the LMS key (state loss, HSM death, leaf exhaustion) removes *all* quorums, so liveness of authority change collapses onto the most fragile key. The fix is a fourth slot of the `SHA2` waist that is stateless: SLH-DSA-SHA2. Four slots (ML-DSA, SLH-DSA-SHAKE, LMS-SHA256, SLH-DSA-SHA2) give four disjoint pairs, each avoiding LMS in two of them:

| Pair | Avoids LMS? |
|---|---|
| ML-DSA + LMS | no |
| ML-DSA + SLH-DSA-SHA2 | yes |
| SLH-DSA-SHAKE + LMS | no |
| SLH-DSA-SHAKE + SLH-DSA-SHA2 | yes |

Cost: 4 × 32 B = 128 B of slot hashes instead of 96 B. [C: `dq.py` on a five-slot set printed these minimal accepted pairs.]

**Finding F-B2 (atlas gap): MV-1 as written cannot enforce the rule.** MV-1 has "one hash verifier: LMS-SHA-256 W4". A locked stage that can verify only `SHA2`-class signatures has no `KECCAK`-class slot, so there is no disjoint quorum at all: every verifiable signer set has `κ = 1`. Two ways out:
- (a) Add Keccak to the locked stage and an LMS-SHAKE256/256 (RFC 9858) or SLH-DSA-SHAKE verifier. The Keccak permutation costs flash that I have **not measured** [unverified]. It is the price of the rule.
- (b) Verify `ML-DSA` in the second stage only, as HA-1 does, and accept that the locked stage then enforces only the "different slot" floor rule and not the disjoint rule. The memo should say this plainly: the two are different guarantees.

CNSA 2.0 constraint: SLH-DSA is excluded, so a national-security profile of this registry can only use {ML-DSA-87 + LMS} (two atoms: `KECCAK`/`MLWE_MSIS` and `SHA2`), which is still a disjoint pair. [2nd]

**Key theft (t ≥ 1).** `dq.py`: the three-signer set has `κ(S,0) = 2` but `κ(S,1) = 1`. One stolen key plus one atom failure can forge. So the rule must pair with the holder rule: different HSMs, different organisations, and an escrow signer under custody-domain separation. [C]

### B.2.4 Safety theorem and proof sketch

**Theorem (single-failure safety).** Let a verifier accept a state transition `τ` only if it receives valid signatures on `(domain-tag ‖ τ ‖ floor-index)` from a signer set `S` with `κ(S, t) ≥ f + 1`. Assume:
- (A1) *Soundness of the registry.* For every key `k` and every adversary that forges under `k` with non-negligible probability, some atom in the minimal failing sets of `φ_k` has failed.
- (A2) *Distinct keys, distinct randomness.* Signatures under distinct keys are over a message with a domain tag and the key's identity, so a signature cannot be reused across keys or contexts.
- (A3) *State hygiene.* Stateful keys never sign two messages with one leaf.
- (A4) The adversary breaks at most `f` atoms and steals at most `t` keys.

Then the adversary cannot get `τ` accepted unless an honest quorum signed `τ`.

*Proof sketch.*
1. Take the accepted `S`. Each member `k ∈ S` either (i) was stolen (at most `t` of them), (ii) is forgeable under the adversary's atom set `F` (`φ_k(F)` true), or (iii) is neither.
2. For (iii), (A1) says a forgery under `k` implies an atom in `k`'s failing sets failed, and by hypothesis none in `F` fits, so the adversary must have got `k`'s signature from an honest signer. Honest signers sign only authorised transitions, and by (A2)/(A3) a replayed signature on a different `τ'` does not verify for `τ`.
3. So if no honest quorum signed `τ`, every member of `S` is in (i) or (ii).
4. That means `|{k ∈ S : ¬φ_k(F)}| ≤ t`, and by definition `|F| ≥ κ(S,t) ≥ f+1`.
5. This contradicts (A4). ∎

**Where the proof is weak (limits).**
- (A1) is a *modelling* assumption. The theorem is conditional on the registry's atom lists being complete. This is why Level 0 uses coarse, merged waists, and why a merged-waist stress test exists.
- It does not cover implementation bugs. Those are common-mode and are the reason for implementation diversity (B.3, B.9).
- It does not cover the ordering of events (the adversary breaking an atom *after* a long-lived signed authority was issued). That is handled by the molting protocol and epochs, not by the theorem.
- For the probabilistic version (M2), if atom failures are independent with probabilities `p_α`, then `Pr[forge S] ≤ Σ_{α≠β} p_α p_β` over covering pairs. This is a model, not a theorem. Positive correlation between `SHA2` and `KECCAK` makes it optimistic. [I]

### B.2.5 Interaction with the epoch profile

The checker runs once per *epoch profile*. In "pre-CRQC", `SHOR` holds and an ECDSA+ML-DSA AND-composite counts as two classes. In "post-CRQC", `SHOR` has failed, so classical keys are treated as already forgeable (their slot is deleted from `S`). A policy that is safe only in the pre-CRQC profile fails CI, because the whole point is to survive the epoch change. [H]

### B.2.6 Ties to the atlas

- **M2 / 10.3.** This section is the formal and executable version of the rule. It adds the exact condition, the key-theft extension, the composite treatment, and the two gaps F-B1 and F-B2.
- **11.1 floor rule.** "Floor advance needs a signature from a different slot than the one retired" is a *holder/slot* rule. The disjoint rule is an *assumption* rule. A floor advance must satisfy both.
- **PAM rule (11.2).** A revocation of the current authority set needs the escrow class plus physical-presence evidence. Physical presence is the only element that does not share any hash atom, so it is the fallback for the merged-waist case.

---

## B.3 Provider strategy: reuse, wrap or avoid

**Selection criteria** (in order): (1) correctness evidence (formal proofs, test vectors, ACVP), (2) constant-time evidence, (3) memory model fit (no heap, static scratch), (4) licence, (5) maintenance health. Health data below is from GitHub pages and package indexes fetched in this session. Where a page did not show a date I say so.

| Candidate | Facts found | Verification status | Licence | Decision |
|---|---|---|---|---|
| **mlkem-native** (PQCA) | v2.0.0 "Latest", 07 Aug (year not shown; v1.2.0 was in liboqs 0.16.0, July 2026, so 2026 [I]). Users: AWS-LC (since v1.50.0), liboqs default (since 0.13.0), rustls via AWS-LC. | CBMC proofs: memory-safe and type-safe C. HOL-Light: AArch64 and x86-64 asm proved functionally correct, memory-safe and constant-time. valgrind-based secret-independence tests. 32-bit Armv8.1-M (Helium) backend experimental. [F: README] | Apache-2.0, ISC, MIT badges | **REUSE as the primary ML-KEM C core.** Wrap behind our ABI. Cortex-M0+/M3/M4 use portable C or our own asm until a verified M-profile backend exists. |
| **mldsa-native** (PQCA) | v2.0.0 07 Aug (same caveat). Users: AWS-LC, liboqs (default since 0.16.0), CHERIoT-PQC, Pavona. | CBMC proofs (UB, overflow). HOL-Light/s2n-bignum for asm. The matrix sampler is deliberately variable-time (public data). **Secret-vector samplers have no proof yet.** Tested against ACVP and Wycheproof vectors. [F: README] | Apache-2.0, ISC, MIT | **REUSE as the primary ML-DSA core.** Record the unproven samplers as an open item and cover them with dynamic CT tests. |
| **slhdsa-c** (PQCA) | All 12 FIPS 205 sets. "WE DO NOT CURRENTLY RECOMMEND..." production use; no release yet. No SP 800-230 mention. | `proofs/cbmc` directory exists, scope not described. | MIT or Apache-2.0 | **WRAP for host-side signing and as a differential oracle only.** Write our own verify-only SLH-DSA for MCUs (about the smallest part of the standard), cross-checked against it. |
| **liboqs** (OQS) | 0.16.0 (2026-07-09): mldsa-native default; HQC enabled; **SPHINCS+ removed**; LMS init and indexing bug fixed; XMSS verify out-of-bounds read fixed. README says not for production. | Mixed; delegates to upstream implementations. | MIT | **Test oracle and interop only.** The stateful-signature bugs fixed in 0.16.0 are direct evidence for AVOID as a stateful signer. |
| **PQClean** | **Archived read-only 2026-08-04**, points users to PQCA. | n/a | CC0 / MIT / public domain | **AVOID.** Retired. |
| **pqm4** | README: **deprecated**, archive "in or after January 2027", last PRs by 2026-11-30. | n/a | Apache-2.0 / CC0 | **AVOID as a dependency.** Keep as a source of Cortex-M4 reference numbers and asm ideas (see B.3.2). |
| **libcrux** (Cryspen) | Crates at 0.0.11 (pre-0.1). `ml-kem` and `ml-dsa`. `no_std` needs a global allocator. | Verified paths via hax and HACL*; per-crate badge not visible on the page. Compiled output *not* verified side-channel-resistant. [F: README] | Apache-2.0, MIT | **WATCH.** Rust option and differential oracle. The allocator requirement conflicts with our no-heap rule. |
| **RustCrypto** `ml-kem` 0.3.4 (2026-10-31), `ml-dsa` 0.1.2 (2026-10-31), `slh-dsa` 0.2.0-rc.5 (2026-04-28) | Versions and dates from crates.io [F]. Audit status and constant-time statements not found. | Unknown | Apache-2.0 or MIT | **Differential oracle.** Not a primary. |
| **OpenSSL 3.5 LTS** | 3.5.9 on 2026-09-29. OSS support to 2030-04-08. ML-KEM, ML-DSA, SLH-DSA; X25519MLKEM768 in the default TLS groups. | CMVP #5523 is a *Chainguard FIPS provider for OpenSSL* module listing ML-KEM/ML-DSA/SLH-DSA CAVP certs. Whether the upstream OpenSSL FIPS provider 3.5 is itself validated: unverified. | Apache-2.0 [I] | **REUSE on C4/C5 hosts** (gateways, KDC, release tooling). |
| **AWS-LC** | Uses mlkem-native and mldsa-native. Formal verification of SHA-2, HMAC, AES-GCM/KW, some s2n-bignum curve code. Page makes no FIPS claim. | Partial | Apache-2.0 (template note only; check) | **REUSE on C4/C5 as the second host implementation** for diversity. |
| **wolfCrypt / wolfBoot** | wolfBoot v2.9.0 (2026-07-02): LMS/HSS, XMSS, ML-DSA, hybrid; many MCU targets. No certification claim on the page. | Unknown | **GPL-3.0** on the wolfBoot page (commercial terms not shown) | **INTEROP TEST only.** Licence prevents a permissive core from depending on it. |
| **Mbed TLS / TF-PSA-Crypto** | Implements PSA Crypto API **1.2**; page does not confirm ML-KEM or ML-DSA; mentions LMS as an extended API. Release data not retrieved. | Unverified | Apache-2.0 or GPL-2.0-or-later | **PSA host for classical algorithms; PQ via our provider.** Revisit when a PQ release is confirmed. |
| **Botan** | Not assessed this session. | unverified | BSD-2 [I, memory] | Survey task; not in baseline. |
| **cisco/hash-sigs** | LMS and HSS; files named `hss_reserve`; licence and recent activity not shown by the page. | Unknown | Not shown | **WRAP for test vectors and host signing study only.** |
| **xmss-reference** | README: intended for cross-validation, not production; deployment needs careful analysis. | n/a | CC0 | **Oracle only.** |
| **PSA Crypto PQC extension** | v1.4 extension at Final 1; covers ML-KEM, ML-DSA, SLH-DSA. `PSA_ALG_ML_DSA` = 0x06004400 (hedged), deterministic variant 0x06004500, key pair stored as a 32-byte seed. LMS/XMSS appear only in the first Beta change note. | [F via fetch] | Spec | **Align numerically where defined; extend** (B.4). |
| **Hardware accelerators / vendor kits** | Search-result titles only: FortifyIQ CAVP-validated ML-DSA verification library [V], Infineon PQC-ready control MCUs, ST X-CUBE-PQC, Nordic nRF Connect ML-DSA sample. | Contents not read | Mixed | **Assess per part from published evidence.** Not baseline. |

### B.3.1 Decision and rationale

**DECISION.** Three layers:
1. *Primitive cores:* take mlkem-native and mldsa-native unmodified as vendored, pinned, hash-checked subtrees. Our own code is a thin provider adapter. We also write two small things ourselves: a **verify-only LMS** and a **verify-only SLH-DSA** for the locked stage (formally specified and model-checked, B.9).
2. *Diversity:* every primitive has at least two independent implementations in the test matrix (mlkem-native vs libcrux vs RustCrypto vs OpenSSL; mldsa-native vs the same).
3. *Host side:* OpenSSL 3.5 LTS and AWS-LC as C4/C5 backends.

**WHY.**
- The ecosystem is consolidating into the PQCA "native" family: PQClean was retired on 2026-08-04, pqm4 is deprecated and liboqs now defers to mlkem-native and mldsa-native. [F]
- Those two have the strongest public evidence (CBMC and HOL-Light). Betting on them means we inherit their verification work.
- Verify-only hash-based code is small enough to verify end to end ourselves.

**ALTERNATIVES REJECTED.** Write all primitives ourselves (no verification budget, N20); use liboqs as the core (README says not production, and the LMS bug history); vendor PQClean or pqm4 (dead).

**ASSUMPTIONS.** The PQCA projects stay healthy. Mitigation: vendored subtrees plus a documented switch to libcrux or RustCrypto behind the same ABI.

**TRADE-OFFS.** No Cortex-M0+/M3/M4 verified assembly; we use portable C or accept unverified asm (B.3.2).

**LIMITS.** Formal verification covers memory safety, type safety and, for asm, constant time. It does **not** cover power, EM, speculation or fault attacks (mldsa-native README states these are out of scope [F]).

**HOW WE VALIDATE.** B.9.

### B.3.2 Cortex-M numbers, with sources

pqm4 benchmarks ([D], `benchmarks.md`, Cortex-M4; board and clock not stated on the page; times computed here at assumed clocks [C]):

| Operation | Cycles | ms at 64 MHz | ms at 120 MHz | Memory per page |
|---|---|---|---|---|
| ML-KEM-768 decaps, `m4fstack` | 714,194 | 11.2 | 6.0 | 2,844 B |
| ML-KEM-768 decaps, `m4fspeed` | 707,827 | 11.1 | 5.9 | 6,452 B |
| ML-KEM-768 decaps, `clean` | 1,387,984 | 21.7 | 11.6 | 14,480 B |
| ML-KEM-768 keygen, `m4fspeed` | 642,096 | 10.0 | 5.4 | 5,396 B |
| ML-DSA-65 verify, `m4f` | 2,415,944 | 37.7 | 20.1 | 9,888 B |
| ML-DSA-65 verify, `m4fstack` | 5,732,397 | 89.6 | 47.8 | 2,712 B |
| ML-DSA-65 sign, `m4f` (avg) | 6,193,171 | 96.8 | 51.6 | 68,872 B |
| ML-DSA-65 sign, `m4fstack` (avg) | 24,421,526 | 381.6 | 203.5 | 6,616 B |
| SLH-DSA-SHA2-128f verify, `clean` | 21,923,628 | 342.6 | 182.7 | 2,664 B |
| SLH-DSA-SHA2-128f sign, `clean` | 368,575,228 | 5,759 | 3,072 | 2,468 B |

- The atlas "22 ms, 14.2 KB" figure for an M0+ decapsulation matches the `clean` M4 row (21.7 ms at 64 MHz, 14,480 B). So the atlas number is the unoptimised implementation, and the M4 asm cuts memory 5× and time 2× (14,480/2,844 = 5.1; 1,387,984/714,194 = 1.94). [C]
- Verification of the stack-minimal ML-DSA variant costs 2.4× the cycles of the speed variant (5,732,397/2,415,944 = 2.37) but needs 3.6× less memory (9,888/2,712). [C]
- Caveat: the page's "Memory" column is not labelled as stack, the ML-KEM rows average only 10 runs, and the pqm4 project is deprecated. These are reference numbers for sizing, not guarantees.

---

## B.4 The provider interface

### B.4.1 Principles

**DECISION.** A PSA-Crypto-like, algorithm-agile C ABI with these contracts:
1. **Algorithm identity** is `alg_id` from the registry; where PSA defines a value (e.g. 0x06004400 for ML-DSA hedged), a mapping table is provided.
2. **No heap.** Every call takes caller-provided scratch memory. Required sizes are available as compile-time constants (`PQ_VERIFY_SCRATCH(alg)`) and a runtime query for dynamic builds.
3. **Constant-time contract:** functions that handle secret inputs are declared `PQ_CT_SECRET` and must satisfy B.7. Functions that handle only public data (verify, encapsulate) are `PQ_PUBLIC` and may branch on data.
4. **Zeroisation:** every scratch buffer, key buffer and context is wiped on all exit paths. The provider uses a platform `pq_secure_zero()` that is not elided by the compiler.
5. **Verify returns a decision, not a reason.** To remote callers, "bad signature", "wrong key" and "malformed" are the same `PQ_VERIFY_REJECT`.
6. **Boot-time self-test gate:** the first call to a primitive fails with `PQ_E_SELFTEST_PENDING` until its KAT has passed.

**WHY.** PSA's property that a key is referenced by a handle and policy, and the heap-free `PSA_*_MAX_SIZE` macros, fit OT. But PSA has no scratch-size query for PQ operations, no stateful signing model, and no per-algorithm side-channel profile. [I]

**ALTERNATIVES REJECTED.** Pure PSA 1.4 (no state model; LMS/XMSS only in beta notes); OpenSSL EVP (heap, provider search); a custom per-primitive API (no agility).

**TRADE-OFFS.** Our own ABI plus a PSA shim on hosts. One more layer, which buys a no-heap guarantee.

**LIMITS.** The scratch-size constants are only as good as the vendored core's actual stack use, which must be measured per build (B.9).

**HOW WE VALIDATE.** Static-analysis check that no provider object calls `malloc`; stack watermark tests; a symbol audit.

### B.4.2 Representative signatures

```c
typedef int32_t pq_status_t;
typedef uint16_t pq_alg_t;

/* ---- registry access (const, no allocation) ---- */
const pq_alg_desc_t *pq_alg_lookup(pq_alg_t alg);                 /* NULL if not compiled in */
size_t pq_sig_max_bytes(pq_alg_t alg);                            /* also compile-time macros per alg */

/* ---- scratch sizing: static query, usable in #define / array dims ---- */
#define PQ_MLDSA65_VERIFY_SCRATCH  /* generated from measured build; 9,888 B on m4f per B.3.2 */
size_t pq_verify_scratch_bytes(pq_alg_t alg);

/* ---- one-shot verify, public inputs only ---- */
pq_status_t pq_verify(pq_alg_t alg,
        const uint8_t *pk, size_t pk_len,
        const uint8_t *ctx, size_t ctx_len,       /* domain-separation string, <= 255 B (FIPS 204) */
        const uint8_t *msg, size_t msg_len,
        const uint8_t *sig, size_t sig_len,
        void *scratch, size_t scratch_len);       /* PQ_OK = accepted; PQ_VERIFY_REJECT otherwise */

/* ---- KEM ---- */
pq_status_t pq_kem_encaps(pq_alg_t alg, const uint8_t *ek, size_t ek_len,
        uint8_t *ct, size_t ct_cap, size_t *ct_len,
        uint8_t ss[32], pq_rng_t *rng, void *scratch, size_t scratch_len);
pq_status_t pq_kem_decaps(pq_alg_t alg, const pq_secret_t *dk,   /* seed form, kept in secret region */
        const uint8_t *ct, size_t ct_len, uint8_t ss[32],
        void *scratch, size_t scratch_len) PQ_CT_SECRET;

/* ---- signing, stateless ---- */
pq_status_t pq_sign(pq_alg_t alg, const pq_secret_t *sk, const uint8_t *ctx, size_t ctx_len,
        const uint8_t *msg, size_t msg_len, uint8_t *sig, size_t sig_cap, size_t *sig_len,
        pq_rng_t *rng /* hedged: required for ML-DSA unless profile says deterministic */,
        void *scratch, size_t scratch_len) PQ_CT_SECRET;

/* ---- signing, stateful: see B.5. The caller cannot name a leaf index. ---- */
pq_status_t pq_sts_sign(pq_sts_key_t *key, const uint8_t *msg, size_t msg_len,
        uint8_t *sig, size_t sig_cap, size_t *sig_len, pq_audit_t *audit);

/* ---- self-test and health ---- */
pq_status_t pq_selftest_run(pq_alg_t alg);          /* KAT; sets sticky state */
pq_status_t pq_health(pq_alg_t alg);                /* PQ_OK or PQ_E_SELFTEST_FAILED / PQ_E_FAULT */
```

### B.4.3 Error model

| Code | Meaning | Caller behaviour |
|---|---|---|
| `PQ_OK` | Success; for verify, **accepted** | proceed |
| `PQ_VERIFY_REJECT` | Verification said no (bad signature, wrong key, malformed) | treat as an attack, rate-limit |
| `PQ_E_ARG` | Pointer or length invalid; sizes inconsistent | programming error |
| `PQ_E_SCRATCH` | Scratch too small | programming error (should be unreachable if sizes came from the static query) |
| `PQ_E_UNSUPPORTED` | Algorithm not compiled in or `DENIED` | policy path |
| `PQ_E_SELFTEST_PENDING` | KAT not yet run | run `pq_selftest_run` |
| `PQ_E_SELFTEST_FAILED` | **Sticky, fatal** for that algorithm until reset | fail closed for authority; for a safety function keep the last-known-good behaviour (atlas class C3) |
| `PQ_E_FAULT` | Redundant-computation or consistency check failed | **Sticky**, same as above, and log |
| `PQ_E_RNG` | Entropy source unhealthy | do not sign or encapsulate |
| `PQ_E_STATE_EXHAUSTED` | Stateful key has no leaves left (B.5) | alarm; switch slot |
| `PQ_E_STATE_IO` | State could not be persisted | **must not sign** |

Rules:
- No error value encodes secret-dependent information.
- Every non-OK path wipes outputs.
- Fault and self-test failures are never silently recoverable.

### B.4.4 Self-test and fault requirements (API level)

- **CAST at boot** for every enabled algorithm: one fixed-input KAT per primitive (ML-KEM encaps/decaps round-trip with a fixed seed; ML-DSA sign/verify; SLH-DSA and LMS verify of a stored signature; SHA-2 and SHA-3 digests). FIPS 140-3 IG 10.3.A requires such self-tests for ML-KEM, ML-DSA and SLH-DSA. [2nd]
- **Pairwise consistency test (PCT)** on every key generation: sign/verify for signatures, encaps/decaps for KEMs. [2nd, same IG]
- **Verify-after-sign** on signing devices, as a policy flag `PQ_POLICY_VERIFY_AFTER_SIGN`. Cost for ML-DSA-65 on the optimised M4 is verify/sign = 2,415,944 / 6,193,171 = 39% extra time. [C from the pqm4 [D] figures]
- **Redundant verification flag** `PQ_POLICY_REDUNDANT_VERIFY`: the verifier evaluates its accept decision twice and combines it so that one corrupted flag cannot admit a signature. Described at API level only.
- Input validation per FIPS 203 §3.3: encaps/decaps may only run on checked inputs. [F via fetch]
- **The pairwise and KAT tests prove implementation integrity at one moment, not freshness.** They are rerun on a schedule (B.9).

---

## B.5 Stateful signatures

### B.5.1 Context

LMS and XMSS (SP 800-208; RFC 8554, RFC 9802 for X.509 [F]) are the only schemes CNSA 2.0 prefers for firmware roots of trust [2nd]. SP 800-230 limited-use SLH-DSA sets (2^24 signatures per key, draft) share the same "count" hazard in a milder form [F]. Atlas problems: R6, P3, P25, N22, N39, N51.

LMS size arithmetic [C; structure per RFC 8554, `nums.py`]:

| Parameter | LMS signature | Leaves (2^h) |
|---|---|---|
| N32, W4, H10 | 2,508 B (matches atlas) | 1,024 |
| N32, W4, H15 | 2,668 B | 32,768 |
| N32, W4, H20 | 2,828 B | 1,048,576 |
| N32, W8, H15 | 1,612 B | 32,768 |
| N24, W8, H10 (SHA-256/192, RFC 9858) | 900 B | 1,024 |
| HSS L=2, H10/H10, W4, N32 | 5,076 B (4 + (2,508 + 56) + 2,508) | 2^20 |

- Formula check: LM-OTS signature = 4 + n + p·n with p = 67 for W4: 4 + 32 + 2,144 = 2,180; LMS signature = 4 + 2,180 + 4 + 32·h; at h=10 that is 2,508.
- CNSA 2.0 does not approve HSS, so CNSA profiles use **single-tree** keys only. [2nd]

**Key-generation cost [E]:** I estimated about `p·(2^w − 1)` hash steps per leaf. That gives 1.1×10^6 hashes for H10/W4, 3.5×10^7 for H15/W4, 1.1×10^9 for H20/W4. At an assumed 10^6 hashes/s (HSM-class software) that is 1 s, 35 s and about 19 min; at an assumed 2×10^7 hashes/s it is 0 s, 2 s and 56 s. The hash rates are assumptions, not measurements.

### B.5.2 Design

**DECISION.** Stateful keys live only inside a signing module that exposes `pq_sts_sign()`. The caller cannot choose, read or set the leaf index. State is managed by **reserve-then-sign with a durable high-water mark** and **non-exportable state**.

```
persistent record (A/B copies, each CRC'd, bound to a hardware monotonic counter):
  { key_id[16], next_free_leaf u64, reserved_until u64, mono_ctr u64, epoch u32, crc u32 }

sign():
  1. if next_free_leaf == reserved_until:
        new_hw = reserved_until + R                       # R = reservation batch, e.g. 1 for roots
        persist {reserved_until = new_hw, mono_ctr++}     # atomic A/B write, then verify readback
        if persist fails -> return PQ_E_STATE_IO          # never sign
  2. leaf = next_free_leaf++ (volatile)                    # only after step 1 returned
  3. sig = LMS_sign(leaf, msg)
  4. verify-after-sign
  5. append audit record (hash chain): {key_id, leaf, SHA-256(msg), time-hint, signer_id}
  6. zeroise one-time key material
crash recovery: on boot, next_free_leaf := reserved_until   # skip unused reservation; waste <= R-1
```

Properties and trade-offs:
- A crash may waste up to `R − 1` leaves, but can never reuse one. For roots that sign a few times a year, `R = 1` costs one persistent write per signature. That is acceptable.
- Waste budget: with 12 signatures a year for 40 years at 2× margin (the counter-capacity rule, B.6.4) the need is 960 leaves, fitting H10 (1,024) with 6.7% spare. H15 (32,768) gives a 34× margin. For a signing service with 4 signatures/day: 4 × 365 × 40 × 2 = 116,800 leaves, which needs H17 or larger; H20 gives 9×. [C]
- **No backup restore.** The key and its state are non-exportable. A restored image of a stateful key is the primary failure mode (N39, N51). Disaster recovery is not a backup but a **pre-provisioned alternate slot** (another LMS key set, or the SLH-DSA-SHA2 slot from F-B1). If an operator must restore, the module refuses unless the restore carries a hardware counter value at least equal to the persisted one, and otherwise marks the key `EXHAUSTED` and burns it.

**Multi-HSM partitioning.** Three options:
1. *Leaf-range partitioning inside one tree* (HSM 1 gets leaves 0-9, etc.). Needs a trusted partition table and a single tree secret in all HSMs. Rejected: the secret is replicated, so a compromise of one HSM yields all.
2. *HSS with per-HSM subtrees.* One offline root signs each HSM's child key. Rejected for CNSA profiles (HSS not approved [2nd]), and signatures grow to 5,076 B.
3. **One independent single-tree key per HSM, with the verifier holding a commitment to a key set.** **Chosen.** The verifier slot holds `H(key-set manifest)`. Each signature carries its public key and a Merkle inclusion proof. No leaf index is ever shared between HSMs. Cost: an extra `32·log2(m)` bytes for m HSMs (for 4 HSMs 64 B) plus the 56 B LMS public key. [C]

**What the verifier needs.**
- A per-slot **leaf-index floor** `q_floor` (monotone). The device stores the highest leaf index it has accepted under each slot and rejects anything below. This does not make LMS stateless. It means that after any accepted authority change, a signer that restores an old state and re-signs old leaves is rejected by every device that already saw a later leaf, which limits the damage of a reset to devices that have not moved. [I] Cost: 8 B per slot; 4 slots = 32 B.
- A **release/epoch counter** in the signed payload that provides anti-rollback independently of the leaf index. The floor is a defence-in-depth measure, not the primary anti-rollback.
- Its own reuse detection is not possible in the verifier. Detection of two different messages under one `(key_id, leaf)` happens in the audit and fleet-evidence layer (11.7): the transparency log flags it and the escape route is the PAM rule (rotate to the alternate slot under a disjoint quorum).

**Auditing.** Every signature appends a hash-chained record. The chain head is countersigned by a second custody domain at least daily. HSM operators cannot delete records; auditors compare leaf counters to the persisted counter. [H]

**Alternatives rejected.** Cisco hash-sigs-style in-library reservation with software state files (no hardware counter; restore hazard remains); XMSS (not in ACVP [F]); stateless SLH-DSA everywhere (CNSA excludes it [2nd]; the 2^64 sets are large and slow, and the 2^24 sets are draft).

**ASSUMPTIONS.** The signing module has durable storage with atomic write semantics and a hardware monotonic counter or equivalent. If not, it must not host a stateful key.

**LIMITS.** An attacker who can restore both state and the counter inside the module defeats this. Physical attacks on HSMs are out of scope here (BRIEF rule 3).

**HOW WE VALIDATE.** TLA+ model of the reserve/sign/crash state machine with the invariant "no `(key_id, leaf)` is ever used twice" under arbitrary crash and restart; fault-injection tests on the storage layer (torn write, stale read); a conformance test that an interrupted `pq_sts_sign` never yields a reused leaf.

---

## B.6 Hybrids, combiners and the symmetric fabric key schedule

### B.6.1 When to hybridise and when not

**DECISION (rules).**

| Situation | Rule | Why |
|---|---|---|
| Key establishment on a networked link (TLS, IKE, enrolment) | **Hybridise**: X25519 + ML-KEM-768 (RFC 10024 group 0x11EC [F]) | Cheap, and protects against an implementation or lattice surprise while classical remains useful |
| Enrolment to a constrained C1/C2 device that cannot afford X25519 + ML-KEM | **ML-KEM-768 alone** (atlas 11.3), once | Fewer cycles, smaller code; the key is one-shot and then replaced by symmetric keys |
| Authority signatures (firmware, floor advance, debug, voucher) | **No classical-only, no OR-hybrid.** Use disjoint-class *quorum* of PQ keys (B.2). A classical AND-composite may be added in the pre-CRQC epoch only as an extra, never as a quorum member | Post-CRQC, the classical half is void (B.1.4); a composite does not add an independent waist |
| Locked first stage | **Never hybrid.** Hash-based only | Smallest code; trust is the lock |
| National-security profile | CNSA 2.0 set only (ML-KEM-1024, ML-DSA-87, LMS) | Compliance; no hybrid mandated, left to the application per NIST IR 8547 [F via fetch] |
| Long-lived symmetric keys | No hybrid concept; use per-device diversification | The symmetric layer is already PQ |

**WHY.** NIST says hybrid is "typically temporary" and adds complexity and risk [F via fetch]. A hybrid is justified when classical still has value over the horizon and the cost is small. It is not justified when it bloats the verifier or gives a false sense of independence.

**ALTERNATIVES REJECTED.** "Hybrid everywhere" (code size in C1/C2 and a false independence claim); "PQ-only everywhere" (loses the hedge for TLS-class links during the period when lattice implementations are young; KyberSlash showed implementation-level flaws exist [2nd: paper title seen in search, details unverified]).

### B.6.2 KEM combiner

**DECISION.** For hybrid KEMs use a *concatenation-with-binding* combiner of the X-Wing type: `ss = SHA3-256(ss_mlkem ‖ ss_x25519 ‖ ct_x25519 ‖ pk_x25519 ‖ label)`. X-Wing's draft states security reduces to ML-KEM-768 IND-CCA or X25519 gap-CDH given SHA3 modelled as a random oracle; sizes: encapsulation key 1,216 B, ciphertext 1,120 B, 32-byte shared secret. [F via fetch, an individual draft, not a standard]

- The ML-KEM ciphertext is **not** in X-Wing's hash because of an ML-KEM-768-specific argument that the draft says depends on its FO transform. So the combiner must not be reused with other KEMs. For ML-KEM-1024 or a different pair, use the generic IETF composite KEM, whose draft (`-23`) is in the RFC Editor queue. [F]
- Series vs parallel principle [H]: assumptions in a **chain** accumulate (AND), those in a **quorum** intersect. For the confidentiality of a hybrid KEM chain, the security is `KECCAK ∧ (MLWE ∨ GapCDH)`: X-Wing keeps `KECCAK` as a single point of dependence, and the hybrid does **not** add a second hash waist.

Sizes [C]: ML-KEM-768 enrolment `ek + ct` = 1,184 + 1,088 = 2,272 B; X-Wing = 1,216 + 1,120 = 2,336 B; ML-KEM-1024 = 1,568 + 1,568 = 3,136 B.

**LIMITS.** An individual draft is not stable. We pin the construction by registry id and test vectors, so the identifier survives if the draft changes.

### B.6.3 Symmetric process-bus key schedule

Atlas ties: 11.3, N10, P19, P20, class rules 12.2 (diversification rule).

**Design.** Levels (all KDF inputs carry a length-prefixed label, device UUID and epoch):

```
L0  KDK[zone]            256-bit key-diversification key, HSM-resident at C4/C5, never leaves; one per zone/site
L1  KEK_dev  = KDF(ss, "KEK/v1" ‖ suite ‖ uuid ‖ kdc_id ‖ H(enrol transcript))     # ss from ML-KEM-768 enrolment
             or  KDF(KDK, "KEK-diversify/v1" ‖ uuid ‖ epoch)                           # factory-injected / no PK path
L2  K_grp(g,e)           256-bit random per group g and epoch e, generated at the KDC DRBG
             delivered as AES-256-KWP(KEK_dev, K_grp ‖ g ‖ e)                          # SP 800-38F style wrap [I]
L3  K_stream = KDF(K_grp, "stream/v1" ‖ stream_id ‖ direction)                        # MAC/GMAC key per stream
L4  per-message tag = MAC(K_stream, counter ‖ payload)                                 # IEC 62351-6 format unchanged
```

**KDF choice.** HKDF with HMAC-SHA-256 (or SHA-384) at L1-L3.
- *Why SHA-2 here:* the bus MAC is already SHA-2/AES. Choosing SHA-2 for the KDF keeps the per-device symmetric chain on a single hash atom. Enrolment adds `KECCAK` and `MLWE` once (unavoidable: ML-KEM uses them internally). The derived-key chain's atoms are therefore {`MLWE_MSIS`, `KECCAK`, `SHA2`} at enrolment and {`SHA2`, `SYM_BLOCK`} afterwards. [I]
- *Rejected:* KMAC256/cSHAKE for L1-L3. It would keep `KECCAK` only but add a second MAC family on a bus whose MAC is SHA-2, widening the union. Revisit if the bus MAC moves.

**Per-device keys.** L1 is unique per device. Dominance and diversification rules of 12.2 hold: a C1 key never opens a C3 relay.

**What group keys cannot do [I]:** any group member can forge any message in the group (a symmetric multicast limit; the atlas's "colony odour"). Mitigations in the design: short epochs, one group per role and zone, per-sender sub-keys where the receiver is not also a sender, and anomaly detection in fleet evidence. Source-origin authentication for multicast under a PQ threat model is an open research item.

**Rekey epochs.** The KDC rotates `K_grp` on a schedule and on any membership change. Epoch `e` is a 32-bit counter plus the group's current-key hash, so a missed rekey is recovered through the counter floor (atlas 11.3).

### B.6.4 Nonce and counter management: the counter-capacity rule

**DECISION (rule).** For every monotonic counter or nonce space with width `w` bits, maximum rate `r` per second and a horizon `H` in seconds (asset life, or key lifetime if rekeyed), the design must satisfy

`2^w ≥ 2 · r · H` (at least 2× margin),

must have **no reset path** short of replacing the key, must raise an alarm at 50% consumption, must force rekey at 90%, and must fail closed for authority operations at 100% (fail-safe for the safety path).

Arithmetic [C, `nums.py`], using a 40-year horizon (1,262,304,000 s):

| Counter / stream | Rate | 32-bit wraps in | 40-year count | Bits needed with 2× | Verdict |
|---|---|---|---|---|---|
| SV, 80 samples/cycle at 50 Hz | 4,000/s | 12.4 days | 5.05×10^12 = 2^42.2 | 43.2 | 32-bit fails; needs 44+ bits **or** rekey ≤ 24 h (2^28.4 per key; 32-bit margin 12.4×) |
| SV, 60 Hz | 4,800/s | 10.4 days | 2^42.5 | 43.5 | Same |
| GOOSE burst average | 100/s | 1.36 years | 2^36.9 | 37.9 | 32-bit fails over life; rekey yearly or widen |
| GOOSE heartbeat | 1/s | 136 years | 2^30.2 | 31.2 | 32-bit OK |
| LoRaWAN-like | 0.1/s | 1,361 years | 2^26.9 | 27.9 | 32-bit OK |
| 1 per ms | 1,000/s | 49.7 days | 2^40.2 | 41.2 | needs 42+ bits or rekey |

These sample rates are scenario assumptions [E]; the 32-bit wrap column is arithmetic.

Related counters:
- Signed 32-bit Unix time wraps on 2038-01-19 03:14:08 UTC (2^31 s); unsigned 32-bit on 2106-02-07. [C]
- The GPS week 10-bit rollover: 1,024 weeks after 2019-04-07 is 2038-11-21 in my arithmetic; the atlas gives 20 November 2038 (GPS time leads UTC by about 18 s, so the UTC rollover falls on the 20th at 23:59:42). [C/I]
- LMS leaf budgets: table in B.5.2. SP 800-230: 2^24 = 16,777,216 signatures per key; at one signature per second that lasts 194 days, so these sets are for release signing, never for online signing. [C]

AEAD nonce rule: for AES-GCM and GMAC (the bus), use a **deterministic counter-based** 96-bit nonce composed of `device-id-slice ‖ epoch ‖ counter` and never random nonces for high-rate streams. SP 800-38D limits random 96-bit nonces to 2^32 invocations per key, and limits by length for the deterministic construction. [F from memory of SP 800-38D; not re-fetched this session. Verify before freezing.]

---

## B.7 Side-channel and implementation-security requirements

### B.7.1 Per-class requirements

| Class | Secret operations present | Requirement | Evidence required |
|---|---|---|---|
| C0 | none | none | n/a |
| C1 (symmetric) | AES/HMAC with per-device key | Table-free or bitsliced AES; MAC compare in constant time. Pqm4's README warns its t-table AES "may be vulnerable to cache attacks" on M4 with a data cache. [F] | CT test (below) |
| C2 (verify-capable) | ML-KEM decapsulation once at enrolment; verify only otherwise | Decaps is `PQ_CT_SECRET`. Verify is public data, no CT demanded, but the accept decision is fault-hardened (B.4.4). | CT test for decaps; redundant-verify test |
| C3 (safety) | as C2, crypto confined to boot/update | Crypto must not share the control loop (R5). No public-key operation in the loop. | WCET report; partition proof |
| C4 (concentrators) | KDC keys, TLS/IKE, decaps, signing of statements | Constant-time cores; hedged signing; stack/heap cleaning; build diversity (two libraries) | CT tests, differential tests |
| C5 (authorities) | release signing, voucher, debug credential | HSM-resident; hedged ML-DSA; stateful rules (B.5); verify-after-sign | HSM certification; B.5 audits |

### B.7.2 Specific cryptographic requirements

1. **Hedged signing is the default.** FIPS 204 says deterministic signing "should not be used" where side-channel attacks are a concern and can't otherwise be mitigated. [F via fetch] Deterministic mode is permitted only in the registry profile `deterministic` and only for host-side tools with a documented reason. PSA also recommends hedged. [F]
2. **Seed-form private keys** for ML-KEM and ML-DSA (32-64 B), with expansion on use. This matches PSA's 32-byte ML-DSA key pair form and NIST's lean toward seed-only for HQC. [F via fetch]
3. **No variable-time division or branching on secrets.** KyberSlash is the cautionary example of a timing flaw from a division in a widely deployed implementation (paper TCHES; I saw its title in search results but did not fetch the abstract). [2nd]
4. **Compiler discipline.** mlkem-native uses barriers and tests several compiler/option combinations against valgrind. [F] We adopt the same: CT tests run for every supported compiler and optimisation level in CI, not just one.
5. **Rejection sampling.** Sampling of public matrices may be variable-time (mldsa-native does this deliberately). Samplers of secret vectors must be constant-time. [F]

### B.7.3 Constant-time verification tooling

| Tool / approach | What it gives | Status in this memo |
|---|---|---|
| valgrind-based secret-taint ("ctgrind"-style) | Detects branches and addresses depending on secret-marked memory in a given run | Used by mlkem-native and mldsa-native [F] |
| `dudect`-style statistical timing | Black-box timing leakage test on real hardware | Named from memory [I]; repository not fetched |
| `timecop` | Poisoning-based taint check used in PQ projects | Named from memory [I] |
| `binsec/rel`, `ct-verif`-style | Static / symbolic constant-time proof on binaries or IR | Named from memory [I]; applicability to our asm unmeasured |
| HOL-Light proofs | Constant-time for asm routines (mlkem-native, mldsa-native) | [F] |

**DECISION.** Three tiers of evidence per implementation, recorded in the descriptor's `sc_profile`:
- `CT-PROVED`: machine-checked constant time for the shipped binary form (only the HOL-Light-covered asm today).
- `CT-TESTED`: valgrind taint and statistical tests pass across the compiler matrix.
- `CT-ASSERTED`: vendor statement only.

A product claim may not say better than its descriptor.

### B.7.4 Fault-attack policy (API level only)

No attack detail is given here. The policy:
- Signing devices use verify-after-sign (B.4.4). Verifying devices that gate authority use the redundant-verify flag.
- Counters and floors are written via the two-copy scheme of B.5.
- A fault or self-test failure is sticky and logged.
- Fault resistance of the hardware is assessed per part from published evidence and certification, not assumed.

### B.7.5 Masking status (what exists, what does not)

| Item | Finding | Evidence |
|---|---|---|
| First-order masked ML-KEM-768 decapsulation, Cortex-M4 | A first-order masked **fine-shuffling** variant has 25% overhead on full ML-KEM-768 decaps, proved secure in the probing model at first order; it replaces a variant whose 51% shuffling was broken by a template attack. | [D] eprint 2026/934 abstract |
| Masked Kyber (Heinz et al.), Cortex-M4 | Paper exists (TCHES 2022; eprint 2022/058, seen in search results). Overhead factors not retrieved. | unverified here |
| Masked FrodoKEM, Cortex-M4 | Exists, but it is FrodoKEM, not ML-KEM. | [D] eprint 2025/1065 |
| Masked ML-DSA | First-order hardware (FPGA) design: 1.127× LUTs, 1.2× flip-flops, **378× execution time**. I found no Cortex-M software masked ML-DSA in this session. | [D] eprint 2024/1817 abstract |
| Masked ML-KEM decaps hardware | First-order 125.4 kGE vs 54.1 kGE unmasked (125.4/54.1 = 2.32×). | [D] eprint 2026/1265 abstract, ratio [C] |

**Conclusion [I].** Masking for ML-KEM on Cortex-M4 has published first-order software, for ML-DSA it does not appear mature on MCUs, and attacks on shuffling variants exist. The project therefore makes **no "masked" claim** in v1. The register entry `sc_profile` has a `MASKED_ORDER1_EVALUATED` code that is unset by default. Devices that hold an ML-KEM or ML-DSA secret on a physically accessible part rely on the atlas's design principle instead: **one opened device yields no fleet authority** (per-device keys, public hashes only in the first stage). Whether any particular MCU needs masking is a per-part assessment from published evidence and certification.

---

## B.8 Encoding and format decisions

**DECISION.** Three formats, by audience:

| Audience | Format | Reason |
|---|---|---|
| Locked first stage (class C2/C3, boot) | **Fixed binary "authority envelope", no parser** | Smallest verifier; no CBOR/ASN.1 attack surface in immutable code |
| Constrained updatable software, SUIT, attestation, vouchers | **Deterministic CBOR (RFC 8949 §4.2) in COSE** (`COSE_Sign` for multi-signature quorums) | Native multi-signer structure maps to the quorum rule; compact; SUIT is CBOR-based |
| C4/C5 PKI, TLS, CMS | **X.509/ASN.1 DER** per RFC 9881 / 9909 / 9935 | Existing PKI and TLS stacks |

**Authority envelope v1 (binary, big-endian, fixed offsets).**

```
off  len  field
0    4    magic "AUTH"
4    2    format_version = 1
6    2    n_sigs (<= 4)
8    4    policy_id            (selects accept_table, B.2.2)
12   8    release_epoch        (u64, anti-rollback)
20   8    leaf_floor_hint      (u64, informative)
28   32   payload_hash         (SHA-256 or SHA3-256 per policy; algorithm in policy)
60   per signature i:  { alg_id u16, key_slot u8, rsvd u8, sig_len u16, sig[sig_len] }
```
Size [C]: header 60 B; per-signature framing 6 B. A two-signature quorum of LMS W4 H10 (2,508) + ML-DSA-65 (3,309) is 60 + 2·6 + 2,508 + 3,309 = **5,889 B**. A CNSA pairing ML-DSA-87 (4,627) + LMS W4 H10 (2,508) is 60 + 12 + 7,135 = **7,207 B**. LMS + SLH-DSA-128-24 (draft 3,856 [F via fetch]) is 60 + 12 + 2,508 + 3,856 = **6,436 B**. The raw signature sums are 5,817, 7,135 and 6,364 B. [C]

**Canonical encoding rules.**
1. Signed content is `domain-tag ‖ policy_id ‖ release_epoch ‖ payload_hash` with a registry-assigned domain tag per transition type (floor advance, slot replacement, lifecycle, release). No two transition types share a tag.
2. Fixed-width integers, big-endian; no optional fields in the envelope.
3. CBOR: deterministic encoding only (shortest-form integers and lengths, sorted map keys), definite lengths, no tags except those registered. Decoders must reject non-canonical forms.
4. Signatures: ML-DSA verification checks the standard canonical encodings (the standard's signature decoding is canonical); a library that does not reject malformed hint or response encodings fails conformance (B.9).
5. Public keys in the envelope are always identified by `(alg_id, key_slot)` and checked against the slot hash; keys are never trusted from the envelope itself.

**Identifier status and risk.**

| Identifier | Value | Status | Risk |
|---|---|---|---|
| COSE ML-DSA-44/65/87 | -48 / -49 / -50 | **Final**, RFC 9964 [F] | low |
| COSE key type AKP | 7 | Final, RFC 9964 [F] | low |
| COSE SLH-DSA-SHA2-128s / SHAKE-128s | -51 / -52 requested | **Draft** (`-10`); only 128s sets | medium; limited sets and TBD |
| COSE FN-DSA-512 / 1024 | -54 / -55 requested | **Draft** (`-05`) | high: FIPS 206 not final |
| COSE HSS-LMS | -46 | RFC 8778 from memory | unverified; verify before freezing |
| X.509 ML-DSA, SLH-DSA, ML-KEM | RFC 9881, 9909, 9935 | **Final** [F] | low |
| X.509 FN-DSA OIDs | "TBD"/"XX" in draft | Draft | high |
| X.509 composite | OIDs in IESG-stage drafts | Draft | medium; do not freeze |
| TLS X25519MLKEM768 | 0x11EC | **Final** (RFC 10024) [F] | low |
| TLS pure ML-KEM groups | 0x0200-0x0202 | Draft in RFC Editor queue; "Recommended: N" | medium |
| SUIT PQ profile | none found | **Gap** | high |
| SP 800-230 sets | no COSE or OID yet | Draft | high |

NIST OID leaf values for ML-DSA, ML-KEM and SLH-DSA are in the NIST CSOR registry; I did not re-fetch them this session and so do not list them. [unverified]

**Registry rule.** Project `alg_id` is the stable identity. Mapping tables to COSE, X.509, TLS and PSA ids are separate data and may be updated without touching a descriptor. That prevents N25 (draft OIDs frozen into devices).

**Gap to flag to the merge.** Because the SUIT working group's MTI draft does not carry an ML-DSA or SLH-DSA profile and it expired in January 2026, a SUIT-based update path for PQ signatures needs a project-specified COSE profile, offered upstream. [I]

---

## B.9 Crypto test strategy

**DECISION.** Seven layers, each with a gate in CI.

1. **Known-answer tests (KATs).** NIST ACVP vectors for ML-KEM, ML-DSA, SLH-DSA and LMS; no XMSS entry exists in ACVP [F], so XMSS (if ever added) uses RFC 8391 vectors and the reference implementation. mldsa-native already tests against ACVP and Wycheproof [F], so our adapter test just proves the adapter does not alter the results.
2. **ACVP-style harness in-house.** Run the ACVP request/response format locally against our provider (the specs are public drafts [F]). For any module a customer takes to CMVP, the real CAVP process then applies. CMVP #5523 shows a module with ML-KEM/ML-DSA/SLH-DSA CAVP certificates already exists [F via fetch].
3. **Wycheproof-style negative vectors.** Malformed keys, ciphertexts and signatures; non-canonical encodings; boundary values; ML-KEM encapsulation-key modulus and decapsulation-key checks (FIPS 203 §3.3 requires checked inputs [F via fetch]). We contribute vectors where gaps exist.
4. **Differential testing.** Every primitive runs against at least two independent implementations (mlkem-native, libcrux, RustCrypto `ml-kem` 0.3.4, OpenSSL 3.5, AWS-LC; for ML-DSA likewise; for SLH-DSA: slhdsa-c, OpenSSL, RustCrypto `slh-dsa`; for LMS: our verify-only, hash-sigs, wolfBoot). A disagreement is a release blocker. This is the Knight-Leveson hedge. [I]
5. **Fuzzing.** Coverage-guided fuzzers on every parser and on each `pq_*` entry with sanitizers (ASan, UBSan, MSan). Stateful-signing fuzz: random crash points. Registry and envelope parsers fuzzed continuously. AWS-LC's CI practice is the model (fuzz, sanitizers on every change). [F]
6. **Constant-time suite.** valgrind taint, statistical timing, and, where available, the HOL-Light-proved asm (B.7.3). Run per compiler/optimisation matrix.
7. **Formal methods.** (a) Reuse the CBMC and HOL-Light proofs from mlkem-native and mldsa-native. (b) Our verify-only LMS and SLH-DSA: CBMC for memory safety plus a functional spec checked against test vectors. (c) TLA+ for the quorum policy evaluation, floor monotonicity and the stateful reserve/sign/crash machine (invariants in B.5 and atlas 11.1). (d) The quorum checker (`dq.py`) is property-tested: monotonicity (adding a key never lowers acceptance); exhaustive agreement with `models/quorum.py`; known-answer cases from B.2.3.

**Provenance tests.** Vendored subtrees are checked by hash against the upstream tag; the build refuses an unexpected diff.

**Measurement tests.** Stack and flash per algorithm per target are measured, not estimated, and compared to the scratch constants in the ABI. A mismatch fails the build.

**LIMITS.** Tests demonstrate absence of known bugs, not absence of bugs. Formal proofs, per their authors, are "never absolute" (mlkem-native README [F]); their SOUNDNESS documents define the scope.

**HOW WE VALIDATE THE VALIDATORS.** Mutation testing: seeded defects (flip a rejection bound, skip a check) must be caught by at least one layer.

---

## B.10 Agility policy over decades

### B.10.1 The threats

- **Agility atrophy** (R10, N57, N64): spare algorithm slots that were never used fail when needed.
- **Downgrade** (N45 and the TLS history): an attacker forces the weakest mutually supported algorithm.
- **Draft freeze** (N25): a device ships with a draft identifier that later changes.

### B.10.2 Policy

1. **Authenticated policy, not negotiation.** For authority operations there is no negotiation. The device's own signed policy table says which algorithms are accepted, as a function of the registry state and the epoch. A message cannot select its own verification algorithm: the envelope's `alg_id` must match the slot's recorded algorithm. (B.8)
2. **Monotone floor on algorithms.** The policy has an `algorithm floor`, advanced like the index floor, by a disjoint quorum. Once an algorithm is `DENIED`, no signed message can re-admit it. A new `alg_id` is needed for a fixed version.
3. **Transcript binding for protocols.** Handshakes (TLS, IKE) bind the offered algorithm list into the transcript. The hybrid combiner includes the ciphertexts and public keys (B.6.2).
4. **No silent fallback.** If the preferred algorithm fails (selftest failure, verification error), the device fails to a defined state (B.4.3) and reports it; it does not retry with something weaker.
5. **Draft algorithms are `PROPOSED`.** They can be shadow-signed (the molting protocol of atlas 11.1) but not authorised (B.1.5).

### B.10.3 Drills (anti-atrophy)

| Drill | Frequency | What it proves | Pass criterion |
|---|---|---|---|
| **Slot drill** (atlas I-13) | Yearly per fleet cohort | A release verifies through the *alternate* assumption class alone | Cohort reports the alternate slot verified; no regression |
| **Algorithm-removal build** | Every release in CI | Product builds and passes tests with each non-baseline algorithm compiled out | Green matrix |
| **Registry-denial rehearsal** | Yearly in a lab fleet | A `DENIED` status record propagates and devices reject the algorithm | 100% of lab devices reject |
| **Quorum-loss rehearsal** | Yearly | An authority change succeeds when one slot is unavailable (F-B1) | Succeeds with the LMS slot off-line |
| **State-recovery rehearsal** | Yearly | Stateful key crash recovery never reuses a leaf | Audit shows monotone leaves |
| **Identifier-change rehearsal** | On each standards change | A COSE/OID mapping update flows without touching descriptors | Mapping table updated only |
| **Checker re-run** | On any registry change | `dq.py`-style check on all policies, per epoch profile and merged-waist | No policy with κ < 2 |

Frequency principle from the atlas: "exercise the change path on a rhythm". [H, from atlas Part 0 and 7.3]

### B.10.4 Sunset ladder

Each algorithm has a published planned path through `ADMITTED → RECOMMENDED → LEGACY_VERIFY → DENIED`, aligned with external dates: NIST IR 8547's 2030 deprecation and 2035 disallowance for quantum-vulnerable public-key algorithms [F via fetch] and the CNSA 2.0 dates [2nd]. Devices carry a signed *exit clock* per legacy exception (atlas I-9).

**LIMITS.** No policy can protect a device whose verifier is immutable and single-family (the atlas's "hard boundary"). Agility policy applies only to devices with a locked stage that has a multi-class slot structure and an updatable second stage.

---

## B.11 Consolidated findings for the merge

1. **Two gaps in the atlas's own rule (F-B1, F-B2).**
   - Every accepted disjoint pair of the three-slot set contains the stateful LMS key. Add a stateless SLH-DSA-SHA2 slot (128 B of slot hashes instead of 96 B).
   - MV-1's single-hash verifier cannot enforce the disjoint rule: it needs a `KECCAK`-class verifier in the locked stage.
2. **Atlas statement "LMS-SHA256 or SLH-DSA-SHA2 → {SHA-256}" is incomplete**: LMS also exists with SHAKE256 (RFC 9858), and SLH-DSA-SHA2 uses SHA-512 at categories 3/5. The descriptor must carry the hash.
3. **Standards moved**: IR 8547 is now final (2026-10-27); RFC 9964, 9881, 9909, 9935 and RFC 10024 are published; FIPS 206 and HQC are still not final or not even drafted; SP 800-230 is IPD with comments closed; PQClean is retired and pqm4 deprecated.
4. **CNSA 2.0 excludes SLH-DSA**, which conflicts with using SLH-DSA-limited-use sets (SP 800-230) in national-security profiles. A profile switch is required in the registry.
5. **The 22 ms / 14.2 KB decapsulation figure** corresponds to the unoptimised implementation; the M4 optimised version needs about 2.8-6.5 KB and about half the cycles.
6. **Counter-capacity**: a 32-bit sampled-values counter wraps in 12.4 days at 4,000 frames/s, so counters must be wider or keys rotated at least daily.

## B.12 Open questions

- What is the flash cost of a Keccak-class verifier in the locked stage on M0+? (Needs measurement.)
- Does CNSA 2.0 approve LMS with SHAKE or SHA-256/192 parameters? (NSA PDF unreachable.)
- Is there any SUIT PQ draft in progress beyond `suit-mti`? (Search found none; the working group chairs should be asked.)
- Real Cortex-M0+/M3 numbers for mlkem-native and mldsa-native portable C (pqm4 data is M4 only and the project is deprecated).
- Masked ML-DSA software on MCUs: none found.
- Final FIPS 206 and FIPS 207 text, and SP 800-230 final sizes. The draft table I recorded (3,856 / 7,752 / 14,944 B) was extracted through a summarising fetch and should be re-read from the PDF.

---

<!-- Appendix D -->
# APPENDIX D

# Stream E: Embedded systems and bootloader design

Scope: everything that runs on constrained devices. Evidence labels follow the brief. Scratch code, test vectors and cloned reference repos are under `/home/claude/atlas2/blueprint/code/E/` (`fs/` = first-stage code, `fs/host/` = tests, `fs/build/measure.sh` = size script, `ref/` = shallow clones of upstream repos used for status checks). Today is 2026-11-06.

Terminology: **FS1** = the locked continuity first stage (atlas 11.1 "MV-1/HA-1"). **S2** = the updatable second stage. **PU** = flash program unit (smallest independently programmable chunk).

## E.0 What was measured, what was estimated (read this first)

| Item | Status | How |
|---|---|---|
| FS1 SHA-256 + SHAKE256 + LMS verifier + journal code size on Cortex-M0+/M4/M33 | **Measured [D-local]** | `arm-none-eabi-gcc 13.2.1` and `clang 18.1.3`, `-Os`/`-O2`, `-ffunction-sections`, `arm-none-eabi-size` (text+data), `fs/build/measure.sh` |
| FS1 per-function stack frames | **Measured (compiler `-fstack-usage`, static)** | gcc M0+ `-Os`; worst-path depth is my sum, so [C] |
| LMS verifier correctness | **Measured**: 21 independent vectors from `pyhsslms 2.0.0` (SHA-256 and SHAKE256; W2/W4/W8; H5/H10) all verify; 903 negative cases (bit flips, wrong message, truncation, altered key) all rejected | `fs/host/test_lms.c` |
| Hash-call counts per LMS verify | **Measured (host, instrumented)** | W4/H5: 473, 563, 503 calls for q=0,1,2; W8/H5: 4,088, 3,833, 5,108; W2/H5: 182 |
| Journal power-fail safety | **Measured (simulation)**: 6,720 cut points (PU = 4/8/16/32, clean cut and torn unit with random bit subsets), 0 violations, never a double-program of a unit | `fs/host/test_journal.c` |
| Cycle counts of FS1 on a real MCU | **Not measured**: no hardware or cycle-accurate model here. Every ms figure for FS1 is [E] from measured block counts times an assumed cycles/block | see E.4 |
| ML-KEM/ML-DSA/SLH-DSA Cortex-M4 cycles, stack, code | **[D] from pqm4 repo** `benchmarks.csv` (clone of 2026-10-23, STM32F4 @ 24 MHz, `arm-none-eabi-gcc 11.3.1`) | read directly |
| M0+ ML-KEM numbers (atlas: "22 ms, 14.2 KB") | **Not verified**: pqm4 has no M0+ target. See E.4 | |
| Energy, LoRa airtime | **[C]** from stated formulas; current draws are **assumptions [E]** | python in E.6 |
| Upstream PQ status (MCUboot, wolfBoot, Nordic, ST, PSA, U-Boot, OpenTitan, etc.) | **[F]** where read from upstream source/docs this session, otherwise "unverified" | E.2 |
| Standards clauses (IEC 61508, 62443-4-2, DO-326A, ISO 26262, IEC 62304, EN 50159) | **Not fetched this session.** Stated from general knowledge, labelled [I], no clause numbers | E.5 |

**Headline measured result.** The SHA-256 + SHAKE256 + LMS-verify + journal core compiles to **3,962 B** (gcc `-Os`, Cortex-M0+), 4,717 B with clang `-Os`. The atlas's "~13 KB" (12,864 B demonstrated verifier plus library) is therefore a conservative budget, not a floor: a complete FS1 with two hash waists fits in roughly 7 KB [E] (measured core + estimated boot logic and glue, E.1.3).

---

## E.1 The locked continuity first stage in implementable detail

### E.1.1 Boot flow

```
RESET
 └─ vendor ROM (if any)  [outside our control; assessed per part, E.3.3]
     └─ FS1 entry (locked flash, reset vector points here)
         0  hal.init; debug_state() -> record; wdt start (window >= worst-case verify, E.5)
         1  journal_load(): scan append-only log -> fs_state{kf, svn_floor, slot[4], lkg}   [no trust in RAM copies]
         2  candidates = {A, B}; order by manifest.svn descending (header read only)
         3  for each candidate:
               parse manifest (fixed layout, length-checked)         -> reject on any field error
               svn >= svn_floor ?  key_epoch >= kf ?                 -> else reject (rollback)
               pick sigblock; pk-hash(sigblock.pk) == slot[sigblock.slot].hash && slot.gen >= kf ?
               alg class derived from pk typecodes (never from a stored flag)
               LMS verify(Hash_alg(manifest))                        (E.1.4)
               hash image under every family the manifest carries; compare
               policy: ANY1 (default C2) or DISJOINT2 (C3 default, E.1.5)
            first success -> state RUN
         4  none -> LKG: hash image at LKG slot; equals journal LKG pin ?  -> state LKG (reduced authority)
         5  none -> BRICK_GUARD: hal.safe_state(); stay in watchdog-reset loop; log; no network, no debug
         6  authority-change bundle present (staging area)?  -> E.1.5 (before step 3, so a new floor applies to this boot)
         7  hal.lock_until_reset()  (journal + FS1 region read-only to S2)  -> hal.jump(slot, entry)
```

State machine states are those of atlas 11.1: BOOT, VERIFY_B (verify via first class), VERIFY_ALT (verify via alternate class), RUN, LKG, BRICK_GUARD. Invariants to model-check in TLA+ (atlas lists a, b, c; I add d and e):
(a) no single-class key reaches ADVANCE_FLOOR; (b) a power cut at any step leaves a bootable image or LKG; (c) the floor never decreases; (d) the lock call precedes every `jump`; (e) journal state is a pure function of NV contents (no RAM-only authority).

**DECISION E-1.** Stage 1 never trusts anything it did not just read from locked NV or verify itself, and never exports services at run time (no SVC/callable API after `jump`). Confirmation of an image is a flag in an *unlocked* swap-state area; FS1 acts on it at the next boot.
WHY: a runtime API would be an updatable-code attack surface inside the germline (atlas pattern 17). ALTERNATIVES REJECTED: TF-M-style secure-service partition in FS1 (large, needs MPU/TrustZone policy, moves the lock boundary). ASSUMPTIONS: S2 cannot write the journal after `lock_until_reset` or permanent lock. TRADE-OFFS: image confirm costs one extra boot cycle. LIMITS: parts with no region lock cannot host FS1 safely (E.3.3). VALIDATE: model check (d), (e); fault-injection campaign on the lock call itself (atlas HA-1). Traces: R1, R2, N20, atlas 11.1.

### E.1.2 Memory map (reference, 512 KB-class M33; scale down per class)

| Region | Size | Lock | Content |
|---|---|---|---|
| FS1 code + rodata | 16 KB (2 x 8 KB pages; budget, ~7 KB used [E]) | permanent or lock-until-reset, region-granular | vectors, FS1, HAL glue |
| Journal | 10 KB for C2/C3 (128 entries x 80 B); 2.5 KB for C1 (32 entries) | writable only by FS1 (lock-until-reset before handover) | append-only log (E.1.4) |
| Swap-state / trial-boot flags | 1 page | unlocked | MCUboot-style trailer; not security state |
| Slot A | size S | unlocked | S2 + app |
| Slot B | size S | unlocked | S2 + app (or staging) |
| Slot R (optional, C3) | small | unlocked, signed | recovery S2, subject to floor |
| LKG pin | in journal (32 B + svn) | | image stays in A or B (the non-active slot is not overwritten until a newer image is confirmed) |

RAM: FS1 uses a single static `fs_state` and one stack, then RAM is zeroed before `jump` (no residue). No heap. `.bss` + `.data` for FS1 = `fs_state` (see below).

### E.1.3 Flash and RAM budget

Measured (gcc 13.2.1, `-Os`, Cortex-M0+; text+data per object, `-ffunction-sections`):

| Module | M0+ gcc -Os | M0+ clang -Os | M4 gcc -Os | M33 gcc -Os | M0+ gcc -O2 |
|---|---|---|---|---|---|
| `fs_hash.c` (SHA-256 + SHAKE256/Keccak-f, incl. 256 B K-table and 192 B round tables) | 1,922 | 2,080 | 2,010 | 2,026 | 2,256 |
| `fs_lms.c` (LMS verify, SHA-256 and SHAKE256 types, W2/4/8, H5-25) | 1,252 | 1,629 | 1,170 | 1,170 | 2,171 |
| `fs_journal.c` (load, append, torn handling) | 788 | 1,008 | 776 | 776 | 928 |
| **Measured core** | **3,962** | **4,717** | **3,956** | **3,972** | **5,355** |

Clang `-O2` on M4 reaches 4,492 B for the hash module alone (loop unrolling): **`-Os`/`-Oz`, not `-O2`, for FS1**; and the gcc/clang spread (~19% on M0+ at `-Os`) is why we build with two compilers (E.8).

Estimated additions (not written or measured): manifest parser, slot table policy, quorum rule, boot state machine, authority-bundle handler: about 200 lines of C; scaling from the journal (about 60 lines for 788 B, ~13 B/line) gives ~2.6 KB, I budget 2.0-2.6 KB [E]. Vector table, startup, HAL glue for one part: ~1 KB [E]. **Total FS1 [E]: 3,962 + 2,600 + 1,000 = ~7.6 KB, call it 8 KB**; with hardware SHA/Keccak the software tables (about 1.5 KB of `fs_hash.c`) can be dropped: ~6 KB [E].

SHA-256-only variant (single waist, class C1/C2 minimum) removes Keccak: roughly 1 KB less [E, not compiled separately].

RAM (stack, measured static frames, gcc M0+ `-Os`):

| Function | Frame (B) |
|---|---|
| `fs_lms_verify` (two hash contexts: one union holds a 208 B SHAKE context) | 688 |
| `fs_sha256_update` (with inlined block, 64 B schedule) | 160 |
| `keccakf` / `fs_shake256_update` | 104 / 32 |
| `fs_journal_load` / `tag_of` | 432 / 160 |
| `fs_journal_append` | 248 |

Worst path: verify 688 + `h_upd` 8 + `sha256_update` 160 = **856 B** [C]; journal path 432 + 160 + 160 = 752 B [C]. Add boot-logic frame ~250 B [E] and `fs_state` static (28 B scalars + 4 slots x 36 B + 32 B LKG hash = ~204 B [C]). **FS1 RAM ~1.3-1.5 KB [E]**, consistent with the atlas's 1-1.6 KB. Using a SHA-256-only build shrinks the 208 B SHAKE context out of the union (~ -200 B per context, two contexts: ~ -400 B) [E].

### E.1.4 Data layouts

```c
/* little-endian; all multi-byte fields fixed-width; no padding assumptions (packed, checked at compile time) */
struct fs_manifest {            /* 112 B */
  uint32_t magic;               /* 'FSM1' */
  uint16_t fmt_ver, flags;      /* flags: HAS_SHA256, HAS_SHAKE256, POLICY_DISJOINT2 */
  uint32_t kind;                /* 1 stage2, 2 authority bundle, 3 lkg-note */
  uint32_t svn;                 /* image security version (anti-rollback) */
  uint32_t key_epoch;           /* must be >= journal kf */
  uint32_t img_len;
  uint8_t  device_scope[16];    /* all-zero = fleet; else UUID (debug credentials, spares) */
  uint8_t  img_sha256[32];
  uint8_t  img_shake256[32];
  uint8_t  rsv[8];              /* = 4+2+2+4+4+4+4+16+32+32+8 = 112 */
};
struct fs_sigblock {            /* variable */
  uint8_t  slot, rsv; uint16_t sig_len;
  uint8_t  pk[56];              /* LMS pk: lms_type|ots_type|I[16]|K[32] */
  uint8_t  sig[];               /* LMS-SHA256 W4 H10 = 2,508 B; W8 H10 = 1,452 B */
};
struct fs_slot  { uint8_t hash[32]; uint32_t gen; };           /* 36 B, 4 slots = 144 B in RAM; commitment = Hash_class(pk) */
```
Signed message for a slot of class `A` is `Hash_A(manifest)` and the manifest carries the image digest under each family a signer uses. This is a point the atlas does not state: **if both signers sign a SHA-256-only digest of the image, a SHA-256 break forges both and the "disjoint quorum" is an illusion.** Each class must sign a digest under its own hash waist, so DISJOINT2 verification hashes the image twice (SHA-256 and SHAKE256) in one pass over flash. [I]

**Slot count: four, not three.** Three live slots (OEM-A, OEM-B, operator) plus one empty position so the molting step "provision alongside" (atlas pattern 15) always has a free slot; otherwise provisioning a replacement requires first retiring a live key. +36 B. [H]

**Assumption class is derived from the verified public key, never stored.** `fs_lms_pk_alg()` maps typecodes to SHA2 or Keccak; the quorum test uses bitmasks (SHA2 = 1, KECCAK = 2, LATTICE = 4; ML-DSA = LATTICE|KECCAK because it uses SHAKE internally). A stored class flag could be altered by a slot-replacement bug; a derived one cannot disagree with the key.

**Journal entry** (append-only; `fs_journal.c`): HDR(16: magic `4A 31`, type, slot, seq, arg0, arg1) | PAY(32) | TAG(16 = first 16 B of SHA-256(HDR||PAY)) | VOID(16). Each region rounded up to PU: entry size 80 B for PU = 4, 8, 16; 128 B for PU = 32. Types: FLOOR (arg0 = kf, arg1 = svn floor), SLOT (slot, arg0 = gen, PAY = new hash), LKG (arg0 = svn, PAY = image hash).

Write order PAY, HDR, TAG. **TAG is the commit point.** Valid iff the tag matches, VOID is all-zero, `seq == previous + 1`. Anything else non-empty is torn: it is skipped, counted, and **frozen** by programming VOID. Scan ends at the first all-zero entry. `fs_journal_append` re-reads NV after the commit so RAM state is always derived from NV.

**DECISION E-2 (journal).** Append-only log, every PU programmed exactly once, no erase in the baseline mode (JM-A). Optional rotate-with-erase mode (JM-B, below) for erasable flash only.
WHY: (1) Many NOR parts with ECC allow one program per 16-byte word between erases: write-once-per-unit is the only discipline that is legal on all of them [I; per part datasheet]. (2) Interrupted program leaves a bit-subset of the intended value, so a tag that must equal an exact value cannot be satisfied by a partial write; no erase means no half-erased sector. (3) The state is monotone, so the safe states are exactly "before" and "after".
Capacity arithmetic [E]: over 25 years: initial slots 3 + floor advances ~5 + slot replacements ~4 + LKG pins ~25 (one per confirmed update, assumed 1/yr) + torn-write debris ~4 = **41 entries**; 2x margin (rule E.7) = 82; provisioned 128 entries x 80 B = **10 KB**. For C1 (no LKG pin): 3 + 5 + 4 + 4 = 16, x2 = 32 entries = **2.5 KB**.
ALTERNATIVES REJECTED: (i) in-place two-copy counter with CRC: needs erase or rewrite, which has the torn-page failure mode and on ECC flash is illegal; (ii) hardware monotonic counter only: tiny, but no slot data and not portable; (iii) single unary fuse thermometer for everything: cannot hold 32 B hashes.
ASSUMPTIONS: HAL normalises polarity so unprogrammed = 0 (E.3). A torn unit may read back unstable for a while; VOID plus the exact-tag rule make the late flip of a marginal bit harmless: a torn entry's tag cannot become valid, and VOID has 128 bits, any set bit voids it.
TRADE-OFFS: 10 KB of flash that can never be reclaimed. LIMITS: when the log is full, `append` returns -3 and the device stays in its last committed state (safe-fail) and reports exhaustion; recovery is replacement. VALIDATE: `test_journal.c` (done); TLA+ model of append/recover; physical torn-program characterisation per part family (not done).

**Power-fail cases (measured by simulation, 6,720 runs):** cut before HDR, between HDR and TAG, or with a torn TAG unit: state = pre-state exactly; cut after TAG: state = post-state exactly; after any debris a subsequent append succeeds.

**JM-B (rotate with erase), specified, not implemented.** Two or more journal sectors; sector header with sector-seq and SNAP_DONE unit. When active sector is full: write a snapshot of live state (4 slots + floor + LKG = 6 entries) into the next sector, program SNAP_DONE, *then* erase the old one. Boot picks the highest-seq sector with SNAP_DONE. Needs `FS_CAP_NV_ERASE_JOURNAL` and lock-until-reset on journal sectors. Adds about 400-600 B and two proof obligations [E]. It gives unbounded lifetime on flash with erase, at the price of the one non-monotone operation inside the germline. Given 41 entries over 25 years, wear is irrelevant (endurance is not the limit; the capacity budget is), so **JM-A is the default and JM-B is a profile option only for assets planned beyond 40 years**. [I]

**Medium analysis.**

| Medium | Write semantics | Fit | Notes |
|---|---|---|---|
| NOR flash with ECC word (e.g. 16 B) | erase to all-ones, program once per word | JM-A native; PU = 16 | HAL inverts polarity. Torn program is a real case. |
| NOR flash 4-byte words, 2 programs/word allowed | | JM-A with PU = 4 | Entry = 20 PUs. Do not rely on 2nd program. |
| OTP / UICR OTP | program once, no erase | JM-A native, capacity fixed | Best for 4 slot hashes + thermometer floor; NSIB-style parts (below) |
| eFuse | bit-wise one-way, ms program, may need factory-only voltage | thermometer for kf only; slots in flash journal | usually too small for hashes; per-part |
| FRAM | in-place rewrite, huge endurance | JM-A works unchanged; in-place counters tempting but break monotonicity under lock failure | use append anyway |
| RRAM/MRAM | in-place, unit-write | as FRAM | per-part ECC/write-buffer behaviour: check datasheet |

A fuse/OTP-first variant for parts with enough OTP: slots (4 x 32 B = 128 B), plus a replacement bank (4 x 32 B), a 64-bit floor thermometer and a 1-bit-per-slot "use replacement" flag: ~264 B OTP [C]. Prior art: Nordic's immutable bootloader library stores lifecycle state, hashes of public keys, invalidation tokens and a monotonic counter in OTP, or in internal flash with write blocked before the next image runs [F, `sdk-nrf doc/nrf/libraries/security/bootloader/bl_storage.rst`, clone 2026-11-04]. Nordic counters use a multi-slot scheme, my design differs in carrying 32 B payloads and a commit tag.

### E.1.5 Authority changes (floor advance, slot replacement)

Floor advance `ADVANCE_FLOOR(from_kf -> new_kf, new_svn)`:
1. Bundle `kind=2` signed by a quorum; each signature over `Hash_class(bundle)`; bundle names `from_kf`, must equal current `kf` (replay protection: kf is strictly increasing so a bundle is single-use).
2. Quorum Q = signers whose slot has `gen >= new_kf` (survivors) and whose `pk` hashes to the slot commitment. Valid iff Q contains two members with disjoint assumption masks (`a.mask & b.mask == 0`).
3. Retiring slot k is done *by* raising kf above `slot[k].gen`; slot k may not sign its own retirement (it is not in Q).
4. Append FLOOR entry; reload; continue boot.

Slot replacement `REPLACE_SLOT(slot, from_gen, new_hash, new_gen)`: same quorum, `new_gen >= kf`, `from_gen == slot[slot].gen` (single-use per generation). PAM rule (atlas 11.2): a bundle that would install a hash equal to a *current* live slot's, or revoke a current slot without escrow-class evidence, is structurally rejected. Single entry, single commit: atomic.

**DECISION E-3 (independence needs independent verifier code).** In FS1 the independent quorum classes are **SHA-2 (LMS-SHA256) and Keccak (LMS-SHAKE256)**, verified by the *same locked code*. The atlas HA-1 puts ML-DSA verification in the second stage "under the slot's key hash". That does not give independence: whoever breaks SHA-2 can forge the S2 signature, replace S2 with a version that reports "ML-DSA valid", and the lattice member of the quorum is then not independent. An ML-DSA member counts as independent only if its verifier is in locked flash (pqm4 clean ML-DSA-65 verify code is 7,724 B .text [D], plus the SHAKE it already shares) or in hardware with its own lock (Caliptra's Adams Bridge, vendor ROM). [I]
WHY: independence is a property of the *trust path*, not the key. ALTERNATIVES REJECTED: SLH-DSA-SHAKE in FS1 (signature 7,856 B and, per pqm4, SHAKE-128s verify costs 24.4M cycles on M4 [D]); lattice in FS1 on C2 (7.7 KB flash and 9.9 KB (m4f) or 2.7 KB (m4fstack) stack, at 2.4M-5.7M cycles [D]); both only at C3/C4 with enough flash. ASSUMPTIONS: LMS-SHAKE is acceptable to the policy authority (SP 800-208 defines the SHAKE typecodes; typecodes cross-checked against pyhsslms 2.0.0, which I did not verify against the SP text directly [I]). TRADE-OFFS: both slots in FS1 are stateful hash-based, so the index-reuse hazard (R6) is concentrated at the authority side; mitigated by HSM index reservation and by using the leaf budget only for rare authority and root-level signing (atlas 11.1 interim note; SP 800-230 draft limited-use SLH-DSA is [F, IPD April 2026, `csrc.nist.gov/news/2026/nist-releases-draft-sp-800-230`] a later option). LIMITS: this is atlas correction candidate C-E1 (E.11). VALIDATE: quorum checker (atlas E-N3) as a property test over the slot table.

**LMS parameter choice for FS1 [E-derived from measured counts]:**

| Param set | Signature | Avg hash calls (measured, H5) | Notes |
|---|---|---|---|
| W4, H10 | 2,508 B | ~510 (+~5 for H10) | atlas default; 1,024 leaves |
| W8, H10 | 1,452 B | 3,800-5,100 | 8x slower in software, 1.7x smaller; choose only with HW hash |
| W2, H10 | 4,460 B (H5 measured 4,460 B... at H5; H10 = 4,620 B) [C] | 182 | for very slow cores; LoRa-hostile |

(`4+4+32+133*32+4+10*32 = 4,620 B` for W2/H10 [C]; the measured 4,460 B above is H5.)

---

## E.2 Integration review (what to reuse, wrap, avoid)

Method: shallow clones of upstream repos (dates below) grepped for PQ algorithm support, plus primary documentation fetched this session. "Unverified" means I did not read a primary source for the claim.

| Component | PQ status found | Evidence | Verdict |
|---|---|---|---|
| **MCUboot** | **No PQ in main.** Clone of 2026-10-29 (HEAD `420a2d5`) has no LMS/ML-DSA/XMSS in docs, Kconfig or source. A commit `c6aeaf9` by a contributor adds `docs/lms.md` describing LMS verification (Mbed TLS 4.x, imgtool, bootloader verifier); it is **not in the cloned HEAD**, so treat as an unmerged branch or PR, date approximate (~May 2026) | [F: repo grep; WebFetch of the commit] | **Wrap, do not depend.** MCUboot's image format, trailer, swap and upgrade logic are good S2/app-level material. FS1's journal and quorum stay outside it. Track the LMS work and align `imgtool` manifest fields. |
| **wolfBoot 2.10.0** (clone 2026-11-04) | **ML-DSA (44/65/87), LMS/HSS, XMSS/XMSS^MT**, hybrid classic+PQ mode (e.g. ML-DSA-65 + ECC-384) via a secondary signature; docs `docs/PQ.md`; `docs/FIPS.md` states PQ options are out of scope of its FIPS statement | [F: repo files] | **Reuse as S2 and as a reference/diff target**; strongest open-source PQ boot today. Not suitable as FS1: monolithic, flash footprint in the tens of KB (unmeasured), no disjoint-quorum floor rule, no append-only journal. Adopt its config naming where possible. |
| **TF-M** (Arm) | Unverified this session (my clone attempt of the mirror failed). PSA Crypto API has PQC extension (below); TF-M adoption not checked | none | Reuse PSA crypto *API shape* for S2/app; FS1 does not use TF-M. Verify TF-M release notes before claiming support. |
| **PSA Certified Crypto API** | **PQC Extension 1.4: Final 0 and Final 1 exist**; covers ML-KEM, ML-DSA, SLH-DSA, and LMS/HSS and XMSS/XMSS^MT *verification and public keys*; document history lists no dates | [F: `arm-software.github.io/psa-api/crypto/1.4/ext-pqc/appendix/history.html`] | **Adopt as the S2/app crypto API** (E.3.4). FS1 keeps its own two-function verify (`fs_lms_verify`). |
| **Nordic NSIB / nRF Connect SDK** | NSIB (`b0`) signature choices in `sysbuild/Kconfig.secureboot`: **ED25519, ECDSA, NONE only**. PQ is in the PSA/CRACEN driver: ML-DSA-44/65/87 sign+verify and ML-KEM-512/768/1024 for CRACEN, SHAKE in CRACEN on nRF54L (release notes 3.5.0-preview4); LMS/HSS/XMSS public-key types exist as PSA options; Oberon PQC marked experimental in 3.4.0 notes | [F: sdk-nrf clone 2026-11-04] | **Reuse patterns, not code.** NSIB's OTP key hashes + invalidation tokens + monotonic counter are the closest prior art to FS1. Gap: no PQ verifier in the immutable stage. |
| **ST OEMiRoT / SBSFU / X-CUBE-PQC** | **X-CUBE-PQC**: LMS and XMSS verification "mainly for secure boot", ML-KEM, ML-DSA; **STM32H563 (Cortex-M33) only; status NRND**, ST points to X-CUBE-CRYPTOLIB; page does not mention OEMiRoT/SBSFU | [F: `st.com/en/embedded-software/x-cube-pqc.html`] | OEMiRoT/SBSFU PQ status **unverified**. Treat ST as: PQ verify libraries exist for one part, root-of-trust integration not shown. Hardware lock features (RDP/HDP/WRP) are what FS1 needs; per-part check (E.3.3). |
| **Zephyr** | Unverified this session. Uses MCUboot (above); PSA crypto via Mbed TLS/TF-M | none | Target as an *OS* for S2/app; FS1 independent of it. |
| **FreeRTOS-Kernel** | No PQ strings in the kernel repo (clone 2026-10-29) | [F: grep] | Kernel is not the place for crypto; use with wolfSSL/PSA libs. |
| **Eclipse ThreadX / NetX Duo** | No ML-DSA/ML-KEM/LMS/XMSS strings in `threadx` or `netxduo` clones (2026-11-01) | [F: grep] | Same as FreeRTOS. ThreadX's value is its safety-certification lineage (unverified specifics). |
| **Arm PSA Certified** | Certification levels cover the crypto API conformance; whether an evaluated profile covers PQ is unverified | partial | Record certificate IDs in the part profile (E.3.3), do not infer PQ. |
| **OpenTitan** | Earl Grey ROM docs: "required to support hybrid signature schemes for secure boot ... ECDSA-P256-SHA256 and SLH-DSA" | [F: `sw/device/silicon_creator/rom/doc/sigverify.md`, clone 2026-10-09] | **Align**: OpenTitan validates the hybrid-with-SLH-DSA approach in silicon ROM. Use its SLH-DSA test keys format as an interop target. |
| **Caliptra** | Repo README lists `lms-types`; Caliptra 2.0/2.1 added Adams Bridge ML-DSA/ML-KEM accelerator (atlas 8.5, [F] per atlas; not re-verified here) | [F partial] | **Wrap as a RoT backend** via the HAL `verify` capability for C4/C5 and SoC-class parts. |
| **U-Boot** | Bundled Mbed TLS 3.6.0 contains **LMS verify (LMS_SHA256_M32_H10 only, per its ChangeLog)**; no ML-DSA in U-Boot docs/boot; wiring of LMS into verified boot not found | [F: grep of clone 2026-11-05] | Linux-class: use U-Boot as S2, put FS1-equivalent in vendor ROM or locked SPL, see E.9. |
| **RAUC / Mender** | No PQ strings in clones (2026-11-05 / 2026-10-28) | [F: grep] | Wrap: they carry artifacts; signatures verified by our policy layer. |
| **SWUpdate** | Kconfig option `CMS_REQUIRE_HYBRID_PQC`: requires at least one classic and one PQ (ML-DSA, SLH-DSA) CMS signer, with a stated stripped-signer downgrade rationale; depends on OpenSSL | [F: `crypto/Kconfig`, clone 2026-11-02] | **Reuse the idea** (and the downgrade threat note) as a policy template; best-positioned Linux updater found. |
| **systemd, UEFI, Linux kernel module signing** | Not checked this session | none | Unverified: E.9 treats them as interfaces only. |

**DECISION E-4 (integration stance).** FS1 is standalone C with a six-function HAL; nothing from MCUboot/TF-M/Zephyr is linked into it. Upstream projects are integrated at **S2 and above** through (i) the PSA crypto PQC extension API, (ii) the manifest and sigblock formats being a superset-compatible profile for MCUboot/wolfBoot image headers, (iii) a conformance adapter per bootloader. WHY: every dependency inside the germline becomes unfixable. ALTERNATIVES REJECTED: forking wolfBoot as FS1 (size, licence entanglement [GPLv3 vs commercial, unverified], no quorum logic); wrapping TF-M BL1 (needs ROM or TrustZone). ASSUMPTIONS: wolfBoot/MCUboot keep their PQ work upstream. LIMITS: the version-field mapping (svn vs kf) must be negotiated with each project. VALIDATE: golden-image interop tests (E.3.5).

---

## E.3 Hardware abstraction layer

### E.3.1 Contract

Header: `fs/fs_hal.h` (written; C99, freestanding). Required: `nv_read`, `nv_prog` (with `FS_CAP_NV_PROG_ONCE`), `img_read`, `lock_until_reset`, `jump`. Optional: everything else; absent hooks degrade features, never silently.

| Function | Needed by | Contract |
|---|---|---|
| `nv_read(off,dst,n)` | journal | **Polarity-normalised: unprogrammed = 0, programmed = 1.** Idempotent. |
| `nv_prog(off,src,n)` | journal | OR-semantics; `off, n` multiples of `nv_pu`; each unit programmed at most once; returns on completion; power loss may leave a bit-subset of `src` OR-ed in. |
| `nv_erase(off)` | JM-B | optional |
| `img_read/img_map` | verify | no side effects |
| `lock_until_reset` | handover | after return, S2 cannot program/erase FS1 or the journal; verified by read-back of the vendor lock register where possible |
| `wdt_kick`, `safe_state` | boot | `safe_state` drives outputs to declared safe state before BRICK_GUARD |
| `debug_state` | evidence | CLOSED/OPEN/AUTHENTICATED/UNKNOWN is *recorded* in the first signed state report; FS1 does not enforce |
| `rng` | **not used by FS1** | present for the contract; verification needs no entropy (a property worth keeping: no RNG failure can break boot) |
| `rtc_read(unix, uncert)` | reports | returns a window (E.7); never authority |
| `ctr_read/ctr_inc` | optional hardware counter | cross-check of kf where present |
| `sha256_blocks`, `keccak_f1600` | speed | replace the software block function |
| `caps` bits | | 13 defined in `fs_hal.h` (`NV_PROG_ONCE`, `NV_ERASE_JOURNAL`, `LOCK_UNTIL_RESET`, `LOCK_PERMANENT`, `NV_MARGIN_READ`, `HW_SHA256`, `HW_KECCAK`, `HW_CTR`, `RTC`, `RNG`, `WDT`, `DEBUG_QUERY`, `IMG_MEMMAP`) |

**DECISION E-5 (HAL = data + function table, ABI-versioned).** `fs_hal.abi == 1`, struct is append-only (new fields at the end, `abi` bumped), no callbacks with varargs, no ownership transfer. WHY: FS1 can never be recompiled in the field, but S2 and the HAL tables can be, so the ABI must be stable for decades. ALTERNATIVES REJECTED: link-time weak symbols (hard to test, silent fallbacks); Rust traits (not C-linkable for vendors). VALIDATE: ABI test compiled with both compilers asserting `offsetof/sizeof` of `fs_hal` identical.

### E.3.2 Porting guide (10 steps)

1. Fill a **part profile** (E.3.3) from datasheets and certificates, with source per field.
2. Choose layout (E.1.2) aligned to the lock granularity; if the lock cannot protect FS1+journal as one region, split, but then each region needs its own lock.
3. Implement `nv_*` with polarity inversion for NOR; confirm PU and that the same unit is never written twice (ECC).
4. Implement `lock_until_reset` using the vendor's write-protect-until-reset feature (or permanent lock for FS1 code; journal must remain programmable by FS1 only).
5. Implement `img_read` (and map).
6. Wire `jump`: clear RAM, set VTOR, set MSP, branch.
7. Run **HAL contract tests** (below) on target.
8. Run the **power-cut rig**: toggle power at randomised times during journal append over thousands of cycles; check recovery.
9. Run the conformance vectors (LMS vectors above; image vectors) through a real boot.
10. Archive the profile, test logs and binary hash in the CBOM entry.

### E.3.3 Machine-readable part profile

Format: TOML (human editable, schema-validated, signed when published). Physical-resistance class is a **data field with a source and a date, never a claim by us**.

```toml
schema = "part-profile/1"
part = { vendor = "…", family = "…", core = "cortex-m33", rev = "…" }
nv = { kind = "nor", program_unit = 16, ecc_single_program = true, erase_unit = 8192,
       polarity = "erased_ones", otp_bytes = 0, journal_ok = "JM-A" }
lock = { granularity_bytes = 8192, until_reset = true, permanent = true,
         survives_lifecycle = ["RMA"= "unknown"], source = "ref-manual §…, 2025-xx" }
hash = { sha256_hw = true, keccak_hw = false, source = "…" }
counters = { hw_monotonic_bits = 0 }
debug = { states = ["closed","open","authenticated"], pq_credential_supported = false }
evidence = [ { scheme = "…", level = "…", lab = "…", cert_id = "…", scope = "…", date = "…", source = "URL" } ]
physical_resistance = { class = "unknown|none-claimed|vendor-claimed|independently-evaluated",
                        source = "…", date = "…", note = "absence of evidence is not proof" }
```
Rules: fields without a source are `unknown`; `physical_resistance.class` can only be `independently-evaluated` if a `cert_id` is present; the profile is hashed and recorded in the device's CBOM entry (atlas 8.2, 8.10 rule 4). No attack procedure, parameter or cost appears anywhere in a profile (brief rule 3).

### E.3.4 HAL contract tests (conformance suite "HCT")

Runs on target via a tiny test image; reports through `log`. Items:
- **T1 polarity**: fresh unit reads 0; after programming 0xFF.. reads 1s.
- **T2 program-once**: HAL must refuse or report the second program of a unit (profile-declared); test records vendor behaviour.
- **T3 OR-semantics and alignment**: unaligned write rejected.
- **T4 torn-write rig**: 5,000 randomised power cuts during `nv_prog`; check that reading back yields a subset of intended bits, and that `fs_journal_load` recovers (the `test_journal.c` invariants on silicon).
- **T5 lock**: after `lock_until_reset`, an S2-privilege write to FS1 region and journal region must fail; check from an unprivileged probe image. Also check that the lock survives a warm reset path the vendor documents as preserving it (profile field).
- **T6 hash KATs** for the accelerators vs software; **T7 LMS vectors** (the 21 vectors + 903 negatives from this stream).
- **T8 watchdog** reset-in-time test; **T9 debug_state** truth table; **T10 rtc** monotonicity.
- Gate: a port is "FS1-certified-by-us" only with T1-T7 green, with the log attached to the profile.

---

## E.4 Device classes C0-C5: concrete profiles

Data used (all pqm4, STM32F4 Cortex-M4 @ 24 MHz, gcc 11.3.1, repo clone 2026-10-23, [D]):

| Scheme (impl.) | Cycles | Stack B | .text B | Time @24 MHz | @64 MHz [C] |
|---|---|---|---|---|---|
| ML-KEM-768 decaps (m4fspeed) | 707,827 | 6,452 | .text 16,016 | 29.5 ms | 11.1 ms |
| ML-KEM-768 decaps (m4fstack) | 714,194 | 2,844 | .text 13,320 | 29.8 ms | 11.2 ms |
| ML-KEM-768 decaps (clean C) | 1,387,984 | 14,480 | | 57.8 ms | 21.7 ms |
| ML-KEM-768 encaps (m4fspeed) | 658,754 | | | 27.4 ms | 10.3 ms |
| ML-DSA-65 verify (m4f) | 2,415,944 | 9,888 | 19,328 | 100.7 ms | 37.7 ms |
| ML-DSA-65 verify (m4fstack) | 5,732,397 | 2,712 | 24,120 | 238.9 ms | 89.6 ms |
| ML-DSA-65 verify (clean) | 3,377,305 | 57,736 | 7,724 | 140.7 ms | 52.8 ms |
| SLH-DSA-SHA2-128s-simple verify (sphincs-sha2-128s clean) | 7,471,794 | 1,968 | 5,264 | 311 ms | 116.7 ms |
| SLH-DSA-SHAKE-128s-simple verify | 24,366,771 | 1,872 | 4,492 | 1,015 ms | 380.7 ms |

(Note: stack rows from the pqm4 memory section: ML-KEM-768 decaps 14,480 B clean, 6,452 B m4fspeed, 2,844 B m4fstack; .text for ML-KEM-768 m4fspeed is 16,016 B from the size section. Conversion to 64 MHz assumes no flash wait-state penalty [E]; pqm4 measured at 24 MHz to avoid wait states.)

**Atlas check.** Atlas 11.3: "decapsulation costs 22 ms and 14.2 KB of stack on an M0+". pqm4's *clean C* ML-KEM-768 decaps on a **Cortex-M4** shows 14,480 B stack, which matches the 14.2 KB order of magnitude, so the stack figure is plausible for an unoptimised build; the 22 ms is of the same order as clean-C cycles at 64 MHz on M4 (21.7 ms), but I found **no M0+ primary source**. Flag: the M0+ figure is unverified [I]; an M0+ has no single-cycle 32x32->64 multiply, so lattice code is expected slower than on M4 (factor to be measured, not asserted).

LMS (measured block counts, E.1; cycles/block assumed). The atlas card gives 41.5 ms for W4 software at 64 MHz = 2.66M cycles. With ~560 compression blocks average (calls + 33 extra blocks for the 2,166 B public-key hash + ~10 for 2-block Merkle nodes [C]) that implies ~4.7k cycles per SHA-256 block, the figure I use throughout (assumption [E]; a tuned M0+ implementation may be lower; mbedTLS-class C is plausibly at this order, unverified).
- W4/H10 average ≈ 560 blocks x 4.7k = 2.63M cycles = **41 ms @ 64 MHz, 55 ms @ 48 MHz, 164 ms @ 16 MHz**. Worst case (all 67 chain digits maximal: 1,005 chain steps + 34 + ~22) ≈ 1,061 blocks = 4.99M cycles = **78 ms @ 64 MHz** [C]. This worst case sets the watchdog budget.
- W8: measured 3,833-5,108 calls (avg ~4,350 + ~45) x 4.7k ≈ 20.7M cycles = 323 ms @ 64 MHz average [C].
- HW SHA-256 at an assumed 300 cycles/block including driver overhead [E]: 560 x 300 = 168k cycles = 2.6 ms @ 64 MHz.
- Image hash (done at every boot): size/64 blocks. 64 KB: 1,024 blocks = 75 ms (sw) / 4.8 ms (hw) @ 64 MHz; 256 KB: 301 / 19 ms; 512 KB: 602 / 38 ms; 1 MB: 1.2 s / 77 ms [C, E assumptions as above]. **Image hashing, not signature verification, dominates boot latency on C2/C3**, so a hash engine is worth more than a faster verifier.
- SHAKE256 (Keccak) software: not benchmarked; estimating 24 rounds x ~700 cycles = ~17k cycles per f-1600 permutation on M0+ [E, weak], ~570 permutations -> ~10M cycles = 150 ms @ 64 MHz; make a Keccak engine or the hash-first design (E.1.4) optional for the second class on C1/C2.

Per-class profile (modules linked; flash/RAM from measured and estimated data):

| Class | Typical MCU | Modules linked | Flash (FS1 + libs) | RAM | Verify / boot latency (arithmetic above) |
|---|---|---|---|---|---|
| **C0** inert | no crypto | none; enclave inventory only | 0 | 0 | n/a. Replacement date in CBOM. |
| **C1** symmetric-only (M0+/M0, 16-64 KB flash) | LoRaWAN/802.15.4 node | HAL, `fs_hash` SHA-256 only (~1 KB less than 1,922 [E]), AES-CMAC/GMAC from vendor lib; **optional** FS1 LMS (W4/H10) if updatable | MAC-only: 0 KB FS1; FS1-SHA256-only: ~5 KB [E: 3,962-1,000+2,600+1,000]; journal 2.5 KB | ~1.0 KB stack (verify 688 minus SHAKE ctx ~480 + hash 160 [E]) | LMS verify 55 ms @ 48 MHz [E]; image hash 32 KB: 512 blocks = 2.4M cycles = 50 ms @ 48 MHz |
| **C2** verify-capable (M4/M33, 256 KB-2 MB) | PLC I/O, RTU, IED | FS1 (SHA-256 + SHAKE, journal 10 KB), PSA crypto in S2 incl. ML-KEM-768 decaps once, optional ML-DSA-65 verify in S2 | FS1 ~7.6 KB (8 KB) + journal 10 KB = **~18 KB**; S2 ML-KEM 6-10 KB .text [D, size section] + ML-DSA 8-24 KB [D] | FS1 ~1.4 KB; S2 PQ ops 3-10 KB transient (m4fstack 2.8 KB decaps; ML-DSA-65 verify 2.7-9.9 KB) | boot: hash 256 KB image 19 ms (hw) to 301 ms (sw) @ 64 MHz + LMS 2.6-41 ms; ML-DSA-65 verify 38 ms (m4f) @ 64 MHz in S2 |
| **C3** safety-critical | protection relays, SIS | C2 + LKG pin, DISJOINT2 policy (both hashes; both LMS verifies), crypto partition (E.5), signed settings | FS1 ~8 KB + journal 10 KB; DISJOINT2 needs 2 LMS verifies | FS1 1.4 KB, **crypto runs only in boot/update, never in control loop** | worst case: 2 x 78 ms + 2-pass image hash; budget declared per product in WCET table; must complete before the control task start deadline; boot is not a control period |
| **C4** concentrators (A-class, Linux) | gateways, KDCs, historians | full stacks; TLS/IKE hybrids (liboqs/wolfSSL/OpenSSL), TPM; see E.9 | MBs | MBs | ms |
| **C5** authorities | HSMs | out of embedded scope (Streams A-C) | | | |

**C0-C1 guard (dominance rule, atlas 12.2):** FS1 never accepts an authority change from a lower-class device; FS1's input is a signed bundle only, so a C1 gateway/relay path cannot present anything but bytes, and quorum check decides. [I]

---

## E.5 Real-time and safety coexistence

**DECISION E-6 (crypto is a boot-and-update service, never a control-loop dependency).** On C3: all public-key operations are confined to FS1 and an S2 "update agent" task that is **not schedulable above the control task**; run-time process-bus security is symmetric (atlas 11.3). WHY: EN 50159-style separation: the safety layer sees authenticated frames, the crypto layer can be replaced without reopening the safety case (atlas Part 0 item 3). ALTERNATIVES REJECTED: PQ signatures per message (SV at 4,000 frames/s leaves 250 us per frame vs 12-41 ms for one LMS verify, 49-164x over budget [C]); crypto co-processor shared with control. ASSUMPTIONS: MPU or TrustZone separates the update agent. LIMITS: the update agent can still starve the CPU unless bounded. VALIDATE: WCET measurement of the update task and a schedulability proof with it as the lowest-priority, preemptible task.

Mechanisms:
1. **Partitioning.** MPU regions: S2 update agent (crypto + parsers) in its own unprivileged partition with fixed RAM; control task cannot be written by it; crypto never takes a lock the control loop needs.
2. **Watchdog budget.** Window W must exceed worst-case FS1 time: `T_boot,max = T_hash(image) + n_verifies x T_LMS,max + T_journal`. For a 256 KB image at 16 MHz, sw hash: 4,096 x 4.7k / 16M = 1.20 s; LMS worst 1,061 x 4.7k / 16M = 312 ms (x2 for DISJOINT2) [C] -> watchdog (or kick calls inside the hash loop every N blocks, N = 64 ~19 ms @ 16 MHz) so that a hung hash cannot starve the dog. FS1 kicks `wdt_kick` between verifier phases, not inside primitives.
3. **Deterministic WCET.** All FS1 loops are bounded by table constants (p <= 133 chains (W2), 2^w-1 <= 255, h <= 25, image blocks <= img_len/64); no data-dependent early exit in the signature check except the final compare; no recursion; no heap; no function pointers except the fixed HAL table. Report: WCET table by `(alg, W, H, image KB)` generated from block counts (above), and *measured on silicon* per part before certification [not done].
4. **Fail-safe.** BRICK_GUARD calls `safe_state`; LKG keeps control running with network authority removed (senescence, atlas 11.6); no state where a control output depends on a signature check *result* at run time.
5. **Certification-friendly library requirements** (what the library must provide; labels [I] - the standards were not fetched this session, no clause numbers asserted):

| Requirement | Why a certifier asks | FS1 status |
|---|---|---|
| No dynamic allocation | IEC 61508 / ISO 26262 software constraints on dynamic objects | **Met** (no malloc; stack and static only) |
| No recursion, bounded loops | WCET and stack analysis | **Met by construction**; to be proven by tool (Frama-C/CBMC) |
| Static stack bound | resource analysis | **Measured** frames above; add whole-call-graph tool |
| MISRA C:2012/2023 conformance, with a deviation log | typical project coding standard in IEC 61508 SIL 2+, ISO 26262 ASIL | **Not yet checked** (no MISRA checker available here); known deviations: union in hash context, `memcpy`, packed structs |
| Static-analysis evidence (clang-tidy/Frama-C/Polyspace/cppcheck) | evidence of absence of run-time errors | planned; 0 cppcheck/clang run yet [not done] |
| Test evidence with coverage (MC/DC for ASIL D / DAL A / SIL 4) | structural coverage | 903 negative + 21 positive LMS vectors, 6,720 journal cuts are functional only; coverage not measured |
| WCET table | timing analysis | estimated above, silicon measurement pending |
| Traceability requirement -> code -> test | all standards | this memo's IDs (E-n) and atlas IDs |
| Tool qualification of compilers | ISO 26262 tool confidence, IEC 61508 | E.8: two compilers + qualified commercial option |
| Safety manual and "assumptions of use" | SEooC (ISO 26262), IEC 61508 route 1s/2s | to write per profile |
| Separation of security and safety lifecycles | IEC 62443-4-1/-4-2, DO-326A airworthiness security process | design keeps crypto out of safety function; mapping tables are a Stream F matter |
| IEC 62304 (medical): SOUP | software of unknown provenance record | FS1 is first-party, but wolfSSL/PSA libs in S2 are SOUP: record version, anomaly list |

**Position on library certification.** The first stage is small enough (one verifier, <1,000 lines) to qualify as a **SEooC/pre-certified component** with an assumptions-of-use list (lock call, polarity, PU rule); the S2 PQ stack is not (tens of KB, upstream-owned): certify the *interface* and its partitioning, not the lattice code.

---

## E.6 Power and bandwidth

Assumptions (labelled): active current **4 mA at 3.0 V at 48 MHz** for an M0+-class part (typical order, [E], no datasheet cited); LoRa transmit **40 mA** and receive **10 mA** at 3.3 V (typical order, [E]); CR2032 nominal 225 mAh x 3 V = 2,430 J [I].

**Compute energy** E = V x I x t:
- LMS W4/H10 verify, software, 48 MHz: 2.63M cycles / 48 MHz = 54.8 ms; 3.0 x 0.004 x 0.0548 = **0.66 mJ** [E]. Worst case 78 ms @ 64 MHz scaling to 104 ms @ 48 MHz: 1.25 mJ.
- With HW SHA at 300 cycles/block: 560 x 300 = 168k cycles = 3.5 ms: **0.042 mJ** [E].
- ML-KEM-768 decaps (once), M4 24 MHz measured 707,827 cycles = 14.7 ms @ 48 MHz; at 4 mA, 3 V: **0.18 mJ**; if M0+ is 2.5x slower [E, unverified factor]: **0.44 mJ**.
- Image hash 32 KB (512 blocks): 2.4M cycles at 48 MHz = 50 ms = **0.60 mJ**.
All are below 1 mJ. 2,430 J / 0.66 mJ = 3.7M verifications [C]: **compute is irrelevant to battery life; radio dominates**.

**Radio:** LoRaWAN at SF10/125 kHz, 51 B application payload per frame (consistent with the atlas card 24 frames for an ML-KEM-768 key, 65 for ML-DSA-65: 1,184/51 = 23.2 -> 24; 3,309/51 = 64.9 -> 65 [C]). Time on air for a 64 B PHY payload (51 + 13 B header) at SF10: 698 ms; SF7 118 ms; SF12 2.79 s [C, Semtech formula, CR 4/5, 8-symbol preamble, CRC on, explicit header; I did not re-verify against Semtech's calculator]. Artifact delivery:

| Artifact | Bytes | LoRa frames @51 B | Airtime SF10 | Time at 1% duty | 802.15.4 frames @~88 B payload [E] |
|---|---|---|---|---|---|
| LMS W4/H10 signature | 2,508 | 50 | 34.9 s | 0.97 h | 29 |
| LMS W8/H10 signature | 1,452 | 29 | 20.3 s | 0.56 h | 17 |
| ML-DSA-44 signature | 2,420 | 48 | 33.5 s | 0.93 h | 28 |
| ML-DSA-65 signature | 3,309 | 65 | 45.4 s | 1.26 h | 38 |
| SLH-DSA-128s signature | 7,856 | 155 | 108.2 s | 3.01 h | 90 |
| ML-KEM-768 encaps key | 1,184 | 24 | 16.8 s | 0.47 h | 14 |
| ML-KEM-768 ciphertext | 1,088 | 22 | 15.4 s | 0.43 h | 13 |

(Duty-cycle column uses 1% as the EU868 sub-band order; applies to *uplink*; class-A downlinks are limited by gateway duty cycle and RX windows instead. I did not verify regional rules this session.) Energy for a device *receiving* 50 downlink frames: 50 x ~1 s x 10 mA x 3.3 V = **1.65 J** [E] vs 0.66 mJ to verify: **2,500x**. Uplink of an ML-KEM key (24 frames x 0.698 s x 40 mA x 3.3 V) = **2.2 J** [E].

**DECISION E-7 (C1 over LoRa: do not ship PQ signatures to the node).** For C1 nodes, authenticate via the diversified symmetric key; do enrolment with ML-KEM *at the gateway* (atlas 11.3; N10) and deliver firmware only as hash-chained differential updates verified against an FS1-anchored manifest delivered once per release, never per fragment. WHY: 50 frames x 0.7 s per signature. ALTERNATIVES REJECTED: SLH-DSA on node (155 frames, 7.9 KB); per-fragment signature. LIMITS: a full image at 51 B/frame (a 64 KB image = 1,285 frames, 15 min of airtime at SF10 [C]) is operationally hard; the unit that matters is *delta size*.

**Update delta strategies** [I/H unless noted]:
1. **Hash-chained fragments** (each fragment carries the hash of the next; manifest signed once): O(1) signature overhead; classical block authentication; needs in-order delivery or a Merkle tree. Merkle tree with 64-B leaves: proof depth log2(1,024) = 10 hashes x 32 B = 320 B per fragment for a 64 KB image, which is more than the fragment, so chain, not tree, for LoRa. [C]
2. **Differential (bsdiff/Janpatch-class, or block-level) updates** decoded by S2 into the inactive slot; signature covers the *result* hash, so the delta itself need not be signed, but the delta must be *bound* to the base hash to avoid applying to the wrong base. Typical size reduction depends on the change; unmeasured here.
3. **Crypto-only updates** kept separate from functional updates (atlas 11.5, N48): an authority-change bundle (floor/slot) is ~270 B + signatures: bundle 112 B + 2 x 2,508 B sigs = 5,128 B = 101 LoRa frames [C]; for C1 this is why C1 holds no FS1 authority and relies on the gateway.
4. **Staged dormant** download (atlas 11.5) during window prep; activation is a single flag.

---

## E.7 Time handling on devices

**Zeitgeber-stack API** (S2/library, not FS1; FS1 only *reports* the window):

```c
typedef struct { int64_t earliest, latest; } fs_tw;        /* seconds since 1970-01-01, signed 64-bit */
typedef enum { ZG_RTC, ZG_COUNTER_ORDER, ZG_BOOT_REMANENCE, ZG_NET_AUTH, ZG_GRID, ZG_GNSS,
               ZG_TECH_TOKEN, ZG_PEER } fs_zg_kind;
typedef struct { fs_zg_kind kind; uint8_t indep_class; int64_t t; uint32_t uncert_s; } fs_zg_cue;
void fs_time_init(fs_tw *w, int64_t epoch_lo, int64_t epoch_hi, uint32_t drift_ppm);
void fs_time_tick(fs_tw *w, uint32_t elapsed_oscillator_s);       /* widens by drift_ppm */
int  fs_time_propose(fs_tw *w, const fs_zg_cue *cue);            /* 1 narrowed, 0 recorded-only, <0 reject */
int  fs_time_report(const fs_tw *w, uint8_t out[24]);            /* fixed-width signed-report field */
```
**Fusion rule (atlas I-23, 6.5) as code semantics:** window widens at the drift bound; a cue **inside** the window narrows it; a cue **outside** is recorded and ignored **unless at least two cues of different `indep_class` agree** on the new position; time never grants authority: no function in FS1 or the library takes a `fs_tw` as input to advance a floor or change a slot. Window report goes into the signed state report. [H, from atlas]

Drift budget arithmetic (atlas M4 [C], recomputed): 20 ppm x 31,557,600 s/yr = 631 s/yr; -164 ppm worst-case cold = 5,175 s/yr = 86 min; over a decade 14.4 h. Window width after one year with 20 ppm = ±631 s; if validity rules use month-sized epochs the window is far smaller than the epoch. Use coarse epochs (months).

**Monotonic epoch counters**: floor `kf`, `svn_floor` live in the journal; "epoch" semantics are ordinal, not temporal; replay protection uses `from_kf` in bundles.

**Counter-capacity rule (atlas 6.6, E.7 rule)**: for every counter write capacity C, consumption rate r per year, asset life L; require C >= 2 r L.

| Counter | Capacity | Rate | Life | Required | Verdict |
|---|---|---|---|---|---|
| journal entries (JM-A) | 128 | ~1.6/yr | 25 | 82 | pass (1.56x of requirement, 3.1x of expected 41) |
| `kf` (u32 in entry arg0) | 2^32 | 0.2/yr | 40 | tiny | pass |
| LMS h = 10 leaves | 1,024 | rare root signing: ~12/yr | 25 | 600 | pass; nightly signing (365/yr) fails at 2.8 yr (atlas 21.1) |
| fuse thermometer 64 bits | 64 | 0.2/yr | 40 | 16 | pass |
| `time_t` | signed 64-bit | | | | pass; signed 32-bit ends 2038-01-19 03:14:07 UTC |
| GPS week (10-bit) | 1,024 weeks ≈ 19.7 yr | | | next rollover 2038-11-20 (atlas, unverified here) | interpret GPS with pivot date from the build epoch plus the window |

**Y2038/GPS rollover-safe types:** `int64_t` seconds everywhere; GPS weeks stored as 16-bit absolute week-since-1980 reconstructed from the 10-bit field using the window's `earliest` as pivot (valid while true time is within ±512 weeks of the pivot); never `time_t` in a wire struct; compile-time `_Static_assert(sizeof(int64_t)==8)`; CI test injects dates 2038-01-19, 2038-11-20 and 2106-02-07 (u32 end). "No expiry" = notAfter 99991231235959Z as defined value (atlas 6.6, RFC 5280).

---

## E.8 Language strategy for the device side

Options compared:

| Option | Pros | Cons | Fit |
|---|---|---|---|
| **C99/C11 subset, MISRA/CERT, formal-verified** | universal vendor toolchains (every MCU), ABI stable for decades, vendors will link it, WCET tools target it | memory-safety is by discipline and analysis | **FS1 and HAL** |
| Rust `no_std` | memory safety, good for S2 parsers | thumbv6m/v8m support OK (targets installed here), but vendor SDKs C-only; qualification (Ferrocene) exists but unverified here; panic paths, ABI instability beyond `extern "C"` | **S2/app parsers, gateway, tools** |
| Ada/SPARK | proof of absence of RTE, safety heritage | small vendor ecosystem, few RTOS ports, hiring | optional for C3 vendors |
| Verified C extraction (F*/Low*, HACL*; libcrux) | machine-checked memory safety/functional correctness | extraction output is big, build chain heavy | **candidate for the hash/LMS core later**; mlkem-native already uses CBMC proofs of memory safety and HOL-Light proofs for assembly (AArch64/x86_64) [F: mlkem-native README, clone 2026-11-04]; no Cortex-M assembly proof claimed |
| Verus/Rust | verification inside Rust | young, not for C vendors | research |

**DECISION E-8.** FS1, HAL, journal, manifest parser = **C99 subset** (no VLAs, no recursion, no heap, no function pointers except the HAL table, fixed-width types only, `-Os`), verified by (1) deductive proofs with Frama-C/WP or CBMC bounded model of the parser, journal and the quorum rule; (2) the host-side differential tests (done) against an independent implementation (pyhsslms, done) and later a second independent C implementation written by a different team ("implemented twice", atlas 11.1); (3) two-compiler builds. S2 parsers and update agent: **Rust `no_std`** where the vendor allows, with `extern "C"` ABI to the C HAL. WHY: the germline's audience is vendor toolchains for 30+ years; the updatable layers can adopt safer languages. ALTERNATIVES REJECTED: Rust FS1 (no vendor toolchain guarantee; proof tooling for Rust embedded immature [I]); SPARK FS1 (adoption friction); Low*-extracted FS1 (size, build chain) but the *hash and LMS code paths* should be re-based on verified extraction when size permits. ASSUMPTIONS: C compilers 25 years out still accept C99. TRADE-OFFS: C leaves memory-safety to analysis. LIMITS: proofs are not done (state machine and parser: not started). VALIDATE: proof artifacts published with code.

**FFI/ABI stability:** `fs_hal` and all FS1 interfaces are plain C structs with explicit widths and an `abi` field; Rust bindings generated by `bindgen` from the same header, not hand-written; no C++ in any public interface; no `bool`/enum width assumptions on the wire (use `uint8_t`/`uint32_t`).

**Toolchain qualification and compiler diversity.** The evidence from this session: two compilers produce different code size for the same source (e.g. M0+ `-Os`: gcc 3,962 B vs clang 4,717 B; M4 `-O2` clang's hash module 4,492 B vs gcc 2,160 B) [measured]. Policy: (1) FS1 binary is built with **both** gcc and clang; both must pass the full vector suite on target and host (host test passes with gcc 13.3.0 x86-64; I did *not* run the Thumb binaries on target or in an emulator this session); (2) release uses one compiler, the other is a differential check of semantic equivalence by test, not by bit equality; (3) compiler version and flags are pinned in the CBOM; reproducible builds; (4) for C3 products a qualified commercial compiler (IEC 61508 / ISO 26262 tool qualification, availability unverified) replaces one of the two; (5) check the object code for the lock call and the polarity inversion at binary level (compilers may reorder or elide).

---

## E.9 Linux-class devices and gateways (C4, A-class SoCs)

Architecture (high level; component statuses from E.2):
- **FS1-equivalent for Linux-class SoCs**: the immutable stage is the vendor ROM plus a locked SPL/BL2 holding the same slot table and floor concept; FS1 can run as the locked SPL if the SoC provides OTP and a lock. The key-hash slots and floor can live in OTP/fuses (E.1.4 fuse variant) where ROM supports PQ hash tables; otherwise the SPL carries the verifier. U-Boot as S2/BL33: bundled Mbed TLS has LMS verify (SHA-256, H10 only, per ChangeLog [F]) which is a verifier source for LMS-signed FIT images but not a floor mechanism.
- **Updaters** (RAUC, SWUpdate, Mender): wrap, do not fork. SWUpdate's `CMS_REQUIRE_HYBRID_PQC` [F] demonstrates the dual-signature policy that also defeats stripping one signer; adopt that semantic for every Linux updater: **an artifact is valid only if all required classes verify, evaluated by the policy layer, not by counting signatures present**.
- **Measured boot / attestation**: record PQ evidence in CBOM and TCG/IETF RATS formats (atlas 11.7); TPM-based keys per atlas (TPM 2.0 v1.85; not re-verified here).
- **Gateways as keystone nodes (atlas 12.4)**: C4 gateways terminate PQ TLS/IKE hybrids for C0/C1 enclaves; hold per-device KEK diversification via HSM/TPM, never a fleet key. They run full libraries (wolfSSL/OpenSSL/liboqs; ML-KEM-768 decaps ~1 ms on A-class [E] without a benchmark here).
- **UEFI/systemd** (ESP signing, sd-boot, dm-verity measured boot): status of PQ in UEFI Secure Boot and in the Linux kernel module-signing path was **not verified** this session; plan: treat as interfaces; require that any UEFI db/dbx change on C4 gateways be authorised by the same quorum, and that dm-verity root hashes use SHA-256 + SHA-3 in the manifest.
- **Time on gateways**: authenticated time (Roughtime or authenticated PTP) feeds `fs_time_propose` with `ZG_NET_AUTH`; two independent classes (net + GNSS plausibility + tech token) needed to move the window.

**DECISION E-9.** On Linux-class devices, A/B + RAUC/SWUpdate/Mender remain the update mechanism; the **policy layer** (the library's `verify_artifact()` with required-class set) replaces the signature check, and journal/floor state lives in OTP, RPMB or a TPM NV index with write-once semantics. ALTERNATIVES REJECTED: replacing the updater. ASSUMPTIONS: the SoC offers OTP or RPMB. LIMITS: RPMB/NV-index semantics differ per part (profile field). VALIDATE: the SWUpdate-style downgrade/stripping test as an acceptance test.

---

## E.10 Measured data and honest limits

**Methodology.** Source in `code/E/fs/`. Cross-compile: `arm-none-eabi-gcc 13.2.1 (Ubuntu 15:13.2.rel1-2)`, and `clang 18.1.3` with `--target=thumbv6m/thumbv7em/thumbv8m.main-none-eabi`, headers from newlib. Size = `arm-none-eabi-size` text+data of each object (includes rodata tables, excludes startup, vector table, libc `memcpy`/`memset` stubs: **on M0+ gcc may emit calls to `memcpy`/`memset` from libc that are not counted**; add ~100-200 B if the build must supply them [E]). Stack from `-fstack-usage` static frames. Test on host: gcc 13.3.0 x86-64 `-std=c99 -pedantic`.

**What was *not* done:** running the Thumb binaries (no emulator or hardware); cycle measurement; the boot state machine, manifest parser and bundle handler are *designed, not implemented*; no MISRA/Frama-C/CBMC run; no SHAKE timing; no PSA/TF-M integration test.

**Reproduce:** `sh code/E/fs/build/measure.sh`; `cd code/E/fs/host && python3 -I gen_vectors.py vec && gcc -O2 -std=c99 -o test_lms test_lms.c ../fs_lms.c ../fs_hash.c && ./test_lms vec`; `gcc -std=c99 -O1 -o test_journal test_journal.c ../fs_journal.c ../fs_hash.c && ./test_journal`.

## E.11 Findings against the atlas and open questions

1. **C-E1: second-stage ML-DSA verification (atlas 11.1 HA-1) does not give an independent quorum member** (E.1.5). Independence needs the verifier in locked flash or in separately locked hardware. Fix: quorum classes in FS1 are SHA-2 and Keccak via LMS-SHA256/LMS-SHAKE; ML-DSA gives agility at S2 and independence only with a locked verifier.
2. **C-E2: "~13 KB" is a conservative budget**: measured core is 3,962 B (gcc M0+ -Os); complete FS1 estimated ~8 KB (E.1.3). Keep 16 KB allocated for growth; the dominant locked-flash cost is actually the **journal (10 KB)**, not the code.
3. **C-E3: quorum messages must be hashed per class.** A shared SHA-256 digest of the image makes a SHA-2 break forge both signers (E.1.4).
4. **C-E4: "22 ms and 14.2 KB stack on an M0+" for ML-KEM-768 decaps is not supported by pqm4**, which has no M0+ target; on M4 clean C the stack is 14,480 B and time 21.7 ms @ 64 MHz; the stack-optimised M4 build uses 2,844 B.
5. **C-E5: slot count 4 not 3** to allow "provision alongside" without retiring a live key.
6. **MCUboot has no merged PQ support in main as of 2026-10-29** (a docs-only LMS commit exists elsewhere); wolfBoot 2.10.0 is the only open boot-loader found with merged ML-DSA/LMS/XMSS and hybrid. NSIB's immutable bootloader is still ECDSA/ED25519.

Open questions: (a) actual cycle/stack of FS1 on M0+/M33 silicon with and without HW SHA; (b) per-part lock semantics survive warm reset, RMA and debug re-enable (the side-door audit; needs the part-profile corpus); (c) whether SHAKE/Keccak without hardware is too slow for C1/C2 second-class verification (~150 ms estimated, unbenchmarked) and whether SP 800-230 limited-use SLH-DSA or LMS-SHAKE is the better second waist; (d) status of TF-M, Zephyr, ST OEMiRoT/SBSFU, UEFI/systemd/Linux PQ support (unverified); (e) formal proof of the journal and quorum rule; (f) confirm the SHAKE LMS typecodes against SP 800-208 text itself (cross-checked only with pyhsslms).

---

<!-- Appendix E -->
# APPENDIX E

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

---

<!-- Appendix F -->
# APPENDIX F

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

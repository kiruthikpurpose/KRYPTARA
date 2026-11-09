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

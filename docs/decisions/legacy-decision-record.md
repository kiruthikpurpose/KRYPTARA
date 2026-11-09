<!-- Title: Legacy decision record D/C/X/J (Rev 4) -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L2. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 20. Architectural decision record

This is the contract of the project. **Decided** means we build it. **Conditional** means we build it only if the named experiment passes, with a stated fallback. **Research** means we do not depend on it. **Rejected** means we considered it and chose not to, with the reason. Status against Rev 2: **NEW**, **CARRIED** (unchanged), **AMENDED** (changed as stated) or **REVERSED**.

### 20.1 DECIDED: what we are building

| ID | Status | Decision | Why | Alternatives considered |
|---|---|---|---|---|
| **D-21** | NEW | The foundation is a **governed-change kernel**: Evidence, Rule, Record, Effect behind a three-surface frozen waist | Covers G1–G24 with one rule; each primitive removes a named failure class (§4.6) | V1–V6 (§5.1): algorithm library, PKI, update framework, ledger, hardware root, perimeter |
| **D-22** | NEW | **Evidence atoms**: ≤ 8 per device, kinds SIG, PRES, WIT; label word per atom; assumption labels *derived by the device* from the verifier descriptor; group, site and infrastructure labels declared at T2; duplicate key hashes rejected | Classes, not signatures, determine safety; deriving assumption labels removes one way to lie | Counting signatures (fails on shared assumptions); declared assumption masks (can lie); > 8 atoms (J-27) |
| **D-23** | NEW | **On-device interval admission.** A table is installed only if monotone and Lo ≤ f ≤ U (and f ≤ f_old when tightening), with U and Lo computed on the device from labels | Theorem 1: exact characterisation; closes G13 and G14; 682 B (Rev 4; now 902 B hardened, see CHANGELOG) [M] | Host-only lint with structural device checks (J-32); fixed rule compiled into the locked stage (no evolvability); a policy interpreter (J-09) |
| **D-24** | NEW (replaces the D-05 rule table) | **Tiers with explicit fault budgets.** T0 HALT; T1 OPERATE (1,1); T2 CONSTITUTION recoverable (1,2) by default for terrestrial profiles; remote and nano variants (§4.2). Re-keying a group lives in exactly one tier per profile | Theorem 3: the weakest full-control path is the security level, so budgets must be explicit | One uniform "two groups" rule (Rev 2: governance loss 39% over 40 years [M]); per-action ad-hoc rules (unauditable) |
| **D-25** | NEW | **Presence is an evidence atom**, sampled by the locked stage at reset from an input firmware cannot drive. It is required for T2 in terrestrial profiles and never sufficient alone | The only non-cryptographic class available everywhere on Earth; its cost scales per device; it restores safety and liveness under a family loss (Theorem 2) | Treating presence as a process note (unanalysed); presence-only recovery (J-33) |
| **D-26** | NEW (amends D-10) | **Publicity atom.** Devices verify witnessed receipts themselves (≥ 2 independent logs; C2SP checkpoint, cosignature and witness formats; RFC 9162 inclusion proofs). Publicity is modelled as exposure, never prevention, and every authorising evidence set without presence must include it, in every profile. On-site sets may omit it only with extra custody diversity, to stay live during log outages, and such acts appear in the next witnessed state report. Devices never *query* a log | Converts covert authority into visible, vetoable authority (G9); a gateway can no longer feed an unlogged transition | Gateway-held receipts only (Rev 2); counting witnesses as preventive (J-25) |
| **D-27** | NEW (reverses part of D-05) | **Code is authority.** The locked stage boots only the image digest committed by an authorised `ACTIVATE_IMAGE`. The OEM signature is provenance checked at STAGE | Red-team: one OEM key could otherwise run arbitrary second-stage code on every device | Boot any OEM-signed image ≥ floor (J-31) |
| **D-28** | NEW | **History is a chain**: per-device hash-chained transitions, verified under the policy in force at each link; domain separation by action, tier, target, previous head, epoch and format; jump transitions allowed at the highest replaced tier | Removes the join-versus-chain ambiguity; replay and catch-up are exact | Order-free join-set state (J-28) |
| **D-29** | NEW (amends D-11) | **Halt budget**: one custody atom (or local presence) may halt one named bundle; at most *h* halts per atom per epoch; cancelled by a T1 RESUME; never lowers a floor | Bounded veto: a stolen halt key cannot freeze a fleet | Unscoped one-signer halt (J-12); halts expiring only by epoch, which an attacker can stall (red-team X.7) |
| **D-30** | NEW | **Stale devices.** Every accepted chain ends at a fresh witnessed checkpoint. With a trusted RTC, authority-tier catch-up older than window W requires presence. Stated bound: safe against one class break during sleep | Long-range attacks are structural (§3.7) | Silent catch-up from any valid chain (unsafe across sequential breaks) |
| **D-31** | NEW | **Renewal invariant and class lifecycle.** Keep ≥ t + s + 1 live classes per tier; `DECLARE_CLASS_DEAD` is a T1 tightening; NIST IR 8547 dates become label-retirement dates; PQ migration is class retirement | Turns migration from an event into a maintained invariant | Big-bang algorithm swaps |
| **D-32** | NEW | **Recovery is the T2 recoverable tier**: presence + two custody atoms + (publicity or a second custody group) + delay. The lint refuses any configuration in which a single declared loss makes governance unrecoverable | Custody loss is the dominant 40-year risk; presence makes recovery single-fault safe | Break-glass by all three groups (not live after any loss); escrow timers on device (time would grant authority) |
| **D-33** | NEW | **Ceremony records**: label declarations come from a machine-readable custody graph (who holds which key in which HSM, wrapped by what) captured by `ac-ceremony` and logged with the T2 transition | Labels are the closed world. Making them evidence-backed and public narrows the gap (red-team X.2.2) | Hand-written labels |
| **D-34** | NEW | **Reference layouts**: dual-terrestrial 8-atom layout (OEM, OWNER, ESCROW × SHA-2/Keccak, PRES, WIT); nano and remote variants (§5.7) | Gives vendors one audited default | Per-vendor layouts |
| **D-35** | NEW (extends D-20) | Tables stored with complements; every authorisation evaluated twice with complementary encodings | A single bit flip on the decision path must not authorise | Plain tables |
| **D-36** | NEW | **Dog-fooding**: the project's own releases are governed by the same tiers, logs and ceremonies | Credibility and continuous testing of the governance tools | Conventional release signing |
| **D-37** | NEW | **Claims discipline**: novelty claimed only for the composition (§12); theorems presented as applications of classical results; every number reproducible (§21) | Reviews showed earlier over-claims | — |
| D-01 | CARRIED | Hourglass with a pure-function kernel; waist = `ac_step` + crypto table + platform table | Small, provable, portable (S 4.48 [M]) | A1–A6 (§5.2) |
| D-02 | CARRIED | No device holds fleet-scale or authority signing keys; device-scoped reporting key only if C-02 | One opened device yields no fleet authority | — |
| D-03 | AMENDED | Minimal on-device state: atom states EMPTY / ACTIVE / RETIRED; anergy and molting off-device. **Amendment:** assumption labels are on-device in all profiles, derived from descriptors | TLC lockout counterexample (~465k states) [M]; admission needs labels | Rev 2 kept masks only in host tools |
| D-04 | AMENDED | Profiles: {nano, dual} × {terrestrial, remote} (§5.7) | Different physical realities, different budgets | One profile for all |
| D-05 | AMENDED | Custody groups (OEM, OWNER, ESCROW), claim, transfer, sovereign exit and PAM revocation semantics retained. Rules expressed as tier tables (D-24); single-OEM boot reversed (D-27) | Same goals, now provable | — |
| D-06 | CARRIED | NV contract with `torn_read` profile; OTP/counter/FRAM preferred | Hardware hazard confirmed from vendor sources | Universal fault-handler trick (rejected in Rev 2) |
| D-07 | CARRIED | Zero-crypto safety core as preferred C3 pattern | Recertification and interference | Software partition primary (J-08) |
| D-08 | CARRIED | Device-echo two-person commit for settings | Custody is not intent integrity | Workstation quorum as boundary (J-06) |
| D-09 | CARRIED | ML-KEM-768 enrolment, online or pre-encapsulated token | Offline-capable keying | Fleet keys |
| D-10 | AMENDED | Reuse the standards stack; devices never *query* a log but do verify receipts (D-26) | — | — |
| D-11 | AMENDED | Staging = haltable activation order, now with halt budget and resume (D-29) | Twin: halt is the mechanism that works (0.15% vs 2.3%) [M] | Staging without halt |
| D-12 | CARRIED | Providers: mlkem-native, mldsa-native; own verify-only LMS and SLH-DSA; no PQClean/pqm4/liboqs in firmware. ML-DSA carries the Keccak label | Maintained code; independence honesty | — |
| D-13 | CARRIED | C99 subset with two compilers + Rust `no_std` twin + Python model | Systematic-fault defence | Single implementation |
| D-14 | AMENDED | Assurance as design, plus mechanised Theorems 1–3, CBMC equivalence of admission, independent re-implementation from spec | The theory is now load-bearing | — |
| D-15 | CARRIED | Port owners own ports; conformance suite and part-profile registry | 40-year maintenance | Project maintains all ports |
| D-16 | AMENDED | Sectored containment with dated exit; **gateways run the kernel as governed devices** | Containment inherits the same guarantees | — |
| D-17 | AMENDED | Planner and exposure-years KPI, plus the governance-loss simulator and label-retirement schedules | Makes budgets visible to procurement | — |
| D-18 | CARRIED | Counter capacity lint; time may only restrict authority | G23, G24 | — |
| D-19 | AMENDED | Two settings tiers; widening a safety envelope is a T2 action (presence) | A remote quorum cannot widen physical limits | — |
| D-20 | CARRIED | Verification hygiene: public inputs only, redundant complementary checks, resumable verification with locked-stage re-decision | — | — |

### 20.2 CONDITIONAL: build only if the experiment passes

| ID | Status | Idea | Gate | If it fails |
|---|---|---|---|---|
| C-01 | CARRIED | Dual profile as default for C2 | E-B1 and EXP-18 | Nano + presence; residual documented |
| C-02 | CARRIED | Device-scoped one-time report signatures | EXP-03 | Gateway-witnessed reports |
| C-03 | CARRIED | Install-time verification with stored root | Lock assessment; boot budget | Full verification each boot |
| C-04 | CARRIED | Hold-in-reset external supervisor | E-C1 | D-07 only |
| C-05 | CARRIED | Port-level enforcer reference design | E-S1 | Sectored gateways only |
| C-06 | CARRIED | ML-DSA verifier in the locked stage (atom labels LATTICE + KECCAK) | E-B1b | Lattice not an independent atom |
| C-07 | CARRIED | PQ FDO voucher profile | FIDO engagement | Own off-device profile |
| C-08 | CARRIED | Replaceable trust cartridge | Vendor pilot | None needed |
| C-09 | CARRIED | Persister cohort default | E-F1 calibration | Option, off by default |
| C-10 | CARRIED | Merkle-page tiered image verification | E-P1 | Whole-image hashing |
| C-11 | CARRIED | Hash-chain beacons for activation and halt on narrowband links | Delay/isolation review | Signed orders only |
| C-12 | AMENDED | Canary tripwires; a trip performs `DECLARE_CLASS_DEAD` (tightening only) | Cryptographer review | Ordinary T1 declarations |
| C-13 | AMENDED | Optical or local token port, now also a presence form | E-O1, EXP-15 | Wired port |
| **C-14** | NEW | **Fortress constitution (2,1)** as a fleet option; re-keying moves into the 2-safe tier | Fleet risk assessment; govsim acceptable at calibrated hazards (EXP-14) | Recoverable T2 (default) |
| **C-15** | NEW | **RTC trust-age window W** for catch-up | Parts with battery-backed RTC; EXP-12 | Bound stated without window; procedural re-claim of dormant spares |
| **C-16** | NEW | **Third cryptographic class for remote fleets** (an Ascon-based or AES-based hash-signature instantiation; SP 800-232 Ascon is final [F], but no standardised signature instantiation exists) | EXP-18-style independence review; verifier fits; a standards path | Remote fleets choose freeze (safe) or declared degraded mode (live) per fleet |
| **C-17** | NEW | **Log personality enforcing one successor per device head** (honest-log prevention of forks by a compromised quorum) | Design review on Tessera personalities | Detection by monitors only |

### 20.3 RESEARCH: we do not depend on these

| ID | Status | Question |
|---|---|---|
| X-01 | AMENDED | Threshold and distributed hash-based signing *inside* custody atoms. Now published (Kelsey–Lang–Lucks 2025, peer reviewed) with 2026 preprints; dealer, state size and DKG limits remain |
| X-02 | CARRIED | Universal STARK or bytecode verifier on devices |
| X-03 | CARRIED | Hardware diff token with independent parsers |
| X-04 | CARRIED | RAM-shadow patching of orphaned non-safety RTUs |
| X-05 | CARRIED | Formal model of SHA-2 / Keccak independence (EXP-18 is the practical step) |
| X-06 | CARRIED | Masking for ML-KEM/ML-DSA on Cortex-M |
| X-07 | CARRIED | Real fault correlation in OT rollouts |
| X-08 | AMENDED | Witness and log institutions that last decades; now load-bearing for exposure |
| X-09 | CARRIED | Runtime-assurance envelopes (safety function, not locked stage) |
| X-10 | CARRIED | Zero-knowledge fleet posture proofs |
| X-11 | CARRIED | Shared-physical-noise ratcheting |
| X-12 | CARRIED | Hardware side-channel countermeasures for device secrets |
| X-13 | CARRIED | Cross-device gossip for equivocation |
| **X-14** | NEW | Device-side fork uniqueness via verifiable maps small enough for microcontrollers |
| **X-15** | NEW | Proximity-bounded presence (distance bounding) against remote-hands relays |
| **X-16** | NEW | Delays without trusted time (verifiable-delay functions, witness time) on constrained devices |
| **X-17** | NEW | Evidence for label truthfulness: attested HSM provenance, provable custody graphs |
| **X-18** | NEW | Cross-domain transfer pilots (§19.4) |

### 20.4 REJECTED: considered and deliberately not built

| ID | What | Why not |
|---|---|---|
| J-01–J-23 | CARRIED from Rev 2: Vision III MPC as *the* mechanism; bearer vouchers; neutral custodian utility, new-ROM licensing, threshold ML-DSA succession; in-place flash reprogramming; on-device anergy/molting; workstation quorum as boundary; gateway-only containment for high-value assets; software partition as primary C3 argument; policy interpreters; OR-hybrids; dynamic loading below the waist; unscoped halt; KEM challenge-response as evidence; hardware product lines; 150 mW RJ45 enforcer; live patching on SIL devices; analog correlator authentication; shared-noise ratchet; hash-chain reveal as signature; device-level cross-vendor witnessing; per-device diversified binaries; control-barrier evaluator in the locked stage; sealed second-stage "verified" flag | Reasons as recorded in Rev 2 §4.4, still valid |
| **J-24** | Claiming two-fault safety for full control while any single-fault-safe recovery path exists | Theorem 3: the weakest full-control path is the security level |
| **J-25** | Counting publicity (logging, witnessing) as a preventive factor | Logging is not consent; witnesses cosign whatever is appended |
| **J-26** | Any rule in which time grants authority (including on-device escrow release timers) | Clocks fail and are forged; D-18 |
| **J-27** | More than 8 atoms, or general formula interpreters, on device | Loses exhaustive checkability and auditability; nest structures inside atoms instead |
| **J-28** | Order-free join-set authority state | Policy depends on order; the chain gives exact replay |
| **J-29** | Unbudgeted one-signer veto | Fleet freeze by one stolen key |
| **J-30** | Single-family degraded mode as the default for terrestrial fleets | Presence path is both safer and more survivable (govsim 1.0% vs 9.9% [M]) |
| **J-31** | Boot authorised by one OEM signature | Single key runs arbitrary code fleet-wide; reversed by D-27 |
| **J-32** | Host-only policy validation with structural-only device checks (the earlier red-team's compromise) | Leaves G14 open; the full check costs 682 B (Rev 4; now 902 B hardened, see CHANGELOG) |
| **J-33** | Presence as sufficient alone for any non-halt action | One insider would suffice |
| **J-34** | Two-party (two-group) governance designs | Theorem 2: cannot be single-fault safe and single-loss live |

---


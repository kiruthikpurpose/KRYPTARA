<!-- Title: Executive summary (Rev 4) -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Reviewed against the R2 red-team findings on 2026-11-12; conflicting passages were corrected in place (see CHANGELOG).

# 0. Executive summary

### 0.1 The opportunity

Industry describes the coming decade as "post-quantum migration": replace RSA and elliptic-curve signatures with ML-DSA, SLH-DSA, LMS or XMSS before a cryptographically relevant quantum computer exists. For long-lived machines that framing is too small and slightly wrong. A pump controller, protection relay, meter, vehicle ECU, implant, satellite, package registry or archive lives 15 to 50 years. Over that span the algorithm may break, but so may the hash function under it. The vendor may vanish, the owner may change, keys will be lost and stolen, the device may sit offline for a decade, and the people who understood the system will retire. Each of these is handled today by a different mechanism: secure boot, update frameworks, key rotation, PKI, ownership vouchers, escrow contracts, vendor support, physical recall. Each is designed separately and each has its own failure modes, and the side doors between them are where incidents live.

**The deeper problem we found** is that all of these are one problem: *governed change of an artefact that outlives its makers, its custodians and its cryptography.* The question is always the same. Who may change what this machine trusts? What evidence must they show? How does the machine know? And how does it recover when a party, an assumption or a place fails?

**The opportunity** is to make that question have one answer, small enough to put in a locked boot stage and precise enough to prove. Post-quantum migration then becomes one instance of it: retiring a broken assumption class while keeping authority safe and live. So do ownership transfer, vendor exit, key rotation, debug unlock, safety-limit changes, decommissioning and resurrection.

### 0.2 The foundation, in one paragraph

We will build a **governed-change kernel**: four primitives behind a frozen waist. **Evidence:** up to eight *evidence atoms*, each something the locked boot stage can check itself. An atom is a signature under a stored key hash, physical presence at the device, or publication in a witnessed log, and each carries *labels* naming what it depends on: custody group, cryptographic family, site. **Rule:** for each tier of power, a monotone policy stored as a 256-bit truth table over those atoms, *admitted on the device itself* only if it lies inside a lattice interval computed from the labels. **Record:** a monotone authority state (epochs and floors that only rise, keys that can only be retired), extended by a hash-chained, per-device transition history that a device asleep for years can replay. **Effect:** every change is staged, delayed, haltable by any one custodian and activated only by quorum, and every change made without physical presence is published before it takes effect. The waist is three frozen interfaces: `ac_step(state, message) → (state', intents)`, a crypto-provider table and a platform table. Everything else, from algorithms and transports to formats, storage, fleet services and user interfaces, is replaceable data or replaceable code above or below the waist.

### 0.3 What makes it a foundation rather than a product

Three results, each checked by exhaustive or randomised computation, give the design its shape. Each is stated precisely in §3.

1. **The interval theorem [P][M].** Describe what an adversary can do in one fault, and what loss the system must survive, as families of atom sets. Then the policies that are both *safe* (no single fault authorises) and *live* (the survivors of any single loss can still act) are exactly the monotone functions in one lattice interval **[Lo, U]**. That interval is non-empty if and only if no compromise set and loss set together cover every atom, a mixed form of the Q² condition from general-adversary multiparty computation. Admission therefore reduces to `monotone(f) ∧ (f & ~U) = 0 ∧ (Lo & ~f) = 0`. The C implementation computes U and Lo on the device from the labels. It took **682 bytes in Rev 4; 812 bytes after the red-team R2 hardening; 902 bytes with the projection function (arm-none-eabi-gcc -Os, Cortex-M0+, measured 2026-11-09; stack not re-measured; these figures are stale and the current size is unmeasured, see CLM-07)** of Cortex-M0+ code with an 88-byte worst-case stack, and it matched an independent Python reference on 3,000 random cases.
2. **The class-count law, or diversity budget [P][M].** Suppose evidence falls into *k* independent classes and the system must resist *t* compromised classes while remaining live after *s* lost classes. A policy exists if and only if **k ≥ t + s + 1**. Two custody groups can never give single-fault safety and liveness; three can. Two hash families can never give safety against one break and liveness after one break; adding physical presence as a non-cryptographic class can.
3. **Every recovery path is an attack path [P].** The effective security of a device is the weakest path to full control, so for full control *t_eff + s_max ≤ k − 1*. A design cannot be maximally recoverable and maximally resistant at once. It must *spend* its diversity, and it must say how.

A 40-year Monte Carlo of custody loss and hash-family breaks shows why the spending decision matters. The hazards are illustrative; the comparison between designs is the result [M]. The Rev 2 rule (two groups and two families required, no presence) lost governance permanently in **39%** of runs even with renewal. The presence-based recovery tier adopted here lost it in **1.0%**.

### 0.4 What we are building first

| Build now (Phase 0–1) | After validation (Phase 2–3) | Research frontier (not depended on) |
|---|---|---|
| Kernel in C99 subset plus a Rust `no_std` twin and a Python reference: lattice state, interval admission, tiers, chain verification, staging and halt | End-to-end flows: claim, operate, constitution, recovery, sovereign exit, decommission, reactivation; pilot fleets | Device-side fork uniqueness through verifiable maps |
| Verify-only LMS and SLH-DSA providers, SHA-256 and SHAKE256 waists, ML-KEM enrolment through mlkem-native | Witness network with ≥ 2 independent logs (Tessera + C2SP checkpoints); monitors | Third cryptographic class for remote devices (Ascon- or AES-based hash signatures) |
| Presence atom reference designs (key switch, jumper, optical/NFC local port) | Fortress constitution option; RTC trust-age window | Threshold hash-based signing for custody groups |
| NV contract and part profiles; power-cut rig on real silicon | Certification evidence (IEC 62443-4-1, SESIP/PSA), external audit, T0 freeze | Formal machine-checked proofs (Lean/Isabelle) of the whole kernel |
| Host tools: label-driven lint, ceremony kit, migration twin, governance-loss simulator | Cross-domain pilots: vehicles, meters, registries | Proximity-bounded presence; zero-knowledge fleet posture |

### 0.5 What changed from Revision 3, in nine lines

1. The six primitives are condensed into **four (Evidence, Rule, Record, Effect)** plus the waist.
2. The on-device policy check is generalised from a fixed 6-slot validator to **interval admission over labelled atoms**, with bounds computed on the device.
3. **Physical presence and publicity become evidence atoms.** Presence is preventive, publicity is exposure-only, and the theory says exactly what each buys.
4. The single "default dual rule" is replaced by **tiers derived from fault budgets**: HALT, OPERATE (1,1), CONSTITUTION (1,2) recoverable or (2,1) fortress, with remote and nano variants.
5. **Code is authority.** The locked stage boots only an image whose digest an authorised activation committed. One OEM key no longer suffices, which fixes the red-team's single-key boot finding.
6. **Chain, not join-set,** for history, with per-link historical policy and full domain separation.
7. **HALT is budgeted and overridable**, so a stolen halt key cannot freeze a fleet.
8. **Stale devices** get an explicit bound: safe against one class break during their sleep. An RTC window can force presence for older catch-up.
9. **Claims are narrowed** after independent prior-art, citation and red-team reviews. Composition and on-device admission are the plausibly new parts; the mathematics underneath is classical and is cited as such.

---


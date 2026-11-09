<!-- Title: Mathematical foundations: the theory of governed change -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L2. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 3. The theory of governed change

This section is the intellectual core. It is short on purpose: a foundation meant to outlive its implementers has to fit in a few pages. Every statement is either proved here **[P]**, computed by a script **[M]**, or labelled as inference.

### 3.1 Evidence atoms and labels

An **evidence atom** is a predicate that the device's locked stage can evaluate *by itself* for a proposed transition *x*. The kernel supports at most eight atoms. That ceiling is deliberate: a 256-bit table is exhaustively checkable, fits in a few words of RAM, and can be read by a human auditor. Three kinds exist:

| Kind | True for transition *x* when… | Preventive? | Example |
|---|---|---|---|
| `SIG` | A signature over `TBS(x)` verifies under the key whose hash is stored in the atom slot, using a verifier inside the locked stage | Yes | OWN-1: LMS-SHA-256 key of the owner's first HSM |
| `PRES` | The locked stage sampled a dedicated presence input at reset (key switch, jumper, held button, optical or NFC local port), on a pin that firmware cannot drive while the locked stage runs | Yes, against remote attackers | A maintenance key switch on a PLC |
| `WIT` | *x* is included, by Merkle inclusion proof, in a checkpoint cosigned by ≥ k of n witnesses of one of ≥ 2 independent logs listed in the atom | **No: exposure only** | Two transparency logs, each with 2-of-3 witnesses |

Each atom carries a **label word** naming what it depends on:

* **Assumption labels** (bits 0–15) are *derived by the device* from the algorithm descriptor of the atom's verifier: H_SHA2, H_KECCAK, LATTICE, DLOG, FACTOR and others, with UNKNOWN intersecting everything. A policy author cannot mislabel them.
* **Custody-group labels** (bits 16–23): OEM, OWNER, ESCROW, plus any further groups.
* **Site labels** (bits 24–27): which physical site or presence domain.
* **Infrastructure labels** (bits 28–30): declared shared dependencies such as HSM vendor, cloud KMS or ceremony tooling.

Group, site and infrastructure labels are *declared*. They are installed only by a constitution-tier transition, recorded in the public log together with the ceremony record that justifies them, and they cannot be verified by the device. The device does check what it can: assumption labels come from the verifier itself, and duplicate key hashes are rejected.

### 3.2 Faults, budgets and structures

A **fault class** is one atom, or all atoms sharing one label value. One fault means one class fails, in one of two ways:

* **Compromise:** the adversary can make every atom in the class true.
* **Loss:** nobody can make any atom in the class true.

A **fault budget** (t, s) says a tier must remain *safe* when any t classes are compromised simultaneously, and *live* when any s classes are lost simultaneously. Some combinations may be declared out of scope, for example "both hash families broken at once". These declarations are themselves logged.

From the labels the device builds:

* the **compromise structure** 𝒜c: every union of t compromise classes, *plus every exposure atom*, because an attacker can always get a transition logged: publication is not consent;
* the **loss structure** 𝒜l: every union of s loss classes, *plus every absent atom*, because an atom that does not exist on this device is permanently lost.

Let P be the set of all atoms. A **policy** is a monotone Boolean function f on subsets of P: adding evidence never removes authority. f(S) = 1 means the evidence set S authorises.

### 3.3 Theorem 1: the interval theorem [P][M]

**Definitions.** f is **safe** if f(A) = 0 for every A ∈ 𝒜c. It is **live** if f(P ∖ L) = 1 for every L ∈ 𝒜l. Define

* **U**(S) = 1 if and only if S ⊄ A for every A ∈ 𝒜c (the most permissive safe policy), and
* **Lo**(S) = 1 if and only if S ⊇ P ∖ L for some L ∈ 𝒜l (the most restrictive live policy).

**Theorem 1.** Among monotone policies:
(i) f is safe ⇔ f ≤ U;
(ii) f is live ⇔ f ≥ Lo;
(iii) the safe-and-live policies are exactly the lattice interval [Lo, U];
(iv) [Lo, U] ≠ ∅ ⇔ A ∪ L ≠ P for every A ∈ 𝒜c and L ∈ 𝒜l (the mixed Q² condition).

**Proof.** (i) If f is safe and f(S) = 1 with S ⊆ A for some A ∈ 𝒜c, monotonicity gives f(A) = 1, a contradiction; so f(S) = 1 ⇒ U(S) = 1. Conversely, f ≤ U and U(A) = 0 give f(A) = 0. (ii) If f is live and S ⊇ P∖L, monotonicity gives f(S) ≥ f(P∖L) = 1; so Lo ≤ f. Conversely, Lo(P∖L) = 1 ≤ f(P∖L). (iii) follows from (i) and (ii); U and Lo are themselves monotone. (iv) The interval is non-empty iff Lo ≤ U. Lo is the upward closure of the sets P∖L, so this holds iff U(P∖L) = 1 for every L, i.e. iff P∖L ⊄ A for all A, L, i.e. iff A ∪ L ≠ P. ∎

**Corollaries.**
* *Admission is two bitwise comparisons.* Given U and Lo, a candidate table f is admissible iff `monotone(f) && (f & ~U) == 0 && (Lo & ~f) == 0`. A tightening update f_new from f_old additionally needs `(f_new & ~f_old) == 0`. Tightening never breaks safety. It breaks liveness only by leaving the interval, which the check catches.
* *Mandatory evidence is an upper bound.* Requiring atom W ("must be published") is the constraint f ≤ x_W, so the admissible set remains an interval: [Lo, U ∧ x_W]. Every property we need (safety, liveness, mandatory atoms, tighten-only) is either an upper or a lower bound. This is why one tiny check covers all of them.

**Verification [M].** On 1,050 randomly generated compromise and loss structures over 3–5 atoms, exhaustively over all monotone functions (168 for 4 atoms, 7,581 for 5), the brute-force safe-and-live set equalled the predicted interval and existence equalled the mixed Q² condition in every case (`code/G/interval.py`). The earlier 6-slot results are reproduced as interval sizes. Over all 7,828,354 monotone functions on six slots, 4,778,188 are safe and live under slot and group faults. Adding hash-family compromise gives 1,227,427. Adding hash-family loss gives 0.

**Worked example.** Take six signature slots: OEM-1 (SHA-2), OEM-2 (Keccak), OWN-1, OWN-2, ESC-1, ESC-2, alternating families. With compromise classes {slot, group, family}, U = `0xfffefafaffcceac0`. This is exactly the rule "two signers from different groups *and* different families", the rule the project used informally since Rev 2. The theorem shows it is the *most permissive* safe policy, not merely a safe one, and that it cannot be live after a family loss.

### 3.4 Theorem 2: the class-count law (the diversity budget) [P][M]

**Theorem 2.** Partition the atoms into k classes. Faults are whole classes, the adversary may compromise any t of them, and any s may be lost. A safe-and-live policy exists if and only if **k ≥ t + s + 1**.

**Proof.** (⇐) The threshold policy "evidence from at least t + 1 distinct classes" is safe, since t compromised classes give at most t, and live, since k − s ≥ t + 1 classes survive. (⇒) If k ≤ t + s, pick t classes as A and s classes as L, disjoint and covering all k; then A ∪ L = P and Theorem 1(iv) says no policy exists. ∎ Brute-force check over k ≤ 6, t, s ≤ 2: 0 disagreements [M].

**Consequences.**

| Situation | k | Best budget | Meaning |
|---|---|---|---|
| Two custody groups | 2 | (1,0) or (0,1) | Either one bad group can act, or losing one group freezes governance. **There is no two-party governance that is both safe and live.** |
| Three custody groups | 3 | (1,1) | The minimum for single-fault-safe *and* single-loss-live authority |
| Two hash families as both compromise and loss classes | 2 | (1,0) | Safe against one break, frozen after it; or live after one break, forgeable by it |
| Two hash families + physical presence | 3 | (1,1) | Safe against one break *and* live after one break |
| Three custody groups + presence (terrestrial) | 4 | (1,2) or (2,1) | Recoverable *or* fortress, not both |
| Three custody groups, no presence (remote) | 3 | (1,1) | No double-loss recovery that is also single-fault safe |

When classes cross-cut, such as groups × families, there is no simple partition and Theorem 1 is the exact tool. The lint computes the interval directly from labels (§6.3). Theorem 2 is the rule of thumb for design.

### 3.5 Theorem 3: every recovery path is an attack path [P]

Call a transition sequence a **path to full control** if it ends in a state where the actor can authorise arbitrary future transitions: re-keying all groups or re-labelling. Let each path g have compromise tolerance t(g) and loss tolerance s(g).

**Theorem 3.** The device's effective compromise tolerance is t_eff = min_g t(g). Its ability to regain full control after losses is s_max = max_g s(g). For any partition into k independent classes, **t_eff + s_max ≤ k − 1**.

**Proof.** Let g* achieve s_max. By Theorem 2 applied to g*'s policy, t(g*) ≤ k − 1 − s_max. Then t_eff ≤ t(g*). ∎

**What it means.** Recoverability and resistance draw on the *same* diversity. A designer who adds an "easy recovery" path has lowered the device's security to that path's level, whatever the front door says. A "stronger" tier above the weakest full-control path buys delay and visibility, not safety. This is why §4.2 assigns re-keying to exactly one tier per profile, and why the fortress option (2,1) is only meaningful if re-keying a group lives in the 2-safe tier (checked by `tiers_extra.py` [M]).

### 3.6 What no policy can do: the impossibility catalogue [M]

Each row was computed with the label-driven lint (`code/G/lint.py`) on the reference layouts. "Impossible" means the interval [Lo, U] is empty: *no* policy exists, so no cleverness in the policy language can help.

| # | Profile and requirement | Result | Design consequence |
|---|---|---|---|
| (a) | Terrestrial: safe against one fault, live after losing **both** hash families | Impossible | If all cryptography is gone, only presence remains, and one insider has it. Re-provision physically. |
| (b) | Terrestrial: safe against **two** faults, live after losing one family | Impossible | The fortress option gives up liveness after a family loss |
| (c) | Terrestrial: safe against two faults, live after site loss | Impossible | Fortress constitution needs presence |
| (d) | Remote (no presence): safe against one fault incl. a family, live after a family loss | Impossible | Remote devices freeze or degrade after a hash break; a third crypto class is the only fix (C-16) |
| (e) | Remote: any policy safe against every pair of faults | Impossible | Two family breaks forge every signature; remote devices are at most "two-safe except double family" |
| (f) | Remote: safe against one fault, live after two group losses | Impossible | Remote fleets need a fourth independent custodian class, or accept frozen governance after two losses |
| (g) | Nano (one hash family) without presence: any policy safe against a hash break | Impossible | Nano's residual: a SHA-256 break compromises the device unless presence is required |
| (h) | Nano with presence: safe against a hash break, live after it | Impossible | Nano governance freezes after a hash break, by necessity |

### 3.7 Time: cumulative faults and stale devices

Faults accumulate. A device that sleeps through the interval in which classes A₁ and then A₂ break faces A₁ ∪ A₂ when it wakes: an adversary who can forge both may build a fork from the device's old head. This is the *long-range attack* known from proof-of-stake systems, where it motivated "weak subjectivity" checkpoints (Buterin, 25 Nov 2014 [F]).

**Bound [P from Theorem 1].** A device whose head policy is safe against single faults is safe at catch-up against any one class break during its sleep, but not against two sequential breaks unless its policy requires an atom outside both. Physical presence is such an atom. For a remotely reachable device, no policy is safe across two family breaks (§3.6 (e)).

**Mitigations adopted (D-30).** Every accepted chain must end at a *fresh* witnessed checkpoint, so a fork must be published to be accepted (exposure). If the device has a battery-backed RTC, authority-tier catch-up from a head older than a window W requires presence. The RTC can only *restrict*, so a manipulated clock can cause denial, never authority. Without an RTC, the bound above is the honest claim.

### 3.8 Publicity: exposure, not prevention

A transparency log with witnesses guarantees that the checkpoints a device sees are consistent with those everyone else sees. It does **not** guarantee that the logged content was authorised or wanted: witnesses cosign whatever the log appends. In the fault model, therefore, `WIT` atoms belong to *every* compromise set (§3.2). What publicity buys is the property **Exposure(f) ⇔ f ≤ x_WIT**: every authorising evidence set includes publication. Our default tables satisfy this for every evidence set without presence. Sets with presence may omit publication only with extra custody diversity, so that governance stays live during log outages (§4.2). Combined with staging delay and a one-custodian HALT, that turns a covert authority act into a visible one with a window for veto. Uniqueness, meaning no two successors of one head, is *not* given by witnesses. Monitors detect forks after the fact, and device-side uniqueness needs a verifiable map (X-14).

### 3.9 How this relates to existing theory, and what is new

| Existing theory | What it gives us | Source status |
|---|---|---|
| Access structures as monotone functions (Ito, Saito, Nishizeki, 1987; Benaloh and Leichter, CRYPTO '88) | Policies as monotone Boolean functions | [F] titles and venues verified |
| General adversary structures and the Q² / Q³ conditions (Hirt and Maurer, *J. Cryptology* 13(1):31–60, 2000) | Adversaries as families of corruptible sets; Q²-type existence conditions | [F] verified via DOI |
| Fault-tree minimal cut sets; common-cause failure and the β-factor method (IEC 61508-6 Annex D) | "No single point of failure" as minimal cut order ≥ 2; correlated faults dominate | [F] standard preview |
| Threshold fault tolerance (n ≥ t + s + 1 style bounds) | The class-count law is the threshold bound applied to classes | [I] standard argument |
| Weak subjectivity (Buterin 2014) | Long-range attacks need out-of-band checkpoints | [F] |
| CRDTs and join-semilattices (Shapiro et al., SSS 2011) | Monotone, mergeable state; we choose a chain instead (D-28) | [F] |
| Attenuation of authority (Macaroons, NDSS 2014; object capabilities) | Tighten-only updates as attenuation | [F] |
| Witness cosigning (Syta et al., IEEE S&P 2016, pp. 526–545; C2SP tlog-witness v1.1.0) | Split-view resistance for checkpoints | [F] |
| One-way functions suffice for signatures (Rompel, STOC 1990) | The minimal cryptographic root is a one-way function | [F] |
| TUF 1.0.37, Uptane 2.1.0 | Threshold roles, chained root rotation, rollback counters | [F] fetched by prior-art review |

**What is plausibly new [N]** is the composition, not the mathematics. It has four parts. (1) The device itself derives the adversary structure from labels that mix parties, assumptions, places and publicity, and admits only policies inside [Lo, U]. (2) The diversity-budget method assigns each power exactly one (t, s) budget and treats the weakest full-control path as the security level. (3) Physical presence is a first-class, non-cryptographic evidence class that restores safety and liveness under a hash-family loss. (4) There is an impossibility catalogue for device governance (§3.6). Limited searches found none of these combined; patents were not searched. "Not found" is weaker than "does not exist".

---


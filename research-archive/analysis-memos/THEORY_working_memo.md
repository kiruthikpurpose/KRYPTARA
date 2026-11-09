# Theory memo for red-team review: labelled evidence, interval admission, diversity budget

Status: working memo, 2026-11-06. Labels: [M] computed by scripts in `code/G/`, [P] proof given here, [I] inference, [X] open.

## 1. Objects

* **Evidence atom** (≤ 8 per device): something the locked boot stage can evaluate for a proposed transition.
  * `SIG`: a signature verifies under the key whose hash is in the atom slot (verified by the locked stage itself).
  * `PRES`: physical presence, sampled by the locked stage at reset from a dedicated input that firmware cannot drive (button, key switch, jumper, optical/NFC local port).
  * `WIT`: publicity. The transition is included (Merkle inclusion proof) in a checkpoint cosigned by ≥k of n witnesses of one of ≥2 independent logs.
* **Labels** (32-bit word per atom): bits 0–15 assumption atoms derived *by the device* from the algorithm descriptor (H_SHA2, H_KECCAK, LATTICE, DLOG, …; UNKNOWN intersects all); bits 16–23 custody group (OEM, OWNER, ESCROW, …); bits 24–27 site; bits 28–30 declared custody infrastructure (e.g. HSM vendor). Group, site and infrastructure labels are declared (installed at the constitution tier) and cannot be verified by the device; the device rejects duplicate key hashes.
* **Fault class**: one atom, or all atoms sharing one label value. One fault = one class fails.
  * Compromise structure 𝒜c: unions of t compromise classes, each union plus all exposure (`WIT`) atoms (logging is not consent: an attacker can always get logged).
  * Loss structure 𝒜l: unions of s loss classes, each union plus all absent atoms.
* **Policy**: monotone Boolean function f over 2^8 evidence sets, stored as a 256-bit truth table, one per action tier.

## 2. Interval theorem [P][M]

Let U(S) = 1 iff S ⊄ A for all A ∈ 𝒜c, and Lo = up-closure of {P∖L : L ∈ 𝒜l}.

* Safe(f) ⇔ f(A) = 0 ∀A∈𝒜c ⇔ f ≤ U. (⇒: if f(S)=1 and S ⊆ A then f(A)=1 by monotonicity; ⇐: f(A) ≤ U(A) = 0.)
* Live(f) ⇔ f(P∖L) = 1 ∀L∈𝒜l ⇔ f ≥ Lo.
* So the safe-and-live monotone policies are exactly the lattice interval **[Lo, U]**. It is non-empty iff Lo ≤ U iff **A ∪ L ≠ P for every A∈𝒜c, L∈𝒜l** (mixed Q² condition). U is the most permissive safe policy, Lo the most restrictive live one.
* Tighten-only updates keep safety; a tightening is admissible iff the new table stays ≥ Lo.
* Verified [M]: 1,050 random structures on 3–5 atoms, exhaustive over all monotone functions: 0 mismatches between brute force and interval/Q² prediction. Reproduces earlier 6-slot counts (4,778,188 and 1,227,427 are exactly interval sizes; 0 when hash families are both compromise and loss classes).

**Device admission rule:** monotone(f) ∧ (f & ~U) = 0 ∧ (Lo & ~f) = 0 [∧ (f & ~f_old) = 0 when tightening]. C implementation `policy8.c`: 682 B Thumb (Cortex-M0+, -Os), worst stack ≈ 88 B, U and Lo computed on-device from labels; cross-checked against an independent Python reference on 3,000 random cases, 0 mismatches [M].

## 3. Class-count law and the diversity budget [P][M]

If atoms are partitioned into k independent classes and faults are whole classes, a policy safe against any t compromised classes and live against any s lost classes exists iff **k ≥ t + s + 1** (threshold argument; brute-force check 0 disagreements for k ≤ 6, t,s ≤ 2 [M]).

Consequences [I]:
1. Two custody groups can never give single-fault safety *and* liveness (k=2 < 3). Three can.
2. Two hash families as compromise classes plus loss classes: impossible to be safe against one family break and live after losing one (they cover all signature atoms). A third, non-cryptographic class (presence) restores it.
3. **Every recovery path is an attack path.** The effective security of a device is the minimum over all paths to full control (re-key + re-label). A tier that is "stronger" than the weakest full-control path buys delay and visibility, not safety.

## 4. Tiers (reference 8-atom layout: OEM1 H1, OEM2 H2, OWN1 H1, OWN2 H2, ESC1 H1, ESC2 H2, PRES, WIT)

| Tier | Powers | Budget | Default (C = #groups, F = #families, K = #custody atoms, p presence, w publicity) |
|---|---|---|---|
| T0 HALT | pause a staged activation | none (any 1 custody atom) | K ≥ 1; budget of h halts per key per epoch; overridable by a T1 resume |
| T1 OPERATE | activate image ≥ floor; advance floor; rotate a key inside its labels; owner transfer; tighten any table; retire a group (sovereign exit) | safe vs 1 compromise (key, group, family, site); live vs 1 loss (key, group, family, site) | w ∧ C≥2 ∧ (F≥2 ∨ p)  ∨  p ∧ C≥2 ∧ F≥2 |
| T2 CONSTITUTION (recoverable) | widen tables; change labels or atom kinds; add a family; re-key lost groups; reset counters; widen safety envelope; decommission/reactivate | safe vs 1 compromise; live vs any 2 losses except both families | p ∧ K≥2 ∧ (w ∨ C≥2), plus mandatory delay |
| T2' CONSTITUTION (fortress option) | same | safe vs any 2 compromises; live vs 1 key/group loss | p ∧ F≥2 ∧ ((C≥2 ∧ w) ∨ C≥3) |
| Remote T1 / T2 | as above, no presence atom | T1: safe vs 1 (incl. family), live vs key/group loss. T2: safe vs any 2 except both families; live vs 1 key loss | T1: w ∧ C≥2 ∧ F≥2 ; T2: w ∧ C≥3 ∧ ≥2 groups with H1 atoms ∧ ≥2 groups with H2 atoms |

All tables verified with `lint.py` [M]. Impossibility results [M]: (a) 1-safe and live after losing both families; (b) 2-safe and live after one family loss; (c) 2-safe and live after site loss; (d) remote: 1-safe and live after one family loss; (e) remote: any 2-safe policy; (f) remote: 1-safe and live after two group losses; (g) nano (one hash family) without presence: no safe policy against a hash break; (h) nano with presence: not live after hash loss.

## 5. Monte Carlo of governance loss over 40 years (X-E5) [M, illustrative hazards]

Group loss 2%/yr each, family break 0.5%/yr each, re-key 1 yr, new family 3 yr, 200k trials:

| Design | P(governance permanently lost in 40 yr) |
|---|---|
| Rev 2 rule, no renewal | 0.715 |
| Rev 2 rule, with renewal (2 groups + 2 families needed) | 0.392 |
| Remote, family loss not replaceable | 0.392 |
| Remote, single-family degraded mode after a break | 0.099 (not safe against a second-family break meanwhile) |
| Terrestrial with T2 presence tier | 0.010 |

At 5%/yr group loss: 0.613 vs 0.039. At 2%/yr family break: 0.816 vs 0.094.

## 6. Time, history, publicity

* **Chain, not join set.** Transitions are hash-chained per device (prev head, epoch, action, tier, target, domain label); a log sequences them. The device verifies each link under the policy in force at that link.
* **Publicity is exposure, not prevention.** `WIT` is free to an attacker in the safety analysis. It makes every authority act public before it takes effect; with staging delay and HALT, a covert act becomes a visible, vetoable act. Uniqueness (no two successors of one head) is *not* guaranteed by witnesses; monitors detect it. Device-side uniqueness needs a verifiable map [X].
* **Long-range bound.** A device stale over an interval in which classes A1, A2 broke faces A1∪A2. Theorem consequence: a remotely updatable device cannot stay safe across two class breaks during its offline period unless reactivation needs an atom outside both (presence). Mitigation: if the device has an RTC, authority-tier catch-up older than a window W requires presence (time only restricts authority); every accepted chain must end at a fresh witnessed checkpoint, so a fork must be published to be accepted.
* **HALT.** One custody signer, scoped to a bundle, budgeted (h per key per epoch), overridable by a T1 resume order; never lowers a floor.

## 7. Questions for the red team

1. Is the interval theorem stated and proved correctly, including the exposure-atom and absent-atom constructions?
2. Does the tier design achieve its claimed budgets once *all* paths to full control are considered (including T0/T1 interactions, rotation inside labels, sovereign exit, counter reset)?
3. Presence: how can it be spoofed (firmware driving the pin, supply-chain implants, remote hands), and does treating it as one class hold?
4. Labels: what happens when declared labels lie, and what can the device check?
5. Publicity: is "exposure, not prevention" the right modelling? Is a delay enforceable without trustworthy time?
6. Is the Monte Carlo biased toward the new design?
7. What would most likely invalidate this direction?

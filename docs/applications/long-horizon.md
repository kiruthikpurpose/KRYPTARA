<!-- Title: The long horizon -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Reviewed against the R2 red-team findings on 2026-11-12; conflicting passages were corrected in place (see CHANGELOG).

# 19. The long horizon: what could last

No implementation will run for centuries, and none is claimed to. What can last is what has always lasted in infrastructure: a small set of rules that successive generations can re-implement and check, together with the habit of renewing what decays. The question here is which rules and habits.

### 19.1 Enduring invariants

1. **Monotone history.** Authority moves forward; reversal is a new, stronger, public act.
2. **Authority is a monotone function of independent evidence.** Whatever future evidence looks like (new signature families, new physical tokens, institutions not yet invented), the interval rule applies to it unchanged once it has labels.
3. **The diversity budget.** For any power, (resisted compromises) + (recoverable losses) ≤ (independent classes) − 1. This is arithmetic, not technology, and will be as true in 2526 as in 2026.
4. **Renewal before decay.** Keep at least t + s + 1 live classes per power. Re-attest records under current classes before old ones age out (RFC 4998 is the archival precedent).
5. **Time restricts, never grants.** Clocks fail and are forged. A rule that only lets time *remove* authority survives every clock.
6. **Publicity plus delay plus veto.** Covert power is the most dangerous kind; making every act public before it is effective is cheap, and it ages well.
7. **Minimal roots.** Signatures need only one-way functions (Rompel 1990 [F]). Monotonicity needs only a physical irreversibility (a fuse, a counter). Presence needs only locality. These are the most assumption-light foundations available.
8. **Every party can exit.** No custodian is permanent: OEM exit, owner transfer, escrow replacement and decommissioning are all first-class transitions.

### 19.2 The reconstruction kit

To be renewable by people who never met us, the project keeps four artefacts small and self-describing:

* **The specification.** At most about 30 pages: the theory (§3), the record layouts, the action and tier table, the waist ABI and the label registry.
* **Test vectors.** Positive and negative, covering every action, tier and profile. Vectors are what a future implementer trusts first.
* **A genesis record per device** in the public log, stating in plain language what the fields mean and where the specification and vectors are archived. Its digest is the first link of the device's chain.
* **Algorithm descriptors referenced by content hash** of their specifications, so a verifier in a later era can tell which document defines which `alg_id`.

### 19.3 What we will not pretend

Long-lived media, for example glass storage claimed to last 10,000 years from accelerated ageing [S, secondary], do not solve the authority problem. They make it more pressing, because the data outlives the keys. Institutions that run logs and escrow will change many times. The design's answer is that every institution is replaceable by a governed transition, not that institutions will last.

### 19.4 Beyond operational technology

The same four primitives describe any artefact whose rules of change must outlive its custodians. These are analogies to be piloted, not claims [X]:

| Domain | Atoms | Presence analogue | What the kernel adds |
|---|---|---|---|
| Satellites and space systems | Ground-segment custody groups, two hash families | None (remote profile) | Honest remote budget (1,1); motivation for a third crypto class |
| Implantable medical devices | Manufacturer, clinic, patient-advocate or regulator escrow | Programmer wand in near field | Clinic and patient survival of manufacturer exit; envelope tier for therapy limits |
| Vehicles | OEM, fleet owner, independent repair/escrow | Service connector at a workshop | General policy instead of a fixed two-repository AND (Uptane-compatible) |
| Smart meters and grid edge | Utility, regulator-appointed escrow, meter OEM | Optical port (already standard on meters) | 15–20-year meter life with hash-based roots and presence-gated constitution |
| Software registries | Maintainers, organisation, foundation | Hardware-key ceremony in person | Tighten-only policies; class-aware maintainer quorums |
| Long-term archives | Archive, depositor, legal custodian | Physical vault access | Monotone authority over records; renewal schedules |
| Autonomous agents and AI systems | Operator, developer, independent overseer | Human approval at the controlled site | Permissions that only tighten without constitutional approval; one-signer halt; public, delayed widening of capabilities |

---


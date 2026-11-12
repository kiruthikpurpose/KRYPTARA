<!-- Title: Roadmap, constraints and adoption path -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Reviewed against the R2 red-team findings on 2026-11-12; conflicting passages were corrected in place (see CHANGELOG).

# 15. Roadmap, milestones and acceptance criteria

Durations and team size are estimates [E]; no reference project exists to benchmark them. A plausible core team is 6–9 engineers (embedded C and Rust, cryptography, formal methods, fleet services), plus an external cryptographer and a safety assessor on retainer.

### Phase 0 — falsification sprints (weeks 0–8)

EXP-01, E-A1, E-B1, EXP-10 (a and b), EXP-12, EXP-18 (started), EXP-19, E-C1 (outreach), EXP-15 (design).
**Exit:** the theory is mechanised; the C admission code is proven equivalent to the spec; silicon power-cut results exist for ≥ 1 family; dual-profile cost is known on 2 parts. Any failed gate triggers its fallback, recorded in §20.

### Phase 1 — the kernel and two ports (months 2–7)

`ac-core` v1 (C + Rust twin + Python model) with tiers, admission, chain, halt budget and catch-up. Verify-only LMS/HSS (+ SLH-DSA where it fits). `ac-wit` with C2SP formats. `ac-nv` with three ports (an ECC-flash M33, an M0+, a Linux host). Presence ports on two boards. `ac-lint`, `ac-govsim` and `ac-ceremony` v0.
**Acceptance:**
* all vectors pass on every provider and port;
* C, Rust and Python agree on all small-universe inputs;
* ≥ 10⁵ power cuts with 0 violations;
* locked stage ≤ 8 KiB (dual-terrestrial, LMS only);
* admission ≤ 10 ms and receipt ≤ 150 ms on M0+;
* two builders produce identical binaries;
* external design review of waist and theory passed.

### Phase 2 — end-to-end governance and pilots (months 7–15)

All actions of §6.2 end to end; two independent logs with ≥ 3 witnesses each; `ac-monitor`; state reports; ML-KEM enrolment; device echo; gateway as governed device; pilots with two asset owners (one terrestrial OT fleet, one meter or vehicle fleet).
**Acceptance:**
* sovereign exit demonstrated with the OEM keys destroyed;
* two-custodian-loss recovery demonstrated with presence within the declared delay;
* a hash-family break drill (simulated declaration) completes with budgets restored;
* equivocation drill detected before `not_before` (EXP-13);
* halt behaviour in the pilot matches the twin within stated bounds;
* an interoperability event with ≥ 3 external implementers.

### Phase 3 — freeze, audit, certification evidence (months 12–24, overlapping)

T0 freeze of the waist and kernel after three unrelated ports and the independent re-implementation agree. Implementation audit; formal refinement complete; ACVP/FIPS 140-3 work for providers; IEC 62443-4-1 process evidence; PSA or SESIP evidence for the locked stage; assessor packs for P2. Stewardship: annual custody drills, release-ceremony rehearsals, evidence renewal.

### Phase 4 — transfer and frontier (month 24 onward)

Cross-domain pilots (§19.4), the remote third class (C-16), verifiable-map uniqueness (X-14), threshold-HBS custody inside atoms (X-01), and proximity-bounded presence (X-15).

### Milestones

| Milestone | Content | Gate |
|---|---|---|
| M1 (wk 8) | Theory mechanised; admission proven; silicon power-cut data | Phase 0 exit |
| M2 (mo 4) | Kernel alpha on two ports; vectors v1 | Differential agreement |
| M3 (mo 7) | Kernel beta; design review passed | Phase 1 acceptance |
| M4 (mo 10) | Full action set end to end on a test fleet | Drills pass |
| M5 (mo 15) | Two pilots complete | Phase 2 acceptance |
| M6 (mo 18) | Independent re-implementation agrees | P-12 |
| M7 (mo 24) | T0 freeze; audit closed | Phase 3 exit |
| M8 (mo 30+) | First cross-domain deployment | Pilot report |

---


## 16. Real-world constraints and the adoption path

* **Embedded.** C1/C2 parts have 16–64 KiB of lockable region at best, a few KiB of RAM and no hardware SHA-3. Hence nano as the default where E-B1 fails, verify-only hash-based signatures in the locked stage, and fixed records instead of CBOR.
* **Industrial.** Changes ride maintenance windows (staging + `not_before`); safety images are untouched (P2). Procurement needs a written profile per device class and a conformance certificate per port.
* **Offline.** Chains, jump transitions and pre-encapsulated enrolment tokens move by any medium. Receipts are self-contained; devices never query a log.
* **Long-lived.** Counter capacity lint; NV wear budgets; renewal schedules from label-retirement dates; evidence renewal.
* **Mixed-vendor.** Port owners own their ports (D-15) and claim profiles only through the conformance suite. Part profiles record hazards such as torn-read behaviour.
* **Institutions.** Three custody groups and two logs must exist for decades. Realistic holders: the OEM; the owner or operator; an independent escrow or trust-service provider, an insurer or an industry body. Logs and witnesses are run by at least two unaffiliated organisations. The governance simulator gives procurement a number to argue with.
* **Adoption path.** (1) Owner-side tools first: the lint, the governance simulator and monitors have value without new devices. (2) Gateways as governed devices. (3) The kernel as an authority add-on under existing bootloaders (EXP-20). (4) Native greenfield designs.

---


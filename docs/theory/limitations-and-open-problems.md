<!-- Title: Open questions, risks and limits -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 17. Unresolved scientific and engineering questions

Ranked by how much the answer could change the design. Each names the experiment or research item that addresses it.

| # | Question | Why it matters | Addressed by |
|---|---|---|---|
| Q1 | Are SHA-2 and Keccak independent enough to count as two classes in the locked-stage verifiers? Shared elements include the hash-based signature constructions themselves (multi-target and tweakable-hash security arguments) and the wrapper code | If not, the dual profile collapses to nano + presence. That is still sound, but routine T1 then has no protection against a hash break without presence | EXP-18, X-05 |
| Q2 | How complete can a declared fault model be? What common-cause share (β-factor) applies to custody institutions, HSM products, ceremony tooling and the verifier itself? | Every guarantee is relative to the declared classes, and undeclared common-mode faults dominate real incidents | EXP-11, EXP-16, D-33, X-17 |
| Q3 | Can presence be made robust against remote-hands services, firmware-driven inputs and implants, at an acceptable cost per device class? | Presence carries the constitution tier in terrestrial profiles | EXP-15, X-15 |
| Q4 | Can a microcontroller obtain fork uniqueness (one successor per head) without querying a service? | Forks are currently prevented only up to the fault budget, and otherwise detected | C-17, X-14 |
| Q5 | How can delay be enforced without trustworthy time? | Delay is what makes exposure useful | X-16, C-15, witness-checkpoint time |
| Q6 | Who runs logs and witnesses for 40 years, and with which signature algorithms? The published C2SP cosignature format uses a classical algorithm [R], so a hash-based cosignature profile must be defined and witness one-time-key capacity planned. An LMS tree of height 20 gives 2²⁰ ≈ 1.05 million signatures, about 120 years at one checkpoint per hour [M, arithmetic] | Publicity is load-bearing for G9 and G10 | X-08, EXP-13, EXP-19 |
| Q7 | What do SHAKE256 verification, admission and receipt verification cost on real silicon? The Keccak figure (≈ 17,000 cycles per permutation on M0+) is a weak estimate | Decides C-01 and the receipt cadence | E-B1, EXP-19 |
| Q8 | Is there a standardisable third cryptographic class for remote fleets (Ascon- or AES-based hash signatures) with a defensible independence argument? | It is the only fix for remote liveness after a family break (§3.6 (d)) | C-16 |
| Q9 | What are realistic hazard rates over decades for custody institutions: HSM vendor exit, escrow agent dissolution, key loss? | The 1.0% vs 39% governance-loss result uses illustrative hazards | EXP-14 |
| Q10 | Will safety assessors accept a zero-crypto safety core, and presence-gated widening of safety envelopes, as recertification-neutral? | Decides P2 and D-19 in regulated plants | E-C1 |
| Q11 | What integration effort does the kernel add over a verify-only boot stage? | Adoption | EXP-20 |
| Q12 | How do ceremonies, presence procedures and monitoring work as human practice over decades? | The theory is only as good as the people who carry it out | Phase 2 pilots and drills |
| Q13 | When does threshold hash-based signing become practical inside custody atoms (no dealer, small state, audited)? | It would lighten the HSM-ceremony burden with no device change | X-01 |
| Q14 | Legal: enforceability of escrow triggers, EU CRA steward duties, patent freedom to operate | Governance institutions need legal footing | Counsel, Phase 0 |
| Q15 | PQ profiles of OPC UA, IEC 62351, DNP3-SA and Modbus Security; FN-DSA (FIPS 206) and HQC finalisation; the exact SHA-2 function assignment in the SLH-DSA SHA2 parameter sets | Edge integration and correct derivation of assumption labels | Standards tracking |
| Q15a | FIPS 206 (FN-DSA/FALCON) remained a draft as of 2026-09-28 (NIST's own update on fixed-point arithmetic for keygen/signing to ease constant-time implementation); separately, NIST's *Additional Digital Signature Schemes* process (a distinct track seeking non-lattice diversity) advanced nine candidates — FAEST, HAWK, MAYO, MQOM, QR-UOV, SDitH, SNOVA, SQIsign, UOV — to a third round in 2026-05, expected to run ~2 years [S, verified 2026-11-09]. Neither changes anything KRYPTARA currently depends on (ML-KEM/ML-DSA/SLH-DSA/LMS-HSS are all final); noted here because the "remote third class" (C-16, item X-14 in roadmap.md Phase 4) that wants non-lattice signature diversity should watch this track once it stabilises. | Future custody-group diversity beyond lattice/hash constructions | NIST IR 8610; csrc.nist.gov/News/2026/nist-advances-9-candidates-to-the-3rd-round-of-pqc |

---


## 18. Risks that could invalidate the direction

Likelihoods are judgements [I], drawn from the two independent red-team reviews and our own analysis.

| # | Risk | Likelihood | Early signal | If it materialises |
|---|---|---|---|---|
| R-1 | **Fault-model incompleteness.** Serious incidents come from systematic or common-mode faults outside the declared classes: a verifier bug, a shared HSM or KMS, a ceremony script used by every group | High: the first serious incident is likely to lie outside the list | Mutants surviving the test suite; custody-graph audits finding hidden sharing | The direction survives as defence in depth with an explicit residual, not as a safety-standard fault-tolerance claim. Investment shifts to implementation assurance and custody-graph evidence |
| R-2 | **The institutions do not materialise.** Three custody groups and two independent log-and-witness operators are not funded or not sustained for decades | Medium–high | No escrow or witness operator signs up during pilots | Nano-terrestrial with fewer institutions; industry bodies or insurers as escrow; consortium-run logs. The owner-side tools still deliver value |
| R-3 | **Presence fails in practice**: unmanned sites, contractor abuse, remote-hands relays, hardware implants | Medium | EXP-15 finds remote assertion paths; pilots bypass the procedure | Remote profile for the affected classes; proximity bounding (X-15). Because presence is never sufficient alone, the damage stays limited |
| R-4 | **Silicon cannot host it**: few industrial MCU families can lock a first stage with safe torn reads, or Keccak and receipts are too slow | Medium | E-A1 below 30%; E-B1 or EXP-19 budgets missed. Literature pre-check (`docs/research/mcu-survey.md`, item 29): lockability itself is well-documented (14/17 families, 82%); torn-write safety as a HARDWARE guarantee is essentially undocumented anywhere (0-1/17) — confirming the architecture's own premise that a journal is needed, not undermining it, but meaning GATE-10 cannot be closed from documentation alone | Nano by default; the gateway pattern (P3); a supervisor (C-04) or new ROM for new designs; hardware hash engines as a procurement requirement |
| R-5 | **Hash-family independence is indefensible** | Medium | EXP-18 reviewers list non-negligible shared assumptions | Dual collapses to nano + presence. Terrestrial guarantees survive; remote ones weaken |
| R-6 | **Adoption economics**: vendors prefer single-vendor update and buyers will not pay for governance | Medium–high | EXP-20 effort above 2×; no pilot sponsor | Ship owner-side tools and the verify-only layering first; align with regulation (CRA, IR 8547 timelines) and with insurers |
| R-7 | **Operational complexity causes outages**: mislabelled atoms, failed ceremonies, monitors nobody reads | Medium | Drill failures; below-budget reports ignored | Simpler default profiles, mandatory drills, and the governance simulator in procurement |
| R-8 | **A general break of hash-based signature constructions**: a flaw in the tweakable-hash or multi-target arguments that LMS and SLH-DSA share | Low, but severe | Cryptanalytic results | Presence-gated recovery and a third class (C-16). This residual is shared by every hash-based design |
| R-9 | **Prior art or patents** cover the composition | Unknown | Freedom-to-operate search | Licence, design around, or publish defensively |
| R-10 | **The theory is wrong** in a way the checks missed | Low: the proofs are short, and 1,050 random structures and 3,000 C cases agree [M] | EXP-10 mechanisation fails | Fix before any freeze. Nothing is frozen before EXP-10 passes |

**Review status.** Rev 3 was shaped by two independent reviews (red-team and prior-art), and this revision by an independent citation fact-check. A second independent red-team review of this revision's theory and tiers was commissioned but had not reported when the document was finalised. Its remit, the seven questions in the working memo `THEORY.md`, is carried into the Phase 0 gate alongside EXP-10 and EXP-11, and nothing is frozen before it reports.

---


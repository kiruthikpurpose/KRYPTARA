<!-- Title: Falsification programme (EXP-xx) -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L2. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Reviewed against the R2 red-team findings on 2026-11-12; conflicting passages were corrected in place (see CHANGELOG).

# 14. The falsification programme

Every load-bearing claim has an experiment that could kill it. Carried experiments keep their Rev 2 IDs.

| ID | Question | Method | Pass | If it fails |
|---|---|---|---|---|
| **EXP-01** | Is the NV contract safe on real ECC flash? | Power-cut rig, ≥ 50,000 cuts per family, STM32H5 + one other | 0 unrecoverable; boot ≤ 45 ms | Force OTP, counter or FRAM for that family (D-06) |
| **E-A1** | Can industrial MCUs lock a first stage and read torn words safely? | Desk and register survey of ten families | ≥ 50% lockable *and* a recoverable torn-read path | < 30% reopens new-ROM and supervisor arguments |
| **E-B1 / E-B1b** | What does the dual profile cost? Does ML-DSA fit in the locked stage? | Flash and cycles on two parts, with and without SHA-3 hardware | Boot verification ≤ 250 ms on ≥ 50% of parts; ≤ 16 KiB | Nano default; ML-DSA not an independent atom |
| **EXP-02** | Does the kernel protocol meet its invariants? | TLA+ with tiers, halt budget, catch-up, sovereign exit, recovery | 0 violations; state counts recorded | Redesign the offending transition |
| **EXP-03** | Device-scoped one-time reports | M0+ and M33 measurements; exhaustive power-cut on index reservation | ≤ 1 KiB code, ≤ 100 ms, no index reuse | Gateway-witnessed reports only |
| **EXP-10** | Are Theorems 1–3 and the C admission code correct? | (a) Lean/Isabelle proof; (b) CBMC equivalence of `policy8.c` to spec | Proofs complete | Fix and re-verify before any freeze |
| **EXP-11** (red-team X-E1) | How often are admissible tables breakable by undeclared coincidences? | 8-atom sampling with pair-events and custody-graph-derived faults | < 10% of admitted tables breakable by realistic pairs once the custody graph is an input | Make the custody graph a mandatory input to T2 label declarations |
| **EXP-12** (X-E3) | Does the stale-device bound hold exactly as stated? | Fork simulation: break times, sleep lengths, RTC on or off | 0 acceptance with one break; acceptance with two sequential breaks only without presence or RTC window | Narrow the claim further or require re-claim |
| **EXP-13** (X-E4) | Do publicity and monitors detect equivocation in time? | Two logs, one malicious; witnesses; monitors | Detection before `not_before` in ≥ 99% of drills | Lengthen delays; add log diversity |
| **EXP-14** (X-E5 calibrated) | Is the governance-loss advantage real with real hazards? | Recalibrate `brick_mc.py` with custody, HSM and vendor-exit data from pilots and insurers | Terrestrial design ≤ 2% over 40 years at calibrated hazards | Add custodians, shorten renewal, or change T2 |
| **EXP-15** | Can presence be faked without being on site? | Red-team three device types: firmware-driven pins, debug paths, local-port parsers, remote-hands scenarios | No remote-only presence assertion; local-port parser survives 10⁹ fuzz execs | Hardware requirement change; restrict presence forms |
| **EXP-16** (X-E2) | Does the test suite catch systematic verifier bugs? | 100 seeded mutations in C and Rust cores | ≥ 95% killed | Strengthen vectors; record residuals |
| **EXP-17** (X-E6) | Can legitimate service tools roll state back? | Restore old NV snapshots on two target parts | Floor, retired set and head never regress | Exclude part from monotone profiles |
| **EXP-18** (X-E7) | Are SHA-2 and Keccak independent enough to be two classes? | Two cryptographers list shared and non-shared assumptions for the locked-stage verifiers | Written argument that the shared set is negligible | Treat as one class: dual collapses to nano + presence |
| **EXP-19** | What do WIT and admission cost on small parts? | Measure receipt verification and admission on M0+ and M33 | Receipt ≤ 150 ms and ≤ 8 KB; admission ≤ 10 ms | Hourly checkpoints → coarser; fewer witnesses; hardware hash requirement |
| **EXP-20** | Is adoption effort acceptable? | Integrate under MCUboot and one vendor bootloader; measure engineer-weeks versus a verify-only baseline | ≤ 2× baseline effort | Ship the verify-only layering first; kernel as later add-on |
| **E-C1** | Will safety assessors accept the zero-crypto core and the C-04 supervisor? | Written pre-assessment | A written view | C-04 dropped |
| **E-P1**, **E-O1**, canary review | Merkle-page timing; optical token; canary construction | As Rev 2 | As Rev 2 | As Rev 2 |

---


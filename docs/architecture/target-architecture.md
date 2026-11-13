<!-- Title: Target architecture and the path to it -->
> **Level:** L3 (plan). **Date:** 2026-11-13. Evidence labels: [M] machine-checked in this repository, [E] estimate, [P] proposal, [H] hypothesis. Status words: BUILT (code in this repository with a passing check), MODEL (Python or TLA+ only), SPEC (prose only), NONE.
> Written after `src/ac_step.c` made the waist real (ADR-041). Where this document and the code disagree, the code and its checks win.

# Target architecture and the path to it

## 1. Where the code stands

| Layer (system-architecture §5.3) | What exists | Status |
|---|---|---|
| L0 admission | `src/policy8.c`: monotone, projection, interval bounds, tightening, dual-copy tables, key-install rule, label derivation, duplicate-key check | BUILT on the host. Cortex-M0+ size unmeasured since additions (OQ-13) |
| L0 waist step | `src/ac_step.c` over `src/ac_waist.h`: genesis, halt/resume, image commit, table install and tighten, key install and retire, epochs, hash chain, snapshots | BUILT on the host; independent Python model agrees on 15,250 random lines; 750 golden input lines [M]. Not on any MCU |
| L0 tier engine, image check, chain hash | `src/kernel.c` | BUILT on the host |
| L0 evidence verification (waist W2) | Prototype LMS and SHA-256 (`src/prototypes/c`, 98 vectors); PQ libraries only as host conformance evidence | The kernel consumes already-verified evidence; the layer that produces it is SPEC |
| L0 persistence | Journal prototype survives 72,816 simulated power cuts | BUILT as a prototype, not connected to `ac_step` |
| L1 platform ports | none | NONE |
| L2 formats | CBOR encoder agreement (`models/wire_format.py`), Merkle proofs | MODEL. No parser |
| L3 modules, L4 fleet tools | lint, governance simulator, ceremony tool, gateway profile | MODEL and toy tools |
| Formal | TLA+ first stage (reduced configurations pass), Z3 instance proofs, exhaustive n ≤ 4 | partial; GATE-08 open |

## 2. Principles the code already obeys [M]

1. **One function decides.** Everything the kernel does is `ac_step(ctx, msg) -> status + intents`. No hidden state, no callbacks.
2. **Four artefacts per behaviour.** Prose, an independent model, the C code, and golden vectors. A behaviour is not done until all four agree. Rust twins, formal proofs and ports bind to the same vectors.
3. **Trust boundaries are layers.** Verification, parsing and platform effects live outside the kernel and meet it at a small struct and a list of intents.
4. **Profiles are data.** Fault classes, budgets and the action-to-tier map are provisioned, not compiled. The remote profile is admitted by the same C with no change [M, `models/step_check.py`].
5. **Fail closed, explicably.** Every refusal is one of 11 stable status codes and one `REJECT` intent, and changes nothing.
6. **The rules are executable.** See §5.
7. **Numbers carry their provenance.** Host x86-64 measurements are never presented as silicon.

## 3. The waist: what freezes and how it evolves

**Frozen at the T0 freeze:** status codes and their values; enum values (tiers, actions, message and intent kinds); the layouts in `src/waist-v1.abi`; the transition serialisation and domain tags; the context digest serialisation; `tests/vectors/waist-v1.txt`.
**Not frozen:** providers, ports, profiles, wire formats outside the kernel, every host tool.
**Before the freeze** a layout change is allowed only by updating the lock and, if behaviour changed, the vectors, in the same commit, with the reason in the commit message. **After it,** a change means waist v2: a new header, a new vectors file, v1 kept and still passing. Deployed devices live for decades, so tools must speak v1 for as long as v1 devices exist.

## 4. The path: five slices, each with an exit test [P]

| Slice | Adds | Exit test |
|---|---|---|
| 1 (done) | Pure step over admission, tiers, halt, image commit, key slots, chain, snapshots | Differential and golden vectors agree; `arch_check` passes |
| 2 Evidence and labels | The evidence layer (`ac_verify` over W2 provider ops, resumable); `LABEL_DECLARE`; `DECLARE_CLASS_DEAD` counting real classes (today the retire rule counts key slots); CBOR-to-struct projection with its own fuzzing | A message whose evidence a provider rejects never reaches the step; known-answer tests per provider; fuzz of the projection |
| 3 Record and publicity | `CATCH_UP` (chain verified under the policy in force at each link); receipt verification (Merkle done, C2SP cosignatures not); the stale-device bound; evidence sets without presence must carry a receipt | Golden vectors for catch-up; a forged-receipt corpus is refused |
| 4 Platform and persistence | W3; the snapshot encoding; the journal carrying the context; boot recovery | The power-cut sweep over the whole step: a cut at every write leaves the old or the new state, never a mix |
| 5 Ports and proof | Cortex-M0+ and M33 builds with size and cycle measurements (GATE-07, GATE-09); the Rust twin reproduces the golden vectors; bounded proofs of `ac_step`; a second team's re-implementation | All of the above agree; external review. Then the T0 freeze |

## 5. How the architecture defends itself

| Check | What it enforces | Caught so far |
|---|---|---|
| `scripts/arch_check.py` R1–R8 | includes, no I/O or allocation, clean strict build, no mutable globals, closed set of external symbols, no recursion, stack bound, ABI lock | A hidden `strlen` that GCC generated from a name-length loop. The self-test planted six violations and found that recursion is invisible at `-O2` (the optimiser turns it into a loop), so the call graph is now taken at `-O0` |
| Differential (`models/step_check.py`) | C and the independent model agree line by line; a coverage gate requires all 12 status codes and all 9 actions | Three planted bugs, all caught |
| Golden vectors | Any implementation reproduces the recorded behaviour | (acts at the freeze) |
| Mutation testing of `ac_step.c` | The checks above can fail | First run: 75% killed. It showed the generator never made malformed provisioning records, never hit field boundaries and never made a loss budget exceed the class count; the generator was strengthened, and one redundant check was deleted instead of tested |

## 6. Open decisions that need the owner

- **OQ-14.** The PAM rule makes a lost escrow key unrecoverable in the first-stage design. ADR-040 and the tier model assume it can be recovered. Resolve before either is accepted.
- **ADR-041** is Proposed. Acceptance needs the Rust twin and an outside reader of `ac_step.c`.
- **Real classes.** Slice 2 must replace "live key slots" in the retire rule with classes (groups, families, presence).
- **RAM.** The context is 788 B of the 4,096 B locked-stage budget; slices 2–4 will add to it. `arch_check` prints the size every run.
- **The shared-author risk.** The C and the model were written by the same author from the same ADR. A shared misreading passes the differential check. A human re-implementation is the fix.

## 7. What would change this plan [H]

- Real-silicon torn-write behaviour (E-A1) failing GATE-10: slice 4 moves to the gateway pattern for those parts.
- A cryptographer's rejection of hash-family independence (GATE-11): the dual-family profiles shrink to one family plus presence; profiles being data, this changes provisioning, not the kernel.
- The Rust twin disagreeing with the vectors: the vectors, the ADR text and the C are re-read together before anything is changed.

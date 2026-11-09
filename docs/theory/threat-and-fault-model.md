<!-- Title: Threat and fault model -->
> New (2026-11-09), item 6 of the 50-things completion list. Consolidates assumptions that were
> previously scattered across mathematical-foundations.md, the risk register (R-1..R-10 in
> limitations-and-open-problems.md) and individual ADRs, into one numbered list every theorem can
> cite. Document level: L2. Evidence labels: [P] proved, [M] machine-checked, [E] estimate,
> [S] standard/literature, [H] hypothesis.

# Threat and fault model

Every safety/liveness guarantee in this repository holds **only inside this declared model**
(R-1). This document says precisely what that model is, so "the theory is wrong" (R-10) and "the
model is incomplete" (R-1) are different, checkable claims rather than the same vague worry.

## A. Adversary powers (what an attacker CAN do)

| # | Power | Scope |
|---|---|---|
| A-1 | Hold any subset of compromised SIG/PRES atoms' private material, for atoms the declared fault structure allows as a simultaneous compromise | Per declared t |
| A-2 | Present any evidence set S derivable from held keys plus exposure atoms (WIT, publicity) — exposure is always free to the attacker (F-R2-01) | Always |
| A-3 | Control absent atoms completely (they count as permanently compromised AND lost, F-R2-01/ADR-014) | Always |
| A-4 | Correlate a declared site-controller group's compromise with presence (F-R2-04/REQ-LINT-03) | When a site controller is declared |
| A-5 | Trigger one common-cause event that compromises every atom in a declared common-cause group simultaneously, as a single fault (item 7, `models/common_cause.py`) | When a common-cause group is declared |
| A-6 | Forge a signature under any key whose declared assumption set is broken (hash-family break) | Per declared break |
| A-7 | Replay, reorder, or selectively withhold any message not authenticated and chained (mitigated by REQ-CHAIN-01's domain-separated hash chain, not eliminated by the admission math alone) | Always, bounded by the chain |

## B. Adversary powers (what an attacker CANNOT do, by assumption)

| # | Assumption | Theorem(s) relying on it |
|---|---|---|
| A-8 | Cannot forge physical presence (PRES) without physically satisfying the sampling circuit | Theorem 2 (class-count law), via PRES being an independent class |
| A-9 | Cannot compromise atoms outside the declared fault structure's stated t/s budget simultaneously (classes are otherwise independent) | Theorem 1, Theorem 2 — directly weakened by A-5 when declared |
| A-10 | Cannot break the admission code itself (no memory-safety or logic bug in `ac_tbl_*`) — addressed by testing (fixcheck, fuzzing, mutation testing), not assumed away by the math | All theorems (they reason about the SPECIFICATION, not the C implementation; REQ-ADM-01..05 bridge the two) |
| A-11 | Cannot forge a hash-chain link without either a valid signature under the policy in force AT THAT LINK, or breaking the chain's hash function (REQ-CHAIN-01) | Not a Theorem 1-3 dependency; a separate claim, CLM-32 |

## C. Fault classes (the formal structures Ac, Al in `models/interval.py`/`lint.py`)

| # | Class | Declared via |
|---|---|---|
| F-1 | Single-atom compromise (one SIG/PRES key stolen) | `comp_labels` singleton |
| F-2 | Label-value compromise (every atom sharing a group/family/site label fails together) | `comp_labels` by label type |
| F-3 | Single-atom loss (key destroyed, custodian gone) | `loss_labels`/`loss_kinds` singleton |
| F-4 | Label-value loss | `loss_labels` by label type |
| F-5 | Absent-atom compromise+loss (atom doesn't exist on this device) | `present` set, automatic (A-3) |
| F-6 | Common-cause compromise (item 7) | `common_cause_groups` |

## D. What is explicitly OUT of this model (R-1's residual, stated positively)

| # | Out-of-model risk | Where it's tracked instead |
|---|---|---|
| O-1 | A verifier implementation bug (not a spec gap) | `fixcheck.c`, `fuzz_policy8.c`, `scripts/mutation_test.py` — testing, not proof |
| O-2 | A shared HSM/KMS vendor across declared-independent custody groups, undeclared | R-1; `ac-ceremony` custody-graph evidence (item 32) is meant to surface this, once built |
| O-3 | A ceremony script used by every custody group (a process common cause not expressed as a label) | Same as O-2; closeable only by declaring it as a common-cause group (F-6) once discovered |
| O-4 | Side-channel extraction of key material from a device that holds it | Out of scope for the admission math entirely; a hardware/implementation concern |
| O-5 | Social-engineering or coercion of a human custodian (not a cryptographic fault) | Out of scope; organisational mitigation only |
| O-6 | A flaw in the proof itself, as opposed to the model (R-10) | `docs/theory/proofs.md` (item 3) and `models/z3_mechanised.py` (item 5) narrow this, do not eliminate it |

## E. Theorem-to-assumption cross-reference

| Theorem | Relies on | Broken by (declare the correlation/break and the guarantee narrows accordingly) |
|---|---|---|
| Theorem 1 (interval) | A-1, A-2, A-3, A-9 | A-5 (common cause) shrinks U/Lo exactly as computed in `models/common_cause.py`; does not invalidate the theorem, changes its INPUT |
| Theorem 2 (class-count law, k≥t+s+1) | A-1, A-3, A-8, A-9 | Declaring any A-5 common-cause group effectively merges classes, so the k in k≥t+s+1 must be counted AFTER merging, not before (open modelling note, see limitations-and-open-problems.md Q7) |
| Theorem 3 (recovery is an attack path) | Same as Theorem 2, plus the existence of a recovery tier at all | A-4 (site-controller correlation) is the worked example already in red-team-r2-findings.md F-R2-04 |

## F. Residual statement

Every guarantee above is relative to A-1..A-11 and F-1..F-6 as declared for a specific profile. R-1
through R-10 in `limitations-and-open-problems.md` are the standing, unresolved residuals this model
does not and cannot close — they are listed there, not hidden. This document does not reduce the
residual; it makes explicit exactly what is and is not inside the fence.

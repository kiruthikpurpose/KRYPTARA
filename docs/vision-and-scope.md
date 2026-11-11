# Vision, identity and scope

**Document level:** L2 (authoritative). **Status:** identity text is Proposed; scientific scope is bounded by `docs/research/evidence-register.md`.

## Name
**KRYPTARA — Kiruthik's Recursive Yielding Paradigm for Transformative and Adaptive Reconfigurable Architectures.** The name was assigned by the project owner on 2026-11-09. No source document (S01–S11) uses it. It is preserved unchanged. This document does not rename it; it records what the words can defensibly mean.

## What is verified today
The only part of the programme with proofs, scripts and code in this repository is the **governed-change kernel**: evidence atoms, interval-admitted monotone rule tables, a hash-chained authority record, and staged haltable effects (docs/theory/mathematical-foundations.md; `models/`, `src/policy8.c`). Everything beyond that is scope, not result.

## Interpretation of the name's terms (all Proposed, none established science)
| Word | Defensible technical reading | Where it appears in the verified work | Status |
|---|---|---|---|
| Recursive | Governance of governance: a higher tier changes the rules of a lower tier, and admission checks apply to those rule changes themselves. | T2 replaces T1 tables; `ac_tbl_within`/`ac_tbl_tighten` apply at every tier. | Proposed, now with a passing test (item 2, 50-things list): `models/recursive_property.py`, 4/4 cases — a T2-proposed T1 widening is rejected by the tightening check regardless of who proposes it, and a tightening that drops a load-bearing liveness point is caught by the interval check even though the tightening check alone would have passed it. Still "Proposed" as a design property, not elevated to a theorem — the test exercises one concrete scenario, not a general proof that nesting is unbounded or that every tier interaction behaves this way |
| Yielding | **Primary:** the admissible policy set is *yielded* (deterministically derived) from declared labels: given the labels, the device computes the exact interval [Lo, U] (Theorem 1) and accepts only policies inside it. **Secondary:** a custodian *yields* authority (halt, delay, hand-over) under bounded budgets. | Admission algorithm; halt budget (D-29). | Proposed. Primary reading is a precise, testable function; secondary is informal. |
| Transformative / Adaptive / Reconfigurable | The system can change class sets, tables and algorithms over decades while preserving invariants (renewal invariant, class retirement). | `DECLARE_CLASS_DEAD`, T2 renewal. | Proposed; adaptation is bounded to labelled classes. |
| Architectures (plural) | The kernel is meant to host other computational models, not only PQC authority. | None implemented. | **Speculative** |
| Paradigm | A claim of a new way of computing or building systems. | Not supported by evidence. | **Speculative**; the repository makes no paradigm claim. |

If "Yielding" is later given a different intended meaning by the owner, record it as an ADR and revise this table; do not silently change it.

## Scope
In scope: long-lived authority and update governance for devices and artefacts that outlive their makers, custodians and algorithms; PQC migration as one application (class retirement); fault-model-explicit policy design; simulation and proof tooling.
Out of scope until evidence exists: a new computational model, general OS/agent claims, hardware attack content, safety-certified fault tolerance claims (see R-1).

## Non-goals
Not a PQC algorithm library; not a PKI replacement claim; no physical-attack material against MCU lock bits; no invented equations.

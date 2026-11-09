# ADR-015: Slot-holder co-signature for key installation

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: none (new)

## Context
F-R2-03: without a holder co-signature, any outside quorum that reaches a tier's custody threshold
can install its own keys into every ACTIVE slot, closing the gap to full control without that slot's
current holder ever participating (`tests/redteam_r2/r2_paths.py`, `rotate` vs the fix).

## Decision
Requirement REQ-LIFE-02: installing a key into an ACTIVE slot MUST require that slot's own holder to
co-sign the installation.

Implemented as:
- `ac_key_install_authorised(t, S, holder_atom, active)` in `src/policy8.c`: requires the admission
  table to authorise the transition AND, when the slot is active, the holder's atom to be present in
  the evidence set S. Tested by `tests/redteam_r2/fixcheck.c` (cases I, J, K).
- `Repl3OK` in `simulations/tla/FirstStage.tla`: slot 3's replacement now additionally requires
  `ValidSig(r.sg, Esc)` whenever `SlotActive(Esc)` holds, modelling the holder's own co-signature.

## Consequences
Raises the cost of the "rotate without the holder" escalation path identified by F-R2-03: an attacker
below the T2 threshold can no longer install keys into a slot it does not already hold evidence for.
A slot with no key yet (not ACTIVE) has no holder to co-sign, so first installation is unaffected.

The C primitive is unit-tested and passing (`fixcheck.c` I/J/K). The TLA+ model-checking run of
`Repl3OK` under `cfg_base` (GATE-08) did not finish: it was killed after 14m43s having generated
249M states (40M distinct), with its queue falling from an 8.5M peak to 4.9M when stopped —
converging, not diverging, but slower than the time available for this pass. This is a capacity
problem, not a reported violation, so it neither confirms nor refutes the model-level change;
GATE-08 remains not passed and should be re-run with more time/memory or a reduced configuration.

## Alternatives considered
Allow rotation by other parties — rejected: this is exactly the gap F-R2-03 identifies, and
`r2_paths.py` shows it collapses the minimum-cut distance from T1 to full control.

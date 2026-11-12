# ADR-040: Re-keying a slot whose holder is lost

**Status:** Proposed
**Date:** 2026-11-12
**Legacy IDs:** Legacy: none (new; resolves OQ-12)

## Context
REQ-LIFE-02 (ADR-015) requires the current holder to co-sign any key installed into an ACTIVE slot, to close F-R2-03. If the holder has lost the key, no co-signature is possible, and no document said how such a slot is re-keyed (OQ-12).

## Decision
Re-keying a slot whose holder is lost is two transitions:
1. Retire the slot: a T1 tightening, refused if fewer than t+s+1 classes would remain (REQ-LIFE-01).
2. Install the new key into the now-EMPTY slot: a T2 action (`KEY_INSTALL` maps to T2 in `src/kernel.c`). With no holder, REQ-LIFE-02's co-signature does not apply (`ac_key_install_authorised` with `active = 0`).

The co-signature is never waived for a slot that is still ACTIVE.

## Consequences
- Safety: the path gives an attacker no shorter route to full control than the co-signature rule alone (`models/lost_holder.py` part 1, all three reference profiles). This follows almost directly from step 2 requiring T2 evidence by itself; retirement removes atoms and never adds any to an attacker's set.
- Liveness, terrestrial: after the loss of any one whole custody group, the survivors can still retire (T1 OPERATE live) and install (T2 RECOVERY live) (part 2).
- Liveness, remote: **the path does not work.** The remote T2 table needs all three custody groups, so after losing a whole group the survivors can retire the slot but never fill it (part 3). A remote device that loses a custody group cannot be re-keyed; this follows the existing impossibility catalogue (the remote profile is live against one key loss, not one group loss). Fleets that need this must use the terrestrial profile.
- First-stage model: in `simulations/tla/FirstStage.tla`, where slot 3 is also the escrow slot, revoking slot 3's current key requires slot 3's own signature (PAM rule). With slot 3's key lost (`EscLost`), slot 3 is never replaced (exhaustive, one request). See GATE-08r for the two-request runs.
- An attacker who holds T1 evidence can retire honest slots. This is a denial-of-service bounded by REQ-LIFE-01, and it is publicly witnessed (REQ-PUB-01).

## Alternatives considered
- Let the T2 RECOVERY tier override the co-signature on an ACTIVE slot. Rejected: it reopens F-R2-03 for any party that can reach T2 RECOVERY, and makes "the holder must consent" conditional.
- No mechanism (slot is lost forever). Rejected: governance loss after one custodian loss contradicts the recoverable T2 budget.

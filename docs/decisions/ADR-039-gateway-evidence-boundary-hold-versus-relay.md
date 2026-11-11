# ADR-039: Gateway evidence boundary — HOLD versus RELAY

**Status:** Accepted
**Date:** 2026-11-11
**Legacy IDs:** (none — new decision; extends ADR-035)

## Context

ADR-035 decided that devices which cannot host the kernel sit behind sectored containment gateways
with signed configuration and dated exit, and that each such gateway is itself a governed device
running the kernel. ADR-035 does not say what, precisely, a gateway may assert *on behalf of* a
device it fronts, as opposed to what it merely relays. Item 33 of the 50-things completion list
(`docs/architecture/gateway-pattern.md`) found that this gap needs an explicit rule, not just prose:
without one, nothing stops a gateway-relayed signal from being silently treated as equivalent to a
device's own independent evidence (most dangerously, a relayed presence-like signal being modelled
as `PRES` instead of `WIT`), which would misrepresent the fleet's actual safety margin.

## Decision

Every evidence atom a gateway carries about a fronted device MUST be labelled as one of:
- **HOLD**: the gateway itself holds the key/secret/decision logic and asserts on the device's
  behalf. Modelled with the gateway's own group label (e.g. `group:GATEWAY`), so that compromising
  the gateway process counts as a single fault against every HOLD atom it carries, using the
  existing group-label convention in `models/lint.py` — no new fault-model mechanism.
- **RELAY**: the device itself holds the key or produces the signal, and the gateway only forwards
  it unmodified, so the gateway's own compromise alone does not yield it.

A signal observed or forwarded by a gateway that resembles physical presence but is not sampled by
a locked stage per REQ-PRES-01 (firmware-independent input, sampled at reset, before second-stage
code runs) MUST be modelled as `WIT` (exposure only), never as `PRES`, regardless of how it is
wired or reported.

## Consequences

- `models/gateway_lint.py` gives this rule a runnable reference check (CLM-51, CLM-52 in
  `docs/research/evidence-register.md`): a HOLD-only gateway profile collapses to a single fault
  class per CLM-02, and a table that mistakes a relayed signal for presence is unsafe even against
  a zero-fault attacker.
- The residual-risk statement in `docs/architecture/gateway-pattern.md` follows directly: a
  compromised gateway can lie about every device behind it for every HOLD atom, and this is not the
  same safety property as the kernel running natively on the device. This must not be described as
  equivalent in any planning or customer-facing material.
- Deployment design should actively seek and preserve RELAY-category evidence (surviving
  device-held keys, physically pass-through signals) wherever a legacy device happens to retain any,
  since it is the only way to narrow — not close — the gap this ADR formalises.
- `docs/architecture/brownfield-containment-guide.md` applies this rule in a worked example.

## Alternatives considered

- **Treat all gateway-relayed evidence as equivalent to native device evidence.** Rejected: this
  would silently misstate the fleet's safety margin, exactly the error REQ-PRES-01 and the R2
  red-team findings exist to prevent for presence specifically, and the same error class applies to
  custody evidence generally.
- **Leave the HOLD/RELAY distinction as prose guidance only, with no runnable check.** Rejected per
  this project's own rule against describing unverified judgment calls as settled; a lint profile
  that can actually compute the safe-and-live interval for a gateway-fronted claim is strictly
  better evidence than a paragraph asserting the same conclusion.

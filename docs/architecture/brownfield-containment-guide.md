<!-- Title: Brownfield and containment: a how-to -->
> New (2026-11-11), item 34 of the 50-things completion list. Document level: L2 (architecture).
> Evidence labels follow `docs/research/evidence-register.md`. This document is a how-to built from
> existing material — `docs/architecture/system-architecture.md` §5.1 (V6), §5.8 (P3 retrofit),
> `docs/architecture/mechanisms.md` §6.16, `docs/decisions/ADR-035-sectored-containment-with-dated-exit-gateways.md`,
> and `docs/architecture/gateway-pattern.md` (item 33) — and adds no new theory of its own. The
> worked example is illustrative [Proposed], not a report of a real deployment: no such deployment
> exists in this project yet, and this document says so rather than implying otherwise.

# Brownfield and containment: a how-to

## Why this document exists

Nearly every other document in this repo assumes a greenfield device: one designed from the start
to run `ac-core`. Most real fleets are not that. They are existing devices, bought, installed and in
many cases certified years before this kernel existed, that cannot be redesigned around it. This
document is the practical complement to that fact: a decision tree for what to do with one existing
fleet device, and one worked example carried all the way through rather than left as an abstract
pattern.

## Decision tree

```text
START: you have an existing (brownfield) device in the fleet.
|
|-- Can the device's firmware be modified at all (not locked, not certified-frozen,
|   has spare flash/ROM for a locked first stage, has or can gain a presence input)?
|     YES --> This is NOT a brownfield problem. Follow the greenfield path: P1 single
|             chip or P2 safety split (system-architecture.md §5.8). Stop here; this
|             guide does not apply.
|     NO  --> continue
|
|-- Does the device sit on a network/bus a gateway could realistically front
|   (serial bus, fieldbus, Ethernet segment) without breaking its real-time
|   safety function?
|     NO  --> This device is out of scope for governed change today. Record it
|             honestly as an uncovered asset (do not invent a mechanism for it).
|             Candidate for the zero-crypto safety-core pattern (P2) only if it is
|             ever redesigned; until then it is accepted residual risk, full stop.
|     YES --> continue
|
|-- Does the device still hold ANY of its own secret (a factory-provisioned key,
|   a device-unique certificate) that a gateway could relay but not forge?
|     YES --> Gateway pattern (docs/architecture/gateway-pattern.md), WITH at least
|             one RELAY-category atom in the profile. This is the best case this
|             guide covers: narrows, but does not close, the HOLD/RELAY gap.
|     NO  --> Gateway pattern, HOLD-only. Proceed, but the residual-risk statement
|             in gateway-pattern.md applies in full: a compromised gateway can lie
|             about every device behind it, with no mitigating device-rooted
|             evidence at all. This MUST be stated in the deployment's own risk
|             record, not only in this repo.
|
|-- Does the device have (or can a technician-operated local input be added at
|   the GATEWAY, not the device) a presence signal, and will your deployment
|   accept that this is presence AT THE GATEWAY'S SITE, not independently
|   verified presence AT THE DEVICE?
|     YES --> The gateway's OWN kernel instance (it is itself a governed device,
|             ADR-035) can use a genuine PRES atom for its own T2 tier. This does
|             NOT upgrade any RELAY/HOLD atom asserted on the device's behalf to
|             PRES-kind — keep those as WIT or SIG per gateway-pattern.md.
|     NO  --> The gateway's own T2 (constitution) tier is capped at whatever a
|             no-presence (remote) profile can offer (system-architecture.md §5.7).
|
|-- Set a dated exit clock on the containment (ADR-035: "sectored... with dated
|   exit"). A gateway that is never revisited is exactly the V6 failure mode
|   system-architecture.md §5.1 already warned about: "temporary enclaves become
|   permanent." Put a real calendar date on it, assign an owner, and treat the
|   date passing without action as an incident, not a formality.
|
DONE: you have a sectored, dated-exit, gateway-fronted device with an honest
HOLD/RELAY accounting of what the fleet can actually rely on for it.
```

## Worked example: a legacy Modbus RTU at a water treatment site

### The device

A Remote Terminal Unit (RTU) controlling a chemical dosing pump at a water treatment plant,
installed roughly a decade ago. Facts assumed for this example [Proposed — illustrative, chosen to
be a realistic composite of commonly-described OT deployments, not a specific real site]:

- Fixed firmware in masked ROM; no update mechanism exists, let alone one with spare space for a
  locked first stage.
- Communicates over serial Modbus RTU (no transport security; the protocol has none built in, per
  `mechanisms.md` §6.14's note that "industrial protocols... unchanged real-time paths stay
  symmetric").
- No cryptographic key of any kind. It was never provisioned with one; "device-unique secret" is
  not available at any point in this example. This is the HOLD-only branch of the decision tree.
- A physical key-locked selector switch exists at the RTU's enclosure (local/remote mode), wired
  directly to the RTU, not to anything that could become a gateway input.
- Decommissioning or replacing it is out of scope for the operator this quarter; the real decision
  being made is "how do we bring this under governed change without touching it."

### Walking the decision tree

1. **Can firmware be modified?** No — masked ROM, no update path, no spare flash, no presence
   input that could be repurposed. Confirmed brownfield.
2. **Can a gateway front it without breaking its real-time function?** Yes — Modbus RTU is a
   polled serial protocol; a gateway can sit on the bus as a protocol-aware intermediary without
   touching the RTU's control loop (the dosing-pump safety function itself stays untouched, per the
   zero-crypto safety-core principle in `mechanisms.md` §6.13/ADR-026 — this example does not put
   any of our cryptography near the pump's actual control path, only around the governance of
   configuration changes sent to it).
3. **Does the device hold any of its own secret?** No. HOLD-only branch.
   → Gateway pattern, `docs/architecture/gateway-pattern.md`, with the honest limitation that every
   claim the fleet receives about this RTU is a HOLD atom rooted entirely in the gateway.
4. **Presence?** The RTU's own key switch is wired to the RTU, not the gateway, and this example's
   gateway has no separate local input added. Two honest options, and this example picks the first:
   - **(chosen)** Do not claim device-level presence through the gateway at all. The RTU's key
     switch continues to govern *local/remote mode* as it always has, entirely outside this
     framework's evidence model — this document does not pretend to absorb it. Any `WIT`-kind
     relay of "someone reported being at the RTU" is logged as `GW_RELAY_SIGNAL` (exposure only,
     `models/gateway_lint.py`'s atom of that name) and never promoted to a `PRES` atom, per
     gateway-pattern.md's explicit rule.
   - (not chosen here, but valid) Add a genuine presence input at the gateway's own enclosure,
     which only raises the *gateway's own* T2 tier (ADR-035 — the gateway is itself a governed
     device) and still does nothing for RELAY/HOLD atoms about the RTU specifically.
5. **What does the gateway actually assert, concretely, for this RTU?**
   - HOLD: "I observed a Modbus write to this RTU's dosing setpoint register, within the configured
     envelope, at this time" — a fact about the gateway's own perimeter view, signed by the
     gateway's own `GW_HOLD1`/`GW_HOLD2`-equivalent keys (`group:GATEWAY` in
     `models/gateway_lint.py`'s terms).
   - WIT: that observation is wrapped in a witnessed receipt and logged (`GW_WIT`), giving exposure
     (a tampered or omitted log entry is detectable after the fact) but, per §3.8 of
     `mathematical-foundations.md`, no independent safety property.
   - Nothing RELAY-category exists for this RTU specifically, because step 3 found no device-held
     secret. This gap is recorded, not hidden.
6. **Dated exit.** The gateway's configuration is signed with an explicit review-by date (e.g. one
   year out). Passing that date without a human decision (renew the containment with a fresh
   ceremony, replace the RTU, or accept and re-date the risk explicitly) is treated as an incident.

### What this does and does not achieve, stated honestly

- **Achieves:** every configuration change reaching this RTU through the gateway is now signed,
  tiered and logged, where before it was an unauthenticated serial write any bus-connected device
  could issue. That is a real improvement over the status quo.
- **Does not achieve:** anything resembling the safety property of the RTU running the kernel
  itself. Per `gateway-pattern.md`'s CLM-02-based argument, every claim about this specific RTU
  collapses to a single fault class (the gateway process), because there was no device-held secret
  to relay. A gateway compromise here is not "one of several faults the system tolerates" — for
  this RTU's evidence specifically, it is total.
- **Does not fit cleanly at all:** the RTU's own key-switch-governed local/remote mode is a real,
  pre-existing physical control that this framework does not model, absorb, or improve — it simply
  continues operating alongside the gateway's governance, unconnected to it. Pretending otherwise
  (e.g. by wiring that switch into the gateway and calling it a `PRES` atom for the RTU) would be
  exactly the mistake `gateway-pattern.md` test D exists to catch: that switch, observed by a
  gateway rather than sampled by a locked stage at reset, cannot meet REQ-PRES-01, and relabelling
  it does not change that.

## See also

- `docs/architecture/gateway-pattern.md` — the HOLD/RELAY distinction and residual-risk statement
  this guide applies.
- `docs/decisions/ADR-035-sectored-containment-with-dated-exit-gateways.md` — the standing decision
  that containment is sectored and dated, not indefinite.
- `docs/architecture/mechanisms.md` §6.16, `docs/architecture/system-architecture.md` §5.1 (V6),
  §5.8 (P3) — the architectural material this guide turns into a procedure.

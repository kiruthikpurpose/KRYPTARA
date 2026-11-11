<!-- Title: Gateway pattern for devices that cannot host the kernel -->
> New (2026-11-11), item 33 of the 50-things completion list. Document level: L2 (architecture).
> Evidence labels follow `docs/research/evidence-register.md`: Established / Derived / Proposed /
> Hypothesis / Speculative / Refuted. The runnable reference check backing the Derived claims below
> is `models/gateway_lint.py` (`python3 models/gateway_lint.py`), registered as CLM-51 and CLM-52.
> This document extends, and does not duplicate, `docs/decisions/ADR-035-sectored-containment-with-dated-exit-gateways.md`
> and `docs/architecture/mechanisms.md` §6.16: those establish *that* a gateway is itself a governed
> device running the kernel; this document specifies *what it may assert on behalf of a device it
> fronts*, which neither existing document states precisely.

# Gateway pattern for devices that cannot host the kernel

## Why

Many operational-technology (OT) devices cannot run `ac-core` directly: fixed-function PLCs, RTUs
and meters too small for the locked stage, devices with certified or regulator-locked firmware that
cannot be modified without re-certification, or hardware with no lockable first-stage flash region
at all (`docs/architecture/mechanisms.md` §6.13). `docs/architecture/system-architecture.md` §5.8
already names the pattern for this (**P3 retrofit**: "Sectored PQ gateways with signed configuration
and dated exit; the gateway itself runs the kernel as its own governed device") and §5.1's V6
analysis of perimeter-centric designs gave the honest verdict this document keeps: a gateway "does
not fix any updatable device; temporary enclaves become permanent" unless bounded by the dated-exit
discipline in ADR-035. What neither document says is exactly what evidence a gateway can
*legitimately stand in for* versus what it can only *carry through unmodified* — that gap is this
document's subject. [Proposed]

## HOLD versus RELAY

Every evidence atom the fleet receives about a fronted device arrives through the gateway. Two
categories exist, and the difference between them is the entire content of this document:

| Category | Definition | Who can forge it |
|---|---|---|
| **HOLD** | The gateway itself possesses the key, secret, or local decision logic, and asserts on the fronted device's behalf (e.g. the gateway signs "this Modbus frame from unit 14 is within its configured envelope" using a key the gateway — not the PLC — holds). | Anyone who compromises the gateway process, full stop. |
| **RELAY** | The fronted device itself holds a key or produces a signal (a factory-provisioned certificate it still has, a contact closure wired to a physical maintenance switch) and the gateway only forwards it unmodified. | Only someone who compromises the device itself, or who compromises both the device's output path AND the gateway (two independent faults, not one). |

[Proposed] This is the one precise rule this document adds on top of ADR-035: **a gateway profile
MUST label every atom it carries as HOLD or RELAY**, and a HOLD atom's compromise set MUST include
"the gateway process is compromised" as a single fault, not as the multi-atom independence the same
atom shape would get if it were genuinely device-rooted. `models/gateway_lint.py` gives this a
concrete, checkable form by reusing the existing group-label convention (`models/lint.py`'s "atoms
sharing a group label are compromised together"): a gateway's two HOLD key shares are labelled
`group:GATEWAY`, exactly as the reference layout labels OEM1/OEM2 `group:OEM`, because both live in
one administrative/physical entity. No new fault-model mechanism was invented for this; the existing
one already says the right thing once the label is honest.

### What a gateway can legitimately HOLD

- Facts about **its own perimeter**: which ports are open, what protocol translation it performed,
  whether a frame it forwarded was within a configured envelope, when it last rotated its own keys.
  These are true statements about the gateway, not about the device, and the gateway is the right
  authority for them.
- A **relay witness atom** (`WIT` kind) wrapping its own report of what it observed — subject to the
  same rule as every other `WIT` atom in this framework (§3.8 of
  `docs/theory/mathematical-foundations.md`): exposure only, never an independent safety property.
  [Established — restates existing theory, not new]
- Its own custody tier (T1/T2) governance, run exactly like any other device, per ADR-035 and
  `mechanisms.md` §6.16. That part of the pattern is unchanged by this document.

### What a gateway can only RELAY — or must honestly say it cannot provide at all

- **A fronted device's own cryptographic signature**, if the device still holds a key the gateway
  cannot access. Rare in true brownfield (most legacy OT devices were never provisioned with a
  device-unique key at all), but when it exists it is the single most valuable evidence a gateway
  pattern can carry, because it survives gateway compromise. `models/gateway_lint.py` test C shows
  this concretely: one independent device-held key (`DEV_OWN`) restores safety that a HOLD-only
  gateway cannot provide on its own (test B). [Derived — CLM-51]
- **Physical presence.** `docs/specifications/requirements.md`'s REQ-PRES-01 requires presence to be
  sampled by the locked stage itself, from an input firmware cannot drive, at reset, before any
  second-stage code runs. A gateway is a general-purpose host running full second-stage-equivalent
  software; by definition it cannot meet REQ-PRES-01 for a device it merely fronts. A "a technician
  reported being on-site" signal relayed through a gateway is **not a PRES atom** no matter how it
  is wired, and must be modelled as `WIT` (exposure, free to the attacker per §3.8), never as `PRES`.
  Treating it as PRES would be the exact mistake REQ-PRES-01 exists to prevent. `models/gateway_lint.py`
  test D shows this formally: a table that mistakes a relayed signal for presence is unsafe even
  against an attacker who has compromised *nothing* (t=0), because `WIT`-kind evidence is always
  free. That is not "weaker than real presence" — it is a table with no safety property at all.
  [Derived — CLM-52]
- **Anything requiring the device's own internal state at the moment of the claim**, if the device
  has no sensor or interface the gateway can read. The honest answer here is "this gateway profile
  cannot assert that", not an approximation.

## Why a gateway's own assertion is categorically different from the device's

The interval-admission theory (`docs/theory/mathematical-foundations.md` §3.3–3.4, Theorems 1–2,
CLM-01/CLM-02) treats safety as holding against every compromise set in the declared structure, and
liveness as holding against every loss set. A device running the kernel natively distributes its
evidence across atoms rooted in genuinely separate custody groups, families and (for terrestrial
profiles) a firmware-independent physical input — enough independent classes (k ≥ t+s+1, CLM-02) to
have a non-empty safe-and-live interval at a useful tier. A gateway asserting "the device behind me
is fine" collapses that structure: every HOLD atom for every fronted device shares the one fault
"the gateway process is compromised." Under the fleet's own accounting rules, that is k=1 for
everything the gateway holds, and CLM-02 says directly that k=1 cannot be both safe against t=1
compromise and live against any loss (t+s+1 ≥ 2 > k=1) — there is no tier available with a single
atom class that is both recoverable and safe. [Derived — restates CLM-02 applied to this case;
`models/gateway_lint.py` test B gives the concrete instance]

This is why the distinction matters operationally, not just formally: a device making its own claim
and a gateway making the same claim on the device's behalf are not interchangeable inputs to the
same safety argument. Treating a gateway's HOLD-only assertion as equivalent to the device's own
PRES/SIG evidence would silently inflate k without actually adding an independent class.

## The residual risk, stated plainly

**A compromised gateway can lie about every device behind it.** This is not a hypothetical edge
case this document is hedging against — it is the direct consequence of the HOLD category existing
at all, and it is **not the same safety property as the kernel running natively** on each device.
Nothing in this pattern, no amount of signed configuration or dated exit clock, changes that a
single gateway compromise is a single fault that can forge every HOLD-based claim about every
device it fronts simultaneously. The dated-exit discipline in ADR-035 bounds *how long* this
exposure is tolerated and forces a decision point; it does not reduce the blast radius of a
compromise that occurs before the exit date. [Proposed — this is the design's own honest accounting,
not a result that can be "improved away" by better engineering within this pattern]

**What this pattern is actually worth, stated honestly:**
- It gives devices that structurally cannot run the kernel *some* governed-change discipline (signed
  configuration, logged transitions, a cohort view, an exit deadline) where the alternative is none.
- It is strictly weaker, for every fronted device, than that device running the kernel itself, by
  exactly the gap CLM-02 makes precise above. It should never be described, in any planning
  document or customer-facing material, as providing the same guarantee as native kernel deployment.
- Preserving and relaying any device-rooted evidence the legacy device still happens to have (an
  old factory key, a physical keyswitch wired through rather than observed and reported) is the only
  way to narrow that gap, and should be actively sought during gateway deployment design rather than
  treated as an optional nicety.

## Lint profile

`models/gateway_lint.py` is the runnable reference lint for this pattern, in the same style as
`models/lint.py` and `models/second_domain_ca_root.py`: a 5-atom layout (`GW_HOLD1`, `GW_HOLD2`,
`DEV_OWN`, `GW_RELAY_SIGNAL`, `GW_WIT`) and four concrete checks (`_tests()`), run with
`python3 models/gateway_lint.py`. It does not introduce new admission theory; it applies the
existing interval/label machinery honestly to the gateway case. See CLM-51 and CLM-52 in
`docs/research/evidence-register.md` for exactly what it checks and its limits.

## Cross-reference

See `docs/architecture/brownfield-containment-guide.md` for a worked end-to-end example (a legacy
Modbus RTU) that applies this pattern, and for the decision tree covering when a gateway is the
right answer at all versus when a device should simply stay out of scope.

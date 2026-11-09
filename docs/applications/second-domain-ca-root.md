<!-- Title: Second application domain: root CA key governance -->
> New (2026-11-09), item 46 of the 50-things completion list. Tests HYP-07 ("the kernel generalises
> beyond update/authority governance") against a real domain that is explicitly NOT a device/update
> problem. Document level: L3 (illustrative application). Evidence labels: [M] machine-checked by
> `models/second_domain_ca_root.py`, [H] hypothesis, [E] estimate.

# Second application domain: root CA key governance

## Why this domain

Root Certificate Authority key governance is a real, long-running, already-institutionalised
problem: root CA ceremonies already require physical, witnessed, multi-party attendance; Certificate
Transparency (RFC 9162) already runs a public append-only log network. Unlike a device fleet, there
is no firmware, no boot sequence, and no hardware at all — testing whether the SAME admission math
fits a domain with none of those removes the risk that any apparent generality is really just "every
example so far has been a device."

## The mapping

| KRYPTARA concept | CA-root equivalent |
|---|---|
| Evidence atom (SIG) | A root-key custodian's signing key (CA operator, independent auditor/trustee, root-program representative), each holding two algorithm families (RSA, ECDSA) |
| PRES | Physical ceremony-room attendance — this is literally how real root ceremonies already work, not an analogy |
| WIT | Publication to a Certificate Transparency log — arguably a BETTER fit than KRYPTARA's own primary domain, where the witness-log network (`ac-wit`) doesn't exist yet (REQ-PUB-01) |
| T1 (OPERATE) | Routine intermediate cross-signing / policy-constrained issuance |
| T2 (RECOVERY) | Root re-key or root policy change — the rare, ceremony-gated action |

## What machine-checked [M]

`models/second_domain_ca_root.py`, 3/3 cases:
- Routine issuance is 1-safe and live against losing any one custodian.
- The root-ceremony tier is 1-safe and live against any two losses except losing both algorithm
  families entirely (the exact shape of the device domain's RECOVERY tier, same formula structure:
  presence + ≥2 surviving keys + (log or a second surviving group)).
- A 2-safe root-ceremony tier is NOT simultaneously live against even one loss — **the identical
  impossibility Theorem 3 predicts in the device domain**, same arithmetic, different nouns.

## Where it strains [H]

- **No boot/image concept exists in CA governance at all.** REQ-IMG-01 (locked stage boots only the
  committed digest) and the staged-effect halt machinery (REQ-HALT-01) have no analogue here — a CA
  doesn't "boot." Expressing them anyway would be forcing the domain to fit the kernel rather than
  the reverse.
- **`DECLARE_CLASS_DEAD` maps awkwardly.** In the device domain it means "this custody group's key
  is gone, permanently." In CA governance, the nearest analogue — deprecating a root certificate —
  is a different lifecycle shape: the root doesn't die because a KEY died, it dies on a published
  schedule for unrelated (often purely calendar) reasons. Forcing this mapping would misrepresent
  both domains.
- **The chain/record model (REQ-CHAIN-01) maps unusually well** — CT logs already ARE a hash chain
  with inclusion proofs (RFC 9162), arguably the one place this domain is a cleaner fit than
  KRYPTARA's own primary target.

## Verdict on HYP-07

The core admission math (Theorem 1/2/3, the interval computation, the tier-table pattern) carries
over to a structurally different domain without any new theory — same code
(`models/lint.py`/`interval.py`), different atom labels. The STAGED-EFFECT and IMAGE-BOOT layers do
not carry over at all; those are specific to governing a thing that runs code, not to governing a
key. **Per the 50-things list's own stop condition**: this is a positive result for the kernel's
core (admission/tiers/evidence), not a positive result for "the whole kernel generalises to
anything." The honest scope statement, per that stop condition, is: *the admission/tier/evidence
layer generalises across device and non-device long-lived-authority domains; the boot/image/halt
layers are device-specific and should not be claimed as general.*

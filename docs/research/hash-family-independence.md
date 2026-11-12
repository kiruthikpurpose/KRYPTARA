# Hash-family independence: internal analysis for EXP-18

**Level:** L3. **Date:** 2026-11-12. **Status:** internal analysis only. EXP-18 asks for a review by cryptographers; none has taken place, so GATE-11 stays "not run". This document narrows what the design may claim until that review exists.

## The claim under test

CLM-11 says the SHA-2 and Keccak families can be counted as two independent fault classes. The dual-family profiles depend on it: tier T1 OPERATE is "safe against one family break" only if a break of one family leaves the other intact.

## What the two families share, and what they do not

| Aspect | SHA-2 (FIPS 180-4) | SHA-3 / SHAKE (FIPS 202) | Shared? |
|---|---|---|---|
| Construction | Merkle–Damgård with a Davies–Meyer style compression function | Sponge over the Keccak-f permutation | No. [Established: the two standards] |
| Origin | Designed by NSA | Public competition | No |
| Generic attacks (birthday bounds, Grover-type quantum search) | Apply | Apply | **Yes.** Generic attacks depend on output and capacity sizes, not on the design |
| Security argument of the signature scheme built on top (LMS in SP 800-208, SLH-DSA in FIPS 205): second-preimage and multi-target arguments | Used | Used | **Yes.** The same proof structure sits above either hash (risk R-8) |
| Signature-wrapper code in this project (one LMS verifier, two hash back ends) | Same code | Same code | **Yes.** An implementation fault is common to both |
| Who holds the keys, in which HSM | Same custody groups | Same custody groups | **Yes**, but this is already a separate label (group) in the model |

So the families are independent with respect to a structural break of one primitive. They are not independent with respect to a generic advance, a flaw in the shared signature argument, or a bug in the shared verifier. [Derived from the table; the weight of each row is a judgement that EXP-18 reviewers must make.]

## What the model says if the shared cause happens

`models/common_cause.py` (cases E–H) declares one common cause covering every signature atom, which is the worst case in the right-hand column, and recomputes the admissible interval for each reference tier [Derived, machine-checked, CLM-56]:

| Profile and tier | One family breaks (the designed-for case) | Both break through a shared cause |
|---|---|---|
| Terrestrial T1 OPERATE | safe | **unsafe; no table can meet the tier's budget** |
| Terrestrial T2 CONST, RECOVERY | safe | safe and live (presence is required and is not a signature) |
| Remote T1, T2 | T1 safe | **no safe table at either tier** |
| Nano with presence | safe | safe |

## Decision on the claim

1. CLM-11 is **reduced**, not removed: the families count as two classes for structural breaks of a primitive only. This is recorded in the evidence register.
2. Against the shared causes, the design's protection is physical presence, not the second family. Terrestrial T2 and the nano-with-presence profile keep their guarantees. Terrestrial T1 and the whole remote profile do not.
3. The remote profile therefore has an unmitigated residual: a generic break of hash-based signatures defeats it. This was already listed as risk R-8; the model now shows it concretely. The planned third class for remote fleets (C-16) does not help unless it is not hash-based.
4. None of this replaces EXP-18. If reviewers judge the shared rows above to be non-negligible in practice, the 50-item plan's stop condition applies: default to one hash family plus presence.

## Limits

The analysis treats a shared cause as all-or-nothing. It says nothing about likelihood. The table of shared aspects is drawn from the cited standards and from this project's own design, not from a literature survey of cryptanalysis.

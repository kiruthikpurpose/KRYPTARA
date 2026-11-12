# PQC migration profile: migration as class retirement

**Level:** L3 (application profile). **Date:** 2026-11-12. Evidence labels as in the evidence register. The worked schedule below is the output of `models/pqc_migration.py` [M]; the dates are policy inputs [S, secondary sources], not results.

## Dates used

NIST IR 8547 (*Transition to Post-Quantum Cryptography Standards*) was reported final on 2026-10-27, deprecating quantum-vulnerable public-key algorithms after 2030 and disallowing them after 2035 [S, trade press, re-verify against the NIST publication page before citing]. In this project those two years become **label-retirement dates** for the classical family (ADR on D-31, ADR-011): after 2030 no new authority may depend on an ECC atom; after 2035 the class is dead.

## The migration, in kernel terms

A migration is not an algorithm swap. It is two governed transitions, repeated per custody group:

1. `KEY_INSTALL` of the new hash-family key into the group's second slot. This is a T2 action (`src/kernel.c` action table) and, because the slot is ACTIVE, requires the current holder's co-signature (REQ-LIFE-02).
2. After the last group has migrated, `DECLARE_CLASS_DEAD` for the classical family: a T1 tightening (REQ-LIFE-01), refused if fewer than t+s+1 classes would remain (`models/class_lifecycle.py`).

## Order matters [M]

| Year | Swap in place (one group per step) | Retire first, then install |
|---|---|---|
| 2026 | all tiers within budget | all tiers within budget |
| 2027 | within budget* | **all tiers below budget** |
| 2028 | within budget* | **all tiers below budget** |
| 2029 | within budget | RECOVERY below budget |
| 2030 | — | within budget |

\* While three families coexist (ECC, H1, H2), RECOVERY is live only if the loss of any two whole families is excluded from its budget, the same exclusion the steady state already makes for its two families. Losing H1 together with one of the second-slot families leaves a single key. This is a stated residual of the swap order, not a hidden one.

**Rule for operators:** install the replacement before retiring the old class, one custody group at a time. Never declare a class dead to make room.

## Limits

Reference 8-atom layout only. No timing, no fleet logistics (see SIM-02, the migration twin), no hazard rates. The dates are policy inputs from secondary sources.

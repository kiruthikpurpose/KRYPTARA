# ADR-002: Evidence atoms with device-derived assumption labels

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: D-22, J-27

## Context
Classes, not signature counts, determine safety.

## Decision
≤8 atoms (SIG/PRES/WIT), 32-bit labels; assumption labels derived on device; others declared at T2.

## Consequences
Closed world is explicit; labels can still be wrong if ceremonies are wrong (R-1).

## Alternatives considered
Count signatures; declared assumption masks; >8 atoms

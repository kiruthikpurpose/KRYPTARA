# ADR-009: Bounded halt budget

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: D-29, J-12

## Context
A stolen halt key must not freeze a fleet.

## Decision
h halts per atom per epoch; T1 RESUME cancels.

## Consequences
Not yet verified to completion in TLA+.

## Alternatives considered
Unscoped halt

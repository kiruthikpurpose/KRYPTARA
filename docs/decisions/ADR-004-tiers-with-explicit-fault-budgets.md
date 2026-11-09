# ADR-004: Tiers with explicit fault budgets

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: D-24

## Context
Weakest full-control path sets the security level (Theorem 3).

## Decision
T0 HALT, T1 OPERATE (1,1), T2 recoverable (1,2) default, fortress (2,1) optional.

## Consequences
Budgets are auditable.

## Alternatives considered
Uniform two-group rule (39% loss in SIM-01); ad hoc per-action rules

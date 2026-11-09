# ADR-014: Absent atoms count as compromised and lost; tables are projection-canonical

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: none (new)

## Context
R2 red-team F-R2-01, F-R2-02.

## Decision
Implemented in lint.py and policy8.c.

## Consequences
Slightly larger code (902 B).

## Alternatives considered
Treat absent as unavailable to attacker (unsafe)

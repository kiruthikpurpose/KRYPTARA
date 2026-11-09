# ADR-003: On-device interval admission

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: D-23, J-32, J-09

## Context
Theorem 1 characterises safe-and-live policies exactly.

## Decision
Install a table only if monotone and in [Lo, U] (and ≤ old when tightening).

## Consequences
Closes unsafe-policy installation; cost ≈0.9 KB code (measured).

## Alternatives considered
Host-only lint; fixed rule; policy interpreter

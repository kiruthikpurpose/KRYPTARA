# ADR-011: Renewal invariant and class retirement

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: D-31

## Context
Migration should be a maintained invariant.

## Decision
Keep ≥ t+s+1 live classes; DECLARE_CLASS_DEAD is a tightening.

## Consequences
Independence of classes is a hypothesis (CLM-11).

## Alternatives considered
Big-bang swaps

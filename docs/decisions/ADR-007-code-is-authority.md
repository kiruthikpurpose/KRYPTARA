# ADR-007: Code is authority

**Status:** Accepted  
**Date:** 2026-11-09  
**Legacy IDs:** Legacy: D-27, J-31

## Context
One OEM key could otherwise run arbitrary second-stage code.

## Decision
Locked stage boots only the committed image digest.

## Consequences
Needs lockable first stage (R-4).

## Alternatives considered
Boot any OEM-signed image

# ADR-025: NV contract with torn_read profile

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: D-06

## Context
Hardware hazard confirmed from vendor sources

## Decision
NV contract with torn_read profile; OTP/counter/FRAM preferred

## Consequences
Direct migration of a legacy Rev 4 decision (D-06, status CARRIED in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
Universal fault-handler trick (rejected in Rev 2)

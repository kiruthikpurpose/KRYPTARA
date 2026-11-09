# ADR-016: Recovery is the T2 recoverable tier: presence + two custody atoms + (publicity

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: D-32

## Context
Custody loss is the dominant 40-year risk; presence makes recovery single-fault safe

## Decision
Recovery is the T2 recoverable tier: presence + two custody atoms + (publicity or a second custody group) + delay. The lint refuses any configuration in which a single declared loss makes governance unrecoverable

## Consequences
Direct migration of a legacy Rev 4 decision (D-32, status NEW in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
Break-glass by all three groups (not live after any loss); escrow timers on device (time would grant authority)

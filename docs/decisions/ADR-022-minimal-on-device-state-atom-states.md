# ADR-022: Minimal on-device state: atom states EMPTY / ACTIVE / RETIRED

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: D-03

## Context
TLC lockout counterexample (~465k states) [M]; admission needs labels

## Decision
Minimal on-device state: atom states EMPTY / ACTIVE / RETIRED; anergy and molting off-device. Amendment: assumption labels are on-device in all profiles, derived from descriptors

## Consequences
Direct migration of a legacy Rev 4 decision (D-03, status AMENDED in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
Rev 2 kept masks only in host tools

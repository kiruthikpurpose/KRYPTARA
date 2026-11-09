# ADR-020: Hourglass with a pure-function kernel

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: D-01

## Context
Small, provable, portable (S 4.48 [M])

## Decision
Hourglass with a pure-function kernel; waist = ac_step + crypto table + platform table

## Consequences
Direct migration of a legacy Rev 4 decision (D-01, status CARRIED in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
A1–A6 (§5.2)

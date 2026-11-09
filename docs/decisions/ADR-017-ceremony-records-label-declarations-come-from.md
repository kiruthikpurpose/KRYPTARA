# ADR-017: Ceremony records: label declarations come from a machine-readable custody graph

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: D-33

## Context
Labels are the closed world. Making them evidence-backed and public narrows the gap (red-team X.2.2)

## Decision
Ceremony records: label declarations come from a machine-readable custody graph (who holds which key in which HSM, wrapped by what) captured by ac-ceremony and logged with the T2 transition

## Consequences
Direct migration of a legacy Rev 4 decision (D-33, status NEW in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
Hand-written labels

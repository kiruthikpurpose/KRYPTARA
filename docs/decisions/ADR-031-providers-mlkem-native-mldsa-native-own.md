# ADR-031: Providers: mlkem-native, mldsa-native

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: D-12

## Context
Maintained code; independence honesty

## Decision
Providers: mlkem-native, mldsa-native; own verify-only LMS and SLH-DSA; no PQClean/pqm4/liboqs in firmware. ML-DSA carries the Keccak label

## Consequences
Direct migration of a legacy Rev 4 decision (D-12, status CARRIED in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
(none recorded)

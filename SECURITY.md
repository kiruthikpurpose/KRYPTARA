# Security policy

**Supported:** the `main` branch. There are no releases or deployments.

KRYPTARA is a research repository for a governed-change kernel: admission policy math, a reference
C implementation, and formal models. It is **pre-Phase-0** on its own roadmap (`docs/implementation/
roadmap.md`) — there is no shipped firmware, no deployed instance, and no production secret material
in this repository. Treat findings accordingly: most "vulnerabilities" here are findings against the
*design*, which is exactly what `docs/theory/red-team-r2-findings.md` and the falsification programme
(`docs/validation/falsification-programme.md`) exist to track, in the open, as part of normal work.

## Scope

In scope for a security report:
- A flaw in the admission math (`models/interval.py`, `models/lint.py`) or its C implementation
  (`src/policy8.c`) where the two disagree, or where either contradicts the theorems in
  `docs/theory/mathematical-foundations.md`.
- A gap in the hardened API (`tests/redteam_r2/`) that lets malformed input past `ac_tbl_upper`,
  `ac_tbl_lower`, `ac_labels_valid`, `ac_faults_from_labels`, or `ac_key_install_authorised`.
- A red-team path to full control not already tracked in `docs/theory/red-team-r2-findings.md` or
  `tests/redteam_r2/r2_paths.py`.
- A real secret, token, or credential accidentally committed (there should be none; report
  immediately if found, independent of severity).

Out of scope (please use the normal issue tracker instead): missing features, requirements not yet
implemented (`docs/specifications/requirements.md` already lists these honestly), documentation
gaps, and anything already listed as a known limitation in `docs/theory/limitations-and-open-problems.md`.

## Reporting

Open a GitHub issue for anything that is not an accidentally-committed secret. This project has no
shipped deployment to protect and benefits from findings being public and attributable, the same way
the R2 red-team findings are: a tracked finding with a resolution is more valuable here than a private
disclosure with no public record. If a report involves an accidentally committed credential, say so
in the title without pasting the credential itself, and it will be rotated/removed immediately.

## What happens to a confirmed finding

1. It gets an `F-R2-NN`-style ID (or the next stream in sequence) in
   `docs/theory/red-team-r2-findings.md`.
2. If it implies a new requirement, it gets a `REQ-` ID in `docs/specifications/requirements.md` and
   an ADR via `docs/decisions/ADR-TEMPLATE.md`.
3. It is tracked to a fix or an explicit "open" status — see `docs/validation/validation-gates.md`
   for how gates move from "not passed" to "passed" in this repository: only on a check that
   actually ran and is reproducible with `./scripts/run_all_checks.sh`.

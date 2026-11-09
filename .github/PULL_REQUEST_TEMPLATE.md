## What changed and why

## Checklist (see CONTRIBUTING.md)
- [ ] Every new claim has an evidence class (Established/Derived/Proposed/Hypothesis/Speculative/Refuted)
      and, if Derived, a runnable check committed alongside it.
- [ ] New/changed decisions went through an ADR (`docs/decisions/ADR-TEMPLATE.md`) rather than editing
      an accepted one in place.
- [ ] `./scripts/run_all_checks.sh` passes locally.
- [ ] `python3 scripts/audit_docs.py` passes locally.
- [ ] No claim describes unrun work as done; unrun gates are labelled "not run", not left implied.
- [ ] Hardware/attack content stays defensive (no MCU-flash-lock bypass procedures).

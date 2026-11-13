# Governance

- **Maintainer:** Kiruthik M R (@kiruthikpurpose). The maintainer merges changes and owns the roadmap.
- **Decisions** are recorded as ADRs (`docs/decisions/`). An accepted ADR is superseded, never edited.
  Status values: Proposed, Accepted, Superseded. Acceptance criteria are written in the ADR itself.
- **Claims** carry one of six classes: Established, Derived, Proposed, Hypothesis, Speculative,
  Refuted. Every claim is in `docs/research/evidence-register.md`; a Derived claim names the command
  that reproduces it.
- **Gates** (`docs/validation/validation-gates.md`) pass only when a recorded command exits zero.
  "Not run" is a valid state. A failed gate on real silicon stops the roadmap and is reported.
- **Document hierarchy** and conflict rules: `docs/document-hierarchy.md`.
- **Owner decisions** still open are listed in `docs/research/open-questions.md`.
- **Independent review** (cryptographers, red team, a second implementation team) is sought, not
  assumed. Until it happens, docs say so.

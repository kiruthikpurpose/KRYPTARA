# Document hierarchy and conflict resolution

| Level | Contents | Authority |
|---|---|---|
| L1 | `CLAUDE.md`, `README.md` | Routing and rules for working in the repo |
| L2 | docs/vision-and-scope, theory/mathematical-foundations, theory/red-team-r2-findings, architecture/*, specifications/requirements, specifications/interfaces-and-data-models, decisions/ADR-*, decisions/legacy-decision-record, validation/*, simulation/*, research/evidence-register | Authoritative |
| L3 | executive summary, lifecycle, problem mapping, comparison, implementation, roadmap, resource estimates, limitations, source inventory, applications | Supporting; may be out of date |
| L4 | `research-archive/` (sources, legacy blueprints, streams, memos) | Historical; never overrides L1–L3 |

**Conflict resolution.** (1) Executable evidence (a passing script) beats prose. (2) Higher level beats lower. (3) Within a level, newer ADR beats older text and `red-team-r2-findings.md` beats Rev 4-derived text. (4) Unresolved conflicts are recorded in `docs/research/open-questions.md` with an ID, and the more conservative reading applies until an ADR decides.

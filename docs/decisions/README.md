# Decisions

ADR-001..038 are the authoritative decisions (L2). `legacy-decision-record.md` holds the full Rev 4
D/C/X/J tables, which remain valid unless an ADR supersedes them. Mapping: each ADR lists its legacy
IDs. Every D-xx ("DECIDED: what we are building") item now has an ADR — ADR-001..015 migrated the
load-bearing R2-era decisions first; `scripts/migrate_legacy_decisions.py` mechanically generated
ADR-016..038 for the rest (D-01..D-19, D-32..D-34, D-36) directly from the legacy table's own
Decision/Why/Alternatives columns, with no new analysis added. Re-run that script if
`legacy-decision-record.md` changes and new D-ids appear; it skips any D-id already referenced by an
existing ADR.

**Not migrated to individual ADRs, by design:** the C-xx (conditional), X-xx (research) and J-xx
(rejected) tables — roughly 80 items. These are not "decisions we build," which is what an ADR
records; they are gates-to-watch, research questions, and a record of rejected alternatives. Writing
one near-empty ADR file per item would be churn, not clarity. They stay in
`legacy-decision-record.md` as the authoritative record for their category, cross-referenced from the
ADRs and findings that depend on them (e.g. ADR-015 cites C-14's fortress tier; red-team-r2-
findings.md cites several J-ids).

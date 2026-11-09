# Source inventory

**Level:** L4 (historical) for the sources; this index is L3. Only material present in `research-archive/` is listed. Anything the project owner attached that is not listed here was **not reviewed** by this repository build. **No source mentions the name KRYPTARA** (grep of S01–S11 and all docs, 2026-11-09).

| SRC | Archive file | Size | Type | Author/origin | Role | Reliability note |
|---|---|---|---|---|---|---|
| SRC-01 | S01_Invention_Atlas_Authority_Continuity.md | 53,650 B | Claude-generated atlas | This programme | Origin of "authority continuity" thesis | Contains early over-claims later withdrawn (S03) |
| SRC-02 | S02_Managed_Trust_Plane.md | 57,491 B | Claude-generated report | This programme | "Managed trust plane" framing | Superseded by S05/S06 |
| SRC-03 | S03_Audit_Foundations_Revised_Thesis.md | 54,622 B | Self-audit of S01/S02 | This programme | Corrections and revised thesis | Higher reliability than S01/S02 |
| SRC-04 | S04_Second_Pass_Discovery_Atlas.md | 60,324 B | Claude-generated atlas | This programme | Second-pass discovery | Superseded by S05 |
| SRC-05 | S05_Unified_Atlas.md | 119,328 B | Claude-generated atlas | This programme | Unified atlas ("Trust That Outlives Its Makers") | Superseded by S06 |
| SRC-06 | S06_Atlas_2nd_Edition.md | 349,463 B | Claude-generated atlas | This programme | Latest atlas; literature-linked | Web-sourced claims partly verified (stream X_factcheck) |
| SRC-07 | S07_Global_Opportunity_Report.md | 59,429 B | Claude-generated report | This programme | Market/opportunity context | Contains market estimates; Estimate only |
| SRC-08 | S08_Gemini_God_Mode_Suggestions.md | 82,016 B | Third-party model text (Gemini) | External | Alternative reinvention suggestions | Unverified; claims corrected where checked |
| SRC-09 | S09_Gemini_Physical_Layer_Paper.txt | 21,550 B | Third-party model text (Gemini) | External | Physical-layer suggestions | Contains attack-adjacent material; **not used** in hardware discussion |
| SRC-10 | S10_ClaudeConvo_Transcript.md | 675,667 B | Conversation transcript | This programme | Full working history, 2026-11-05 to 11-06 | Contains superseded intermediate positions |
| SRC-11 | S11_Gemini_God_Mode_Reinvention_Atlas.txt | 59,703 B | Third-party model text (Gemini) | External | Same title as SRC-08 but **different content and size** (SRC-08 82,016 B vs SRC-11 59,703 B); relation not resolved | Unverified; treat as separate document |
| SRC-12 | legacy-blueprints/L1–L5 | — | Blueprints Rev 1–4 | This programme | L5 (Rev 4) is the base of the authoritative docs | Rev 4 predates R2 fixes |
| SRC-13 | streams/ (A, B, E, F, L, R, X_*) | — | Sub-agent working papers | This programme | Architecture, crypto, embedded, fleet, landscape, requirements, fact-check, prior-art, red-team | Agent output; spot-checked, not fully re-verified |
| SRC-14 | models/, simulations/, src/, tests/ | — | Code and models | This programme | Executable evidence | Reproduced by `scripts/run_all_checks.sh` |

## Not done / limits
- The owner's other attachments from the 2026-11-06 mission are not separately catalogued here beyond what lies in the archive.
- Streams SRC-13 were spot-checked, not independently re-derived.
- Prior-art coverage is a literature survey, not a patent search.
- None of the sources is peer reviewed.

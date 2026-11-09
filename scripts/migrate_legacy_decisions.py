#!/usr/bin/env python3
"""Next-work item 5: migrate remaining legacy D-xx decisions (research-archive-sliced into
docs/decisions/legacy-decision-record.md) into individual ADRs, following docs/decisions/ADR-
TEMPLATE.md, for every D-id not already referenced by an existing ADR's 'Legacy IDs' line.

Mechanical generation from the legacy table's own columns (Decision / Why / Alternatives), not
invented content: Context <- Why, Decision <- the Decision/Idea text, Alternatives <- Alternatives
considered. Status is set to Accepted (these are already-built, CARRIED/AMENDED decisions, not new
proposals) with a Consequences line noting it is a direct migration, not a new analysis.
Does not touch C-xx/X-xx/X-xx/J-xx (conditional/research/rejected) -- those are tracked as a single
index instead; see docs/decisions/README.md for why individual ADRs weren't written for ~80 of them.
"""
import re, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = os.path.join(ROOT, "docs", "decisions", "legacy-decision-record.md")
DECISIONS_DIR = os.path.join(ROOT, "docs", "decisions")

ROW_RE = re.compile(r"^\|\s*\*?\*?(D-\d+)\*?\*?\s*\|\s*(\w+(?:\s*\(\w+[^)]*\))?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", re.M)

def already_migrated():
    ids = set()
    for path in glob.glob(os.path.join(DECISIONS_DIR, "ADR-*.md")):
        text = open(path).read()
        m = re.search(r"\*\*Legacy IDs:\*\*\s*(?:Legacy:)?\s*(.*)", text)
        if m:
            ids |= set(re.findall(r"D-\d+", m.group(1)))
    return ids

def slug(text, maxwords=6):
    words = re.findall(r"[A-Za-z0-9]+", text.lower())[:maxwords]
    return "-".join(words)

def next_adr_number():
    nums = [int(re.search(r"ADR-(\d+)", os.path.basename(p)).group(1))
            for p in glob.glob(os.path.join(DECISIONS_DIR, "ADR-*.md"))
            if re.search(r"ADR-(\d+)-", os.path.basename(p))]
    return max(nums, default=0) + 1

def strip_md(s):
    return re.sub(r"\*\*|`", "", s).strip()

def main():
    text = open(LEGACY).read()
    # Only the DECIDED section (20.1) -- stop at 20.2
    section = text.split("### 20.2")[0]
    rows = ROW_RE.findall(section)
    migrated = already_migrated()
    n = next_adr_number()
    written = []
    for rid, status, decision, why, alts in rows:
        if rid in migrated:
            continue
        decision_c, why_c, alts_c = strip_md(decision), strip_md(why), strip_md(alts)
        title = slug(decision_c)
        fname = f"ADR-{n:03d}-{title}.md"
        path = os.path.join(DECISIONS_DIR, fname)
        heading = decision_c.split(";")[0].split(".")[0]
        if len(heading) > 80:
            heading = heading[:80].rsplit(" ", 1)[0]
        content = f"""# ADR-{n:03d}: {heading}

**Status:** Accepted
**Date:** 2026-11-09
**Legacy IDs:** Legacy: {rid}

## Context
{why_c if why_c and why_c != '—' else '(no reason recorded beyond the decision itself in the legacy record)'}

## Decision
{decision_c}

## Consequences
Direct migration of a legacy Rev 4 decision ({rid}, status {status.strip()} in the legacy record)
into ADR form; no new analysis was done in this migration. See `docs/decisions/legacy-decision-
record.md` for the original table row and `docs/theory/red-team-r2-findings.md` for any R2 finding
that may have since amended it.

## Alternatives considered
{alts_c if alts_c and alts_c != '—' else '(none recorded)'}
"""
        with open(path, "w") as f:
            f.write(content)
        written.append((rid, fname))
        n += 1
    return written

if __name__ == "__main__":
    written = main()
    print(f"Wrote {len(written)} ADRs:")
    for rid, fname in written:
        print(f"  {rid} -> {fname}")

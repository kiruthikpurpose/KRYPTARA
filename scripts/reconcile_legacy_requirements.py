#!/usr/bin/env python3
"""Next-work item 4: reconcile the 221 legacy FR-/NFR- requirements (research-archive/streams/
R_requirements.md) against the current kernel-only REQ- set (docs/specifications/requirements.md).

This is a MECHANICAL first pass, not a semantic review: it extracts every legacy FR-/NFR- row and
every current REQ- row, scores them by keyword overlap, and classifies each legacy item into one of
three buckets:
  - LIKELY-COVERED: decent keyword overlap with a current REQ- (needs a human to confirm the match
    is real, not just shared vocabulary).
  - OUT-OF-SCOPE-BY-PREFIX: the legacy area (update/migration/enclave/ownership/provisioning/
    governance/fleet/certification) is explicitly outside the kernel-only scope this repo's README
    and roadmap declare today ("What is verified today is one thing: a governed-change kernel...").
  - GAP-CANDIDATE: kernel-relevant topic (assumption/quorum/authority/time/lifecycle/signature/
    presence/key/record/halt area) with no matching current REQ- -- a genuine candidate for a new
    REQ- and ADR, for a human to triage.
Output: docs/research/legacy-requirements-reconciliation.md, machine-generated, regenerate with
`python3 scripts/reconcile_legacy_requirements.py`.
"""
import re, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = os.path.join(ROOT, "research-archive", "streams", "R_requirements.md")
CURRENT = os.path.join(ROOT, "docs", "specifications", "requirements.md")
OUT = os.path.join(ROOT, "docs", "research", "legacy-requirements-reconciliation.md")

ROW_RE = re.compile(r"^\|\s*((?:FR|NFR)-[A-Za-z0-9-]+)\s*\|\s*(.*?)\s*\|\s*([IPATD+]+)\s*\|\s*(MUST|SHOULD|MAY)\s*\|\s*(M[0-5])\s*\|", re.M)
REQ_RE = re.compile(r"^\|\s*(REQ-[A-Za-z0-9-]+)\s*\|\s*(.*?)\s*\|", re.M)

# Legacy area -> in-scope (kernel: evidence/admission/tiers/lifecycle/presence/record/effect) or
# out-of-scope-today (fleet orchestration, OTA update mechanics, migration ceremonies, enclaves,
# ownership transfer protocol, provisioning, governance institutions, certification process).
# This mapping is itself a judgment call, documented so a reviewer can disagree with a specific line
# rather than with an opaque score.
OUT_OF_SCOPE_PREFIXES = {
    "FR-UPD": "OTA update mechanics (staging, rollout) -- Phase 2 fleet feature, not the kernel",
    "FR-MIG": "cross-algorithm migration ceremonies -- Phase 2/4, not the kernel",
    "FR-ENC": "enclave profile / HA-1 variant -- a port profile, not the kernel itself",
    "FR-OWN": "ownership-transfer protocol mechanics -- uses the kernel's PRES/tier primitives but the protocol itself is a Phase 2 action, not a kernel requirement",
    "FR-PRO": "provisioning/enrolment mechanics -- Phase 2 (ac-enrol), not the kernel",
    "FR-GOV": "governance institution process (custody groups, escrow contracts) -- organisational, not a device/kernel requirement",
    "NFR-PORT": "port/toolchain portability -- a build-system property, not a kernel behaviour",
    "NFR-CERT": "certification process evidence (FIPS/IEC) -- Phase 3 audit evidence, not the kernel",
    "NFR-OPS": "fleet operations tooling -- Phase 2/3, not the kernel",
}

def norm_words(text):
    return set(w for w in re.findall(r"[a-z]{4,}", text.lower())
               if w not in {"shall", "must", "should", "every", "which", "that", "this", "with",
                             "from", "have", "been", "will", "than", "when", "where", "while"})

def main():
    legacy_text = open(LEGACY).read()
    current_text = open(CURRENT).read()
    legacy_rows = ROW_RE.findall(legacy_text)
    req_rows = [(rid, txt) for rid, txt in REQ_RE.findall(current_text) if rid != "REQ"]
    req_words = {rid: norm_words(txt) for rid, txt in req_rows}

    buckets = collections.defaultdict(list)
    for rid, text, verif, prio, ms in legacy_rows:
        prefix3 = "-".join(rid.split("-")[:2])
        if prefix3 in OUT_OF_SCOPE_PREFIXES:
            buckets["OUT-OF-SCOPE-BY-PREFIX"].append((rid, text, prio, ms, OUT_OF_SCOPE_PREFIXES[prefix3], None))
            continue
        lw = norm_words(text)
        best_id, best_score = None, 0
        for req_id, rw in req_words.items():
            overlap = len(lw & rw)
            if overlap > best_score:
                best_score, best_id = overlap, req_id
        if best_score >= 3:
            buckets["LIKELY-COVERED"].append((rid, text, prio, ms, best_id, best_score))
        else:
            buckets["GAP-CANDIDATE"].append((rid, text, prio, ms, None, best_score))

    with open(OUT, "w") as f:
        f.write("# Legacy requirements reconciliation (next-work item 4)\n\n")
        f.write("**Machine-generated** by `scripts/reconcile_legacy_requirements.py` -- a mechanical "
                "keyword-overlap first pass over all 221 `FR-`/`NFR-` rows in "
                "`research-archive/streams/R_requirements.md` against the 23 current `REQ-` rows in "
                "`docs/specifications/requirements.md`. This classifies, it does not verify: a "
                "LIKELY-COVERED match is a keyword-overlap score, not a confirmed semantic match, and "
                "every GAP-CANDIDATE still needs a human decision (new REQ-/ADR, explicit waiver, or "
                "recognise it as already out of scope for a reason this script's prefix table doesn't "
                "know about). Re-run after any change to either source file.\n\n")
        total = len(legacy_rows)
        f.write(f"**Totals:** {total} legacy requirements -- "
                f"{len(buckets['LIKELY-COVERED'])} likely covered, "
                f"{len(buckets['OUT-OF-SCOPE-BY-PREFIX'])} out of scope by area, "
                f"{len(buckets['GAP-CANDIDATE'])} gap candidates needing triage.\n\n")

        f.write("## Likely covered (keyword overlap >= 3 with a current REQ-)\n\n")
        f.write("| Legacy ID | Priority | Milestone | Best REQ- match | Overlap score | Legacy text |\n|---|---|---|---|---|---|\n")
        for rid, text, prio, ms, match, score in sorted(buckets["LIKELY-COVERED"]):
            f.write(f"| {rid} | {prio} | {ms} | {match} | {score} | {text[:140]}{'...' if len(text) > 140 else ''} |\n")

        f.write("\n## Out of scope today, by area (kernel-only scope per README/roadmap)\n\n")
        f.write("| Legacy ID | Priority | Milestone | Why out of scope | Legacy text |\n|---|---|---|---|---|\n")
        for rid, text, prio, ms, reason, _ in sorted(buckets["OUT-OF-SCOPE-BY-PREFIX"]):
            f.write(f"| {rid} | {prio} | {ms} | {reason} | {text[:140]}{'...' if len(text) > 140 else ''} |\n")

        f.write("\n## Gap candidates (kernel-relevant area, no current REQ- match) -- needs triage\n\n")
        f.write("| Legacy ID | Priority | Milestone | Best overlap score (below threshold) | Legacy text |\n|---|---|---|---|---|\n")
        for rid, text, prio, ms, _, score in sorted(buckets["GAP-CANDIDATE"]):
            f.write(f"| {rid} | {prio} | {ms} | {score} | {text[:160]}{'...' if len(text) > 160 else ''} |\n")

    print(f"Wrote {OUT}")
    print(f"Totals: {total} legacy FR-/NFR- rows -> "
          f"{len(buckets['LIKELY-COVERED'])} likely-covered, "
          f"{len(buckets['OUT-OF-SCOPE-BY-PREFIX'])} out-of-scope, "
          f"{len(buckets['GAP-CANDIDATE'])} gap-candidates")
    if total != 221:
        print(f"WARNING: expected 221 legacy rows per CLAUDE.md, found {total}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

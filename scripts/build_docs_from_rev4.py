#!/usr/bin/env python3
"""Slices the legacy Rev 4 monolith into per-topic documents. Run once; outputs are then maintained by hand.
Each slice gets a provenance banner and evidence-label legend. Known corrections are applied by CORRECTIONS."""
import re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
src = (R/"research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md").read_text().split("\n")
heads = [(i, l) for i, l in enumerate(src) if l.startswith("## ")]
def sec(n):
    for k, (i, l) in enumerate(heads):
        if re.match(rf"## {n}\.", l):
            j = heads[k+1][0] if k+1 < len(heads) else len(src)
            return src[i:j]
    raise KeyError(n)
def sub(n, m):  # subsection "### n.m"
    s = sec(n); out = []; on = False
    for l in s:
        if l.startswith("### "): on = l.startswith(f"### {n}.{m} ")
        if on: out += [l]
    return out
CORR = [("682 bytes", "682 bytes in Rev 4; 812 bytes after the red-team R2 hardening; 902 bytes with the projection function (arm-none-eabi-gcc -Os, Cortex-M0+, measured 2026-11-09; stack not re-measured)"),
        ("682 B", "682 B (Rev 4; now 902 B hardened, see CHANGELOG)")]
BANNER = ("> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).\n"
          "> Document level: {lvl}. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.\n"
          "> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.\n\n")
MAP = {
 "docs/executive-summary.md": ("Executive summary (Rev 4)", "L3", [sec(0)]),
 "docs/theory/mathematical-foundations.md": ("Mathematical foundations: the theory of governed change", "L2", [sec(3)]),
 "docs/architecture/primitives-and-waist.md": ("Four primitives and the frozen waist", "L2", [sec(4)]),
 "docs/architecture/system-architecture.md": ("System architecture", "L2", [sec(5)]),
 "docs/architecture/mechanisms.md": ("Mechanisms in depth", "L2", [sec(6)]),
 "docs/architecture/lifecycle.md": ("Lifecycle from manufacture to resurrection", "L3", [sec(7)]),
 "docs/specifications/interfaces-and-data-models.md": ("Interfaces and data models", "L2", [sec(8)]),
 "docs/specifications/resource-estimates.md": ("Resource estimates", "L3", [sec(9)]),
 "docs/research/problem-mapping.md": ("Problem analysis and problem-to-mechanism mapping", "L3", [sec(1), sec(10)]),
 "docs/research/comparison-and-reuse.md": ("Comparison with existing systems; what is reused and what is new", "L3", [sec(11), sec(12)]),
 "docs/implementation/implementation-strategy.md": ("Implementation strategy", "L3", [sec(13)]),
 "docs/implementation/roadmap.md": ("Roadmap, constraints and adoption path", "L3", [sec(15), sec(16)]),
 "docs/validation/falsification-programme.md": ("Falsification programme (EXP-xx)", "L2", [sec(14)]),
 "docs/theory/limitations-and-open-problems.md": ("Open questions, risks and limits", "L3", [sec(17), sec(18)]),
 "docs/applications/long-horizon.md": ("The long horizon", "L3", [sec(19)]),
 "docs/decisions/legacy-decision-record.md": ("Legacy decision record D/C/X/J (Rev 4)", "L2", [sec(20)]),
 "docs/research/reproducibility-and-sources.md": ("Reproducibility index and sources (Rev 4)", "L3", [sec(21)]),
 "docs/project-principles.md": ("Vision, principles, objectives, non-goals (Rev 4)", "L2", [sec(2)]),
}
for rel, (title, lvl, parts) in MAP.items():
    body = []
    for p in parts: body += p + [""]
    t = "\n".join(body)
    for a, b in CORR: t = t.replace(a, b)
    t = re.sub(r"^## ", "# ", t, count=1, flags=re.M)
    p = R/rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"<!-- Title: {title} -->\n" + BANNER.format(s=", ".join(h.split('.')[0].lstrip('# ') for h in [x[0] for x in parts] if False) or rel, lvl=lvl) + t)
print("wrote", len(MAP), "files")

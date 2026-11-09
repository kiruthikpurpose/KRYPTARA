#!/usr/bin/env python3
"""Documentation integrity audit: relative links, ADR files, ID references, index coverage, empty files."""
import re, pathlib, sys
R = pathlib.Path(__file__).resolve().parent.parent; D = R/"docs"; bad = []
docs = [p for p in R.rglob("*.md") if "research-archive" not in p.parts and "build" not in p.parts]
for p in docs:
    t = p.read_text()
    if not t.strip(): bad.append(f"empty {p}")
    for m in re.finditer(r"\]\(([^)#]+)\)", t):
        l = m.group(1)
        if "://" in l: continue
        if not (p.parent/l).exists(): bad.append(f"broken link {p.relative_to(R)} -> {l}")
index = (D/"index.md").read_text()
for p in D.rglob("*.md"):
    n = p.stem
    if p.name == "index.md" or n.startswith("ADR-0"): continue
    if n not in index: bad.append(f"not in index: {p.relative_to(R)}")
adr_ids = {re.match(r"ADR-(\d+)", p.name).group(1) for p in (D/"decisions").glob("ADR-0*")}
allt = "\n".join(p.read_text() for p in docs)
for m in set(re.findall(r"ADR-(\d{3})", allt)):
    if m not in adr_ids and m != "NNN": bad.append(f"ADR-{m} referenced, no file")
req_def = set(re.findall(r"^\| (REQ-[A-Z]+-\d+) \|", (D/"specifications/requirements.md").read_text(), re.M))
for m in set(re.findall(r"REQ-[A-Z]+-\d+", allt)):
    if m not in req_def: bad.append(f"{m} referenced, not defined")
clm_def = set(re.findall(r"^\| (CLM-\d+) \|", (D/"research/evidence-register.md").read_text(), re.M))
for m in set(re.findall(r"CLM-\d+", allt)):
    if m not in clm_def: bad.append(f"{m} referenced, not defined")
ids = re.findall(r"^\| (REQ-[A-Z]+-\d+) \|", (D/"specifications/requirements.md").read_text(), re.M)
if len(ids) != len(set(ids)): bad.append("duplicate REQ ids")
print("\n".join(bad) or "AUDIT PASSED"); print(len(docs), "markdown files checked"); sys.exit(1 if bad else 0)

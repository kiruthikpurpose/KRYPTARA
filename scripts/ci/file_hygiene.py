#!/usr/bin/env python3
"""File hygiene over git-tracked files (research-archive/ exempt from size and whitespace rules).

Rules: no trailing whitespace in src/ (C and headers) ; no tab characters in C/H files under src/ and
tests/ ; every tracked text file under src/ scripts/ models/ docs/ .github/ ends with a final newline ; no tracked file over 2 MB ; no merge-conflict markers ; no CRLF in source files.
"""
import os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAX = 2 * 1024 * 1024
C_EXT = (".c", ".h")
NL_DIRS = ("src/", "scripts/", "models/", "docs/", ".github/", "tests/", "simulations/")
NL_EXT = (".c", ".h", ".py", ".sh", ".md", ".yml", ".yaml", ".toml", ".tla", ".cfg", ".rs")
CONFLICT = re.compile(r"^(<<<<<<< |>>>>>>> |=======$)")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [f for f in out.decode().split("\0") if f and os.path.isfile(os.path.join(ROOT, f))]


def baseline():
    """Known, accepted violations: lines 'path:line: reason' in hygiene_baseline.txt (reported, not failing)."""
    p = os.path.join(os.path.dirname(__file__), "hygiene_baseline.txt")
    if not os.path.exists(p):
        return set()
    return {l.strip() for l in open(p) if l.strip() and not l.startswith("#")}


def main():
    bad = []
    for rel in tracked():
        p = os.path.join(ROOT, rel)
        archive = rel.startswith("research-archive/")
        size = os.path.getsize(p)
        if size > MAX and not archive:
            bad.append((rel, 0, "file is %.1f MB, limit 2 MB" % (size / 1048576)))
        if archive or size == 0:
            continue
        data = open(p, "rb").read()
        if b"\0" in data[:8192]:
            continue
        text = data.decode("utf-8", "replace")
        lines = text.split("\n")
        if rel.startswith(NL_DIRS) and rel.endswith(NL_EXT):
            if not text.endswith("\n"):
                bad.append((rel, len(lines), "missing final newline"))
        if rel.endswith(C_EXT + (".py", ".sh")) and "\r" in text:
            bad.append((rel, 0, "CRLF line endings"))
        for i, line in enumerate(lines, 1):
            if rel.startswith("src/") and rel.endswith(C_EXT) and not rel.startswith("src/prototypes/rust") \
                    and re.search(r"[ \t\r]+$", line):
                bad.append((rel, i, "trailing whitespace"))
            if rel.endswith(C_EXT) and rel.startswith(("src/", "tests/")) and "\t" in line:
                bad.append((rel, i, "tab character in C source"))
            if rel.endswith((".c", ".h", ".py", ".sh", ".md", ".yml", ".tla", ".cfg")) and CONFLICT.match(line) \
                    and not rel.endswith(".md"):
                bad.append((rel, i, "merge conflict marker"))
    known = baseline()
    waived = [b for b in bad if "%s:%s: %s" % (b[0], b[1] or "-", b[2]) in known]
    bad = [b for b in bad if b not in waived]
    for rel, ln, why in waived:
        print("baselined (not failing): %s:%s: %s" % (rel, ln or "-", why))
    for rel, ln, why in bad[:200]:
        print("%s:%s: %s" % (rel, ln or "-", why))
    if len(bad) > 200:
        print("... %d more" % (len(bad) - 200))
    print("file hygiene: %d problems" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

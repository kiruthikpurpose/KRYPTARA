#!/usr/bin/env python3
"""Line and branch coverage of src/*.c from the C test programs, with a threshold gate.

Builds each test with gcc --coverage, runs it, runs gcov --json-format, merges counts across
all test binaries (a line counts as covered if any test executed it), writes a text report and a
JSON summary, and exits 1 if a src/ file set total falls under the thresholds.

Scope: src/*.c and src/*.h excluding src/prototypes, src/legacy (not exercised by these tests).
Usage: python3 scripts/ci/coverage_gate.py [--out DIR] [--min-line PCT] [--min-branch PCT]
Thresholds are floors below the value measured on 2026-11-13 (see docs/architecture/ci-architecture.md);
raise them when coverage improves, never lower them to make a failing run pass.
"""
import argparse, glob, gzip, json, os, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TESTS = [("fuzz_policy8", []), ("step_test", ["self"]), ("kernel_test", ["self"]), ("test_projection", [])]
DEFAULT_MIN_LINE = 88.0
DEFAULT_MIN_BRANCH = 72.0


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("command failed: %s\n%s%s\n" % (" ".join(cmd), r.stdout, r.stderr))
        sys.exit(2)
    return r.stdout


def in_scope(path):
    rel = os.path.relpath(path, ROOT)
    return rel.startswith("src" + os.sep) and rel.endswith((".c", ".h")) and not rel.startswith(
        ("src/prototypes", "src/legacy"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "coverage"))
    ap.add_argument("--min-line", type=float, default=DEFAULT_MIN_LINE)
    ap.add_argument("--min-branch", type=float, default=DEFAULT_MIN_BRANCH)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    work = tempfile.mkdtemp(prefix="cov_", dir=a.out)

    lines = {}     # (file, line) -> count
    branches = {}  # (file, line, idx) -> count
    for name, args in TESTS:
        exe = os.path.join(work, name)
        run(["gcc", "-std=gnu99", "-O0", "-g", "--coverage", "-o", exe, "tests/%s.c" % name], ROOT)
        run([exe] + args, work)
        run(["gcov", "--json-format", "--branch-probabilities", "--branch-counts", name + ".gcda"], work)
        for jf in glob.glob(os.path.join(work, "*.gcov.json.gz")):
            with gzip.open(jf, "rt") as f:
                data = json.load(f)
            for fe in data["files"]:
                path = os.path.normpath(os.path.join(work, fe["file"])) if not os.path.isabs(fe["file"]) else fe["file"]
                if not in_scope(path):
                    path = os.path.normpath(os.path.join(ROOT, fe["file"]))
                if not in_scope(path):
                    continue
                rel = os.path.relpath(path, ROOT)
                for ln in fe["lines"]:
                    k = (rel, ln["line_number"])
                    lines[k] = lines.get(k, 0) + ln["count"]
                    for i, b in enumerate(ln.get("branches", [])):
                        bk = (rel, ln["line_number"], i)
                        branches[bk] = branches.get(bk, 0) + b["count"]
            os.remove(jf)

    if not lines:
        sys.stderr.write("no coverage data for src/ found\n")
        return 2

    files = sorted({k[0] for k in lines})
    rows, uncovered = [], []
    for f in files:
        l = [c for (ff, _), c in lines.items() if ff == f]
        b = [c for (ff, _, _), c in branches.items() if ff == f]
        rows.append((f, sum(1 for c in l if c), len(l), sum(1 for c in b if c), len(b)))
        uncovered.append((f, sorted(n for (ff, n), c in lines.items() if ff == f and c == 0)))
    tl, cl = sum(r[2] for r in rows), sum(r[1] for r in rows)
    tb, cb = sum(r[4] for r in rows), sum(r[3] for r in rows)
    pl = 100.0 * cl / tl if tl else 0.0
    pb = 100.0 * cb / tb if tb else 0.0

    out = ["%-24s %14s %16s" % ("file", "lines", "branches")]
    for f, c1, t1, c2, t2 in rows:
        out.append("%-24s %5d/%-5d %3.0f%% %6d/%-6d %3.0f%%" % (
            f, c1, t1, 100.0 * c1 / max(t1, 1), c2, t2, 100.0 * c2 / max(t2, 1)))
    out.append("%-24s %5d/%-5d %3.1f%% %5d/%-6d %3.1f%%" % ("TOTAL", cl, tl, pl, cb, tb, pb))
    out.append("")
    out.append("uncovered lines (merged over: %s)" % ", ".join(t[0] for t in TESTS))
    for f, ns in uncovered:
        out.append("  %s: %s" % (f, ",".join(map(str, ns)) or "none"))
    text = "\n".join(out)
    print(text)
    with open(os.path.join(a.out, "coverage.txt"), "w") as f:
        f.write(text + "\n")
    with open(os.path.join(a.out, "coverage.json"), "w") as f:
        json.dump({"line_percent": pl, "branch_percent": pb, "min_line": a.min_line, "min_branch": a.min_branch,
                   "files": {r[0]: {"lines": [r[1], r[2]], "branches": [r[3], r[4]]} for r in rows}}, f, indent=1)

    bad = []
    if pl < a.min_line:
        bad.append("line coverage %.1f%% < %.1f%%" % (pl, a.min_line))
    if pb < a.min_branch:
        bad.append("branch coverage %.1f%% < %.1f%%" % (pb, a.min_branch))
    for b in bad:
        print("FAIL: " + b)
    if bad:
        return 1
    print("coverage gate OK: lines %.1f%% (min %.1f), branches %.1f%% (min %.1f)" % (pl, a.min_line, pb, a.min_branch))
    return 0


if __name__ == "__main__":
    sys.exit(main())

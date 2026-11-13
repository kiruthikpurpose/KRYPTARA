#!/usr/bin/env python3
"""Commit-message hygiene: fail if any commit in a range has a Co-Authored-By trailer or the words
'Generated with'. Also flags an empty subject and a subject over 100 characters.

Usage: check_commits.py [--range A..B]   (default: origin/<GITHUB_BASE_REF>..HEAD in a PR,
       else origin/main..HEAD, else the last 20 commits)
"""
import argparse, os, re, subprocess, sys

BAD = [("Co-Authored-By trailer", re.compile(r"^\s*co-authored-by\s*:", re.I | re.M)),
       ("'Generated with' text", re.compile(r"generated with", re.I))]


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def default_range():
    base = os.environ.get("GITHUB_BASE_REF")
    for ref in ([("origin/" + base)] if base else []) + ["origin/main"]:
        if git("rev-parse", "--verify", "-q", ref).returncode == 0:
            return ref + "..HEAD"
    return "HEAD~20..HEAD" if git("rev-parse", "--verify", "-q", "HEAD~20").returncode == 0 else "HEAD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", dest="rng")
    rng = ap.parse_args().rng or default_range()
    r = git("log", "--format=%H%x1f%B%x1e", rng)
    if r.returncode != 0:
        print("git log failed for range %s: %s" % (rng, r.stderr.strip()))
        return 2
    bad = n = 0
    for rec in filter(None, (x.strip("\n") for x in r.stdout.split("\x1e"))):
        sha, _, msg = rec.partition("\x1f")
        n += 1
        subject = msg.strip().splitlines()[0] if msg.strip() else ""
        probs = [name for name, rx in BAD if rx.search(msg)]
        if not subject:
            probs.append("empty subject")
        if len(subject) > 100:
            probs.append("subject longer than 100 characters")
        for p in probs:
            print("%s: %s (%s)" % (sha[:10], p, subject[:60]))
            bad += 1
    print("commit check: range %s, %d commits, %d problems" % (rng, n, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

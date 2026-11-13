#!/usr/bin/env python3
"""Offline secret scan over git-tracked files (falls back to a directory walk outside git).

Looks for private key blocks, cloud and VCS tokens, and quoted high-entropy-looking assignments to
secret-named variables. research-archive/ is scanned too. Binary files
and test vectors named in ALLOW are skipped. A line containing 'secret-scan: allow' is ignored.
Exit 1 with file:line and rule name on any finding. The matched text is never printed in full.
"""
import os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RULES = [
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe-live-key", re.compile(r"\b[sr]k_live_[0-9A-Za-z]{20,}\b")),
    ("anthropic-or-openai-key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("url-with-password", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s:@]{4,}@[^/\s]+")),
    ("secret-assignment", re.compile(
        r"""(?i)\b(?:password|passwd|api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*["'][A-Za-z0-9/+_=-]{16,}["']""")),
]
SKIP_SUFFIX = (".png", ".jpg", ".gif", ".pdf", ".o", ".a", ".bin", ".gz", ".zip", ".jar")


def files():
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
        return [f for f in out.decode().split("\0") if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        res = []
        for d, dn, fn in os.walk(ROOT):
            dn[:] = [x for x in dn if x not in (".git", "build", "__pycache__")]
            res += [os.path.relpath(os.path.join(d, f), ROOT) for f in fn]
        return res


def main():
    hits = 0
    n = 0
    for rel in files():
        if rel.endswith(SKIP_SUFFIX) or not os.path.isfile(os.path.join(ROOT, rel)):
            continue
        try:
            text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        n += 1
        for i, line in enumerate(text.splitlines(), 1):
            if "secret-scan: allow" in line:
                continue
            for name, rx in RULES:
                if rx.search(line):
                    hits += 1
                    print("%s:%d: possible secret (%s)" % (rel, i, name))
    print("secret scan: %d files, %d findings" % (n, hits))
    if hits:
        print("If a finding is a test vector or example, append 'secret-scan: allow' to that line; otherwise rotate the secret.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

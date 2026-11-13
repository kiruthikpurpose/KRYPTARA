#!/usr/bin/env python3
"""Internal Markdown link checker: relative file links and #anchors across all tracked *.md.

Ignores research-archive/, external (http, mailto) links, and links inside fenced code blocks and
inline code. Anchors are checked against GitHub-style heading slugs of the target file.
Exit 1 listing file:line, the link and the reason.
"""
import os, re, subprocess, sys
from urllib.parse import unquote

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LINK = re.compile(r"(?<!!)\[(?:[^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)|!\[[^\]]*\]\(\s*<?([^)\s>]+)>?")
REFDEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)")
HEAD = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")


def md_files():
    try:
        out = subprocess.run(["git", "ls-files", "-z", "*.md"], cwd=ROOT, capture_output=True, check=True).stdout
        fs = [f for f in out.decode().split("\0") if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        fs = [os.path.relpath(os.path.join(d, f), ROOT) for d, _, fn in os.walk(ROOT) for f in fn if f.endswith(".md")]
    return [f for f in fs if not f.startswith("research-archive/") and os.path.exists(os.path.join(ROOT, f))]


def slug(h):
    h = re.sub(r"`|\*|_(?=\W|$)|(?<=\W)_", "", h)
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h, flags=re.UNICODE)
    return h.replace(" ", "-")


_cache = {}


def anchors(rel):
    if rel in _cache:
        return _cache[rel]
    seen, res, fence = {}, set(), False
    for line in open(os.path.join(ROOT, rel), encoding="utf-8").read().splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
            continue
        m = None if fence else HEAD.match(line)
        if m:
            s = slug(m.group(2))
            n = seen.get(s, 0)
            seen[s] = n + 1
            res.add(s if n == 0 else "%s-%d" % (s, n))
        for a in re.findall(r'<a\s+(?:name|id)="([^"]+)"', line):
            res.add(a)
    _cache[rel] = res
    return res


def main():
    bad = total = 0
    for rel in md_files():
        fence = False
        for ln, line in enumerate(open(os.path.join(ROOT, rel), encoding="utf-8").read().splitlines(), 1):
            if line.lstrip().startswith(("```", "~~~")):
                fence = not fence
                continue
            if fence:
                continue
            stripped = re.sub(r"`[^`]*`", "", line)
            targets = [m.group(1) or m.group(2) for m in LINK.finditer(stripped)]
            m = REFDEF.match(stripped)
            if m:
                targets.append(m.group(1))
            for t in targets:
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", t) or t.startswith("//"):
                    continue
                total += 1
                path, _, frag = t.partition("#")
                path = unquote(path)
                if path == "":
                    tgt = rel
                else:
                    tgt = os.path.normpath(os.path.join(os.path.dirname(rel), path)) if not path.startswith("/") else path.lstrip("/")
                full = os.path.join(ROOT, tgt)
                if not os.path.exists(full):
                    print("%s:%d: broken link %s (no such file: %s)" % (rel, ln, t, tgt))
                    bad += 1
                elif frag and tgt.endswith(".md") and os.path.isfile(full) and unquote(frag).lower() not in anchors(tgt):
                    print("%s:%d: broken anchor %s (no heading '%s' in %s)" % (rel, ln, t, frag, tgt))
                    bad += 1
    print("link check: %d internal links, %d broken" % (total, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

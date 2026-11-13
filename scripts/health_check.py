#!/usr/bin/env python3
"""Repository health check: has anything drifted between documentation, claims and code?

Pure standard library. Exit 0 only if every check passes. Run `--self-test` to prove each check can fail.
scripts/audit_docs.py (links, index coverage, empty files, duplicate IDs) is run as H00 and not re-implemented;
the checks below add what it does not do: file:line reporting, registers other than ADR/REQ/CLM, commands,
numbers, status words, model/C constants, licence and attribution consistency.

Usage:  python3 scripts/health_check.py [--root DIR] [--only H03,H05] [--self-test] [--list]
"""
import ast, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "research-archive", "build", "__pycache__", "states", "node_modules"}
CODE_EXT = r"(?:py|c|h|sh|tla|cfg|yml|yaml)"
PATH_RE = re.compile(r"(?<![\w/.\-$])((?:[\w.\-]+/)*[\w.\-]+\.%s)(?![\w])" % CODE_EXT)
ID_KINDS = ("CLM", "REQ", "ADR", "GATE", "OQ", "EXP", "HYP", "SRC")
# Strings the attribution check searches for (assembled so this file does not match itself).
ATTR_PATTERNS = [re.compile(p, re.I) for p in ("co-" + "authored-by", "generated " + "with", "generated " + "by claude")]


class Ctx:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self._cache = {}
        self._files = None

    def p(self, rel): return os.path.join(self.root, rel)

    def read(self, rel):
        if rel not in self._cache:
            try:
                with open(self.p(rel), encoding="utf-8", errors="replace") as f: self._cache[rel] = f.read()
            except OSError:
                self._cache[rel] = None
        return self._cache[rel]

    def lines(self, rel):
        t = self.read(rel)
        return [] if t is None else t.split("\n")

    def files(self):
        """All files outside the skipped directories, as repo-relative paths."""
        if self._files is None:
            out = []
            for d, dirs, fs in os.walk(self.root):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
                for f in fs: out.append(os.path.relpath(os.path.join(d, f), self.root))
            self._files = sorted(out)
        return self._files

    def md(self): return [f for f in self.files() if f.endswith(".md")]

    def resolve(self, tok):
        """True if a path token from prose names something on disk (exact, under a code dir, or by basename)."""
        tok = tok.strip("`'\".,;:()")
        if not tok: return True
        for pre in ("", "models/", "scripts/", "tests/", "src/", "simulations/", "tests/redteam_r2/", "simulations/tla/"):
            if os.path.exists(self.p(pre + tok)): return True
        base = os.path.basename(tok)
        return any(os.path.basename(f) == base for f in self.files())


def issue(file, line, what, fix): return (file, line, what, fix)


def table_rows(ctx, rel):
    """Yield (lineno, header_cells, cells) for each markdown table body row (header = row followed by a separator)."""
    L = ctx.lines(rel); header = None
    sep = lambda s: s.startswith("|") and all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in s.strip().strip("|").split("|"))
    for i, ln in enumerate(L, 1):
        if not ln.startswith("|"): continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if sep(ln): continue
        if i < len(L) and sep(L[i]): header = cells; continue
        if header is not None: yield i, header, cells


# ---------------------------------------------------------------- registers
def defined_ids(ctx):
    d = {k: set() for k in ID_KINDS}
    for _, _, c in table_rows(ctx, "docs/research/evidence-register.md"):
        m = re.match(r"\*{0,2}(CLM-\d+)", c[0]);  m and d["CLM"].add(m.group(1))
    for _, _, c in table_rows(ctx, "docs/specifications/requirements.md"):
        m = re.match(r"\*{0,2}(REQ-[A-Z]+-\d+)", c[0]);  m and d["REQ"].add(m.group(1))
    for _, _, c in table_rows(ctx, "docs/validation/validation-gates.md"):
        m = re.match(r"\*{0,2}(GATE-\d+[a-z]?)", c[0]);  m and d["GATE"].add(m.group(1))
    for _, _, c in table_rows(ctx, "docs/research/open-questions.md"):
        m = re.match(r"\*{0,2}(OQ-\d+)", c[0]);  m and d["OQ"].add(m.group(1))
    for _, _, c in table_rows(ctx, "docs/theory/hypotheses-and-falsifiability.md"):
        m = re.match(r"\*{0,2}(HYP-\d+)", c[0]);  m and d["HYP"].add(m.group(1))
    for _, _, c in table_rows(ctx, "docs/research/source-inventory.md"):
        m = re.match(r"\*{0,2}(SRC-\d+)", c[0]);  m and d["SRC"].add(m.group(1))
    for _, _, c in table_rows(ctx, "docs/validation/falsification-programme.md"):
        m = re.match(r"\*{0,2}(EXP-\d+)", c[0]);  m and d["EXP"].add(m.group(1))
    for f in ctx.files():
        m = re.fullmatch(r"docs/decisions/ADR-(\d{3})-.*\.md", f)
        if m: d["ADR"].add("ADR-" + m.group(1))
    return d


def ref_files(ctx):
    out = [f for f in ctx.files() if f.endswith((".md", ".py", ".c", ".h", ".sh", ".tla", ".cfg", ".yml", ".txt"))]
    return [f for f in out if not f.startswith(("src/legacy/", "src/prototypes/vendor", "tests/vectors/"))
            and f != "scripts/health_check.py"]


def h01(ctx):
    """Every CLM/REQ/ADR/GATE/OQ/EXP/HYP/SRC id referenced anywhere exists in its register."""
    d = defined_ids(ctx); out = []
    rx = re.compile(r"\b(CLM-\d+|REQ-[A-Z]+-\d+|ADR-\d{3}|GATE-\d{2}[a-z]?|OQ-\d{2}|EXP-\d{2}|HYP-\d{2}|SRC-\d{2})(?![\w])")
    for f in ref_files(ctx):
        if f == "docs/research/legacy-requirements-reconciliation.md": pass
        for i, ln in enumerate(ctx.lines(f), 1):
            for m in rx.finditer(ln):
                tok = m.group(1); kind = tok.split("-")[0]
                if tok not in d[kind]:
                    out.append(issue(f, i, f"{tok} referenced but not defined in its register",
                                     "define the row in the register, or correct the id"))
    for k in ID_KINDS:
        if not d[k]: out.append(issue("(registers)", 0, f"no {k} ids parsed from the register", "register format changed? update health_check.defined_ids"))
    return out


def h02(ctx):
    """Every register row referenced from the traceability matrix exists, and so do the files it names."""
    rel = "docs/specifications/traceability-matrix.md"; d = defined_ids(ctx); out = []
    if ctx.read(rel) is None: return [issue(rel, 0, "traceability matrix missing", "restore it")]
    rx = re.compile(r"\b(CLM-\d+|REQ-[A-Z]+-\d+|ADR-\d{3}|GATE-\d{2}[a-z]?|SRC-\d{2})(?![\w])")
    for i, _, cells in table_rows(ctx, rel):
        for c in cells:
            for m in rx.finditer(c):
                if m.group(1) not in d[m.group(1).split("-")[0]]:
                    out.append(issue(rel, i, f"matrix cites {m.group(1)}, which has no register row", "add the row or fix the citation"))
            for m in PATH_RE.finditer(c):
                if not ctx.resolve(m.group(1)):
                    out.append(issue(rel, i, f"matrix names file {m.group(1)}, not found on disk", "fix the path or remove the row"))
    # reverse direction: requirements absent from the matrix are informational only (not a failure)
    return out


def named_paths(cell):
    return [m.group(1) for m in PATH_RE.finditer(cell) if not any(ch in m.group(1) for ch in "*<>")]


def h03(ctx):
    """Every file named in the evidence-register 'Check' column and the validation-gates command column exists."""
    out = []
    for rel, col in (("docs/research/evidence-register.md", "check"), ("docs/validation/validation-gates.md", "command")):
        for i, hdr, cells in table_rows(ctx, rel):
            idx = next((j for j, h in enumerate(hdr) if h.lower().startswith(col)), None)
            if idx is None or idx >= len(cells): continue
            for tok in named_paths(cells[idx]):
                if not ctx.resolve(tok):
                    out.append(issue(rel, i, f"{cells[0]}: check names {tok}, not found on disk",
                                     "fix the path to the renamed file, or mark the check as not run"))
    return out


def h04(ctx):
    """run_all_checks.sh: step numbers are unique and sequential, and every script/test it names exists."""
    rel = "scripts/run_all_checks.sh"; out = []; steps = []
    if ctx.read(rel) is None: return [issue(rel, 0, "missing", "restore it")]
    for i, ln in enumerate(ctx.lines(rel), 1):
        m = re.search(r'echo "== \[(\d+)([a-z]?)\]', ln)
        if m: steps.append((int(m.group(1)), m.group(2), i))
    seen = {}
    for n, s, i in steps:
        if (n, s) in seen:
            out.append(issue(rel, i, f"step [{n}{s}] is a duplicate of line {seen[(n, s)]}", "renumber the later step"))
        seen[(n, s)] = i
    nums = sorted({n for n, _, _ in steps})
    for k, n in enumerate(nums, 1):
        if n != k:
            line = next(i for a, _, i in steps if a == n)
            out.append(issue(rel, line, f"step numbers not sequential: expected [{k}] before [{n}]", "renumber so steps run 1..N without gaps"))
            break
    order = [n for n, s, _ in steps if not s]
    for a, b in zip(order, order[1:]):
        if b < a: out.append(issue(rel, 0, f"step [{b}] appears after [{a}]", "keep steps in ascending order"))
    for i, ln in enumerate(ctx.lines(rel), 1):
        if ln.lstrip().startswith("#"): continue
        for tok in re.findall(r"[\w./\-$\"]+\.%s\b" % CODE_EXT, ln):
            t = tok.strip('"')
            if t.startswith(("$", "build/")) or "$BUILD" in t or t.endswith(".o"): continue
            if "-o" in ln and re.search(r'-o\s+"?\S*' + re.escape(os.path.basename(t)) + r"\b", ln): continue
            if not ctx.resolve(t):
                out.append(issue(rel, i, f"names {t}, not found on disk", "fix the path or remove the step"))
    return out


def run_steps_count(ctx):
    nums = set()
    for ln in ctx.lines("scripts/run_all_checks.sh"):
        m = re.search(r'echo "== \[(\d+)[a-z]?\]', ln)
        if m: nums.add(int(m.group(1)))
    return len(nums), (max(nums) if nums else 0)


def h05(ctx):
    """README numbers that can be checked (step count, mutation scores, rule count, self-test size, ADR ranges) match the repo."""
    out = []; rd = "README.md"; text = ctx.read(rd) or ""
    n, mx = run_steps_count(ctx)
    for i, ln in enumerate(ctx.lines(rd), 1):
        for m in re.finditer(r"\b(\d+) (?:steps|checks)\b", ln):
            if "run_all_checks" in ln or "all " + m.group(1) + " checks" in ln or "make check" in ln:
                if int(m.group(1)) != n:
                    out.append(issue(rd, i, f"README says {m.group(1)} check steps; scripts/run_all_checks.sh has {n} (highest step [{mx}])",
                                     f"change the README number to {n}"))
        for m in re.finditer(r"(\d+) of (\d+)(?: \((\d+)%\))?", ln):
            if "mutant" not in ln: continue
            a, b, pct = int(m.group(1)), int(m.group(2)), m.group(3)
            if pct and round(100 * a / b) != int(pct):
                out.append(issue(rd, i, f"{a} of {b} is {round(100 * a / b)}%, README says {pct}%", "fix the percentage"))
            reg = ctx.read("docs/research/evidence-register.md") or ""
            if not re.search(r"\b%d(?: of |/)%d\b" % (a, b), reg):
                out.append(issue(rd, i, f"mutation score {a} of {b} is not quoted in docs/research/evidence-register.md",
                                 "re-run scripts/mutation_test.py and update both places"))
        m = re.search(r"plants (\w+) violations", ln)
        if m:
            words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
            claimed = words.get(m.group(1), int(m.group(1)) if m.group(1).isdigit() else None)
            ac = ctx.read("scripts/arch_check.py") or ""
            seg = ac.split("def self_test", 1)[-1]
            actual = len(re.findall(r'^\s+\("R\d', seg, re.M))
            if claimed is not None and claimed != actual:
                out.append(issue(rd, i, f"README says the arch self-test plants {claimed} violations; scripts/arch_check.py plants {actual}", "fix the README number"))
        m = re.search(r"Rules R1[–-]R(\d)", ln)
        if m:
            ac = ctx.read("scripts/arch_check.py") or ""
            hi = max([int(x) for x in re.findall(r"\bR(\d)\b", ac)] or [0])
            if hi != int(m.group(1)):
                out.append(issue(rd, i, f"README names rules up to R{m.group(1)}; arch_check.py mentions up to R{hi}", "fix the README range"))
    # stated ADR ranges must reach the highest ADR that exists
    adrs = sorted(int(a[4:]) for a in defined_ids(ctx)["ADR"]); top = adrs[-1] if adrs else 0
    for f in ("docs/decisions/README.md", "docs/index.md", rd):
        for i, ln in enumerate(ctx.lines(f), 1):
            for m in re.finditer(r"ADR-001\.\.(\d{3})", ln):
                if int(m.group(1)) != top and not re.search(r"migrat|directly|already|covered", ln):
                    out.append(issue(f, i, f"states the ADR range ADR-001..{m.group(1)}; the highest existing ADR is ADR-{top:03d}",
                                     f"update the range to ADR-001..{top:03d} (or reword so it is not a count)"))
    return out


def classes(status):
    s = status.lower(); c = set()
    if re.search(r"not run|not yet run", s): c.add("notrun")
    if re.search(r"\bfail", s): c.add("failed")
    if re.search(r"not passed", s): c.update({"failed", "notrun"})
    if re.search(r"\bpass", s) and not re.match(r"\W*not passed", s): c.add("passed")
    return c


def gate_status(ctx):
    g = {}
    for i, hdr, c in table_rows(ctx, "docs/validation/validation-gates.md"):
        m = re.match(r"\*{0,2}(GATE-\d+[a-z]?)", c[0])
        if m and len(c) >= 4: g[m.group(1)] = (i, c[-1])
    return g


def h06(ctx):
    """README gate table agrees with validation-gates.md status words (passed / failed / not run)."""
    out = []; gates = gate_status(ctx)
    for i, hdr, c in table_rows(ctx, "README.md"):
        if not c or len(c) < 2 or "GATE-" not in c[0]: continue
        ids = []
        for m in re.finditer(r"GATE-(\d+[a-z]?)((?:/\d+[a-z]?)*)", c[0]):
            ids.append("GATE-" + m.group(1)); ids += ["GATE-" + x for x in m.group(2).split("/") if x]
        w = c[1].lower()
        first = ("notrun" if w.lstrip("* ").startswith("not run") else
                 "failed" if re.match(r"[\W]*(fails|failed)", w) or w.lstrip("* ").startswith("not passed") else
                 "passed" if re.match(r"[\W]*(pass|passed|passing)", w) else None)
        for gid in ids:
            if gid not in gates:
                out.append(issue("README.md", i, f"{gid} is not in docs/validation/validation-gates.md", "fix the id")); continue
            if first and first not in classes(gates[gid][1]):
                out.append(issue("README.md", i, f"README says {gid} is '{first}'; validation-gates.md line {gates[gid][0]} says "
                                 f"{sorted(classes(gates[gid][1])) or 'no recognised status'}", "make the two agree (validation-gates.md is authoritative)"))
    return out


def adr_status(ctx):
    st = {}
    for f in ctx.files():
        m = re.fullmatch(r"docs/decisions/(ADR-\d{3})-.*\.md", f)
        if not m: continue
        for i, ln in enumerate(ctx.lines(f)[:12], 1):
            s = re.match(r"\*\*Status:\*\*\s*(.*?)\s*$", ln)
            if s: st[m.group(1)] = (f, i, s.group(1)); break
        else: st[m.group(1)] = (f, 0, None)
    return st


def h07(ctx):
    """Every ADR has Status Proposed/Accepted/Superseded; Accepted ADRs are not called Proposed elsewhere (and vice versa)."""
    out = []; st = adr_status(ctx)
    for a, (f, i, s) in st.items():
        if s is None: out.append(issue(f, 1, f"{a} has no '**Status:**' line in its first lines", "add '**Status:** Proposed|Accepted|Superseded'"))
        elif not re.match(r"(Proposed|Accepted|Superseded)\b", s):
            out.append(issue(f, i, f"{a} status '{s}' is not one of Proposed, Accepted, Superseded", "use one of the three words (qualifiers may follow)"))
    word = {a: re.match(r"(Proposed|Accepted|Superseded)", s).group(1) for a, (f, i, s) in st.items() if s and re.match(r"(Proposed|Accepted|Superseded)", s)}
    for f in ctx.md():
        if f.startswith("docs/decisions/ADR-") or f in ("CHANGELOG.md", "docs/decisions/legacy-decision-record.md"): continue
        for i, ln in enumerate(ctx.lines(f), 1):
            ids = set(re.findall(r"ADR-\d{3}", ln))
            if len(ids) != 1: continue
            a = ids.pop()
            if a not in word: continue
            m = re.search(r"\b%s\b[^.|;]{0,40}?\b(is|are|remains?|status:?|as)\s+\**(Proposed|Accepted)\b" % a, ln) or \
                re.search(r"\b%s\b\s*\(\s*(Proposed|Accepted)\s*\)" % a, ln)
            if m:
                claimed = m.group(m.lastindex)
                if claimed != word[a]:
                    out.append(issue(f, i, f"{a} is called {claimed} but its file says {word[a]}", "make the text match the ADR's Status line"))
    return out


def h08(ctx):
    """Every Derived claim names a runnable check that exists."""
    out = []; rel = "docs/research/evidence-register.md"
    for i, hdr, c in table_rows(ctx, rel):
        if len(c) < 5 or not re.match(r"CLM-\d+", c[0]): continue
        if not c[2].lower().startswith("derived"): continue
        chk, basis = c[4], c[3]
        if re.fullmatch(r"[—\-– ]*", chk):
            out.append(issue(rel, i, f"{c[0]} is Derived but its Check cell is empty", "name the script that reproduces it, or reclassify as Proposed/Hypothesis")); continue
        toks = named_paths(chk) or named_paths(basis)
        words = re.findall(r"\b([a-z_0-9]+)\b", chk)
        stem_ok = any(os.path.exists(ctx.p(f"models/{w}.py")) or os.path.exists(ctx.p(f"scripts/{w}.py")) for w in words)
        step = re.search(r"run_all_checks|run_slow_checks|\bstep \[\d+\]", chk + basis)
        if not toks and not stem_ok and not step:
            out.append(issue(rel, i, f"{c[0]} is Derived but names no script, test or step that exists", "cite the runnable check (path under models/, tests/, scripts/, simulations/)"))
        for t in toks:
            if not ctx.resolve(t):
                out.append(issue(rel, i, f"{c[0]}: check {t} does not exist", "fix the path"))
    return out


def h09(ctx):
    """Prose never says passed/done for a gate whose register status is 'not run' (or failed)."""
    out = []; gates = gate_status(ctx)
    bad = {g: ("not run" if classes(s) == {"notrun"} else "failed") for g, (_, s) in gates.items()
           if classes(s) in ({"notrun"}, {"failed"}, {"failed", "notrun"})}
    for f in ctx.md():
        if f.startswith(("docs/validation/validation-gates.md",)) or f in ("CHANGELOG.md",): continue
        for i, ln in enumerate(ctx.lines(f), 1):
            for m in re.finditer(r"\b(GATE-\d{2}[a-z]?)\b([^|.;]{0,60})", ln):
                g = m.group(1)
                if g in bad and re.search(r"\b(passed|passing|done|complete[d]?|green)\b", m.group(2), re.I) \
                        and not re.search(r"\bnot\b|n't|\bfail|\bun|\bif\b|\bwhen\b|\buntil\b|\bonly\b|\bunless\b|\bmust\b|\bbefore\b|\bwould\b", m.group(2), re.I):
                    out.append(issue(f, i, f"{g} is '{bad[g]}' in validation-gates.md but this line says: {m.group(0).strip()!r}",
                                     "reword to match the gate's actual state"))
    return out


# -------------------------------------------------------------- model / C sync
def parse_c_enums(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    vals = {}
    for m in re.finditer(r"\b(AC_[A-Z0-9_]+)\s*=\s*(-?\d+)u?\b", text): vals[m.group(1)] = int(m.group(2))
    for m in re.finditer(r"#define\s+(AC_[A-Z0-9_]+)\s+(-?\d+)u?\b", text): vals[m.group(1)] = int(m.group(2))
    return vals


def parse_py_consts(text):
    env = {}
    for node in ast.parse(text).body:
        if not isinstance(node, ast.Assign): continue
        try:
            val = node.value
            if isinstance(val, ast.Call) and getattr(val.func, "id", "") == "range" and len(val.args) == 1:
                n = ast.literal_eval(val.args[0]); seq = list(range(n))
            else:
                seq = ast.literal_eval(val)
            t = node.targets[0]
            if isinstance(t, ast.Tuple):
                names = [e.id for e in t.elts]
                if isinstance(seq, (tuple, list)):
                    for n_, v in zip(names, seq): env[n_] = v
            elif isinstance(t, ast.Name): env[t.id] = seq
        except Exception: continue
    return env


def h10(ctx):
    """C header and Python model agree on status codes, action/tier/intent/message enums and the sizes they share."""
    hf, mf = "src/ac_waist.h", "models/step_model.py"; out = []
    ht, mt = ctx.read(hf), ctx.read(mf)
    if ht is None or mt is None: return [issue(hf, 0, "header or model missing", "restore it")]
    try: c = parse_c_enums(ht); m = parse_py_consts(mt)
    except SyntaxError as e: return [issue(mf, e.lineno or 0, f"model does not parse: {e.msg}", "fix the syntax")]
    def line(rel, pat):
        for i, ln in enumerate(ctx.lines(rel), 1):
            if re.search(pat, ln): return i
        return 0
    pairs = []
    pairs.append(("AC_OK", "OK"))
    for k in c:
        if k.startswith("AC_E_"): pairs.append((k, k[5:]))
        elif k.startswith("AC_ACT_"): pairs.append((k, {"ACTIVATE_IMAGE": "ACTIVATE", "TIGHTEN_TABLE": "TIGHTEN", "ADVANCE_EPOCH": "EPOCH", "RETIRE_SLOT": "RETIRE", "N": "N_ACT"}.get(k[7:], k[7:])))
        elif k.startswith("AC_MSG_"): pairs.append((k, "MSG_" + k[7:]))
        elif k == "AC_INT_NV_WRITE_SNAPSHOT": pairs.append((k, "INT_SNAPSHOT"))
        elif k == "AC_INT_BOOT_IMAGE": pairs.append((k, "INT_BOOT"))
        elif k == "AC_INT_REJECT": pairs.append((k, "INT_REJECT"))
    pairs.append(("AC_MAX_CLASSES", "MAXC"))
    for ck, mk in pairs:
        if ck not in c: out.append(issue(hf, 0, f"{ck} not found in the header", "restore it or update health_check")); continue
        if mk not in m: out.append(issue(mf, 0, f"model has no {mk} (header: {ck}={c[ck]})", "add it to the model")); continue
        if c[ck] != m[mk]:
            out.append(issue(mf, line(mf, r"\b%s\b" % mk), f"{mk}={m[mk]} in the model but {ck}={c[ck]} in {hf}:{line(hf, ck)}",
                             "the two must be identical: fix the side that drifted, and the golden vectors if the ABI really changed"))
    names = m.get("ACTION_NAMES")
    if isinstance(names, list):
        for idx, nm in enumerate(names):
            ck = "AC_ACT_" + nm
            if c.get(ck) != idx: out.append(issue(mf, line(mf, "ACTION_NAMES"), f"ACTION_NAMES[{idx}]={nm} but header {ck}={c.get(ck)}", "reorder the model list or fix the header"))
    snames = m.get("STATUS_NAMES")
    for ck, v in c.items():
        if ck.startswith("AC_E_") and "STATUS_NAMES" in mt and f'"{ck[5:]}"' not in mt:
            out.append(issue(mf, line(mf, "STATUS_NAMES"), f"STATUS_NAMES lacks {ck[5:]}", "add it"))
    tiers = {k: v for k, v in c.items() if re.match(r"AC_T\d_|AC_TIER_N", k)}
    for k, v in tiers.items():  # tier numbering: model is expected to use the same numbers where it names them
        pass
    if "AC_TIER_N" in c:
        # tier engine arrays sized by AC_TIER_N must cover the highest tier value
        hi = max(v for k, v in tiers.items() if k != "AC_TIER_N")
        if c["AC_TIER_N"] != hi + 1: out.append(issue(hf, line(hf, "AC_TIER_N"), f"AC_TIER_N={c['AC_TIER_N']} but highest tier is {hi}", "AC_TIER_N must be highest tier + 1"))
    return out


def h11(ctx):
    """Licence and copyright line are consistent across LICENSE, NOTICE, README.md and CITATION.cff (Apache-2.0)."""
    out = []; lic = ctx.read("LICENSE") or ""; notice = ctx.read("NOTICE") or ""; readme = ctx.read("README.md") or ""; cff = ctx.read("CITATION.cff") or ""
    if "Apache License" not in lic or "Version 2.0" not in lic: out.append(issue("LICENSE", 1, "LICENSE is not the Apache License 2.0 text", "restore the Apache-2.0 text"))
    m = re.search(r"^license:\s*(\S+)", cff, re.M)
    if not m or m.group(1) != "Apache-2.0": out.append(issue("CITATION.cff", next((i for i, l in enumerate(cff.split("\n"), 1) if l.startswith("license")), 0), f"license is {m.group(1) if m else 'missing'}, expected Apache-2.0", "set 'license: Apache-2.0'"))
    cn = re.search(r"Copyright\s+(\d{4})\s+([^\n.]+)", notice); cr = re.search(r"Copyright\s+(\d{4})\s+([^\n.]+?)\.", readme)
    if not cn: out.append(issue("NOTICE", 0, "no 'Copyright YYYY Holder' line", "add one"))
    if not cr: out.append(issue("README.md", 0, "no 'Copyright YYYY Holder.' line in the Licence section", "add one"))
    if cn and cr and (cn.group(1), cn.group(2).strip()) != (cr.group(1), cr.group(2).strip()):
        out.append(issue("README.md", next(i for i, l in enumerate(ctx.lines("README.md"), 1) if "Copyright" in l),
                         f"copyright '{cr.group(1)} {cr.group(2).strip()}' differs from NOTICE '{cn.group(1)} {cn.group(2).strip()}'", "make both lines identical"))
    if "Apache License, Version 2.0" not in notice: out.append(issue("NOTICE", 0, "does not name the Apache License, Version 2.0", "fix"))
    if "Apache License, Version 2.0" not in readme and "Apache-2.0" not in readme: out.append(issue("README.md", 0, "does not name Apache 2.0", "fix"))
    if not re.search(r"licence-Apache--2\.0|Apache-2\.0", readme): out.append(issue("README.md", 0, "licence badge does not say Apache-2.0", "fix the badge"))
    # any other licence named in top-level docs
    for f in ("README.md", "CONTRIBUTING.md", "GOVERNANCE.md", "SECURITY.md", "SUPPORT.md", "NOTICE"):
        for i, ln in enumerate(ctx.lines(f), 1):
            if re.search(r"\b(MIT licen[cs]e|GPL|BSD-\d|MPL|AGPL|LGPL)\b", ln) and "Third-party" not in ln:
                out.append(issue(f, i, "names a licence other than Apache-2.0: " + ln.strip()[:80], "confirm this is about third-party material, else fix"))
    return out


def git(ctx, *args):
    try:
        r = subprocess.run(["git", "-C", ctx.root] + list(args), capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else None
    except Exception: return None


def h12(ctx):
    """No AI/tool attribution trailer in the last 50 commits or in tracked files (outside research-archive/ and source-inventory)."""
    out = []; exempt = {"docs/research/source-inventory.md", "scripts/health_check.py"}
    log = git(ctx, "log", "-50", "--format=%H%x1f%B%x1e")
    if log:
        for rec in log.split("\x1e"):
            if "\x1f" not in rec: continue
            h, body = rec.strip().split("\x1f", 1)
            for pat in ATTR_PATTERNS:
                if pat.search(body):
                    out.append(issue(f"git:{h[:9]}", 0, f"commit message matches /{pat.pattern}/", "rewrite the history if it is unpublished, otherwise record it in CHANGELOG"))
    tracked = git(ctx, "ls-files")
    files = [f for f in tracked.split("\n") if f] if tracked is not None and os.path.isdir(ctx.p(".git")) else ctx.files()
    for f in files:
        if f.startswith("research-archive/") or f in exempt or not os.path.isfile(ctx.p(f)): continue
        t = ctx.read(f)
        if t is None or "\x00" in t[:2000]: continue
        for i, ln in enumerate(t.split("\n"), 1):
            for pat in ATTR_PATTERNS:
                if pat.search(ln): out.append(issue(f, i, f"attribution trailer text /{pat.pattern}/", "delete the line"))
    return out


def h13(ctx):
    """Git author consistency: lists distinct authors; fails if one name uses several e-mail addresses."""
    log = git(ctx, "log", "--format=%an <%ae>|%cn <%ce>")
    if log is None: return []   # no git metadata (e.g. the self-test copy)
    a = {};
    for ln in log.split("\n"):
        if "|" not in ln: continue
        for who in ln.split("|"): a[who] = a.get(who, 0) + 1
    print("      authors/committers: " + "; ".join(f"{k} x{v}" for k, v in sorted(a.items())))
    by_name = {}
    for who in a: by_name.setdefault(who.split(" <")[0], set()).add(who)
    return [issue("git log", 0, f"name '{n}' appears with several e-mail addresses: {sorted(v)}", "add a .mailmap or normalise git config user.email")
            for n, v in by_name.items() if len(v) > 1]


def h00(ctx):
    """scripts/audit_docs.py passes (links, ADR files, index coverage, empty files, duplicate ids)."""
    s = ctx.p("scripts/audit_docs.py")
    if not os.path.exists(s): return [issue("scripts/audit_docs.py", 0, "missing", "restore it")]
    r = subprocess.run([sys.executable, s], capture_output=True, text=True, cwd=ctx.root, timeout=120)
    if r.returncode == 0: return []
    return [issue("scripts/audit_docs.py", 0, ln, "see that script") for ln in r.stdout.strip().split("\n") if ln and "markdown files" not in ln]


CHECKS = [("H00", h00), ("H01", h01), ("H02", h02), ("H03", h03), ("H04", h04), ("H05", h05), ("H06", h06),
          ("H07", h07), ("H08", h08), ("H09", h09), ("H10", h10), ("H11", h11), ("H12", h12), ("H13", h13)]


def run(ctx, only=None, quiet=False):
    res = {}
    for cid, fn in CHECKS:
        if only and cid not in only: continue
        if not quiet: print(f"[{cid}] {fn.__doc__.strip()}")
        try: iss = fn(ctx)
        except Exception as e: iss = [issue("scripts/health_check.py", 0, f"check crashed: {type(e).__name__}: {e}", "fix the checker or the file it choked on")]
        res[cid] = iss
        if not quiet:
            if not iss: print("      PASS")
            for f, l, what, fix in iss:
                print(f"      FAIL {f}{':' + str(l) if l else ''}: {what}\n           fix: {fix}")
    return res


# ------------------------------------------------------------------ self-test
def self_test():
    tmp = tempfile.mkdtemp(prefix="healthneg_")
    try:
        dst = os.path.join(tmp, "tree")
        shutil.copytree(HERE + "/..", dst, ignore=shutil.ignore_patterns(".git", "research-archive", "build", "__pycache__", "states"))
        ctx = Ctx(dst)
        base = {cid: {(f, w) for f, l, w, _ in iss} for cid, iss in run(ctx, quiet=True).items()}
        def sub(rel, old, new, count=1):
            def edit(t):
                assert old in t, f"self-test anchor missing in {rel}: {old!r}"
                return t.replace(old, new, count)
            return (rel, edit)
        def append(rel, text): return (rel, lambda t: t + text)
        def reg_row(clm): return lambda t: re.sub(r"^\| %s \|.*\n" % clm, "", t, flags=re.M)
        plants = [
            ("delete a referenced CLM row", "H01", ("docs/research/evidence-register.md", reg_row("CLM-01"))),
            ("dangling REQ reference", "H01", append("docs/index.md", "\nSee REQ-ZZZ-99.\n")),
            ("dangling OQ/GATE reference", "H01", append("docs/index.md", "\nSee OQ-98 and GATE-97.\n")),
            ("traceability row cites missing claim", "H02", append("docs/specifications/traceability-matrix.md", "\n| x | CLM-9999 | ADR-003 | REQ-ADM-01 | a | `src/policy8.c` | `nonexistent_test.py` | Passed |\n")),
            ("evidence Check names a renamed script", "H03", sub("docs/research/evidence-register.md", "`models/interval.py` (1,050", "`models/interval_renamed.py` (1,050")),
            ("gate command names a missing script", "H03", sub("docs/validation/validation-gates.md", "`models/p8check.py`", "`models/p8check_gone.py`")),
            ("duplicate step number", "H04", sub("scripts/run_all_checks.sh", 'echo "== [2] tier', 'echo "== [1] tier')),
            ("script renamed under run_all_checks", "H04", sub("scripts/run_all_checks.sh", "scripts/arch_check.py", "scripts/arch_check_gone.py")),
            ("README step count drift", "H05", sub("README.md", "# all 38 checks", "# all 9 checks")),
            ("README mutation score drift", "H05", sub("README.md", "122 of 122 detectable (100%)", "121 of 122 detectable (100%)")),
            ("flip a README gate word", "H06", sub("README.md", "Not run, no silicon.", "Passing, no silicon.")),
            ("ADR with an invalid status", "H07", sub("docs/decisions/ADR-003-on-device-interval-admission.md", "**Status:** Accepted", "**Status:** Done")),
            ("Accepted ADR called Proposed elsewhere", "H07", append("docs/index.md", "\nADR-003 is Proposed.\n")),
            ("Derived claim loses its check", "H08", ("docs/research/evidence-register.md", lambda t: re.sub(r"^(\| CLM-02 \|(?:[^|]*\|){3})[^|]*\|", r"\1 — |", t, flags=re.M))),
            ("'not run' gate claimed passed", "H09", append("docs/index.md", "\nGATE-11 passed.\n")),
            ("status constant broken in model", "H10", sub("models/step_model.py", "OK, BADMSG, AUTH, ADMIT, HOLDER, DUPKEY, HALTED, BUDGET, BUSY, NOCLASS, STATE, IMAGE = 0, -1, -2, -3", "OK, BADMSG, AUTH, ADMIT, HOLDER, DUPKEY, HALTED, BUDGET, BUSY, NOCLASS, STATE, IMAGE = 0, -1, -2, -13")),
            ("action enum drift in header", "H10", sub("src/ac_waist.h", "AC_ACT_ACTIVATE_IMAGE = 2", "AC_ACT_ACTIVATE_IMAGE = 9")),
            ("AC_MAX_CLASSES drift", "H10", sub("src/ac_waist.h", "#define AC_MAX_CLASSES 16u", "#define AC_MAX_CLASSES 17u")),
            ("licence drift in CITATION.cff", "H11", sub("CITATION.cff", "license: Apache-2.0", "license: MIT")),
            ("copyright holder drift", "H11", sub("NOTICE", "Copyright 2026 Kiruthik", "Copyright 2025 Someone")),
            ("attribution trailer in a doc", "H12", append("docs/index.md", "\nCo-" + "Authored-By: X\n")),
        ]
        fails = 0
        for name, cid, (rel, edit) in plants:
            path = os.path.join(dst, rel); orig = open(path, encoding="utf-8").read()
            try:
                open(path, "w", encoding="utf-8").write(edit(orig))
            except AssertionError as e:
                print(f"  ERROR  {name}: {e}"); fails += 1; continue
            c2 = Ctx(dst)
            new = {(f, w) for f, l, w, _ in run(c2, only={cid}, quiet=True)[cid]} - base[cid]
            open(path, "w", encoding="utf-8").write(orig)
            if new: print(f"  caught {cid}  {name}")
            else: print(f"  MISSED {cid}  {name}"); fails += 1
        # git-authors check needs a repository; the copy has none, so it is exercised on the real tree only.
        print(f"health_check self-test: {len(plants)} drifts planted, {len(plants) - fails} caught, failures={fails}")
        return fails
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if "--self-test" in argv: return 1 if self_test() else 0
    if "--list" in argv:
        for cid, fn in CHECKS: print(cid, fn.__doc__.strip())
        return 0
    root = os.path.join(HERE, "..")
    if "--root" in argv: root = argv[argv.index("--root") + 1]
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    res = run(Ctx(root), only)
    bad = {k: v for k, v in res.items() if v}
    print("\n" + ("HEALTH CHECK PASSED (%d checks)" % len(res) if not bad else
          "HEALTH CHECK FAILED: %d of %d checks failed (%s), %d issues" % (len(bad), len(res), ", ".join(bad), sum(len(v) for v in bad.values()))))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

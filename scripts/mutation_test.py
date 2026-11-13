#!/usr/bin/env python3
"""Item 27 (50-things list): mutation testing of the test suite. [C]
Tests that cannot fail prove nothing. This mutates src/policy8.c (one textual mutation at a time:
flip a comparison operator, flip a boolean return, flip a logical connective) and reruns the
existing test binaries (tests/redteam_r2/fixcheck.c, and the p8test.c + models/p8check.py
differential test) against each mutant, in a scratch directory that mirrors the real build layout
(p8test.c and fixcheck.c both #include "policy8.c" by relative/quoted path, so the mutant has to
sit where the include resolves, exactly as a real build would see it -- not a separate code path).
A mutant that still passes every test is a SURVIVOR: evidence of a blind spot in the suite, not of
the suite's correctness. A survivor is sometimes harmless (an unreachable branch, a comment-only
region) rather than a real gap -- each one is printed with its line number for a human to judge.
"""
import re, os, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "src", "policy8.c")
TYPES_H = os.path.join(ROOT, "src", "ac_types.h")
FIXCHECK_SRC = os.path.join(ROOT, "tests", "redteam_r2", "fixcheck.c")
P8TEST_SRC = os.path.join(ROOT, "src", "p8test.c")
P8CHECK_PY = os.path.join(ROOT, "models", "p8check.py")

MUTATORS = [
    (r"<=", "<", "<= -> <"),
    (r">=", ">", ">= -> >"),
    (r"==", "!=", "== -> !="),
    (r"!=", "==", "!= -> =="),
    (r"\bk > nf\b", "k >= nf", "k > nf -> k >= nf"),
    (r"return 0;", "return 1;", "return 0 -> return 1"),
    (r"return 1;", "return 0;", "return 1 -> return 0"),
    (r"\|\|", "&&", "|| -> &&"),
    (r"&&", "\\|\\|", "&& -> ||"),
]

# Known EQUIVALENT mutants: a human (not the test suite) proved these produce identical observable
# behaviour for every input, so no test can ever kill them -- reporting them as survivors forever
# would misrepresent a 100%-detectable suite as merely 98%. Each entry needs a one-line proof, not
# just a claim; see run_all_checks.sh step [27]'s output for where this list is cross-checked.
KNOWN_EQUIVALENT = {
    ("k > nf -> k >= nf", "if (k > nf) k = nf;"):
        "ac_tbl_upper's `if (k > nf) k = nf;`: when k==nf, the original skips the assignment "
        "(k already equals nf); the mutant's `k >= nf` executes it, assigning nf to a variable "
        "already equal to nf -- a no-op. Identical for k<nf and k>nf too. No input distinguishes them.",
}

def blank_comments(source):
    """Replace /* ... */ comment bytes with spaces (same length, so offsets into the ORIGINAL
    source stay valid) so mutation sites are never chosen inside a comment -- a 'mutation' to text
    that isn't compiled is not a mutation at all, just a false survivor."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), source, flags=re.S)

def find_mutations(source):
    code_only = blank_comments(source)
    sites = []
    for pattern, repl, desc in MUTATORS:
        for m in re.finditer(pattern, code_only):
            sites.append((m.start(), m.end(), repl.replace("\\|", "|"), desc))
    return sites

def run_tests_against(mutant_source):
    """Builds a scratch dir with the mutant as src/policy8.c, plus copies of fixcheck.c and
    p8test.c alongside their includer's expected relative location. Returns True = SURVIVED
    (all tests passed anyway), False = KILLED (some test caught it, or it failed to even build)."""
    build = tempfile.mkdtemp(prefix="mut_")
    try:
        src_dir = os.path.join(build, "src")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "policy8.c"), "w") as f:
            f.write(mutant_source)
        shutil.copy(TYPES_H, src_dir)   # policy8.c includes "ac_types.h" from its own directory

        # fixcheck.c: quoted #include "../../src/policy8.c" relative to its own folder --
        # replicate the same relative depth (tests/redteam_r2/ -> ../../src/).
        fixcheck_dir = os.path.join(build, "tests", "redteam_r2")
        os.makedirs(fixcheck_dir)
        shutil.copy(FIXCHECK_SRC, fixcheck_dir)
        fx_exe = os.path.join(build, "fixcheck")
        cc = subprocess.run(["gcc", "-O1", "-o", fx_exe, os.path.join(fixcheck_dir, "fixcheck.c")],
                             capture_output=True, text=True)
        if cc.returncode != 0:
            return False, "fixcheck build failed"
        run = subprocess.run([fx_exe], capture_output=True, text=True)
        if run.returncode != 0:
            return False, "fixcheck caught it"

        # p8test.c: quoted #include "policy8.c" relative to its own folder -- copy alongside.
        shutil.copy(P8TEST_SRC, src_dir)
        p8_exe = os.path.join(build, "p8test")
        cc2 = subprocess.run(["gcc", "-O2", "-Wall", "-o", p8_exe, os.path.join(src_dir, "p8test.c")],
                              capture_output=True, text=True)
        if cc2.returncode != 0:
            return False, "p8test build failed"
        check = subprocess.run([sys.executable, P8CHECK_PY], cwd=build, capture_output=True, text=True)
        if check.returncode != 0 or "mismatches=0" not in check.stdout:
            return False, "p8check differential test caught it"

        return True, "survived"
    finally:
        shutil.rmtree(build, ignore_errors=True)

STEP_TARGET = os.path.join(ROOT, "src", "ac_step.c")
STEP_MUTATORS = MUTATORS + [
    (r"(?<![<>=!-])<(?![<=])", "<=", "< -> <="),
    (r"(?<![<>=!-])>(?![>=])", ">=", "> -> >="),
    (r"\+\+", "--", "++ -> --"),
]
# Known-equivalent mutants of ac_step.c: (description, stripped source line) -> why no input can tell them apart.
STEP_EQUIVALENT = {}

def make_step_scratch():
    d = tempfile.mkdtemp(prefix="mutstep_")
    shutil.copytree(os.path.join(ROOT, "src"), os.path.join(d, "src"), ignore=shutil.ignore_patterns("legacy"))
    os.makedirs(os.path.join(d, "tests")); os.makedirs(os.path.join(d, "models"))
    shutil.copy(os.path.join(ROOT, "tests", "step_test.c"), os.path.join(d, "tests"))
    shutil.copytree(os.path.join(ROOT, "tests", "vectors"), os.path.join(d, "tests", "vectors"))
    for f in os.listdir(os.path.join(ROOT, "models")):
        if f.endswith(".py"): shutil.copy(os.path.join(ROOT, "models", f), os.path.join(d, "models"))
    return d

def run_step_mutant(d, mutant_source):
    """True = SURVIVED (self checks, differential check and golden vectors all still pass)."""
    with open(os.path.join(d, "src", "ac_step.c"), "w") as f: f.write(mutant_source)
    cc = subprocess.run(["gcc", "-O2", "-o", "models/step_test", "tests/step_test.c"], cwd=d, capture_output=True, text=True)
    if cc.returncode != 0: return False
    try:
        if subprocess.run(["models/step_test", "self"], cwd=d, capture_output=True, timeout=20).returncode != 0: return False
        for cmd in (["python3", "step_check.py"], ["python3", "step_check.py", "--verify-golden", "../tests/vectors/waist-v1.txt"]):
            if subprocess.run(cmd, cwd=os.path.join(d, "models"), capture_output=True, timeout=60).returncode != 0: return False
    except subprocess.TimeoutExpired:
        return False
    return True

def main_step(limit=None):
    source = open(STEP_TARGET).read()
    code_only = blank_comments(source)
    sites = []
    for pattern, repl, desc in STEP_MUTATORS:
        for m in re.finditer(pattern, code_only):
            sites.append((m.start(), m.end(), repl.replace("\\|", "|"), desc))
    if limit: sites = sites[:limit]
    d = make_step_scratch(); killed = equivalent = 0; survivors = []
    try:
        for start, end, repl, desc in sites:
            line_no = source[:start].count("\n") + 1
            if run_step_mutant(d, source[:start] + repl + source[end:]):
                key = (desc, source.split("\n")[line_no - 1].strip())
                if key in STEP_EQUIVALENT:
                    equivalent += 1
                    print(f"  EQUIVALENT line {line_no}: {desc} -- {STEP_EQUIVALENT[key]}")
                else:
                    survivors.append((line_no, desc, key[1])); print(f"  SURVIVOR  line {line_no}: {desc}   [{key[1][:90]}]")
            else: killed += 1
    finally:
        shutil.rmtree(d, ignore_errors=True)
    total = killed + len(survivors)
    print(f"\nac_step.c mutation score: {killed}/{total} detectable mutants killed ({killed / total:.0%}); "
          f"{equivalent} known-equivalent excluded; {len(survivors)} survivor(s)")
    if survivors: sys.exit(1)

def main(limit=None):
    source = open(TARGET).read()
    sites = find_mutations(source)
    if limit:
        sites = sites[:limit]
    killed = survived = equivalent = 0
    survivors = []
    for start, end, repl, desc in sites:
        mutant_source = source[:start] + repl + source[end:]
        line_no = source[:start].count("\n") + 1
        ok, reason = run_tests_against(mutant_source)
        if ok:
            key = (desc, source.split("\n")[line_no - 1].strip())
            if key in KNOWN_EQUIVALENT:
                equivalent += 1
                print(f"  EQUIVALENT (not a gap)  line {line_no}: {desc} -- {KNOWN_EQUIVALENT[key]}")
            else:
                survived += 1
                survivors.append((line_no, desc))
                print(f"  SURVIVOR  line {line_no}: {desc}")
        else:
            killed += 1
    total = killed + survived
    detectable_total = total + equivalent
    score = killed / total if total else 1.0
    print(f"\nMutation score: {killed}/{total} of DETECTABLE mutants killed ({score:.0%}); "
          f"{equivalent} known-equivalent mutant(s) excluded (proof in KNOWN_EQUIVALENT) out of "
          f"{detectable_total} total mutation sites. {len(survivors)} real survivor(s) need review.")
    if survivors:
        sys.exit(1)
    return survivors

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    limit = int(args[0]) if args else None
    if "--step" in sys.argv: main_step(limit)
    else: main(limit)

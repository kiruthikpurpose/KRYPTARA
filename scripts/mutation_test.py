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
    (130, "k > nf -> k >= nf"):
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
            key = (line_no, desc)
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
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)

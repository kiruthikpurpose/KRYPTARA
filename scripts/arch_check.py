#!/usr/bin/env python3
"""Architecture fitness checks: the kernel's design rules, made executable (REQ-WAIST-01, ADR-041).
Each rule fails the build when broken, so the rules cannot erode silently as the code grows.

Rules, for the kernel core (src/ac_types.h, ac_waist.h, policy8.c, policy8_prov.c, kernel.c, ac_step.c):
  R1  includes: only <stdint.h>, <stddef.h>, <string.h> and files of the core itself
  R2  no I/O, allocation, clock, randomness or non-local jumps in the source
  R3  each translation unit builds clean under -std=c99 -pedantic -Wall -Wextra -Werror
  R4  no mutable global state: the object files have no .data or .bss symbols
  R5  a closed set of external symbols: memset, memcpy, memcmp and the hash provider, nothing else
  R6  no recursion, from the compiler's call graph
  R7  no unbounded dynamic stack use; the deepest static call chain is reported and budgeted
  R8  the frozen ABI (constants and struct layouts) equals the committed lock src/waist-v1.abi
`--update-lock` rewrites the lock. Until the T0 freeze (roadmap Phase 3) updating it is allowed; after
the freeze a lock change means a new waist major version.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.environ.get("ARCH_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
CORE = ["ac_types.h", "ac_waist.h", "policy8.c", "policy8_prov.c", "kernel.c", "ac_step.c"]
CORE_TUS = ["policy8.c", "policy8_prov.c", "kernel.c", "ac_step.c"]
SYSTEM_INCLUDES = {"stdint.h", "stddef.h", "string.h"}
QUOTED_INCLUDES = set(CORE) | {"prototypes/c/sha256.h"}
BANNED = r"\b(malloc|calloc|realloc|free|alloca|printf|fprintf|sprintf|snprintf|vsnprintf|puts|putchar|scanf|sscanf|fopen|fclose|fread|fwrite|getchar|exit|abort|rand|srand|time|clock|gettimeofday|signal|setjmp|longjmp|qsort|errno|asm|__asm__)\b"
ALLOWED_EXTERNS = {"memset", "memcpy", "memcmp", "sha256_init", "sha256_update", "sha256_final"}
STACK_BUDGET = 1024    # bytes, deepest static call chain, host x86-64 -O2 (not target silicon)
CFLAGS = ["-std=c99", "-pedantic", "-Wall", "-Wextra", "-Werror", "-O2", "-fno-pic", "-fno-pie",
          "-fno-stack-protector", "-fcf-protection=none"]

def strip(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return re.sub(r'"(\\.|[^"\\])*"', '""', text)

failures = []
def fail(rule, msg): failures.append(f"{rule}: {msg}"); print(f"  FAIL {rule}: {msg}")
def ok(rule, msg): print(f"  ok   {rule}: {msg}")

def r1_r2():
    n = 0
    for f in CORE:
        raw = open(os.path.join(SRC, f)).read()
        for m in re.finditer(r'^\s*#\s*include\s*([<"])([^>"]+)[>"]', raw, re.M):
            kind, name = m.groups()
            if (kind == "<" and name not in SYSTEM_INCLUDES) or (kind == '"' and name not in QUOTED_INCLUDES):
                fail("R1", f"{f} includes {kind}{name}{'>' if kind == '<' else kind}")
            n += 1
        for m in re.finditer(BANNED, strip(raw)):
            fail("R2", f"{f} uses '{m.group(0)}'")
    if not any(x.startswith(("R1", "R2")) for x in failures): ok("R1/R2", f"{n} includes allowed, no banned identifiers in {len(CORE)} core files")

def build(tu, out, extra=()):
    return subprocess.run(["gcc", *CFLAGS, *extra, "-c", os.path.join(SRC, tu), "-o", out], cwd=ROOT, capture_output=True, text=True)

def check_tus():
    worst = {}
    with tempfile.TemporaryDirectory() as d:
        for tu in CORE_TUS:
            o = os.path.join(d, tu + ".o")
            r = build(tu, o, ["-fcallgraph-info=su", "-fstack-usage"])
            if r.returncode != 0:
                fail("R3", f"{tu} does not build clean: {r.stderr.strip().splitlines()[0] if r.stderr.strip() else 'error'}"); continue
            nm = subprocess.run(["nm", o], capture_output=True, text=True).stdout.splitlines()
            data = [l for l in nm if len(l.split()) == 3 and l.split()[1] in "dDbBsSgGcC"]
            if data: fail("R4", f"{tu} has mutable data symbols: {[l.split()[2] for l in data]}")
            ext = {l.split()[-1] for l in nm if l.split()[-2:-1] == ["U"]}
            if ext - ALLOWED_EXTERNS: fail("R5", f"{tu} references unexpected symbols {sorted(ext - ALLOWED_EXTERNS)}")
            graph, frames = {}, {}
            # The call graph comes from an -O0 build: at -O2 the optimiser can turn recursion into a
            # loop (found by the self-test), which would hide a source-level cycle.
            o0 = os.path.join(d, tu + ".O0.o")
            r0 = build(tu, o0, ["-O0", "-fcallgraph-info=su"])
            ci = open(os.path.join(d, tu + ".O0.ci")).read() if r0.returncode == 0 else ""
            for m in re.finditer(r'edge: \{ sourcename: "([^"]+)" targetname: "([^"]+)"', ci): graph.setdefault(m.group(1), set()).add(m.group(2))
            ci2 = open(os.path.join(d, tu + ".ci")).read()
            for m in re.finditer(r'edge: \{ sourcename: "([^"]+)" targetname: "([^"]+)"', ci2): graph.setdefault(m.group(1), set()).add(m.group(2))
            for l in open(os.path.join(d, tu + ".su")):
                p = l.rstrip("\n").split("\t")
                if len(p) >= 3:
                    name = p[0].split(":")[-1]
                    frames[name] = int(p[1])
                    if "dynamic" in p[2] and "bounded" not in p[2]: fail("R7", f"{tu}: {name} has unbounded dynamic stack use")
            # R6: cycle detection over the call graph
            state = {}
            def dfs(n, path):
                state[n] = 1
                for m in graph.get(n, ()):
                    if state.get(m) == 1: fail("R6", f"{tu}: recursion {' -> '.join(path + [n, m])}"); continue
                    if m not in state: dfs(m, path + [n])
                state[n] = 2
            for n in list(graph):
                if n not in state: dfs(n, [])
            def depth(n, seen=()):
                return frames.get(n, 0) + max([depth(m, seen + (n,)) for m in graph.get(n, ()) if m not in seen] or [0])
            for n in frames: worst[n] = depth(n)
    return worst

def abi():
    with tempfile.TemporaryDirectory() as d:
        exe = os.path.join(d, "abi_probe")
        r = subprocess.run(["gcc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", exe, os.path.join(ROOT, "tests", "abi_probe.c")], capture_output=True, text=True)
        if r.returncode: fail("R8", "ABI probe does not build: " + r.stderr.strip()); return None
        return subprocess.run([exe], capture_output=True, text=True).stdout

def main():
    update = "--update-lock" in sys.argv
    print("architecture fitness checks (kernel core)")
    r1_r2()
    worst = check_tus()
    if not any(x.split(":")[0] in ("R3", "R4", "R5", "R6", "R7") for x in failures):
        ok("R3", f"{len(CORE_TUS)} translation units build clean under {' '.join(CFLAGS[:4])}")
        ok("R4", "no .data or .bss symbols: no mutable global state")
        ok("R5", f"external symbols within {sorted(ALLOWED_EXTERNS)}")
        ok("R6", "no recursion in the compiler's call graph")
    chain = max(worst.values()) if worst else 0
    if chain > STACK_BUDGET: fail("R7", f"deepest static call chain {chain} B exceeds the {STACK_BUDGET} B budget")
    else: ok("R7", f"deepest static call chain {chain} B (host x86-64, budget {STACK_BUDGET} B; not target silicon)")
    probe = abi()
    lock = os.path.join(SRC, "waist-v1.abi")
    if probe is not None:
        if update:
            open(lock, "w").write(probe); print(f"  wrote {lock}")
        elif not os.path.exists(lock): fail("R8", "src/waist-v1.abi is missing; run with --update-lock")
        else:
            old, new = open(lock).read().splitlines(), probe.splitlines()
            diff = [f"{a} -> {b}" for a, b in zip(old, new) if a != b] + [f"missing {x}" for x in old[len(new):]] + [f"new {x}" for x in new[len(old):]]
            if diff: fail("R8", "frozen ABI changed: " + "; ".join(diff[:6]))
            else:
                sz = [l for l in new if l.startswith("sizeof(ac_ctx_t)")][0]
                ok("R8", f"{len(new)} constants and layouts equal the lock ({sz}; locked-stage RAM budget 4096 B)")
    print(f"arch_check failures={len(failures)}")
    return len(failures)

def self_test():
    """Plant one violation of each kind in a scratch copy; every one must make the check fail."""
    import shutil
    plants = [
        ("R1 stray include", "policy8.c", lambda t: t.replace('#include <string.h>', '#include <string.h>\n#include <stdlib.h>', 1)),
        ("R2 allocation", "kernel.c", lambda t: t + "\nvoid *leak(void) { return malloc(4); }\n"),
        ("R4 mutable global", "kernel.c", lambda t: t + "\nint ac_calls;\nvoid ac_count(void) { ac_calls++; }\n"),
        ("R5 new external symbol", "policy8.c", lambda t: t + "\nint ac_uses_libc(const char *s) { return (int)strlen(s); }\n"),
        ("R6 recursion", "kernel.c", lambda t: t + "\nunsigned ac_fact(unsigned n);\nunsigned ac_fact(unsigned n) { return n <= 1 ? 1 : n * ac_fact(n - 1); }\n"),
        ("R8 ABI drift", "ac_waist.h", lambda t: re.sub(r"AC_E_IMAGE\s*=\s*-11", "AC_E_IMAGE = -12", t)),
    ]
    bad = 0
    for name, fname, edit in plants:
        d = tempfile.mkdtemp(prefix="archneg_")
        try:
            shutil.copytree(os.path.join(ROOT, "src"), os.path.join(d, "src"), ignore=shutil.ignore_patterns("legacy"))
            shutil.copytree(os.path.join(ROOT, "tests"), os.path.join(d, "tests"), ignore=shutil.ignore_patterns("vectors", "redteam_r2"))
            path = os.path.join(d, "src", fname)
            before = open(path).read(); after = edit(before)
            assert before != after, f"plant '{name}' did not change {fname}"
            open(path, "w").write(after)
            r = subprocess.run([sys.executable, os.path.join(HERE, "arch_check.py")], env=dict(os.environ, ARCH_ROOT=d), capture_output=True, text=True)
            caught = r.returncode != 0
            print(f"  {'caught' if caught else 'MISSED'}  {name}")
            bad += not caught
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"arch_check self-test failures={bad}")
    return bad

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(1 if self_test() else 0)
    sys.exit(1 if main() else 0)

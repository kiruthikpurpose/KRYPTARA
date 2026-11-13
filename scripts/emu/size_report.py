#!/usr/bin/env python3
"""Per-function Thumb-1 (Cortex-M0+) code size of the admission code, from zig cc (LLVM).

LABEL: this is zig/LLVM -Os output (`zig cc -target thumb-freestanding-eabi -mcpu=cortex_m0plus`),
NOT arm-none-eabi-gcc and NOT silicon. GCC and LLVM differ by tens of percent on small functions,
so GATE-07 (defined against arm-none-eabi-gcc) is not decided by this script; it is an independent
second-compiler estimate. Needs: pip install ziglang pyelftools (see scripts/emu/README in the
script header of cycles.py). Exits 0 with a notice if the tools are absent.

Usage: size_report.py    (budget read from scripts/emu/size_budget.txt)
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE_BUDGET_BYTES = int([l for l in open(os.path.join(HERE, "size_budget.txt")) if l.strip() and not l.startswith("#")][0])
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from elftools.elf.elffile import ELFFile
except ImportError:
    print("size_report: pyelftools not installed (pip install ziglang pyelftools); not run"); sys.exit(0)

def zig_cc(src, out, defs=()):
    cmd = [sys.executable, "-m", "ziglang", "cc", "-target", "thumb-freestanding-eabi",
           "-mcpu=cortex_m0plus", "-Os", "-ffunction-sections", "-std=c99", "-I", SRC, "-I", os.path.join(HERE, "shim"),
           *[f"-D{d}" for d in defs], "-c", src, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit("zig cc failed:\n" + r.stderr)

def funcs(obj):
    with open(obj, "rb") as f:
        e = ELFFile(f)
        text = sum(s["sh_size"] for s in e.iter_sections() if s.name.startswith(".text"))
        ro = sum(s["sh_size"] for s in e.iter_sections() if s.name.startswith(".rodata"))
        fs = {}
        for s in e.get_section_by_name(".symtab").iter_symbols():
            if s["st_info"]["type"] == "STT_FUNC": fs[s.name] = s["st_size"]
    return fs, text, ro

def report(title, src, defs=()):
    with tempfile.TemporaryDirectory() as d:
        o = os.path.join(d, "x.o"); zig_cc(src, o, defs)
        fs, text, ro = funcs(o)
    print(f"\n{title}")
    for n, s in sorted(fs.items(), key=lambda kv: -kv[1]): print(f"  {s:6d}  {n}")
    print(f"  .text total = {text} B, .rodata = {ro} B, text+rodata = {text + ro} B")
    return text + ro

if __name__ == "__main__":
    print("zig/LLVM -Os, thumbv6m (cortex_m0plus). NOT arm-none-eabi-gcc, NOT silicon.")
    full = report("src/policy8.c (all of it, incl. provisioning)", os.path.join(SRC, "policy8.c"))
    rt = report("src/policy8.c -DAC_RUNTIME_ONLY (locked-stage runtime admission)",
                os.path.join(SRC, "policy8.c"), ["AC_RUNTIME_ONLY"])
    if os.path.exists(os.path.join(SRC, "policy8_prov.c")):
        report("src/policy8_prov.c (provisioning/derivation TU)", os.path.join(SRC, "policy8_prov.c"))
    print(f"\nbudget (scripts/emu/size_budget.txt): {SIZE_BUDGET_BYTES} B; runtime-only (text+rodata) = {rt} B -> "
          f"{'within' if rt <= SIZE_BUDGET_BYTES else 'OVER'} (llvm estimate, not the gcc gate)")

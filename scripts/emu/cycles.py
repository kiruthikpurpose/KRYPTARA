#!/usr/bin/env python3
"""Instruction counts and an ESTIMATED Cortex-M0+ cycle count for the admission functions.

LABEL: ESTIMATE. Code is zig/LLVM -Os Thumb-1 (not arm-none-eabi-gcc), executed in the Unicorn (QEMU)
CPU emulator, which is functionally exact but has NO timing model. Cycles are computed here from a
documented per-instruction table (below). This is not a silicon measurement and does not decide GATE-09.

Cycle model (ARMv6-M / Cortex-M0+ TRM instruction timings, single-cycle I/O port, zero flash wait
states, no DMA/interrupt contention):
  data-processing, MOV/CMP/ADD/SUB/shifts/logic/MUL/extend/REV : 1
  LDR/LDRB/LDRH/STR/STRB/STRH (any addressing)                  : 2
  LDM/STM                                                       : 1 + N registers
  PUSH/POP                                                      : 1 + N ; POP that loads PC: 4 + N
  B / Bcond taken: 2   Bcond not taken: 1   BL: 4   BX/BLX register: 3
  anything unrecognised                                         : counted separately and reported
Assumptions and limits: real parts have flash wait states above ~24 MHz (typically 1-3 extra cycles
per fetch without a cache), which can double these figures; M0+ on some vendors uses a slower
multiplier (32 cycles) - this code was checked to contain no MUL; the Unicorn instruction hook counts
architectural instructions, so no pipeline stalls beyond the table above are modelled. Treat results
as a lower bound to within a flash-wait-state factor, pending EXP-19 silicon measurement.
Needs: pip install ziglang unicorn pyelftools capstone
"""
import os, subprocess, sys, tempfile, struct

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
try:
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UcError
    from unicorn.arm_const import *
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
    from elftools.elf.elffile import ELFFile
except ImportError as e:
    print(f"cycles: missing module ({e}); pip install ziglang unicorn pyelftools capstone. not run"); sys.exit(0)

CODE, RAM, STACK_TOP, HALT = 0x08000000, 0x20000000, 0x20010000, 0x08FFFFF0

def build(d, defs=()):
    out = os.path.join(d, "fw.elf")
    cmd = [sys.executable, "-m", "ziglang", "cc", "-target", "thumb-freestanding-eabi", "-mcpu=cortex_m0plus",
           "-Os", "-g", "-ffreestanding", "-fno-builtin", "-std=c99", "-I", os.path.join(ROOT, "src"), "-I", os.path.join(HERE, "shim"),
           *[f"-D{x}" for x in defs],
           os.path.join(ROOT, "src", "policy8.c"), os.path.join(HERE, "emu_rt.c"),
           "-nostdlib", "-static", "-Wl,--no-gc-sections", f"-Wl,--image-base={CODE:#x}",
           "-Wl,--entry=0", "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit("zig cc failed:\n" + r.stderr)
    return out

def cyc(mn, ops, taken, nregs):
    m = mn.lower()
    if m in ("ldr", "ldrb", "ldrh", "ldrsb", "ldrsh", "str", "strb", "strh"): return 2
    if m in ("ldm", "ldmia", "stm", "stmia"): return 1 + nregs
    if m == "push": return 1 + nregs
    if m == "pop": return (4 if "pc" in ops else 1) + nregs
    if m == "bl": return 4
    if m in ("bx", "blx"): return 3
    if m == "b": return 2
    if m.startswith("b") and m[1:] in ("eq","ne","hs","lo","mi","pl","vs","vc","hi","ls","ge","lt","gt","le","cs","cc"):
        return 2 if taken else 1
    if m in ("mov","movs","mvn","mvns","add","adds","sub","subs","adc","adcs","sbc","sbcs","and","ands","orr","orrs",
             "eor","eors","bic","bics","lsl","lsls","lsr","lsrs","asr","asrs","ror","rors","cmp","cmn","tst","neg","negs",
             "rsb","rsbs","sxtb","sxth","uxtb","uxth","rev","rev16","revsh","nop","adr","muls","mul"): return 1
    return None

class Run:
    def __init__(self, elf_path):
        self.elf = ELFFile(open(elf_path, "rb"))
        self.sym = {s.name: s["st_value"] & ~1 for s in self.elf.get_section_by_name(".symtab").iter_symbols()
                    if s["st_info"]["type"] == "STT_FUNC"}
        self.segs = [(p["p_vaddr"], p.data()) for p in self.elf.iter_segments() if p["p_type"] == "PT_LOAD"]
        self.cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS); self.cs.detail = False
    def call(self, fn, args, ram_init=()):
        mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        mu.mem_map(CODE & ~0xFFFFFF, 0x1000000); mu.mem_map(RAM, 0x20000)
        for a, b in self.segs: mu.mem_write(a, b)
        for a, b in ram_init: mu.mem_write(a, b)
        for i, v in enumerate(args[:4]): mu.reg_write(UC_ARM_REG_R0 + i, v)
        sp = STACK_TOP - 4 * len(args[4:])          # AAPCS: arguments 5.. go on the stack
        for i, v in enumerate(args[4:]): mu.mem_write(sp + 4 * i, struct.pack("<I", v))
        mu.reg_write(UC_ARM_REG_SP, sp); mu.reg_write(UC_ARM_REG_LR, HALT | 1)
        st = {"n": 0, "c": 0, "unk": {}}
        prev = {"pc": None, "mn": None, "sz": 0}
        def settle(pc):  # resolve taken/not-taken of the previous conditional branch
            if prev["mn"] is not None:
                taken = pc != prev["pc"] + prev["sz"]
                c = cyc(*prev["mn"], taken)
                if c is None: st["unk"][prev["mn"][0]] = st["unk"].get(prev["mn"][0], 0) + 1; c = 1
                st["c"] += c
        def hook(uc, addr, size, _):
            if addr == HALT: return
            settle(addr)
            code = bytes(uc.mem_read(addr, size))
            ins = next(self.cs.disasm(code, addr), None)
            st["n"] += 1
            if ins is None: prev["mn"] = ("?", "", 0)
            else:
                ops = ins.op_str; nreg = ops.count(",") + 1 if "{" in ops else 0
                prev["mn"] = (ins.mnemonic, ops, nreg)
            prev["pc"], prev["sz"] = addr, size
        mu.hook_add(UC_HOOK_CODE, hook)
        mu.emu_start(self.sym[fn] | 1, HALT, count=2_000_000)
        settle(HALT)
        return mu, st

def table_from_masks(f):  # same monotone table the host bench uses is not needed; a simple threshold table
    t = [0] * 8
    for m in range(256):
        if bin(m).count("1") >= 2: t[m >> 5] |= 1 << (m & 31)
    return struct.pack("<8I", *t)

def host_reference():
    """Host gcc build of src/policy8.c as a shared library, used only to check that the emulated Thumb
    code computes the SAME results (a timing figure for wrong code would be meaningless)."""
    import ctypes
    d = tempfile.mkdtemp(); so = os.path.join(d, "p8.so")
    subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", so, os.path.join(ROOT, "src", "policy8.c")], check=True)
    return ctypes.CDLL(so)

def main():
    import ctypes
    host = host_reference()
    with tempfile.TemporaryDirectory() as d:
        elf = build(d, defs=sys.argv[1:])
        r = Run(elf)
        T, F, U = RAM, RAM + 0x100, RAM + 0x200
        tbl = table_from_masks(None)
        rows = []
        bad = []
        def go(label, fn, args, init, out=None):
            mu, st = r.call(fn, args, init)
            rows.append((label, st["n"], st["c"], st["unk"]))
            # functional check against the host build: return value, and the output table if any
            hargs = [ctypes.c_void_p(a) if False else a for a in args]
            ret = mu.reg_read(UC_ARM_REG_R0) & 0xFFFFFFFF
            hbuf = ctypes.create_string_buffer(32); hf = ctypes.create_string_buffer(bytes(init[-1][1]) if fn.startswith("ac_tbl_up") or fn.startswith("ac_tbl_lo") else tbl, 64)
            hfn = getattr(host, fn); hfn.restype = ctypes.c_int
            if fn in ("ac_tbl_upper", "ac_tbl_lower"):
                hret = hfn(hbuf, hf, ctypes.c_uint(args[2]), ctypes.c_uint(args[3]), ctypes.c_ubyte(args[4]), None)
                if bytes(mu.mem_read(U, 32)) != hbuf.raw: bad.append(label + " table")
            elif fn == "ac_tbl_authorises":
                hret = hfn(hf, ctypes.c_ubyte(args[1]))
            else:
                hret = hfn(hf, ctypes.c_ubyte(args[1]), ctypes.c_ubyte(args[2]), ctypes.c_int(args[3]))
            if (hret & 0xFFFFFFFF) != ret: bad.append(label + f" return emu={ret} host={hret & 0xFFFFFFFF}")
            return mu
        for S in (0x00, 0x03, 0xFF):
            go(f"ac_tbl_authorises S={S:#04x}", "ac_tbl_authorises", [T, S], [(T, tbl)])
        for act in (0, 1):
            go(f"ac_key_install_authorised S=0xFF active={act}", "ac_key_install_authorised", [T, 0xFF, 0x04, act], [(T, tbl)])
        for nf in (3, 12):
            fcls = bytes((1 << (i % 8)) | (1 << ((i * 3 + 1) % 8)) if nf == 12 else (1 << i) for i in range(nf))
            mu = go(f"ac_tbl_upper nf={nf} k=2 expo=0x80", "ac_tbl_upper", [U, F, nf, 2, 0x80, 0], [(F, fcls)])
            go(f"ac_tbl_lower nf={nf} k=2 absent=0x00", "ac_tbl_lower", [U, F, nf, 2, 0x00, 0], [(F, fcls)])
    print("functional check vs host gcc build of the same source:", "MISMATCH " + "; ".join(bad) if bad else "all outputs identical")
    print("ESTIMATE ONLY: zig/LLVM -Os Thumb-1 code, Unicorn instruction counts, table-driven Cortex-M0+ cycles.")
    print("Not arm-none-eabi-gcc, not silicon, zero flash wait states. See module docstring for the model.\n")
    print(f"{'case':46s} {'instr':>8s} {'est cycles':>11s}  {'us@48MHz':>9s}")
    for label, n, c, unk in rows:
        print(f"{label:46s} {n:8d} {c:11d}  {c/48:9.2f}" + (f"  UNMODELLED:{unk}" if unk else ""))

if __name__ == "__main__":
    main()

# Differential check of waist v1: src/ac_step.c (via tests/step_test.c) against models/step_model.py. [C]
#   python3 step_check.py                        random scenarios, C vs Python, with a coverage gate
#   python3 step_check.py --emit-golden FILE     write golden vectors (input lines and expected output)
#   python3 step_check.py --verify-golden FILE   replay golden vectors through the C build only
# Expects ./step_test in the working directory (built by scripts/run_all_checks.sh).
# The golden file is the long-lived artefact: any implementation of waist v1 (a Rust twin, a port)
# must reproduce it line for line. It is not regenerated on a normal run.
import os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import step_model as sm
from step_model import *
from lint import (lint, structures, project, present_mask, ATOMS, ALL, REMOTE, NANO, OPERATE, CONST, RECOVERY, HALT as T_HALT, BOTHF,
                  REMOTE_OPERATE, REMOTE_CONST2, NANO_OPERATE, NANO_PRES_OPERATE)

BASE12 = [1, 2, 4, 8, 16, 32, 64, 3, 12, 48, 0x15, 0x2A]

def upclose(points):
    return sum(1 << m for m in range(256) if any(m & p == p for p in points))

def reference_genesis(fortress):
    """The project's reference terrestrial profile, with classes and budgets taken from models/lint.py."""
    names = [a.name for a in ATOMS]
    def classes(t, s, kw):
        Ac, Al, Fc, Fl = structures(ATOMS, ALL, t, s, **kw)
        dedupe = lambda d: list(dict.fromkeys(d.values()))
        return Fc, Fl, dedupe(Fc), dedupe(Fl)
    out = []
    specs = [(1, 0, {}), (1, 1, dict(loss_kinds=("SIG", "PRES"))), (2, 1, dict(loss_labels={"group"})),
             (1, 2, dict(loss_labels={"group", "family"}, exclude_loss_combo=BOTHF))]
    for (t, s, kw) in specs:
        Fc, Fl, fc, fl = classes(t, s, kw)
        xl = (NONE, NONE)
        if kw.get("exclude_loss_combo"):
            masks = [Fl[k] for k in Fl]
            a, b = kw["exclude_loss_combo"][0]
            ia, ib = fl.index(Fl[a]), fl.index(Fl[b])
            xl = (min(ia, ib), max(ia, ib))
        out.append(budget(t, s, fc, fl, xl=xl))
    tiers = [T_HALT, OPERATE, CONST, RECOVERY]
    at = [0, 1, 1, 1, 1, 1, 2 if fortress else 3, 2 if fortress else 3]
    return dict(present=0xff, kinds=[1, 1, 1, 1, 1, 1, 2, 3], key_present=0x3f, halt_budget=2, bud=out,
                action_tier=at, table=[project(t, 0xff) for t in tiers])

def lint_budget(present, t, s, **kw):
    """A per-tier budget taken from models/lint.py's fault structure for the given present atoms."""
    Ac, Al, Fc, Fl = structures(ATOMS, present, t, s, **kw)
    dedupe = lambda d: list(dict.fromkeys(d.values()))
    fc, fl = dedupe(Fc), dedupe(Fl)
    xl = (NONE, NONE)
    if kw.get("exclude_loss_combo"):
        a, b = kw["exclude_loss_combo"][0]
        ia, ib = fl.index(Fl[a]), fl.index(Fl[b]); xl = (min(ia, ib), max(ia, ib))
    xc = (NONE, NONE)
    if kw.get("exclude_comp_combo"):
        a, b = kw["exclude_comp_combo"][0]
        ia, ib = fc.index(Fc[a]), fc.index(Fc[b]); xc = (min(ia, ib), max(ia, ib))
    return budget(t, s, fc, fl, xc, xl)

def remote_genesis():
    """The remote profile (no presence atom): the same kernel, different data. No C change is involved."""
    present = REMOTE
    mask = present_mask(ATOMS, present)
    t1 = lint_budget(present, 1, 1, loss_labels={"group"})
    t2 = lint_budget(present, 2, 1, loss_labels=set(), exclude_comp_combo=BOTHF)
    t0 = lint_budget(present, 1, 0)
    tables = [project(T_HALT, mask), project(REMOTE_OPERATE, mask), project(REMOTE_CONST2, mask), project(REMOTE_CONST2, mask)]
    return dict(present=mask, kinds=[1, 1, 1, 1, 1, 1, 2, 3], key_present=0x3f, halt_budget=2, bud=[t0, t1, t2, t2],
                action_tier=[0, 1, 1, 1, 1, 1, 2, 2], table=tables)

def random_genesis(rng):
    kinds = [1] * 6 + [2, 3] if rng.random() < 0.8 else [rng.choice([0, 1, 1, 1, 2, 3]) for _ in range(8)]
    present = 0xff if rng.random() < 0.8 else rng.randrange(256)
    sig = sum(1 << i for i in range(8) if kinds[i] == 1 and (present >> i) & 1)
    kp = sig if rng.random() < 0.6 else sig & rng.randrange(256)
    def classes():
        if rng.random() < 0.1: return [rng.randrange(1, 256) for _ in range(rng.choice([0, 1, 2]))]   # tiny list: budget may exceed it
        c = [m for m in BASE12 if rng.random() < 0.8] + [rng.randrange(1, 256) for _ in range(rng.choice([0, 0, 1, 2]))]
        return c[:MAXC]
    bud = []
    for t in range(4):
        fc, fl = classes(), classes()
        xc = xl = (NONE, NONE)
        if len(fc) > 1 and rng.random() < 0.15: a, b = sorted(rng.sample(range(len(fc)), 2)); xc = (a, b)
        if len(fl) > 1 and rng.random() < 0.25: a, b = sorted(rng.sample(range(len(fl)), 2)); xl = (a, b)
        bud.append(budget(rng.choice([0, 1, 1, 2]), rng.choice([0, 1, 1, 2]), fc, fl, xc, xl))
    at = [0, 1, 1, 1, 1, 1, 3, 3] if rng.random() < 0.85 else [rng.randrange(5) for _ in range(8)]
    if rng.random() < 0.4 and at[6] in (2, 3): at[6] = at[7] = 2
    g = dict(present=present, kinds=kinds, key_present=kp, halt_budget=rng.choice([0, 1, 2, 2, 3]), bud=bud,
             action_tier=at, table=[0] * 4)
    probe = Model(); probe.present, probe.kinds, probe.bud = present, kinds, bud
    for t in range(4):
        iv = probe.interval(t) if t else None
        if t and iv and (iv[0] & ~iv[1]) == 0 and rng.random() < 0.9:
            lo, up = iv
            seeds = [m for m in range(256) if (up >> m) & 1 and rng.random() < 0.02]
            g["table"][t] = project(lo | upclose(seeds), present)
        else:
            seeds = [rng.randrange(256) for _ in range(rng.randint(1, 4))]
            g["table"][t] = project(upclose(seeds), present)
    if rng.random() < 0.3: g = corrupt_genesis(g, rng)
    return g

def corrupt_genesis(g, rng):
    """One malformed-provisioning mutation. Genesis must refuse each of these with ADMIT."""
    import copy
    g = copy.deepcopy(g)
    t = rng.randrange(4)
    kind = rng.randrange(12)
    if kind == 0: g["kinds"][rng.randrange(8)] = rng.choice([4, 5, 200])
    elif kind == 1:
        bad = [i for i in range(8) if not (g["present"] >> i) & 1 or g["kinds"][i] != 1]
        if bad: g["key_present"] |= 1 << rng.choice(bad)
    elif kind == 2: g["bud"][t]["nfc"] = rng.choice([17, 255])
    elif kind == 3: g["bud"][t]["nfl"] = rng.choice([17, 255])
    elif kind == 4: g["bud"][t][rng.choice(["t", "s"])] = rng.choice([3, 255])
    elif kind == 5 and g["bud"][t]["nfc"]: g["bud"][t]["fc"][rng.randrange(g["bud"][t]["nfc"])] = 0
    elif kind == 6 and g["bud"][t]["nfl"]: g["bud"][t]["fl"][rng.randrange(g["bud"][t]["nfl"])] = 0
    elif kind == 7:
        side = rng.choice(["xc", "xl"]); n = g["bud"][t]["nfc" if side == "xc" else "nfl"]
        g["bud"][t][side] = rng.choice([(1, 1), (2, 1), (0, n), (NONE, 0), (0, NONE), (n, n + 1)])
    elif kind == 8:
        a = rng.randrange(8); g["action_tier"][a] = rng.choice([x for x in range(5) if x != g["action_tier"][a]])
    elif kind == 9: g["action_tier"][sm.INSTALL_TABLE] = 2 if g["action_tier"][sm.KEY_INSTALL] == 3 else 3
    elif kind == 10:
        pts = [rng.randrange(256) for _ in range(rng.randint(1, 3))]
        g["table"][t] = upclose(pts) ^ (1 << rng.randrange(256))      # almost certainly not monotone
    else: g["bud"][t]["nfl"] = min(g["bud"][t]["nfl"], 1); g["bud"][t]["s"] = 2   # loss budget above the class count
    return g

def authorising(mod, tier, rng, must_have=None):
    pool = [S for S in range(256) if (mod.table[tier] >> S) & 1]
    S = rng.choice(pool) if pool and rng.random() < 0.8 else rng.randrange(256)
    if must_have is not None and rng.random() < 0.8: S |= 1 << must_have
    return S

def candidate_table(mod, tier, rng):
    iv = mod.interval(tier) if tier else None
    old = mod.table[tier]
    pts = [m for m in range(256) if (old >> m) & 1]
    r = rng.random()
    if iv and r < 0.35:     # a tightening that stays inside [Lo, U]
        keep = [m for m in pts if rng.random() < 0.6]
        return project(upclose(keep) | iv[0], mod.present) & old | (iv[0] & old)
    if iv and r < 0.55:     # a widening inside U
        extra = [m for m in range(256) if (iv[1] >> m) & 1 and rng.random() < 0.02]
        return project(old | upclose(extra), mod.present)
    if r < 0.65 and mod.present != 0xff:   # not projected: depends on an absent atom
        return old | upclose([rng.randrange(256)])
    if r < 0.70: return FULL
    if r < 0.73: return 0
    if r < 0.78: return rng.getrandbits(256)          # almost certainly not monotone
    return project(upclose([rng.randrange(256) for _ in range(rng.randint(1, 4))]), mod.present)

def random_message(mod, rng, stats):
    r = rng.random()
    if not mod.init:   # genesis was refused: every step must now answer STATE
        k = rng.choice([MSG_BOOT, MSG_PROPOSE_TX, MSG_HALT])
        return msg(k, action=rng.randrange(8), evidence=rng.randrange(256), atom=rng.randrange(8), digest=rng.randbytes(32) if k == MSG_BOOT else bytes(32))
    slots = [i for i in range(8) if (mod.present >> i) & 1 and mod.kinds[i] == 1] or [0]
    if r < 0.08:
        d = mod.committed if rng.random() < 0.6 else rng.randbytes(32)
        return msg(MSG_BOOT, digest=d)
    if r < 0.22:
        atom = rng.choice(slots) if rng.random() < 0.85 else rng.choice([8, 9, 32, 255, rng.randrange(256)])
        return msg(MSG_HALT, evidence=authorising(mod, 0, rng, atom % 8), atom=atom, bundle=rng.choice([0, 1, 2, 3, 3, 4, 15, 16, 17, 32, 200]))
    act = rng.choice([RESUME, ACTIVATE, ACTIVATE, TIGHTEN, TIGHTEN, EPOCH, RETIRE, INSTALL_TABLE, KEY_INSTALL, KEY_INSTALL, KEY_INSTALL, 0, 8, 9, 255])
    tier = rng.choice([1, 2, 3, 1, 2, 3, 0, 4, 5, 255])
    atom = rng.choice(slots) if rng.random() < 0.85 else rng.choice([8, 9, 32, 255, rng.randrange(256)])
    bundle = rng.choice([0, 1, 2, 3, 3, 4, 15, 16, 17, 32, 200])
    at = mod.action_tier[act] if act < N_ACT else 1
    S = authorising(mod, at, rng, atom % 8 if act == KEY_INSTALL else None)
    digest, table = bytes(32), 0
    if act == ACTIVATE: digest = rng.randbytes(32) if rng.random() < 0.5 else bytes([rng.randrange(256)]) * 32
    if act == KEY_INSTALL:
        r2 = rng.random()
        digest = (bytes([0x10 + rng.randrange(8)]) * 32 if r2 < 0.25 else rng.randbytes(32))
    if act in (TIGHTEN, INSTALL_TABLE):
        t_eff = tier if tier < 4 else 1
        table = candidate_table(mod, t_eff, rng)
    return msg(MSG_PROPOSE_TX, action=act, evidence=S, atom=atom, bundle=bundle, tier=tier, digest=digest, table=table)

def scenario(rng, n_steps, genesis=None):
    """Returns (input_lines, model_output_lines, stats)."""
    g = genesis or random_genesis(rng)
    mod, lines, out = Model(), [genesis_line(g)], []
    out.append(mod.line("G", mod.genesis(g)))
    for _ in range(n_steps):
        if mod.init and mod.seq != mod.acked and rng.random() < 0.85:
            lines.append(f"A {mod.seq:x}"); out.append(mod.line("A", mod.ack(mod.seq))); continue
        if rng.random() < 0.03:
            lines.append(f"A {rng.randrange(5):x}"); out.append(mod.line("A", mod.ack(int(lines[-1].split()[1], 16)))); continue
        m = random_message(mod, rng, None)
        lines.append(message_line(m))
        st, fx = mod.step(m)
        out.append(mod.line(lines[-1].split()[0], st, fx))
    return lines, out

def run_c(lines):
    r = subprocess.run(["./step_test", "run"], input="\n".join(lines) + "\n", capture_output=True, text=True)
    return r.stdout.split("\n")[:-1], r.returncode

def coverage(outs):
    seen_status, accepted = set(), set()
    for ln in outs:
        f = ln.split()
        st = int(f[1].split("=")[1]); seen_status.add(st)
        if st == OK and f[0] == "P": accepted.add("P")
    return seen_status

def main(n_scen=250, steps=60, seed=1337):
    rng = random.Random(seed)
    scenarios = []
    for i in range(n_scen):
        scenarios.append(scenario(rng, steps, (reference_genesis(i % 2 == 0) if i < 40 else remote_genesis() if i < 50 else None)))
    all_in = [ln for s in scenarios for ln in s[0]]
    all_out = [ln for s in scenarios for ln in s[1]]
    c_out, rc = run_c(all_in)
    mism = [i for i, (a, b) in enumerate(zip(all_out, c_out)) if a != b]
    mism_total = len(mism) + abs(len(all_out) - len(c_out)) + (rc != 0)
    for i in mism[:3]:
        print(f"  MISMATCH at line {i}: input {all_in[i][:100]}\n    python: {all_out[i]}\n    c     : {c_out[i]}")
    print(f"  {len(scenarios)} scenarios, {len(all_in)} lines compared, C vs Python mismatches={mism_total}")
    # coverage gate: the check must have exercised every status code and every accepted action
    seen = coverage(all_out)
    missing = [STATUS_NAMES[c] for c in sorted(STATUS_NAMES, reverse=True) if c not in seen]
    accepted = {ACTION_NAMES[int(l.split()[1], 16)] for l in all_in if l[0] == "P" and l[1] == " "} if False else None
    accepted_actions = set()
    cur = None
    for inp, o in zip(all_in, all_out):
        if inp[0] == "H" and " st=0 " in o: accepted_actions.add("HALT")
        if inp[0] == "P" and " st=0 " in o: accepted_actions.add(ACTION_NAMES[int(inp.split()[1], 16)])
        if inp[0] == "B" and " st=0 " in o: accepted_actions.add("BOOT")
    need = set(ACTION_NAMES) | {"BOOT"}
    print(f"  status codes seen: {len(seen)}/12; missing: {missing or 'none'}")
    print(f"  accepted actions seen: {sorted(accepted_actions)}; missing: {sorted(need - accepted_actions) or 'none'}")
    fails = mism_total + len(missing) + len(need - accepted_actions)
    # Profiles are data: the reference profiles must be admitted by the same kernel.
    for name, g in (("terrestrial recoverable", reference_genesis(False)), ("terrestrial fortress", reference_genesis(True)), ("remote", remote_genesis())):
        st = Model().genesis(g)
        print(f"  profile '{name}' admitted by genesis: {'yes' if st == OK else 'NO (' + STATUS_NAMES[st] + ')'}")
        fails += st != OK
    print(f"step_check failures={fails}")
    return fails

def emit_golden(path, seed=2026):
    rng = random.Random(seed)
    with open(path, "w") as f:
        f.write("# Waist v1 golden vectors. '>' lines are inputs for `step_test run`; '<' lines are the exact expected output.\n"
                "# Generated by models/step_check.py --emit-golden from models/step_model.py and confirmed equal to src/ac_step.c.\n"
                "# Any implementation of waist v1 must reproduce every '<' line. Do not regenerate to make a failing build pass.\n")
        for i in range(30):
            lines, out = scenario(rng, 24, reference_genesis(i % 2 == 0) if i < 6 else None)
            c_out, _ = run_c(lines)
            assert c_out == out, "refusing to write golden vectors the C build does not reproduce"
            for a, b in zip(lines, out): f.write(f"> {a}\n< {b}\n")
    print(f"wrote {path}")

def verify_golden(path):
    ins, exp = [], []
    for ln in open(path):
        if ln.startswith("> "): ins.append(ln[2:].rstrip("\n"))
        elif ln.startswith("< "): exp.append(ln[2:].rstrip("\n"))
    c_out, rc = run_c(ins)
    bad = sum(1 for a, b in zip(c_out, exp) if a != b) + abs(len(c_out) - len(exp)) + (rc != 0)
    print(f"  golden vectors: {len(ins)} lines, mismatches={bad}")
    print(f"step_check golden failures={bad}")
    return bad

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--emit-golden": emit_golden(sys.argv[2]); sys.exit(0)
    if len(sys.argv) == 3 and sys.argv[1] == "--verify-golden": sys.exit(1 if verify_golden(sys.argv[2]) else 0)
    sys.exit(1 if main() else 0)

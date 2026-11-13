#!/usr/bin/env python3
"""Generate the README diagrams as self-contained SVG files in docs/assets/.

Reproducible: `python3 scripts/make_diagrams.py` rewrites every file; `--check` fails if the committed
files differ from what the script would write (so the diagrams cannot drift from this source).
Standard library only. Every diagram uses solid backgrounds, so it reads on light and dark pages.
Facts shown here come from the repository (status words follow docs/validation/validation-gates.md).
"""
import os, sys
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "assets")
FONT = "Inter, 'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, Menlo, monospace"
BG0, BG1 = "#0b1020", "#151b33"
CYAN, VIOLET, GREEN, AMBER, ROSE, BLUE, SLATE = "#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#fb7185", "#60a5fa", "#94a3b8"
INK, MUTED = "#e6edf7", "#9aa7c2"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title, self.parts = w, h, title, []

    def add(self, s): self.parts.append(s)

    def text(self, x, y, s, size=14, fill=INK, weight=400, anchor="start", mono=False, opacity=1):
        fam = MONO if mono else FONT
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
                 f'fill="{fill}" text-anchor="{anchor}" opacity="{opacity}">{escape(s)}</text>')

    def box(self, x, y, w, h, color, title, sub=None, r=14, filled=True, title_size=15, sub_size=12, sub2=None):
        fill = f'url(#g_{color[1:]})' if filled else "none"
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{color}" '
                 f'stroke-width="1.6" filter="url(#shadow)"/>')
        cx = x + w / 2
        if sub is None:
            self.text(cx, y + h / 2 + 5, title, title_size, INK, 700, "middle")
        else:
            ty = y + h / 2 - (8 if sub2 is None else 14)
            self.text(cx, ty, title, title_size, INK, 700, "middle")
            self.text(cx, ty + 20, sub, sub_size, MUTED, 400, "middle")
            if sub2: self.text(cx, ty + 38, sub2, sub_size, MUTED, 400, "middle")

    def pill(self, x, y, w, h, color, label, size=12):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{color}" opacity="0.18"/>')
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="none" stroke="{color}" stroke-width="1.3"/>')
        self.text(x + w / 2, y + h / 2 + size * 0.35, label, size, color, 700, "middle")

    def arrow(self, x1, y1, x2, y2, color=SLATE, dash=False, label=None, curve=0, lw=2):
        d = f'M{x1},{y1} L{x2},{y2}' if not curve else f'M{x1},{y1} Q{(x1+x2)/2},{(y1+y2)/2 + curve} {x2},{y2}'
        da = ' stroke-dasharray="6 5"' if dash else ''
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{lw}"{da} marker-end="url(#arr_{color[1:]})"/>')
        if label:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 - 8 + curve / 2, label, 11, MUTED, 400, "middle")

    def render(self):
        colors = [CYAN, VIOLET, GREEN, AMBER, ROSE, BLUE, SLATE]
        defs = ['<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
                '<feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000" flood-opacity="0.35"/></filter>',
                f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/>'
                f'<stop offset="1" stop-color="{BG1}"/></linearGradient>']
        for c in colors:
            defs.append(f'<linearGradient id="g_{c[1:]}" x1="0" y1="0" x2="0" y2="1">'
                        f'<stop offset="0" stop-color="{c}" stop-opacity="0.30"/>'
                        f'<stop offset="1" stop-color="{c}" stop-opacity="0.08"/></linearGradient>')
            defs.append(f'<marker id="arr_{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-label="{escape(self.title)}"><title>{escape(self.title)}</title><defs>{"".join(defs)}</defs>'
                f'<rect width="{self.w}" height="{self.h}" rx="20" fill="url(#bg)"/>')
        return head + "".join(self.parts) + "</svg>\n"


def dots(s, w, h, step=34):
    s.add(f'<defs><pattern id="dots" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
          f'<circle cx="{step/2}" cy="{step/2}" r="1.1" fill="#ffffff" opacity="0.06"/></pattern></defs>'
          f'<rect width="{w}" height="{h}" rx="20" fill="url(#dots)"/>')


def hero():
    s = Svg(1200, 300, "KRYPTARA: a governed-change kernel")
    dots(s, 1200, 300)
    # eight evidence atoms on a ring, three kinds: SIG, PRES, WIT
    import math
    cx, cy, R = 1010, 150, 92
    kinds = [CYAN, CYAN, CYAN, VIOLET, VIOLET, GREEN, GREEN, GREEN]
    pts = [(cx + R * math.cos(math.radians(-90 + i * 45)), cy + R * math.sin(math.radians(-90 + i * 45))) for i in range(8)]
    for i, (x, y) in enumerate(pts):
        for j in range(i + 1, 8):
            if (i + j) % 3 == 0:
                s.add(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{pts[j][0]:.1f}" y2="{pts[j][1]:.1f}" stroke="{SLATE}" stroke-width="1" opacity="0.35"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#g_{AMBER[1:]})" stroke="{AMBER}" stroke-width="1.6" filter="url(#shadow)"/>')
    s.text(cx, cy + 5, "f(S)", 16, INK, 700, "middle", mono=True)
    for (x, y), c in zip(pts, kinds):
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{BG1}"/>')
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{c}" opacity="0.25"/>')
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="none" stroke="{c}" stroke-width="2"/>')
    s.text(90, 118, "KRYPTARA", 76, INK, 800)
    s.add(f'<rect x="90" y="134" width="150" height="5" rx="2.5" fill="{CYAN}"/><rect x="246" y="134" width="70" height="5" rx="2.5" fill="{VIOLET}"/>'
          f'<rect x="322" y="134" width="40" height="5" rx="2.5" fill="{GREEN}"/>')
    s.text(90, 178, "A governed-change kernel for devices and artefacts", 24, INK, 600)
    s.text(90, 210, "that outlive their makers, their custodians and their cryptography.", 24, INK, 600)
    x = 90
    for label, c, w in [("Apache-2.0", BLUE, 122), ("C99 · pure step", CYAN, 150), ("research · pre-Phase-0", AMBER, 200), ("claims carry evidence classes", GREEN, 236)]:
        s.pill(x, 238, w, 30, c, label); x += w + 12
    return s


def architecture():
    s = Svg(1200, 640, "Architecture: an hourglass around a frozen waist")
    dots(s, 1200, 640)
    s.text(60, 56, "Architecture", 28, INK, 800)
    s.text(60, 82, "Many tools above, many ports below, one small frozen interface in the middle.", 15, MUTED)
    # L4/L2 top band
    s.pill(60, 112, 120, 26, BLUE, "L4 · L2  HOST")
    s.box(60, 148, 270, 74, BLUE, "Policy lint", "models/lint.py · bounds before provisioning", sub_size=11)
    s.box(350, 148, 270, 74, BLUE, "Ceremony tool · simulators", "scripts/ac_ceremony.py · simulations/", sub_size=11)
    s.box(640, 148, 270, 74, BLUE, "Formats", "CBOR projection · Merkle proofs", sub_size=11)
    s.box(930, 148, 210, 74, SLATE, "Fleet tools", "toy models today", sub_size=11, filled=True)
    # funnel
    s.add(f'<path d="M60,246 L1140,246 L800,318 L400,318 Z" fill="{VIOLET}" opacity="0.12"/>')
    s.add(f'<path d="M60,246 L400,318 M1140,246 L800,318" stroke="{VIOLET}" stroke-width="1.5" opacity="0.6" fill="none"/>')
    s.text(600, 276, "validated, fixed-size projection", 13, MUTED, 400, "middle")
    # waist
    s.add(f'<rect x="400" y="318" width="400" height="104" rx="18" fill="url(#g_{AMBER[1:]})" stroke="{AMBER}" stroke-width="2.4" filter="url(#shadow)"/>')
    s.text(600, 340, "THE WAIST", 11, AMBER, 800, "middle")
    s.text(600, 366, "ac_step(ctx, msg) → status + intents", 16, INK, 700, "middle", mono=True)
    s.text(600, 388, "pure · no I/O · no allocation · no clock · no recursion", 12.5, MUTED, 400, "middle")
    s.text(600, 408, "src/ac_step.c · src/ac_waist.h · src/waist-v1.abi", 11.5, SLATE, 400, "middle", mono=True)
    # inside kernel
    s.box(120, 330, 250, 80, VIOLET, "Admission", "src/policy8.c · interval [Lo, U]", sub_size=11.5)
    s.box(830, 330, 250, 80, VIOLET, "Tier engine · chain · image", "src/kernel.c", sub_size=11.5)
    s.arrow(370, 370, 400, 370, VIOLET, lw=2.4); s.arrow(830, 370, 800, 370, VIOLET, lw=2.4)
    s.text(60, 346, "L0", 13, VIOLET, 800); s.text(60, 364, "locked", 11, MUTED); s.text(60, 380, "kernel", 11, MUTED)
    # bottom: evidence + platform
    s.add(f'<path d="M480,446 L720,446 L1140,520 L60,520 Z" fill="{GREEN}" opacity="0.10"/>')
    s.arrow(250, 540, 500, 424, GREEN)
    s.arrow(680, 424, 590, 540, ROSE, dash=True)
    s.text(340, 478, "evidence in (pre-verified)", 11.5, GREEN, 700, "end")
    s.text(660, 478, "intents out", 11.5, ROSE, 700)
    s.box(60, 540, 300, 66, GREEN, "W2 · Evidence verification", "LMS · SHA-256 prototypes (98 vectors)", sub_size=11)
    s.box(390, 540, 330, 66, ROSE, "W3 · Platform · NV journal", "not built · power-cut sweep on prototype", sub_size=11, filled=True)
    s.box(750, 540, 390, 66, SLATE, "Ports: Cortex-M0+, M33, Rust twin", "not built · Rust twin never run", sub_size=11)
    s.text(62, 530, "L1 · PROVIDERS AND PORTS", 11, GREEN, 700)
    s.text(1140, 478, "NV_WRITE_SNAPSHOT · BOOT_IMAGE · REJECT", 11.5, MUTED, 400, "end")
    return s


def step_flow():
    s = Svg(1200, 360, "One step with a fixed check order")
    dots(s, 1200, 360)
    s.text(60, 52, "One step, fixed check order", 28, INK, 800)
    s.text(60, 78, "Nothing changes before the apply step, so a rejected message leaves the context byte-identical.", 15, MUTED)
    steps = [("1", "Initialised?", "genesis done", CYAN), ("2", "Idle?", "no pending ack", CYAN), ("3", "Fields valid?", "slots · tiers · bounds", CYAN),
             ("4", "Authority", "evidence authorises\nthe action at its tier", VIOLET), ("5", "State · budget\nadmission", "interval [Lo, U]\ntightening", VIOLET), ("6", "Apply", "one mutator", GREEN)]
    w, gap, x0, y0, h = 160, 28, 60, 118, 110
    for i, (n, t, sub, c) in enumerate(steps):
        x = x0 + i * (w + gap)
        s.add(f'<rect x="{x}" y="{y0}" width="{w}" height="{h}" rx="14" fill="url(#g_{c[1:]})" stroke="{c}" stroke-width="1.6" filter="url(#shadow)"/>')
        s.add(f'<circle cx="{x+22}" cy="{y0+22}" r="14" fill="{c}"/>'); s.text(x + 22, y0 + 27, n, 14, BG0, 800, "middle")
        tl = t.split("\n"); sl = sub.split("\n")
        for k, line in enumerate(tl): s.text(x + w / 2 + 16, y0 + 34 + k * 17, line, 14.5, INK, 700, "middle")
        for k, line in enumerate(sl): s.text(x + w / 2, y0 + 70 + k * 15 + (0 if len(tl) == 1 else 4), line, 11.5, MUTED, 400, "middle")
        if i < len(steps) - 1: s.arrow(x + w, y0 + h / 2, x + w + gap, y0 + h / 2, SLATE, lw=2.2)
        if i < 5:
            s.add(f'<line x1="{x + w/2}" y1="{y0+h}" x2="{x + w/2}" y2="268" stroke="{ROSE}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    for i in range(5):
        x = x0 + i * (w + gap)
    s.add(f'<line x1="{x0 + w/2}" y1="268" x2="{x0 + 4*(w+gap) + w/2}" y2="268" stroke="{ROSE}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    s.pill(x0, 290, 330, 30, ROSE, "any failure → one REJECT intent · state untouched", 12)
    xa = x0 + 5 * (w + gap)
    s.arrow(xa + w / 2, y0 + h, xa + w / 2, y0 + h + 40, GREEN, lw=2.2)
    s.pill(xa - 20, 290, 200, 30, GREEN, "NV_WRITE_SNAPSHOT → ac_ack", 12)
    return s


def tiers():
    s = Svg(1200, 440, "Tiers and who may authorise what")
    dots(s, 1200, 440)
    s.text(60, 52, "Tiers: who may authorise what", 28, INK, 800)
    s.text(60, 78, "Each tier is a monotone table; each safety and liveness claim is a lint-checked interval.", 15, MUTED)
    rows = [("T0 · HALT", "any single key or presence", "stops staged effects", ROSE, 135),
            ("T1 · OPERATE", "1-safe · live after 1 loss", "day-to-day change", CYAN, 210),
            ("T2 · CONST", "2-safe", "changes to the key set and tables", VIOLET, 285),
            ("T2 · RECOVERY", "1-safe · live after any 2 losses", "except both hash families", GREEN, 360)]
    for i, (t, a, b, c, y) in enumerate(rows):
        inset = i * 36
        s.add(f'<rect x="{60+inset}" y="{y-26}" width="{1080-2*inset}" height="62" rx="14" fill="url(#g_{c[1:]})" stroke="{c}" stroke-width="1.6" filter="url(#shadow)"/>')
        s.text(84 + inset, y + 2, t, 18, INK, 800); s.text(84 + inset, y + 24, b, 12, MUTED)
        s.text(1116 - inset, y + 8, a, 14, c, 700, "end")
    s.text(600, 424, "Re-keying lives in exactly one T2 tier per profile (REQ-TIER-02, machine-checked).", 12, SLATE, 400, "middle")
    return s


def verification():
    s = Svg(1200, 460, "Verification: four artefacts per behaviour")
    dots(s, 1200, 460)
    s.text(60, 52, "Four artefacts per behaviour", 28, INK, 800)
    s.text(60, 78, "A behaviour is done only when prose, an independent model, the C code and golden vectors agree.", 15, MUTED)
    s.box(60, 130, 230, 90, BLUE, "Prose", "requirements · ADRs", sub_size=12)
    s.box(60, 270, 230, 90, VIOLET, "Independent model", "models/step_model.py", sub_size=12)
    s.box(480, 200, 230, 90, AMBER, "C implementation", "src/ac_step.c", sub_size=12)
    s.box(900, 130, 240, 90, GREEN, "Golden vectors", "750 input lines · tests/vectors/", sub_size=12)
    s.box(900, 270, 240, 90, ROSE, "Rust twin · re-implementation", "not run", sub_size=12)
    s.arrow(290, 175, 480, 235, SLATE); s.arrow(290, 315, 480, 260, SLATE)
    s.arrow(710, 235, 900, 175, SLATE); s.arrow(710, 260, 900, 315, ROSE, dash=True)
    s.text(385, 352, "differential: 17,000+ random lines", 11.5, MUTED, 400, "middle")
    items = [("arch_check R1–R8", CYAN), ("mutation: 122/122", VIOLET), ("fuzz · ASan · UBSan", GREEN), ("TLA+ · Z3 · exhaustive n≤4", AMBER), ("health check · 14 checks", BLUE)]
    x = 60
    for label, c in items:
        w = 20 + len(label) * 8.2
        s.pill(x, 400, w, 32, c, label, 12.5); x += w + 12
    return s


def interval():
    s = Svg(1200, 400, "The interval theorem")
    dots(s, 1200, 400)
    s.text(60, 52, "Interval theorem", 28, INK, 800)
    s.text(60, 78, "Given a fault structure, the safe-and-live policies are exactly the monotone tables between Lo and U.", 15, MUTED)
    y = 190
    s.add(f'<rect x="60" y="{y}" width="1080" height="46" rx="23" fill="{SLATE}" opacity="0.15"/>')
    s.add(f'<rect x="300" y="{y}" width="640" height="46" rx="23" fill="url(#g_{GREEN[1:]})" stroke="{GREEN}" stroke-width="2"/>')
    s.text(620, y + 29, "safe  and  live:   Lo  ≤  f  ≤  U", 18, INK, 700, "middle", mono=True)
    s.add(f'<path d="M60,{y-22} L300,{y-22}" stroke="{ROSE}" stroke-width="2" marker-end="url(#arr_{ROSE[1:]})"/>')
    s.text(180, y - 32, "too weak: loses liveness", 13, ROSE, 700, "middle")
    s.add(f'<path d="M1140,{y-22} L940,{y-22}" stroke="{ROSE}" stroke-width="2" marker-end="url(#arr_{ROSE[1:]})"/>')
    s.text(1040, y - 32, "too strong: one fault authorises", 13, ROSE, 700, "middle")
    for x, lab in [(300, "Lo"), (940, "U")]:
        s.add(f'<circle cx="{x}" cy="{y+23}" r="9" fill="{AMBER}" stroke="{BG0}" stroke-width="3"/>')
        s.text(x, y + 74, lab, 17, AMBER, 800, "middle", mono=True)
    s.box(60, 290, 330, 70, CYAN, "Class-count law", "k ≥ t + s + 1", sub_size=14, title_size=14)
    s.box(435, 290, 330, 70, VIOLET, "Admission (REQ-ADM-01)", "table in [Lo, U] and tightening", sub_size=12, title_size=14)
    s.box(810, 290, 330, 70, AMBER, "Recovery is an attack path", "every recovery route is priced", sub_size=12, title_size=14)
    return s


def roadmap():
    s = Svg(1200, 400, "Roadmap")
    dots(s, 1200, 400)
    s.text(60, 52, "Roadmap to the T0 freeze", 28, INK, 800)
    s.text(60, 78, "Each slice has an exit test; status words follow the validation gates.", 15, MUTED)
    items = [("1", "Pure step", "admission · tiers · halt\nchain · snapshots", "DONE · host", GREEN),
             ("2", "Evidence + labels", "verification layer\nclass-dead · projection", "next", AMBER),
             ("3", "Record + publicity", "catch-up · receipts\nstale-device bound", "planned", SLATE),
             ("4", "Platform + journal", "W3 · boot recovery\npower-cut sweep", "planned", SLATE),
             ("5", "Ports + proof", "M0+/M33 · Rust twin\nproofs · review", "planned", SLATE)]
    s.add(f'<line x1="120" y1="150" x2="1080" y2="150" stroke="{SLATE}" stroke-width="3" opacity="0.4"/>')
    s.add(f'<line x1="120" y1="150" x2="250" y2="150" stroke="{GREEN}" stroke-width="3"/>')
    w, gap = 190, 32
    for i, (n, t, sub, st, c) in enumerate(items):
        x = 60 + i * (w + gap) - 0
        cx = x + w / 2
        s.add(f'<circle cx="{cx}" cy="150" r="17" fill="{c}" stroke="{BG0}" stroke-width="4"/>'); s.text(cx, 156, n, 15, BG0, 800, "middle")
        s.add(f'<rect x="{x}" y="190" width="{w}" height="130" rx="14" fill="url(#g_{c[1:]})" stroke="{c}" stroke-width="1.6" filter="url(#shadow)"/>')
        s.text(cx, 220, t, 15, INK, 700, "middle")
        for k, line in enumerate(sub.split("\n")): s.text(cx, 248 + k * 17, line, 12, MUTED, 400, "middle")
        s.pill(x + 30, 284, w - 60, 24, c, st, 11)
    s.add(f'<path d="M1150,150 m-18,-22 l0,44 l36,-22 z" fill="{AMBER}"/>')
    s.text(1138, 352, "T0 freeze", 12, AMBER, 700, "end")
    s.text(60, 372, "Also open: GATE-07 size verdict (CI), GATE-08 exhaustive run, silicon gates, external review.", 12, SLATE)
    return s


FILES = {"hero.svg": hero, "architecture.svg": architecture, "step-flow.svg": step_flow, "tiers.svg": tiers,
         "verification.svg": verification, "interval.svg": interval, "roadmap.svg": roadmap}


def main():
    check = "--check" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for name, fn in FILES.items():
        text = fn().render()
        path = os.path.join(OUT, name)
        if check:
            same = os.path.exists(path) and open(path).read() == text
            print(f"  {'ok  ' if same else 'DIFF'} {name}")
            bad += not same
        else:
            open(path, "w").write(text); print(f"  wrote docs/assets/{name} ({len(text)} B)")
    if check: print(f"diagrams failures={bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)

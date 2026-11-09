# Reference policy lint: labelled evidence atoms -> fault structures -> interval [Lo, U] -> admission. [C]
# Fault sets are generated from labels (one fault = one label value fails), never hand-written.
import itertools
from interval import upper, lower

N = 8
class Atom:
    def __init__(s, name, kind, labels): s.name, s.kind, s.labels = name, kind, set(labels)

def structures(atoms, present, t, s, comp_labels=None, loss_labels=None, exclude_loss=(),
               loss_kinds=("SIG",), exclude_comp_combo=(), exclude_loss_combo=(), site_controller=None):
    """Return (Ac, Al) for t simultaneous compromise faults and s simultaneous loss faults.
    - each SIG/PRES atom is a singleton fault; each label value is a fault (all atoms carrying it)
    - exposure atoms (kind WIT) are free to the attacker: added to every compromise set
    - absent atoms are permanently lost: added to every loss set
    - site_controller (REQ-LINT-03): name of a custody group label (e.g. "group:OWN") declared to run
      the site. F-R2-04: compromising that group's atoms is modelled as also yielding PRES (correlated
      presence), since a site-controller insider needs no separate presence fault."""
    idx = {a.name: i for i, a in enumerate(atoms)}
    absent = 0
    for i, a in enumerate(atoms):
        if a.name not in present: absent |= 1 << i
    expo = sum(1 << i for i, a in enumerate(atoms) if a.kind == "WIT" and a.name in present)
    pres_bit = sum(1 << i for i, a in enumerate(atoms) if a.kind == "PRES" and a.name in present)
    ctrl_bit = sum(1 << i for i, a in enumerate(atoms)
                   if a.name in present and site_controller in a.labels) if site_controller else 0
    def faults(kind_filter, label_filter):
        F = {}
        for i, a in enumerate(atoms):
            if a.name not in present: continue
            if a.kind in kind_filter: F[f"atom:{a.name}"] = 1 << i
            for l in a.labels:
                if label_filter is None or l.split(":")[0] in label_filter:
                    F[l] = F.get(l, 0) | (1 << i)
        return F
    Fc = faults(("SIG", "PRES"), comp_labels)
    Fl = faults(loss_kinds, loss_labels)
    for k in exclude_loss: Fl.pop(k, None)
    def u(c):
        r = 0
        for x in c: r |= x
        return r
    def ok(combo, names, excl):
        return not any(set(x) <= set(names) for x in excl)
    free = expo | absent   # F-R2-01: exposure AND absent atoms are always available to the attacker
    def with_corr(x):      # REQ-LINT-03: site-controller compromise correlates with presence
        return x | pres_bit if (ctrl_bit and (x & ctrl_bit)) else x
    Ac = sorted({with_corr(u([Fc[k] for k in c]) | free) for c in itertools.combinations(Fc, t)
                 if ok(c, c, exclude_comp_combo)}) if t else [with_corr(free)]
    Al = sorted({u([Fl[k] for k in c]) | absent for c in itertools.combinations(Fl, s)
                 if ok(c, c, exclude_loss_combo)}) if s else [absent]
    return Ac, Al, Fc, Fl

def present_mask(atoms, present):
    return sum(1 << i for i, a in enumerate(atoms) if a.name in present)

def project(table, mask):
    """Canonical form: f'(S) = f(S & mask). Monotone if f is. Tables must equal their projection (REQ-ADM-05)."""
    t = 0
    for m in range(1 << N):
        if (table >> (m & mask)) & 1: t |= 1 << m
    return t

def lint(table, atoms, present, t, s, **kw):
    table = project(table, present_mask(atoms, present))
    Ac, Al, Fc, Fl = structures(atoms, present, t, s, **kw)
    U, Lo = upper(N, Ac), lower(N, Al)
    return dict(safe=(table & ~U) == 0, live=(Lo & ~table) == 0, exists=(Lo & ~U) == 0, U=U, Lo=Lo)

def site_controller_guard(table, atoms, present, t, s, group_label, **kw):
    """REQ-PRES-02: 'A site-controller group declared at T2 MUST NOT satisfy presence for its own
    recovery tier in the default profile.' Lint-level guard: re-run `lint` with that group declared
    as the correlated-presence site controller (REQ-LINT-03's `site_controller=`) and REJECT the
    declaration (return False = violation) if the table stops being safe-and-live under that
    assumption. This is a procurement-time check on a profile declaration, not a device-time check;
    the device has no way to know who "controls the site" and REQ-PRES-01 already requires presence
    sampling to be firmware-independent, so there is nothing for the locked stage to enforce here."""
    r = lint(table, atoms, present, t, s, site_controller=group_label, **kw)
    return r["exists"] and r["safe"] and r["live"]

def tbl(pred):
    t = 0
    for m in range(1 << N):
        if pred(m): t |= 1 << m
    return t

# ---- the reference 8-atom layout --------------------------------------------------------------
ATOMS = [Atom("OEM1", "SIG", ["group:OEM", "family:H1"]), Atom("OEM2", "SIG", ["group:OEM", "family:H2"]),
         Atom("OWN1", "SIG", ["group:OWN", "family:H1"]), Atom("OWN2", "SIG", ["group:OWN", "family:H2"]),
         Atom("ESC1", "SIG", ["group:ESC", "family:H1"]), Atom("ESC2", "SIG", ["group:ESC", "family:H2"]),
         Atom("PRES", "PRES", ["site:S"]), Atom("WIT", "WIT", ["log:L"])]
GROUPS = [0b11, 0b1100, 0b110000]; FAMS = [0b010101, 0b101010]; SITE = 1 << 6; LOG = 1 << 7
def C(m): return sum(1 for g in GROUPS if m & g)
def F(m): return sum(1 for f in FAMS if m & f)
def K(m): return bin(m & 0b111111).count("1")
def p(m): return bool(m & SITE)
def w(m): return bool(m & LOG)

HALT     = tbl(lambda m: K(m) >= 1)                                   # availability-only, exempt from safety
OPERATE  = tbl(lambda m: (w(m) and C(m) >= 2 and (F(m) >= 2 or p(m))) or (p(m) and C(m) >= 2 and F(m) >= 2))
CONST    = tbl(lambda m: p(m) and F(m) >= 2 and ((C(m) >= 2 and w(m)) or C(m) >= 3))
RECOVERY = tbl(lambda m: p(m) and K(m) >= 2 and (w(m) or C(m) >= 2))
REMOTE_OPERATE = tbl(lambda m: w(m) and C(m) >= 2 and F(m) >= 2)
REMOTE_CONST   = tbl(lambda m: w(m) and C(m) >= 3 and F(m) >= 2)
NANO_OPERATE   = tbl(lambda m: w(m) and C(m) >= 2)

ALL = {a.name for a in ATOMS}
REMOTE = ALL - {"PRES"}
NANO = {"OEM1", "OWN1", "ESC1", "PRES", "WIT"}

REMOTE_CONST2 = tbl(lambda m: w(m) and C(m) >= 3
                   and sum(1 for g in GROUPS if m & g & FAMS[0]) >= 2 and sum(1 for g in GROUPS if m & g & FAMS[1]) >= 2)
NANO_PRES_OPERATE = tbl(lambda m: p(m) and C(m) >= 2)
BOTHF = [("family:H1", "family:H2")]

if __name__ == "__main__":
    rows = [
     # title, table, present, t, s, kwargs
     ("TERRESTRIAL dual+presence+publicity", None, None, None, None, None),
     ("OPERATE : 1-safe (key,group,family,site); live vs 1 loss (key,group,family,site)", OPERATE, ALL, 1, 1,
        dict(loss_kinds=("SIG", "PRES"))),
     ("CONST   : 2-safe (all pairs incl. both families); live vs 1 loss (key,group)", CONST, ALL, 2, 1,
        dict(loss_labels={"group"})),
     ("RECOVERY: 1-safe; live vs any 2 losses (key,group,family) except both families", RECOVERY, ALL, 1, 2,
        dict(loss_labels={"group", "family"}, exclude_loss_combo=BOTHF)),
     ("HALT    : (exempt) shown for completeness: 1-safe?", HALT, ALL, 1, 0, dict()),
     ("OPERATE w/ OWN as site controller (REQ-LINT-03, F-R2-04): 1-safe?", OPERATE, ALL, 1, 1,
        dict(loss_kinds=("SIG", "PRES"), site_controller="group:OWN")),
     ("REMOTE (no presence)", None, None, None, None, None),
     ("OPERATE : 1-safe incl. family; live vs 1 loss (key,group)", REMOTE_OPERATE, REMOTE, 1, 1,
        dict(loss_labels={"group"})),
     ("CONST   : 2-safe except both families; live vs 1 key loss", REMOTE_CONST2, REMOTE, 2, 1,
        dict(loss_labels=set(), exclude_comp_combo=BOTHF)),
     ("NANO (one hash family)", None, None, None, None, None),
     ("OPERATE : 1-safe excl. hash break; live vs 1 loss (key,group)", NANO_OPERATE, NANO, 1, 1,
        dict(comp_labels={"group", "site"}, loss_labels={"group"})),
     ("OPERATE+P: 1-safe incl. hash break; live vs 1 loss (key,group)", NANO_PRES_OPERATE, NANO, 1, 1,
        dict(loss_labels={"group"})),
    ]
    for title, table, present, t, s_, kw in rows:
        if table is None: print(title); continue
        r = lint(table, ATOMS, present, t, s_, **kw)
        print(f"  {title:86s} safe={r['safe']!s:5s} live={r['live']!s:5s} nonempty={r['exists']}")
    print("IMPOSSIBILITY (interval empty for every policy):")
    imp = [
     ("terrestrial: 1-safe & live vs loss of both families (only presence left)", ALL, 1, 1,
        dict(loss_labels={"family"}), True),
     ("terrestrial: 2-safe & live vs 1 family loss", ALL, 2, 1, dict(loss_labels={"family"}), False),
     ("terrestrial: 2-safe & live vs site loss", ALL, 2, 1, dict(loss_kinds=("PRES",), loss_labels=set()), False),
     ("remote: 1-safe & live vs 1 family loss", REMOTE, 1, 1, dict(loss_labels={"family"}), False),
     ("remote: 2-safe (any pair) & any nonzero policy", REMOTE, 2, 0, dict(), False),
     ("remote: 1-safe & live vs 2 group losses", REMOTE, 1, 2, dict(loss_labels={"group"}), False),
     ("nano without presence: 1-safe incl. hash break & any nonzero policy", NANO - {"PRES"}, 1, 0, dict(), False),
     ("nano with presence: 1-safe incl. hash & live vs hash loss", NANO, 1, 1, dict(loss_labels={"family"}), False),
    ]
    for title, present, t, s_, kw, both in imp:
        Ac, Al, *_ = structures(ATOMS, present, t, s_, **kw)
        if both: Al = [FAMS[0] | FAMS[1]]
        U, Lo = upper(N, Ac), lower(N, Al)
        print(f"  {title:86s} {'POSSIBLE' if (Lo & ~U) == 0 and U else 'IMPOSSIBLE'}")
    for n_, t_ in [("HALT", HALT), ("OPERATE", OPERATE), ("CONST", CONST), ("RECOVERY", RECOVERY),
                   ("R_OPERATE", REMOTE_OPERATE), ("R_CONST", REMOTE_CONST2)]:
        print(f"  {n_:9s} " + " ".join(f"{(t_ >> (64*i)) & ((1<<64)-1):016x}" for i in range(4)) + f"  popcount={bin(t_).count('1')}")

    # REQ-PRES-02: "A site-controller group declared at T2 MUST NOT satisfy presence for its own
    # recovery tier in the default profile." For the default terrestrial profile, RECOVERY and
    # CONST must each REJECT (site_controller_guard -> False) every group as a candidate site
    # controller, i.e. none of OEM/OWN/ESC may be declared to run the site without breaking T2's
    # safe-and-live claim. A guard returning True (profile stays safe+live) for any group is the
    # violation this requirement exists to catch.
    print("\nREQ-PRES-02 check (no custody group may be the declared site controller at T2):")
    req_pres_02_failures = 0
    T2_PROFILES = [
        ("RECOVERY", RECOVERY, ALL, 1, 2, dict(loss_labels={"group", "family"}, exclude_loss_combo=BOTHF)),
        ("CONST", CONST, ALL, 2, 1, dict(loss_labels={"group"})),
    ]
    for tier_name, table, present, t, s_, kw in T2_PROFILES:
        for grp in ("group:OEM", "group:OWN", "group:ESC"):
            ok = site_controller_guard(table, ATOMS, present, t, s_, grp, **kw)
            print(f"  {tier_name:8s} with {grp:12s} as site controller: "
                  f"{'VIOLATION (stays safe+live, i.e. that group alone could run the site)' if ok else 'rejected (correctly unsafe)'}")
            if ok:
                req_pres_02_failures += 1
    print(f"REQ-PRES-02 failures={req_pres_02_failures}")
    if req_pres_02_failures:
        raise SystemExit(1)

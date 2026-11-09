#!/usr/bin/env python3
"""Migration twin prototype: discrete-event simulation of a staged, dormant-then-activate
update with persisters, partitions and a faulty update. stdlib only. Time unit = days.
All parameters are ASSUMPTIONS (see blueprint F.6); results are model output [C], not measurements.
Usage: python3 migration_twin.py [n_runs]
"""
import heapq, random, statistics, sys, itertools
from dataclasses import dataclass, field

@dataclass
class Params:
    n_sites: int = 60
    devs_per_site: tuple = (20, 60)
    bad_site_share: float = 0.20      # sites whose hardware mix includes the faulty revision heavily
    bad_mix_in_bad_site: float = 0.70
    bad_mix_elsewhere: float = 0.03
    faulty_update: bool = True
    latent_share: float = 0.30        # share of faults that only manifest latent_delay days after activation
    latent_delay: float = 14.0
    rollback_ok: float = 0.85         # A/B rollback restores LKG; else device is out (truck roll)
    report_delay: float = 1.0         # device->controller, only if site online
    window_periods: tuple = (30, 90); window_p30: float = 0.7
    hold_down: float = 7.0            # min days between delivery and first activation
    partition_prob: float = 0.15; partition_len: tuple = (20, 120); partition_start_max: float = 200
    island_sites: int = 3             # permanently offline (sneakernet only), never reached
    wave_fracs: tuple = (0.03, 0.12, 0.30, 0.55); wave_gap: float = 21.0
    horizon: float = 365.0
    # strategy knobs
    staged: bool = True
    halt: bool = True; halt_min_n: int = 15; halt_threshold: float = 0.05
    persister_frac: float = 0.0; persister_release_after: float = 60.0   # days after last wave, if no halt
    lease: float = 0.0                # >0: site must have heard controller within lease days before activating
    stratified_canary: bool = False

STRATEGIES = {
 "A big-bang (all sites, no halt)":        dict(staged=False, halt=False),
 "B staged waves, no halt":                dict(halt=False),
 "C staged + auto-halt":                   dict(),
 "D staged + halt + 5% persisters":        dict(persister_frac=0.05),
 "E D + activation lease 45d":             dict(persister_frac=0.05, lease=45.0),
 "F E + stratified canary":                dict(persister_frac=0.05, lease=45.0, stratified_canary=True),
}

class Sim:
    def __init__(s, p: Params, seed: int):
        s.p = p; r = s.r = random.Random(seed); s.t = 0.0; s.q = []; s.cnt = itertools.count()
        s.sites = []
        for i in range(p.n_sites):
            bad = r.random() < p.bad_site_share
            mix = p.bad_mix_in_bad_site if bad else p.bad_mix_elsewhere
            n = r.randint(*p.devs_per_site)
            devs = [dict(bad=r.random() < mix, persister=(r.random() < p.persister_frac), state="old") for _ in range(n)]
            per = 30 if r.random() < p.window_p30 else 90
            site = dict(id=i, devs=devs, per=per, phase=r.uniform(0, per), staged=False, deliver_t=None, cancelled=False,
                        last_heard=-1e9, online=True, island=False, bad=bad, pending_reports=[], activated_at=None)
            if r.random() < p.partition_prob:
                a = r.uniform(0, p.partition_start_max); b = a + r.uniform(*p.partition_len)
                s.at(a, "part_start", i); s.at(b, "part_end", i)
            s.sites.append(site)
        for k in r.sample(range(p.n_sites), p.island_sites):
            s.sites[k]["island"] = True; s.sites[k]["online"] = False
        # controller state
        s.halted = False; s.halt_t = None; s.rep_act = 0; s.rep_fail = 0; s.released = []
        s.migrated_t = []   # (t, count migrated) for exposure integral
        s.events_fail = 0
        s.plan_waves()

    def at(s, t, kind, *a):
        heapq.heappush(s.q, (t, next(s.cnt), kind, a))

    def plan_waves(s):
        p = s.p; order = [x for x in s.sites if not x["island"]]
        s.r.shuffle(order)
        if not p.staged:
            waves = [order]
        else:
            sizes = [max(1, round(f * len(order))) for f in p.wave_fracs]
            if p.stratified_canary:   # inventory knows hardware mix class: one canary from each stratum
                bads = [x for x in order if x["bad"]]; goods = [x for x in order if not x["bad"]]
                canary = ([bads[0]] if bads else []) + goods[:max(1, sizes[0] - 1)]
                rest = [x for x in order if x not in canary]; order = canary + rest
            waves = []; i = 0
            for sz in sizes[:-1]:
                waves.append(order[i:i + sz]); i += sz
            waves.append(order[i:])
        s.waves = waves
        for k, w in enumerate(waves):
            s.at(k * p.wave_gap if p.staged else 0.0, "release", k)
        s.at((len(waves) - 1) * p.wave_gap + p.persister_release_after, "persister_release")

    # --- helpers
    def connected(s, site): return site["online"] and not site["island"]

    def run(s):
        p = s.p
        while s.q:
            t, _, kind, a = heapq.heappop(s.q)
            if t > p.horizon: break
            s.t = t; getattr(s, "on_" + kind)(*a)
        return s.result()

    def on_part_start(s, i):
        s.sites[i]["online"] = False; s.sites[i]["last_heard"] = s.t   # last contact = partition start
    def on_part_end(s, i):
        site = s.sites[i]; site["online"] = True
        if not site["island"]:
            s.sync(site)
            for rep in site["pending_reports"]: s.at(s.t + p_delay(s), "report", *rep)
            site["pending_reports"] = []

    def sync(s, site):  # site hears controller: cancel if halted, deliver if released and not halted
        site["last_heard"] = s.t
        if s.halted: site["cancelled"] = True
        elif site["id"] in s.released and not site["staged"]:
            site["staged"] = True; site["deliver_t"] = s.t
            s.at(s.next_window(site, s.t + s.p.hold_down), "window", site["id"])

    def next_window(s, site, t0):
        per, ph = site["per"], site["phase"]
        k = max(0, -(-(t0 - ph) // per)); return ph + k * per

    def on_release(s, k):
        if s.halted: return
        for site in s.waves[k]:
            s.released.append(site["id"])
            if s.connected(site): s.sync(site)

    def on_window(s, i):
        site = s.sites[i]
        if not site["staged"] or site["activated_at"] is not None: return
        if site["cancelled"] and site["online"]: return
        if site["cancelled"]: return                      # site learned of cancel earlier
        if site["online"]: site["last_heard"] = s.t        # online sites hear the controller continuously
        if s.p.lease > 0 and s.t - site["last_heard"] > s.p.lease:
            s.at(s.t + site["per"], "window", i); return  # lease expired: stay dormant, retry next window
        site["activated_at"] = s.t
        for d in site["devs"]:
            if d["persister"] or d["state"] != "old": continue
            d["state"] = "new"; s.migrated_t.append((s.t, 1))
            if d["bad"]:
                if s.r.random() < s.p.latent_share: s.at(s.t + s.p.latent_delay, "fail", i, id(d))
                else: s.fail(site, d)
            s.report(site, ok=not (d["bad"] and d["state"] == "failed"), kind="act")
        # reports of success for good devices counted as activations
    def report(s, site, ok, kind):
        rep = (kind, ok)
        if s.connected(site): s.at(s.t + p_delay(s), "report", *rep)
        elif not site["island"]: site["pending_reports"].append(rep)

    def fail(s, site, d):
        s.events_fail += 1
        if s.r.random() < s.p.rollback_ok: d["state"] = "transient"; s.at(s.t + 2.0, "recover", id(d), site["id"])
        else: d["state"] = "failed"
        s.report(site, ok=False, kind="fail")
    def on_fail(s, i, did):
        site = s.sites[i]
        for d in site["devs"]:
            if id(d) == did and d["state"] == "new": s.fail(site, d)
    def on_recover(s, did, i):
        for d in s.sites[i]["devs"]:
            if id(d) == did and d["state"] == "transient": d["state"] = "rolled_back"
    def on_report(s, kind, ok):
        if kind == "act": s.rep_act += 1
        else: s.rep_fail += 1
        if s.p.halt and not s.halted and s.rep_act >= s.p.halt_min_n and s.rep_fail / s.rep_act >= s.p.halt_threshold:
            s.halted = True; s.halt_t = s.t
            for site in s.sites:                         # cancel order reaches online sites now
                if s.connected(site): site["cancelled"] = True
    def on_persister_release(s):
        if s.halted: return
        for site in s.sites:
            if site["activated_at"] is None: continue
            for d in site["devs"]:
                if d["persister"] and d["state"] == "old": d["state"] = "new"; s.migrated_t.append((s.t, 1))

    def result(s):
        tot = sum(len(x["devs"]) for x in s.sites)
        failed = sum(d["state"] == "failed" for x in s.sites for d in x["devs"])
        trans = sum(d["state"] in ("transient", "rolled_back") for x in s.sites for d in x["devs"])
        outage = sum(1 for x in s.sites if sum(d["state"] == "failed" for d in x["devs"]) >= 0.3 * len(x["devs"]))
        total_loss = sum(1 for x in s.sites if all(d["state"] == "failed" for d in x["devs"]))
        mig_good = sum(d["state"] in ("new",) for x in s.sites for d in x["devs"])
        # exposure: integral over horizon of unmigrated devices / total, in device-years per device
        H = s.p.horizon; ev = sorted(s.migrated_t); mig = 0; last = 0.0; area = 0.0
        for t, c in ev: area += (1 - mig / tot) * (t - last); mig += c; last = t
        area += (1 - mig / tot) * (H - last)
        return dict(total=tot, failed=failed, failed_frac=failed / tot, transient=trans, site_outages=outage, total_loss=total_loss,
                    halted=s.halted, halt_t=s.halt_t, migrated_frac=mig_good / tot, exposure_days=area)

def p_delay(s): return s.p.report_delay

def run_many(strategy_kw, n, faulty=True, **override):
    out = []
    for seed in range(n):
        p = Params(faulty_update=faulty, **strategy_kw)
        for k, v in override.items(): setattr(p, k, v)
        if not faulty: p.bad_mix_in_bad_site = p.bad_mix_elsewhere = 0.0
        out.append(Sim(p, seed).run())
    return out

def pct(xs, q): xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    print(f"runs per strategy: {n}; devices ~{60*40}; horizon 365 d\n")
    print("FAULTY UPDATE (16% of devices carry the bad revision; 30% latent) -- blast radius = devices left out of service")
    print(f"{'strategy':36s} {'mean%':>6s} {'p95%':>6s} {'max%':>6s} {'siteOut':>7s} {'transient%':>10s} {'P(halt)':>7s} {'halt day':>8s}")
    for name, kw in STRATEGIES.items():
        R = run_many(kw, n)
        ff = [r["failed_frac"] * 100 for r in R]; ht = [r["halt_t"] for r in R if r["halt_t"] is not None]
        print(f"{name:36s} {statistics.mean(ff):6.2f} {pct(ff,.95):6.2f} {max(ff):6.2f} "
              f"{statistics.mean(r['site_outages'] for r in R):7.2f} {statistics.mean(r['transient']/r['total']*100 for r in R):10.2f} "
              f"{sum(r['halted'] for r in R)/n:7.2f} {statistics.mean(ht) if ht else float('nan'):8.1f}")
    print("\nGOOD UPDATE (no fault) -- cost of caution: share migrated by horizon and exposure (unmigrated device-years per device, 1 yr)")
    print(f"{'strategy':36s} {'migrated%':>9s} {'exposure':>9s} {'false halt':>10s}")
    for name, kw in STRATEGIES.items():
        R = run_many(kw, n, faulty=False)
        print(f"{name:36s} {statistics.mean(r['migrated_frac'] for r in R)*100:9.1f} "
              f"{statistics.mean(r['exposure_days'] for r in R)/365:9.3f} {sum(r['halted'] for r in R)/n:10.2f}")
    print("\nSTRESS: site-homogeneous fault (bad hw in 100% of devices at bad sites), rollback 50%, report delay 10 d, 70% latent")
    print(f"{'strategy':36s} {'mean%':>6s} {'p95%':>6s} {'siteTotalLoss':>13s} {'P(halt)':>7s}")
    for name, kw in STRATEGIES.items():
        R = run_many(kw, n, bad_mix_in_bad_site=1.0, rollback_ok=0.5, report_delay=10.0, latent_share=0.7)
        ff = [r["failed_frac"] * 100 for r in R]
        print(f"{name:36s} {statistics.mean(ff):6.2f} {pct(ff,.95):6.2f} {statistics.mean(r['total_loss'] for r in R):13.2f} {sum(r['halted'] for r in R)/n:7.2f}")

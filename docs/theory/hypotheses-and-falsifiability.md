# Hypotheses and falsifiability

| ID | Hypothesis | Class | Falsified if | Test |
|---|---|---|---|---|
| HYP-01 | Presence design cuts 40-year governance loss ≥10× vs Rev 2 rule | Hypothesis (model-conditional) | Ordering flips under plausible hazard sweep | SIM-01 + sweep (GATE-12) |
| HYP-02 | Auto-halt cuts rollout harm several-fold | Hypothesis | Variant C not materially better than B | SIM-02 |
| HYP-03 | AND of disjoint-assumption keys is single-failure safe | Derived (algebra) | Hidden shared assumption | SIM-03, EXP-18 |
| HYP-04 | First-stage invariants hold | Hypothesis | Any TLC violation in base | SIM-04 (GATE-08) |
| HYP-05 | Admission ≤10 ms at 64 MHz | Hypothesis | Silicon measurement exceeds | EXP-19 |
| HYP-06 | A lockable first stage exists on ≥30% of industrial MCU families | Hypothesis | Survey below 30% | E-A1 |
| HYP-07 | KRYPTARA's kernel generalises beyond update/authority governance | Speculative, narrowed | `models/second_domain_ca_root.py` (item 46): the admission/tier/evidence layer (Theorems 1-3, interval computation) carries over cleanly to root-CA key governance with no new theory, same arithmetic and even the same impossibility (2-safe+1-loss-live is unreachable). The staged-effect/boot/image layers (REQ-HALT-01, REQ-IMG-01) do NOT carry over -- CA governance has no boot concept. Narrowed claim: "the admission/tier core generalises across long-lived-authority domains; the device-specific layers do not" -- see docs/applications/second-domain-ca-root.md's Verdict. Still Speculative beyond this one worked example (n=2 domains is not evidence of unlimited generality) |

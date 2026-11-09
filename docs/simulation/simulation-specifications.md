# Simulation and model specifications

**Level:** L2. Each model uses the 15 required fields. "Run status" states what was actually executed and recorded in this repository.

## SIM-01 Governance-loss Monte Carlo (`models/brick_mc.py`)
| Field | Content |
|---|---|
| Question | How much does the probability of unrecoverable governance loss over 40 years differ between the Rev 2 rule, a single-family degraded mode, and the terrestrial presence design? |
| Hypothesis | HYP-01: the presence design reduces 40-year governance-loss probability by an order of magnitude versus the Rev 2 rule. |
| Scope | One device population's governance state; not fleet logistics. |
| Assumptions | Independent annual hazards for key loss, custodian loss and hash-family break; hazard values are **illustrative**. |
| State variables | Live/lost/compromised status per atom per year. |
| Governing rules | Each tier's table decides if the survivors can act. |
| Initial conditions | All atoms live at year 0. |
| Inputs | Hazard rates, horizon (40 y), tier tables from `lint.py`. |
| Methods | Monte Carlo over years. |
| Outputs | Probability of governance loss per rule set. |
| Metrics | Governance-loss fraction. |
| Baseline | Rev 2 rule. |
| Reproducibility | Fixed seed in script; `python3 models/brick_mc.py`. |
| Limitations | Hazards not measured; independence assumed; no correlated-failure model beyond what the script encodes. |
| Rejection conditions | HYP-01 is rejected if the ordering changes under plausible hazard ranges (sensitivity sweep: `simulations/hazard_sweep.py`, GATE-12). |
| Run status | Previously produced 39% / 9.9% / 1.0% at baseline hazards. Hazard sweep (`simulations/hazard_sweep.py`, GATE-12) run 2026-11-09 over `h_group` ∈ [1%,10%]/yr × `h_family` ∈ [0.1%,3%]/yr, 16 points, 20,000 trials/point: 0/16 points violate the claimed ordering terrestrial ≤ remote_degraded ≤ {remote, rev2_*}. HYP-01's rejection condition was not triggered over this range. |

## SIM-02 Migration twin (`simulations/twin/migration_twin.py`)
| Field | Content |
|---|---|
| Question | Do staged waves, auto-halt, activation lease and stratified canary reduce harm from a faulty fleet update? |
| Hypothesis | HYP-02: auto-halt cuts expected harm several-fold versus big-bang or staged-without-halt. |
| Scope | Fleet rollout of one update. |
| Assumptions | As coded in the script (fault injection model, persisters 5%). |
| State variables | Per-site update state, harm counters. |
| Governing rules | Policy variants A–F. |
| Initial conditions | Script defaults. |
| Inputs | Variant, persister fraction, lease length. |
| Methods | Discrete simulation. |
| Outputs | Two harm metrics plus two further columns (see `run_output.txt`). |
| Metrics | First two numeric columns of the output table. Their column names are defined in the script; they are not restated here. |
| Baseline | Variant A (big-bang). |
| Reproducibility | `python3 simulations/twin/migration_twin.py`. |
| Limitations | Synthetic fleet; no field data. |
| Rejection conditions | HYP-02 rejected if variant C is not materially better than B. |
| Run status | Recorded output: A 10.58/14.93, B 10.58/14.82, C 1.47/4.18, F 1.14/2.97 (first two columns). Supports HYP-02 inside the model only. |

## SIM-03 Diversity / disjoint-quorum checker (`simulations/diversity/`)
| Field | Content |
|---|---|
| Question | Given keys with declared assumption sets, which compositions keep authority safe under one assumption failure? |
| Hypothesis | HYP-03: AND-composition of keys with disjoint assumption sets is single-failure safe; OR-accept is never safe. |
| Scope | Assumption-failure algebra on monotone DNFs. |
| Assumptions | Assumption atoms are complete and independent (the "closed world"). |
| State variables | Set of failed assumption atoms. |
| Governing rules | AND = cross product; OR = union; minimise. |
| Initial conditions | None. |
| Inputs | Assumption sets per key. |
| Methods | Exact enumeration. |
| Outputs | Minimal failing sets. |
| Metrics | Smallest failing set size. |
| Baseline | Single key. |
| Reproducibility | `python3 simulations/diversity/dq.py`. |
| Limitations | Result is only as good as the declared assumptions (R-1, R-5). |
| Rejection conditions | A hidden shared assumption found by audit (EXP-18) rejects independence for that pair. |
| Run status | Script present; not re-run this session. |

## SIM-04 First-stage TLA+ model (`simulations/tla/`)
| Field | Content |
|---|---|
| Question | Does the first-stage state machine preserve its safety invariants under power loss and attack steps? |
| Hypothesis | HYP-04: invariants hold in the base configuration; mutations M1–M8 each break at least one invariant (mutation check). |
| Scope | First-stage update/activate state machine. |
| Assumptions | Bounded constants in cfg files. |
| State variables | Defined in `FirstStage.tla`. |
| Governing rules | TLA+ actions. |
| Initial conditions | `Init`. |
| Inputs | cfg_*.cfg. |
| Methods | TLC explicit-state model checking. |
| Outputs | `out_*.txt`. |
| Metrics | Invariant violations; states explored. |
| Baseline | `cfg_base.cfg`. |
| Reproducibility | `simulations/tla/run.sh` (needs TLC; not available in every environment). |
| Limitations | Bounded model; **does not model holder co-signature (F-R2-03)**. |
| Rejection conditions | Any invariant violation in base rejects HYP-04. |
| Run status | **The base run output ends in a progress line (29.8 M distinct states, 8.2 M on queue); the recorded output shows no completion, so HYP-04 is not established.** Recorded outputs also show a counterexample for the earlier v1 spec (`out_cex0…`, invariant Inv_NoSingleAssumptionAdvance) and for mutation M2 (`out_m2_twoof`, invariant Inv_NoAnergyLockout), consistent with mutation checks catching those weakened rules; the M3 output is partial. This must be re-run to completion before any claim. |

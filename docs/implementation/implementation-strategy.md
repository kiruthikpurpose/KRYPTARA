<!-- Title: Implementation strategy -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 13. Implementation strategy

### 13.1 Repository architecture

```text
/spec/                 the long-lived artefacts: kernel spec (≤ 30 pages), waist ABI, record layouts,
                       CDDL, label registry, action/tier table, test-vector format, genesis-record template
/spec/vectors/         positive and negative vectors for every action, tier, profile and part profile
/core/c/               ac-core, ac-policy, ac-hash, ac-hbs-verify, ac-wit (C99 subset, MISRA-style rules)
/core/rust/            no_std twin of the same (panic-free; Kani harnesses)
/model/python/         executable reference model; lint; theorem checks (interval.py, lint.py lineage)
/model/tla/            TLA+ specification of the kernel and the transition protocol
/providers/            mlkem-native, mldsa-native wrappers; verify-only LMS/HSS, SLH-DSA; hardware-engine ports
/ports/<part>/         NV, counter, presence, RTC ports; part profile (torn_read, OTP, counters, presence input)
/stage2/               ac-stage, ac-report, ac-enrol, ac-config-echo, protocol adapters
/host/                 ac-lint, ac-ceremony, ac-monitor, ac-planner, ac-twin, ac-govsim (Rust + Python)
/fleet/                reference log (Tessera) and witness deployments; bundle builder; receipt fetcher
/conformance/          suite run by port owners to claim a profile; power-cut rig scripts; mutation tests
/ref-designs/          presence input designs; P2 safety split; P3 gateway; C-04 supervisor (if gated in)
/docs/                 rationale, threat model, decision record (this document's §20), assessor packs
```

### 13.2 Languages and dependency policy

* **Locked stage and kernel:** a C99 subset compiled by two compilers (GCC and Clang) with identical vector results, plus an independent Rust `no_std` twin. No dynamic memory, no recursion, no libc beyond `memset`/`memcpy`, fixed capacities, and static stack bounds checked in CI.
* **Above the waist:** Rust preferred, C where vendor SDKs require it.
* **Host:** Rust for production tools; Python for reference models, simulations and the lint reference.
* **Dependencies:** none in `/core`. Providers wrap mlkem-native and mldsa-native. Our own verify-only LMS and SLH-DSA are permissively licensed. **Avoided:** PQClean (archived 2026-08-04 [S, landscape audit]), pqm4 as a dependency, liboqs in firmware, and GPL in firmware.

### 13.3 Development infrastructure

Monorepo; CMake + Cargo; pinned, containerised toolchains; reproducible builds checked by two independent builders. CI gates: layer-graph check, undefined-symbol check, flash/RAM/stack budgets per profile, all vectors on all providers and ports, C/Rust/Python differential tests on every small-universe input, bounded TLC, CBMC on the C kernel, Kani on Rust, fuzzing with sanitisers for every parser above the waist, the policy lint, and mutation testing on release branches. **Dog-fooding:** the project's own releases are governed artefacts. Release signing uses three custody groups, two hash families, logs with witnesses and a presence-gated constitution for changes to the release rules.

### 13.4 Testing framework

| Layer | Technique | Exit criterion |
|---|---|---|
| Admission and tiers | Exhaustive checks over all monotone functions for ≤ 5 atoms; randomised for 8; C vs Python | 0 mismatches (current: 3,000 cases [M]) |
| Kernel state machine | TLA+ invariants: epoch and floor monotone; no single declared fault reaches a T1 or T2 commit; no lockout under declared single losses; power cut at any step leaves a bootable image | 0 violations on bounded configurations with recorded state counts |
| C implementation | CBMC bounded proofs of memory safety and of admission ≡ spec; Frama-C WP for loop invariants | Proof obligations discharged |
| Rust twin | Kani panic-freedom; proptest differential against the model | 0 panics; 0 divergences |
| Parsers above the waist | libFuzzer/AFL++ with ASan/UBSan | No crashes in 10⁹ execs per parser before release |
| Power safety | Hardware power-cut rig | ≥ 10⁵ cuts, 0 unrecoverable, on ≥ 2 ECC-flash families |
| Clock hostility | Property tests with arbitrary RTC values | Time only ever reduces the authorised set |
| Fault injection (software model) | Bit flips in tables, masks and counters at decision points | Every single flip either detected or harmless (complement checks) |
| Mutation testing | 100 seeded single-point bugs (red-team X-E2 list) | ≥ 95% killed |

### 13.5 Formal methods plan

1. **Theorem level.** Mechanise Theorems 1–3 in Lean or Isabelle, a few hundred lines (EXP-10a).
2. **Protocol level.** TLA+ model of transitions, tiers, chain, halt budget and catch-up, with the attacker able to compromise any declared class and to reorder, delay and drop messages (EXP-02 extended).
3. **Code level.** CBMC/Frama-C proofs that `ac_tbl_*` implement the spec for all 2²⁵⁶ tables. This is feasible because the functions are loops over 256 entries with bitwise bodies. Refinement of the TLA+ step to the C step uses the Python model as the executable oracle.

### 13.6 Security review process

* Internal red team at each phase gate, with a written memo and falsification experiments (the X-memos in this programme are the template).
* **External design review** of the waist, the theory and the tiers before any T0 freeze. **Implementation audit** of the locked stage and providers. Constant-time review of the few secret-bearing paths: the ML-KEM decapsulation key and the reporting seed.
* An **independent re-implementation** of the kernel from `/spec` alone by a team that has not seen our code, followed by differential testing (P-12).
* A bug bounty and coordinated disclosure policy. Every fixed issue becomes a vector.

### 13.7 Benchmarks

Platforms: Cortex-M0+ (64 MHz), Cortex-M33 (with and without TrustZone), Cortex-M4F/M7, RV32IMC, a Linux-class gateway, and one HSM firmware target. Metrics: flash, RAM, worst stack, cycles per primitive and per action, protection-ready time, verification energy (µJ), bytes on the wire per action, time to catch up N epochs, and admission time. Published per release with toolchain hashes.

---


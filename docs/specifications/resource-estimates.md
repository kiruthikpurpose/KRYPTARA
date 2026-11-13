<!-- Title: Resource estimates -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Reviewed against the R2 red-team findings on 2026-11-12; conflicting passages were corrected in place (see CHANGELOG).

# 9. Resource estimates

| Item | Value | Label |
|---|---|---|
| Core (SHA-256, SHAKE256, LMS verify, journal), Cortex-M0+, gcc -Os | 3,962 B (clang 4,717 B) | [M, compiled; binaries not executed on silicon] |
| Interval admission incl. on-device bounds (`policy8.c`) | 682 B (Rev 4; 902 B hardened as of the R2 fixes — **stale**: measured 1,196 B in CI on 2026-11-13, see GATE-07, CLM-07) M0+, 680 B M33; stack ≈ 88 B | [M] |
| Earlier 6-slot validator (Rev 3) | 176 B | [M] superseded |
| Witnessed-receipt verifier (inclusion proof + cosignature loop) | ≈ 0.6–1.0 KiB | [E] |
| Presence sampling + glue | ≈ 0.2 KiB | [E] |
| Locked stage total, dual-terrestrial | ≈ 6–8 KiB code (+ SLH-DSA verifier if used: unmeasured) | [E] |
| State | ≈ 700 B (A/B copies) + 128 B snapshots | [E from layouts] |
| Worst-path stack | ≈ 856 B core + ≈ 88 B admission | [M, static frames] |
| LMS W4 verify | 473–563 hash calls; ≈ 42 ms at 64 MHz (software SHA-256) | [M calls; E time] |
| LMS-SHAKE verify | ≈ 570 Keccak permutations ≈ 151 ms (≈ 17,000 cycles/permutation, weak estimate) | [E] |
| Admission (2-fault bounds, 12 classes) | ≈ 3–10 ms at 64 MHz | [E] — host measurement of the same operation (`ac_tbl_upper`, nf=12, k≤2, `tests/bench_policy8.c`) takes ≈ 21.4 µs on a ~2026 x86 laptop at -O2; scaling by a rough clock+throughput factor (~100–300×) for a 64 MHz Cortex-M0+ lands in the same 2–6 ms range, which is consistent with (does not prove) this estimate. See CLM-23. The on-device *per-transition* hot path is `ac_tbl_authorises`, a single bit test (< 1 ns host-measured): `ac_tbl_upper`/`ac_tbl_lower` run once at policy provisioning, not per admission. |
| Witnessed receipt | ≈ 6 KB, ≈ 85 ms (two LMS cosignatures + 24-level proof) | [E] |
| T1 transition, dual | 2 LMS signatures (≈ 2 × 2.5 KB) + receipt ≈ 11 KB; ≈ 280 ms verify (SHA-256 LMS ≈ 42 ms + SHAKE256 LMS ≈ 151 ms + receipt ≈ 85 ms) | [E] |
| Protection-ready time with Merkle-page + stored root | ≈ 1.5–2.8 ms (first 2 KiB page) | [E] |
| One-time report signature | 2,144 B; ≈ 48 ms software | [M size; E time] |
| Leaf list per device / per 100,000 devices | 128 KiB / ≈ 12.2 GiB | [M] |
| ML-KEM-768 enrolment ciphertext | 1,088 B | [F] |
| Optical local token with two LMS signatures + payload | 5,316 B ≈ 21 s at 2 kbps | [M arithmetic] |
| Real-silicon cycle counts and fault behaviour | **not yet measured** | Phase 0 |

---


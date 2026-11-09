<!-- Title: Reproducibility index and sources (Rev 4) -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L3. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 21. Reproducibility index and sources

### 21.1 Every computed number, and how to reproduce it

All paths are relative to the project's `blueprint/` folder.

| Claim | Script | Command |
|---|---|---|
| Dedekind counts; 6-slot counts (4,778,188; 1,227,427; 0) | `code/G/enum6.py`, `code/G/policy_study.py`, `code/G/theory.py` | `python3 theory.py` |
| Interval theorem on 1,050 random structures; class-count law | `code/G/interval.py` | `python3 interval.py` |
| Tier tables, budgets, impossibility catalogue | `code/G/lint.py`, `code/G/tiers_extra.py` | `python3 lint.py; python3 tiers_extra.py` |
| C admission ≡ Python reference (3,000 cases); 682 B (Rev 4; now 902 B hardened, see CHANGELOG); stack 88 B | `code/G/policy8.c`, `p8test.c`, `p8check.py` | `gcc -O2 -o p8test p8test.c && python3 p8check.py`; `arm-none-eabi-gcc -mcpu=cortex-m0plus -mthumb -Os -c policy8.c` |
| Governance-loss Monte Carlo | `code/G/brick_mc.py` | `python3 brick_mc.py` (≈ 6 min) |
| κ disjointness model (19.2×) | `code/B/dq.py` | — |
| Migration twin (2.31% / 2.32% / 0.15%) | `code/F/migration_twin.py` | — |
| TLA+ runs (lockout counterexample; 13.5M states) | `code/V/FirstStage.tla` + TLC logs | — |
| Core size 3,962 B; LMS vectors; power-cut host simulator | `code/E/`, `code/P/` | — |
| Red-team computations (n = 5 tables) | `code/X/rt.py` | — |

### 21.2 Sources checked in this programme

Standards and specifications:
* NIST FIPS 204 (ML-DSA): https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf. SHAKE use confirmed.
* NIST FIPS 205 (SLH-DSA): https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf. Exact per-function SHA-2 assignment not re-read.
* NIST SP 800-208 (LMS/XMSS incl. SHAKE256 sets): https://csrc.nist.gov/pubs/sp/800/208/final
* NIST SP 800-230 (draft, 13 Apr 2026, additional SLH-DSA parameter sets): https://csrc.nist.gov/pubs/sp/800/230/ipd
* NIST SP 800-232 (Ascon, final 13 Aug 2025): https://csrc.nist.gov/pubs/sp/800/232/final
* NIST IR 8547 (final 27 Oct 2026): https://csrc.nist.gov/pubs/ir/8547/final
* FIPS 206 status (pqc-forum, Apr 2026): https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/1HXzjlMUU6Y
* NSA CNSA 2.0 algorithms (secondary access): https://media.defense.gov/2025/May/30/2003728741/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS.PDF
* RFC 9943 (SCITT): https://www.rfc-editor.org/rfc/rfc9943.html · RFC 9162 (CT 2.0): https://www.rfc-editor.org/rfc/rfc9162.html · RFC 4998: https://www.rfc-editor.org/info/rfc4998
* C2SP tlog-witness / checkpoint / cosignature: https://c2sp.org/tlog-witness · https://c2sp.org/tlog-checkpoint@v1.1.0 · https://c2sp.org/tlog-cosignature@v1.1.0 · Sigsum: https://www.sigsum.org/docs
* TCG Physical Presence Interface: https://trustedcomputinggroup.org/resource/tcg-physical-presence-interface-specification/ · TPM 2.0 Library: https://trustedcomputinggroup.org/resource/tpm-library-specification/
* TUF specification: https://theupdateframework.github.io/specification/latest/ · Uptane 2.1.0: https://uptane.org/papers/uptane-standard.2.1.0.pdf
* IEC 61508-6 (β-factor, Annex D; preview): https://assets.vde-verlag.de/iec-normen/preview-pdf/info_iec61508-6%7Bed2.0%7Db.pdf

Research literature:
* Hirt & Maurer, J. Cryptology 13(1):31–60 (2000): https://doi.org/10.1007/s001459910003
* Benaloh & Leichter, CRYPTO '88: https://link.springer.com/doi/10.1007/0-387-34799-2_3
* Rompel, STOC 1990: https://www.doi.org/10.1145/100216.100269
* Syta et al., IEEE S&P 2016 (witness cosigning): https://eprint.iacr.org/2014/1004
* Kelsey, Lang & Lucks, Communications in Cryptology 2(2), 2025: https://csrc.nist.gov/pubs/journal/2025/07/turning-hash-based-signatures-into-distributed-sig/final
* PRAWNS (ePrint 2026/2142): https://eprint.iacr.org/2026/2142 · One-round threshold XMSS/SPHINCS+ from FHE (ePrint 2026/2360): https://eprint.iacr.org/2026/2360
* Buterin, weak subjectivity (25 Nov 2014): https://blog.ethereum.org/2014/11/25/proof-stake-learned-love-weak-subjectivity
* Shapiro et al., CRDTs, SSS 2011: https://link.springer.com/doi/10.1007/978-3-642-24550-3_29
* Macaroons, NDSS 2014: https://www.ndss-symposium.org/ndss2014/programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/
* CONIKS, USENIX Security 2015: https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/melara
* Lazarus (diversity management in BFT), Middleware 2019: https://www.dpss.inesc-id.pt/~ler/projects/abyss
* Hardware hazard evidence (carried from Rev 2): ST Community articles and AN5342 on STM32H5 ECC behaviour, as listed in Rev 2 §12.

**Not verified in this programme:** IEC/ISO clause numbers beyond the β-factor annex; CMVP status of PQ providers; PQ profiles of OPC UA, IEC 62351, DNP3-SA, Modbus Security and Sparkplug; TPM v1.85 PQC content from TCG text; any BOM figure; the exact SHA-2 function assignment per SLH-DSA parameter set; real-silicon timings. Fitzi–Hirt–Maurer (CRYPTO '98) is deliberately not cited because a 1999 note reported an error in its mixed-adversary protocol [F]. Our mixed condition is proved directly in §3.3.

---


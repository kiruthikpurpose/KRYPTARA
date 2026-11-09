# Stream E: Embedded systems and bootloader design

Scope: everything that runs on constrained devices. Evidence labels follow the brief. Scratch code, test vectors and cloned reference repos are under `/home/claude/atlas2/blueprint/code/E/` (`fs/` = first-stage code, `fs/host/` = tests, `fs/build/measure.sh` = size script, `ref/` = shallow clones of upstream repos used for status checks). Today is 2026-11-06.

Terminology: **FS1** = the locked continuity first stage (atlas 11.1 "MV-1/HA-1"). **S2** = the updatable second stage. **PU** = flash program unit (smallest independently programmable chunk).

## E.0 What was measured, what was estimated (read this first)

| Item | Status | How |
|---|---|---|
| FS1 SHA-256 + SHAKE256 + LMS verifier + journal code size on Cortex-M0+/M4/M33 | **Measured [D-local]** | `arm-none-eabi-gcc 13.2.1` and `clang 18.1.3`, `-Os`/`-O2`, `-ffunction-sections`, `arm-none-eabi-size` (text+data), `fs/build/measure.sh` |
| FS1 per-function stack frames | **Measured (compiler `-fstack-usage`, static)** | gcc M0+ `-Os`; worst-path depth is my sum, so [C] |
| LMS verifier correctness | **Measured**: 21 independent vectors from `pyhsslms 2.0.0` (SHA-256 and SHAKE256; W2/W4/W8; H5/H10) all verify; 903 negative cases (bit flips, wrong message, truncation, altered key) all rejected | `fs/host/test_lms.c` |
| Hash-call counts per LMS verify | **Measured (host, instrumented)** | W4/H5: 473, 563, 503 calls for q=0,1,2; W8/H5: 4,088, 3,833, 5,108; W2/H5: 182 |
| Journal power-fail safety | **Measured (simulation)**: 6,720 cut points (PU = 4/8/16/32, clean cut and torn unit with random bit subsets), 0 violations, never a double-program of a unit | `fs/host/test_journal.c` |
| Cycle counts of FS1 on a real MCU | **Not measured**: no hardware or cycle-accurate model here. Every ms figure for FS1 is [E] from measured block counts times an assumed cycles/block | see E.4 |
| ML-KEM/ML-DSA/SLH-DSA Cortex-M4 cycles, stack, code | **[D] from pqm4 repo** `benchmarks.csv` (clone of 2026-10-23, STM32F4 @ 24 MHz, `arm-none-eabi-gcc 11.3.1`) | read directly |
| M0+ ML-KEM numbers (atlas: "22 ms, 14.2 KB") | **Not verified**: pqm4 has no M0+ target. See E.4 | |
| Energy, LoRa airtime | **[C]** from stated formulas; current draws are **assumptions [E]** | python in E.6 |
| Upstream PQ status (MCUboot, wolfBoot, Nordic, ST, PSA, U-Boot, OpenTitan, etc.) | **[F]** where read from upstream source/docs this session, otherwise "unverified" | E.2 |
| Standards clauses (IEC 61508, 62443-4-2, DO-326A, ISO 26262, IEC 62304, EN 50159) | **Not fetched this session.** Stated from general knowledge, labelled [I], no clause numbers | E.5 |

**Headline measured result.** The SHA-256 + SHAKE256 + LMS-verify + journal core compiles to **3,962 B** (gcc `-Os`, Cortex-M0+), 4,717 B with clang `-Os`. The atlas's "~13 KB" (12,864 B demonstrated verifier plus library) is therefore a conservative budget, not a floor: a complete FS1 with two hash waists fits in roughly 7 KB [E] (measured core + estimated boot logic and glue, E.1.3).

---

## E.1 The locked continuity first stage in implementable detail

### E.1.1 Boot flow

```
RESET
 └─ vendor ROM (if any)  [outside our control; assessed per part, E.3.3]
     └─ FS1 entry (locked flash, reset vector points here)
         0  hal.init; debug_state() -> record; wdt start (window >= worst-case verify, E.5)
         1  journal_load(): scan append-only log -> fs_state{kf, svn_floor, slot[4], lkg}   [no trust in RAM copies]
         2  candidates = {A, B}; order by manifest.svn descending (header read only)
         3  for each candidate:
               parse manifest (fixed layout, length-checked)         -> reject on any field error
               svn >= svn_floor ?  key_epoch >= kf ?                 -> else reject (rollback)
               pick sigblock; pk-hash(sigblock.pk) == slot[sigblock.slot].hash && slot.gen >= kf ?
               alg class derived from pk typecodes (never from a stored flag)
               LMS verify(Hash_alg(manifest))                        (E.1.4)
               hash image under every family the manifest carries; compare
               policy: ANY1 (default C2) or DISJOINT2 (C3 default, E.1.5)
            first success -> state RUN
         4  none -> LKG: hash image at LKG slot; equals journal LKG pin ?  -> state LKG (reduced authority)
         5  none -> BRICK_GUARD: hal.safe_state(); stay in watchdog-reset loop; log; no network, no debug
         6  authority-change bundle present (staging area)?  -> E.1.5 (before step 3, so a new floor applies to this boot)
         7  hal.lock_until_reset()  (journal + FS1 region read-only to S2)  -> hal.jump(slot, entry)
```

State machine states are those of atlas 11.1: BOOT, VERIFY_B (verify via first class), VERIFY_ALT (verify via alternate class), RUN, LKG, BRICK_GUARD. Invariants to model-check in TLA+ (atlas lists a, b, c; I add d and e):
(a) no single-class key reaches ADVANCE_FLOOR; (b) a power cut at any step leaves a bootable image or LKG; (c) the floor never decreases; (d) the lock call precedes every `jump`; (e) journal state is a pure function of NV contents (no RAM-only authority).

**DECISION E-1.** Stage 1 never trusts anything it did not just read from locked NV or verify itself, and never exports services at run time (no SVC/callable API after `jump`). Confirmation of an image is a flag in an *unlocked* swap-state area; FS1 acts on it at the next boot.
WHY: a runtime API would be an updatable-code attack surface inside the germline (atlas pattern 17). ALTERNATIVES REJECTED: TF-M-style secure-service partition in FS1 (large, needs MPU/TrustZone policy, moves the lock boundary). ASSUMPTIONS: S2 cannot write the journal after `lock_until_reset` or permanent lock. TRADE-OFFS: image confirm costs one extra boot cycle. LIMITS: parts with no region lock cannot host FS1 safely (E.3.3). VALIDATE: model check (d), (e); fault-injection campaign on the lock call itself (atlas HA-1). Traces: R1, R2, N20, atlas 11.1.

### E.1.2 Memory map (reference, 512 KB-class M33; scale down per class)

| Region | Size | Lock | Content |
|---|---|---|---|
| FS1 code + rodata | 16 KB (2 x 8 KB pages; budget, ~7 KB used [E]) | permanent or lock-until-reset, region-granular | vectors, FS1, HAL glue |
| Journal | 10 KB for C2/C3 (128 entries x 80 B); 2.5 KB for C1 (32 entries) | writable only by FS1 (lock-until-reset before handover) | append-only log (E.1.4) |
| Swap-state / trial-boot flags | 1 page | unlocked | MCUboot-style trailer; not security state |
| Slot A | size S | unlocked | S2 + app |
| Slot B | size S | unlocked | S2 + app (or staging) |
| Slot R (optional, C3) | small | unlocked, signed | recovery S2, subject to floor |
| LKG pin | in journal (32 B + svn) | | image stays in A or B (the non-active slot is not overwritten until a newer image is confirmed) |

RAM: FS1 uses a single static `fs_state` and one stack, then RAM is zeroed before `jump` (no residue). No heap. `.bss` + `.data` for FS1 = `fs_state` (see below).

### E.1.3 Flash and RAM budget

Measured (gcc 13.2.1, `-Os`, Cortex-M0+; text+data per object, `-ffunction-sections`):

| Module | M0+ gcc -Os | M0+ clang -Os | M4 gcc -Os | M33 gcc -Os | M0+ gcc -O2 |
|---|---|---|---|---|---|
| `fs_hash.c` (SHA-256 + SHAKE256/Keccak-f, incl. 256 B K-table and 192 B round tables) | 1,922 | 2,080 | 2,010 | 2,026 | 2,256 |
| `fs_lms.c` (LMS verify, SHA-256 and SHAKE256 types, W2/4/8, H5-25) | 1,252 | 1,629 | 1,170 | 1,170 | 2,171 |
| `fs_journal.c` (load, append, torn handling) | 788 | 1,008 | 776 | 776 | 928 |
| **Measured core** | **3,962** | **4,717** | **3,956** | **3,972** | **5,355** |

Clang `-O2` on M4 reaches 4,492 B for the hash module alone (loop unrolling): **`-Os`/`-Oz`, not `-O2`, for FS1**; and the gcc/clang spread (~19% on M0+ at `-Os`) is why we build with two compilers (E.8).

Estimated additions (not written or measured): manifest parser, slot table policy, quorum rule, boot state machine, authority-bundle handler: about 200 lines of C; scaling from the journal (about 60 lines for 788 B, ~13 B/line) gives ~2.6 KB, I budget 2.0-2.6 KB [E]. Vector table, startup, HAL glue for one part: ~1 KB [E]. **Total FS1 [E]: 3,962 + 2,600 + 1,000 = ~7.6 KB, call it 8 KB**; with hardware SHA/Keccak the software tables (about 1.5 KB of `fs_hash.c`) can be dropped: ~6 KB [E].

SHA-256-only variant (single waist, class C1/C2 minimum) removes Keccak: roughly 1 KB less [E, not compiled separately].

RAM (stack, measured static frames, gcc M0+ `-Os`):

| Function | Frame (B) |
|---|---|
| `fs_lms_verify` (two hash contexts: one union holds a 208 B SHAKE context) | 688 |
| `fs_sha256_update` (with inlined block, 64 B schedule) | 160 |
| `keccakf` / `fs_shake256_update` | 104 / 32 |
| `fs_journal_load` / `tag_of` | 432 / 160 |
| `fs_journal_append` | 248 |

Worst path: verify 688 + `h_upd` 8 + `sha256_update` 160 = **856 B** [C]; journal path 432 + 160 + 160 = 752 B [C]. Add boot-logic frame ~250 B [E] and `fs_state` static (28 B scalars + 4 slots x 36 B + 32 B LKG hash = ~204 B [C]). **FS1 RAM ~1.3-1.5 KB [E]**, consistent with the atlas's 1-1.6 KB. Using a SHA-256-only build shrinks the 208 B SHAKE context out of the union (~ -200 B per context, two contexts: ~ -400 B) [E].

### E.1.4 Data layouts

```c
/* little-endian; all multi-byte fields fixed-width; no padding assumptions (packed, checked at compile time) */
struct fs_manifest {            /* 112 B */
  uint32_t magic;               /* 'FSM1' */
  uint16_t fmt_ver, flags;      /* flags: HAS_SHA256, HAS_SHAKE256, POLICY_DISJOINT2 */
  uint32_t kind;                /* 1 stage2, 2 authority bundle, 3 lkg-note */
  uint32_t svn;                 /* image security version (anti-rollback) */
  uint32_t key_epoch;           /* must be >= journal kf */
  uint32_t img_len;
  uint8_t  device_scope[16];    /* all-zero = fleet; else UUID (debug credentials, spares) */
  uint8_t  img_sha256[32];
  uint8_t  img_shake256[32];
  uint8_t  rsv[8];              /* = 4+2+2+4+4+4+4+16+32+32+8 = 112 */
};
struct fs_sigblock {            /* variable */
  uint8_t  slot, rsv; uint16_t sig_len;
  uint8_t  pk[56];              /* LMS pk: lms_type|ots_type|I[16]|K[32] */
  uint8_t  sig[];               /* LMS-SHA256 W4 H10 = 2,508 B; W8 H10 = 1,452 B */
};
struct fs_slot  { uint8_t hash[32]; uint32_t gen; };           /* 36 B, 4 slots = 144 B in RAM; commitment = Hash_class(pk) */
```
Signed message for a slot of class `A` is `Hash_A(manifest)` and the manifest carries the image digest under each family a signer uses. This is a point the atlas does not state: **if both signers sign a SHA-256-only digest of the image, a SHA-256 break forges both and the "disjoint quorum" is an illusion.** Each class must sign a digest under its own hash waist, so DISJOINT2 verification hashes the image twice (SHA-256 and SHAKE256) in one pass over flash. [I]

**Slot count: four, not three.** Three live slots (OEM-A, OEM-B, operator) plus one empty position so the molting step "provision alongside" (atlas pattern 15) always has a free slot; otherwise provisioning a replacement requires first retiring a live key. +36 B. [H]

**Assumption class is derived from the verified public key, never stored.** `fs_lms_pk_alg()` maps typecodes to SHA2 or Keccak; the quorum test uses bitmasks (SHA2 = 1, KECCAK = 2, LATTICE = 4; ML-DSA = LATTICE|KECCAK because it uses SHAKE internally). A stored class flag could be altered by a slot-replacement bug; a derived one cannot disagree with the key.

**Journal entry** (append-only; `fs_journal.c`): HDR(16: magic `4A 31`, type, slot, seq, arg0, arg1) | PAY(32) | TAG(16 = first 16 B of SHA-256(HDR||PAY)) | VOID(16). Each region rounded up to PU: entry size 80 B for PU = 4, 8, 16; 128 B for PU = 32. Types: FLOOR (arg0 = kf, arg1 = svn floor), SLOT (slot, arg0 = gen, PAY = new hash), LKG (arg0 = svn, PAY = image hash).

Write order PAY, HDR, TAG. **TAG is the commit point.** Valid iff the tag matches, VOID is all-zero, `seq == previous + 1`. Anything else non-empty is torn: it is skipped, counted, and **frozen** by programming VOID. Scan ends at the first all-zero entry. `fs_journal_append` re-reads NV after the commit so RAM state is always derived from NV.

**DECISION E-2 (journal).** Append-only log, every PU programmed exactly once, no erase in the baseline mode (JM-A). Optional rotate-with-erase mode (JM-B, below) for erasable flash only.
WHY: (1) Many NOR parts with ECC allow one program per 16-byte word between erases: write-once-per-unit is the only discipline that is legal on all of them [I; per part datasheet]. (2) Interrupted program leaves a bit-subset of the intended value, so a tag that must equal an exact value cannot be satisfied by a partial write; no erase means no half-erased sector. (3) The state is monotone, so the safe states are exactly "before" and "after".
Capacity arithmetic [E]: over 25 years: initial slots 3 + floor advances ~5 + slot replacements ~4 + LKG pins ~25 (one per confirmed update, assumed 1/yr) + torn-write debris ~4 = **41 entries**; 2x margin (rule E.7) = 82; provisioned 128 entries x 80 B = **10 KB**. For C1 (no LKG pin): 3 + 5 + 4 + 4 = 16, x2 = 32 entries = **2.5 KB**.
ALTERNATIVES REJECTED: (i) in-place two-copy counter with CRC: needs erase or rewrite, which has the torn-page failure mode and on ECC flash is illegal; (ii) hardware monotonic counter only: tiny, but no slot data and not portable; (iii) single unary fuse thermometer for everything: cannot hold 32 B hashes.
ASSUMPTIONS: HAL normalises polarity so unprogrammed = 0 (E.3). A torn unit may read back unstable for a while; VOID plus the exact-tag rule make the late flip of a marginal bit harmless: a torn entry's tag cannot become valid, and VOID has 128 bits, any set bit voids it.
TRADE-OFFS: 10 KB of flash that can never be reclaimed. LIMITS: when the log is full, `append` returns -3 and the device stays in its last committed state (safe-fail) and reports exhaustion; recovery is replacement. VALIDATE: `test_journal.c` (done); TLA+ model of append/recover; physical torn-program characterisation per part family (not done).

**Power-fail cases (measured by simulation, 6,720 runs):** cut before HDR, between HDR and TAG, or with a torn TAG unit: state = pre-state exactly; cut after TAG: state = post-state exactly; after any debris a subsequent append succeeds.

**JM-B (rotate with erase), specified, not implemented.** Two or more journal sectors; sector header with sector-seq and SNAP_DONE unit. When active sector is full: write a snapshot of live state (4 slots + floor + LKG = 6 entries) into the next sector, program SNAP_DONE, *then* erase the old one. Boot picks the highest-seq sector with SNAP_DONE. Needs `FS_CAP_NV_ERASE_JOURNAL` and lock-until-reset on journal sectors. Adds about 400-600 B and two proof obligations [E]. It gives unbounded lifetime on flash with erase, at the price of the one non-monotone operation inside the germline. Given 41 entries over 25 years, wear is irrelevant (endurance is not the limit; the capacity budget is), so **JM-A is the default and JM-B is a profile option only for assets planned beyond 40 years**. [I]

**Medium analysis.**

| Medium | Write semantics | Fit | Notes |
|---|---|---|---|
| NOR flash with ECC word (e.g. 16 B) | erase to all-ones, program once per word | JM-A native; PU = 16 | HAL inverts polarity. Torn program is a real case. |
| NOR flash 4-byte words, 2 programs/word allowed | | JM-A with PU = 4 | Entry = 20 PUs. Do not rely on 2nd program. |
| OTP / UICR OTP | program once, no erase | JM-A native, capacity fixed | Best for 4 slot hashes + thermometer floor; NSIB-style parts (below) |
| eFuse | bit-wise one-way, ms program, may need factory-only voltage | thermometer for kf only; slots in flash journal | usually too small for hashes; per-part |
| FRAM | in-place rewrite, huge endurance | JM-A works unchanged; in-place counters tempting but break monotonicity under lock failure | use append anyway |
| RRAM/MRAM | in-place, unit-write | as FRAM | per-part ECC/write-buffer behaviour: check datasheet |

A fuse/OTP-first variant for parts with enough OTP: slots (4 x 32 B = 128 B), plus a replacement bank (4 x 32 B), a 64-bit floor thermometer and a 1-bit-per-slot "use replacement" flag: ~264 B OTP [C]. Prior art: Nordic's immutable bootloader library stores lifecycle state, hashes of public keys, invalidation tokens and a monotonic counter in OTP, or in internal flash with write blocked before the next image runs [F, `sdk-nrf doc/nrf/libraries/security/bootloader/bl_storage.rst`, clone 2026-11-04]. Nordic counters use a multi-slot scheme, my design differs in carrying 32 B payloads and a commit tag.

### E.1.5 Authority changes (floor advance, slot replacement)

Floor advance `ADVANCE_FLOOR(from_kf -> new_kf, new_svn)`:
1. Bundle `kind=2` signed by a quorum; each signature over `Hash_class(bundle)`; bundle names `from_kf`, must equal current `kf` (replay protection: kf is strictly increasing so a bundle is single-use).
2. Quorum Q = signers whose slot has `gen >= new_kf` (survivors) and whose `pk` hashes to the slot commitment. Valid iff Q contains two members with disjoint assumption masks (`a.mask & b.mask == 0`).
3. Retiring slot k is done *by* raising kf above `slot[k].gen`; slot k may not sign its own retirement (it is not in Q).
4. Append FLOOR entry; reload; continue boot.

Slot replacement `REPLACE_SLOT(slot, from_gen, new_hash, new_gen)`: same quorum, `new_gen >= kf`, `from_gen == slot[slot].gen` (single-use per generation). PAM rule (atlas 11.2): a bundle that would install a hash equal to a *current* live slot's, or revoke a current slot without escrow-class evidence, is structurally rejected. Single entry, single commit: atomic.

**DECISION E-3 (independence needs independent verifier code).** In FS1 the independent quorum classes are **SHA-2 (LMS-SHA256) and Keccak (LMS-SHAKE256)**, verified by the *same locked code*. The atlas HA-1 puts ML-DSA verification in the second stage "under the slot's key hash". That does not give independence: whoever breaks SHA-2 can forge the S2 signature, replace S2 with a version that reports "ML-DSA valid", and the lattice member of the quorum is then not independent. An ML-DSA member counts as independent only if its verifier is in locked flash (pqm4 clean ML-DSA-65 verify code is 7,724 B .text [D], plus the SHAKE it already shares) or in hardware with its own lock (Caliptra's Adams Bridge, vendor ROM). [I]
WHY: independence is a property of the *trust path*, not the key. ALTERNATIVES REJECTED: SLH-DSA-SHAKE in FS1 (signature 7,856 B and, per pqm4, SHAKE-128s verify costs 24.4M cycles on M4 [D]); lattice in FS1 on C2 (7.7 KB flash and 9.9 KB (m4f) or 2.7 KB (m4fstack) stack, at 2.4M-5.7M cycles [D]); both only at C3/C4 with enough flash. ASSUMPTIONS: LMS-SHAKE is acceptable to the policy authority (SP 800-208 defines the SHAKE typecodes; typecodes cross-checked against pyhsslms 2.0.0, which I did not verify against the SP text directly [I]). TRADE-OFFS: both slots in FS1 are stateful hash-based, so the index-reuse hazard (R6) is concentrated at the authority side; mitigated by HSM index reservation and by using the leaf budget only for rare authority and root-level signing (atlas 11.1 interim note; SP 800-230 draft limited-use SLH-DSA is [F, IPD April 2026, `csrc.nist.gov/news/2026/nist-releases-draft-sp-800-230`] a later option). LIMITS: this is atlas correction candidate C-E1 (E.11). VALIDATE: quorum checker (atlas E-N3) as a property test over the slot table.

**LMS parameter choice for FS1 [E-derived from measured counts]:**

| Param set | Signature | Avg hash calls (measured, H5) | Notes |
|---|---|---|---|
| W4, H10 | 2,508 B | ~510 (+~5 for H10) | atlas default; 1,024 leaves |
| W8, H10 | 1,452 B | 3,800-5,100 | 8x slower in software, 1.7x smaller; choose only with HW hash |
| W2, H10 | 4,460 B (H5 measured 4,460 B... at H5; H10 = 4,620 B) [C] | 182 | for very slow cores; LoRa-hostile |

(`4+4+32+133*32+4+10*32 = 4,620 B` for W2/H10 [C]; the measured 4,460 B above is H5.)

---

## E.2 Integration review (what to reuse, wrap, avoid)

Method: shallow clones of upstream repos (dates below) grepped for PQ algorithm support, plus primary documentation fetched this session. "Unverified" means I did not read a primary source for the claim.

| Component | PQ status found | Evidence | Verdict |
|---|---|---|---|
| **MCUboot** | **No PQ in main.** Clone of 2026-10-29 (HEAD `420a2d5`) has no LMS/ML-DSA/XMSS in docs, Kconfig or source. A commit `c6aeaf9` by a contributor adds `docs/lms.md` describing LMS verification (Mbed TLS 4.x, imgtool, bootloader verifier); it is **not in the cloned HEAD**, so treat as an unmerged branch or PR, date approximate (~May 2026) | [F: repo grep; WebFetch of the commit] | **Wrap, do not depend.** MCUboot's image format, trailer, swap and upgrade logic are good S2/app-level material. FS1's journal and quorum stay outside it. Track the LMS work and align `imgtool` manifest fields. |
| **wolfBoot 2.10.0** (clone 2026-11-04) | **ML-DSA (44/65/87), LMS/HSS, XMSS/XMSS^MT**, hybrid classic+PQ mode (e.g. ML-DSA-65 + ECC-384) via a secondary signature; docs `docs/PQ.md`; `docs/FIPS.md` states PQ options are out of scope of its FIPS statement | [F: repo files] | **Reuse as S2 and as a reference/diff target**; strongest open-source PQ boot today. Not suitable as FS1: monolithic, flash footprint in the tens of KB (unmeasured), no disjoint-quorum floor rule, no append-only journal. Adopt its config naming where possible. |
| **TF-M** (Arm) | Unverified this session (my clone attempt of the mirror failed). PSA Crypto API has PQC extension (below); TF-M adoption not checked | none | Reuse PSA crypto *API shape* for S2/app; FS1 does not use TF-M. Verify TF-M release notes before claiming support. |
| **PSA Certified Crypto API** | **PQC Extension 1.4: Final 0 and Final 1 exist**; covers ML-KEM, ML-DSA, SLH-DSA, and LMS/HSS and XMSS/XMSS^MT *verification and public keys*; document history lists no dates | [F: `arm-software.github.io/psa-api/crypto/1.4/ext-pqc/appendix/history.html`] | **Adopt as the S2/app crypto API** (E.3.4). FS1 keeps its own two-function verify (`fs_lms_verify`). |
| **Nordic NSIB / nRF Connect SDK** | NSIB (`b0`) signature choices in `sysbuild/Kconfig.secureboot`: **ED25519, ECDSA, NONE only**. PQ is in the PSA/CRACEN driver: ML-DSA-44/65/87 sign+verify and ML-KEM-512/768/1024 for CRACEN, SHAKE in CRACEN on nRF54L (release notes 3.5.0-preview4); LMS/HSS/XMSS public-key types exist as PSA options; Oberon PQC marked experimental in 3.4.0 notes | [F: sdk-nrf clone 2026-11-04] | **Reuse patterns, not code.** NSIB's OTP key hashes + invalidation tokens + monotonic counter are the closest prior art to FS1. Gap: no PQ verifier in the immutable stage. |
| **ST OEMiRoT / SBSFU / X-CUBE-PQC** | **X-CUBE-PQC**: LMS and XMSS verification "mainly for secure boot", ML-KEM, ML-DSA; **STM32H563 (Cortex-M33) only; status NRND**, ST points to X-CUBE-CRYPTOLIB; page does not mention OEMiRoT/SBSFU | [F: `st.com/en/embedded-software/x-cube-pqc.html`] | OEMiRoT/SBSFU PQ status **unverified**. Treat ST as: PQ verify libraries exist for one part, root-of-trust integration not shown. Hardware lock features (RDP/HDP/WRP) are what FS1 needs; per-part check (E.3.3). |
| **Zephyr** | Unverified this session. Uses MCUboot (above); PSA crypto via Mbed TLS/TF-M | none | Target as an *OS* for S2/app; FS1 independent of it. |
| **FreeRTOS-Kernel** | No PQ strings in the kernel repo (clone 2026-10-29) | [F: grep] | Kernel is not the place for crypto; use with wolfSSL/PSA libs. |
| **Eclipse ThreadX / NetX Duo** | No ML-DSA/ML-KEM/LMS/XMSS strings in `threadx` or `netxduo` clones (2026-11-01) | [F: grep] | Same as FreeRTOS. ThreadX's value is its safety-certification lineage (unverified specifics). |
| **Arm PSA Certified** | Certification levels cover the crypto API conformance; whether an evaluated profile covers PQ is unverified | partial | Record certificate IDs in the part profile (E.3.3), do not infer PQ. |
| **OpenTitan** | Earl Grey ROM docs: "required to support hybrid signature schemes for secure boot ... ECDSA-P256-SHA256 and SLH-DSA" | [F: `sw/device/silicon_creator/rom/doc/sigverify.md`, clone 2026-10-09] | **Align**: OpenTitan validates the hybrid-with-SLH-DSA approach in silicon ROM. Use its SLH-DSA test keys format as an interop target. |
| **Caliptra** | Repo README lists `lms-types`; Caliptra 2.0/2.1 added Adams Bridge ML-DSA/ML-KEM accelerator (atlas 8.5, [F] per atlas; not re-verified here) | [F partial] | **Wrap as a RoT backend** via the HAL `verify` capability for C4/C5 and SoC-class parts. |
| **U-Boot** | Bundled Mbed TLS 3.6.0 contains **LMS verify (LMS_SHA256_M32_H10 only, per its ChangeLog)**; no ML-DSA in U-Boot docs/boot; wiring of LMS into verified boot not found | [F: grep of clone 2026-11-05] | Linux-class: use U-Boot as S2, put FS1-equivalent in vendor ROM or locked SPL, see E.9. |
| **RAUC / Mender** | No PQ strings in clones (2026-11-05 / 2026-10-28) | [F: grep] | Wrap: they carry artifacts; signatures verified by our policy layer. |
| **SWUpdate** | Kconfig option `CMS_REQUIRE_HYBRID_PQC`: requires at least one classic and one PQ (ML-DSA, SLH-DSA) CMS signer, with a stated stripped-signer downgrade rationale; depends on OpenSSL | [F: `crypto/Kconfig`, clone 2026-11-02] | **Reuse the idea** (and the downgrade threat note) as a policy template; best-positioned Linux updater found. |
| **systemd, UEFI, Linux kernel module signing** | Not checked this session | none | Unverified: E.9 treats them as interfaces only. |

**DECISION E-4 (integration stance).** FS1 is standalone C with a six-function HAL; nothing from MCUboot/TF-M/Zephyr is linked into it. Upstream projects are integrated at **S2 and above** through (i) the PSA crypto PQC extension API, (ii) the manifest and sigblock formats being a superset-compatible profile for MCUboot/wolfBoot image headers, (iii) a conformance adapter per bootloader. WHY: every dependency inside the germline becomes unfixable. ALTERNATIVES REJECTED: forking wolfBoot as FS1 (size, licence entanglement [GPLv3 vs commercial, unverified], no quorum logic); wrapping TF-M BL1 (needs ROM or TrustZone). ASSUMPTIONS: wolfBoot/MCUboot keep their PQ work upstream. LIMITS: the version-field mapping (svn vs kf) must be negotiated with each project. VALIDATE: golden-image interop tests (E.3.5).

---

## E.3 Hardware abstraction layer

### E.3.1 Contract

Header: `fs/fs_hal.h` (written; C99, freestanding). Required: `nv_read`, `nv_prog` (with `FS_CAP_NV_PROG_ONCE`), `img_read`, `lock_until_reset`, `jump`. Optional: everything else; absent hooks degrade features, never silently.

| Function | Needed by | Contract |
|---|---|---|
| `nv_read(off,dst,n)` | journal | **Polarity-normalised: unprogrammed = 0, programmed = 1.** Idempotent. |
| `nv_prog(off,src,n)` | journal | OR-semantics; `off, n` multiples of `nv_pu`; each unit programmed at most once; returns on completion; power loss may leave a bit-subset of `src` OR-ed in. |
| `nv_erase(off)` | JM-B | optional |
| `img_read/img_map` | verify | no side effects |
| `lock_until_reset` | handover | after return, S2 cannot program/erase FS1 or the journal; verified by read-back of the vendor lock register where possible |
| `wdt_kick`, `safe_state` | boot | `safe_state` drives outputs to declared safe state before BRICK_GUARD |
| `debug_state` | evidence | CLOSED/OPEN/AUTHENTICATED/UNKNOWN is *recorded* in the first signed state report; FS1 does not enforce |
| `rng` | **not used by FS1** | present for the contract; verification needs no entropy (a property worth keeping: no RNG failure can break boot) |
| `rtc_read(unix, uncert)` | reports | returns a window (E.7); never authority |
| `ctr_read/ctr_inc` | optional hardware counter | cross-check of kf where present |
| `sha256_blocks`, `keccak_f1600` | speed | replace the software block function |
| `caps` bits | | 13 defined in `fs_hal.h` (`NV_PROG_ONCE`, `NV_ERASE_JOURNAL`, `LOCK_UNTIL_RESET`, `LOCK_PERMANENT`, `NV_MARGIN_READ`, `HW_SHA256`, `HW_KECCAK`, `HW_CTR`, `RTC`, `RNG`, `WDT`, `DEBUG_QUERY`, `IMG_MEMMAP`) |

**DECISION E-5 (HAL = data + function table, ABI-versioned).** `fs_hal.abi == 1`, struct is append-only (new fields at the end, `abi` bumped), no callbacks with varargs, no ownership transfer. WHY: FS1 can never be recompiled in the field, but S2 and the HAL tables can be, so the ABI must be stable for decades. ALTERNATIVES REJECTED: link-time weak symbols (hard to test, silent fallbacks); Rust traits (not C-linkable for vendors). VALIDATE: ABI test compiled with both compilers asserting `offsetof/sizeof` of `fs_hal` identical.

### E.3.2 Porting guide (10 steps)

1. Fill a **part profile** (E.3.3) from datasheets and certificates, with source per field.
2. Choose layout (E.1.2) aligned to the lock granularity; if the lock cannot protect FS1+journal as one region, split, but then each region needs its own lock.
3. Implement `nv_*` with polarity inversion for NOR; confirm PU and that the same unit is never written twice (ECC).
4. Implement `lock_until_reset` using the vendor's write-protect-until-reset feature (or permanent lock for FS1 code; journal must remain programmable by FS1 only).
5. Implement `img_read` (and map).
6. Wire `jump`: clear RAM, set VTOR, set MSP, branch.
7. Run **HAL contract tests** (below) on target.
8. Run the **power-cut rig**: toggle power at randomised times during journal append over thousands of cycles; check recovery.
9. Run the conformance vectors (LMS vectors above; image vectors) through a real boot.
10. Archive the profile, test logs and binary hash in the CBOM entry.

### E.3.3 Machine-readable part profile

Format: TOML (human editable, schema-validated, signed when published). Physical-resistance class is a **data field with a source and a date, never a claim by us**.

```toml
schema = "part-profile/1"
part = { vendor = "…", family = "…", core = "cortex-m33", rev = "…" }
nv = { kind = "nor", program_unit = 16, ecc_single_program = true, erase_unit = 8192,
       polarity = "erased_ones", otp_bytes = 0, journal_ok = "JM-A" }
lock = { granularity_bytes = 8192, until_reset = true, permanent = true,
         survives_lifecycle = ["RMA"= "unknown"], source = "ref-manual §…, 2025-xx" }
hash = { sha256_hw = true, keccak_hw = false, source = "…" }
counters = { hw_monotonic_bits = 0 }
debug = { states = ["closed","open","authenticated"], pq_credential_supported = false }
evidence = [ { scheme = "…", level = "…", lab = "…", cert_id = "…", scope = "…", date = "…", source = "URL" } ]
physical_resistance = { class = "unknown|none-claimed|vendor-claimed|independently-evaluated",
                        source = "…", date = "…", note = "absence of evidence is not proof" }
```
Rules: fields without a source are `unknown`; `physical_resistance.class` can only be `independently-evaluated` if a `cert_id` is present; the profile is hashed and recorded in the device's CBOM entry (atlas 8.2, 8.10 rule 4). No attack procedure, parameter or cost appears anywhere in a profile (brief rule 3).

### E.3.4 HAL contract tests (conformance suite "HCT")

Runs on target via a tiny test image; reports through `log`. Items:
- **T1 polarity**: fresh unit reads 0; after programming 0xFF.. reads 1s.
- **T2 program-once**: HAL must refuse or report the second program of a unit (profile-declared); test records vendor behaviour.
- **T3 OR-semantics and alignment**: unaligned write rejected.
- **T4 torn-write rig**: 5,000 randomised power cuts during `nv_prog`; check that reading back yields a subset of intended bits, and that `fs_journal_load` recovers (the `test_journal.c` invariants on silicon).
- **T5 lock**: after `lock_until_reset`, an S2-privilege write to FS1 region and journal region must fail; check from an unprivileged probe image. Also check that the lock survives a warm reset path the vendor documents as preserving it (profile field).
- **T6 hash KATs** for the accelerators vs software; **T7 LMS vectors** (the 21 vectors + 903 negatives from this stream).
- **T8 watchdog** reset-in-time test; **T9 debug_state** truth table; **T10 rtc** monotonicity.
- Gate: a port is "FS1-certified-by-us" only with T1-T7 green, with the log attached to the profile.

---

## E.4 Device classes C0-C5: concrete profiles

Data used (all pqm4, STM32F4 Cortex-M4 @ 24 MHz, gcc 11.3.1, repo clone 2026-10-23, [D]):

| Scheme (impl.) | Cycles | Stack B | .text B | Time @24 MHz | @64 MHz [C] |
|---|---|---|---|---|---|
| ML-KEM-768 decaps (m4fspeed) | 707,827 | 6,452 | .text 16,016 | 29.5 ms | 11.1 ms |
| ML-KEM-768 decaps (m4fstack) | 714,194 | 2,844 | .text 13,320 | 29.8 ms | 11.2 ms |
| ML-KEM-768 decaps (clean C) | 1,387,984 | 14,480 | | 57.8 ms | 21.7 ms |
| ML-KEM-768 encaps (m4fspeed) | 658,754 | | | 27.4 ms | 10.3 ms |
| ML-DSA-65 verify (m4f) | 2,415,944 | 9,888 | 19,328 | 100.7 ms | 37.7 ms |
| ML-DSA-65 verify (m4fstack) | 5,732,397 | 2,712 | 24,120 | 238.9 ms | 89.6 ms |
| ML-DSA-65 verify (clean) | 3,377,305 | 57,736 | 7,724 | 140.7 ms | 52.8 ms |
| SLH-DSA-SHA2-128s-simple verify (sphincs-sha2-128s clean) | 7,471,794 | 1,968 | 5,264 | 311 ms | 116.7 ms |
| SLH-DSA-SHAKE-128s-simple verify | 24,366,771 | 1,872 | 4,492 | 1,015 ms | 380.7 ms |

(Note: stack rows from the pqm4 memory section: ML-KEM-768 decaps 14,480 B clean, 6,452 B m4fspeed, 2,844 B m4fstack; .text for ML-KEM-768 m4fspeed is 16,016 B from the size section. Conversion to 64 MHz assumes no flash wait-state penalty [E]; pqm4 measured at 24 MHz to avoid wait states.)

**Atlas check.** Atlas 11.3: "decapsulation costs 22 ms and 14.2 KB of stack on an M0+". pqm4's *clean C* ML-KEM-768 decaps on a **Cortex-M4** shows 14,480 B stack, which matches the 14.2 KB order of magnitude, so the stack figure is plausible for an unoptimised build; the 22 ms is of the same order as clean-C cycles at 64 MHz on M4 (21.7 ms), but I found **no M0+ primary source**. Flag: the M0+ figure is unverified [I]; an M0+ has no single-cycle 32x32->64 multiply, so lattice code is expected slower than on M4 (factor to be measured, not asserted).

LMS (measured block counts, E.1; cycles/block assumed). The atlas card gives 41.5 ms for W4 software at 64 MHz = 2.66M cycles. With ~560 compression blocks average (calls + 33 extra blocks for the 2,166 B public-key hash + ~10 for 2-block Merkle nodes [C]) that implies ~4.7k cycles per SHA-256 block, the figure I use throughout (assumption [E]; a tuned M0+ implementation may be lower; mbedTLS-class C is plausibly at this order, unverified).
- W4/H10 average ≈ 560 blocks x 4.7k = 2.63M cycles = **41 ms @ 64 MHz, 55 ms @ 48 MHz, 164 ms @ 16 MHz**. Worst case (all 67 chain digits maximal: 1,005 chain steps + 34 + ~22) ≈ 1,061 blocks = 4.99M cycles = **78 ms @ 64 MHz** [C]. This worst case sets the watchdog budget.
- W8: measured 3,833-5,108 calls (avg ~4,350 + ~45) x 4.7k ≈ 20.7M cycles = 323 ms @ 64 MHz average [C].
- HW SHA-256 at an assumed 300 cycles/block including driver overhead [E]: 560 x 300 = 168k cycles = 2.6 ms @ 64 MHz.
- Image hash (done at every boot): size/64 blocks. 64 KB: 1,024 blocks = 75 ms (sw) / 4.8 ms (hw) @ 64 MHz; 256 KB: 301 / 19 ms; 512 KB: 602 / 38 ms; 1 MB: 1.2 s / 77 ms [C, E assumptions as above]. **Image hashing, not signature verification, dominates boot latency on C2/C3**, so a hash engine is worth more than a faster verifier.
- SHAKE256 (Keccak) software: not benchmarked; estimating 24 rounds x ~700 cycles = ~17k cycles per f-1600 permutation on M0+ [E, weak], ~570 permutations -> ~10M cycles = 150 ms @ 64 MHz; make a Keccak engine or the hash-first design (E.1.4) optional for the second class on C1/C2.

Per-class profile (modules linked; flash/RAM from measured and estimated data):

| Class | Typical MCU | Modules linked | Flash (FS1 + libs) | RAM | Verify / boot latency (arithmetic above) |
|---|---|---|---|---|---|
| **C0** inert | no crypto | none; enclave inventory only | 0 | 0 | n/a. Replacement date in CBOM. |
| **C1** symmetric-only (M0+/M0, 16-64 KB flash) | LoRaWAN/802.15.4 node | HAL, `fs_hash` SHA-256 only (~1 KB less than 1,922 [E]), AES-CMAC/GMAC from vendor lib; **optional** FS1 LMS (W4/H10) if updatable | MAC-only: 0 KB FS1; FS1-SHA256-only: ~5 KB [E: 3,962-1,000+2,600+1,000]; journal 2.5 KB | ~1.0 KB stack (verify 688 minus SHAKE ctx ~480 + hash 160 [E]) | LMS verify 55 ms @ 48 MHz [E]; image hash 32 KB: 512 blocks = 2.4M cycles = 50 ms @ 48 MHz |
| **C2** verify-capable (M4/M33, 256 KB-2 MB) | PLC I/O, RTU, IED | FS1 (SHA-256 + SHAKE, journal 10 KB), PSA crypto in S2 incl. ML-KEM-768 decaps once, optional ML-DSA-65 verify in S2 | FS1 ~7.6 KB (8 KB) + journal 10 KB = **~18 KB**; S2 ML-KEM 6-10 KB .text [D, size section] + ML-DSA 8-24 KB [D] | FS1 ~1.4 KB; S2 PQ ops 3-10 KB transient (m4fstack 2.8 KB decaps; ML-DSA-65 verify 2.7-9.9 KB) | boot: hash 256 KB image 19 ms (hw) to 301 ms (sw) @ 64 MHz + LMS 2.6-41 ms; ML-DSA-65 verify 38 ms (m4f) @ 64 MHz in S2 |
| **C3** safety-critical | protection relays, SIS | C2 + LKG pin, DISJOINT2 policy (both hashes; both LMS verifies), crypto partition (E.5), signed settings | FS1 ~8 KB + journal 10 KB; DISJOINT2 needs 2 LMS verifies | FS1 1.4 KB, **crypto runs only in boot/update, never in control loop** | worst case: 2 x 78 ms + 2-pass image hash; budget declared per product in WCET table; must complete before the control task start deadline; boot is not a control period |
| **C4** concentrators (A-class, Linux) | gateways, KDCs, historians | full stacks; TLS/IKE hybrids (liboqs/wolfSSL/OpenSSL), TPM; see E.9 | MBs | MBs | ms |
| **C5** authorities | HSMs | out of embedded scope (Streams A-C) | | | |

**C0-C1 guard (dominance rule, atlas 12.2):** FS1 never accepts an authority change from a lower-class device; FS1's input is a signed bundle only, so a C1 gateway/relay path cannot present anything but bytes, and quorum check decides. [I]

---

## E.5 Real-time and safety coexistence

**DECISION E-6 (crypto is a boot-and-update service, never a control-loop dependency).** On C3: all public-key operations are confined to FS1 and an S2 "update agent" task that is **not schedulable above the control task**; run-time process-bus security is symmetric (atlas 11.3). WHY: EN 50159-style separation: the safety layer sees authenticated frames, the crypto layer can be replaced without reopening the safety case (atlas Part 0 item 3). ALTERNATIVES REJECTED: PQ signatures per message (SV at 4,000 frames/s leaves 250 us per frame vs 12-41 ms for one LMS verify, 49-164x over budget [C]); crypto co-processor shared with control. ASSUMPTIONS: MPU or TrustZone separates the update agent. LIMITS: the update agent can still starve the CPU unless bounded. VALIDATE: WCET measurement of the update task and a schedulability proof with it as the lowest-priority, preemptible task.

Mechanisms:
1. **Partitioning.** MPU regions: S2 update agent (crypto + parsers) in its own unprivileged partition with fixed RAM; control task cannot be written by it; crypto never takes a lock the control loop needs.
2. **Watchdog budget.** Window W must exceed worst-case FS1 time: `T_boot,max = T_hash(image) + n_verifies x T_LMS,max + T_journal`. For a 256 KB image at 16 MHz, sw hash: 4,096 x 4.7k / 16M = 1.20 s; LMS worst 1,061 x 4.7k / 16M = 312 ms (x2 for DISJOINT2) [C] -> watchdog (or kick calls inside the hash loop every N blocks, N = 64 ~19 ms @ 16 MHz) so that a hung hash cannot starve the dog. FS1 kicks `wdt_kick` between verifier phases, not inside primitives.
3. **Deterministic WCET.** All FS1 loops are bounded by table constants (p <= 133 chains (W2), 2^w-1 <= 255, h <= 25, image blocks <= img_len/64); no data-dependent early exit in the signature check except the final compare; no recursion; no heap; no function pointers except the fixed HAL table. Report: WCET table by `(alg, W, H, image KB)` generated from block counts (above), and *measured on silicon* per part before certification [not done].
4. **Fail-safe.** BRICK_GUARD calls `safe_state`; LKG keeps control running with network authority removed (senescence, atlas 11.6); no state where a control output depends on a signature check *result* at run time.
5. **Certification-friendly library requirements** (what the library must provide; labels [I] - the standards were not fetched this session, no clause numbers asserted):

| Requirement | Why a certifier asks | FS1 status |
|---|---|---|
| No dynamic allocation | IEC 61508 / ISO 26262 software constraints on dynamic objects | **Met** (no malloc; stack and static only) |
| No recursion, bounded loops | WCET and stack analysis | **Met by construction**; to be proven by tool (Frama-C/CBMC) |
| Static stack bound | resource analysis | **Measured** frames above; add whole-call-graph tool |
| MISRA C:2012/2023 conformance, with a deviation log | typical project coding standard in IEC 61508 SIL 2+, ISO 26262 ASIL | **Not yet checked** (no MISRA checker available here); known deviations: union in hash context, `memcpy`, packed structs |
| Static-analysis evidence (clang-tidy/Frama-C/Polyspace/cppcheck) | evidence of absence of run-time errors | planned; 0 cppcheck/clang run yet [not done] |
| Test evidence with coverage (MC/DC for ASIL D / DAL A / SIL 4) | structural coverage | 903 negative + 21 positive LMS vectors, 6,720 journal cuts are functional only; coverage not measured |
| WCET table | timing analysis | estimated above, silicon measurement pending |
| Traceability requirement -> code -> test | all standards | this memo's IDs (E-n) and atlas IDs |
| Tool qualification of compilers | ISO 26262 tool confidence, IEC 61508 | E.8: two compilers + qualified commercial option |
| Safety manual and "assumptions of use" | SEooC (ISO 26262), IEC 61508 route 1s/2s | to write per profile |
| Separation of security and safety lifecycles | IEC 62443-4-1/-4-2, DO-326A airworthiness security process | design keeps crypto out of safety function; mapping tables are a Stream F matter |
| IEC 62304 (medical): SOUP | software of unknown provenance record | FS1 is first-party, but wolfSSL/PSA libs in S2 are SOUP: record version, anomaly list |

**Position on library certification.** The first stage is small enough (one verifier, <1,000 lines) to qualify as a **SEooC/pre-certified component** with an assumptions-of-use list (lock call, polarity, PU rule); the S2 PQ stack is not (tens of KB, upstream-owned): certify the *interface* and its partitioning, not the lattice code.

---

## E.6 Power and bandwidth

Assumptions (labelled): active current **4 mA at 3.0 V at 48 MHz** for an M0+-class part (typical order, [E], no datasheet cited); LoRa transmit **40 mA** and receive **10 mA** at 3.3 V (typical order, [E]); CR2032 nominal 225 mAh x 3 V = 2,430 J [I].

**Compute energy** E = V x I x t:
- LMS W4/H10 verify, software, 48 MHz: 2.63M cycles / 48 MHz = 54.8 ms; 3.0 x 0.004 x 0.0548 = **0.66 mJ** [E]. Worst case 78 ms @ 64 MHz scaling to 104 ms @ 48 MHz: 1.25 mJ.
- With HW SHA at 300 cycles/block: 560 x 300 = 168k cycles = 3.5 ms: **0.042 mJ** [E].
- ML-KEM-768 decaps (once), M4 24 MHz measured 707,827 cycles = 14.7 ms @ 48 MHz; at 4 mA, 3 V: **0.18 mJ**; if M0+ is 2.5x slower [E, unverified factor]: **0.44 mJ**.
- Image hash 32 KB (512 blocks): 2.4M cycles at 48 MHz = 50 ms = **0.60 mJ**.
All are below 1 mJ. 2,430 J / 0.66 mJ = 3.7M verifications [C]: **compute is irrelevant to battery life; radio dominates**.

**Radio:** LoRaWAN at SF10/125 kHz, 51 B application payload per frame (consistent with the atlas card 24 frames for an ML-KEM-768 key, 65 for ML-DSA-65: 1,184/51 = 23.2 -> 24; 3,309/51 = 64.9 -> 65 [C]). Time on air for a 64 B PHY payload (51 + 13 B header) at SF10: 698 ms; SF7 118 ms; SF12 2.79 s [C, Semtech formula, CR 4/5, 8-symbol preamble, CRC on, explicit header; I did not re-verify against Semtech's calculator]. Artifact delivery:

| Artifact | Bytes | LoRa frames @51 B | Airtime SF10 | Time at 1% duty | 802.15.4 frames @~88 B payload [E] |
|---|---|---|---|---|---|
| LMS W4/H10 signature | 2,508 | 50 | 34.9 s | 0.97 h | 29 |
| LMS W8/H10 signature | 1,452 | 29 | 20.3 s | 0.56 h | 17 |
| ML-DSA-44 signature | 2,420 | 48 | 33.5 s | 0.93 h | 28 |
| ML-DSA-65 signature | 3,309 | 65 | 45.4 s | 1.26 h | 38 |
| SLH-DSA-128s signature | 7,856 | 155 | 108.2 s | 3.01 h | 90 |
| ML-KEM-768 encaps key | 1,184 | 24 | 16.8 s | 0.47 h | 14 |
| ML-KEM-768 ciphertext | 1,088 | 22 | 15.4 s | 0.43 h | 13 |

(Duty-cycle column uses 1% as the EU868 sub-band order; applies to *uplink*; class-A downlinks are limited by gateway duty cycle and RX windows instead. I did not verify regional rules this session.) Energy for a device *receiving* 50 downlink frames: 50 x ~1 s x 10 mA x 3.3 V = **1.65 J** [E] vs 0.66 mJ to verify: **2,500x**. Uplink of an ML-KEM key (24 frames x 0.698 s x 40 mA x 3.3 V) = **2.2 J** [E].

**DECISION E-7 (C1 over LoRa: do not ship PQ signatures to the node).** For C1 nodes, authenticate via the diversified symmetric key; do enrolment with ML-KEM *at the gateway* (atlas 11.3; N10) and deliver firmware only as hash-chained differential updates verified against an FS1-anchored manifest delivered once per release, never per fragment. WHY: 50 frames x 0.7 s per signature. ALTERNATIVES REJECTED: SLH-DSA on node (155 frames, 7.9 KB); per-fragment signature. LIMITS: a full image at 51 B/frame (a 64 KB image = 1,285 frames, 15 min of airtime at SF10 [C]) is operationally hard; the unit that matters is *delta size*.

**Update delta strategies** [I/H unless noted]:
1. **Hash-chained fragments** (each fragment carries the hash of the next; manifest signed once): O(1) signature overhead; classical block authentication; needs in-order delivery or a Merkle tree. Merkle tree with 64-B leaves: proof depth log2(1,024) = 10 hashes x 32 B = 320 B per fragment for a 64 KB image, which is more than the fragment, so chain, not tree, for LoRa. [C]
2. **Differential (bsdiff/Janpatch-class, or block-level) updates** decoded by S2 into the inactive slot; signature covers the *result* hash, so the delta itself need not be signed, but the delta must be *bound* to the base hash to avoid applying to the wrong base. Typical size reduction depends on the change; unmeasured here.
3. **Crypto-only updates** kept separate from functional updates (atlas 11.5, N48): an authority-change bundle (floor/slot) is ~270 B + signatures: bundle 112 B + 2 x 2,508 B sigs = 5,128 B = 101 LoRa frames [C]; for C1 this is why C1 holds no FS1 authority and relies on the gateway.
4. **Staged dormant** download (atlas 11.5) during window prep; activation is a single flag.

---

## E.7 Time handling on devices

**Zeitgeber-stack API** (S2/library, not FS1; FS1 only *reports* the window):

```c
typedef struct { int64_t earliest, latest; } fs_tw;        /* seconds since 1970-01-01, signed 64-bit */
typedef enum { ZG_RTC, ZG_COUNTER_ORDER, ZG_BOOT_REMANENCE, ZG_NET_AUTH, ZG_GRID, ZG_GNSS,
               ZG_TECH_TOKEN, ZG_PEER } fs_zg_kind;
typedef struct { fs_zg_kind kind; uint8_t indep_class; int64_t t; uint32_t uncert_s; } fs_zg_cue;
void fs_time_init(fs_tw *w, int64_t epoch_lo, int64_t epoch_hi, uint32_t drift_ppm);
void fs_time_tick(fs_tw *w, uint32_t elapsed_oscillator_s);       /* widens by drift_ppm */
int  fs_time_propose(fs_tw *w, const fs_zg_cue *cue);            /* 1 narrowed, 0 recorded-only, <0 reject */
int  fs_time_report(const fs_tw *w, uint8_t out[24]);            /* fixed-width signed-report field */
```
**Fusion rule (atlas I-23, 6.5) as code semantics:** window widens at the drift bound; a cue **inside** the window narrows it; a cue **outside** is recorded and ignored **unless at least two cues of different `indep_class` agree** on the new position; time never grants authority: no function in FS1 or the library takes a `fs_tw` as input to advance a floor or change a slot. Window report goes into the signed state report. [H, from atlas]

Drift budget arithmetic (atlas M4 [C], recomputed): 20 ppm x 31,557,600 s/yr = 631 s/yr; -164 ppm worst-case cold = 5,175 s/yr = 86 min; over a decade 14.4 h. Window width after one year with 20 ppm = ±631 s; if validity rules use month-sized epochs the window is far smaller than the epoch. Use coarse epochs (months).

**Monotonic epoch counters**: floor `kf`, `svn_floor` live in the journal; "epoch" semantics are ordinal, not temporal; replay protection uses `from_kf` in bundles.

**Counter-capacity rule (atlas 6.6, E.7 rule)**: for every counter write capacity C, consumption rate r per year, asset life L; require C >= 2 r L.

| Counter | Capacity | Rate | Life | Required | Verdict |
|---|---|---|---|---|---|
| journal entries (JM-A) | 128 | ~1.6/yr | 25 | 82 | pass (1.56x of requirement, 3.1x of expected 41) |
| `kf` (u32 in entry arg0) | 2^32 | 0.2/yr | 40 | tiny | pass |
| LMS h = 10 leaves | 1,024 | rare root signing: ~12/yr | 25 | 600 | pass; nightly signing (365/yr) fails at 2.8 yr (atlas 21.1) |
| fuse thermometer 64 bits | 64 | 0.2/yr | 40 | 16 | pass |
| `time_t` | signed 64-bit | | | | pass; signed 32-bit ends 2038-01-19 03:14:07 UTC |
| GPS week (10-bit) | 1,024 weeks ≈ 19.7 yr | | | next rollover 2038-11-20 (atlas, unverified here) | interpret GPS with pivot date from the build epoch plus the window |

**Y2038/GPS rollover-safe types:** `int64_t` seconds everywhere; GPS weeks stored as 16-bit absolute week-since-1980 reconstructed from the 10-bit field using the window's `earliest` as pivot (valid while true time is within ±512 weeks of the pivot); never `time_t` in a wire struct; compile-time `_Static_assert(sizeof(int64_t)==8)`; CI test injects dates 2038-01-19, 2038-11-20 and 2106-02-07 (u32 end). "No expiry" = notAfter 99991231235959Z as defined value (atlas 6.6, RFC 5280).

---

## E.8 Language strategy for the device side

Options compared:

| Option | Pros | Cons | Fit |
|---|---|---|---|
| **C99/C11 subset, MISRA/CERT, formal-verified** | universal vendor toolchains (every MCU), ABI stable for decades, vendors will link it, WCET tools target it | memory-safety is by discipline and analysis | **FS1 and HAL** |
| Rust `no_std` | memory safety, good for S2 parsers | thumbv6m/v8m support OK (targets installed here), but vendor SDKs C-only; qualification (Ferrocene) exists but unverified here; panic paths, ABI instability beyond `extern "C"` | **S2/app parsers, gateway, tools** |
| Ada/SPARK | proof of absence of RTE, safety heritage | small vendor ecosystem, few RTOS ports, hiring | optional for C3 vendors |
| Verified C extraction (F*/Low*, HACL*; libcrux) | machine-checked memory safety/functional correctness | extraction output is big, build chain heavy | **candidate for the hash/LMS core later**; mlkem-native already uses CBMC proofs of memory safety and HOL-Light proofs for assembly (AArch64/x86_64) [F: mlkem-native README, clone 2026-11-04]; no Cortex-M assembly proof claimed |
| Verus/Rust | verification inside Rust | young, not for C vendors | research |

**DECISION E-8.** FS1, HAL, journal, manifest parser = **C99 subset** (no VLAs, no recursion, no heap, no function pointers except the HAL table, fixed-width types only, `-Os`), verified by (1) deductive proofs with Frama-C/WP or CBMC bounded model of the parser, journal and the quorum rule; (2) the host-side differential tests (done) against an independent implementation (pyhsslms, done) and later a second independent C implementation written by a different team ("implemented twice", atlas 11.1); (3) two-compiler builds. S2 parsers and update agent: **Rust `no_std`** where the vendor allows, with `extern "C"` ABI to the C HAL. WHY: the germline's audience is vendor toolchains for 30+ years; the updatable layers can adopt safer languages. ALTERNATIVES REJECTED: Rust FS1 (no vendor toolchain guarantee; proof tooling for Rust embedded immature [I]); SPARK FS1 (adoption friction); Low*-extracted FS1 (size, build chain) but the *hash and LMS code paths* should be re-based on verified extraction when size permits. ASSUMPTIONS: C compilers 25 years out still accept C99. TRADE-OFFS: C leaves memory-safety to analysis. LIMITS: proofs are not done (state machine and parser: not started). VALIDATE: proof artifacts published with code.

**FFI/ABI stability:** `fs_hal` and all FS1 interfaces are plain C structs with explicit widths and an `abi` field; Rust bindings generated by `bindgen` from the same header, not hand-written; no C++ in any public interface; no `bool`/enum width assumptions on the wire (use `uint8_t`/`uint32_t`).

**Toolchain qualification and compiler diversity.** The evidence from this session: two compilers produce different code size for the same source (e.g. M0+ `-Os`: gcc 3,962 B vs clang 4,717 B; M4 `-O2` clang's hash module 4,492 B vs gcc 2,160 B) [measured]. Policy: (1) FS1 binary is built with **both** gcc and clang; both must pass the full vector suite on target and host (host test passes with gcc 13.3.0 x86-64; I did *not* run the Thumb binaries on target or in an emulator this session); (2) release uses one compiler, the other is a differential check of semantic equivalence by test, not by bit equality; (3) compiler version and flags are pinned in the CBOM; reproducible builds; (4) for C3 products a qualified commercial compiler (IEC 61508 / ISO 26262 tool qualification, availability unverified) replaces one of the two; (5) check the object code for the lock call and the polarity inversion at binary level (compilers may reorder or elide).

---

## E.9 Linux-class devices and gateways (C4, A-class SoCs)

Architecture (high level; component statuses from E.2):
- **FS1-equivalent for Linux-class SoCs**: the immutable stage is the vendor ROM plus a locked SPL/BL2 holding the same slot table and floor concept; FS1 can run as the locked SPL if the SoC provides OTP and a lock. The key-hash slots and floor can live in OTP/fuses (E.1.4 fuse variant) where ROM supports PQ hash tables; otherwise the SPL carries the verifier. U-Boot as S2/BL33: bundled Mbed TLS has LMS verify (SHA-256, H10 only, per ChangeLog [F]) which is a verifier source for LMS-signed FIT images but not a floor mechanism.
- **Updaters** (RAUC, SWUpdate, Mender): wrap, do not fork. SWUpdate's `CMS_REQUIRE_HYBRID_PQC` [F] demonstrates the dual-signature policy that also defeats stripping one signer; adopt that semantic for every Linux updater: **an artifact is valid only if all required classes verify, evaluated by the policy layer, not by counting signatures present**.
- **Measured boot / attestation**: record PQ evidence in CBOM and TCG/IETF RATS formats (atlas 11.7); TPM-based keys per atlas (TPM 2.0 v1.85; not re-verified here).
- **Gateways as keystone nodes (atlas 12.4)**: C4 gateways terminate PQ TLS/IKE hybrids for C0/C1 enclaves; hold per-device KEK diversification via HSM/TPM, never a fleet key. They run full libraries (wolfSSL/OpenSSL/liboqs; ML-KEM-768 decaps ~1 ms on A-class [E] without a benchmark here).
- **UEFI/systemd** (ESP signing, sd-boot, dm-verity measured boot): status of PQ in UEFI Secure Boot and in the Linux kernel module-signing path was **not verified** this session; plan: treat as interfaces; require that any UEFI db/dbx change on C4 gateways be authorised by the same quorum, and that dm-verity root hashes use SHA-256 + SHA-3 in the manifest.
- **Time on gateways**: authenticated time (Roughtime or authenticated PTP) feeds `fs_time_propose` with `ZG_NET_AUTH`; two independent classes (net + GNSS plausibility + tech token) needed to move the window.

**DECISION E-9.** On Linux-class devices, A/B + RAUC/SWUpdate/Mender remain the update mechanism; the **policy layer** (the library's `verify_artifact()` with required-class set) replaces the signature check, and journal/floor state lives in OTP, RPMB or a TPM NV index with write-once semantics. ALTERNATIVES REJECTED: replacing the updater. ASSUMPTIONS: the SoC offers OTP or RPMB. LIMITS: RPMB/NV-index semantics differ per part (profile field). VALIDATE: the SWUpdate-style downgrade/stripping test as an acceptance test.

---

## E.10 Measured data and honest limits

**Methodology.** Source in `code/E/fs/`. Cross-compile: `arm-none-eabi-gcc 13.2.1 (Ubuntu 15:13.2.rel1-2)`, and `clang 18.1.3` with `--target=thumbv6m/thumbv7em/thumbv8m.main-none-eabi`, headers from newlib. Size = `arm-none-eabi-size` text+data of each object (includes rodata tables, excludes startup, vector table, libc `memcpy`/`memset` stubs: **on M0+ gcc may emit calls to `memcpy`/`memset` from libc that are not counted**; add ~100-200 B if the build must supply them [E]). Stack from `-fstack-usage` static frames. Test on host: gcc 13.3.0 x86-64 `-std=c99 -pedantic`.

**What was *not* done:** running the Thumb binaries (no emulator or hardware); cycle measurement; the boot state machine, manifest parser and bundle handler are *designed, not implemented*; no MISRA/Frama-C/CBMC run; no SHAKE timing; no PSA/TF-M integration test.

**Reproduce:** `sh code/E/fs/build/measure.sh`; `cd code/E/fs/host && python3 -I gen_vectors.py vec && gcc -O2 -std=c99 -o test_lms test_lms.c ../fs_lms.c ../fs_hash.c && ./test_lms vec`; `gcc -std=c99 -O1 -o test_journal test_journal.c ../fs_journal.c ../fs_hash.c && ./test_journal`.

## E.11 Findings against the atlas and open questions

1. **C-E1: second-stage ML-DSA verification (atlas 11.1 HA-1) does not give an independent quorum member** (E.1.5). Independence needs the verifier in locked flash or in separately locked hardware. Fix: quorum classes in FS1 are SHA-2 and Keccak via LMS-SHA256/LMS-SHAKE; ML-DSA gives agility at S2 and independence only with a locked verifier.
2. **C-E2: "~13 KB" is a conservative budget**: measured core is 3,962 B (gcc M0+ -Os); complete FS1 estimated ~8 KB (E.1.3). Keep 16 KB allocated for growth; the dominant locked-flash cost is actually the **journal (10 KB)**, not the code.
3. **C-E3: quorum messages must be hashed per class.** A shared SHA-256 digest of the image makes a SHA-2 break forge both signers (E.1.4).
4. **C-E4: "22 ms and 14.2 KB stack on an M0+" for ML-KEM-768 decaps is not supported by pqm4**, which has no M0+ target; on M4 clean C the stack is 14,480 B and time 21.7 ms @ 64 MHz; the stack-optimised M4 build uses 2,844 B.
5. **C-E5: slot count 4 not 3** to allow "provision alongside" without retiring a live key.
6. **MCUboot has no merged PQ support in main as of 2026-10-29** (a docs-only LMS commit exists elsewhere); wolfBoot 2.10.0 is the only open boot-loader found with merged ML-DSA/LMS/XMSS and hybrid. NSIB's immutable bootloader is still ECDSA/ED25519.

Open questions: (a) actual cycle/stack of FS1 on M0+/M33 silicon with and without HW SHA; (b) per-part lock semantics survive warm reset, RMA and debug re-enable (the side-door audit; needs the part-profile corpus); (c) whether SHAKE/Keccak without hardware is too slow for C1/C2 second-class verification (~150 ms estimated, unbenchmarked) and whether SP 800-230 limited-use SLH-DSA or LMS-SHAKE is the better second waist; (d) status of TF-M, Zephyr, ST OEMiRoT/SBSFU, UEFI/systemd/Linux PQ support (unverified); (e) formal proof of the journal and quorum rule; (f) confirm the SHAKE LMS typecodes against SP 800-208 text itself (cross-checked only with pyhsslms).

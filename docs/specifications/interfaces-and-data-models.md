<!-- Title: Interfaces and data models -->
> **Provenance.** Sliced from legacy Rev 4 (`research-archive/legacy-blueprints/L5_Blueprint_Rev4_monolith.md`, matching sections).
> Document level: L2. Evidence labels: [P] proved, [M] machine-checked or measured by a script in this repo, [E] estimate, [S] standard/literature, [H] hypothesis.
> Rev 4 predates the R2 red-team fixes: absent atoms count as compromised and lost, tables must be projection-canonical, a slot holder must co-sign key installation, and presence can be correlated with ownership (see `docs/theory/red-team-r2-findings.md`). Where this text conflicts with those, the R2 document wins.

# 8. Representative interfaces and data models

### 8.1 Kernel messages and intents (W1)

```c
typedef enum {
  AC_MSG_BOOT            = 1,  /* reset: sample presence, select activated image, finish pending commits */
  AC_MSG_PROPOSE_TX      = 2,  /* ac_tx v2 + evidence (signatures, receipts) */
  AC_MSG_CATCH_UP        = 3,  /* chain of ac_tx + final receipt */
  AC_MSG_VERIFY_IMAGE    = 4,  /* image chunks for resumable verification against active digest */
  AC_MSG_HALT            = 5,  /* T0 */
  AC_MSG_REPORT_REQUEST  = 6   /* produce canonical state for ac-report */
} ac_msg_kind_t;

typedef enum {
  AC_INT_NV_WRITE_SNAPSHOT = 1, AC_INT_COUNTER_ADVANCE = 2, AC_INT_BOOT_IMAGE = 3,
  AC_INT_DEBUG_ENABLE_SCOPED = 4, AC_INT_REPORT_READY = 5, AC_INT_REJECT = 6
} ac_intent_kind_t;

typedef struct { ac_msg_kind_t kind; const uint8_t *data; size_t len; } ac_msg_t;
typedef struct { ac_intent_kind_t kind; uint32_t seq; const uint8_t *data; size_t len; } ac_intent_t;
```

**Reset-time flow (locked stage)**, in outline:

```c
ac_status_t locked_stage_main(void) {
  ac_ctx_t ctx; ac_effects_t fx; size_t need;
  AC_TRY(ac_init(&ctx, &providers, &platform));          /* reads snapshot via nv_read_safe   */
  AC_TRY(ac_step(&ctx, &(ac_msg_t){AC_MSG_BOOT,0,0}, &fx, &need)); /* presence sampled here     */
  if (pending_tx_present()) {                            /* staged by the second stage        */
    ac_step(&ctx, &(ac_msg_t){AC_MSG_PROPOSE_TX, pend, pend_len}, &fx, &need);
    platform_execute(&fx);                               /* snapshot write, counter advance   */
  }
  return boot_activated_image(&ctx);                     /* digest from state, never a header */
}
```

### 8.2 Host lint (reference implementation `code/G/lint.py`)

```text
$ ac-lint check fleet-17.labels.cbor --profile dual-terrestrial
tier T1  budget (1,1)   safe=yes  live=yes  |f|=146  |U|=218  |Lo|=20
tier T2  recoverable (1,2 excl. both-families)  safe=yes  live=yes  |f|=111
impossible-by-construction: live after loss of both families (only presence remains)
renewal: OK (3 groups, 2 families, presence, 2 logs)
$ ac-lint simulate --retire OEM
tier T1  safe=yes  live-vs-key-loss=yes  live-vs-group-loss=NO   -> BELOW BUDGET: appoint third custodian
```

The figures above are the actual outputs of `lint.py` and `tiers_extra.py` for the reference layout [M], reformatted.

### 8.3 Exchanged objects (CDDL sketch)

```cddl
transition-bundle = {
  1: 2,                          ; format
  2: bstr .size 112,             ; ac_tx v2 projection (the only bytes the locked stage parses)
  3: action-payload,             ; bound by payload_digest
  4: [* evidence],               ; signatures by atom index
  5: receipt,                    ; publicity
  ? 6: tstr .size (0..256),      ; human rationale, signed
  ? 7: ceremony-ref              ; for T2: hash + log index of the ceremony record
}
evidence = [atom: uint .le 7, alg: uint, sig: bstr]
receipt  = { 1: tstr,            ; log origin
             2: bstr,            ; C2SP checkpoint (signed note body)
             3: [* bstr],        ; C2SP cosignatures
             4: [* bstr .size 32],; inclusion proof (RFC 9162 audit path)
             5: uint }           ; leaf index
label-declaration = {            ; installed only by T2; logged with its ceremony record
  1: [8* atom-decl],
  2: { * tstr => uint },         ; label name -> bit
  3: [* [uint, uint]],           ; declared-out-of-scope pairs (e.g. both families)
  4: bstr                        ; custody-graph digest from ac-ceremony
}
atom-decl = { 1: uint, 2: uint, 3: uint, 4: bstr .size 32 }   ; kind, alg_id, declared labels, ref
log-set   = [2* { 1: tstr, 2: [* bstr .size 32], 3: uint, 4: uint }] ; origin, witness keys, k, max age
```

### 8.4 Rust twin (sketch)

```rust
pub trait Platform {
    fn nv_read_safe(&self, addr: u32, buf: &mut [u8]) -> NvResult;      // Ok | Blank | Torn | Err
    fn nv_program_unit_once(&mut self, addr: u32, unit: &[u8; 16]) -> Result<(), AcError>;
    fn counter_advance_to(&mut self, id: u32, v: u64) -> Result<(), AcError>; // monotone
    fn presence_sample(&self, desc: &PresenceDesc) -> bool;              // locked stage only
    fn rtc(&self) -> Option<TrustedTime>;                                // restricts only
}
pub fn step(state: &State, msg: &Msg, plat: &dyn PlatformView) -> Result<(State, Intents), AcError>;
```

The Rust twin is panic-free (Kani target) and is differentially tested against the C core and the Python model on every small-universe input.

---


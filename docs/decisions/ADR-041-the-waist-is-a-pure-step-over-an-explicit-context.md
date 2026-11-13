# ADR-041: The waist is a pure step over an explicit context

**Status:** Proposed
**Date:** 2026-11-13
**Legacy IDs:** Legacy: none (new; makes D-01 executable)

## Context
D-01 (ADR-020) commits to a "hourglass with a pure-function kernel", and `primitives-and-waist.md` §4.5 describes the waist in prose. Until now no header or function existed: admission, the tier engine, the chain hash and the image check were separate functions with no state machine around them, so nothing could be ported, proven or re-implemented against a fixed target.

## Decision
1. **A pure step.** `ac_step(ctx, msg, effects, needed)` is the whole kernel. It reads the context and the message and returns status plus intents. No I/O, allocation, clock, mutable global state or recursion. The only libc it may use is `memset`, `memcpy` and `memcmp`, plus the hash provider; compilers emit those themselves, so banning them would be unenforceable. This amends the "no libc" wording of §4.5.
2. **Fail closed, one mutator.** Fixed check order (initialised, busy, field validity, authority, state/budget/admission, apply). Nothing changes before the apply step, so a rejected message leaves the context byte-identical and yields one `REJECT` intent. An accepted transition yields one `NV_WRITE_SNAPSHOT`; no further transition is accepted until `ac_ack` (REQ-WAIST-02).
3. **Evidence arrives verified.** The message carries the set of atoms whose evidence an evidence layer has verified. Signature verification (waist W2) and platform access (W3) are not in this slice. This keeps the step testable on its own and moves the trust boundary to a small, separate layer; it also means the kernel is only as safe as that layer, which is not yet built.
4. **A fixed-size projection.** The message is a struct, not a parser. The CBOR bundle is parsed outside the kernel and projected to it.
5. **Profiles are data.** Per-tier fault classes, budgets, one excluded class pair per side and the action-to-tier map are part of the genesis record, admitted by the same rules as any table. Genesis enforces REQ-TIER-02 (re-keying, meaning `KEY_INSTALL` and `INSTALL_TABLE`, lives in exactly one T2 tier). The terrestrial recoverable, terrestrial fortress and remote profiles are all admitted with no change to C.
6. **State is committable.** `ac_ctx_digest` hashes a canonical serialisation of the context, and the chain starts from a commitment to the genesis state.
7. **Stability is executable.** `src/waist-v1.abi` locks the constants and struct layouts and `tests/vectors/waist-v1.txt` holds golden vectors. Both are checked on every run. The promise (negative, never-reused status codes; layout changes only with a new major version) takes effect at the T0 freeze, not before.

## Consequences
- The kernel has one small, closed surface for the Rust twin, CBMC or Frama-C, and independent re-implementations. The golden vectors are the acceptance test for each.
- Defended by checks: `scripts/arch_check.py` (rules R1–R8, with a self-test that plants six violations and requires each to be caught), a differential check of the C against an independent Python model, and mutation testing of `ac_step.c`.
- Costs and open points: the evidence layer (W2) and platform (W3) remain to be built; the model and the C were written by the same author, so a shared misreading of this ADR would not be caught by the differential check (a human re-implementation would); stack and size are host measurements only.
- Acceptance criteria for moving this ADR to Accepted: the Rust twin reproduces the golden vectors; an external reviewer has read `ac_step.c` against this ADR.

## Alternatives considered
- **Callbacks into W2 and W3 from inside the step.** Rejected for this slice: it makes the step impure and hard to test exhaustively; the evidence layer produces the verified set instead.
- **A policy interpreter or loadable rules** (J-09). Rejected: an interpreter on the irreversible path.
- **Global kernel state.** Rejected: untestable in isolation and incompatible with a pure step.
- **A single global action-to-tier table.** Rejected: re-keying lives in a different tier in the recoverable and fortress profiles (REQ-TIER-02), so the map is profile data.

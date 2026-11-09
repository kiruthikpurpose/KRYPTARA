# STREAM B: Cryptographic layer (lead cryptographer + crypto library engineer)

Date of verification: 2026-11-06. Evidence labels per BRIEF. Scratch code: `/home/claude/atlas2/blueprint/code/B/dq.py` (quorum checker), `/home/claude/atlas2/blueprint/code/B/nums.py` (size, time and counter arithmetic). Both were run in this session; their outputs are quoted below as [C].

Verification limits, stated once. Several primary hosts (nvlpubs PDFs via curl, media.defense.gov, csrc FIPS 206/207 pages) were blocked or unreachable. WebFetch summarises pages with a small model, so any figure marked "[F via fetch]" was read from a primary page but has not been re-read from the PDF. A rate limit cut off the last batch of checks (Mbed TLS releases, KyberSlash and Masking-Kyber abstracts, Botan, MCUboot/Zephyr). Those items are marked "unverified".

---

## B.0 Standards status as of 2026-11-06 (verified where marked)

| Item | Status found | Evidence |
|---|---|---|
| FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA | Final since August 2024 | [F] csrc.nist.gov/projects/post-quantum-cryptography (page updated 2026-10-27) |
| FIPS 206 FN-DSA | **Not final.** The IETF drafts of Nov 2026 and May 2026 say "expected late 2026 / early 2027" and "forthcoming". NIST said in Aug 2025 that the draft was submitted up the chain. I found no evidence of a published initial public draft. | [F] draft-ietf-cose-falcon-05 (2026-11-01); [F] draft-ietf-lamps-fn-dsa-certificates-00 (2026-05-20); [F] pqc-forum post, Aug 2025 |
| HQC (FIPS 207) | Draft not yet released as of an Aug 2026 report. NIST leans to a seed-only private key format. | [2nd] freenode.net article, 2026-08-03; [2nd] securityweek (draft planned early 2026, final 2027), so the schedule has slipped |
| SP 800-208 (LMS/HSS, XMSS/XMSS^MT) | Final. NIST says not for general use, suited to firmware and software signing. | [F] NIST IR 8547 final text (via fetch) |
| SP 800-230 (additional SLH-DSA sets) | **Initial public draft, 2026-04-13. Comments closed 2026-06-12.** Six sets, hard limit of 2^24 signatures per key, "not approved for general-purpose use". Still draft. | [F] csrc.nist.gov/pubs/sp/800/230/ipd |
| NIST IR 8547 | **Final, 2026-10-27.** Quantum-vulnerable signatures and key establishment are deprecated after 2030 and disallowed after 2035. Federal high-impact systems must move to PQ key establishment by 2030-12-31 and PQ signatures by 2031-12-31, per EO 14412 and OMB M-26-15 (names as quoted by the page). Hybrid is "typically temporary". | [F via fetch] csrc.nist.gov/pubs/ir/8547/final and the PDF |
| CNSA 2.0 | Only ML-KEM-1024 and ML-DSA-87. HashML-DSA prohibited. **SLH-DSA excluded from NSS.** FN-DSA not added. LMS and XMSS (single-tree only, no HSS or XMSS^MT) preferred for firmware roots of trust. Dates: new acquisitions 2027-01-01, phase-out 2030-12-31, mandatory 2031-12-31. | [2nd] postquantum.com FAQ v2.1 summary; the NSA PDF was unreachable |
| IETF X.509 | RFC 9881 (ML-DSA, Oct 2025), RFC 9909 (SLH-DSA, Dec 2025), RFC 9935 (ML-KEM, Mar 2026), RFC 9802 (HSS/XMSS, Jun 2025). FN-DSA certificates is a WG draft (-00). | [F] rfc-editor.org subject index |
| IETF CMS | RFC 9882 (ML-DSA), RFC 9814 (SLH-DSA, Jul 2025). KEM-in-CMS (ML-KEM) was in the RFC Editor queue in March 2026. | [F] IETF 125 LAMPS agenda; rfc-editor |
| Composite signatures and KEMs | Composite ML-DSA (`pq-composite-sigs-19`) is in the RFC Editor queue. Composite ML-KEM (`-23`, 2026-10-14) is in the RFC Editor queue. Neither is an RFC. | [F] datatracker |
| COSE/JOSE | **RFC 9964** (May 2026): ML-DSA-44/65/87 = -48/-49/-50, AKP key type = 7. SLH-DSA (`cose-sphincs-plus-10`): -51 and -52 requested, **only the 128s sets listed**. FN-DSA (`cose-falcon-05`): -54 and -55 requested. | [F] rfc-editor RFC 9964; [F] datatracker drafts |
| LMS extras | RFC 9858 (Oct 2025, informational/CFRG) adds SHA-256/192, SHAKE256/256 and SHAKE256/192 sets. Its security argument rests on preimage and second-preimage resistance. | [F via fetch] RFC 9858 |
| TLS | RFC 10024 (Aug 2026): X25519MLKEM768 = 0x11EC (4588). Pure ML-KEM groups (`draft-ietf-tls-mlkem-11`, Informational) are in the RFC Editor queue, with no consensus on recommendation. | [F] datatracker |
| SUIT | `draft-ietf-suit-mti-23` (Jul 2025, expired Jan 2026) lists HSS-LMS as MTI and no ML-DSA or SLH-DSA profile. I found no SUIT PQ draft by search. **Gap.** | [F] datatracker; search result [I] |
| X-Wing | Individual independent submission `-11` (2026-09-23), not a WG or RFC. | [F] datatracker |
| ACVP | Spec drafts exist for ML-KEM, ML-DSA, SLH-DSA and LMS. **No XMSS entry.** | [F] pages.nist.gov/ACVP |
| CMVP | Certificate #5523 (Chainguard FIPS Provider for OpenSSL, FIPS 140-3 Level 1, active, sunset 2031-09-14) lists ML-KEM, ML-DSA and SLH-DSA with CAVP certificates. I have not seen a validated LMS entry. | [F via fetch] csrc cert 5523 |
| FIPS 140-3 IG | IG 10.3.A has self-test requirements for ML-KEM (#15), ML-DSA (#16), SLH-DSA (#17): CASTs and pairwise consistency tests. | [2nd] SafeLogic blog, Aug 2024 |

Consequence for the build: **the ABI must carry algorithm identity as "(standard, parameter set, profile)", not as a bare name.** FN-DSA, HQC and the SP 800-230 sets are not final, and the COSE and X.509 identifiers for them are TBD. Those algorithms get registry status `PROPOSED`, which cannot be used to authorise anything. A registry rule (B.1.5) enforces this.

---

## B.1 Algorithm abstraction: the registry

### B.1.1 Decision

**DECISION.** Every algorithm is an immutable, content-addressed descriptor in an append-only registry. The descriptor never changes. Everything that changes over time (lifecycle status, deprecation, assumption-class corrections) is a separate signed *status record* that references the descriptor hash.

**WHY.** The atlas's R10 and N57 (agility atrophy) and N25 (draft OIDs) come from mutable "supported algorithm" lists. Immutable descriptors let a device, an auditor and a CBOM tool agree on what "ML-DSA-65 / pure / hedged" meant in 2026 even in 2046. [I]

**ALTERNATIVES REJECTED.**
- A mutable enum in a header, as in liboqs `OQS_SIG_alg_*` strings and OpenSSL NIDs. These change meaning between releases.
- Using IANA, COSE or OID numbers as the identity. They are assigned late, and two of them (COSE SLH-DSA, FN-DSA) are still TBD.

**ASSUMPTIONS.** Descriptors are small enough to live in `.rodata`.

**TRADE-OFFS.** A second lookup (descriptor id to status) on every use. Mitigated by compiling the status table into the image.

**LIMITS.** The registry cannot make a bad assumption classification good (see B.1.3).

**HOW WE VALIDATE.** The registry is a generated artefact with a schema, a golden hash per entry, and a CI check that no entry's bytes changed.

### B.1.2 Descriptor layout (flash form, 32 bytes, little-endian)

```c
typedef struct pq_alg_desc {            /* const, in .rodata, content hash = SHA-256 of canonical CBOR form */
    uint16_t alg_id;        /* 2  stable forever, never reused. Allocation is by this project, not IANA */
    uint8_t  kind;          /* 1  KEM, SIG, SIG_STATEFUL, XOF, HASH, MAC, AEAD, KDF, COMBINER */
    uint8_t  profile;       /* 1  pure | prehash | hedged | deterministic | hybrid-AND | hybrid-OR(forbidden for authority) */
    uint16_t pk_bytes;      /* 2  fits u16: max 2592 (ML-DSA-87) .. 49856 is sig */
    uint16_t sk_bytes;      /* 2  stored form (seed form where defined) */
    uint16_t out_bytes;     /* 2  signature, or ciphertext for KEMs */
    uint8_t  ss_bytes;      /* 1  shared secret (KEM) or 0 */
    uint8_t  nist_cat;      /* 1  1,3,5 or 0 */
    uint32_t assump_bits;   /* 4  bitmask over the registry's assumption atoms (B.1.3) */
    uint32_t prop_bits;     /* 4  property-level tags (B.1.3, level 1) */
    uint16_t state_class;   /* 2  0 stateless | 1 stateful-tree (LMS/XMSS) | 2 limited-use (SP 800-230) */
    uint8_t  sc_profile;    /* 1  side-channel profile code (B.7) */
    uint8_t  verify_scratch_class; /* 1 index into static scratch table (B.4) */
    uint32_t std_ref;       /* 4  index into the standards table: FIPS 204, RFC 8554, ... */
    uint16_t max_uses_log2; /* 2  0 = unlimited; 24 for SP 800-230 sets; tree height for LMS */
} pq_alg_desc_t;            /* 34 B packed; pad or drop max_uses to reach 32 */
```
Arithmetic: 2+1+1+2+2+2+1+1+4+4+2+1+1+4+2 = 30 B before alignment, 32 B padded. Sixteen algorithms cost 512 B of flash. [C]

**Status record (separate, signed, append-only).** `{alg_id, desc_hash[32], status, effective_epoch, reason_code, supersedes}` under the same quorum rule as any authority change. Lifecycle states, ordered:

`PROPOSED` (draft standard; never authorises) then `ADMITTED` (final standard; verify and encrypt allowed; may take part in quorums only if its assumption atoms are declared) then `RECOMMENDED` then `LEGACY_VERIFY` (verify only, no new signing) then `DENIED`.

Rules:
- Transitions are monotone except `ADMITTED` to `RECOMMENDED`.
- `DENIED` is permanent for that descriptor. A fixed version gets a new `alg_id`.

### B.1.3 How to encode "assumption classes" defensibly

**What is a real independent assumption and what is not.** The atlas (10.3) counts SHA-2 and Keccak as the only two waists. I agree with that as a conservative rule, and add three refinements.

**(1) Two levels of encoding.**
- *Level 0, the rule input.* Coarse "waist" atoms. These are the only atoms the quorum rule may use by default. Merkle-Damgård hashes (SHA-256, SHA-512, SHA-384, SHA-512/256) form one atom `SHA2`, because they share a design lineage and a compression-function style. Keccak (SHA-3, SHAKE, cSHAKE, KMAC) forms `KECCAK`.
- *Level 1, the property tags.* They record which hash property the scheme needs: collision resistance (CR), second-preimage resistance (SPR), preimage resistance (PRE), PRF behaviour, or random-oracle (RO) modelling. They are used to rank risk, not to loosen the rule.

Why tags matter, with sources:
- Hash-based signatures (LMS, XMSS, SLH-DSA) rest on SPR/PRE-style properties and not on collision resistance. RFC 9858 says so for LMS. [F via fetch]
- ML-DSA uses SHAKE256 as H for the message representative and the commitment hash, and SHAKE128 for matrix expansion (FIPS 204 §3.7 as extracted). [F via fetch; the step-by-step mapping is my reading of the standard, [I]]
- ML-DSA is a hash-and-sign construction in the Fiat-Shamir style. A collision attack on the hash that binds the message gives a substitute-message forgery, and its QROM proof models the XOF as a random oracle. [I]
- So a SHA-256 *collision* result of the SHA-1 kind (hits ECDSA/Ed25519 and certificates) would not touch LMS-SHA256 or SLH-DSA-SHA2. A *preimage* break would. The Level-0 rule stays conservative: it treats any SHA2 failure as taking out every SHA2-tagged key.

**(2) Is ML-DSA "really SHAKE-dependent in a way that matters"? Yes, for the quorum rule.** Every hash and sampler call in ML-DSA is SHAKE (FIPS 204 §3.7 [F via fetch]); I know of no SHA-2 use in pure ML-DSA. A practical break of SHAKE256 collision or preimage resistance, or a structural distinguisher on Keccak-f, would hit ML-DSA and SLH-DSA-SHAKE together. It would also hit ML-KEM (H = SHA3-256, G = SHA3-512, J and PRF = SHAKE256, XOF = SHAKE128 per FIPS 203 §4.1 [F via fetch]). The atlas conclusion stands: ML-DSA and SLH-DSA-SHAKE share `KECCAK`, so a quorum of those two is not single-assumption-safe. My run reproduces this: the pair (ML-DSA, SLH-DSA-SHAKE) has cover number 1. [C: `dq.py`]

**(3) SLH-DSA-SHA2 vs SHAKE, LMS and XMSS.**
- SLH-DSA-SHA2 at category 1 uses SHA-256 only. At categories 3 and 5 it also uses SHA-512 for H and T_l; both are `SHA2`. [I from FIPS 205 structure, not re-fetched]
- SLH-DSA-SHAKE is `KECCAK` only.
- LMS and XMSS exist in both flavours: LMS-SHA256 (RFC 8554), plus SHA-256/192, SHAKE256/256 and SHAKE256/192 (RFC 9858 [F via fetch]). **So "LMS" does not by itself mean SHA-2.** The descriptor must carry the hash. This matters for B.2: LMS-SHAKE is a `KECCAK` key.

**(4) Other atoms.**

| Atom | Keys that depend on it | Independent of others? |
|---|---|---|
| `SHA2` | LMS/XMSS-SHA2, SLH-DSA-SHA2, Ed25519 (SHA-512), ECDSA with SHA-2, HMAC-SHA2 | Own atom |
| `KECCAK` | ML-DSA, ML-KEM, SLH-DSA-SHAKE, LMS-SHAKE, FN-DSA (Falcon uses SHAKE256 [I]), X-Wing combiner | Own atom |
| `MLWE_MSIS` | ML-DSA, ML-KEM | Lattice family |
| `NTRU_SIS` | FN-DSA | **Treated as correlated with `MLWE_MSIS`** through a shared `LATTICE_REDUCTION` atom (both fall to better lattice-reduction algorithms). Keys carry both atoms. [I] |
| `ECDLP`, `DLP`, `FACTORING` | ECDSA, Ed25519, X25519, RSA | **One atom `SHOR`**: a CRQC kills all of them together. RSA and ECC are not independent. [I] |
| `CODE_BASED` | HQC, Classic McEliece (KEM only) | Independent of lattice and hash |
| `SYM_BLOCK` | AES-based AEAD and KW | Not an authority-quorum atom |

**(5) Things that are not assumptions but must be separate dimensions.**
- *Implementation common mode.* Same library, same compiler, same HSM firmware. This is a "build diversity" tag on the signing path, outside the assumption rule. The atlas's Knight-Leveson point applies. [I]
- *Holder independence.* Different organisations or HSMs (key theft is not an assumption failure). The checker handles it with a theft budget t (B.2).
- *Epoch profile.* The probability or status of `SHOR` differs before and after a CRQC. The registry stores an `epoch_profile` per atom, and the checker is run once per profile (B.2.5).

**What must not be claimed [I].** Independence between `SHA2` and `KECCAK` is a judgement. They are different constructions studied by one community. The rule therefore ships with a *merged-waist stress test*: re-run the checker with `SHA2 = KECCAK` and report what survives. Under the merged model nothing hash-and-lattice survives, which is why the physical-presence/escrow element of the atlas PAM rule matters (B.2.6).

**New third waist?** Code-based signatures do not exist as standards. The NIST on-ramp signature candidates (multivariate, isogeny, etc.) are not standardised, and my fetch of the NIST page gave no round or dates. Policy: such atoms may be registered as `PROPOSED` and cannot count toward an authority quorum until a final standard exists. [I]

### B.1.4 Hybrid composition in the registry

A composite key is a registry entry of `profile = hybrid-AND`. Its compromise condition is a *monotone formula*, not a union of atoms:
- A single key `k` fails if **any** atom in A(k) fails.
- An AND-composite (both signatures must verify) is forgeable only if **both** components are forgeable.
- An OR-hybrid ("either verifies") is forgeable if either is. It is **forbidden for authority**.

The descriptor therefore stores a list of component descriptors and a combiner mode, and the checker computes the minimal failing atom sets. Output from `dq.py` [C]:

```
composite ML-DSA ^ Ed25519 min failing sets: {ECDLP,KECCAK} {ECDLP,MLWE} {KECCAK,SHA2} {MLWE,SHA2}
OR-accept hybrid min failing sets:         {ECDLP} {KECCAK} {MLWE} {SHA2}     (cover number 1)
post-CRQC composite (ECDLP already failed): {KECCAK} {MLWE}                  (degrades to its PQ half)
```

This shows three things:
1. An AND-composite is, by itself, two-failure-safe *in the pre-CRQC epoch*, but the safety comes from the classical half, which a CRQC removes.
2. Post-CRQC the composite is exactly as strong as ML-DSA alone, so it cannot substitute for a hash-based slot.
3. The OR-hybrid is worse than either component.

### B.1.5 Registry invariants (enforced by tooling)

1. Only `ADMITTED` or higher algorithms may appear in an authority quorum.
2. Every descriptor lists its atoms. A missing atom is a registry error.
3. A `PROPOSED` algorithm may be used in shadow-sign (observe-only) mode, per the molting protocol.
4. `max_uses_log2 != 0` forces the stateful-signing path (B.5).

---

## B.2 The disjoint-quorum rule, formalised

### B.2.1 Definitions

- `Σ`: finite set of atoms (B.1.3 Level 0).
- `K`: finite set of keys (slots). Each key `k` has a monotone compromise predicate `φ_k(F)` over `F ⊆ Σ`: true iff an adversary who can break exactly the atoms in `F` can forge under `k`. For a plain key, `φ_k(F) = (F ∩ A(k) ≠ ∅)`. For an AND-composite, `φ = φ_{k1} ∧ φ_{k2}`.
- A *signer set* `S ⊆ K` is the set of distinct keys whose signatures over a single, domain-separated authority message are presented.
- *Assumption-cover number* `κ(S, t)`: the smallest `|F|` such that, after the adversary additionally steals up to `t` keys of its choice, every member of `S` is forgeable. Formally `κ(S,t) = min{ |F| : |{k ∈ S : ¬φ_k(F)}| ≤ t }`.
- A policy `P` is a set of accepted signer sets plus rules for anti-replay and the floor. `P` is **(f, t)-safe** iff every `S ∈ P` has `κ(S, t) ≥ f + 1`.

**The atlas rule.** The atlas states the 10.3 rule as "pairwise disjoint in at least two members". That wording is sufficient but not exact. The exact single-failure condition is `∩_{k∈S} A(k) = ∅` (for plain keys, `t = 0`, `f = 1`). The pairwise form is a special case that also gives `κ = |S|`.

**DECISION.** The project defines "disjoint quorum" as **(f=1, t=0)-safety with an explicit holder rule**, i.e. `κ(S,0) ≥ 2`. The pairwise-disjoint form is a *profile* for high assurance (HA-1). The holder rule is that members must belong to different custody domains. A policy may additionally demand `(f=1, t=1)`.

**WHY.** `κ ≥ 2` is precisely what M2 simulates: no single atom failure yields a quorum. It is also checkable by brute force in microseconds, on host tools.

**ALTERNATIVES REJECTED.**
- Plain threshold (2-of-3). Fails the test: `dq.py` shows ML-DSA + SLH-DSA-SHAKE has `κ = 1`. [C]
- Pairwise-disjoint only. Rejects safe 3-signer sets whose pairs overlap.
- Probabilistic acceptance ("sum of failure probabilities below x"). Not auditable offline, and it needs numbers nobody can defend.

### B.2.2 Checker algorithm

```python
# dq.py (excerpt; whole file in code/B/dq.py)
def cover_number(keys, S, theft=0, amax=6):
    at = atoms({k: keys[k] for k in S})
    for a in range(0, amax+1):
        for F in itertools.combinations(at, a):          # F = set of failed atoms
            F = frozenset(F)
            rest = [k for k in S if not broken(keys[k], F)]   # keys still honest
            if len(rest) <= theft: return a                   # adversary steals the rest
    return 99
def accepted_sets(keys, slots, f, t=0, minsize=2):
    return [S for m in range(minsize, len(slots)+1)
              for S in itertools.combinations(slots, m) if cover_number(keys, S, t) > f]
```

Complexity: `|Σ|` is under 10 and `|K|` under 8 in any realistic deployment, so the loop runs over under 2^10 atom subsets per signer set. This is a host-side policy-compile step. **Devices never run it.** They receive its output as an `accept_table`.

**Device-side form.** For `n ≤ 4` slots, `accept_table` is a bitmap over the `2^n` subsets: 16 bits for 4 slots. The first stage evaluates "signature set bitmask → table lookup". The table lives in the locked stage, or in a signed policy that is *monotone-tightening only* (it may clear bits, never set them). This stops a forger of a later policy from loosening the rule.

### B.2.3 Results [C: `dq.py`; `models/quorum.py` re-run]

For the atlas slot set {ML-DSA, LMS-SHA256, SLH-DSA-SHAKE}:

| Signer set | Cover number κ | Accepted at f=1 |
|---|---|---|
| ML-DSA + LMS-SHA256 | 2 | yes |
| LMS-SHA256 + SLH-DSA-SHAKE | 2 | yes |
| ML-DSA + SLH-DSA-SHAKE | **1** (Keccak) | **no** |
| all three | 2 | yes (but see t=1 below) |

I re-ran `models/quorum.py`:
- Plain 2-of-3: attacker P = 0.005249, honest availability 0.99475.
- Disjoint: attacker P = 0.000274, honest availability 0.99002.
- Ratio 0.005249 / 0.000274 = 19.2. This matches the atlas's "about 19-fold" (the atlas text's "0.52% and 0.027%" are the same numbers rounded). [C]

**Finding F-B1 (atlas gap): every accepted pair contains LMS.** With the three-slot set, both disjoint pairs include LMS-SHA256. LMS is stateful, hard to back up, and has a finite leaf budget. M2's "honest availability" counts only assumption failures; operational loss of the LMS key (state loss, HSM death, leaf exhaustion) removes *all* quorums, so liveness of authority change collapses onto the most fragile key. The fix is a fourth slot of the `SHA2` waist that is stateless: SLH-DSA-SHA2. Four slots (ML-DSA, SLH-DSA-SHAKE, LMS-SHA256, SLH-DSA-SHA2) give four disjoint pairs, each avoiding LMS in two of them:

| Pair | Avoids LMS? |
|---|---|
| ML-DSA + LMS | no |
| ML-DSA + SLH-DSA-SHA2 | yes |
| SLH-DSA-SHAKE + LMS | no |
| SLH-DSA-SHAKE + SLH-DSA-SHA2 | yes |

Cost: 4 × 32 B = 128 B of slot hashes instead of 96 B. [C: `dq.py` on a five-slot set printed these minimal accepted pairs.]

**Finding F-B2 (atlas gap): MV-1 as written cannot enforce the rule.** MV-1 has "one hash verifier: LMS-SHA-256 W4". A locked stage that can verify only `SHA2`-class signatures has no `KECCAK`-class slot, so there is no disjoint quorum at all: every verifiable signer set has `κ = 1`. Two ways out:
- (a) Add Keccak to the locked stage and an LMS-SHAKE256/256 (RFC 9858) or SLH-DSA-SHAKE verifier. The Keccak permutation costs flash that I have **not measured** [unverified]. It is the price of the rule.
- (b) Verify `ML-DSA` in the second stage only, as HA-1 does, and accept that the locked stage then enforces only the "different slot" floor rule and not the disjoint rule. The memo should say this plainly: the two are different guarantees.

CNSA 2.0 constraint: SLH-DSA is excluded, so a national-security profile of this registry can only use {ML-DSA-87 + LMS} (two atoms: `KECCAK`/`MLWE_MSIS` and `SHA2`), which is still a disjoint pair. [2nd]

**Key theft (t ≥ 1).** `dq.py`: the three-signer set has `κ(S,0) = 2` but `κ(S,1) = 1`. One stolen key plus one atom failure can forge. So the rule must pair with the holder rule: different HSMs, different organisations, and an escrow signer under custody-domain separation. [C]

### B.2.4 Safety theorem and proof sketch

**Theorem (single-failure safety).** Let a verifier accept a state transition `τ` only if it receives valid signatures on `(domain-tag ‖ τ ‖ floor-index)` from a signer set `S` with `κ(S, t) ≥ f + 1`. Assume:
- (A1) *Soundness of the registry.* For every key `k` and every adversary that forges under `k` with non-negligible probability, some atom in the minimal failing sets of `φ_k` has failed.
- (A2) *Distinct keys, distinct randomness.* Signatures under distinct keys are over a message with a domain tag and the key's identity, so a signature cannot be reused across keys or contexts.
- (A3) *State hygiene.* Stateful keys never sign two messages with one leaf.
- (A4) The adversary breaks at most `f` atoms and steals at most `t` keys.

Then the adversary cannot get `τ` accepted unless an honest quorum signed `τ`.

*Proof sketch.*
1. Take the accepted `S`. Each member `k ∈ S` either (i) was stolen (at most `t` of them), (ii) is forgeable under the adversary's atom set `F` (`φ_k(F)` true), or (iii) is neither.
2. For (iii), (A1) says a forgery under `k` implies an atom in `k`'s failing sets failed, and by hypothesis none in `F` fits, so the adversary must have got `k`'s signature from an honest signer. Honest signers sign only authorised transitions, and by (A2)/(A3) a replayed signature on a different `τ'` does not verify for `τ`.
3. So if no honest quorum signed `τ`, every member of `S` is in (i) or (ii).
4. That means `|{k ∈ S : ¬φ_k(F)}| ≤ t`, and by definition `|F| ≥ κ(S,t) ≥ f+1`.
5. This contradicts (A4). ∎

**Where the proof is weak (limits).**
- (A1) is a *modelling* assumption. The theorem is conditional on the registry's atom lists being complete. This is why Level 0 uses coarse, merged waists, and why a merged-waist stress test exists.
- It does not cover implementation bugs. Those are common-mode and are the reason for implementation diversity (B.3, B.9).
- It does not cover the ordering of events (the adversary breaking an atom *after* a long-lived signed authority was issued). That is handled by the molting protocol and epochs, not by the theorem.
- For the probabilistic version (M2), if atom failures are independent with probabilities `p_α`, then `Pr[forge S] ≤ Σ_{α≠β} p_α p_β` over covering pairs. This is a model, not a theorem. Positive correlation between `SHA2` and `KECCAK` makes it optimistic. [I]

### B.2.5 Interaction with the epoch profile

The checker runs once per *epoch profile*. In "pre-CRQC", `SHOR` holds and an ECDSA+ML-DSA AND-composite counts as two classes. In "post-CRQC", `SHOR` has failed, so classical keys are treated as already forgeable (their slot is deleted from `S`). A policy that is safe only in the pre-CRQC profile fails CI, because the whole point is to survive the epoch change. [H]

### B.2.6 Ties to the atlas

- **M2 / 10.3.** This section is the formal and executable version of the rule. It adds the exact condition, the key-theft extension, the composite treatment, and the two gaps F-B1 and F-B2.
- **11.1 floor rule.** "Floor advance needs a signature from a different slot than the one retired" is a *holder/slot* rule. The disjoint rule is an *assumption* rule. A floor advance must satisfy both.
- **PAM rule (11.2).** A revocation of the current authority set needs the escrow class plus physical-presence evidence. Physical presence is the only element that does not share any hash atom, so it is the fallback for the merged-waist case.

---

## B.3 Provider strategy: reuse, wrap or avoid

**Selection criteria** (in order): (1) correctness evidence (formal proofs, test vectors, ACVP), (2) constant-time evidence, (3) memory model fit (no heap, static scratch), (4) licence, (5) maintenance health. Health data below is from GitHub pages and package indexes fetched in this session. Where a page did not show a date I say so.

| Candidate | Facts found | Verification status | Licence | Decision |
|---|---|---|---|---|
| **mlkem-native** (PQCA) | v2.0.0 "Latest", 07 Aug (year not shown; v1.2.0 was in liboqs 0.16.0, July 2026, so 2026 [I]). Users: AWS-LC (since v1.50.0), liboqs default (since 0.13.0), rustls via AWS-LC. | CBMC proofs: memory-safe and type-safe C. HOL-Light: AArch64 and x86-64 asm proved functionally correct, memory-safe and constant-time. valgrind-based secret-independence tests. 32-bit Armv8.1-M (Helium) backend experimental. [F: README] | Apache-2.0, ISC, MIT badges | **REUSE as the primary ML-KEM C core.** Wrap behind our ABI. Cortex-M0+/M3/M4 use portable C or our own asm until a verified M-profile backend exists. |
| **mldsa-native** (PQCA) | v2.0.0 07 Aug (same caveat). Users: AWS-LC, liboqs (default since 0.16.0), CHERIoT-PQC, Pavona. | CBMC proofs (UB, overflow). HOL-Light/s2n-bignum for asm. The matrix sampler is deliberately variable-time (public data). **Secret-vector samplers have no proof yet.** Tested against ACVP and Wycheproof vectors. [F: README] | Apache-2.0, ISC, MIT | **REUSE as the primary ML-DSA core.** Record the unproven samplers as an open item and cover them with dynamic CT tests. |
| **slhdsa-c** (PQCA) | All 12 FIPS 205 sets. "WE DO NOT CURRENTLY RECOMMEND..." production use; no release yet. No SP 800-230 mention. | `proofs/cbmc` directory exists, scope not described. | MIT or Apache-2.0 | **WRAP for host-side signing and as a differential oracle only.** Write our own verify-only SLH-DSA for MCUs (about the smallest part of the standard), cross-checked against it. |
| **liboqs** (OQS) | 0.16.0 (2026-07-09): mldsa-native default; HQC enabled; **SPHINCS+ removed**; LMS init and indexing bug fixed; XMSS verify out-of-bounds read fixed. README says not for production. | Mixed; delegates to upstream implementations. | MIT | **Test oracle and interop only.** The stateful-signature bugs fixed in 0.16.0 are direct evidence for AVOID as a stateful signer. |
| **PQClean** | **Archived read-only 2026-08-04**, points users to PQCA. | n/a | CC0 / MIT / public domain | **AVOID.** Retired. |
| **pqm4** | README: **deprecated**, archive "in or after January 2027", last PRs by 2026-11-30. | n/a | Apache-2.0 / CC0 | **AVOID as a dependency.** Keep as a source of Cortex-M4 reference numbers and asm ideas (see B.3.2). |
| **libcrux** (Cryspen) | Crates at 0.0.11 (pre-0.1). `ml-kem` and `ml-dsa`. `no_std` needs a global allocator. | Verified paths via hax and HACL*; per-crate badge not visible on the page. Compiled output *not* verified side-channel-resistant. [F: README] | Apache-2.0, MIT | **WATCH.** Rust option and differential oracle. The allocator requirement conflicts with our no-heap rule. |
| **RustCrypto** `ml-kem` 0.3.4 (2026-10-31), `ml-dsa` 0.1.2 (2026-10-31), `slh-dsa` 0.2.0-rc.5 (2026-04-28) | Versions and dates from crates.io [F]. Audit status and constant-time statements not found. | Unknown | Apache-2.0 or MIT | **Differential oracle.** Not a primary. |
| **OpenSSL 3.5 LTS** | 3.5.9 on 2026-09-29. OSS support to 2030-04-08. ML-KEM, ML-DSA, SLH-DSA; X25519MLKEM768 in the default TLS groups. | CMVP #5523 is a *Chainguard FIPS provider for OpenSSL* module listing ML-KEM/ML-DSA/SLH-DSA CAVP certs. Whether the upstream OpenSSL FIPS provider 3.5 is itself validated: unverified. | Apache-2.0 [I] | **REUSE on C4/C5 hosts** (gateways, KDC, release tooling). |
| **AWS-LC** | Uses mlkem-native and mldsa-native. Formal verification of SHA-2, HMAC, AES-GCM/KW, some s2n-bignum curve code. Page makes no FIPS claim. | Partial | Apache-2.0 (template note only; check) | **REUSE on C4/C5 as the second host implementation** for diversity. |
| **wolfCrypt / wolfBoot** | wolfBoot v2.9.0 (2026-07-02): LMS/HSS, XMSS, ML-DSA, hybrid; many MCU targets. No certification claim on the page. | Unknown | **GPL-3.0** on the wolfBoot page (commercial terms not shown) | **INTEROP TEST only.** Licence prevents a permissive core from depending on it. |
| **Mbed TLS / TF-PSA-Crypto** | Implements PSA Crypto API **1.2**; page does not confirm ML-KEM or ML-DSA; mentions LMS as an extended API. Release data not retrieved. | Unverified | Apache-2.0 or GPL-2.0-or-later | **PSA host for classical algorithms; PQ via our provider.** Revisit when a PQ release is confirmed. |
| **Botan** | Not assessed this session. | unverified | BSD-2 [I, memory] | Survey task; not in baseline. |
| **cisco/hash-sigs** | LMS and HSS; files named `hss_reserve`; licence and recent activity not shown by the page. | Unknown | Not shown | **WRAP for test vectors and host signing study only.** |
| **xmss-reference** | README: intended for cross-validation, not production; deployment needs careful analysis. | n/a | CC0 | **Oracle only.** |
| **PSA Crypto PQC extension** | v1.4 extension at Final 1; covers ML-KEM, ML-DSA, SLH-DSA. `PSA_ALG_ML_DSA` = 0x06004400 (hedged), deterministic variant 0x06004500, key pair stored as a 32-byte seed. LMS/XMSS appear only in the first Beta change note. | [F via fetch] | Spec | **Align numerically where defined; extend** (B.4). |
| **Hardware accelerators / vendor kits** | Search-result titles only: FortifyIQ CAVP-validated ML-DSA verification library [V], Infineon PQC-ready control MCUs, ST X-CUBE-PQC, Nordic nRF Connect ML-DSA sample. | Contents not read | Mixed | **Assess per part from published evidence.** Not baseline. |

### B.3.1 Decision and rationale

**DECISION.** Three layers:
1. *Primitive cores:* take mlkem-native and mldsa-native unmodified as vendored, pinned, hash-checked subtrees. Our own code is a thin provider adapter. We also write two small things ourselves: a **verify-only LMS** and a **verify-only SLH-DSA** for the locked stage (formally specified and model-checked, B.9).
2. *Diversity:* every primitive has at least two independent implementations in the test matrix (mlkem-native vs libcrux vs RustCrypto vs OpenSSL; mldsa-native vs the same).
3. *Host side:* OpenSSL 3.5 LTS and AWS-LC as C4/C5 backends.

**WHY.**
- The ecosystem is consolidating into the PQCA "native" family: PQClean was retired on 2026-08-04, pqm4 is deprecated and liboqs now defers to mlkem-native and mldsa-native. [F]
- Those two have the strongest public evidence (CBMC and HOL-Light). Betting on them means we inherit their verification work.
- Verify-only hash-based code is small enough to verify end to end ourselves.

**ALTERNATIVES REJECTED.** Write all primitives ourselves (no verification budget, N20); use liboqs as the core (README says not production, and the LMS bug history); vendor PQClean or pqm4 (dead).

**ASSUMPTIONS.** The PQCA projects stay healthy. Mitigation: vendored subtrees plus a documented switch to libcrux or RustCrypto behind the same ABI.

**TRADE-OFFS.** No Cortex-M0+/M3/M4 verified assembly; we use portable C or accept unverified asm (B.3.2).

**LIMITS.** Formal verification covers memory safety, type safety and, for asm, constant time. It does **not** cover power, EM, speculation or fault attacks (mldsa-native README states these are out of scope [F]).

**HOW WE VALIDATE.** B.9.

### B.3.2 Cortex-M numbers, with sources

pqm4 benchmarks ([D], `benchmarks.md`, Cortex-M4; board and clock not stated on the page; times computed here at assumed clocks [C]):

| Operation | Cycles | ms at 64 MHz | ms at 120 MHz | Memory per page |
|---|---|---|---|---|
| ML-KEM-768 decaps, `m4fstack` | 714,194 | 11.2 | 6.0 | 2,844 B |
| ML-KEM-768 decaps, `m4fspeed` | 707,827 | 11.1 | 5.9 | 6,452 B |
| ML-KEM-768 decaps, `clean` | 1,387,984 | 21.7 | 11.6 | 14,480 B |
| ML-KEM-768 keygen, `m4fspeed` | 642,096 | 10.0 | 5.4 | 5,396 B |
| ML-DSA-65 verify, `m4f` | 2,415,944 | 37.7 | 20.1 | 9,888 B |
| ML-DSA-65 verify, `m4fstack` | 5,732,397 | 89.6 | 47.8 | 2,712 B |
| ML-DSA-65 sign, `m4f` (avg) | 6,193,171 | 96.8 | 51.6 | 68,872 B |
| ML-DSA-65 sign, `m4fstack` (avg) | 24,421,526 | 381.6 | 203.5 | 6,616 B |
| SLH-DSA-SHA2-128f verify, `clean` | 21,923,628 | 342.6 | 182.7 | 2,664 B |
| SLH-DSA-SHA2-128f sign, `clean` | 368,575,228 | 5,759 | 3,072 | 2,468 B |

- The atlas "22 ms, 14.2 KB" figure for an M0+ decapsulation matches the `clean` M4 row (21.7 ms at 64 MHz, 14,480 B). So the atlas number is the unoptimised implementation, and the M4 asm cuts memory 5× and time 2× (14,480/2,844 = 5.1; 1,387,984/714,194 = 1.94). [C]
- Verification of the stack-minimal ML-DSA variant costs 2.4× the cycles of the speed variant (5,732,397/2,415,944 = 2.37) but needs 3.6× less memory (9,888/2,712). [C]
- Caveat: the page's "Memory" column is not labelled as stack, the ML-KEM rows average only 10 runs, and the pqm4 project is deprecated. These are reference numbers for sizing, not guarantees.

---

## B.4 The provider interface

### B.4.1 Principles

**DECISION.** A PSA-Crypto-like, algorithm-agile C ABI with these contracts:
1. **Algorithm identity** is `alg_id` from the registry; where PSA defines a value (e.g. 0x06004400 for ML-DSA hedged), a mapping table is provided.
2. **No heap.** Every call takes caller-provided scratch memory. Required sizes are available as compile-time constants (`PQ_VERIFY_SCRATCH(alg)`) and a runtime query for dynamic builds.
3. **Constant-time contract:** functions that handle secret inputs are declared `PQ_CT_SECRET` and must satisfy B.7. Functions that handle only public data (verify, encapsulate) are `PQ_PUBLIC` and may branch on data.
4. **Zeroisation:** every scratch buffer, key buffer and context is wiped on all exit paths. The provider uses a platform `pq_secure_zero()` that is not elided by the compiler.
5. **Verify returns a decision, not a reason.** To remote callers, "bad signature", "wrong key" and "malformed" are the same `PQ_VERIFY_REJECT`.
6. **Boot-time self-test gate:** the first call to a primitive fails with `PQ_E_SELFTEST_PENDING` until its KAT has passed.

**WHY.** PSA's property that a key is referenced by a handle and policy, and the heap-free `PSA_*_MAX_SIZE` macros, fit OT. But PSA has no scratch-size query for PQ operations, no stateful signing model, and no per-algorithm side-channel profile. [I]

**ALTERNATIVES REJECTED.** Pure PSA 1.4 (no state model; LMS/XMSS only in beta notes); OpenSSL EVP (heap, provider search); a custom per-primitive API (no agility).

**TRADE-OFFS.** Our own ABI plus a PSA shim on hosts. One more layer, which buys a no-heap guarantee.

**LIMITS.** The scratch-size constants are only as good as the vendored core's actual stack use, which must be measured per build (B.9).

**HOW WE VALIDATE.** Static-analysis check that no provider object calls `malloc`; stack watermark tests; a symbol audit.

### B.4.2 Representative signatures

```c
typedef int32_t pq_status_t;
typedef uint16_t pq_alg_t;

/* ---- registry access (const, no allocation) ---- */
const pq_alg_desc_t *pq_alg_lookup(pq_alg_t alg);                 /* NULL if not compiled in */
size_t pq_sig_max_bytes(pq_alg_t alg);                            /* also compile-time macros per alg */

/* ---- scratch sizing: static query, usable in #define / array dims ---- */
#define PQ_MLDSA65_VERIFY_SCRATCH  /* generated from measured build; 9,888 B on m4f per B.3.2 */
size_t pq_verify_scratch_bytes(pq_alg_t alg);

/* ---- one-shot verify, public inputs only ---- */
pq_status_t pq_verify(pq_alg_t alg,
        const uint8_t *pk, size_t pk_len,
        const uint8_t *ctx, size_t ctx_len,       /* domain-separation string, <= 255 B (FIPS 204) */
        const uint8_t *msg, size_t msg_len,
        const uint8_t *sig, size_t sig_len,
        void *scratch, size_t scratch_len);       /* PQ_OK = accepted; PQ_VERIFY_REJECT otherwise */

/* ---- KEM ---- */
pq_status_t pq_kem_encaps(pq_alg_t alg, const uint8_t *ek, size_t ek_len,
        uint8_t *ct, size_t ct_cap, size_t *ct_len,
        uint8_t ss[32], pq_rng_t *rng, void *scratch, size_t scratch_len);
pq_status_t pq_kem_decaps(pq_alg_t alg, const pq_secret_t *dk,   /* seed form, kept in secret region */
        const uint8_t *ct, size_t ct_len, uint8_t ss[32],
        void *scratch, size_t scratch_len) PQ_CT_SECRET;

/* ---- signing, stateless ---- */
pq_status_t pq_sign(pq_alg_t alg, const pq_secret_t *sk, const uint8_t *ctx, size_t ctx_len,
        const uint8_t *msg, size_t msg_len, uint8_t *sig, size_t sig_cap, size_t *sig_len,
        pq_rng_t *rng /* hedged: required for ML-DSA unless profile says deterministic */,
        void *scratch, size_t scratch_len) PQ_CT_SECRET;

/* ---- signing, stateful: see B.5. The caller cannot name a leaf index. ---- */
pq_status_t pq_sts_sign(pq_sts_key_t *key, const uint8_t *msg, size_t msg_len,
        uint8_t *sig, size_t sig_cap, size_t *sig_len, pq_audit_t *audit);

/* ---- self-test and health ---- */
pq_status_t pq_selftest_run(pq_alg_t alg);          /* KAT; sets sticky state */
pq_status_t pq_health(pq_alg_t alg);                /* PQ_OK or PQ_E_SELFTEST_FAILED / PQ_E_FAULT */
```

### B.4.3 Error model

| Code | Meaning | Caller behaviour |
|---|---|---|
| `PQ_OK` | Success; for verify, **accepted** | proceed |
| `PQ_VERIFY_REJECT` | Verification said no (bad signature, wrong key, malformed) | treat as an attack, rate-limit |
| `PQ_E_ARG` | Pointer or length invalid; sizes inconsistent | programming error |
| `PQ_E_SCRATCH` | Scratch too small | programming error (should be unreachable if sizes came from the static query) |
| `PQ_E_UNSUPPORTED` | Algorithm not compiled in or `DENIED` | policy path |
| `PQ_E_SELFTEST_PENDING` | KAT not yet run | run `pq_selftest_run` |
| `PQ_E_SELFTEST_FAILED` | **Sticky, fatal** for that algorithm until reset | fail closed for authority; for a safety function keep the last-known-good behaviour (atlas class C3) |
| `PQ_E_FAULT` | Redundant-computation or consistency check failed | **Sticky**, same as above, and log |
| `PQ_E_RNG` | Entropy source unhealthy | do not sign or encapsulate |
| `PQ_E_STATE_EXHAUSTED` | Stateful key has no leaves left (B.5) | alarm; switch slot |
| `PQ_E_STATE_IO` | State could not be persisted | **must not sign** |

Rules:
- No error value encodes secret-dependent information.
- Every non-OK path wipes outputs.
- Fault and self-test failures are never silently recoverable.

### B.4.4 Self-test and fault requirements (API level)

- **CAST at boot** for every enabled algorithm: one fixed-input KAT per primitive (ML-KEM encaps/decaps round-trip with a fixed seed; ML-DSA sign/verify; SLH-DSA and LMS verify of a stored signature; SHA-2 and SHA-3 digests). FIPS 140-3 IG 10.3.A requires such self-tests for ML-KEM, ML-DSA and SLH-DSA. [2nd]
- **Pairwise consistency test (PCT)** on every key generation: sign/verify for signatures, encaps/decaps for KEMs. [2nd, same IG]
- **Verify-after-sign** on signing devices, as a policy flag `PQ_POLICY_VERIFY_AFTER_SIGN`. Cost for ML-DSA-65 on the optimised M4 is verify/sign = 2,415,944 / 6,193,171 = 39% extra time. [C from the pqm4 [D] figures]
- **Redundant verification flag** `PQ_POLICY_REDUNDANT_VERIFY`: the verifier evaluates its accept decision twice and combines it so that one corrupted flag cannot admit a signature. Described at API level only.
- Input validation per FIPS 203 §3.3: encaps/decaps may only run on checked inputs. [F via fetch]
- **The pairwise and KAT tests prove implementation integrity at one moment, not freshness.** They are rerun on a schedule (B.9).

---

## B.5 Stateful signatures

### B.5.1 Context

LMS and XMSS (SP 800-208; RFC 8554, RFC 9802 for X.509 [F]) are the only schemes CNSA 2.0 prefers for firmware roots of trust [2nd]. SP 800-230 limited-use SLH-DSA sets (2^24 signatures per key, draft) share the same "count" hazard in a milder form [F]. Atlas problems: R6, P3, P25, N22, N39, N51.

LMS size arithmetic [C; structure per RFC 8554, `nums.py`]:

| Parameter | LMS signature | Leaves (2^h) |
|---|---|---|
| N32, W4, H10 | 2,508 B (matches atlas) | 1,024 |
| N32, W4, H15 | 2,668 B | 32,768 |
| N32, W4, H20 | 2,828 B | 1,048,576 |
| N32, W8, H15 | 1,612 B | 32,768 |
| N24, W8, H10 (SHA-256/192, RFC 9858) | 900 B | 1,024 |
| HSS L=2, H10/H10, W4, N32 | 5,076 B (4 + (2,508 + 56) + 2,508) | 2^20 |

- Formula check: LM-OTS signature = 4 + n + p·n with p = 67 for W4: 4 + 32 + 2,144 = 2,180; LMS signature = 4 + 2,180 + 4 + 32·h; at h=10 that is 2,508.
- CNSA 2.0 does not approve HSS, so CNSA profiles use **single-tree** keys only. [2nd]

**Key-generation cost [E]:** I estimated about `p·(2^w − 1)` hash steps per leaf. That gives 1.1×10^6 hashes for H10/W4, 3.5×10^7 for H15/W4, 1.1×10^9 for H20/W4. At an assumed 10^6 hashes/s (HSM-class software) that is 1 s, 35 s and about 19 min; at an assumed 2×10^7 hashes/s it is 0 s, 2 s and 56 s. The hash rates are assumptions, not measurements.

### B.5.2 Design

**DECISION.** Stateful keys live only inside a signing module that exposes `pq_sts_sign()`. The caller cannot choose, read or set the leaf index. State is managed by **reserve-then-sign with a durable high-water mark** and **non-exportable state**.

```
persistent record (A/B copies, each CRC'd, bound to a hardware monotonic counter):
  { key_id[16], next_free_leaf u64, reserved_until u64, mono_ctr u64, epoch u32, crc u32 }

sign():
  1. if next_free_leaf == reserved_until:
        new_hw = reserved_until + R                       # R = reservation batch, e.g. 1 for roots
        persist {reserved_until = new_hw, mono_ctr++}     # atomic A/B write, then verify readback
        if persist fails -> return PQ_E_STATE_IO          # never sign
  2. leaf = next_free_leaf++ (volatile)                    # only after step 1 returned
  3. sig = LMS_sign(leaf, msg)
  4. verify-after-sign
  5. append audit record (hash chain): {key_id, leaf, SHA-256(msg), time-hint, signer_id}
  6. zeroise one-time key material
crash recovery: on boot, next_free_leaf := reserved_until   # skip unused reservation; waste <= R-1
```

Properties and trade-offs:
- A crash may waste up to `R − 1` leaves, but can never reuse one. For roots that sign a few times a year, `R = 1` costs one persistent write per signature. That is acceptable.
- Waste budget: with 12 signatures a year for 40 years at 2× margin (the counter-capacity rule, B.6.4) the need is 960 leaves, fitting H10 (1,024) with 6.7% spare. H15 (32,768) gives a 34× margin. For a signing service with 4 signatures/day: 4 × 365 × 40 × 2 = 116,800 leaves, which needs H17 or larger; H20 gives 9×. [C]
- **No backup restore.** The key and its state are non-exportable. A restored image of a stateful key is the primary failure mode (N39, N51). Disaster recovery is not a backup but a **pre-provisioned alternate slot** (another LMS key set, or the SLH-DSA-SHA2 slot from F-B1). If an operator must restore, the module refuses unless the restore carries a hardware counter value at least equal to the persisted one, and otherwise marks the key `EXHAUSTED` and burns it.

**Multi-HSM partitioning.** Three options:
1. *Leaf-range partitioning inside one tree* (HSM 1 gets leaves 0-9, etc.). Needs a trusted partition table and a single tree secret in all HSMs. Rejected: the secret is replicated, so a compromise of one HSM yields all.
2. *HSS with per-HSM subtrees.* One offline root signs each HSM's child key. Rejected for CNSA profiles (HSS not approved [2nd]), and signatures grow to 5,076 B.
3. **One independent single-tree key per HSM, with the verifier holding a commitment to a key set.** **Chosen.** The verifier slot holds `H(key-set manifest)`. Each signature carries its public key and a Merkle inclusion proof. No leaf index is ever shared between HSMs. Cost: an extra `32·log2(m)` bytes for m HSMs (for 4 HSMs 64 B) plus the 56 B LMS public key. [C]

**What the verifier needs.**
- A per-slot **leaf-index floor** `q_floor` (monotone). The device stores the highest leaf index it has accepted under each slot and rejects anything below. This does not make LMS stateless. It means that after any accepted authority change, a signer that restores an old state and re-signs old leaves is rejected by every device that already saw a later leaf, which limits the damage of a reset to devices that have not moved. [I] Cost: 8 B per slot; 4 slots = 32 B.
- A **release/epoch counter** in the signed payload that provides anti-rollback independently of the leaf index. The floor is a defence-in-depth measure, not the primary anti-rollback.
- Its own reuse detection is not possible in the verifier. Detection of two different messages under one `(key_id, leaf)` happens in the audit and fleet-evidence layer (11.7): the transparency log flags it and the escape route is the PAM rule (rotate to the alternate slot under a disjoint quorum).

**Auditing.** Every signature appends a hash-chained record. The chain head is countersigned by a second custody domain at least daily. HSM operators cannot delete records; auditors compare leaf counters to the persisted counter. [H]

**Alternatives rejected.** Cisco hash-sigs-style in-library reservation with software state files (no hardware counter; restore hazard remains); XMSS (not in ACVP [F]); stateless SLH-DSA everywhere (CNSA excludes it [2nd]; the 2^64 sets are large and slow, and the 2^24 sets are draft).

**ASSUMPTIONS.** The signing module has durable storage with atomic write semantics and a hardware monotonic counter or equivalent. If not, it must not host a stateful key.

**LIMITS.** An attacker who can restore both state and the counter inside the module defeats this. Physical attacks on HSMs are out of scope here (BRIEF rule 3).

**HOW WE VALIDATE.** TLA+ model of the reserve/sign/crash state machine with the invariant "no `(key_id, leaf)` is ever used twice" under arbitrary crash and restart; fault-injection tests on the storage layer (torn write, stale read); a conformance test that an interrupted `pq_sts_sign` never yields a reused leaf.

---

## B.6 Hybrids, combiners and the symmetric fabric key schedule

### B.6.1 When to hybridise and when not

**DECISION (rules).**

| Situation | Rule | Why |
|---|---|---|
| Key establishment on a networked link (TLS, IKE, enrolment) | **Hybridise**: X25519 + ML-KEM-768 (RFC 10024 group 0x11EC [F]) | Cheap, and protects against an implementation or lattice surprise while classical remains useful |
| Enrolment to a constrained C1/C2 device that cannot afford X25519 + ML-KEM | **ML-KEM-768 alone** (atlas 11.3), once | Fewer cycles, smaller code; the key is one-shot and then replaced by symmetric keys |
| Authority signatures (firmware, floor advance, debug, voucher) | **No classical-only, no OR-hybrid.** Use disjoint-class *quorum* of PQ keys (B.2). A classical AND-composite may be added in the pre-CRQC epoch only as an extra, never as a quorum member | Post-CRQC, the classical half is void (B.1.4); a composite does not add an independent waist |
| Locked first stage | **Never hybrid.** Hash-based only | Smallest code; trust is the lock |
| National-security profile | CNSA 2.0 set only (ML-KEM-1024, ML-DSA-87, LMS) | Compliance; no hybrid mandated, left to the application per NIST IR 8547 [F via fetch] |
| Long-lived symmetric keys | No hybrid concept; use per-device diversification | The symmetric layer is already PQ |

**WHY.** NIST says hybrid is "typically temporary" and adds complexity and risk [F via fetch]. A hybrid is justified when classical still has value over the horizon and the cost is small. It is not justified when it bloats the verifier or gives a false sense of independence.

**ALTERNATIVES REJECTED.** "Hybrid everywhere" (code size in C1/C2 and a false independence claim); "PQ-only everywhere" (loses the hedge for TLS-class links during the period when lattice implementations are young; KyberSlash showed implementation-level flaws exist [2nd: paper title seen in search, details unverified]).

### B.6.2 KEM combiner

**DECISION.** For hybrid KEMs use a *concatenation-with-binding* combiner of the X-Wing type: `ss = SHA3-256(ss_mlkem ‖ ss_x25519 ‖ ct_x25519 ‖ pk_x25519 ‖ label)`. X-Wing's draft states security reduces to ML-KEM-768 IND-CCA or X25519 gap-CDH given SHA3 modelled as a random oracle; sizes: encapsulation key 1,216 B, ciphertext 1,120 B, 32-byte shared secret. [F via fetch, an individual draft, not a standard]

- The ML-KEM ciphertext is **not** in X-Wing's hash because of an ML-KEM-768-specific argument that the draft says depends on its FO transform. So the combiner must not be reused with other KEMs. For ML-KEM-1024 or a different pair, use the generic IETF composite KEM, whose draft (`-23`) is in the RFC Editor queue. [F]
- Series vs parallel principle [H]: assumptions in a **chain** accumulate (AND), those in a **quorum** intersect. For the confidentiality of a hybrid KEM chain, the security is `KECCAK ∧ (MLWE ∨ GapCDH)`: X-Wing keeps `KECCAK` as a single point of dependence, and the hybrid does **not** add a second hash waist.

Sizes [C]: ML-KEM-768 enrolment `ek + ct` = 1,184 + 1,088 = 2,272 B; X-Wing = 1,216 + 1,120 = 2,336 B; ML-KEM-1024 = 1,568 + 1,568 = 3,136 B.

**LIMITS.** An individual draft is not stable. We pin the construction by registry id and test vectors, so the identifier survives if the draft changes.

### B.6.3 Symmetric process-bus key schedule

Atlas ties: 11.3, N10, P19, P20, class rules 12.2 (diversification rule).

**Design.** Levels (all KDF inputs carry a length-prefixed label, device UUID and epoch):

```
L0  KDK[zone]            256-bit key-diversification key, HSM-resident at C4/C5, never leaves; one per zone/site
L1  KEK_dev  = KDF(ss, "KEK/v1" ‖ suite ‖ uuid ‖ kdc_id ‖ H(enrol transcript))     # ss from ML-KEM-768 enrolment
             or  KDF(KDK, "KEK-diversify/v1" ‖ uuid ‖ epoch)                           # factory-injected / no PK path
L2  K_grp(g,e)           256-bit random per group g and epoch e, generated at the KDC DRBG
             delivered as AES-256-KWP(KEK_dev, K_grp ‖ g ‖ e)                          # SP 800-38F style wrap [I]
L3  K_stream = KDF(K_grp, "stream/v1" ‖ stream_id ‖ direction)                        # MAC/GMAC key per stream
L4  per-message tag = MAC(K_stream, counter ‖ payload)                                 # IEC 62351-6 format unchanged
```

**KDF choice.** HKDF with HMAC-SHA-256 (or SHA-384) at L1-L3.
- *Why SHA-2 here:* the bus MAC is already SHA-2/AES. Choosing SHA-2 for the KDF keeps the per-device symmetric chain on a single hash atom. Enrolment adds `KECCAK` and `MLWE` once (unavoidable: ML-KEM uses them internally). The derived-key chain's atoms are therefore {`MLWE_MSIS`, `KECCAK`, `SHA2`} at enrolment and {`SHA2`, `SYM_BLOCK`} afterwards. [I]
- *Rejected:* KMAC256/cSHAKE for L1-L3. It would keep `KECCAK` only but add a second MAC family on a bus whose MAC is SHA-2, widening the union. Revisit if the bus MAC moves.

**Per-device keys.** L1 is unique per device. Dominance and diversification rules of 12.2 hold: a C1 key never opens a C3 relay.

**What group keys cannot do [I]:** any group member can forge any message in the group (a symmetric multicast limit; the atlas's "colony odour"). Mitigations in the design: short epochs, one group per role and zone, per-sender sub-keys where the receiver is not also a sender, and anomaly detection in fleet evidence. Source-origin authentication for multicast under a PQ threat model is an open research item.

**Rekey epochs.** The KDC rotates `K_grp` on a schedule and on any membership change. Epoch `e` is a 32-bit counter plus the group's current-key hash, so a missed rekey is recovered through the counter floor (atlas 11.3).

### B.6.4 Nonce and counter management: the counter-capacity rule

**DECISION (rule).** For every monotonic counter or nonce space with width `w` bits, maximum rate `r` per second and a horizon `H` in seconds (asset life, or key lifetime if rekeyed), the design must satisfy

`2^w ≥ 2 · r · H` (at least 2× margin),

must have **no reset path** short of replacing the key, must raise an alarm at 50% consumption, must force rekey at 90%, and must fail closed for authority operations at 100% (fail-safe for the safety path).

Arithmetic [C, `nums.py`], using a 40-year horizon (1,262,304,000 s):

| Counter / stream | Rate | 32-bit wraps in | 40-year count | Bits needed with 2× | Verdict |
|---|---|---|---|---|---|
| SV, 80 samples/cycle at 50 Hz | 4,000/s | 12.4 days | 5.05×10^12 = 2^42.2 | 43.2 | 32-bit fails; needs 44+ bits **or** rekey ≤ 24 h (2^28.4 per key; 32-bit margin 12.4×) |
| SV, 60 Hz | 4,800/s | 10.4 days | 2^42.5 | 43.5 | Same |
| GOOSE burst average | 100/s | 1.36 years | 2^36.9 | 37.9 | 32-bit fails over life; rekey yearly or widen |
| GOOSE heartbeat | 1/s | 136 years | 2^30.2 | 31.2 | 32-bit OK |
| LoRaWAN-like | 0.1/s | 1,361 years | 2^26.9 | 27.9 | 32-bit OK |
| 1 per ms | 1,000/s | 49.7 days | 2^40.2 | 41.2 | needs 42+ bits or rekey |

These sample rates are scenario assumptions [E]; the 32-bit wrap column is arithmetic.

Related counters:
- Signed 32-bit Unix time wraps on 2038-01-19 03:14:08 UTC (2^31 s); unsigned 32-bit on 2106-02-07. [C]
- The GPS week 10-bit rollover: 1,024 weeks after 2019-04-07 is 2038-11-21 in my arithmetic; the atlas gives 20 November 2038 (GPS time leads UTC by about 18 s, so the UTC rollover falls on the 20th at 23:59:42). [C/I]
- LMS leaf budgets: table in B.5.2. SP 800-230: 2^24 = 16,777,216 signatures per key; at one signature per second that lasts 194 days, so these sets are for release signing, never for online signing. [C]

AEAD nonce rule: for AES-GCM and GMAC (the bus), use a **deterministic counter-based** 96-bit nonce composed of `device-id-slice ‖ epoch ‖ counter` and never random nonces for high-rate streams. SP 800-38D limits random 96-bit nonces to 2^32 invocations per key, and limits by length for the deterministic construction. [F from memory of SP 800-38D; not re-fetched this session. Verify before freezing.]

---

## B.7 Side-channel and implementation-security requirements

### B.7.1 Per-class requirements

| Class | Secret operations present | Requirement | Evidence required |
|---|---|---|---|
| C0 | none | none | n/a |
| C1 (symmetric) | AES/HMAC with per-device key | Table-free or bitsliced AES; MAC compare in constant time. Pqm4's README warns its t-table AES "may be vulnerable to cache attacks" on M4 with a data cache. [F] | CT test (below) |
| C2 (verify-capable) | ML-KEM decapsulation once at enrolment; verify only otherwise | Decaps is `PQ_CT_SECRET`. Verify is public data, no CT demanded, but the accept decision is fault-hardened (B.4.4). | CT test for decaps; redundant-verify test |
| C3 (safety) | as C2, crypto confined to boot/update | Crypto must not share the control loop (R5). No public-key operation in the loop. | WCET report; partition proof |
| C4 (concentrators) | KDC keys, TLS/IKE, decaps, signing of statements | Constant-time cores; hedged signing; stack/heap cleaning; build diversity (two libraries) | CT tests, differential tests |
| C5 (authorities) | release signing, voucher, debug credential | HSM-resident; hedged ML-DSA; stateful rules (B.5); verify-after-sign | HSM certification; B.5 audits |

### B.7.2 Specific cryptographic requirements

1. **Hedged signing is the default.** FIPS 204 says deterministic signing "should not be used" where side-channel attacks are a concern and can't otherwise be mitigated. [F via fetch] Deterministic mode is permitted only in the registry profile `deterministic` and only for host-side tools with a documented reason. PSA also recommends hedged. [F]
2. **Seed-form private keys** for ML-KEM and ML-DSA (32-64 B), with expansion on use. This matches PSA's 32-byte ML-DSA key pair form and NIST's lean toward seed-only for HQC. [F via fetch]
3. **No variable-time division or branching on secrets.** KyberSlash is the cautionary example of a timing flaw from a division in a widely deployed implementation (paper TCHES; I saw its title in search results but did not fetch the abstract). [2nd]
4. **Compiler discipline.** mlkem-native uses barriers and tests several compiler/option combinations against valgrind. [F] We adopt the same: CT tests run for every supported compiler and optimisation level in CI, not just one.
5. **Rejection sampling.** Sampling of public matrices may be variable-time (mldsa-native does this deliberately). Samplers of secret vectors must be constant-time. [F]

### B.7.3 Constant-time verification tooling

| Tool / approach | What it gives | Status in this memo |
|---|---|---|
| valgrind-based secret-taint ("ctgrind"-style) | Detects branches and addresses depending on secret-marked memory in a given run | Used by mlkem-native and mldsa-native [F] |
| `dudect`-style statistical timing | Black-box timing leakage test on real hardware | Named from memory [I]; repository not fetched |
| `timecop` | Poisoning-based taint check used in PQ projects | Named from memory [I] |
| `binsec/rel`, `ct-verif`-style | Static / symbolic constant-time proof on binaries or IR | Named from memory [I]; applicability to our asm unmeasured |
| HOL-Light proofs | Constant-time for asm routines (mlkem-native, mldsa-native) | [F] |

**DECISION.** Three tiers of evidence per implementation, recorded in the descriptor's `sc_profile`:
- `CT-PROVED`: machine-checked constant time for the shipped binary form (only the HOL-Light-covered asm today).
- `CT-TESTED`: valgrind taint and statistical tests pass across the compiler matrix.
- `CT-ASSERTED`: vendor statement only.

A product claim may not say better than its descriptor.

### B.7.4 Fault-attack policy (API level only)

No attack detail is given here. The policy:
- Signing devices use verify-after-sign (B.4.4). Verifying devices that gate authority use the redundant-verify flag.
- Counters and floors are written via the two-copy scheme of B.5.
- A fault or self-test failure is sticky and logged.
- Fault resistance of the hardware is assessed per part from published evidence and certification, not assumed.

### B.7.5 Masking status (what exists, what does not)

| Item | Finding | Evidence |
|---|---|---|
| First-order masked ML-KEM-768 decapsulation, Cortex-M4 | A first-order masked **fine-shuffling** variant has 25% overhead on full ML-KEM-768 decaps, proved secure in the probing model at first order; it replaces a variant whose 51% shuffling was broken by a template attack. | [D] eprint 2026/934 abstract |
| Masked Kyber (Heinz et al.), Cortex-M4 | Paper exists (TCHES 2022; eprint 2022/058, seen in search results). Overhead factors not retrieved. | unverified here |
| Masked FrodoKEM, Cortex-M4 | Exists, but it is FrodoKEM, not ML-KEM. | [D] eprint 2025/1065 |
| Masked ML-DSA | First-order hardware (FPGA) design: 1.127× LUTs, 1.2× flip-flops, **378× execution time**. I found no Cortex-M software masked ML-DSA in this session. | [D] eprint 2024/1817 abstract |
| Masked ML-KEM decaps hardware | First-order 125.4 kGE vs 54.1 kGE unmasked (125.4/54.1 = 2.32×). | [D] eprint 2026/1265 abstract, ratio [C] |

**Conclusion [I].** Masking for ML-KEM on Cortex-M4 has published first-order software, for ML-DSA it does not appear mature on MCUs, and attacks on shuffling variants exist. The project therefore makes **no "masked" claim** in v1. The register entry `sc_profile` has a `MASKED_ORDER1_EVALUATED` code that is unset by default. Devices that hold an ML-KEM or ML-DSA secret on a physically accessible part rely on the atlas's design principle instead: **one opened device yields no fleet authority** (per-device keys, public hashes only in the first stage). Whether any particular MCU needs masking is a per-part assessment from published evidence and certification.

---

## B.8 Encoding and format decisions

**DECISION.** Three formats, by audience:

| Audience | Format | Reason |
|---|---|---|
| Locked first stage (class C2/C3, boot) | **Fixed binary "authority envelope", no parser** | Smallest verifier; no CBOR/ASN.1 attack surface in immutable code |
| Constrained updatable software, SUIT, attestation, vouchers | **Deterministic CBOR (RFC 8949 §4.2) in COSE** (`COSE_Sign` for multi-signature quorums) | Native multi-signer structure maps to the quorum rule; compact; SUIT is CBOR-based |
| C4/C5 PKI, TLS, CMS | **X.509/ASN.1 DER** per RFC 9881 / 9909 / 9935 | Existing PKI and TLS stacks |

**Authority envelope v1 (binary, big-endian, fixed offsets).**

```
off  len  field
0    4    magic "AUTH"
4    2    format_version = 1
6    2    n_sigs (<= 4)
8    4    policy_id            (selects accept_table, B.2.2)
12   8    release_epoch        (u64, anti-rollback)
20   8    leaf_floor_hint      (u64, informative)
28   32   payload_hash         (SHA-256 or SHA3-256 per policy; algorithm in policy)
60   per signature i:  { alg_id u16, key_slot u8, rsvd u8, sig_len u16, sig[sig_len] }
```
Size [C]: header 60 B; per-signature framing 6 B. A two-signature quorum of LMS W4 H10 (2,508) + ML-DSA-65 (3,309) is 60 + 2·6 + 2,508 + 3,309 = **5,889 B**. A CNSA pairing ML-DSA-87 (4,627) + LMS W4 H10 (2,508) is 60 + 12 + 7,135 = **7,207 B**. LMS + SLH-DSA-128-24 (draft 3,856 [F via fetch]) is 60 + 12 + 2,508 + 3,856 = **6,436 B**. The raw signature sums are 5,817, 7,135 and 6,364 B. [C]

**Canonical encoding rules.**
1. Signed content is `domain-tag ‖ policy_id ‖ release_epoch ‖ payload_hash` with a registry-assigned domain tag per transition type (floor advance, slot replacement, lifecycle, release). No two transition types share a tag.
2. Fixed-width integers, big-endian; no optional fields in the envelope.
3. CBOR: deterministic encoding only (shortest-form integers and lengths, sorted map keys), definite lengths, no tags except those registered. Decoders must reject non-canonical forms.
4. Signatures: ML-DSA verification checks the standard canonical encodings (the standard's signature decoding is canonical); a library that does not reject malformed hint or response encodings fails conformance (B.9).
5. Public keys in the envelope are always identified by `(alg_id, key_slot)` and checked against the slot hash; keys are never trusted from the envelope itself.

**Identifier status and risk.**

| Identifier | Value | Status | Risk |
|---|---|---|---|
| COSE ML-DSA-44/65/87 | -48 / -49 / -50 | **Final**, RFC 9964 [F] | low |
| COSE key type AKP | 7 | Final, RFC 9964 [F] | low |
| COSE SLH-DSA-SHA2-128s / SHAKE-128s | -51 / -52 requested | **Draft** (`-10`); only 128s sets | medium; limited sets and TBD |
| COSE FN-DSA-512 / 1024 | -54 / -55 requested | **Draft** (`-05`) | high: FIPS 206 not final |
| COSE HSS-LMS | -46 | RFC 8778 from memory | unverified; verify before freezing |
| X.509 ML-DSA, SLH-DSA, ML-KEM | RFC 9881, 9909, 9935 | **Final** [F] | low |
| X.509 FN-DSA OIDs | "TBD"/"XX" in draft | Draft | high |
| X.509 composite | OIDs in IESG-stage drafts | Draft | medium; do not freeze |
| TLS X25519MLKEM768 | 0x11EC | **Final** (RFC 10024) [F] | low |
| TLS pure ML-KEM groups | 0x0200-0x0202 | Draft in RFC Editor queue; "Recommended: N" | medium |
| SUIT PQ profile | none found | **Gap** | high |
| SP 800-230 sets | no COSE or OID yet | Draft | high |

NIST OID leaf values for ML-DSA, ML-KEM and SLH-DSA are in the NIST CSOR registry; I did not re-fetch them this session and so do not list them. [unverified]

**Registry rule.** Project `alg_id` is the stable identity. Mapping tables to COSE, X.509, TLS and PSA ids are separate data and may be updated without touching a descriptor. That prevents N25 (draft OIDs frozen into devices).

**Gap to flag to the merge.** Because the SUIT working group's MTI draft does not carry an ML-DSA or SLH-DSA profile and it expired in January 2026, a SUIT-based update path for PQ signatures needs a project-specified COSE profile, offered upstream. [I]

---

## B.9 Crypto test strategy

**DECISION.** Seven layers, each with a gate in CI.

1. **Known-answer tests (KATs).** NIST ACVP vectors for ML-KEM, ML-DSA, SLH-DSA and LMS; no XMSS entry exists in ACVP [F], so XMSS (if ever added) uses RFC 8391 vectors and the reference implementation. mldsa-native already tests against ACVP and Wycheproof [F], so our adapter test just proves the adapter does not alter the results.
2. **ACVP-style harness in-house.** Run the ACVP request/response format locally against our provider (the specs are public drafts [F]). For any module a customer takes to CMVP, the real CAVP process then applies. CMVP #5523 shows a module with ML-KEM/ML-DSA/SLH-DSA CAVP certificates already exists [F via fetch].
3. **Wycheproof-style negative vectors.** Malformed keys, ciphertexts and signatures; non-canonical encodings; boundary values; ML-KEM encapsulation-key modulus and decapsulation-key checks (FIPS 203 §3.3 requires checked inputs [F via fetch]). We contribute vectors where gaps exist.
4. **Differential testing.** Every primitive runs against at least two independent implementations (mlkem-native, libcrux, RustCrypto `ml-kem` 0.3.4, OpenSSL 3.5, AWS-LC; for ML-DSA likewise; for SLH-DSA: slhdsa-c, OpenSSL, RustCrypto `slh-dsa`; for LMS: our verify-only, hash-sigs, wolfBoot). A disagreement is a release blocker. This is the Knight-Leveson hedge. [I]
5. **Fuzzing.** Coverage-guided fuzzers on every parser and on each `pq_*` entry with sanitizers (ASan, UBSan, MSan). Stateful-signing fuzz: random crash points. Registry and envelope parsers fuzzed continuously. AWS-LC's CI practice is the model (fuzz, sanitizers on every change). [F]
6. **Constant-time suite.** valgrind taint, statistical timing, and, where available, the HOL-Light-proved asm (B.7.3). Run per compiler/optimisation matrix.
7. **Formal methods.** (a) Reuse the CBMC and HOL-Light proofs from mlkem-native and mldsa-native. (b) Our verify-only LMS and SLH-DSA: CBMC for memory safety plus a functional spec checked against test vectors. (c) TLA+ for the quorum policy evaluation, floor monotonicity and the stateful reserve/sign/crash machine (invariants in B.5 and atlas 11.1). (d) The quorum checker (`dq.py`) is property-tested: monotonicity (adding a key never lowers acceptance); exhaustive agreement with `models/quorum.py`; known-answer cases from B.2.3.

**Provenance tests.** Vendored subtrees are checked by hash against the upstream tag; the build refuses an unexpected diff.

**Measurement tests.** Stack and flash per algorithm per target are measured, not estimated, and compared to the scratch constants in the ABI. A mismatch fails the build.

**LIMITS.** Tests demonstrate absence of known bugs, not absence of bugs. Formal proofs, per their authors, are "never absolute" (mlkem-native README [F]); their SOUNDNESS documents define the scope.

**HOW WE VALIDATE THE VALIDATORS.** Mutation testing: seeded defects (flip a rejection bound, skip a check) must be caught by at least one layer.

---

## B.10 Agility policy over decades

### B.10.1 The threats

- **Agility atrophy** (R10, N57, N64): spare algorithm slots that were never used fail when needed.
- **Downgrade** (N45 and the TLS history): an attacker forces the weakest mutually supported algorithm.
- **Draft freeze** (N25): a device ships with a draft identifier that later changes.

### B.10.2 Policy

1. **Authenticated policy, not negotiation.** For authority operations there is no negotiation. The device's own signed policy table says which algorithms are accepted, as a function of the registry state and the epoch. A message cannot select its own verification algorithm: the envelope's `alg_id` must match the slot's recorded algorithm. (B.8)
2. **Monotone floor on algorithms.** The policy has an `algorithm floor`, advanced like the index floor, by a disjoint quorum. Once an algorithm is `DENIED`, no signed message can re-admit it. A new `alg_id` is needed for a fixed version.
3. **Transcript binding for protocols.** Handshakes (TLS, IKE) bind the offered algorithm list into the transcript. The hybrid combiner includes the ciphertexts and public keys (B.6.2).
4. **No silent fallback.** If the preferred algorithm fails (selftest failure, verification error), the device fails to a defined state (B.4.3) and reports it; it does not retry with something weaker.
5. **Draft algorithms are `PROPOSED`.** They can be shadow-signed (the molting protocol of atlas 11.1) but not authorised (B.1.5).

### B.10.3 Drills (anti-atrophy)

| Drill | Frequency | What it proves | Pass criterion |
|---|---|---|---|
| **Slot drill** (atlas I-13) | Yearly per fleet cohort | A release verifies through the *alternate* assumption class alone | Cohort reports the alternate slot verified; no regression |
| **Algorithm-removal build** | Every release in CI | Product builds and passes tests with each non-baseline algorithm compiled out | Green matrix |
| **Registry-denial rehearsal** | Yearly in a lab fleet | A `DENIED` status record propagates and devices reject the algorithm | 100% of lab devices reject |
| **Quorum-loss rehearsal** | Yearly | An authority change succeeds when one slot is unavailable (F-B1) | Succeeds with the LMS slot off-line |
| **State-recovery rehearsal** | Yearly | Stateful key crash recovery never reuses a leaf | Audit shows monotone leaves |
| **Identifier-change rehearsal** | On each standards change | A COSE/OID mapping update flows without touching descriptors | Mapping table updated only |
| **Checker re-run** | On any registry change | `dq.py`-style check on all policies, per epoch profile and merged-waist | No policy with κ < 2 |

Frequency principle from the atlas: "exercise the change path on a rhythm". [H, from atlas Part 0 and 7.3]

### B.10.4 Sunset ladder

Each algorithm has a published planned path through `ADMITTED → RECOMMENDED → LEGACY_VERIFY → DENIED`, aligned with external dates: NIST IR 8547's 2030 deprecation and 2035 disallowance for quantum-vulnerable public-key algorithms [F via fetch] and the CNSA 2.0 dates [2nd]. Devices carry a signed *exit clock* per legacy exception (atlas I-9).

**LIMITS.** No policy can protect a device whose verifier is immutable and single-family (the atlas's "hard boundary"). Agility policy applies only to devices with a locked stage that has a multi-class slot structure and an updatable second stage.

---

## B.11 Consolidated findings for the merge

1. **Two gaps in the atlas's own rule (F-B1, F-B2).**
   - Every accepted disjoint pair of the three-slot set contains the stateful LMS key. Add a stateless SLH-DSA-SHA2 slot (128 B of slot hashes instead of 96 B).
   - MV-1's single-hash verifier cannot enforce the disjoint rule: it needs a `KECCAK`-class verifier in the locked stage.
2. **Atlas statement "LMS-SHA256 or SLH-DSA-SHA2 → {SHA-256}" is incomplete**: LMS also exists with SHAKE256 (RFC 9858), and SLH-DSA-SHA2 uses SHA-512 at categories 3/5. The descriptor must carry the hash.
3. **Standards moved**: IR 8547 is now final (2026-10-27); RFC 9964, 9881, 9909, 9935 and RFC 10024 are published; FIPS 206 and HQC are still not final or not even drafted; SP 800-230 is IPD with comments closed; PQClean is retired and pqm4 deprecated.
4. **CNSA 2.0 excludes SLH-DSA**, which conflicts with using SLH-DSA-limited-use sets (SP 800-230) in national-security profiles. A profile switch is required in the registry.
5. **The 22 ms / 14.2 KB decapsulation figure** corresponds to the unoptimised implementation; the M4 optimised version needs about 2.8-6.5 KB and about half the cycles.
6. **Counter-capacity**: a 32-bit sampled-values counter wraps in 12.4 days at 4,000 frames/s, so counters must be wider or keys rotated at least daily.

## B.12 Open questions

- What is the flash cost of a Keccak-class verifier in the locked stage on M0+? (Needs measurement.)
- Does CNSA 2.0 approve LMS with SHAKE or SHA-256/192 parameters? (NSA PDF unreachable.)
- Is there any SUIT PQ draft in progress beyond `suit-mti`? (Search found none; the working group chairs should be asked.)
- Real Cortex-M0+/M3 numbers for mlkem-native and mldsa-native portable C (pqm4 data is M4 only and the project is deprecated).
- Masked ML-DSA software on MCUs: none found.
- Final FIPS 206 and FIPS 207 text, and SP 800-230 final sizes. The draft table I recorded (3,856 / 7,752 / 14,944 B) was extracted through a summarising fetch and should be re-read from the PDF.

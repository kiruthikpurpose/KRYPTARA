# Standards mapping: SUIT, TUF, transparency logs, ownership vouchers

**Level:** L3. **Date:** 2026-11-12. This maps kernel concepts onto existing standards so KRYPTARA can ride on them rather than replace them. Only the TUF row and the RFC 9162 row have executable checks; the rest is a design mapping [Proposed]. No standard's parser or reference implementation was run against KRYPTARA objects.

| Standard | What it carries | Kernel concept it maps to | Where KRYPTARA is stricter | Check |
|---|---|---|---|---|
| SUIT manifests | Image digest, sequence number, conditions, signature by a manifest signer | An `ACTIVATE_IMAGE` transition carries the image digest; the chain position plays the role of the sequence number | The SUIT signer is provenance only. Authority to boot comes from the authorised `ACTIVATE_IMAGE` record (ADR-007, REQ-IMG-01), so one OEM key cannot make a device boot an image | `src/kernel.c` `ac_image_bootable` (host) [M]; SUIT encoding not exercised |
| TUF / Uptane roles | Per-role k-of-n thresholds, chained root rotation, expiry | Each role's threshold is a monotone table over SIG atoms | Thresholds are checked against labelled fault classes. 2-of-3 is unsafe if the keys share an organisation or an algorithm; TUF metadata does not express this. Expiry is not used as authority (time only restricts, D-18) | `models/tuf_mapping.py` [M], CLM-59 |
| Certificate Transparency (RFC 9162) | Merkle tree head, inclusion proofs | Witnessed receipt (WIT atom, REQ-PUB-01) | Two independent logs are required for evidence without presence | `models/merkle_inclusion.py` [M], `models/witness_receipt.py` [M] |
| SCITT, C2SP checkpoints and cosignatures | Signed statements, receipts, witness cosignatures | Same WIT atom; the C2SP cosignature is what makes a log "independent" in practice | Same as above | **None.** Checkpoint text format and cosignature verification are not implemented |
| FDO ownership vouchers | A chain of signed entries, each passing ownership to the next owner | An owner transfer is a `KEY_INSTALL` into the OWNER group's slots | The current owner must co-sign the installation of the new owner's key (REQ-LIFE-02). A voucher that skips the holder is refused | `ac_key_install_authorised` (host C) [M]; voucher encoding not exercised |
| EAT / CoRIM attestation | Device claims and reference values | State reports (out of the locked stage) | No KRYPTARA decision depends on an attestation claim | None |

## Worked transfer: owner A sells a device to owner B

1. A's two OWNER-group keys are installed and ACTIVE. B has generated two keys.
2. B's first key goes into OWNER slot 1: a T2 `KEY_INSTALL`. It needs the T2 table's evidence and A's slot-1 key (holder co-signature). Without A's signature the kernel refuses, even if OEM and ESCROW both sign.
3. The same for slot 2.
4. The transition records go into the chain and are published to two logs, so the transfer is visible.
5. If A has vanished, there is no holder to co-sign. The path is then the T2 RECOVERY tier (presence plus custody atoms plus delay), not a quiet re-key; this is the trade-off Theorem 3 describes.

**Limits.** Steps 2–3 are exercised in host C and in the TLA+ model (`Repl3OK`, holder co-signature invariant `Inv_HolderConsent`); step 5 is a design statement, not a test.

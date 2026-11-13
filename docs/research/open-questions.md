# Open questions

| ID | Question | Why open |
|---|---|---|
| OQ-01 | What does the owner intend "Yielding" to mean? | No source defines it; vision-and-scope offers proposals only |
| OQ-02 | Do SRC-08 and SRC-11 (same title, different size) derive from one document? | Not compared |
| OQ-03 | Does the TLA+ base model complete without violation? | Recorded run unfinished |
| OQ-04 | How to mitigate correlated presence (F-R2-04) in terrestrial profiles? | Lint mode not written |
| OQ-05 | Are dual hash families independent enough to count as two classes? | EXP-18 not run |
| OQ-06 | Does the 3–10 ms admission estimate hold on silicon? | EXP-19 not run |
| OQ-07 | How do the 221 legacy requirements map onto REQ-? | Not reconciled |
| OQ-08 | Is the composition novel? | No patent search |
| OQ-09 | Does anything justify the broader "paradigm" scope? | No evidence |
| OQ-10 | Rev 4 text still says 682 B in places? | Banner and corrections applied to slices; sources unchanged |
| OQ-11 | Stack usage of hardened admission code | Not re-measured |
| OQ-12 | REQ-LIFE-02 requires the current holder to co-sign any key installed into an ACTIVE slot. If the holder has lost the key, can the slot be re-keyed at all? Candidate answers: retire the slot first (a T1 tightening) and install into the now-empty slot, or let the T2 RECOVERY tier override the co-signature. **Proposed answer: retire first, then install (ADR-040), checked by `models/lost_holder.py`; not in the TLA+ model.** | Found during the R2 review of sliced documents (2026-11-12); affects lifecycle §7.4/§7.8, problem-mapping G5, D-05 |
| OQ-13 | Has the 50-item completion plan's GATE-07 size budget survived the functions added to `src/policy8.c` since 902 B was measured? | Answered 2026-11-13 by the first CI run: no. 1,196 B against the 1,024 B budget (GATE-07 fails as worded). Open: raise the budget by ADR or move provisioning-only functions out of the locked stage |
| OQ-14 | The PAM rule (revoking any current key needs the escrow slot's own signature plus presence, ADR-024/D-05) makes ADR-040's retire step impossible for the escrow slot itself, so a lost escrow key cannot be recovered in the first-stage design. Options: exempt revocation of the escrow slot's own keys from the PAM rule when presence and a disjoint quorum of the other slots sign (re-checking F-R2-03 and Inv_PAM), accept the loss and document it, or keep a spare escrow slot. None is decided | Model-checked 2026-11-12 (`cfg_w_repl_lost3`, `cfg_w_repl_lost3_nopam`); blocks acceptance of ADR-040 |

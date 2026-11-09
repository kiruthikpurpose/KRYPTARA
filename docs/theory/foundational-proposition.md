# Foundational proposition

**Level:** L2. **Class:** Derived inside the stated model; the generalisation is Speculative.

**Proposition (verified scope).** Long-lived artefacts fail at governance when authority is tied to one assumption class (a key, a custodian group, a hash family). If authority is expressed as a monotone function over evidence atoms labelled with fault classes, then the policies that are both safe against one fault and live after one loss are exactly the monotone functions in the interval [Lo, U], computable by a small on-device routine (CLM-01, CLM-02). Recovery capacity is bounded by the number of independent classes (CLM-02, CLM-03).

**Assumptions.** Fault model is complete and classes are independent (R-1, CLM-11); labels are truthful (ceremonies); presence is independent of ownership (F-R2-04).

**Testable consequences.** HYP-01..04 in `docs/simulation/simulation-specifications.md`; EXP-xx in `docs/validation/falsification-programme.md`.

**Not claimed.** A new computational paradigm (CLM-17), novelty (CLM-16), safety-certified fault tolerance.

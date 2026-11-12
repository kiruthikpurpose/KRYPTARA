---------------------------- MODULE FirstStage ----------------------------
\* Stream V, V.2: first-stage authority state machine (locked-flash verifier).
\* States: BOOT, VERIFY_B (primary second stage), VERIFY_ALT (alternate), RUN, LKG, BRICK_GUARD.
\* Authority operations: ADVANCE_FLOOR, REVOKE (with PAM rule), REPLACE_SLOT3, RESTORE (anergy).
\* Power cut: modelled as (a) interleaving at every micro-step of every multi-step NV write
\* (journal commit / burn / clear; image begin/end) and (b) an explicit reset action from any pc.
\* Adversary: at most MaxFail "single failures" chosen at Init: one broken assumption atom
\* (fa) and/or one stolen slot key (fk). Attacker forges signatures only of keys whose
\* assumption set contains fa, or of slot fk. Attacker cannot forge physical presence.
EXTENDS Integers, FiniteSets, TLC

CONSTANTS MaxF, MaxReq, Rule, AnergyMode, CapGuard, ImgGuard, PamRule, MaxFail, Thresh, HolderCoSign, EscLost

Slots  == 1..3
Gens   == 0..MaxF
Atoms  == {"SHA2", "KECCAK", "LATTICE", "ECC"}
NOSIG  == -1
Esc    == 3
NONE   == "NONE"
NoReq  == [op |-> "NONE", sg |-> [s \in 1..3 |-> -1], ts |-> 0, tg |-> 0, nc |-> {}, vo |-> FALSE, pr |-> FALSE, hn |-> FALSE, tf |-> 0]
NOJ    == -1   \* empty journal
Classes == { {"SHA2"}, {"KECCAK"}, {"LATTICE","KECCAK"}, {"ECC"} }

InitCls(s) == IF s = 1 THEN {"SHA2"} ELSE IF s = 2 THEN {"KECCAK"} ELSE {"LATTICE","KECCAK"}
InitHas(s, g) == IF s = 2 THEN g <= MaxF - 1 ELSE TRUE   \* slot 2 has no key for the last generation

VARIABLES floor, has, cls, strikes, anergic, journal, req, imgs, lkg,
          pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder
vars == <<floor, has, cls, strikes, anergic, journal, req, imgs, lkg,
          pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

Img == [st : {"GOOD","TORN","EMPTY"}, sg : Slots, gn : Gens]
GoodImg(s, g) == [st |-> "GOOD", sg |-> s, gn |-> g]

\* ---------- key validity, forgery, quorum ----------
KeyValid(s, g) == has[s][g] /\ g >= floor
Forge(s, g) == (fa \in cls[s][g]) \/ (fk = s)
VoucherForge == (fa = "ECC")

Disj(a, b) == (Rule = "TWOOF") \/ (cls[a[1]][a[2]] \cap cls[b[1]][b[2]] = {})

ValidSig(sg, s) == sg[s] # NOSIG /\ KeyValid(s, sg[s])

\* AnergyMode: OFF (no strikes), TELEMETRY (strikes recorded, no effect on quorum),
\*   SOFT (a quorum may not have both members anergic), STRICT (anergic keys excluded),
\*   CAPPED (STRICT, but anergy is never applied if it would leave no usable disjoint pair)
AnergyOKS(S, i, j) ==
  CASE AnergyMode = "STRICT" \/ AnergyMode = "CAPPED" -> (i \notin S /\ j \notin S)
    [] AnergyMode = "SOFT"   -> ~(i \in S /\ j \in S)
    [] OTHER                 -> TRUE
AnergyOK(i, j) == AnergyOKS(anergic, i, j)

\* QuorumP(sg, P): two valid signatures from different slots, assumption sets disjoint, P holds for the pair
QuorumP(sg, P(_,_)) ==
  \E i, j \in Slots : i < j /\ ValidSig(sg, i) /\ ValidSig(sg, j)
      /\ Disj(<<i, sg[i]>>, <<j, sg[j]>>) /\ AnergyOK(i, j) /\ P(sg[i], sg[j])

AnyPair(a, b) == TRUE
Survivor(a, b) == (a >= floor + 1) \/ (b >= floor + 1)   \* a signer is not retired by this advance

\* quorum capability of a key table at a floor (no anergy: structural capability)
CapAt(f, h, c) ==
  \E i, j \in Slots : i < j /\ \E gi, gj \in Gens :
     gi >= f /\ gj >= f /\ h[i][gi] /\ h[j][gj]
     /\ (Rule = "TWOOF" \/ c[i][gi] \cap c[j][gj] = {})

BootableAt(f, h, im, lk) ==
  \E x \in {im[1], im[2], lk} : x.st = "GOOD" /\ h[x.sg][x.gn] /\ x.gn >= f

Valid(x) == x.st = "GOOD" /\ KeyValid(x.sg, x.gn)

\* ---------- request records ----------
\* op in {"ADV","REVOKE","REPL3","RESTORE"}; sg: slot -> gen or NOSIG; tf: floor the request was signed for
Reqs(sigs, vouchers, press, hon, tfs) ==
  { [op |-> "ADV", sg |-> s, ts |-> 0, tg |-> 0, nc |-> {}, vo |-> v, pr |-> p, hn |-> hon, tf |-> t] :
       s \in sigs, v \in vouchers, p \in press, t \in tfs }
  \cup { [op |-> "REVOKE", sg |-> s, ts |-> ts, tg |-> tg, nc |-> {}, vo |-> v, pr |-> p, hn |-> hon, tf |-> t] :
       s \in sigs, ts \in Slots, tg \in Gens, v \in vouchers, p \in press, t \in tfs }
  \cup { [op |-> "REPL3", sg |-> s, ts |-> 0, tg |-> 0, nc |-> c, vo |-> v, pr |-> p, hn |-> hon, tf |-> t] :
       s \in sigs, c \in Classes, v \in vouchers, p \in press, t \in tfs }
  \cup { [op |-> "RESTORE", sg |-> s, ts |-> ts, tg |-> 0, nc |-> {}, vo |-> v, pr |-> p, hn |-> hon, tf |-> t] :
       s \in sigs, ts \in Slots, v \in vouchers, p \in press, t \in tfs }

\* EscLost = TRUE models OQ-12: slot 3's holder has lost its key, so no honest request carries a
\* slot-3 signature. (An attacker who stole it, fk = 3, still can; the attacker model is unchanged.)
HonestSigs == { f \in [Slots -> {NOSIG} \cup {g \in Gens : g = floor \/ g = floor + 1}] : ~EscLost \/ f[Esc] = NOSIG }
AttackSigs == { f \in [Slots -> {NOSIG} \cup Gens] : \A s \in Slots : f[s] = NOSIG \/ Forge(s, f[s]) }

\* ---------- acceptance predicates ----------
CurrentTarget(r) == has[r.ts][r.tg] /\ r.tg >= floor

AdvOK(r) ==
  /\ r.tf = floor /\ floor < MaxF
  /\ QuorumP(r.sg, Survivor)

AdvGuards ==
  /\ (CapGuard => CapAt(floor + 1, has, cls))
  /\ (ImgGuard => BootableAt(floor + 1, has, imgs, lkg))

HasAfterRevoke(r) == [has EXCEPT ![r.ts][r.tg] = FALSE]

RevOKCore(r) ==
  /\ r.tf = floor
  /\ IF CurrentTarget(r)
       THEN IF PamRule
              THEN ValidSig(r.sg, Esc) /\ r.pr
              ELSE QuorumP(r.sg, AnyPair)
       ELSE \E s \in Slots : ValidSig(r.sg, s)

RevGuards(r) ==
  /\ (CapGuard => CapAt(floor, HasAfterRevoke(r), cls))
  /\ (ImgGuard => BootableAt(floor, HasAfterRevoke(r), imgs, lkg))

HasAfterRepl == [has EXCEPT ![3] = [g \in Gens |-> g = floor]]

\* REQ-LIFE-02: installing a key into an ACTIVE slot requires that slot's own holder to co-sign
\* (F-R2-03: otherwise an outside quorum could replace slot 3's key without slot 3's participation).
\* HolderCoSign = FALSE is the mutation that removes the rule (cfg_m9_nocosign).
\* "ACTIVE" = the slot currently holds a key usable at this floor; an already-revoked slot has
\* no holder left to co-sign, so the requirement does not apply (it is not a live key install then).
SlotActive(s) == \E g \in Gens : g >= floor /\ has[s][g]

Repl3OK(r) ==
  /\ r.tf = floor /\ r.vo
  /\ ((HolderCoSign /\ SlotActive(Esc)) => ValidSig(r.sg, Esc))   \* slot-holder co-signature on its own replacement
  /\ \E s \in {1, 2} : ValidSig(r.sg, s)
       /\ (Rule = "TWOOF" \/ cls[s][r.sg[s]] \cap {"ECC"} = {})   \* voucher assumption {ECC} vs signer

Repl3Guards(r) ==
  /\ (CapGuard => CapAt(floor, HasAfterRepl, [cls EXCEPT ![3][floor] = r.nc]))
  /\ (ImgGuard => BootableAt(floor, HasAfterRepl, imgs, lkg))

RestoreOK(r) ==
  /\ r.tf = floor /\ r.ts \in anergic
  /\ \E i, j \in Slots : i < j /\ ValidSig(r.sg, i) /\ ValidSig(r.sg, j)
        /\ Disj(<<i, r.sg[i]>>, <<j, r.sg[j]>>) /\ ~(i \in anergic /\ j \in anergic)

\* A request is strike-worthy iff it is fresh, carries >=1 valid signature, and LACKS THE SECOND CLASS
\* (v2: a request rejected for another reason, e.g. no surviving signer, is not "probing"; see cex0)
Fresh(r) == r.tf = floor
HasValidSig(r) == \E s \in Slots : ValidSig(r.sg, s)
DisjPairAny(r) == \E i, j \in Slots : i < j /\ ValidSig(r.sg, i) /\ ValidSig(r.sg, j)
                    /\ Disj(<<i, r.sg[i]>>, <<j, r.sg[j]>>)
Lacks2nd(r) ==
  CASE r.op = "ADV" \/ r.op = "RESTORE" -> ~DisjPairAny(r)
    [] r.op = "REVOKE" -> CurrentTarget(r) /\ ~(ValidSig(r.sg, Esc) /\ r.pr)
    [] OTHER -> ~(r.vo /\ \E s \in {1, 2} : ValidSig(r.sg, s))

Accepted(r) ==
  CASE r.op = "ADV"     -> AdvOK(r)
    [] r.op = "REVOKE"  -> RevOKCore(r)
    [] r.op = "REPL3"   -> Repl3OK(r)
    [] r.op = "RESTORE" -> RestoreOK(r)

Guards(r) ==
  CASE r.op = "ADV"    -> AdvGuards
    [] r.op = "REVOKE" -> RevGuards(r)
    [] r.op = "REPL3"  -> Repl3Guards(r)
    [] OTHER           -> TRUE

\* ---------- init ----------
Init ==
  /\ floor = 0
  /\ has = [s \in Slots |-> [g \in Gens |-> InitHas(s, g)]]
  /\ cls = [s \in Slots |-> [g \in Gens |-> InitCls(s)]]
  /\ strikes = [s \in Slots |-> 0] /\ anergic = {}
  /\ journal = NOJ /\ req = NoReq
  /\ imgs = << GoodImg(1, 0), [st |-> "EMPTY", sg |-> 1, gn |-> 0] >>
  /\ lkg = GoodImg(2, 0)
  /\ pc = "BOOT" /\ run = 0 /\ nreq = 0
  /\ fa \in Atoms \cup {NONE} /\ fk \in Slots \cup {0}
  /\ (MaxFail >= 2 \/ fa = NONE \/ fk = 0)
  /\ histAdv = FALSE /\ histRev = FALSE /\ histRepl = FALSE /\ histNoHolder = FALSE

\* ---------- environment ----------
HonestDeposit ==
  /\ req = NoReq /\ nreq < MaxReq
  /\ \E r \in Reqs(HonestSigs, {TRUE}, BOOLEAN, TRUE, {floor}) : req' = r
  /\ nreq' = nreq + 1
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, imgs, lkg, pc, run, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

AttackDeposit ==
  /\ req = NoReq /\ nreq < MaxReq
  /\ \E r \in Reqs(AttackSigs, IF VoucherForge THEN BOOLEAN ELSE {FALSE}, {FALSE}, FALSE, 0..floor) : req' = r
  /\ nreq' = nreq + 1
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, imgs, lkg, pc, run, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

PowerCut ==
  /\ pc # "BOOT"
  /\ pc' = "BOOT" /\ run' = 0
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, imgs, lkg, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

\* ---------- boot: journal replay, then request processing ----------
Burn ==
  /\ pc = "BOOT" /\ journal # NOJ /\ floor < journal
  /\ floor' = journal
  /\ UNCHANGED <<has, cls, strikes, anergic, journal, req, imgs, lkg, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

ClearJ ==
  /\ pc = "BOOT" /\ journal # NOJ /\ floor >= journal
  /\ journal' = NOJ
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, req, imgs, lkg, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

AuthPossibleS(S) ==
  \E i, j \in Slots : i < j /\ \E gi, gj \in Gens :
      KeyValid(i, gi) /\ KeyValid(j, gj) /\ Disj(<<i, gi>>, <<j, gj>>) /\ AnergyOKS(S, i, j)

StrikeUpdate(r) ==
  LET hit == { s \in Slots : ValidSig(r.sg, s) }
      st2 == [s \in Slots |-> IF s \in hit THEN strikes[s] + 1 ELSE strikes[s]]
      cand == anergic \cup { s \in hit : st2[s] >= Thresh }
  IN /\ strikes' = st2
     /\ anergic' = IF AnergyMode = "CAPPED" /\ ~AuthPossibleS(cand) THEN anergic ELSE cand

\* accepted + guards pass: apply
ApplyReq ==
  /\ pc = "BOOT" /\ journal = NOJ /\ req # NoReq
  /\ Accepted(req) /\ Guards(req)
  /\ LET r == req IN
     CASE r.op = "ADV" ->
            /\ journal' = floor + 1 /\ req' = NoReq
            /\ histAdv' = (histAdv \/ ~r.hn)
            /\ UNCHANGED <<floor, has, cls, strikes, anergic, imgs, lkg, pc, run, nreq, fa, fk, histRev, histRepl, histNoHolder>>
       [] r.op = "REVOKE" ->
            /\ has' = HasAfterRevoke(r) /\ req' = NoReq
            /\ histRev' = (histRev \/ (~r.hn /\ CurrentTarget(r)))
            /\ UNCHANGED <<floor, cls, strikes, anergic, journal, imgs, lkg, pc, run, nreq, fa, fk, histAdv, histRepl, histNoHolder>>
       [] r.op = "REPL3" ->
            /\ has' = HasAfterRepl /\ cls' = [cls EXCEPT ![3][floor] = r.nc] /\ req' = NoReq
            /\ histRepl' = (histRepl \/ ~r.hn)
            /\ histNoHolder' = (histNoHolder \/ (SlotActive(Esc) /\ ~ValidSig(r.sg, Esc)))
            /\ UNCHANGED <<floor, strikes, anergic, journal, imgs, lkg, pc, run, nreq, fa, fk, histAdv, histRev>>
       [] OTHER ->  \* RESTORE
            /\ strikes' = [strikes EXCEPT ![r.ts] = 0] /\ anergic' = anergic \ {r.ts} /\ req' = NoReq
            /\ UNCHANGED <<floor, has, cls, journal, imgs, lkg, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

\* not accepted, or accepted but refused by a guard (BRICK_GUARD refusal): drop; strike only if validly-signed but single-class
RejectReq ==
  /\ pc = "BOOT" /\ journal = NOJ /\ req # NoReq
  /\ ~(Accepted(req) /\ Guards(req))
  /\ req' = NoReq
  /\ IF AnergyMode # "OFF" /\ Fresh(req) /\ HasValidSig(req) /\ Lacks2nd(req)
        THEN StrikeUpdate(req)
        ELSE UNCHANGED <<strikes, anergic>>
  /\ UNCHANGED <<floor, has, cls, journal, imgs, lkg, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

Proceed ==
  /\ pc = "BOOT" /\ journal = NOJ /\ req = NoReq
  /\ pc' = "VERIFY_B"
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, imgs, lkg, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

\* ---------- verify chain ----------
VerifyB ==
  /\ pc = "VERIFY_B"
  /\ IF Valid(imgs[1]) THEN pc' = "RUN" /\ run' = 1 ELSE pc' = "VERIFY_ALT" /\ run' = 0
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, imgs, lkg, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

VerifyAlt ==
  /\ pc = "VERIFY_ALT"
  /\ IF Valid(imgs[2]) THEN pc' = "RUN" /\ run' = 2
     ELSE IF Valid(lkg) THEN pc' = "LKG" /\ run' = 0
     ELSE pc' = "BRICK_GUARD" /\ run' = 0
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, imgs, lkg, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

\* ---------- image updates (A/B) and LKG commit, each two-step so a cut can tear them ----------
Other(k) == 3 - k
CanTear(k) == Valid(imgs[Other(k)]) \/ Valid(lkg)

UpdBegin(k) ==
  /\ pc \in {"RUN", "LKG", "BRICK_GUARD"} /\ run # k
  /\ (pc = "BRICK_GUARD" \/ CanTear(k))
  /\ imgs' = [imgs EXCEPT ![k] = [st |-> "TORN", sg |-> imgs[k].sg, gn |-> imgs[k].gn]]
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, lkg, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

UpdEnd(k) ==
  /\ pc \in {"RUN", "LKG", "BRICK_GUARD"} /\ imgs[k].st = "TORN"
  /\ \E s \in Slots, g \in Gens : KeyValid(s, g) /\ imgs' = [imgs EXCEPT ![k] = GoodImg(s, g)]
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, lkg, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

LkgBegin ==
  /\ pc = "RUN" /\ Valid(imgs[run])
  /\ lkg' = [st |-> "TORN", sg |-> lkg.sg, gn |-> lkg.gn]
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, imgs, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

LkgEnd ==
  /\ pc = "RUN" /\ lkg.st = "TORN" /\ Valid(imgs[run])
  /\ lkg' = imgs[run]
  /\ UNCHANGED <<floor, has, cls, strikes, anergic, journal, req, imgs, pc, run, nreq, fa, fk, histAdv, histRev, histRepl, histNoHolder>>

Next ==
  \/ HonestDeposit \/ AttackDeposit \/ PowerCut
  \/ Burn \/ ClearJ \/ ApplyReq \/ RejectReq \/ Proceed
  \/ VerifyB \/ VerifyAlt
  \/ \E k \in 1..2 : UpdBegin(k) \/ UpdEnd(k)
  \/ LkgBegin \/ LkgEnd

Spec == Init /\ [][Next]_vars

\* ---------- invariants ----------
TypeOK == floor \in Gens /\ journal \in Gens \cup {NOJ} /\ pc \in {"BOOT","VERIFY_B","VERIFY_ALT","RUN","LKG","BRICK_GUARD"}
Inv_NoSingleAssumptionAdvance == ~histAdv
Inv_NoSingleAssumptionReplace == ~histRepl
Inv_Bootable == BootableAt(floor, has, imgs, lkg) /\ pc # "BRICK_GUARD"
Inv_PAM == ~histRev
\* REQ-LIFE-02: slot 3's key is never replaced while active without slot 3's own valid signature
Inv_HolderConsent == ~histNoHolder
Inv_SlotCapability == CapAt(floor, has, cls)
Inv_JournalSane == journal = NOJ \/ journal = floor \/ journal = floor + 1

AuthPossible == AuthPossibleS(anergic)
Inv_NoAnergyLockout == CapAt(floor, has, cls) => AuthPossible

\* witnesses (vacuity checks): these are EXPECTED to be violated, proving the behaviours are reachable
Inv_NeverAdv == floor < 2
Inv_NeverRepl == ~(cls[3][floor] # {"LATTICE","KECCAK"})
Inv_NeverRevoke == ~(\E s \in Slots, g \in Gens : ~has[s][g] /\ ~(s = 2 /\ g = MaxF))
Inv_NeverLKG == pc # "LKG"
Inv_NeverBrick == pc # "BRICK_GUARD"

FloorMonotone == [][floor' >= floor]_vars
=============================================================================

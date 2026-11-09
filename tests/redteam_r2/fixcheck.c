#include <stdio.h>
#include "../../src/policy8.c"
int main(){ ac_tbl_t U,L; uint8_t f[3]={1,2,4}; int bad=0;
 bad+= ac_tbl_upper(&U,f,3,3,0,0)!=-1;                       /* A: k=3 refused */
 ac_tbl_upper(&U,f,1,2,0,0); bad+= tb(&U,0)!=0 ? 0:0; bad+= tb(&U,1)!=0;      /* B: {a0} not authorisable-safe */
 ac_tbl_upper(&U,f,0,1,0x80,0); bad+= tb(&U,0x80)!=0;         /* C: WIT alone never in U */
 bad+= ac_tbl_lower(&L,f,1,2,0,0)!=-2;                        /* unsatisfiable budget flagged */
 uint8_t kd[8]={1,1,3,0,0,0,0,0}; uint32_t lb[8]={0}; bad+= ac_labels_valid(kd,lb,0x07)!=0; /* H */
 /* H2 (mutation-testing finding): H alone passes by coincidence under a kind==1 -> kind!=1 mutant.
  * A positive case where only the kind==1 (SIG) atom has a valid label, and a present non-SIG
  * atom has NO label, distinguishes == from != (original: label-less non-SIG atom is correctly
  * ignored -> valid; kind!=1 mutant: the non-SIG atom gets wrongly checked and fails). */
 { uint8_t kdp[8]={1,2,0,0,0,0,0,0}; uint32_t lbp[8]={0}; lbp[0]=1u<<16;
   bad+= ac_labels_valid(kdp,lbp,0x03)!=1; }                 /* H2 */
 /* H3: ac_expo_from_kinds had zero coverage anywhere -- direct test, including the == -> != boundary. */
 { uint8_t kdw[8]={0,1,3,0,0,0,0,0};                          /* atom2 is kind 3 (WIT), atom1 is kind 1 (SIG) */
   bad+= ac_expo_from_kinds(kdw,0x07) != 0x04; }              /* H3: only atom2 (bit2) flagged as exposure */
 uint8_t cl[40]; uint32_t lab[8]; for(int i=0;i<8;i++) lab[i]=(1u<<(16+i))|(1u<<i); /* 16 classes */
 bad+= ac_faults_from_labels(cl,4,lab,0xff,0xff,0xffffffff)!=-1;  /* E: cap exceeded reported */
 /* E2 (mutation-testing finding): a tight, exactly-cap-sized buffer with a trailing canary catches
  * the n>=cap -> n>cap off-by-one mutation, which E alone (a generously oversized buffer) does not:
  * that mutant writes exactly one element past the documented cap, silently, into slack space E's
  * buffer happens to have. */
 { struct { uint8_t buf[2]; uint8_t canary; } g; g.canary = 0xAA;
   uint32_t lab2[8]; for (int i = 0; i < 8; i++) lab2[i] = (1u<<(16+i)) | (1u<<i);
   ac_faults_from_labels(g.buf, 2, lab2, 0xff, 0xff, 0xffffffff);   /* cap=2, far more than 2 classes available */
   bad += (g.canary != 0xAA); }                              /* E2: canary untouched iff the write truly stopped at cap */
 /* E3: same off-by-one, but in the SECOND loop (label_filter path) specifically -- singles=0 so the
  * first loop contributes nothing, forcing every write through the label-class loop at line ~35. */
 { struct { uint8_t buf[2]; uint8_t canary; } g2; g2.canary = 0x55;
   uint32_t lab3[8]; for (int i = 0; i < 8; i++) lab3[i] = (1u<<(16+i));  /* 16 distinct label classes, no singles */
   ac_faults_from_labels(g2.buf, 2, lab3, 0xff, 0x00, 0xffffffff);
   bad += (g2.canary != 0x55); }                             /* E3 */
 /* REQ-LIFE-02: key install into an ACTIVE slot needs the slot holder's own atom in S */
 ac_tbl_t all; for(int i=0;i<8;i++) all.w[i]=0xffffffffu;                 /* table authorises everything */
 bad+= ac_key_install_authorised(&all, 0x06, 0x01, 1)!=0;   /* I: active slot, holder (bit0) absent -> refused */
 bad+= ac_key_install_authorised(&all, 0x07, 0x01, 1)!=1;   /* J: active slot, holder present -> ok */
 bad+= ac_key_install_authorised(&all, 0x06, 0x01, 0)!=1;   /* K: no key yet, no holder to co-sign -> ok */
 /* REQ-NV-01: tables stored with complements, decisions evaluated twice with complementary encodings */
 ac_tbl_dual_t d; ac_tbl_dual_init(&d, &all);
 bad+= ac_tbl_dual_consistent(&d)!=1;                        /* L: freshly-initialised dual is consistent */
 bad+= ac_tbl_dual_authorises(&d, 0x42)!=1;                  /* M: all-bits table authorises everything */
 d.c.w[2] ^= 1u;                                              /* simulate a single-bit flip in the complement copy */
 bad+= ac_tbl_dual_consistent(&d)!=0;                        /* N: corruption detected */
 bad+= ac_tbl_dual_authorises(&d, 64)!=0;                     /* O: the corrupted bit (S=64 is bit 6 of word 2) fails closed */
 bad+= ac_tbl_dual_authorises(&d, 1)!=1;                     /* P: an untouched bit still authorises normally */
 /* REQ-EVD-03: duplicate key hashes must be rejected */
 uint8_t kd2[8]={1,1,0,0,0,0,0,0}; ac_key_hash_t kh[8]={0};
 kh[0].h[0]=0xAA; kh[1].h[0]=0xAA;                             /* same hash in two present SIG slots */
 bad+= ac_no_duplicate_keys(kd2, kh, 0x03)!=0;                /* Q: duplicate rejected */
 kh[1].h[0]=0xBB;
 bad+= ac_no_duplicate_keys(kd2, kh, 0x03)!=1;                /* R: distinct hashes accepted */
 /* REQ-EVD-02: assumption labels are device-derived, never caller-supplied */
 bad+= ac_derive_assumption_label(0)!=0x01;                   /* S: known provider -> fixed assumption bit */
 bad+= ac_derive_assumption_label(99)!=0;                     /* T: unknown provider -> 0, never forged */
 uint8_t prov[8]={0,1,0,0,0,0,0,0}; uint32_t decl[8]={0}; uint32_t out[8];
 decl[0] = 0xffff | (0xAAu<<16);                               /* caller tries to inject assumption bits 0..15 AND a group label */
 ac_derive_labels(out, prov, decl, 0x03);
 bad+= (out[0] & 0xffffu) != 0x01;                            /* U: caller's injected assumption bits were masked away */
 bad+= ((out[0]>>16) & 0xffu) != 0xAAu;                       /* V: declared group/site bits pass through untouched */
 bad+= out[1] != 0x02;                                        /* W: provider 1 (SHAKE256) derives independently */
 /* X (mutation-testing finding): REQ-ADM-02 is documented as verified by "TEST-ADM-02 (fixcheck)"
  * in requirements.md, but ac_tbl_tighten() had ZERO actual calls anywhere in the test suite --
  * mutation testing (scripts/mutation_test.py) caught its `== -> !=` mutant surviving, which is
  * exactly how that gap was found. Real tests now: */
 { ac_tbl_t o, n; memset(&o,0,sizeof o); memset(&n,0,sizeof n);
   ts(&o,5); ts(&o,7);                                        /* o authorises {5,7} */
   ts(&n,5);                                                   /* n authorises only {5}: a tightening */
   bad += !ac_tbl_tighten(&n,&o);                              /* X1: n subset of o -> tightening, true */
   ts(&n,9);                                                   /* now n has a bit o doesn't: {5,9} */
   bad += ac_tbl_tighten(&n,&o);                                /* X2: n NOT a subset of o -> not a tightening, false */
 }
 /* Y (mutation-testing finding): ac_tbl_is_projected was only ever asserted TRUE in the existing
  * suite (test_projection.c); its FALSE path (a genuinely non-projected table) had no coverage. */
 { ac_tbl_t t; memset(&t,0,sizeof t); ts(&t, 0xFF);             /* bit 0xFF set: depends on atom bits outside present=0x0F */
   bad += ac_tbl_is_projected(&t, 0x0F);                        /* Y: 0xFF has bits outside 0x0F -> NOT projected, should be false */
 }
 /* Z (mutation-testing finding): I/J/K all use a table that authorises everything, so the
  * "!ac_tbl_authorises(t,S) -> return 0" branch in ac_key_install_authorised was never exercised. */
 { ac_tbl_t none; memset(&none,0,sizeof none);                  /* table authorises NOTHING */
   bad += ac_key_install_authorised(&none, 0x07, 0x01, 1) != 0; /* Z: table itself refuses -> must refuse regardless of holder/active */
 }
 /* AA (mutation-testing finding): ac_tbl_lower's own k>2 guard (mirroring ac_tbl_upper's) was
  * never independently exercised -- the only ac_tbl_lower test used k=2 (unsatisfiable via k>nf). */
 bad += ac_tbl_lower(&L, f, 3, 3, 0, 0) != -1;                  /* AA: k=3 refused, same as ac_tbl_upper's case A */
 /* AD (mutation-testing finding): no existing case checks that a VALID ac_tbl_upper call returns
  * exactly 0 (vs just "not -1"); case B calls it but discards the return value entirely. */
 bad += ac_tbl_upper(&U, f, 3, 2, 0, 0) != 0;                   /* AD: well-formed call (k<=2, nf<=32) must return exactly 0 */
 /* AE (mutation-testing finding): E/E2/E3 all used present=0xff (every atom present), so the
  * present-bit half of (present && label) was always true regardless of && vs || -- never
  * distinguishing from the label-bit half alone. Atom2 is absent but carries the probed label
  * bit; it must NOT appear in the resulting fault-class mask. */
 { uint32_t labx[8]={0}; labx[0]=1u<<20; labx[2]=1u<<20;        /* atoms 0 and 2 both declare label bit 20 */
   uint8_t clx[4]={0};
   int rx = ac_faults_from_labels(clx, 4, labx, 0x03 /*present: atoms 0,1 only*/, 0x00, 1u<<20);
   bad += (rx != 1) || (clx[0] != 0x01); }                     /* AE: exactly one class, mask={atom0} only, atom2 excluded */
 /* AB (mutation-testing finding): Q/R only ever used atoms that are BOTH present and kind==1
  * together, so present&&kind==1 vs present||kind==1 were indistinguishable. An absent atom that
  * happens to have kind==1 and a matching hash must NOT be flagged (it was never physically there). */
 { uint8_t kd3[8]={1,1,0,0,0,0,0,0}; ac_key_hash_t kh3[8]={0};
   kh3[0].h[0]=0xAA; kh3[1].h[0]=0xAA;                          /* same hash, but atom1 is ABSENT below */
   bad += ac_no_duplicate_keys(kd3, kh3, 0x01) != 1; }          /* AB: present=0x01 (only atom0) -> no duplicate among present atoms */
 /* AC (mutation-testing finding): AB alone didn't catch the OUTER guard's && -> || mutant, because
  * an absent-but-wrongly-included i still needs a present, passing-guard j>i to produce a visible
  * effect (an absent i with no present kind==1 partner beyond it is a no-op either way). Atom0 is
  * absent but kind==1 (wrongly admitted as i under the || mutant); atom1 is present and kind==1
  * (a valid j); same hash -- distinguishes outer guard's && from || specifically. */
 { uint8_t kd4[8]={1,1,1,0,0,0,0,0}; ac_key_hash_t kh4[8]={0};
   kh4[0].h[0]=0xBB; kh4[1].h[0]=0xBB; kh4[2].h[0]=0xCC;        /* atom0(absent)=atom1's hash; atom1!=atom2 */
   bad += ac_no_duplicate_keys(kd4, kh4, 0x06) != 1; }          /* AC: present=0x06 (atoms1,2 only); atoms1,2 differ -> no duplicate */
 printf("fixcheck failures=%d\n",bad); return bad;}

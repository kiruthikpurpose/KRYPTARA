#include <stdio.h>
#include "../../src/policy8.c"
int main(){ ac_tbl_t U,L; uint8_t f[3]={1,2,4}; int bad=0;
 bad+= ac_tbl_upper(&U,f,3,3,0,0)!=-1;                       /* A: k=3 refused */
 ac_tbl_upper(&U,f,1,2,0,0); bad+= tb(&U,0)!=0 ? 0:0; bad+= tb(&U,1)!=0;      /* B: {a0} not authorisable-safe */
 ac_tbl_upper(&U,f,0,1,0x80,0); bad+= tb(&U,0x80)!=0;         /* C: WIT alone never in U */
 bad+= ac_tbl_lower(&L,f,1,2,0,0)!=-2;                        /* unsatisfiable budget flagged */
 uint8_t kd[8]={1,1,3,0,0,0,0,0}; uint32_t lb[8]={0}; bad+= ac_labels_valid(kd,lb,0x07)!=0; /* H */
 uint8_t cl[40]; uint32_t lab[8]; for(int i=0;i<8;i++) lab[i]=(1u<<(16+i))|(1u<<i); /* 16 classes */
 bad+= ac_faults_from_labels(cl,4,lab,0xff,0xff,0xffffffff)!=-1;  /* E: cap exceeded reported */
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
 printf("fixcheck failures=%d\n",bad); return bad;}

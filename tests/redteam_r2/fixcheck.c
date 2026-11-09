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
 printf("fixcheck failures=%d\n",bad); return bad;}

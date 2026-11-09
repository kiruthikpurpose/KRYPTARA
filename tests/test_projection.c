/* TEST-ADM-05: projection is idempotent, monotone-preserving, and yields f'(S)=f(S&present). */
#include <stdio.h>
#include <stdlib.h>
#include "../src/policy8.c"
int main(void){ srand(5); int bad=0;
  for(int it=0; it<20000; it++){
    ac_tbl_t t, p, q; uint8_t present=(uint8_t)rand();
    /* random monotone table: up-closure of random seeds */
    memset(&t,0,sizeof t); unsigned ns=1+rand()%5; uint8_t seed[5]; for(unsigned i=0;i<ns;i++) seed[i]=(uint8_t)rand();
    for(unsigned m=0;m<256;m++) for(unsigned i=0;i<ns;i++) if((seed[i]&~m&0xff)==0){ts(&t,m);break;}
    ac_tbl_project(&p,&t,present); ac_tbl_project(&q,&p,present);
    bad += memcmp(&p,&q,sizeof p)!=0;
    bad += !ac_tbl_is_projected(&p,present);
    bad += !ac_tbl_monotone(&p);
    for(unsigned m=0;m<256;m++) bad += tb(&p,m)!=tb(&t,m&present);
  }
  printf("projection test failures=%d\n",bad); return bad!=0; }

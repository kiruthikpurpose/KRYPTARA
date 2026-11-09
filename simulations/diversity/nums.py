import math
# --- LMS/HSS sizes (RFC 8554 structure) ---
p={ (32,1):265,(32,2):133,(32,4):67,(32,8):34 }  # RFC 8554 p for n=32 (also needed for n=24: p differs)
def lmots_p(n,w):
    # RFC 8554 Appendix B: u=ceil(8n/w); v=ceil((floor(lg((2^w-1)*u))+1)/w); ls=16-v*w; p=u+v
    u=math.ceil(8*n/w); v=math.ceil((math.floor(math.log2((2**w-1)*u))+1)/w); return u+v
def lms_sig(n,w,h):
    P=lmots_p(n,w); ots=4+n+P*n; return 4+ots+4+h*n
def lms_pk(n): return 4+4+16+n
print("p values n=32:",{w:lmots_p(32,w) for w in (1,2,4,8)})
print("LMS sig bytes n=32:",{(w,h):lms_sig(32,w,h) for w in (4,8) for h in (10,15,20,25)})
print("LMS sig bytes n=24:",{(w,h):lms_sig(24,w,h) for w in (4,8) for h in (10,15,20)})
def hss_sig(n,w,levels):
    return 4+(levels-1)*(lms_sig(n,w,10)+lms_pk(n))+lms_sig(n,w,10)
print("HSS L=2 H10/10 W4 N32:",hss_sig(32,4,2))
# keygen cost: per leaf OTS pk = p chains * (2^w-1) hashes + leaf hash; tree interior ~ 2^h
for (w,h) in [(4,10),(4,15),(4,20),(8,15),(8,20)]:
    P=lmots_p(32,w); per=P*(2**w-1)+P+2  # chain steps + pk-compress ; rough
    tot=per*2**h+2**h
    print(f"keygen hashes W{w} H{h}: {tot:.3e}  time @1e6 H/s={tot/1e6:.0f}s  @2e7 H/s={tot/2e7:.0f}s")
# --- cycles to ms ---
cyc={'ML-KEM-768 decaps m4fstack':714194,'ML-KEM-768 decaps m4fspeed':707827,'ML-KEM-768 keygen m4fspeed':642096,'ML-KEM-768 encaps m4fspeed':658754,
 'ML-DSA-65 verify m4f':2415944,'ML-DSA-65 sign m4f (avg)':6193171,'ML-DSA-65 verify m4fstack':5732397,'ML-DSA-65 sign m4fstack(avg)':24421526,
 'SLH-DSA-SHA2-128f verify clean':21923628,'SLH-DSA-SHA2-128f sign clean':368575228}
for k,v in cyc.items(): print(f"{k:34s} {v:>12,d} cyc  @64MHz {v/64e6*1e3:9.1f} ms  @120MHz {v/120e6*1e3:9.1f} ms")
print("verify-after-sign overhead ML-DSA-65 m4f:",2415944/6193171)
# --- bundle sizes ---
sz={'ML-DSA-65':(1952,3309),'ML-DSA-87':(2592,4627),'ML-DSA-44':(1312,2420),'LMS-SHA256-W4-H10':(56,lms_sig(32,4,10)),'LMS-SHA256-W8-H15':(56,lms_sig(32,8,15)),
 'SLH-128s':(32,7856),'SLH-800-230-128-24':(32,3856),'SLH-800-230-192-24':(48,7752),'SLH-128f':(32,17088),'FN-DSA-512':(897,666),'Ed25519':(32,64),'ECDSA-P256':(64,64)}
def tot(*n): return sum(sz[x][1] for x in n)
print("dual-class sig ML-DSA-65+LMS W4H10:",tot('ML-DSA-65','LMS-SHA256-W4-H10'))
print("dual-class ML-DSA-65+SLH-128s:",tot('ML-DSA-65','SLH-128s'))
print("dual LMS W4H10 + SLH 800-230 128-24:",tot('LMS-SHA256-W4-H10','SLH-800-230-128-24'))
print("composite ML-DSA-65+Ed25519 sig/pk:",3309+64,1952+32)
print("CNSA-profile ML-DSA-87+LMS W4 H10 sigs:",tot('ML-DSA-87','LMS-SHA256-W4-H10'))
print("3-class quorum ML-DSA-65+LMS+SLH128s:",tot('ML-DSA-65','LMS-SHA256-W4-H10','SLH-128s'))
# KEM enrolment
mlkem={'512':(800,768),'768':(1184,1088),'1024':(1568,1568)}
print("ML-KEM-768 enrol ek+ct:",1184+1088, " X-Wing ek+ct:",1216+1120, " ML-KEM-1024:",1568+1568)
# --- counters ---
L40=40*365.25*86400
print("40y seconds",L40)
def wrap(bits,rate): return 2**bits/rate/86400
for name,rate in [('SV 4000 fps (80 smp/cyc@50Hz)',4000),('SV 4800 fps (80@60Hz)',4800),('GOOSE heartbeat 1/s',1),('GOOSE burst avg 100/s',100),('LoRa 1 per 10 s',0.1),('1 per ms',1000)]:
    need=2*rate*L40
    print(f"{name:34s} 32-bit wraps in {wrap(32,rate):12.1f} days ({wrap(32,rate)/365.25:9.2f} y); 40y count {rate*L40:.3e}=2^{math.log2(rate*L40):.1f}; need >= 2^{math.log2(need):.1f} for 2x")
    T=86400; print(f"      rekey 24h: msgs/key {rate*T:.3e}=2^{math.log2(rate*T):.1f}; 32-bit margin x{2**32/(rate*T):.1f}")
import datetime
base=datetime.date(2019,4,7); print("GPS 10-bit week rollover after 2019-04-07 +1024w:",base+datetime.timedelta(weeks=1024))
print("2^31 s after epoch:",datetime.datetime(1970,1,1)+datetime.timedelta(seconds=2**31)," 2^32:",datetime.datetime(1970,1,1)+datetime.timedelta(seconds=2**32))
# LMS leaf budgets
for h in (10,15,20,25):
    print(f"H{h}: {2**h:>10,d} leaves; at 12 releases/yr x40y x2 = {12*40*2}; at 4 sigs/day: {4*365*40*2}; years at 1 sig/day {2**h/365.25:.1f}")
# SP800-230 2^24 budget
print("2^24 =",2**24,"; at 1 sig/s lasts days:",2**24/86400)
# first stage flash
print("slots 3x32=",96,"4x32=",128)

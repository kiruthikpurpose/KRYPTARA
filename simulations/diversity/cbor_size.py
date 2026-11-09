def h(mt,n):
    if n<24: return bytes([mt<<5|n])
    if n<256: return bytes([mt<<5|24,n])
    if n<65536: return bytes([mt<<5|25])+n.to_bytes(2,'big')
    return bytes([mt<<5|26])+n.to_bytes(4,'big')
def enc(x):
    if isinstance(x,int): return h(0,x) if x>=0 else h(1,-1-x)
    if isinstance(x,bytes): return h(2,len(x))+x
    if isinstance(x,str): b=x.encode(); return h(3,len(b))+b
    if isinstance(x,list): return h(4,len(x))+b''.join(enc(i) for i in x)
    if isinstance(x,dict):
        items=sorted(((enc(k),enc(v)) for k,v in x.items()),key=lambda kv:kv[0])
        return h(5,len(items))+b''.join(k+v for k,v in items)
Z=lambda n:b'\0'*n
report={1:1,2:Z(16),3:Z(16),4:2,5:2,6:7,7:12,8:[[0,1,0,0,Z(32)],[1,2,1,0,Z(32)],[2,3,0,0,Z(32)]],
 9:Z(32),10:Z(32),11:Z(64),12:{1:Z(4) and 400,2:500,3:3},13:[[1,1024,37],[2,1000000,12]],14:11,15:0,16:[1,2]}
b=enc(report);print("state report payload bytes",len(b))
bundle={1:1,2:Z(16),3:1,4:{1:0b111100,2:[1,2,3],3:5},5:{1:7,2:11,3:Z(32)},6:{1:8,2:12,3:[[2,1,Z(48)]]},
 7:[{1:[Z(32),Z(32)],2:350000,3:"suit://fw"}],8:{1:402,2:20000,3:7,4:5},9:"Advance floor 7->8: retire OEM key class A after drill",10:0b0101}
print("bundle manifest bytes (no sigs)",len(enc(bundle)))

import urllib.request,sys
U="https://download.ifi.uzh.ch/rpg/RVT/datasets/preprocessed/gen4.tar"
T=190351165440
def get(a,n):
    r=urllib.request.Request(U,headers={"Range":f"bytes={a}-{a+n-1}"})
    return urllib.request.urlopen(r,timeout=60).read()
def first_hdr(off,win=8<<20):
    off-=off%512; b=get(off,win)
    for i in range(0,len(b)-512,512):
        h=b[i:i+512]
        if h[257:262]==b"ustar" and h[:5]==b"gen4/":
            return off+i,h[:100].split(b"\0")[0].decode(),int(h[124:135].strip(b"\0 ") or b"0",8)
for f in [0.5,0.7,0.8,0.85,0.9,0.95,0.99]:
    print(f,first_hdr(int(T*f)),flush=True)

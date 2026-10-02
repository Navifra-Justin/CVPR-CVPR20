import http.client,time,json
H="download.ifi.uzh.ch"; P="/rpg/RVT/datasets/preprocessed/gen4.tar"
T=190351165440
c=http.client.HTTPSConnection(H,timeout=60)
def get(a,n):
    global c
    for _ in range(6):
        try:
            c.request("GET",P,headers={"Range":f"bytes={a}-{a+n-1}"}); r=c.getresponse(); return r.read()
        except Exception:
            c=http.client.HTTPSConnection(H,timeout=60); time.sleep(1)
    raise RuntimeError
import os
rows=json.load(open('tar_index.json')) if os.path.exists('tar_index.json') else []
off=0
if rows:
    o,n,sz=rows[-1]; off=o+512+((sz+511)//512)*512
t0=time.time()
while off<T-1024:
    h=get(off,512)
    name=h[:100].split(b"\0")[0].decode()
    if not name: break
    size=int(h[124:135].strip(b"\0 ") or b"0",8)
    rows.append((off,name,size))
    off+=512+((size+511)//512)*512
    if len(rows)%50==0:
        print(len(rows),f"{off/T:.4f}",name[-70:],f"{time.time()-t0:.0f}s",flush=True)
        json.dump(rows,open("tar_index.json","w"))
json.dump(rows,open("tar_index.json","w"))
print("DONE",len(rows),time.time()-t0)

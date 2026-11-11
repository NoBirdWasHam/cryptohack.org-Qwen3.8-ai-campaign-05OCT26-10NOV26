#!/usr/bin/env python
# sigma-special-soundness (226): server reuses SAME r in two rounds.
# z1=r+e1*flag ; z2=r+e2*flag  =>  flag=(z1-z2)/(e1-e2) mod q
import socket, json, secrets, re
q=0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
s=socket.create_connection(("socket.cryptohack.org",13426),timeout=30); s.settimeout(25)
s.recv(65536)  # greeting
def next_obj():
    buf=b""
    for _ in range(600):
        brace=buf.find(b"{")
        if brace>=0:
            try:
                obj,idx=json.JSONDecoder().raw_decode(buf[brace:].decode()); return obj
            except json.JSONDecodeError: pass
        d=s.recv(65536)
        if not d: break
        buf+=d
    raise RuntimeError("no obj")
m=next_obj(); a=m["a"]; y=m["y"]; print("got a,y",flush=True)
e1=secrets.randbits(511); s.sendall((json.dumps({"e":e1})+"\n").encode())
z1=next_obj()["z"]; print("got z1",flush=True)
m2=next_obj(); a2=m2["a2"]; print("a2==a (reused r)?",a2==a,flush=True)
e2=secrets.randbits(511)
while e2==e1: e2=secrets.randbits(511)
s.sendall((json.dumps({"e":e2})+"\n").encode())
z2=next_obj()["z2"]; print("got z2",flush=True)
flag=((z1-z2)*pow((e1-e2)%q,-1,q))%q
raw=flag.to_bytes((flag.bit_length()+7)//8,"big")
mm=re.search(rb"crypto\{[^}]*\}",raw)
print("FLAG:", mm.group(0).decode() if mm else raw[:60],flush=True)
s.close()

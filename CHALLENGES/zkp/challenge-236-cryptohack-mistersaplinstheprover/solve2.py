#!/usr/bin/env python
# mistersaplinstheprover: leak n10 via negative index (node=-1); n11=H(l2||l3),
# l2=H(secret[16]||"crypto{") -> brute 256 values of secret[16], same connection.
import socket, json, hashlib, re, sys
H="socket.cryptohack.org"; P=13432
def h(b): return hashlib.sha256(b).digest()
def merge(a,b): return h(a+b)
def conn():
    s=socket.create_connection((H,P),timeout=30); s.settimeout(20)
    s.recv(65536)
    return s
def readline(s):
    buf=b""
    while b"\n" not in buf:
        d=s.recv(65536)
        if not d: raise RuntimeError("closed")
        buf+=d
    return json.loads(buf.split(b"\n")[0].decode())
def get_node(i):
    s=conn(); r=readline(s) if False else None
    s.sendall((json.dumps({"option":"get_node","node":i})+"\n").encode())
    r=readline(s); s.close()
    assert "msg" in r, (i,r)
    return bytes.fromhex(r["msg"])
# 1) stable leaves 3..7 (depend only on FLAG)
stable={}
for i in (3,4,5,6,7):
    stable[i]=get_node(i); print("leaf",i,stable[i].hex()[:16],"...",flush=True)
n12=merge(stable[4],stable[5]); n13=merge(stable[6],stable[7]); n21=merge(n12,n13)
l3=stable[3]
# 2) proof connection: leak n10, brute secret[16]
s=conn()
s.sendall((json.dumps({"option":"get_node","node":-1})+"\n").encode())
r=readline(s); assert "msg" in r, r
n10=bytes.fromhex(r["msg"]); print("n10:",n10.hex(),flush=True)
found=None
for b in range(256):
    l2=h(bytes([b])+b"crypto{")
    n11=merge(l2,l3); n20=merge(n10,n11); root=merge(n20,n21)
    s.sendall((json.dumps({"option":"do_proof","root":root.hex()})+"\n").encode())
    r=readline(s)
    if "msg" in r and r["msg"]!="you failed!":
        print("HIT b=",b,"resp:",r,flush=True); found=r["msg"]; break
    if "error" in r: print("err at",b,r,flush=True)
s.close()
if found:
    m=re.search(r"crypto\{[^}']*\}",found)
    flag=m.group(0) if m else found
    print("FLAG:",flag,flush=True)
    open("flag_mistersaplinstheprover.txt","w").write(flag+"\n")
else:
    print("NO HIT",flush=True); sys.exit(1)

#!/usr/bin/env python
# mistersaplinstheprover (236, zkp): datas = secret(17B)+FLAG(47B)=64B -> 8 leaves.
# get_node previews nodes[0][i] ONCE per connection (preview_used is per-instance,
# and each socket connection = a fresh Challenge). So 8 connections -> all 8 leaves ->
# compute the Merkle root locally -> do_proof.
import socket, json, hashlib, re
def h(b): return hashlib.sha256(b).digest()
def merge(a,b): return h(a+b)
PORT=13432
leaves=[]
for i in range(8):
    s=socket.create_connection(("socket.cryptohack.org",PORT),timeout=30); s.settimeout(20)
    s.recv(65536)
    def next_obj():
        buf=b""
        for _ in range(600):
            b=buf.find(b"{")
            if b>=0:
                try: obj,j=json.JSONDecoder().raw_decode(buf[b:].decode()); return obj
                except json.JSONDecodeError: pass
            d=s.recv(65536)
            if not d: break
            buf+=d
        raise RuntimeError("no obj")
    s.sendall((json.dumps({"option":"get_node","node":i})+"\n").encode())
    r=next_obj()
    assert "msg" in r, (i,r)
    leaves.append(bytes.fromhex(r["msg"]))
    print(f"leaf {i}: {r['msg'][:24]}...", flush=True)
    s.close()
# root = layer3: merge(merge(l0,l1), merge(merge(l2,l3), merge(merge(l4,l5), merge(l6,l7))))
l1=[merge(leaves[0],leaves[1]),merge(leaves[2],leaves[3]),merge(leaves[4],leaves[5]),merge(leaves[6],leaves[7])]
l2=[merge(l1[0],l1[1]),merge(l1[2],l1[3])]
root=merge(l2[0],l2[1])
print("root:",root.hex(),flush=True)
# do_proof on a fresh connection
s=socket.create_connection(("socket.cryptohack.org",PORT),timeout=30); s.settimeout(20)
s.recv(65536)
def next_obj():
    buf=b""
    for _ in range(600):
        b=buf.find(b"{")
        if b>=0:
            try: obj,j=json.JSONDecoder().raw_decode(buf[b:].decode()); return obj
            except json.JSONDecodeError: pass
        d=s.recv(65536)
        if not d: break
        buf+=d
    raise RuntimeError("no obj")
s.sendall((json.dumps({"option":"do_proof","root":root.hex()})+"\n").encode())
res=next_obj()
print("do_proof:",res,flush=True)
s.close()

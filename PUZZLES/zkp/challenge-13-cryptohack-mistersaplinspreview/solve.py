#!/usr/bin/env python
# mistersaplinspreview (232, zkp): Merkle-tree "saplin" proof.
# Server builds tree: layer0=8 leaves (sha256 of 8-byte chunks), l1=4, l2=2, l3=1 root.
# get_nodes: balance_check() spawns a THREAD (request_checker) and does NOT join it,
#   so challenge() reads self.balance_validated before the thread runs -> still None ->
#   `None != False` is True -> nodes returned FOR FREE (balance never actually deducted/checked).
# So: fetch the 4 layer-1 nodes for free, compute root locally, send to do_proof.
import socket, json, hashlib
def h(b): return hashlib.sha256(b).digest()
def merge(a,b): return h(a+b)
s=socket.create_connection(("socket.cryptohack.org",13414),timeout=30); s.settimeout(20)
s.recv(65536)
def next_obj():
    buf=b""
    for _ in range(600):
        b=buf.find(b"{")
        if b>=0:
            try: obj,i=json.JSONDecoder().raw_decode(buf[b:].decode()); return obj
            except json.JSONDecodeError: pass
        d=s.recv(65536)
        if not d: break
        buf+=d
    raise RuntimeError("no obj")
def send(obj): s.sendall((json.dumps(obj)+"\n").encode())
# The checker thread loops `min(count, 10**7)` times. Request a HUGE count so the
# thread spends ~1s in that loop, while the main thread hits the `if balance_validated
# != False` check (still None) almost instantly -> wins the race -> free nodes.
r=None
for attempt in range(5):
    send({"option":"get_nodes","nodes":"1,10000000"})
    r=next_obj()
    if "msg" in r: break
    print("retry", attempt, r, flush=True)
assert "msg" in r, r
# r['msg'] is a str() of nested list of hex strings -> parse via ast
import ast
nodes=ast.literal_eval(r["msg"])   # [[hex0,hex1,hex2,hex3]]
l1=[bytes.fromhex(x) for x in nodes[0]]
assert len(l1)==4, l1
root=merge(merge(l1[0],l1[1]), merge(l1[2],l1[3]))
print("root hex:", root.hex(), flush=True)
send({"option":"do_proof","root":root.hex()})
res=next_obj()
print("do_proof:", res, flush=True)
s.close()

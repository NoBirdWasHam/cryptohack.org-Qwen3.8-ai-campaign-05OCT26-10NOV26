#!/usr/bin/env python
# sigma-shvzk (227, zkp): server picks e first, I send (a,z).
# Check: g^z == a*y^e and a in <g>.  Back-solve a from chosen z: a = g^z * y^(-e).
import sys, secrets; sys.path.insert(0, r"~\Practice_runs\cryptohack_org")
from jsonconn import Conn
p=0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q=0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g=2
c=Conn("socket.cryptohack.org",13427)
m=c.recv_json(); e=m["e"]; y=m["y"]
print("e bits",e.bit_length())
z=secrets.randbelow(q)
a=(pow(g,z,p)*pow(y,-e,p))%p
assert pow(a,q,p)==1, "a not in subgroup"
c.send_json({"a":a,"z":z})
res=c.recv_json()
print("RESULT:",res)
c.close()

#!/usr/bin/env python
# sigma-nizk (228, zkp): Fiat-Shamir. Source gives w,y. Play protocol:
# a=g^r; e=sha512(str(a)) % 2^511 ; z=r+e*w mod q
import sys, secrets, hashlib; sys.path.insert(0, r"~\Practice_runs\cryptohack_org")
from jsonconn import Conn
p=0x1ed344181da88cae8dc37a08feae447ba3da7f788d271953299e5f093df7aaca987c9f653ed7e43bad576cc5d22290f61f32680736be4144642f8bea6f5bf55ef
q=0xf69a20c0ed4465746e1bd047f57223dd1ed3fbc46938ca994cf2f849efbd5654c3e4fb29f6bf21dd6abb662e911487b0f9934039b5f20a23217c5f537adfaaf7
g=2
w=0xdb968f9220c879b58b71c0b70d54ef73d31b1627868921dfc25f68b0b9495628b5a0ea35a80d6fd4f2f0e452116e125dc5e44508b1aaec89891dddf9a677ddc0
y=0x1a1b551084ac43cc3ae2de2f89c6598a081f220010180e07eb62d0dee9c7502c1401d903018d9d7b06bff2d395c46795aa7cd8765df5ebe7414b072c8289170f0
assert pow(g,w,p)==y
c=Conn("socket.cryptohack.org",13428)
m=c.recv_json(); y2=m["y"]
assert y2==y
r=secrets.randbelow(q)
a=pow(g,r,p)
e=int.from_bytes(hashlib.sha512(str(a).encode()).digest(),"big")%(2**511)
z=(r+e*w)%q
assert pow(g,z,p)==(a*pow(y,e,p))%p
c.send_json({"a":a,"z":z})
res=c.recv_json()
print("RESULT:",res)
c.close()

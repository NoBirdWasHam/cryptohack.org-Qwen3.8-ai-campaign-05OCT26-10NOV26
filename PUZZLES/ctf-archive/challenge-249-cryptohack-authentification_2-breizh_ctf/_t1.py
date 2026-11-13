import time, secrets, sys
t0=time.time
import solve2 as S
from crypto import build_token, verif_token
key = secrets.token_bytes(16)
tok = build_token(key, S.USER, "guest")
C = bytes.fromhex(tok.split(";")[0]); T = bytes.fromhex(tok.split(";")[1])
ks = bytes(a^b for a,b in zip(S.TOKEN_PT, C)); E = ks[:16]
Sobs = int.from_bytes(bytes(t^e for t,e in zip(T,E)),"big")
buf = S.tag_buf(C)
blocks = [int.from_bytes(buf[i:i+16],"big") for i in range(0,len(buf),16)]
f = S.ptrim([Sobs]+blocks)
print("deg f", S.pdeg(f), "t", t0()); sys.stdout.flush()
F=[0,1]
for i in range(128):
    F = S.pmod(S.pmul(F,F), f)
print("frobenius done", t0()); sys.stdout.flush()
z=[0,1]; fz=S.pmod(z,f)
n=max(len(F),len(fz))
h=[(F+[0]*n)[i]^(fz+[0]*n)[i] for i in range(n)]
g = S.pgcd(f, S.ptrim(h))
print("gcd deg", S.pdeg(g), "t", t0()); sys.stdout.flush()
roots = S.split_roots(g)
print("roots", len(roots), "t", t0()); sys.stdout.flush()

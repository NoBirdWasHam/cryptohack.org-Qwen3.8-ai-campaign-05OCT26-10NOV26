import time, secrets
import solve2 as S
from crypto import build_token
key = secrets.token_bytes(16)
tok = build_token(key, S.USER, "guest")
C = bytes.fromhex(tok.split(";")[0]); T = bytes.fromhex(tok.split(";")[1])
ks = bytes(a^b for a,b in zip(S.TOKEN_PT, C)); E = ks[:16]
Sobs = int.from_bytes(bytes(t^e for t,e in zip(T,E)),"big")
buf = S.tag_buf(C)
blocks = [int.from_bytes(buf[i:i+16],"big") for i in range(0,len(buf),16)]
f = S.ptrim([Sobs]+blocks[::-1])
F=[0,1]
for i in range(128): F = S.pmod(S.pmul(F,F), f)
fz = S.pmod([0,1], f)
n = max(len(F),len(fz))
h = [(F+[0]*n)[i]^(fz+[0]*n)[i] for i in range(n)]
g = S.pgcd(f, S.ptrim(h))
print("g deg", S.pdeg(g), flush=True)
t=time.time()
s = 12345
A = S.phpow([s,1], S.Q//3, g)
print("phpow", (time.time()-t)*1e3,"ms deg", S.pdeg(A), flush=True)
p1 = S.pgcd(g, S.ptrim([A[0]^S.ID]+A[1:]))
print("p1 deg", S.pdeg(p1), flush=True)
a2 = S.ptrim(S.pmod(S.ptrim(S.pmul(A,A)+A+[S.ID]), g))
p2 = S.pgcd(g, a2)
print("p2 deg", S.pdeg(p2), flush=True)

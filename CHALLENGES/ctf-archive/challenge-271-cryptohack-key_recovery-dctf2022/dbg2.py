import os
import solve3 as s
K = os.urandom(16)
k0,k1,k2,k3 = s.key_schedule(K)
i = 4
pts = [bytes([a if j==i else 0 for j in range(16)]) for a in range(256)]
cts = [s.enc(K,p) for p in pts]
u0 = [bytes(s.S_box[a]^k for a,k in zip(p,k0)) for p in pts]   # sub THEN xor
z1 = [s.per(u) for u in u0]
u1 = [bytes(s.S_box[a]^k for a,k in zip(z,k1)) for z in z1]
z2 = [s.per(u) for u in u1]
u2 = [bytes(s.S_box[a]^k for a,k in zip(z,k2)) for z in z2]
z3 = [s.per(u) for u in u2]
ct_check = [bytes(s.S_box[a]^k for a,k in zip(z,k3)) for z in z3]
print("check", ct_check[0] == cts[0], ct_check[7] == cts[7])
def rep(nm, L):
    for b in range(16):
        vs = {x[b] for x in L}
        if len(vs) > 1:
            hi = len({v>>4 for v in vs}); lo = len({v&15 for v in vs})
            print(nm, "b%02d" % b, "size", len(vs), "hi", hi, "lo", lo)
for nm, L in [("z1",z1),("z2",z2),("z3",z3),("ct",cts)]:
    rep(nm, L)

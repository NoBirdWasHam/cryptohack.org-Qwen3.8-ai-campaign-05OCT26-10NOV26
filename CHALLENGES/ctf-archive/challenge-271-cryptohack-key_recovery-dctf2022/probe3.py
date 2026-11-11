import os
import solve3 as s
K = os.urandom(16)
k0,k1,k2,k3 = s.key_schedule(K)
print("k3", k3.hex())
i = 4
pts = [bytes([a if j==i else 0 for j in range(16)]) for a in range(256)]
cts = [s.enc(K,p) for p in pts]
# correct structure: ct = S(z3) ^ k3  ->  z3 = S[ct ^ k3]
def confined(vals):
    return len({v>>4 for v in vals})==1 or len({v&15 for v in vals})==1
z3s = [bytes(s.S_box[c ^ k] for c,k in zip(ct,k3)) for ct in cts]
act = sorted({b for b in range(16) if len({z[b] for z in z3s})>1})
print("active z3:", act)
for b in act:
    vs = {z[b] for z in z3s}
    print(" b",b,"size",len(vs),"hi",len({v>>4 for v in vs}),"lo",len({v&15 for v in vs}))
# k3 byte guess test: candidate z3_b = S[ct_b ^ g]; predicate confined + size>=3
for b in act:
    cands = []
    for g in range(256):
        vals = set()
        good = True
        for ct in cts:
            vals.add(s.S_box[ct[b]^g])
            if len(vals)>=3 and not confined(vals): good=False; break
        if good and len(vals)>=3: cands.append(g)
    print(" b",b,"k3 true",k3[b],"ncand",len(cands),cands[:20])

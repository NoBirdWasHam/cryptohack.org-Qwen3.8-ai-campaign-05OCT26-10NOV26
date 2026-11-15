src = open("13406_provided.py").read()
ns = {}
exec(src[src.index("class AES"):src.index("class Challenge")], ns)
AES = ns["AES"]
import json, random
M = json.load(open("M_matrix.json"))["M"]
N=128
def Mx(x):
    y=0
    for i in range(N):
        if x>>i&1: y^=M[i]
    return y
def ti(b): return int.from_bytes(b,"little")
def tb_(x): return x.to_bytes(16,"little")
key = bytes(range(16))
a = AES(key)
D = ti(a.encrypt(bytes(16)))
# find a failing P
random.seed(9)
for t in range(3):
    P = bytes(random.randrange(256) for _ in range(16))
    Ep = ti(a.encrypt(P))
    Lp = Ep ^ D
    print("P=",P.hex())
    print("  E(P)^E(0) =", Lp.to_bytes(16,"little").hex())
    print("  Mx(P)     =", Mx(ti(P)).to_bytes(16,"little").hex())
    print("  match:", Mx(ti(P))==Lp)
    if Mx(ti(P))==Lp:
        break
# Test: is Mx(e_j) == E(e_j)^E(0) for all j?  (should be, by construction)
bad=[j for j in range(N) if Mx(1<<j) != (ti(a.encrypt(bytes([0]*16)) ) ) ]
# recompute properly
E0 = ti(a.encrypt(bytes(16)))
badcols=[j for j in range(N) if Mx(1<<j) != (ti(a.encrypt(bytes([1<<(j%8)]*1 if False else ([0]*16 if False else list(bytes(16))))))) ]
# simpler: build e_j
def e_j(j):
    b=bytearray(16); b[j//8]=1<<(j%8); return bytes(b)
bad=[j for j in range(N) if Mx(1<<j) != (ti(a.encrypt(e_j(j))) ^ E0)]
print("columns j where Mx(e_j) != E(e_j)^E0:", bad[:10], "count", len(bad))

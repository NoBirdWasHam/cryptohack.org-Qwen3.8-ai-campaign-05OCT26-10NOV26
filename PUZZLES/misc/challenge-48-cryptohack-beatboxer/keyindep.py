src = open("13406_provided.py").read()
ns = {}
exec(src[src.index("class AES"):src.index("class Challenge")], ns)
AES = ns["AES"]
import json
N=128
def ti(b): return int.from_bytes(b,"little")
def tb_(x): return x.to_bytes(16,"little")
def e_j(j):
    b=bytearray(16); b[j//8]=1<<(j%8); return bytes(b)

# Build M fresh with zero key (columns), correct application
a0 = AES(bytes(16))
E0 = ti(a0.encrypt(bytes(16)))
cols = [ti(a0.encrypt(e_j(j))) ^ E0 for j in range(N)]
def Mx(x):
    y=0
    for j in range(N):
        if x>>j&1: y^=cols[j]
    return y

P = bytes([0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff,0x00])
print("zero key:  E(P)^E0 =", (ti(a0.encrypt(P))^E0).to_bytes(16,"little").hex())
print("zero key:  Mx(P)   =", Mx(ti(P)).to_bytes(16,"little").hex())
print("match zero:", (ti(a0.encrypt(P))^E0)==Mx(ti(P)))

# KEY-INDEPENDENCE: does E_key(P)^E_key(0) == Mx(P) for a DIFFERENT key?
import random
random.seed(3)
key2 = bytes(random.randrange(256) for _ in range(16))
a2 = AES(key2)
E02 = ti(a2.encrypt(bytes(16)))
print("\nkey2:  E(P)^E0 =", (ti(a2.encrypt(P))^E02).to_bytes(16,"little").hex())
print("key2:  Mx(P)   =", Mx(ti(P)).to_bytes(16,"little").hex())
print("match key2 (key-independence):", (ti(a2.encrypt(P))^E02)==Mx(ti(P)))

# Also test M.e_j consistency across keys for a few j
print("\ncolumn e_0: zero=%s key2=%s" % (cols[0].to_bytes(16,"little").hex(), (ti(a2.encrypt(e_j(0)))^E02).to_bytes(16,"little").hex()))
print("same:", cols[0]==(ti(a2.encrypt(e_j(0)))^E02))

src = open("13406_provided.py").read()
ns = {}
exec(src[src.index("class AES"):src.index("class Challenge")], ns)
AES = ns["AES"]
import random
def bx(a,b): return bytes(x^y for x,y in zip(a,b))
random.seed(7)
for trial in range(5):
    key = bytes(random.randrange(256) for _ in range(16))
    a = AES(key)
    def E(p): return a.encrypt(p)
    z = bytes(16)
    Ez = E(z)
    ok = True
    for _ in range(30):
        x = bytes(random.randrange(256) for _ in range(16))
        y = bytes(random.randrange(256) for _ in range(16))
        if E(x ^ y if False else bx(x,y)) != bx(bx(E(x),E(y)),Ez):
            ok = False; break
    print("trial", trial, "affine E(x^y)==E(x)^E(y)^E(0):", ok)
tb = list(AES.sbox)
def gmul(a,b):
    p=0
    for _ in range(8):
        if b&1: p^=a
        hi=a&0x80; a=(a<<1)&0xff
        if hi: a^=0x1b
        b>>=1
    return p
print("sbox == (42*x ^ 42):", all(tb[x]==gmul(42,x)^42 for x in range(256)))
# now confirm: with M from M_matrix.json, E(P) == M.P ^ D for a couple random keys
import json
M = json.load(open("M_matrix.json"))["M"]
N=128
def Mx(x):
    y=0
    for i in range(N):
        if x>>i&1: y^=M[i]
    return y
def ti(b): return int.from_bytes(b,"little")
def tb_(x): return x.to_bytes(16,"little")
random.seed(9)
for trial in range(3):
    key = bytes(random.randrange(256) for _ in range(16))
    a = AES(key)
    D = ti(a.encrypt(bytes(16)))
    ok = True
    for _ in range(20):
        P = bytes(random.randrange(256) for _ in range(16))
        if a.encrypt(P) != tb_(Mx(ti(P)) ^ D):
            ok = False; break
    print("trial", trial, "E(P)==M.P^D (M from file):", ok)

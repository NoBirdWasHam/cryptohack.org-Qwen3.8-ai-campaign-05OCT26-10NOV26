# tg10: real instances. parity extractor q4(Delta) (real p %8==1). bit test + AES flip search <=3.
import json, hashlib
from Crypto.Cipher import AES
p = None
ls = []
n = 113
sv = [True]*n
for i in range(2, n):
    if sv[i]:
        sv[i*i::i] = [False]*len(sv[i*i::i])
        if i >= 3: ls.append(i)
ls = [l for l in range(3, n) if all(l % d for d in range(2, int(l**.5)+1))] + [139]
ls = sorted(set(ls))
p = 2*__import__("math").prod(ls)-1
d = json.load(open("output.txt"))
def q4(z): return pow(z % p, (p-1)//4, p)
def jac(z): return pow(z % p, (p-1)//2, p)
def D(a4, a6): return (-16*(4*a4**3 + 27*a6**2)) % p
insts = d["challenge_data"]
def coef(v):
    v = list(v)
    assert all(t == 0 for t in v[1:]), "curve not over Fp"
    return int(v[0])
print("p%8 =", p%8, " jac(Delta_E0) =", jac(D(0,1)))
v0 = q4(D(0,1))
print("q4(Delta_E0) =", v0)
preds = []
for c in insts:
    a4C, a6C = coef(c["EC"]["a4"]), coef(c["EC"]["a6"])
    a4A, a6A = coef(c["EA"]["a4"]), coef(c["EA"]["a6"])
    a4B, a6B = coef(c["EB"]["a4"]), coef(c["EB"]["a6"])
    r = q4(D(a4C,a6C)) * pow(q4(D(a4A,a6A))*q4(D(a4B,a6B)) % p, p-2, p) % p
    # sanity: q4(Delta) values must be +-v0 (i.e. jac(D)=-1 style); check r^2
    preds.append(r)
from collections import Counter
print("value multiset of r = q4D(C)/(q4D(A)q4D(B)):", Counter(map(str, preds)))
# parity bit: r==+1 -> Delta even -> predict bit 1; r==-1 -> odd -> bit 0
bits = [1 if r == 1 else (0 if r == p-1 else None) for r in preds]
print("num None (r not +-1!):", bits.count(None))
print("predicted ones:", sum(1 for b in bits if b == 1), "zeros:", sum(1 for b in bits if b == 0))
open("pred_bits.txt","w").write("".join(str(b) for b in bits))
# AES flip search: key = SHA256(int.to_bytes(secret,8))[:32], CBC, IV given; FLAG plaintext unknown but pad + 'crypto{' prefix known
key_iv = bytes.fromhex(d["iv"])
ct = bytes.fromhex(d["ct"])
target = ct
base = "".join(str(b) for b in bits)  # bits[j] = SECRET bit j (LSB first, ZZ.bits())
def try_secret(sec):
    key = hashlib.sha256(int.to_bytes(sec, 8)).digest()[:32]
    c = AES.new(key, AES.MODE_CBC, key_iv)
    pt = c.decrypt(ct)
    return pt
def looks_flag(pt):
    if pt[:7] != b"crypto{": return False
    k = pt[-1]
    return 1 <= k <= 16 and pt[-k:] == bytes([k])*k
n = int(base[::-1], 2)  # LSB-first
found = None
import itertools
cands = ([0] + [1 << i for i in range(63)] + [(1<<i)|(1<<j) for i in range(63) for j in range(i+1,63)]
         + [(1<<i)|(1<<j)|(1<<k) for i,j,k in itertools.combinations(range(63),3)])
for f in cands:
    s = n ^ f
    if 0 <= s < 2**63:
        pt = try_secret(s)
        if looks_flag(pt):
            found = s; break
print("flip<=2 found:", found)

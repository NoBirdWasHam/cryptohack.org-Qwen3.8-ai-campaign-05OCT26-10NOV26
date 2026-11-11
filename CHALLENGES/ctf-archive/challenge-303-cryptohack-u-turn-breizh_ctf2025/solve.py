# U-turn (BreizhCTF): hash = A*x mod 256 with x balanced-quinary digits in {-2..2}
# Find small-digit solution via CVP in lattice {(x, Ax+256y)} near (0, h), then
# undo btq truncation (digits 50.. lost -> out = val + c*5^50) and PKCS7-fold structure.
from ast import literal_eval
from Crypto.Util.Padding import pad

A = literal_eval(open("u-turn/A.txt").read())
k, l, n = 48, 50, 256
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
assert len(h) == k

# ---- pure-python reference of sanitize/btq for verification ----
def btq(a: bytes):
    a = sum(ai * 256 ** i for i, ai in enumerate(a))
    cs = [-2, -1, 0, 1, 2]
    res = []
    while a > 0:
        res.append(cs[a % 5])
        a //= 5
    return res

def sanitize(a: bytes, l=50):
    a = pad(a, 16)
    out = b"\x00" * 16
    for i in range(0, len(a), 16):
        out = bytes(x ^ y for x, y in zip(out, a[i:i+16]))
    return btq(out)[:l]

def hashmsg(msg: str):
    x = sanitize(msg.encode())
    return bytes(sum(A[r][i] * x[i] for i in range(len(x))) % 256 for r in range(k))

# ---- lattice: rows [e_i | A_col_i] and [0 | 256 e_j], target (0^50 | h) ----
from fpylll import IntegerMatrix, LLL, CVP
D = l + k
M = IntegerMatrix(D + 0, D)  # D rows? rows = l + k
M = IntegerMatrix(l + k, D)
for i in range(l):
    M[i, i] = 1
    for r in range(k):
        M[i, l + r] = A[r][i]
for j in range(k):
    M[l + j, l + j] = 256
t = [0] * l + list(h)
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams
import time
t0 = time.time()
bk = BKZReduction(M)
bk.lll_obj()
print("lll done", time.time()-t0, flush=True)
def check(v):
    x = [int(z) for z in v[:l]]
    good = all(-2 <= z <= 2 for z in x) and all(
        sum(A[r][j2] * x[j2] for j2 in range(l)) % 256 == h[r] for r in range(k))
    return (good, x)
ok, x = check(CVP.babai(M, t))
print("babai(after bkz) ok:", ok, flush=True)
if not ok:
    p = CVP.closest_vector(M, t)
    print("cvp done", time.time()-t0, flush=True)
    ok, x = check(p)
    print("cvp ok:", ok, flush=True)
if not ok:
    raise SystemExit("CVP failed to find small-digit solution")

print("A*x == h mod 256 verified:", ok)
val = sum(x[i] * 5**i for i in range(l))
P = 5 ** l
# out = val + c*P must be < 2^128
known = b"BZHCTF{"
cands = []
c = 0
while val + c * P < 1 << 128:
    outv = val + c * P
    out = outv.to_bytes(16, "little")
    # out = b1 ^ b2 ; b1[:7]=known, b2[7:]=... ; b2[:7]=hex[9:16], b1[7:16]=hex[0:9]
    tail_hex = bytes(o ^ b for o, b in zip(out[:7], known))
    if all(48 <= b <= 57 or 97 <= b <= 102 for b in tail_hex):
        mid = bytes(out[j] ^ (0x7d if j == 7 else 0x08) for j in range(7, 16))
        if all(48 <= b <= 57 or 97 <= b <= 102 for b in mid):
            flag = "BZHCTF{" + mid.decode() + tail_hex.decode() + "}"
            if hashmsg(flag) == h:
                cands.append(flag)
    c += 1
print("flag candidates:", cands)
assert len(set(cands)) == 1
open("flag_u-turn-breizh_ctf2025.txt", "w").write(cands[0] + "\n")
print("FLAG:", cands[0])

# Final solver: u-turn (BreizhCTF 2025) — cryptohack ctf-archive #303
#
# Vuln: hash is LINEAR in balanced-quinary digits of the XOR-folded padded message:
#   h = A*x mod 256, x = btq(fold(pad(msg)))[:50], A public 48x50 over Z/256.
# Key subtlety (chal.sage): FLAG.strip("BZHCTF{}") removes a CHARACTER SET, so the
# hashed message is the bare 16 hex chars (exactly one block) -> PKCS7 appends a full
# 0x10*16 block -> fold = hx ^ 0x10*16.  (Not the 24-char "BZHCTF{...}" string!)
#
# Attack: L = {v: A v = 0 mod 256} via 2-adic lifting of F2 kernel; particular sol xp
# (Hensel lift, xp.json); Kannan embedding (W=3, BKZ-60) finds W*x_true (norm ~9.5 <<
# lambda1 ~ 900); then balanced-quinary re-expansion + c*5^50 completion scan with
# known-plaintext structural decode; verify hash==h via the utils code path.
from ast import literal_eval
import json, re
from Crypto.Util.Padding import pad
from fpylll import IntegerMatrix
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))
P = 5 ** l
cs = [-2, -1, 0, 1, 2]

def btq(a_bytes):
    a = int.from_bytes(a_bytes, "little")
    res = []
    while a > 0:
        res.append(cs[a % 5]); a //= 5
    return res

def hash_hex(hexstr: str) -> bytes:
    mm = pad(hexstr.encode(), 16)
    oo = b"\x00" * 16
    for q in range(0, len(mm), 16):
        oo = bytes(p ^ q2 for p, q2 in zip(oo, mm[q:q + 16]))
    xs = btq(oo)[:l]
    return bytes(sum(A[r][i] * xs[i] for i in range(len(xs))) % 256 for r in range(k))

def f2_basis_of_kernel(Mx, ncols):
    M2 = [row[:] for row in Mx]
    pv = {}
    r = 0
    for col in range(ncols):
        sel = next((i for i in range(r, len(M2)) if M2[i][col]), -1)
        if sel < 0:
            continue
        M2[r], M2[sel] = M2[sel], M2[r]
        for i in range(len(M2)):
            if i != r and M2[i][col]:
                M2[i] = [a ^ b for a, b in zip(M2[i], M2[r])]
        pv[col] = r
        r += 1
    free = [c for c in range(ncols) if c not in pv]
    basis = []
    for fc in free:
        v = [0] * ncols
        v[fc] = 1
        for col, rr in pv.items():
            if M2[rr][fc]:
                v[col] = 1
        basis.append(v)
    for j in range(ncols):
        if j in pv:
            basis.append([2 if i == j else 0 for i in range(ncols)])
    return basis

A2 = [[a & 1 for a in row] for row in A]
B = f2_basis_of_kernel(A2, l)
jj = 1
while jj < 8:
    AB = [[sum(A[ii][t] * B[q][t] for t in range(l)) for q in range(l)] for ii in range(k)]
    Mj = [[(v >> jj) & 1 for v in row] for row in AB]
    K = f2_basis_of_kernel(Mj, l)
    B = [[sum(K[p][t] * B[t][c] for t in range(l)) for c in range(l)] for p in range(l)]
    jj += 1
assert all(sum(A[ii][t] * row[t] for t in range(l)) % 256 == 0 for ii in range(k) for row in B)
print("L basis ok")

W = 3
E = IntegerMatrix(l + 1, l + 1)
for i in range(l):
    for c in range(l):
        E[i, c] = B[i][c] * W
    E[i, l] = 0
for c in range(l):
    E[l, c] = xp[c] * W
E[l, l] = 1
BKZReduction(E)(BKZParams.Param(block_size=60))

best = None
for i in range(E.nrows):
    if abs(int(E[i, l])) == 1:
        row = [int(E[i, c]) for c in range(l)]
        nrm = sum(z * z for z in row)
        if best is None or nrm < best[0]:
            best = (nrm, row, int(E[i, l]))
nrm, row, last = best
print("best embedding row norm2:", best[0])
x = [last * z // W for z in row]
assert all(-2 <= v <= 2 for v in x)
assert all(sum(A[ii][c] * x[c] for c in range(l)) % 256 == h[ii] for ii in range(k))
print("x_true digits:", x)

val = sum(x[i] * 5 ** i for i in range(l)) + (P - 1) // 2
flags = []
c = 0
while True:
    outv = val + c * P
    if outv >= 1 << 128:
        break
    o = outv.to_bytes(16, "little")
    # msg = 16 hex chars hx (exactly one block) -> pad appends full 0x10 block
    # -> fold o = hx ^ 0x10*16
    hx = bytes(b ^ 0x10 for b in o)
    if all(48 <= y <= 57 or 97 <= y <= 102 for y in hx):
        hexstr = hx.decode()
        if re.fullmatch(r"[0-9a-f]{16}", hexstr) and hash_hex(hexstr) == h:
            flags.append("BZHCTF{" + hexstr + "}")
    c += 1
flags = sorted(set(flags))
print("flag candidates:", flags, " (scanned c <", c, ")")
assert len(flags) == 1
open("flag_u-turn-breizh_ctf2025.txt", "w").write(flags[0] + "\n")
print("FLAG:", flags[0])

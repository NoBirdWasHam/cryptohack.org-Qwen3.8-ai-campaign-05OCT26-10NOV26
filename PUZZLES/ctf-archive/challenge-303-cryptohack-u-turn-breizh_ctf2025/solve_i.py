# Final2: Kannan-embedding SVP. Base lattice L = {x: Ax=0 mod256} (2-adic lifting).
# E rows: [W*B_i | 0], [W*xp | 1]. Shortest vector = (+-W*x_true, +-1) since
# lambda1(L) ~ 900 >> 3*||x_true|| ~ 24. Then unfold digits -> flag, verify by hash.
from ast import literal_eval
import json
from Crypto.Util.Padding import pad
from fpylll import IntegerMatrix
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))

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
print("best embedding row norm²:", best[0])
nrm, row, last = best
x = [last * z // W for z in row]
assert all(last * z % W == 0 for z in row)
assert all(-2 <= v <= 2 for v in x), max(map(abs, x))
assert all(sum(A[ii][c] * x[c] for c in range(l)) % 256 == h[ii] for ii in range(k))
print("x_true found, digits:", x)

def unfold(x):
    P = 5 ** l
    val = sum(x[i] * 5 ** i for i in range(l)) + (P - 1) // 2
    known = b"BZHCTF{"
    cs = [-2, -1, 0, 1, 2]
    res = []
    c = 0
    while True:
        outv = val + c * P
        if outv >= 1 << 128:
            break
        if outv >= 0:
            out = outv.to_bytes(16, "little")
            tail = bytes(o ^ b for o, b in zip(out[:7], known))
            if all(48 <= y <= 57 or 97 <= y <= 102 for y in tail):
                mid = bytes(out[ii] ^ (0x7d if ii == 7 else 0x08) for ii in range(7, 16))
                if all(48 <= y <= 57 or 97 <= y <= 102 for y in mid):
                    flag = "BZHCTF{" + mid.decode() + tail.decode() + "}"
                    mm = pad(flag.encode(), 16)
                    oo = b"\x00" * 16
                    for q in range(0, len(mm), 16):
                        oo = bytes(a ^ b for a, b in zip(oo, mm[q:q + 16]))
                    av = int.from_bytes(oo, "little")
                    xs = []
                    while av > 0:
                        xs.append(cs[av % 5]); av //= 5
                    xs = xs[:l]
                    if bytes(sum(A[rr][i2] * xs[i2] for i2 in range(len(xs))) % 256
                             for rr in range(k)) == h:
                        res.append(flag)
        c += 1
    return res

flags = sorted(set(unfold(x)))
print("flag candidates:", flags)
assert len(flags) == 1
open("flag_u-turn-breizh_ctf2025.txt", "w").write(flags[0] + "\n")
print("FLAG:", flags[0])

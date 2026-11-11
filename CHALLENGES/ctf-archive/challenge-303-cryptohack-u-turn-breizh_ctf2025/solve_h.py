# Final: exhaustive search of solution coset inside digit box {-2..2}^50 via Kannan
# embedding enumeration (fpylll CVP.closest_vector on embedded lattice), then unfold.
from ast import literal_eval
import json, time
from Crypto.Util.Padding import pad
from fpylll import IntegerMatrix, CVP
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))

# rebuild L basis (2-adic lifting, as solve_g)
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
    assert len(basis) == ncols
    return basis

A2 = [[a & 1 for a in row] for row in A]
B = f2_basis_of_kernel(A2, l)
j = 1
while j < 8:
    AB = [[sum(A[i][t] * B[q][t] for t in range(l)) for q in range(l)] for i in range(k)]
    Mj = [[(v >> j) & 1 for v in row] for row in AB]
    K = f2_basis_of_kernel(Mj, l)
    B = [[sum(K[p][t] * B[t][c] for t in range(l)) for c in range(l)] for p in range(l)]
    j += 1
assert all(sum(A[ii][t] * row[t] for t in range(l)) % 256 == 0 for ii in range(k) for row in B)

# Kannan embedding: lattice rows = [B_i | 0] , [xp*W | emb]; target 0; find points with
# tiny weighted x-norm (= digit box) and small last coord.
emb = 1
W = 3
E = IntegerMatrix(l + 1, l + 1)
for i in range(l):
    for c in range(l):
        E[i, c] = B[i][c] * W
    E[i, l] = 0
for c in range(l):
    E[l, c] = xp[c] * W
E[l, l] = emb
t0 = time.time()
BKZReduction(E)(BKZParams.Param(block_size=60))
print("bkz(E) done", time.time() - t0, flush=True)

# CVP with target all-zero vector
p = CVP.closest_vector(E, [0] * (l + 1))
print("closest:", p[:6], "... last:", p[l], flush=True)

def unfold(x):
    P = 5 ** l
    val = sum(x[i] * 5 ** i for i in range(l)) + (P - 1) // 2
    known = b"BZHCTF{"
    res = []
    c = 0
    while True:
        outv = val + c * P
        if outv >= 1 << 128:
            break
        out = outv.to_bytes(16, "little")
        tail = bytes(o ^ b for o, b in zip(out[:7], known))
        if all(48 <= y <= 57 or 97 <= y <= 102 for y in tail):
            mid = bytes(out[ii] ^ (0x7d if ii == 7 else 0x08) for ii in range(7, 16))
            if all(48 <= y <= 57 or 97 <= y <= 102 for y in mid):
                flag = "BZHCTF{" + mid.decode() + tail.decode() + "}"
                mm = pad(flag.encode(), 16)
                oo = b"\x00" * 16
                for i in range(0, len(mm), 16):
                    oo = bytes(a ^ b for a, b in zip(oo, mm[i:i + 16]))
                cs = [-2, -1, 0, 1, 2]
                av = int.from_bytes(oo, "little")
                xs = []
                while av > 0:
                    xs.append(cs[av % 5]); av //= 5
                xs = xs[:l]
                if bytes(sum(A[r][i2] * xs[i2] for i2 in range(len(xs))) % 256
                         for r in range(k)) == h:
                    res.append(flag)
        c += 1
    return res

def check(x):
    return all(-2 <= v <= 2 for v in x) and all(
        sum(A[r][c] * x[c] for c in range(l)) % 256 == h[r] for r in range(k))

x = None
pv = [int(z) for z in p]
if pv[l] != 0:
    sgn = 1 if pv[l] > 0 else -1
    cand = [sgn * pv[c] // W if sgn * pv[c] % W == 0 else None for c in range(l)]
    if all(v is not None for v in cand):
        x = cand
if x is not None and check(x):
    print("box solution ok", flush=True)
else:
    raise SystemExit("no valid box point from CVP; try enumeration callback")
flags = sorted(set(unfold(x)))
print("flag candidates:", flags)
assert len(flags) == 1
open("flag_u-turn-breizh_ctf2025.txt", "w").write(flags[0] + "\n")
print("FLAG:", flags[0])

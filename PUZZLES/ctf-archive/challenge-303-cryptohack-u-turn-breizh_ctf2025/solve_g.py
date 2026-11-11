# Plan F2: square integer basis of L = {x : Ax = 0 mod 256} by 2-adic lattice lifting,
# then LLL + Babai/BKZ/CVP to target xp.
from ast import literal_eval
import json, time
from fpylll import IntegerMatrix, CVP
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))
assert all(sum(A[r][j]*xp[j] for j in range(l)) % 256 == h[r] for r in range(k))

def f2_basis_of_kernel(Mx, ncols):
    """square Z-basis of {z in Z^ncols: Mx z = 0 mod 2}:
    rows: kernel pattern vectors (free col=1) and 2e_j for pivot columns."""
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
        v = [0]*ncols
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
assert all(sum(A2[ii][t]*row[t] for t in range(l)) % 2 == 0 for ii in range(k) for row in B)
print("L1 basis ok", flush=True)

j = 1
while j < 8:
    AB = [[sum(A[i][t]*B[q][t] for t in range(l)) for q in range(l)] for i in range(k)]
    assert all(v % (2**j) == 0 for row in AB for v in row)
    Mj = [[(v >> j) & 1 for v in row] for row in AB]
    K = f2_basis_of_kernel(Mj, l)
    B = [[sum(K[p][t]*B[t][c] for t in range(l)) for c in range(l)] for p in range(l)]
    j += 1
    print("lifted L_", j, flush=True)

assert all(sum(A[ii][t]*row[t] for t in range(l)) % 256 == 0 for ii in range(k) for row in B)
print("L basis verified (256-annihilated)", flush=True)

Bm = IntegerMatrix(l, l)
for i in range(l):
    for c in range(l):
        Bm[i, c] = B[i][c]

def check(x):
    return all(-2 <= v <= 2 for v in x) and all(
        sum(A[r][c] * x[c] for c in range(l)) % 256 == h[r] for r in range(k))

t0 = time.time()
BKZReduction(Bm).lll_obj()
print("lll done", time.time()-t0, flush=True)
v = CVP.babai(Bm, xp)
x = [xp[c] - int(v[c]) for c in range(l)]
print("babai ok:", check(x), " maxabs:", max(map(abs, x)), flush=True)
if not check(x):
    BKZReduction(Bm)(BKZParams.Param(block_size=40, max_time=120, flags=BKZParams.AUTO_ABORT))
    print("bkz done", time.time()-t0, flush=True)
    v = CVP.babai(Bm, xp)
    x = [xp[c] - int(v[c]) for c in range(l)]
    print("babai2 ok:", check(x), flush=True)
if not check(x):
    p = CVP.closest_vector(Bm, xp)
    x = [xp[c] - int(p[c]) for c in range(l)]
    print("cvp ok:", check(x), flush=True)
assert check(x), "plan F failed"
json.dump(x, open("x_planC.json", "w"))
print("SOLVED digits:", x)

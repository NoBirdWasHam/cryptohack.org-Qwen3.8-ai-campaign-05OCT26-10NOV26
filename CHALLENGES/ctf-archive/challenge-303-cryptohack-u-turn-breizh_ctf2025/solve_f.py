# Plan F: build exact integer basis of L = {x : Ax = 0 mod 256} by 2-adic lattice
# lifting L_1 ⊇ L_2 ⊇ ... ⊇ L_8 = L, then LLL + Babai CVP to target xp.
from ast import literal_eval
import json
from fpylll import IntegerMatrix, CVP
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams
import time

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))
assert all(sum(A[r][j]*xp[j] for j in range(l)) % 256 == h[r] for r in range(k))

def matmul(B, rowsA=A):  # B: 50x50 rows-basis -> A*B^T (48x50)
    return [[sum(rowsA[i][t]*B[j][t] for t in range(l)) for j in range(l)] for i in range(k)]

# L_1: basis of {x: A2 x = 0 mod 2} plus 2e_i
A2 = [[a & 1 for a in row] for row in A]
M = [A2[i][:] for i in range(k)]
piv = {}
r = 0
for col in range(l):
    sel = next((i for i in range(r, k) if M[i][col]), -1)
    if sel < 0:
        continue
    M[r], M[sel] = M[sel], M[r]
    for i in range(k):
        if i != r and M[i][col]:
            M[i] = [a ^ b for a, b in zip(M[i], M[r])]
    piv[col] = r
    r += 1
free = [c for c in range(l) if c not in piv]
gens = []
for fc in free:
    v = [0]*l
    v[fc] = 1
    for col, rr in piv.items():
        if M[rr][fc]:
            v[col] = 1
    gens.append(v)
for i in range(l):
    gens.append([2 if j == i else 0 for j in range(l)])
# reduce to 50-row basis (gens may be 50 exactly: free=3 + 50*? -> 53 -> need rank-50 basis:
# instead compute L_1 basis properly: rows of HNF; simplest: use that L1 basis =
# {k_i} U {2e_i} spans L1; fpylll will handle 53>50? needs full-rank 50x50. Use integer HNF via
# fpylll LLL on stacked? Trick: LLL handles only rank=rows. Do Howell-lite: since 2e_i in lattice,
# work mod 2: L1/2Z-lattice basis: pick 47 k_i' plus 2e_i: too many. Instead: basis =
# rows: for i in free-1: k_i; for others: e_j*2 ... need 50 independent:
# take the 3 k_i, and for 47 pivot columns use 2e_j: independence: det? k_i have 1 in free col.
gens = gens[:len(free)]
for j in range(l):
    if j not in free:
        gens.append([2 if i == j else 0 for i in range(l)])
# express e_{free} doubled too (needed: 2e_free in L1)
for j in free:
    gens.append([2 if i == j else 0 for i in range(l)])
# that's 3+47+3=53 rows for rank 50 lattice -> use fpylll: build 53x50 and LLL? not full rank rows.
# Simpler correct basis for L1: vectors: {k_i} (3) with free-coord 1, {2 e_j}: 50 -> 53 total but
# 2e_free are dependent? k_i*e_free=1: 2*k_i - 2e_free combo in span of k's & pivot-2e's? 2k_i has
# free col 2 and pivot cols 0/2*? -> 2k_i is in span{k}u{2e}: yes drop nothing. Keep all 53 and
# run integer HNF ourselves via column op: use fpylll LLL on TRANSPOSE then back? LLL handles
# dependent rows by outputting zero rows in some builds; use fpylll 'IntegerMatrix' 53x50 lll:
Bm = IntegerMatrix(len(gens), l)
for i, g in enumerate(gens):
    for j in range(l):
        Bm[i, j] = g[j]
from fpylll import LLL
LLL.reduction(Bm, 53, l) if hasattr(LLL, "reduction") else None
# fallback: manual: zero rows at top
rows = [[int(Bm[i, j]) for j in range(l)] for i in range(53)]
rows = [rr for rr in rows if any(rr)]
print("L1 basis rows:", len(rows))
B = rows

def f2kernel(Mx):  # Mx: 48 x ncols over F2 -> list of Z vectors spanning kernel
    ncols = len(Mx[0])
    M2 = [row[:] for row in Mx]
    pv = {}
    rr_ = 0
    for col in range(ncols):
        sel = next((i for i in range(rr_, k) if M2[i][col]), -1)
        if sel < 0:
            continue
        M2[rr_], M2[sel] = M2[sel], M2[rr_]
        for i in range(k):
            if i != rr_ and M2[i][col]:
                M2[i] = [a ^ b for a, b in zip(M2[i], M2[rr_])]
        pv[col] = rr_
        rr_ += 1
    fr = [c for c in range(ncols) if c not in pv]
    out = []
    for fc in fr:
        v = [0]*ncols
        v[fc] = 1
        for col, rrow in pv.items():
            if M2[rrow][fc]:
                v[col] = 1
        out.append(v)
    return fr, out

j = 1
while j < 8:
    # B: 50 x 50 basis of L_j
    AB = matmul(B)
    assert all(all(v % (2**j) == 0 for v in row) for row in AB), j
    Mj = [[(v // (2**j)) & 1 for v in row] for row in AB]
    fr, ker = f2kernel(Mj)
    # new basis: {K_i * B} U {2 B rows}, K_i in F2^50 lifted
    newB = []
    for kv in ker:
        newB.append([sum(kv[t]*B[t][c] for t in range(l)) for c in range(l)])
    for t in range(l):
        newB.append([2*w for w in B[t]])
    # newB has (47*? ...)= |fr| + 50 rows; rank 50; take fpylll LLL to get clean 50-basis
    Bm = IntegerMatrix(len(newB), l)
    for i, g in enumerate(newB):
        for c2 in range(l):
            Bm[i, c2] = g[c2]
    from fpylll import LLL as LLLmod
    LLLmod.reduction(Bm, len(newB), l)
    rows = [[int(Bm[i, c2]) for c2 in range(l)] for i in range(len(newB))]
    rows = [rr for rr in rows if any(rr)]
    assert len(rows) == l, (j, len(rows))
    B = rows
    j += 1
    print("lifted to L_", j, " free:", len(fr), flush=True)

# verify basis: all rows satisfy A x = 0 mod 256, and det == |im| sanity
assert all(sum(A[i][t]*row[t] for t in range(l)) % 256 == 0 for row in B)
print("L basis verified")

Bm = IntegerMatrix(l, l)
for i in range(l):
    for c2 in range(l):
        Bm[i, c2] = B[i][c2]
t0 = time.time()
BKZReduction(Bm).lll_obj()
print("lll done", time.time()-t0, flush=True)

def check(x):
    return all(-2 <= v <= 2 for v in x) and all(
        sum(A[r][c2] * x[c2] for c2 in range(l)) % 256 == h[r] for r in range(k))

v = CVP.babai(Bm, xp)
x = [xp[c2] - int(v[c2]) for c2 in range(l)]
print("babai ok:", check(x), " maxabs:", max(map(abs, x)), flush=True)
if not check(x):
    BKZReduction(Bm)(BKZParams.Param(block_size=40, max_time=120, flags=BKZParams.AUTO_ABORT))
    print("bkz done", time.time()-t0, flush=True)
    v = CVP.babai(Bm, xp)
    x = [xp[c2] - int(v[c2]) for c2 in range(l)]
    print("babai2 ok:", check(x), flush=True)
if not check(x):
    p = CVP.closest_vector(Bm, xp)
    x = [xp[c2] - int(p[c2]) for c2 in range(l)]
    print("cvp ok:", check(x), flush=True)
assert check(x), "plan F failed"
json.dump(x, open("x_planC.json", "w"))
print("SOLVED digits:", x)

# Plan E: L = rowspace([A;256I]) dual trick; random full-rank basis -> sympy HNF ->
# fpylll LLL/BKZ + Babai/CVP to target xp; verify small digits.
from ast import literal_eval
import json, random
from sympy import Matrix, det

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))
assert all(sum(A[r][j]*xp[j] for j in range(l)) % 256 == h[r] for r in range(k))

T = [row[:] for row in A] + [[256 if j == i else 0 for j in range(l)] for i in range(l)]

random.seed(1234)
M = Matrix(T)
rs = M.rowspace()
print("rowspace dim:", len(rs))
assert len(rs) == l
Rs = [[int(z) for z in v] for v in rs]
while True:
    Rm = Matrix([[sum(random.randrange(-3, 4) * Rs[i][j] for i in range(l))
                  for j in range(l)] for _ in range(l)])
    if Rm.det() != 0:
        break
Lm = 256 * Rm.inv()
assert all(e.is_integer for e in Lm), "L basis not integral"
print("L basis ok, det =", Lm.det())

from sympy.matrices.normalforms import hermite_normal_form
from fpylll import IntegerMatrix, CVP
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams

import time
t0 = time.time()
for _ in range(1):
    Bm = IntegerMatrix(l, l)
    for i in range(l):
        for j in range(l):
            Bm[i, j] = int(Lm[i, j])
    BKZReduction(Bm).lll_obj()
    print("lll", time.time() - t0, flush=True)

    def check(x):
        return all(-2 <= v <= 2 for v in x) and all(
            sum(A[r][j] * x[j] for j in range(l)) % 256 == h[r] for r in range(k))

    v = CVP.babai(Bm, xp)
    x = [xp[j] - int(v[j]) for j in range(l)]
    print("babai maxabs", max(map(abs, x)), "ok", check(x), flush=True)
    if check(x):
        break
    BKZReduction(Bm)(BKZParams.Param(block_size=40, max_time=120, flags=BKZParams.AUTO_ABORT))
    print("bkz", time.time() - t0, flush=True)
    v = CVP.babai(Bm, xp)
    x = [xp[j] - int(v[j]) for j in range(l)]
    print("babai2 ok", check(x), flush=True)
    if check(x):
        break
    p = CVP.closest_vector(Bm, xp)
    x = [xp[j] - int(p[j]) for j in range(l)]
    print("cvp ok", check(x), flush=True)
    if check(x):
        break
assert check(x), "plan E failed"
json.dump(x, open("x_planC.json", "w"))
print("SOLVED digits:", x)

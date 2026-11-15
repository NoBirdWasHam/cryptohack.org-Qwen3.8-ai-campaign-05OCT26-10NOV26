# Plan C: 50-dim preimage lattice + LLL + Babai (+ tiny local search)
from ast import literal_eval
import itertools, json
from sympy import Matrix, QQ, Rational, ZZ
from sympy.matrices.normalforms import hermite_normal_form

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50

# integer kernel of [A | -256 I] -> x-parts generate ker(A mod 256) together with 256I
Mq = Matrix(k, l + k, lambda i, j: A[i][j] if j < l else (-256 if j == l + i else 0))
ker = Mq.nullspace()
print("kernel dim:", len(ker))
gens = [[int(z) for z in v[:l]] for v in ker] + [[256 if j == i else 0 for j in range(l)] for i in range(l)]
H = hermite_normal_form(Matrix(gens))
rows = [list(H.row(i)) for i in range(H.rows) if any(H.row(i))]
print("basis rank:", len(rows))

# particular solution mod 256 (from xp.json, Hensel DFS)
import json as _json
xp = _json.load(open("xp.json"))
assert all(sum(A[r][j] * xp[j] for j in range(l)) % 256 == h[r] for r in range(k))
print("xp ok")

import fpylll
from fpylll import IntegerMatrix, CVP
Bm = IntegerMatrix(len(rows), l)
for i, r in enumerate(rows):
    for j in range(l):
        Bm[i, j] = r[j]
from fpylll.algorithms.bkz2 import BKZReduction
BKZReduction(Bm).lll_obj()

def check(x):
    return all(-2 <= v <= 2 for v in x) and all(
        sum(A[r][j] * x[j] for j in range(l)) % 256 == h[r] for r in range(k))

# Babai via CVP.babai on rows-basis lattice, target = xp? find x=xp+v small:
# closest vector to target t = xp in lattice L gives v; x = xp - v? use negation:
t = [v for v in xp]
try:
    v = CVP.babai(Bm, t)
except Exception as e:
    print("babai err", e)
    v = None
if v is not None:
    x = [xp[j] - int(v[j]) for j in range(l)]
    print("babai |x|max:", max(map(abs, x)), " ok:", check(x))
if not check(x):
    # local search: x + small combinations of shortest lattice vectors
    rowsL = [[int(Bm[i, j]) for j in range(l)] for i in range(Bm.nrows)]
    rowsL.sort(key=lambda r: sum(z * z for z in r))
    base = x[:]
    found = None
    for depth in range(1, 4):
        for combo in itertools.combinations(range(min(12, len(rowsL))), depth):
            for signs in itertools.product((-1, 1), repeat=depth):
                cand = base[:]
                for idx, s in zip(combo, signs):
                    cand = [c + s * w for c, w in zip(cand, rowsL[idx])]
                if check(cand):
                    found = cand
                    break
            if found: break
        if found: break
    if found: x = found
assert check(x), "Plan C failed"
print("SOLVED digits:", x)
json.dump(x, open("x_planC.json", "w"))

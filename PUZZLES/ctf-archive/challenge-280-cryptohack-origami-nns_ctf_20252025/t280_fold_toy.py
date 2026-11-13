# t280_fold_toy.py — end-to-end validation of the fold attack on a planted toy.
# n=256,q=127,df=dg=10,dr=5,p=2 -> folded lattices dim 256 (m=128 rings).
import numpy as np, random, time, sys
sys.path.insert(0, ".")
from t280_fold import ringmul, conv512, build_lattice, member, glue_and_decrypt, gf2_solve_unit

rng = random.Random(4242)
n, q, df, dg, dr, m = 256, 127, 10, 10, 5, 128

def rand01(d):
    v = np.zeros(n, dtype=np.int64); v[rng.sample(range(n), d)] = 1; return v

def cm(a, b): return conv512(a, b, n) % q

# plant
for _ in range(10000):
    f = rand01(df); g = rand01(dg)
    # h = g/f over Z_q[x]/(x^n-1): solve circulant
    ok = True
    # invert f via GF? over Z_q: circulant matrix rank check via solving T(f) x = g
    Tm = np.zeros((n, n), dtype=np.int64)
    for r_ in range(n):
        for i in range(n): Tm[r_, i] = f[(r_ - i) % n]
    M2 = np.concatenate([Tm % q, (g % q).reshape(n, 1)], axis=1)
    sing = False
    for col in range(n):
        piv = next((rr for rr in range(col, n) if M2[rr, col] % q), None)
        if piv is None: sing = True; break
        M2[[col, piv]] = M2[[piv, col]]
        inv = pow(int(M2[col, col]), -1, q)
        M2[col] = M2[col] * inv % q
        for rr in range(n):
            if rr != col and M2[rr, col] % q: M2[rr] = (M2[rr] - M2[rr, col] * M2[col]) % q
    if sing: continue
    h = M2[:, n]
    if np.all((cm(f, h) - g) % q == 0): break
print("planted f,g,h ok")

flag_bytes = b"NNS{F0LD_1S_M4GIC_T0Y_OK_123456}"
assert len(flag_bytes) == n // 8, len(flag_bytes)
val = int.from_bytes(flag_bytes, "big")
mm = np.array([(val >> i) & 1 for i in range(n)], dtype=np.int64)
r = rand01(dr)
ct = (2 * cm(h, r) + mm) % q

# folds
h0, h1 = h[:m], h[m:]; hp = (h0 + h1) % q; hm = (h0 - h1) % q
f0, f1 = f[:m], f[m:]; g0, g1 = g[:m], g[m:]
fp = (f0 + f1) % q; fm = (f0 - f1) % q   # minus-part kept SIGNED (not mod q) for glue
print("planted fold norms2:", int(np.sum(((f0+f1)**2).astype(np.int64)) + np.sum((g0+g1)**2)))
print("folded membership check:",
      np.all((ringmul(fp % q, hp, m, +1) - ((g0+g1) % q)) % q == 0),
      np.all((ringmul(fm % q, hm, m, -1) - ((g0-g1) % q)) % q == 0))

import os
os.environ.setdefault("X", "1")
from fpylll import IntegerMatrix, BKZ, GSO
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam

def to_intmat(M):
    d = M.shape[0]
    B = IntegerMatrix(d, d)
    for i in range(d):
        for j in range(d):
            B[i, j] = int(M[i, j])
    return B

def from_intmat(B):
    d = B.nrows
    return np.array([[int(B[i, j]) for j in range(d)] for i in range(d)], dtype=np.int64)

def scan(rows, hf, eps, part_name, found):
    for i in range(rows.shape[0]):
        v = rows[i]
        s2 = int(v @ v)
        if s2 > 8 * (df + dg): continue
        u = v[:m]; w = v[m:]
        for s in (1, -1):
            uu = s * u; ww = s * w
            if part_name == "plus":
                if uu.min() >= 0 and uu.max() <= 2 and ww.min() >= 0 and ww.max() <= 2 \
                   and int(uu.sum()) == df and int(ww.sum()) == dg:
                    if member(s * v, hf, m, q, eps):
                        print(f"  plus row{i} norm2={s2} PATTERN")
                        if not any(np.array_equal(c, uu) for c in found["plus"]):
                            found["plus"].append(uu.copy())
            else:
                if np.abs(uu).max() <= 1 and np.abs(ww).max() <= 1 \
                   and 0 <= sum(abs(x) for x in uu) <= df and 0 <= sum(abs(x) for x in ww) <= dg:
                    if member(s * v, hf, m, q, eps):
                        print(f"  minus row{i} norm2={s2} PATTERN")
                        if not any(np.array_equal(c, uu) for c in found["minus"]):
                            found["minus"].append(uu.copy())

found = {"plus": [], "minus": []}
Hp = build_lattice(hp, m, q, +1)
Hm = build_lattice(hm, m, q, -1)
for beta in (20, 30, 45):
    for name, Hlat, hf, eps in (("plus", Hp, hp, +1), ("minus", Hm, hm, -1)):
        if found[name]: continue
        Bm = to_intmat(Hlat)
        lll_reduction(Bm)
        scan(from_intmat(Bm), hf, eps, name, found)
        if not found[name]:
            t0 = time.time()
            bkz_reduction(Bm, BKZParam(beta))
            print(f"{name} BKZ-{beta} in {time.time()-t0:.1f}s")
            scan(from_intmat(Bm), hf, eps, name, found)
    if found["plus"] and found["minus"]: break

ok = False
flag = None
if found["plus"] and found["minus"]:
    t0 = time.time()
    done = False
    for cp in found["plus"][:4]:
        for cmm in found["minus"][:4]:
            fv, gv, flag = glue_and_decrypt(cp, cmm, h, ct, m=m, q=q, n=n, log=print)
            if flag: done = True; break
        if done: break
    print(f"glue {time.time()-t0:.1f}s ->", flag[:80] if flag else None)
    ok = bool(flag) and flag == flag_bytes
print("TOY FOLD ATTACK:", "FULL SUCCESS" if ok else "FAILED")

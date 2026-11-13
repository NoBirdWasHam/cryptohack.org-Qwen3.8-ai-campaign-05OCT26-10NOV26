# Measure det^(1/n) vs e^m margin for DNG lattice family over (m,t,a)
import re, math, itertools, sys
import gmpy2
from flint import fmpz_mat
from fpylll import IntegerMatrix
from dng import build

txt = open("output.txt").read()
N = int(re.search(r"N = 0x([0-9a-f]+)", txt).group(1), 16)
e = int(re.search(r"e = 0x([0-9a-f]+)", txt).group(1), 16)
eb = e.bit_length()
print("N bits", N.bit_length(), "e bits", eb)

def det_bits_per_row(m, t, a):
    X = 1 << 300; Y = 1 << 256; Z = 1 << 768
    M, mons, efs = build(N, e, m, t, X, Y, Z, a=a)
    n = M.nrows
    A = fmpz_mat(n, M.ncols, [int(M[i, j]) for i in range(n) for j in range(M.ncols)])
    G = A * A.transpose()
    d2 = G.det()
    if d2 == 0:
        return n, float("inf"), len(mons)
    db = abs(d2).bit_length() / 2.0
    return n, db / n, len(mons)

rows = []
for m in range(2, 7):
    for t in range(1, 2*m+3):
        for a in sorted({m-1, m, m+2}):
            if a < 0: continue
            try:
                n, dper, nm = det_bits_per_row(m, t, a)
            except Exception as ex:
                print("fail", m, t, a, repr(ex)[:120], flush=True); continue
            margin = m*eb - dper - 0.5*math.log2(nm)
            rows.append((margin, m, t, a, n, dper))
            print(f"m={m} t={t} a={a} n={n} det^(1/n)={dper:.1f} e^m={m*eb} margin~{margin:+.1f}", flush=True)
rows.sort(reverse=True)
print("\nTOP 12 by margin:")
for margin, m, t, a, n, dper in rows[:12]:
    print(f"m={m} t={t} a={a} n={n} margin={margin:+.1f} det^(1/n)={dper:.1f}")

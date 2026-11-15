# f^m PURE lattice, shifted f (gb bits of p guessed), weighted region 300a+254b<=TH.
# rows: f^m * u^a w^b. value(root) = (epd)^m * H(root) => divisible by (ep)^m (conserv. e*2^255-window).
# HG: min vector norm < M/sqrt(n) => H(k,p)=0.
import math, re, sys
from fractions import Fraction
import sympy
from fpylll import IntegerMatrix, LLL
from purelat import ppow
from windowsolve import make_f2
t=open('output.txt').read()
N=int(re.search(r'N = (0x[0-9a-f]+)',t).group(1),16)
e=int(re.search(r'e = (0x[0-9a-f]+)',t).group(1),16)

def build_pure(f, X, Y, m, TH, WX=300.0, WY=254.0):
    fm = ppow(f, m)
    S = [(a,b) for a in range(0,12) for b in range(0,14) if WX*a+WY*b <= TH]
    polys = [{(i+a,j+b):c for (i,j),c in fm.items() if c} for (a,b) in S]
    cols = sorted({k for p in polys for k in p})
    ci = {k:i for i,k in enumerate(cols)}
    B = IntegerMatrix(len(polys), len(cols))
    for r,p in enumerate(polys):
        for (i,j),v in p.items():
            B[r, ci[(i,j)]] = int(v)*(X**i)*(Y**j)
    return B, cols

def run(m, TH, gb=0):
    if gb:
        base=1<<255; step=1<<(255-gb); C=base+1; Y=step//2
    else:
        C=(1<<255)+1; Y=1<<254
    X=1<<300
    f=make_f2(N, C, Y)
    B, cols = build_pure(f, X, Y, m, TH)
    pmin = (1<<255) + (gb and (1<<(255-gb)) or 0)  # lower bound for p in window
    M = (e * pmin) ** m
    bound = M.bit_length() - 1 - 0.5*math.log2(len(cols))
    LLL.reduction(B, delta=0.99)
    nz=[r for r in range(B.nrows) if any(int(B[r,j]) for j in range(B.ncols))]
    mn = min(math.log2(sum(int(B[rr,j])**2 for j in range(B.ncols)))/2 for rr in nz)
    G=sympy.Matrix([[sum(int(B[i,a2])*int(B[j,a2]) for a2 in range(B.ncols)) for j in nz] for i in nz])
    d1=math.log2(abs(int(G.det())))/len(nz)
    print(f'm={m} TH={TH} gb={gb}: {B.nrows}x{B.ncols} r={len(nz)} det1n={d1:.0f} min={mn:.0f} bound={bound:.0f} margin={bound-mn:.0f}', flush=True)
    return B, cols, mn, bound

if __name__=='__main__':
    for m in (2,3):
        for TH in (554, 808, 1062, 1316, 1570, 2000, 2500):
            try:
                run(m, TH)
            except Exception as ex:
                print(m, TH, 'ERR', ex, flush=True)

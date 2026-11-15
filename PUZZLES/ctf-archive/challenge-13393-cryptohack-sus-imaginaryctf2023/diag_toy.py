from solve_toy3 import *
import sympy
from fpylll import IntegerMatrix, LLL

p,q,r = make_toy()
print("p =", p, flush=True)
N = p*q*r; L = N.bit_length()
p0 = 3<<(p.bit_length()-2); r0 = 3<<(r.bit_length()-2)
X = 1<<(p.bit_length()-1); Y = 1<<(r.bit_length()-1)
Xb, Yb = X.bit_length()-1, Y.bit_length()-1
q0 = p0*p0+p0+1
h2 = {(0,0):q0,(1,0):2*p0+1,(2,0):1}
fshift = poly_mul(h2, {(0,0):r0,(0,1):1}); fshift[(0,0)] -= N
m, T = 6, 15
rows = build_rows(fshift, N, m, Xb, Yb, L, T)
mons = sorted({mm for rr in rows for mm in rr})
t, ncols = len(rows), len(mons)
idx = {mm:i for i,mm in enumerate(mons)}
A = IntegerMatrix(t, ncols)
for ri,d in enumerate(rows):
    for (a,b),c in d.items(): A[ri,idx[(a,b)]] = c*pow(X,a)*pow(Y,b)
LLL.reduction(A)
Nth = N**m
import math
px, ry = p-p0, r-r0
print("t,ncols", t, ncols, "log2 N^m", math.log2(int(Nth)), flush=True)
def unscale(ri):
    g = {}
    for ci in range(ncols):
        v = int(A[ri,ci])
        if v:
            (a,b) = mons[ci]; s = pow(X,a)*pow(Y,b)
            if v % s: return None
            g[(a,b)] = v//s
    return g
for ri in range(t):
    g = unscale(ri)
    if g is None: print(ri, "unscale-fail"); continue
    s2 = sum(int(A[ri,ci])**2 for ci in range(ncols))
    nrm_bits = (s2.bit_length()-1)/2.0 if s2 else -1
    val = sum(c*pow(px,a)*pow(ry,b) for (a,b),c in g.items())
    P = resultant_y(fshift, g, N) if g else None
    print(ri, "log2norm~", round(nrm_bits,1), "log2thr", round(math.log2(int(Nth))-math.log2(t),1),
          "zero" if val==0 else "NONZERO", "mult_of_f" if (P==0 or P is None) else "usable", flush=True)
    if val==0 and P and P!=0:
        Pp = P.subs(SX, px)
        print("P(root) =", Pp, "deg", sympy.degree(P, SX), flush=True)

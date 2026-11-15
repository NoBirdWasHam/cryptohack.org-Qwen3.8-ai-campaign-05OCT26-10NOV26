# tiny3.py — end-to-end extraction test on ground-truth tiny instance.
# Build lattice (same code as solve2), take HG-passing rows, build resultants
# R(u) EXACTLY (integer polys), verify R(u0)==0 directly, then gp gcd + roots.
import math, random, os, subprocess
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

random.seed(11)
u, v = sp.symbols('u v')
bits, ebits, m, K = 160, 70, 8, 6
while True:
    p = sp.nextprime(random.getrandbits(bits) | (1 << (bits-1)) | 1)
    q = sp.nextprime(random.getrandbits(bits) | (1 << (bits-1)) | 1)
    if p != q: break
n = p*q
u0 = -(random.randrange(1 << (ebits-1), 1 << ebits))
p0 = p - u0
q0 = n // p0; v0 = q - q0
c0 = p0*q0 - n
X = 1 << (ebits + 6); Y = X
print("u0", abs(u0).bit_length(), "v0", abs(v0).bit_length(), "X", X.bit_length()-1, flush=True)
gmon = {(1,1):1,(1,0):q0,(0,1):p0,(0,0):c0}
FP={}
def fpow(k):
    if k in FP: return FP[k]
    out={(0,0):1}
    for _ in range(k):
        nxt={}
        for ma,va in out.items():
            for mb,vb in gmon.items():
                mm=(ma[0]+mb[0],ma[1]+mb[1]); nxt[mm]=nxt.get(mm,0)+va*vb
        out=nxt
    FP[k]=out; return out
mons = sorted([(a,b) for a in range(K+1) for b in range(K+1)])
idx = {mm:i for i,mm in enumerate(mons)}; w = len(mons)
rows=[]
for j in range(m+1):
    if j > K: break
    Np = n**(m-j)
    for i2 in range(K-j+1):
        for k2 in range(K-j+1):
            row=[0]*w
            for (ia,ib),vv in fpow(j).items():
                ma, mb = ia+i2, ib+k2
                if ma<=K and mb<=K:
                    row[idx[(ma,mb)]] += vv*Np*X**ma*Y**mb
            rows.append(row)
M = IntegerMatrix(len(rows), w)
for i,r in enumerate(rows):
    for jj,val in enumerate(r):
        if val: M[i,jj] = val
M = lll_reduction(M, delta=0.99)
thr = Fraction(n**m)/(Fraction(math.isqrt(w)+1))
cands=[]
for i in range(M.nrows):
    nr2 = sum(int(M[i,jj])**2 for jj in range(w))
    if Fraction(nr2) >= thr*thr: continue
    rr=[int(M[i,jj]) for jj in range(w)]
    if all(x==0 for x in rr): continue
    h = sum(sp.Rational(rr[idx[(a,b)]], X**a * Y**b) * u**a * v**b for (a,b) in mons if rr[idx[(a,b)]])
    if sp.Poly(h, u, v).total_degree() > 0:
        cands.append(h)
print("cands:", len(cands), flush=True)
vf = -(q0*u + c0)/(u + p0)
Rs=[]
for h in cands:
    hp = sp.Poly(sp.expand(h), u, v)
    dv = hp.degree(v)
    R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
    R = sp.Poly(R, u)
    if R.degree() >= 1:
        at = R.as_expr().subs(u, u0)
        Rs.append(R)
        print("R deg", R.degree(), "R(u0)==0:", at == 0, flush=True)
# gcd chain over Z of the nonzero-rooted Rs
g = Rs[0]
for R in Rs[1:]:
    g = sp.gcd(g, R)
print("gcd deg:", sp.Poly(g,u).degree(), "has root u0:", sp.Poly(g,u).as_expr().subs(u,u0) == 0, flush=True)

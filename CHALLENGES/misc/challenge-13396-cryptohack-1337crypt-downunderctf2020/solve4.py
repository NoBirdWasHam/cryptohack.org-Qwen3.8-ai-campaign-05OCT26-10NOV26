# solve4.py — real instance, GENEROUS root bound X=2^700 (covers any plausible
# hint-error model). If resultants then share a consistent integer root, p|n.
import re, sys, math, os, subprocess, time
sys.set_int_max_str_digits(10**7)
import gmpy2
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

t_start = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(HERE, 'output.txt')).read()
hint = int(re.search(r'hint = (\d+)', txt).group(1))
D = int(re.search(r'D = (\d+)', txt).group(1))
n = int(re.search(r'n = (\d+)', txt).group(1))
c = eval(re.search(r'c = (\[.*\])', txt, re.S).group(1))
S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
t0 = (S_lo + S_hi)//2
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
p0 = (t0 + d0)//2
q0 = n // p0
c0 = p0*q0 - n
X = 1 << 700
Y = X
print("p0 bits", p0.bit_length(), "| d0", d0.bit_length(), "| X=2^700", flush=True)

u, v = sp.symbols('u v')
fmon = {(1,1): 1, (1,0): q0, (0,1): p0, (0,0): c0}
FP = {}
def fpow(k):
    if k in FP: return FP[k]
    out = {(0,0): 1}
    for _ in range(k):
        nxt = {}
        for ma, va in out.items():
            for mb, vb in fmon.items():
                m = (ma[0]+mb[0], ma[1]+mb[1]); nxt[m] = nxt.get(m, 0) + va*vb
        out = nxt
    FP[k] = out
    return out

m, K = 8, 6
mons = sorted([(a,b) for a in range(K+1) for b in range(K+1)])
idx = {mm:i for i,mm in enumerate(mons)}
w = len(mons)
rows = []
for j in range(m+1):
    if j > K: break
    Np = n**(m-j)
    for i2 in range(K-j+1):
        for k2 in range(K-j+1):
            row = [0]*w
            for (ia, ib), vv in fpow(j).items():
                ma, mb = ia+i2, ib+k2
                if ma <= K and mb <= K:
                    row[idx[(ma,mb)]] += vv * Np * X**ma * Y**mb
            rows.append(row)
print("LLL", len(rows), "x", w, flush=True)
M = IntegerMatrix(len(rows), w)
for i, r in enumerate(rows):
    for jj, val in enumerate(r):
        if val: M[i, jj] = val
M = lll_reduction(M, delta=0.99)
thr = Fraction(n**m) / (Fraction(math.isqrt(w)+1))
cands = []
nrm_log = []
for i in range(M.nrows):
    nr2 = sum(int(M[i, jj])**2 for jj in range(w))
    if Fraction(nr2) >= thr*thr: continue
    nrm_log.append((nr2).bit_length())
    rr = [int(M[i, jj]) for jj in range(w)]
    if all(x == 0 for x in rr): continue
    h = sp.Rational(0)
    for jj in range(w):
        val = rr[jj]
        if val:
            (a, b) = mons[jj]
            h += sp.Rational(val, X**(a+b)) * u**a * v**b
    num = sp.numer(sp.expand(sp.together(h)))
    if sp.Poly(num, u, v).total_degree() > 0:
        cands.append(num)
print("HG rows:", len(cands), "norm2-bit range:", min(nrm_log) if nrm_log else None, max(nrm_log) if nrm_log else None, "thr2 bits:", (thr.numerator**2 // thr.denominator**2).bit_length(), flush=True)
vf = -(q0*u + c0)/(u + p0)
Rs = []
for h in cands:
    hp = sp.Poly(sp.expand(h), u, v)
    dv = hp.degree(v)
    R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
    R = sp.Poly(R, u)
    if R.degree() >= 1:
        Rs.append(R.as_expr())
print("Rs:", len(Rs), "degs:", sorted(set(int(sp.Poly(r,u).degree()) for r in Rs)), flush=True)
for i, r in enumerate(Rs[:8]):
    P = sp.Poly(r, u)
    with open(os.path.join(HERE, f"r{i}.txt"), 'w') as fh:
        for co in P.all_coeffs()[::-1]:
            fh.write(str(int(co)) + "\n")
print("dumped r0..r", min(len(Rs),8)-1, "elapsed", int(time.time()-t_start), flush=True)

# selfcheck.py — GROUND-TRUTH full-scale test: my own 1337-bit p,q + hint, run
# through the EXACT solve2 pipeline (parse->S0->p0->lattice->resultants).
# If extraction recovers my p, the pipeline is sound and the real instance has
# some specific pathology; if it fails at identical geometry, pipeline is wrong.
import math, random, sys, time
sys.set_int_max_str_digits(10**7)
from fractions import Fraction
import gmpy2
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

random.seed(int(time.time()) % 1000)
bits = 1337
while True:
    p = sp.nextprime(random.getrandbits(bits) | (1 << (bits-1)) | 1)
    q = sp.nextprime(random.getrandbits(bits) | (1 << (bits-1)) | 1)
    if p != q and p*q != p and abs(p-q) > (1 << 1330): break
n = p*q
D = 63**14
import decimal
decimal.getcontext().prec = 4200
s = decimal.Decimal(p).sqrt() + decimal.Decimal(q).sqrt()
hint = int(D * s)

# ---- exact copy of solve.py head logic ----
S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
t0 = (S_lo + S_hi)//2
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
p0 = (t0 + d0)//2
q0 = n // p0
c0 = p0*q0 - n
dSb = (S_hi-S_lo+2).bit_length()
amp = max(0, t0.bit_length()-d0.bit_length()+1)
X = 1 << (dSb + amp + 4)
Y = X
u0_true = p - p0; v0_true = q - q0
print("TRUE u0 bits", abs(u0_true).bit_length(), "v0 bits", abs(v0_true).bit_length(),
      "X = 2^", X.bit_length()-1, "| in-bound:", abs(u0_true) <= X and abs(v0_true) <= Y, flush=True)
assert S_lo <= p+q <= S_hi, "S not in interval!!"

u, v = sp.symbols('u v')
fmon = {(1,1):1,(1,0):q0,(0,1):p0,(0,0):c0}
FP={}
def fpow(k):
    if k in FP: return FP[k]
    out={(0,0):1}
    for _ in range(k):
        nxt={}
        for ma,va in out.items():
            for mb,vb in fmon.items():
                mm=(ma[0]+mb[0],ma[1]+mb[1]); nxt[mm]=nxt.get(mm,0)+va*vb
        out=nxt
    FP[k]=out; return out
m, K = 8, 6
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
print("LLL...", flush=True)
M = lll_reduction(M, delta=0.99)
thr = Fraction(n**m)/(Fraction(math.isqrt(w)+1))
cands=[]; nvan = 0; ntot = 0
for i in range(M.nrows):
    nr2 = sum(int(M[i,jj])**2 for jj in range(w))
    if Fraction(nr2) >= thr*thr: continue
    rr=[int(M[i,jj]) for jj in range(w)]
    if all(x==0 for x in rr): continue
    h = sum(sp.Rational(rr[idx[(a,b)]], X**a * Y**b) * u**a * v**b for (a,b) in mons if rr[idx[(a,b)]])
    if sp.Poly(h, u, v).total_degree() > 0:
        ntot += 1
        if sp.together(h.subs({u: u0_true, v: v0_true})) == 0: nvan += 1
        cands.append(h)
print(f"pass={ntot} vanish={nvan}", flush=True)
vf = -(q0*u + c0)/(u + p0)
Rs=[]
for h in cands:
    hp = sp.Poly(sp.expand(h), u, v)
    dv = hp.degree(v)
    R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
    R = sp.Poly(R, u)
    if R.degree() >= 1:
        Rs.append(R)
nz = sum(1 for R in Rs if R.as_expr().subs(u, u0_true) == 0)
print(f"Rs={len(Rs)} rooted_at_u0={nz} degs={[R.degree() for R in Rs[:6]]}", flush=True)
if len(Rs) >= 2:
    g = sp.gcd(Rs[0], Rs[1])
    print("gcd01 deg", g.degree(), "rooted:", g.as_expr().subs(u,u0_true)==0, flush=True)
    print("SELF RESULT:", "OK" if (g.degree()>=1 and g.as_expr().subs(u,u0_true)==0) else "BROKEN", flush=True)

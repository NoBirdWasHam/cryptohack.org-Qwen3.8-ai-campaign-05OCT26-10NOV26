import sys, math, random
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
u, v = sp.symbols('u v')
random.seed(7)
p = sp.nextprime(random.getrandbits(40)|2**39); q = sp.nextprime(random.getrandbits(40)|2**39)
n = p*q; dSb, amp = 12, 1; X = 1 << (dSb+amp+4); Y = X
e1 = 12345; e2 = -6789
p0, q0 = p-e1, q-e2
c0 = p0*q0 - n
fmon = {(1,1):1,(1,0):q0,(0,1):p0,(0,0):p0*q0}
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
m, Dd = 6, 4
mons = sorted([(a,b) for d in range(Dd+1) for a in range(d+1) for b in [d-a]])
idx={mm:i for i,mm in enumerate(mons)}; w=len(mons)
rows=[]
for j in range(m+1):
    Np = n**(m-j)
    for dd in range(Dd-2*j+1):
        for a in range(dd+1):
            mm=(a,dd-a); row=[0]*w
            for (ia,ib),vv in fpow(j).items():
                ma,mb = ia+mm[0], ib+mm[1]
                if ma+mb<=Dd: row[idx[(ma,mb)]] += vv*Np*X**ma*Y**mb
            rows.append(row)
M = IntegerMatrix(len(rows), w)
for i,r in enumerate(rows):
    for jj,val in enumerate(r):
        if val: M[i,jj]=val
M = lll_reduction(M, delta=0.99)
thr = Fraction(n**m)/(Fraction(math.isqrt(w)+1))
print("thr bits", math.log2(float(thr)) if float(thr)<1e300 else thr.numerator.bit_length())
fexpr = u*v + q0*u + p0*v + c0
vf = -(p0*u+c0)/(u+q0)
for i in range(min(8, M.nrows)):
    nr2 = sum(int(M[i,jj])**2 for jj in range(w))
    h = sp.Rational(0)
    for jj in range(w):
        val=int(M[i,jj])
        if val:
            (a,b)=mons[jj]; h += sp.Rational(val, X**(a+b))*u**a*v**b
    hh = sp.numer(sp.expand(sp.together(h)))
    rem = sp.expand(sp.together(hh.subs(v, vf)*(u+q0)**12))
    rem = sp.numer(rem)
    iszero = sp.Poly(rem,u).is_zero
    print(f"row {i}: normbits~{nr2.bit_length()/2:.0f} pass={Fraction(nr2)<thr*thr} support={[(k,int(vv).bit_length()) for k,vv in fmon.items()][:0]}",
          "h-deg", sp.Poly(hh,u,v).total_degree(), "f-divisible(zero-on-curve)=", iszero, flush=True)

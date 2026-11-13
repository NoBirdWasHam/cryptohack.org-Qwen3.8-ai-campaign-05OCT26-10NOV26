# tiny2.py — for ONE violating row: is r_ab divisible by X^{a+b}? does the
# integer poly evaluated at root match valQ? where does the mod argument break?
import math, random
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

random.seed(7)
u, v = sp.symbols('u v')
bits, ebits, m, K = 160, 70, 3, 4
while True:
    p = sp.nextprime(random.getrandbits(bits) | (1 << (bits-1)) | 1)
    q = sp.nextprime(random.getrandbits(bits) | (1 << (bits-1)) | 1)
    if p != q: break
n = p*q
_ = random.randrange(1 << (ebits-1), 1 << ebits)
u0 = -(random.randrange(1 << (ebits-1), 1 << ebits))
p0 = p - u0
q0 = n // p0; v0 = q - q0
c0 = p0*q0 - n
X = 1 << (ebits + 6); Y = X
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
np_rows = 0
for i in range(M.nrows):
    nr2 = sum(int(M[i,jj])**2 for jj in range(w))
    if Fraction(nr2) >= thr*thr: continue
    r = [int(M[i,jj]) for jj in range(w)]
    if all(x == 0 for x in r): continue
    div_ok = all(r[idx[(a,b)]] % (X**a * Y**b) == 0 for (a,b) in mons)
    c = [r[idx[(a,b)]] // (X**a * Y**b) for (a,b) in mons]
    val_int = sum(cc * u0**a * v0**b for cc,(a,b) in zip(c, mons))
    valQ = sum(sp.Rational(rr,1)*sp.Rational(u0,X)**a*sp.Rational(v0,Y)**b for rr,(a,b) in zip(r, mons))
    zeroQ = (valQ == 0)
    print(f"row{i}: div_ok={div_ok} int-eval==valQ: {sp.Rational(val_int,1)==valQ} "
          f"eval==0: {val_int==0} eval mod n^m==0: {val_int % n**m == 0}", flush=True)
    np_rows += 1
    

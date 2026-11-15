# Proper HG bivariate lattice: f = q^2 xy + qB x + qA y + AB - n, root (U,V).
# Test at ratio: n ~ N, X=Y ~ N^{1/3} (LSB 1/3 known on both primes).
import random
from Crypto.Util.number import getPrime, isPrime
from fpylll import IntegerMatrix, LLL

QB = 45
q = getPrime(QB)
class LCG:
    def __init__(s,a,x,b): s.a,s.x,s.b=a%q,x%q,b%q
    def fetch(s):
        r=s.x; s.x=(s.a*s.x+s.b)%q; return r
L1=LCG(random.randint(1,q-1),random.randint(1,q-1),random.randint(1,q-1))
L2=LCG(random.randint(1,q-1),random.randint(1,q-1),random.randint(1,q-1))
L3=LCG(random.randint(1,q-1),random.randint(1,q-1),random.randint(1,q-1))
pr=[]
while len(pr)<2:
    p=L3.fetch()*q*q+L2.fetch()*q+L1.fetch()
    if isPrime(p): pr.append(p)
p1,p2=pr; n=p1*p2; A=p1%q; B=p2%q
U=(p1-A)//q; V=(p2-B)//q
print("p bits",p1.bit_length(),"u,v bits",U.bit_length(),V.bit_length())

from sympy import symbols, resultant
Xs,Ys=symbols('Xs Ys')
def to_sym(p):
    return sum(c*Xs**i*Ys**j for (i,j),c in p.items())

def run(s, box=2):
    # basis monomials: box = full box [0..w]^2 with w = s+1
    w = s+1
    mono=[(i,j) for i in range(w+1) for j in range(w+1)]
    midx={m:k for k,m in enumerate(mono)}
    rows=[]
    # f-rows: f * x^i y^j * n^{s-i-j}, i+j <= s
    for i in range(s+1):
        for j in range(s+1-i):
            wt=n**(s-i-j)
            row=[0]*len(mono)
            row[midx[(i+1,j+1)]]=q*q*wt
            row[midx[(i+1,j)]]=q*B*wt
            row[midx[(i,j+1)]]=q*A*wt
            row[midx[(i,j)]]=(A*B-n)*wt
            rows.append(row)
    # N-rows: n^{s+1} * x^k y^l for monomials not covered
    for i in range(w+1):
        for j in range(w+1):
            if (i,j)==(0,0) or (i>0 and j>0 and i<=s+1 and j<=s+1):
                # covered-ish: include only those NOT reachable as x^i y^j *f with i+j<=s
                pass
    # standard: rows n^{s} * x^k y^l for all monomials in box
    for i in range(w+1):
        for j in range(w+1):
            row=[0]*len(mono); row[midx[(i,j)]]=n**s; rows.append(row)
    # scale columns by U^i V^j
    cols=[U**i * V**j for (i,j) in mono]
    M=IntegerMatrix.from_iterable(len(rows),len(mono),[rows[r][c]*cols[c] for r in range(len(rows)) for c in range(len(mono))])
    LLL.reduction(M)
    polys=[]
    for r in range(M.nrows):
        d={}
        for c in range(len(mono)):
            v=int(M[r][c])
            if v: d[mono[c]] = v // cols[c] if v % cols[c]==0 else v  # keep scaled; recompute ev via scaled
        if d: polys.append((d,{mono[c]:int(M[r][c]) for c in range(len(mono)) if int(M[r][c])}, cols))
    van=[]
    for d,sc,cols in polys:
        val=sum(c*U**i*V**j for (i,j),c in sc.items())  # value at root of SCALING-free poly? careful: rows coeffs * U^iV^j => sum(c * U^i V^j) where c = scaled coeff? value = sum(int_coeff * U^i V^j) with int_coeff unscaled; we stored scaled coeffs, so value = sum(scaled * ... /cols * ...) -> compute unscaled
        uns = {k:(v//cols[midx[k]] if v%cols[midx[k]]==0 else 0) for k,v in sc.items()}
        val = sum(c*U**k[0]*V**k[1] for k,c in uns.items())
        if val==0: van.append(uns)
    return van

done=False
for s in (2,3,4,5):
    van=run(s)
    print("s",s,"vanishing polys",len(van))
    import itertools
    for p,qy in itertools.combinations(van,2):
        try:
            r=resultant(to_sym(p),to_sym(qy),Ys)
            poly=r.as_poly(Xs)
            if not poly: continue
            for rt in poly.real_roots():
                if rt.is_Rational and rt.q==1:
                    u=int(rt)
                    if 0<u and (n%(A+q*u))==0:
                        print("SOLVED s=",s,"fac",A+q*u); done=True; break
            if done: break
        except Exception: pass
    if done: break
print("done",done)

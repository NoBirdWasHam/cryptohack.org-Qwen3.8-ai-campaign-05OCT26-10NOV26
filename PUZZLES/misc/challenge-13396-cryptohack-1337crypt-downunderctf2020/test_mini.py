# Mini end-to-end validation of the Coppersmith pipeline on synthetic small primes.
import sys, math, random
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

u, v = sp.symbols('u v')

def build_box(n, X, Y, fpow, m, K):
    # rectangular monomial box a,b<=K; rows n^{m-j} g^j u^i v^k, i,k <= K-j
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
    return rows, mons, w
    FP = {}
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
    Y = X
    for (m, Dd) in [(8,8),(10,8)]:
        mons = sorted([(a,b) for d in range(Dd+1) for a in range(d+1) for b in [d-a]])
        idx={mm:i for i,mm in enumerate(mons)}; w=len(mons)
        rows=[]
        for j in range(m+1):
            Np = n**(m-j)
            for dd in range(Dd-2*j+1):
                for a in range(dd+1):
                    mm=(a,dd-a)
                    row=[0]*w
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
        cands=[]; fails=0
        for i in range(M.nrows):
            nr2 = sum(int(M[i,jj])**2 for jj in range(w))
            if Fraction(nr2) < thr*thr:
                fails=0
                h=sp.Rational(0); nz=False
                for jj in range(w):
                    val=int(M[i,jj])
                    if val:
                        nz=True
                        (a,b)=mons[jj]
                        h += sp.Rational(val, X**(a+b)) * u**a * v**b
                if not nz: continue
                num=sp.numer(sp.expand(sp.together(h)))
                if sp.Poly(num,u,v).total_degree()>0: cands.append(num)
            else:
                fails+=1
                if fails>=5: break
        Rs=[]
        for h in cands:
            hp = sp.Poly(sp.expand(h), u, v)
            try: qh, rh = sp.div(hp, sp.Poly(fexpr,u,v), u, v)
            except Exception: continue
            if not rh.is_zero:
                R = sp.Poly(sp.numer(sp.together(rh.as_expr())), u)
                if R.degree()>=1: Rs.append(R)
        print(f"  m={m} D={Dd}: cands={len(cands)} nonzeroRs={len(Rs)}", flush=True)
        pool=[]
        for i in range(len(Rs)):
            for R2 in Rs[:i]+Rs[i+1:]:
                g=sp.gcd(Rs[i],R2)
                if 1<=g.degree()<=30: pool.append(g)
        pool+= [R for R in Rs if R.degree()<=12]
        for g in pool:
            fac=sp.factor(g.as_expr())
            for f1 in sp.Mul.make_args(fac):
                P=sp.Poly(f1,u)
                if P.degree()==1:
                    a1,a0=P.all_coeffs()
                    if sp.Rational(a0,a1).is_Integer:
                        rc=int(-a0/a1)
                        for pp in (p0+rc,p0-rc):
                            if pp>1 and n%pp==0: return pp
    return None

random.seed(1337)
for trial in range(3):
    p = sp.nextprime(random.getrandbits(60)|2**59)
    q = sp.nextprime(random.getrandbits(60)|2**59)
    n = p*q
    dSb, amp = 25, 1
    X = 1 << (dSb+amp+4)
    e1 = random.randrange(-(1<<(dSb+amp-6)), 1<<(dSb+amp-6))
    e2 = random.randrange(-(1<<(dSb+amp-6)), 1<<(dSb+amp-6))
    # perturb both p0,q0 consistently-ish; the relation only needs SOME (u0,v0) with prod=n
    # so choose p0=p-e1, and q0 = (n - p0*q + q*e2... ) simply: q0 = q - e2, u0 = p-p0=e1, v0=e2
    p0, q0 = p-e1, q-e2
    got = solve_instance(n, p0, q0, X)
    print("trial", trial, "->", got == p)

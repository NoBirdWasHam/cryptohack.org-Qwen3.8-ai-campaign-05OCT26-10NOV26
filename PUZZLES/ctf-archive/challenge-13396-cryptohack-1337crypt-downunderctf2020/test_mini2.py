# Mini validation of RECTANGULAR-BOX bivariate Coppersmith.
# Rows: n^{m-j} g^j u^i v^k, g=(u+p0)(v+q0) (g(root)=n -> rows = 0 mod n^m). Box a,b<=K.
# HG: ||h(Xu,Xv)||_2 < n^m/sqrt(w) => h(u0,v0)=0 over Z. Divide h by exact f (c0=p0q0-n):
# remainder rh(u) nonzero => rh(u0)=0 => gcd/factor => u0.
import math, random
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

u, v = sp.symbols('u v')

def make_fpow(p0, q0):
    gmon = {(1,1):1,(1,0):q0,(0,1):p0,(0,0):p0*q0}
    FP = {}
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
    return fpow

def build_box(n, X, Y, fpow, m, K):
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

def recover(p0, q0, X, fpow, n, cands, mons, w):
    c0 = p0*q0 - n
    fexpr = u*v + q0*u + p0*v + c0
    Rs=[]
    vf = -(q0*u + c0)/(u + p0)
    for h in cands:
        hp = sp.Poly(sp.expand(h), u, v)
        dv = hp.degree(v)
        R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
        R = sp.Poly(R, u)
        if R.degree()>=1: Rs.append(R)
    print(f"    rem-polys={len(Rs)} degs={[r.degree() for r in Rs][:6]}", flush=True)
    pool=[]
    if len(Rs) >= 2:
        g = sp.gcd(Rs[0], Rs[1])
        i = 2
        while g.degree() > 30 and i < len(Rs):
            g = sp.gcd(g, Rs[i]); i += 1
        if g.degree() >= 1:
            pool.append(g)
    pool += [R for R in Rs if R.degree() <= 14]
    print("      pool degs", [pp.degree() for pp in pool], flush=True)
    for g in pool:
        if g.degree()==1:
            a1,a0=g.all_coeffs()
            if sp.Rational(a0,a1).is_Integer:
                rc=int(-a0/a1)
                for pp in (p0+rc,p0-rc):
                    if pp>1 and n%pp==0: return pp
        try: fac=sp.factor(g.as_expr())
        except Exception: continue
        for f1 in sp.Mul.make_args(fac):
            P=sp.Poly(f1,u)
            if P.degree()==1:
                a1,a0=P.all_coeffs()
                if sp.Rational(a0,a1).is_Integer:
                    rc=int(-a0/a1)
                    for pp in (p0+rc,p0-rc):
                        if pp>1 and n%pp==0: return pp
    return None

def solve_instance(n, p0, q0, X, params):
    fpow = make_fpow(p0, q0)
    Y = X
    for (m, K) in params:
        rows, mons, w = build_box(n, X, Y, fpow, m, K)
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
        print(f"  m={m} K={K}: HG-cands={len(cands)}", flush=True)
        got = recover(p0, q0, X, fpow, n, cands, mons, w)
        if got: return got
    return None

if __name__ == "__main__":
    random.seed(1337)
    ok=0
    for trial in range(3):
        p = sp.nextprime(random.getrandbits(60)|2**59)
        q = sp.nextprime(random.getrandbits(60)|2**59)
        n = p*q
        X = 1 << 26
        e1 = random.randrange(-(1<<20), 1<<20)
        e2 = random.randrange(-(1<<20), 1<<20)
        p0, q0 = p-e1, q-e2
        got = solve_instance(n, p0, q0, X, [(8,6)])
        r = (got == p)
        ok += r
        print("trial", trial, "->", r)
    print("MINI RESULT:", ok, "/3")

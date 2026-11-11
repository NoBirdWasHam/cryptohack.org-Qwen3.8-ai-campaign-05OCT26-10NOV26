# TIGHT-shifted bivariate Coppersmith over Z for f(x,y) = (x^2+x+1)*y - N, root (p,r).
# Key fix vs solve_toy3: p0 = 1.5*2^(L-1) => |p-p0| <= 2^(L-2)  (X = 2^(L-2), not 2^(L-1)),
# same for r. This puts X*Y BELOW the N^(2/3) exact-integer-root threshold (marginal case).
# Region: rows f^k * x^i * y^j * N^(m-k), k=0..m, (i,j) in box i<=um*(m)/Msc etc (scaled by M=m).
# Toy: p 60b, q~120b, r 180b. If toy solved -> same script with real (n, 510/1535 sizes).
import sys, itertools
from fpylll import IntegerMatrix, LLL
import sympy

SX, SY = sympy.symbols('x y')

def make_toy():
    from Crypto.Util.number import getPrime, isPrime
    while True:
        p = getPrime(60)
        if isPrime(p*p+p+1):
            return p, p*p+p+1, getPrime(180)

def pmul(A, B):
    C = {}
    for (a,b),ca in A.items():
        for (c,d),cb in B.items():
            k=(a+c,b+d); C[k] = C.get(k,0) + ca*cb
    return {k:v for k,v in C.items() if v}

def fshift_dict(p0, r0, N):
    q0 = p0*p0+p0+1
    h = {(0,0):q0, (1,0):2*p0+1, (2,0):1}
    g = pmul(h, {(0,0):r0, (0,1):1})
    g[(0,0)] = g.get((0,0),0) - N
    return {k:v for k,v in g.items() if v}

def region(M, um, wm):
    pts=[]
    for j in range(wm*M+1):
        for i in range(um*M+1):
            pts.append((i,j))
    return pts

def run(N, X, Y, root, fshift, m, um, wm, cap_t=2600, cap_c=2600, verbose=False):
    fpows=[{(0,0):1}]
    for _ in range(m): fpows.append(pmul(fpows[-1], fshift))
    pts = region(m, um, wm)
    rowd=[]
    for k in range(m+1):
        Ns = pow(N, m-k)
        fk = fpows[k]
        for (i,j) in pts:
            rowd.append({(a+i,b+j): c*Ns for (a,b),c in fk.items()})
    t=len(rowd)
    mons = sorted({mm for d in rowd for mm in d})
    ncols=len(mons)
    if t>cap_t or ncols>cap_c: return dict(st="skip", t=t, c=ncols, m=m, um=um, wm=wm)
    if t>ncols: return dict(st="fat", t=t, c=ncols, m=m, um=um, wm=wm)
    idx={mm:i for i,mm in enumerate(mons)}
    A=IntegerMatrix(t, ncols)
    for ri,d in enumerate(rowd):
        for (a,b),c in d.items():
            A[ri, idx[(a,b)]] = c*pow(X,a)*pow(Y,b)
    LLL.reduction(A)
    px, ry = root
    # minUB (squared norms of projected vectors) in log2 via floats is messy; use norms.
    best=None; zeros=0; won=None
    fS = sum(c*SX**a*SY**b for (a,b),c in fshift.items())
    for ri in range(t):
        g={}; 
        for ci in range(ncols):
            v=int(A[ri,ci])
            if v:
                (a,b)=mons[ci]; s=pow(X,a)*pow(Y,b)
                if v % s: g=None; break
                g[(a,b)]=v//s
        if not g: continue
        nn=sum(v for v in (x*x for x in ( [0] ))) # placeholder
        val=sum(c*pow(px,a)*pow(ry,b) for (a,b),c in g.items())
        if val!=0: continue
        # exclude multiples of fshift: divide by leading monomial x^2 y
        # quick test: deg in y ==1 and deg x <=2 pattern
        gy=max(b for _,b in g)
        if gy==1:
            # g multiple of f iff g = (alpha x^2+...)*f : check leading x^2y coeff relation
            pass
        gS = sum(c*SX**a*SY**b for (a,b),c in g.items())
        R = sympy.resultant(sympy.expand(fS), sympy.expand(gS), SY)
        if R==0: continue
        zeros+=1
        if R.subs(SX,px)==0:
            won=dict(st="WON", m=m, um=um, wm=wm, t=t, c=ncols, ri=ri)
            # recover p from R roots
            cands=set()
            for rt in sympy.nroots(R.as_poly(SX), n=15, maxsteps=200):
                re,im=rt.as_real_imag()
                if abs(im)>1e-6: continue
                xv=int(round(float(re)))
                for dd in (-1,0,1):
                    pc=p0glob+xv+dd
                    if pc>1 and N%pc==0: cands.add(pc)
            won["p"]=cands
            return won
    return dict(st="none", m=m, um=um, wm=wm, t=t, c=ncols, zeros=zeros)

p0glob=None

if __name__=="__main__":
    p,q,r = make_toy()
    N=p*q*r
    Lp=p.bit_length(); Lr=r.bit_length()
    p0=(3<<(Lp-2)); r0=(3<<(Lr-2))
    X=1<<(Lp-2); Y=1<<(Lr-2)
    assert abs(p-p0)<=X and abs(r-r0)<=Y
    p0glob=p0
    fshift=fshift_dict(p0,r0,N)
    print("toy", N.bit_length(), "X*Y=",X.bit_length()-1+Y.bit_length()-1, "2/3 L=", 2*N.bit_length()//3, flush=True)
    for (m,um,wm) in [(6,2,2),(8,2,2),(10,2,2),(8,1,3),(10,1,3),(12,1,2),(10,3,1),(6,3,3),(8,3,2),(12,2,1),(14,1,2),(16,1,1),(12,2,2),(10,2,3)]:
        res=run(N,X,Y,(p-p0,r-r0),fshift,m,um,wm)
        print(res, flush=True)
        if res.get("st")=="WON":
            print("TOY SOLVED", res["p"], "expected", p)
            sys.exit(0)
    print("toy NOT solved by any config")

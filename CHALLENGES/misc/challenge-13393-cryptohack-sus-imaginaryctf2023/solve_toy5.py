# CORRECTED bivariate Coppersmith: F(x,y) = x*(x^2+x+1)*y - N, EXACT integer root (p, r).
# (prior scripts used f=(x^2+x+1)y-N evaluated at (p,r): does NOT vanish there; root is (p,pr).)
# Construction: HG shifts, rows F^k * x^i * y^j * N^(m-k), both vars shifted by p0,r0.
# Phase A: r=40-bit toy (X*Y=2^96 < N^(1/2)=2^110): MUST solve -> validates pipeline.
# Phase B: real-ratio toy r=180 (X*Y ~ 2^237 > N^(1/2)=2^180): expected FAIL, quantifies gap.
import sys
from fpylll import IntegerMatrix, LLL
import sympy

SX, SY = sympy.symbols('x y')

def pmul(A,B):
    C={}
    for (a,b),ca in A.items():
        for (c,d),cb in B.items():
            k=(a+c,b+d); C[k]=C.get(k,0)+ca*cb
    return {k:v for k,v in C.items() if v}

def make_toy(rbits):
    from Crypto.Util.number import getPrime, isPrime
    while True:
        p=getPrime(60)
        if isPrime(p*p+p+1):
            return p, p*p+p+1, getPrime(rbits)

def Fshift(p0,r0,N):
    g0 = {(0,0):p0**3+p0**2+p0, (1,0):3*p0**2+2*p0+1, (2,0):3*p0+1, (3,0):1}
    g = pmul(g0, {(0,0):r0,(0,1):1})
    g[(0,0)] = g.get((0,0),0) - N
    return {k:v for k,v in g.items() if v}

def solve(N, X, Y, root, fs, m, u, w, cap=3000):
    fpows=[{(0,0):1}]
    for _ in range(m): fpows.append(pmul(fpows[-1],fs))
    pts=[(i,j) for j in range(int(w*m)+1) for i in range(int(u*m)+1)]
    rowd=[]
    for k in range(m+1):
        Ns=pow(N,m-k); fk=fpows[k]
        for (i,j) in pts:
            rowd.append({(a+i,b+j):c*Ns for (a,b),c in fk.items()})
    mons=sorted({mm for d in rowd for mm in d})
    t,c=len(rowd),len(mons)
    if t>c or t>cap: return dict(st="skip",t=t,c=c)
    idx={mm:i for i,mm in enumerate(mons)}
    A=IntegerMatrix(t,c)
    for ri,d in enumerate(rowd):
        for (a,b),cc in d.items():
            A[ri,idx[(a,b)]] = cc*pow(X,a)*pow(Y,b)
    LLL.reduction(A)
    px,ry=root
    fS=sum(cc*SX**a*SY**b for (a,b),cc in fs.items())
    for ri in range(t):
        g={}
        ok=True
        for ci in range(c):
            v=int(A[ri,ci])
            if v:
                (a,b)=mons[ci]; s=pow(X,a)*pow(Y,b)
                if v%s: ok=False; break
                g[(a,b)]=v//s
        if not ok or not g: continue
        val=sum(cc*pow(px,a)*pow(ry,b) for (a,b),cc in g.items())
        if val!=0: continue
        gS=sum(cc*SX**a*SY**b for (a,b),cc in g.items())
        R=sympy.resultant(sympy.expand(fS),sympy.expand(gS),SY)
        if R==0: continue
        if R.subs(SX,px)!=0: continue
        hit=None
        for rt in sympy.nroots(R.as_poly(SX),n=50,maxsteps=300):
            re,im=rt.as_real_imag()
            if abs(im)>1e-6: continue
            for dd in (-1,0,1):
                pc=P0+int(round(float(re)))+dd
                if pc>1 and N%pc==0:
                    return dict(st="WON",m=m,u=u,w=w,t=t,p=pc)
    return dict(st="none",t=t,c=c)

def phase(rbits,label,expect):
    p,q,r = make_toy(rbits)
    N=p*q*r
    global P0
    Lp,Lr=p.bit_length(),r.bit_length()
    P0=3<<(Lp-2); R0=3<<(Lr-2)
    X=1<<(Lp-2); Y=1<<(Lr-2)
    assert abs(p-P0)<=X and abs(r-R0)<=Y
    fs=Fshift(P0,R0,N)
    assert fs and sum(v*0 for v in fs.values())==0
    print(f"[{label}] Nbits={N.bit_length()} XYbits={(X.bit_length()-1)+(Y.bit_length()-1)} thresh(N^(1/2))={N.bit_length()//2}", flush=True)
    for m in (1,2,3):
        for (u,w) in ((4,2),(5,2),(6,2),(6,3),(4,3),(8,2),(8,3),(10,2)):
            res=solve(N,X,Y,(p-P0,r-R0),fs,m,u,w)
            print(f"[{label}] m={m} u={u} w={w} -> {res}", flush=True)
            if res.get("st")=="WON":
                print(f"[{label}] SOLVED p={p==res['p']}", flush=True)
                return True
    print(f"[{label}] not solved (expected {expect})", flush=True)
    return False

if __name__=="__main__":
    a = phase(40, "easy-r40", expect="WON")
    if not a:
        print("PIPELINE UNVALIDATED - stop")
        sys.exit(1)
    b = phase(180, "ratio-real", expect="none")
    print("RESULT: pipeline-valid:", a, " real-ratio-solved:", b)

# PURE f^m-shifted lattice: rows f^m * u^a w^b (a+b<=D), scaled by X^i W^j.
# Any lattice element h=f^m*A: h(root) = (e p d)^m * A(root) == 0 mod (ep)^m.
# HG bound (e*2^255)^m/sqrt(n) >> LLL short vectors => h(root)=0 EXACTLY => A(root)=0.
import math, sympy, sys, pickle
from fractions import Fraction
from fpylll import IntegerMatrix, LLL, BKZ

def ppow(f, m):
    r={(0,0):1}
    for _ in range(m):
        out={}
        for (i1,j1),c1 in r.items():
            for (i2,j2),c2 in f.items():
                kk=(i1+i2,j1+j2); out[kk]=out.get(kk,0)+c1*c2
        r=out
    return r

def build(f, X, Y, m, D):
    fm = ppow(f, m)
    polys=[]
    for a in range(D+1):
        for b in range(D-a+1):
            polys.append({(i+a,j+b):c for (i,j),c in fm.items() if c})
    cols=sorted({k for p in polys for k in p})
    ci={k:i for i,k in enumerate(cols)}
    B=IntegerMatrix(len(polys),len(cols))
    for r,p in enumerate(polys):
        for (i,j),v in p.items():
            B[r,ci[(i,j)]]=int(v)*(X**i)*(Y**j)
    return B,cols

def make_f(N):
    u,w=sympy.symbols('u w')
    P=(1<<255)+2*w+1
    Gx=sympy.expand(u*(P-1)*(N-P)+P)
    f={}
    for mon,c in Gx.as_coefficients_dict().items():
        du=int(sympy.degree(mon,u)) if mon!=1 else 0
        dw=int(sympy.degree(mon,w)) if mon!=1 else 0
        if mon==1: du=dw=0
        f[(du,dw)]=int(f.get((du,dw),0))+int(c)
    return f

def solve(N, e, m=2, D=9, k=None, p=None, tag='', save=None):
    f=make_f(N)
    X,Y=1<<300,1<<254
    u0 = k if k is not None else None
    w0 = (p-(1<<255)-1)//2 if p is not None else None
    fm=ppow(f,m)
    B,cols=build(f,X,Y,m,D)
    bound=((e*(1<<255))**m).bit_length()-1-0.5*math.log2(B.ncols)
    print(f'{tag}: {B.nrows}x{B.ncols} bound={(e*(1<<255))**m and bound:.1f}', flush=True)
    LLL.reduction(B, delta=0.999)
    van=[]
    best=9e9
    for r in range(B.nrows):
        s=sum(int(B[r,c])**2 for c in range(B.ncols))
        if s==0: continue
        b2=s.bit_length()/2.0
        best=min(best,b2)
        if b2 < bound:
            row={}
            for ci,(i,j) in enumerate(cols):
                v=int(B[r,ci])
                if v: row[(i,j)]=Fraction(v,(X**i)*(Y**j))
            if u0 is not None:
                val=sum(c*(u0**i)*(w0**j) for (i,j),c in row.items())
                if val==0: van.append(row)
            else:
                van.append(row)
    print(f'{tag}: min={best:.1f} under-bound={len(van)}', flush=True)
    if save:
        with open(save,'wb') as fh: pickle.dump({'van':van,'cols':cols,'X':X,'Y':Y,'f':f,'m':m},fh)
    return van

if __name__=='__main__':
    import random
    from Crypto.Util.number import getPrime
    random.seed(2)
    p=getPrime(256); q=getPrime(768); N=p*q; phi=(p-1)*(q-1)
    while True:
        d=getPrime(300)
        if d>N**0.292: break
    e=pow(d,-1,phi); k=(e*d-1)//phi
    van = solve(N,e,m=2,D=9,k=k,p=p,tag='synthetic m2 D9')
    print('vanishing count:', len(van), flush=True)
    # divide one vanishing poly by f^m exactly and check quotient vanishes
    if van:
        us,ws=sympy.symbols('u w')
        f=make_f(N)
        Fpoly=sum(sympy.Integer(c)*us**i*ws**j for (i,j),c in f.items())
        for row in van[:3]:
            H=sum(sympy.Rational(c)*us**i*ws**j for (i,j),c in row.items())
            qot = sympy.simplify(sympy.together(H/Fpoly))
            # evaluate quotient at root numerically? just check divisibility
            rr = sympy.div(sympy.Poly(H, us, ws), sympy.Poly(Fpoly, us, ws))
            print('div check remainder zero:', rr[1].is_zero if hasattr(rr[1],'is_zero') else rr[1]==0, flush=True)
            if rr[0]:
                u0,w0 = k,(p-(1<<255)-1)//2
                val = rr[0].as_expr().subs({us:u0, ws:w0})
                print('quotient vanishes at root:', val==0, flush=True)

#!/usr/bin/env python3
# Factor R = Res(x^13+37, (x+42)^13+42): p-1 then pure-python ECM (stage1).
import random, sys, time
import sympy
from math import gcd
import gmpy2

n = gmpy2.mpz(open('_R.txt').read().strip())
log = open('factor_log.txt','a',buffering=1)
def P(*a):
    s=' '.join(str(x) for x in a)
    print(s); log.write(s+'\n')

def done(f):
    P("FACTOR FOUND:", f, " cofactor digits:", len(str(n//f)))
    open('factor_found.txt','w').write(str(f))
    sys.exit(0)

def pm1(B):
    for a in (2,3,5):
        g = gmpy2.mpz(a)
        for l in sympy.primerange(2,B+1):
            e = l
            while e*l <= B: e*=l
            g = pow(g, e, n)
            if (g-1) % 10**6 == 0: pass
        d = gcd(g-1, n)
        if 1 < d < n: done(d)
    P("p-1 up to", B, "nothing")

def ecm_curve(A, Bp, x0, y0, B1):
    # affine Weierstrass y^2 = x^3 + A x + Bp over Z/n, point (x0,y0)
    def inv(v):
        r = gmpy2.invert(v, n)   # raises on noninvertible
        return r
    def add(P1, P2):
        if P1 is None: return P2
        if P2 is None: return P1
        x1,y1 = P1; x2,y2 = P2
        if x1==x2:
            if (y1+y2)%n==0: return None
            l = (3*x1*x1 + A)*inv(2*y1) % n
        else:
            l = (y2-y1)*inv(x2-x1) % n
        x3 = (l*l - x1 - x2) % n
        y3 = (l*(x1-x3) - y1) % n
        return (x3,y3)
    def mul(Pk, m):
        r = None; q = Pk
        while m:
            if m&1: r = add(r,q)
            q = add(q,q); m>>=1
        return r
    Q = (x0,y0)
    for l in sympy.primerange(2,B1+1):
        e = l
        while e*l <= B1: e*=l
        Q = mul(Q, e)
    return Q

def ecm(B1, curves):
    rnd = random.Random(0xC0FFEE)
    t0=time.time()
    for c in range(curves):
        try:
            x0 = gmpy2.mpz(rnd.randrange(6, 1<<160))
            y0 = gmpy2.mpz(rnd.randrange(6, 1<<160))
            A  = gmpy2.mpz(rnd.randrange(1, 1<<160))
            Bp = (y0*y0 - x0*x0*x0 - A*x0) % n
            d0 = gcd(4*4*A*A*A + 27*4*Bp*Bp, n)  # rough discriminant check
            if 1 < d0 < n: done(d0)
            ecm_curve(A,Bp,x0,y0,B1)
            if c%25==0: P(f"B1={B1} curve {c}/{curves} t={time.time()-t0:.0f}s")
        except ZeroDivisionError:
            P(f"hit at curve {c} B1={B1}")
            # rerun to extract the factor
            found=None
            def inv2(v):
                g=gcd(v,n)
                if 1<g<n: raise SystemExit(done(g))
                return gmpy2.invert(v,n)
            # brute: repeat with gcd-checking add
            A2=A; 
            def add2(P1,P2):
                if P1 is None: return P2
                if P2 is None: return P1
                x1,y1=P1;x2,y2=P2
                if x1==x2:
                    den=(2*y1)%n; num=(3*x1*x1+A2)%n
                    if (y1+y2)%n==0: return None
                else:
                    den=(x2-x1)%n; num=(y2-y1)%n
                g=gcd(den,n)
                if 1<g<n: done(g)
                l=num*inv2(den)%n
                return ((l*l-x1-x2)%n,(l*(x1-((l*l-x1-x2)%n))-y1)%n)
            Q=(x0,y0)
            for l in sympy.primerange(2,B1+1):
                e=l
                while e*l<=B1: e*=l
                mm=e;r=Qq=None
                q=Q
                while mm:
                    if mm&1: r=add2(r,q)
                    q=add2(q,q); mm>>=1
                Q=r
            P("extract failed?")
    P(f"ECM B1={B1}: {curves} curves, nothing ({time.time()-t0:.0f}s)")

pm1(500000)
ecm(11000, 400)
ecm(50000, 300)
ecm(250000, 200)
P("ECM exhausted for now")

#!/usr/bin/env python3
# rsa_backdoor: CM curve over R=(Z/n)[d]/(d^2-DH), DH=disc(H_-427).
# R/pR = F_p x F_p (H splits mod p), R/qR = F_{q^2} (H irred mod q since (-7/q)=-1).
# E/R: y^2=x^3+Ax+B, A=3x/(1728-x), B=2x/(1728-x), x=(d-HB)/2.
# #E(F_p comp) = p+1-t, t=+-1. If t=+1: [n]P=O mod p -> a denominator in the
# affine chain has gcd(.,n)=p. If t=-1: twist by d in R (nonsquare comps) flips.
# POINT TRICK: x0=a+d => g(x0)=U+V*d with V=3a^2+A1*a+(DD+A0+B1); solve V=0
# mod n (quadratic), then g(x0)=U in Z/n, sqrt via U^((n+1)/4) (n=7 mod 8).
import random
from math import gcd
import gmpy2

HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

class BadDen(Exception):
    def __init__(self, den): self.den = den

def make_R(n):
    DD = (HB*HB - 4*HC) % n
    inv2 = (n + 1) // 2
    def rmul(u, v):
        a, b = u; c, d = v
        return ((a*c + b*d*DD) % n, (a*d + b*c) % n)
    def radd(u, v): return ((u[0]+v[0]) % n, (u[1]+v[1]) % n)
    def rsub(u, v): return ((u[0]-v[0]) % n, (u[1]-v[1]) % n)
    def rsq(u): return rmul(u, u)
    def rnorm(u):
        a, b = u
        return (a*a - b*b*DD) % n
    def rinv(u):
        N = rnorm(u)
        try: g = pow(N, -1, n)
        except ValueError: raise BadDen(N)
        return (u[0]*g % n, (-u[1]) * g % n)
    return DD, inv2, rmul, radd, rsub, rsq, rnorm, rinv

def tsqrt(a, nn):
    x = pow(a % nn, (nn + 1) // 4, nn)
    return x if x*x % nn == a % nn else None

def factor(n, seed=1, trials=30, verbose=False):
    rng = random.Random(seed)
    DD, inv2, rmul, radd, rsub, rsq, rnorm, rinv = make_R(n)
    xd = ((-HB % n) * inv2 % n, inv2)          # x = (d - HB)/2
    ti = rinv(rsub((1728, 0), xd))
    A = rmul((3, 0), ti); B = rmul((2, 0), ti)
    A0, A1 = A; B0, B1 = B

    def add(P, Q, A, B):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if radd(y1, y2) == (0, 0): raise BadDen(rnorm(y1))
            den = rmul((2, 0), y1); num = radd(radd(rsq(x1), rsq(x1)), radd(rsq(x1), (A[0], 0)))
            num = (num[0], num[1])  # 3x^2 + A
        else:
            den = rsub(x2, x1); num = rsub(y2, y1)
        m = rmul(num, rinv(den))
        x3 = rsub(rsub(rsq(m), x1), x2)
        y3 = rsub(rmul(m, rsub(x1, x3)), y1)
        return (x3, y3)

    def find_point(A, B, tries=8):
        A0, A1 = A; B0, B1 = B
        for _ in range(tries):
            bb = rng.randrange(1, n)
            # V(a) = 3*bb*a^2 + A1*a + (bb^3*DD + A0*bb + B1) = 0
            qa = (3*bb) % n
            qb = A1
            qc = (bb*bb % n*bb % n*DD + A0*bb + B1) % n
            Dsc = (qb*qb - 4*qa*qc) % n
            sq = tsqrt(Dsc, n)
            if sq is None:
                g = gcd(Dsc, n)
                if 1 < g < n: return g   # lucky factor
                continue
            a = (-qb + sq) * pow(2*qa, -1, n) % n
            # U = a^3 + 3*a*bb^2*DD + A0*a + A1*bb*DD + B0
            U = (a*a %n*a %n + 3*a %n*(bb*bb %n)*DD + A0*a + A1*bb %n*DD + B0) % n
            x0 = (a, bb)
            # verify g(x0) == U
            gval = radd(radd(rmul(rsq(x0), x0), rmul(A, x0)), B)
            if gval[1] != 0 or gval[0] != U:
                continue
            if gcd(U, n) != 1 or pow(U, (n-1)//2, n) != 1: continue
            y = tsqrt(U, n)
            if y is None: continue
            return ((x0, (y, 0)),)
        return None

    for trial in range(trials):
        if trial == 0:
            d = (1, 0)
        else:
            d = (rng.randrange(n), rng.randrange(n))
        try:
            d2 = rsq(d); d3 = rmul(d2, d)
            At = rmul(d2, A); Bt = rmul(d3, B)
        except BadDen as ex:
            f = gcd(ex.den, n)
            if 1 < f < n: return f
        res = find_point(At, Bt)
        if res is None: continue
        if isinstance(res, int): return res
        P, = res
        R = None; k = n
        try:
            while k:
                if k & 1: R = add(R, P, At, Bt)
                P = add(P, P, At, Bt); k >>= 1
        except BadDen as ex:
            f = gcd(ex.den, n)
            if 1 < f < n: return f
            if verbose: print("  bad den but trivial gcd")
        if R is None and verbose: print("  O mod n, retry")
    return None

if __name__ == "__main__":
    import sys, time
    from Crypto.Util.number import getPrime, isPrime
    mode = sys.argv[1] if len(sys.argv) > 1 else "self"
    if mode == "self":
        rng = random.Random(7)
        ok = 0
        for it in range(4):
            while True:
                s = rng.randrange(2**62, 2**64)
                t = 427*s*s + 1
                if t % 4 == 0 and isPrime(t//4): p = t//4; break
            while True:
                q = getPrime(160); n = p*q
                if n % 4 == 3: break   # tsqrt shortcut needs n=3 mod 4
            t0 = time.time()
            f = factor(n, seed=100+it, verbose=True)
            good = f in (p, q)
            ok += good
            print(f"inst{it}: good={good} f={f} %.1fs" % (time.time()-t0))
        print("ok:", ok, "/4")

#!/usr/bin/env python3
# Validate the ECM implementation on a toy semiprime with known 30-digit factor.
import random, time
from math import gcd
import gmpy2, sympy

p = gmpy2.next_prime(gmpy2.mpz(10)**29 + 7)
q = gmpy2.next_prime(gmpy2.mpz(10)**31 + 101)
n = p*q
print("toy n digits:", len(str(n)), "target factor digits:", len(str(p)))

def ecm_curve(n, A, Bp, x0, y0, B1):
    def add(P1, P2):
        if P1 is None: return P2
        if P2 is None: return P1
        x1,y1 = P1; x2,y2 = P2
        if x1==x2:
            if (y1+y2)%n==0: return None
            den = (2*y1)%n; num = (3*x1*x1 + A)%n
        else:
            den = (x2-x1)%n; num = (y2-y1)%n
        g = gcd(den, n)
        if 1 < g < n: raise ValueError(f"FACTOR {g}")
        l = num*gmpy2.invert(den,n) % n
        x3 = (l*l - x1 - x2) % n
        y3 = (l*(x1-x3) - y1) % n
        return (x3,y3)
    def mul(Pk, m):
        r=None; q_=Pk
        while m:
            if m&1: r=add(r,q_)
            q_=add(q_,q_); m>>=1
        return r
    Q=(x0,y0)
    for l in sympy.primerange(2,B1+1):
        e=l
        while e*l<=B1: e*=l
        Q=mul(Q,e)
    return Q

rnd=random.Random(1)
t0=time.time()
for c in range(400):
    try:
        x0=gmpy2.mpz(rnd.randrange(6,1<<160)); y0=gmpy2.mpz(rnd.randrange(6,1<<160)); A=gmpy2.mpz(rnd.randrange(1,1<<160))
        Bp=(y0*y0-x0*x0*x0-A*x0)%n
        ecm_curve(n,A,Bp,x0,y0,11000)
    except ValueError as e:
        f=int(str(e).split()[1])
        print("found:", n//f==p or f==p, e, f"curve {c}, {time.time()-t0:.0f}s")
        break
    except ZeroDivisionError:
        print("invert blowup (uncaught gcd case!) curve", c)
        break
else:
    print("toy ECM FAILED in 400 curves")

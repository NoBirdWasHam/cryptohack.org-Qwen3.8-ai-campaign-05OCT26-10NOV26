#!/usr/bin/env python3
"""Atkin-Morain CM factoring for rsa_backdoor, fast affine implementation.
E over R=(Z/n)[x]/(H_-427): #E(F_p)=p+1-t, t=+-1. If t=+1 then n*P=O mod p
=> gcd(Z(nP),n)=p. Twists by u in R cover t=-1 (need both p-components nonsquare)."""
import re, random, sys
from math import gcd
import gmpy2

HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

def radd(u,v,n): return ((u[0]+v[0])%n,(u[1]+v[1])%n)
def rsub(u,v,n): return ((u[0]-v[0])%n,(u[1]-v[1])%n)
def rmul(u,v,n):
    a,b=u; c,d=v
    ad_bc=(a*d+b*c)%n; bd=(b*d)%n
    return ((a*c-HB*ad_bc+HC*bd)%n,(ad_bc-HB*bd)%n)
def rsq(u,n): return rmul(u,u,n)
def rnorm(u,n):
    a,b=u; return (a*a-a*b*HB+b*b*HC)%n
def rinv(u,n):
    a,b=u; N=rnorm(u,n)
    g=pow(N,-1,n)  # raises -> gcd(N,n) is a factor
    return ((a-b*HB)*g%n,(-b)*g%n)

def tsqrt(a,n):
    if a==0: return 0
    s,d=0,n-1
    while d%2==0: d//=2; s+=1
    z=2
    while gmpy2.jacobi(z,n)!=-1: z+=1
    c=pow(z,d,n); x=pow(a,(d+1)//2,n); t=pow(a,d,n); m=s
    while t!=1:
        i,tt=1,t*t%n
        while tt!=1: tt=tt*tt%n; i+=1
        b2=pow(c,1<<(m-i-1),n)
        x=x*b2%n; t=t*b2*b2%n; c=b2*b2%n; m=i
    return x

class CE:  # curve y^2=x^3+Ax+B over R, affine, None=O
    def __init__(self,n,u=(1,0)):
        j=(0,1)
        self.n=n
        ti=rinv(rsub((1728,0),j,n),n)
        jti=rmul(j,ti,n)
        A=rmul((3,0),jti,n); B=rmul((2,0),jti,n)
        if u!=(1,0):
            u2=rsq(u,n); u4=rsq(u2,n); u6=rmul(u4,u2,n)
            A=rmul(A,u4,n); B=rmul(B,u6,n)
        self.A=A; self.B=B
    def on(self,P):
        if P is None: return True
        x,y=P; n=self.n
        return rmul(y,y,n)==radd(radd(rmul(rsq(x,n),x,n),rmul(self.A,x,n),n),self.B,n)
    def add(self,P,Q):
        if P is None: return Q
        if Q is None: return P
        n=self.n; x1,y1=P; x2,y2=Q
        if x1==x2:
            if rsub(y1,y2,n)==(0,0): return self.dbl(P)
            return None
        m=rmul(rsub(y1,y2,n),rinv(rsub(x1,x2,n),n),n)
        m2=rsq(m,n)
        x3=rsub(rsub(m2,x1,n),x2,n)
        y3=rsub(rmul(m,rsub(x1,x3,n),n),y1,n)
        return (x3,y3)
    def dbl(self,P):
        if P is None: return None
        n=self.n; x,y=P
        if y==(0,0): return None
        m=rmul(radd(radd(rsq(x,n),rsq(x,n),n),rsq(x,n),n),(3,0),n)
        m=rmul(m,rinv(rmul((2,0),y,n),n),n)
        m2=rsq(m,n)
        x3=rsub(m2,rmul((2,0),x,n),n)
        y3=rsub(rmul(m,rsub(x,x3,n),n),y,n)
        return (x3,y3)
    def mul(self,P,k):
        R=None
        while k:
            if k&1: R=self.add(R,P)
            P=self.dbl(P); k>>=1
        return R

def find_point(E,n,rng):
    while True:
        x0=(rng.randrange(n),rng.randrange(n))
        g=radd(radd(rmul(rsq(x0,n),x0,n),rmul(E.A,x0,n),n),E.B,n)
        N=rnorm(g,n)
        gg=gcd(N,n)
        if gg!=1: raise ZeroDivisionError("gcd=%d"%gg)
        if pow(N,(n-1)//2,n)!=1: continue
        xs=tsqrt(N,n)
        y=rmul(rmul(g,(xs,0),n),rinv((N,0),n),n)
        if rmul(y,y,n)!=g: continue
        P=(x0,y)
        if E.on(P): return P

def factor(n,seed=1,twist=None):
    rng=random.Random(seed)
    E=CE(n,(1,0) if twist is None else twist)
    try:
        P=find_point(E,n,rng)
    except ZeroDivisionError as ex:
        return int(str(ex).split("=")[1])
    R=E.mul(P,n)
    if R is None: return None
    for z in R[0]+R[1]:
        f=gcd(z,n)
        if 1<f<n: return f
    return None

def make_instance(lo,hi,qb,seed):
    from Crypto.Util.number import getPrime,isPrime
    rng=random.Random(seed)
    while True:
        s=rng.randrange(2**lo,2**hi)
        t=427*s*s+1
        if t%4==0 and isPrime(t//4): p=t//4; break
    q=getPrime(qb); return p,q,p*q

if __name__=="__main__":
    import time
    t0=time.time()
    p,q,n=make_instance(62,64,160,42)
    f=factor(n,seed=7)
    print("selftest:",f,"correct:",f in (p,q),"%.1fs"%(time.time()-t0))

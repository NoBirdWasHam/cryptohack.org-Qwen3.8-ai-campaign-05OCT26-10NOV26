#!/usr/bin/env python3
# Leet Universe (ImaginaryCTF daily): server prints flag[:g],
# g = gcd(x^13+37, (x+42)^13+42). g | Res(f,h) always; pick x a common root
# mod enough prime powers of R via CRT => g >= product >> len(flag).
import sys
from sympy import symbols, resultant, Poly
from sympy.ntheory.modular import crt

x = symbols('x')
f = x**13 + 37
h = (x + 42)**13 + 42
R = abs(int(resultant(f, h, x)))
print("digits of R:", len(str(R)))

def primes_upto(n):
    s = bytearray([1])*(n+1); s[0]=s[1]=0
    for i in range(2,int(n**0.5)+1):
        if s[i]: s[i*i::i]=bytearray(len(s[i*i::i]))
    return [i for i in range(2,n+1) if s[i]]

# common root of f,h mod p^e starting from root mod p; lift by brute t
def lift(r, p, maxe):
    e = 1; m = p
    while e < maxe:
        mn = m*p
        found = None
        for t in range(p):
            r2 = r + t*m
            if (pow(r2,13,mn)+37) % mn == 0 and (pow(r2+42,13,mn)+42) % mn == 0:
                found = r2; break
        if found is None: break
        r, m, e = found, mn, e+1
    return r, m

facs = []
rem = R
for p in primes_upto(20000):
    if rem % p == 0:
        facs.append(p)
        while rem % p == 0: rem //= p
    if rem == 1: break
print("small prime factors:", facs[:20], "count", len(facs))

moduli=[]; rems=[]; prod=1
for p in facs:
    r0=None
    for r in range(p):
        if (pow(r,13,p)+37)%p==0 and (pow(r+42,13,p)+42)%p==0:
            r0=r; break
    if r0 is None:
        print("no root mod",p,"(unexpected)"); continue
    r,pe = lift(r0,p,12)
    moduli.append(pe); rems.append(r); prod*=pe
    if prod > 10**80: break

sol = crt(moduli, rems)
X = int(sol[0])
g = __import__('math').gcd(X**13+37, (X+42)**13+42)
print("log10(prod)=",len(str(prod))-1," log10(gcd)=",len(str(g))-1)
if g > 10**70:
    open('payload_x.txt','w').write(str(X))
    print("payload written, digits:", len(str(X)))
else:
    print("gcd too small, need more factors")

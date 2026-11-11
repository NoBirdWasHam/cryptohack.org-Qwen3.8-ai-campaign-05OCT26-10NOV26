import math, gmpy2, sympy
ns={}
exec(open("output.txt").read(), ns)
n=ns['n']
# p-1 attack: gcd(2^M-1, n), M = lcm(1..B)
B1=20000
M=1
for p in sympy.primerange(2,B1):
    pk=p
    while pk*p<=B1: pk*=p
    M*=pk
g=math.gcd(pow(2,M,n)-1, n)
print("p-1 gcd(20k):", "smooth-factor!" if (1<g<n) else g)
# Fermat with multipliers k=1..60
hits=[]
for k in range(1,61):
    kn=k*n; a=gmpy2.isqrt(kn)
    b2=a*a-kn
    if b2>0:
        b=gmpy2.isqrt(b2)
        if b*b==b2: hits.append(k)
print("fermat k<=60 hits:", hits)
# structure: 8n = (2p)(s^2+3) r with s=2p+1. Check n mod 7,9,13 for sanity
print("n mod 3,7,9,13:", n%3, n%7, n%9, n%13)

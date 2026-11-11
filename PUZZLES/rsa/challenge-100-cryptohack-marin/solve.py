#!/usr/bin/env python
# marin (100): p = 2^a - 1, q = 2^b - 1 (Mersenne numbers). n = p*q.
# Since p | n, we have n % (2^a - 1) == 0 for the true a. Brute-force a.
import gmpy2
src=open('output_provided.txt').read()
n=int(src.split('n: ')[1].split()[0])
e=int(src.split('e: ')[1].split()[0])
c=int(src.split('c: ')[1].split()[0])
BL=n.bit_length()
print("n bits:", BL)
factors=[]
for a in range(2, BL+1):
    M=(1<<a)-1
    if n % M == 0:
        factors.append((a,M))
print("a with (2^a-1)|n:", [a for a,_ in factors])
# the two Mersenne primes
p=q=None
for a,M in factors:
    if gmpy2.is_prime(M):
        q2=n//M
        if q2==M or (gmpy2.is_prime(q2) and q2==n//M):
            p,q=M,q2; break
print("p bits",p.bit_length(),"q bits",q.bit_length())
phi=(p-1)*(q-1)
d=pow(e,-1,phi)
m=pow(c,d,n)
from Crypto.Util.number import long_to_bytes
print("FLAG:", long_to_bytes(m).decode())

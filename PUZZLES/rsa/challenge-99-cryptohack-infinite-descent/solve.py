#!/usr/bin/env python
# infinite_descent (99): p,q both derive from the SAME 2048-bit r;
#   p += (512-bit randoms), q += (256-bit randoms)  =>  |p-q| <= ~2^512.
# => p,q extremely close => Fermat: n = ((p+q)/2)^2 - ((p-q)/2)^2.  a=ceil(sqrt n), b^2=a^2-n.
import gmpy2
from Crypto.Util.number import long_to_bytes
src=open('output_provided.txt').read()
n=int(src.split('n = ')[1].split()[0])
e=int(src.split('e = ')[1].split()[0])
c=int(src.split('c = ')[1].split()[0])
a=gmpy2.isqrt(n)
if a*a<n: a+=1
b2=a*a-n
b=gmpy2.isqrt(b2)
assert b*b==b2, f"not a square: b2={b2}, b={b}"
p=a+b; q=a-b
assert p*q==n and gmpy2.is_prime(p) and gmpy2.is_prime(q)
print("p bits",p.bit_length(),"q bits",q.bit_length(),"|p-q| bits",(p-q).bit_length())
phi=(p-1)*(q-1)
d=pow(e, -1, phi)
m=pow(c,d,n)
flag=long_to_bytes(m).decode()
print("FLAG:", flag)

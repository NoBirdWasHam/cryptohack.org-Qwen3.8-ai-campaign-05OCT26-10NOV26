#!/usr/bin/env python3
# RSA Backdoor Viability - CryptoHack rsa_backdoor  (REWRITE: solved)
#
# p = (427 s^2 + 1)/4  =>  4p = 1 + 427 s^2, so p is represented by the
# PRINCIPAL form x^2+xy+107y^2 of discriminant -427 (h(-427)=2).
# => p splits PRINCIPALLY in K = Q(sqrt(-427)), hence p splits COMPLETELY in
# the ring class field.  Since h=2 and -427 = (-7)*61 (prime discriminants),
# the ring class field = genus field = K(sqrt(-7)) = K(sqrt(61)).
# Complete splitting => (-7/p) = (61/p) = +1.
#
# For n = p*q:  alpha^((n-1)/2) mod p = (alpha/p) = +1 for alpha in {-7, 61}
# (proof: w=sqrt(alpha) in F_p, w^(n-1) = w^(pq-1) = (w^p)^q / w = w^q/w = 1).
# If (alpha/q) = -1 then alpha^((n-1)/2) = -1 mod q, so
#     gcd(alpha^((n-1)/2) - 1, n) = p.
# Jacobi(-7,n) = -1 and (-7/p)=+1  =>  (-7/q) = -1  =>  guaranteed factor.
import re, sys
from math import gcd
import gmpy2

txt = open("output.txt").read()
d = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", txt)}
n, e, c = d["n"], d["e"], d["c"]

p = None
for a in (-7, 61, -427):
    g = gcd(pow(a, (n - 1) // 2, n) - 1, n)
    print(f"alpha={a}: gcd = {g if g in (1, n) else g.bit_length()} bits")
    if 1 < g < n:
        p = g
        break
assert p is not None and n % p == 0, "no factor found"
q = n // p
print("p =", p)
print("p bits:", p.bit_length(), " q bits:", q.bit_length())
print("p prime:", gmpy2.is_prime(p), " q prime:", gmpy2.is_prime(q))
# verify p has the promised shape: 4p-1 = 427 s^2
t = (4 * p - 1)
s, r = gmpy2.isqrt_rem(t // 427)
print("4p-1 == 427*s^2:", t == 427 * s * s, " s bits:", s.bit_length())

phi = (p - 1) * (q - 1)
dinv = pow(e, -1, phi)
m = pow(c, dinv, n)
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print("flag:", flag.decode(errors="replace"))
open("flag_rsa_backdoor.txt", "w").write(flag.decode())

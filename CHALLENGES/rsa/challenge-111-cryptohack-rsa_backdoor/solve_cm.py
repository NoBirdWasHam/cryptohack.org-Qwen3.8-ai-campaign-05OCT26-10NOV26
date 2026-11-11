#!/usr/bin/env python3
# RSA Backdoor Viability - CryptoHack rsa_backdoor  (CM over Z/n, integer root of H)
#
# p = (427 s^2+1)/4 => p represented by PRINCIPAL form of disc -427 (h=2)
# => p splits completely in the ring class field => H_-427 splits mod p.
# Jacobi(-427,n)=+1 and (-427/p)=+1 => (-427/q)=+1 => H splits mod q TOO.
# => H has INTEGER roots mod n.  For root j0, E: y^2=x^3+Ax+B over Z/n with
# A=3j0/(1728-j0), B=2j0/(1728-j0) reduces mod p to a CM curve with
# #E(F_p) = p+1-t, t=+-1.  If t=+1: n*P = O mod p => some denominator in
# the affine n*P chain is 0 mod p (nonzero mod q) => gcd(den,n)=p.
# If t=-1: twist E^d: y^2=x^3+d^2 A x+d^3 B has #=p.  Try random d.
# n = 7 mod 8 => sqrt(g) = g^((n+1)/4) mod n for QR g.
import re, random, sys
from math import gcd
import gmpy2

txt = open("output.txt").read()
d_ = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", txt)}
n, e, c = d_["n"], d_["e"], d_["c"]

HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

def tsqrt(a, nn):
    x = pow(a, (nn + 1) // 4, nn)
    return x if x * x % nn == a % nn else None

# ---- integer root of H mod n ----
DH = (HB * HB - 4 * HC) % n
sDH = tsqrt(DH, n)
if sDH is None:
    s, dd = 0, n - 1
    while dd % 2 == 0: dd //= 2; s += 1
    z = 2
    while gmpy2.jacobi(z, n) != -1: z += 1
    cc = pow(z, dd, n); x = pow(DH, (dd + 1) // 2, n); t = pow(DH, dd, n); m = s
    while t != 1:
        i, tt = 1, t * t % n
        while tt != 1: tt = tt * tt % n; i += 1
        b2 = pow(cc, 1 << (m - i - 1), n)
        x = x * b2 % n; t = t * b2 * b2 % n; cc = b2 * b2 % n; m = i
    sDH = x
assert sDH * sDH % n == DH
j0 = (sDH - HB) * ((n + 1) // 2) % n
assert (j0 * j0 + HB * j0 + HC) % n == 0, "j0 not a root of H"
print("j0 = integer root of H mod n OK")

ti = pow(1728 - j0, -1, n)
A0 = 3 * j0 % n * ti % n
B0 = 2 * j0 % n * ti % n

class BadDen(Exception):
    def __init__(self, den): self.den = den

def add(P, Q, A, B, nn):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % nn == 0:
            raise BadDen((2 * y1) % nn)          # doubling: P=-P -> O mod p
        den = (2 * y1) % nn
        num = (3 * x1 * x1 + A) % nn
    else:
        den = (x2 - x1) % nn
        num = (y2 - y1) % nn
    try:
        g = pow(den, -1, nn)
    except ValueError:
        raise BadDen(den)
    m = num * g % nn
    x3 = (m * m - x1 - x2) % nn
    y3 = (m * (x1 - x3) - y1) % nn
    return (x3, y3)

def factor_via_cm(seed=12345, trials=60):
    rng = random.Random(seed)
    for trial in range(trials):
        d = 1 if trial == 0 else rng.randrange(2, n)
        d2 = d * d % n
        A = d2 * A0 % n
        B = d2 * d % n * B0 % n
        for _ in range(3):
            x0 = rng.randrange(2, n)
            g = (pow(x0, 3, n) + A * x0 + B) % n
            gg = gcd(g, n)
            if 1 < gg < n: return gg
            if gg != 1 or pow(g, (n - 1) // 2, n) != 1: continue
            y0 = tsqrt(g, n)
            if y0 is None: continue
            P = (x0, y0); R = None; k = n
            try:
                while k:
                    if k & 1: R = add(R, P, A, B, n)
                    P = add(P, P, A, B, n); k >>= 1
            except BadDen as ex:
                f = gcd(ex.den, n)
                if 1 < f < n: return f
            if R is None:
                return None  # n*P = O mod n entirely: no info
    return None

f = factor_via_cm()
if f and 1 < f < n:
    p = f; q = n // p
    assert p * q == n
    print("p bits:", p.bit_length(), "q bits:", q.bit_length(),
          "primes:", gmpy2.is_prime(p), gmpy2.is_prime(q))
    t4 = 4 * p - 1
    s, r = gmpy2.isqrt_rem(t4 // 427)
    print("shape check 4p-1==427*s^2:", t4 == 427 * s * s)
    m = pow(c, pow(e, -1, (p - 1) * (q - 1)), n)
    flag = m.to_bytes((m.bit_length() + 7) // 8, "big").decode()
    print("flag:", flag)
    open("flag_rsa_backdoor.txt", "w").write(flag)
else:
    print("NOT SOLVED by CM-over-Z/n, result:", f)

#!/usr/bin/env python3
# RSA Backdoor Viability - CryptoHack rsa_backdoor
#
# p = (427 s^2+1)/4 => p represented by PRINCIPAL form of disc -427 (h=2)
# => p splits completely in the ring class field, so H_-427 splits mod p.
# Jacobi(-427,n)=+1 and (-427/p)=+1 => (-427/q)=+1 => H splits mod q TOO.
# => H has INTEGER roots mod n.  For such a root j0, E: y^2=x^3+Ax+B over
# Z/n with A=3j0/(1728-j0), B=2j0/(1728-j0) reduces mod p to a CM curve with
# #E(F_p) = p+1-t, t=+-1.  If t=+1: n*P = O mod p => gcd(Z(nP),n)=p.
# If t=-1: twist E^d: y^2=x^3+d^2 A x+d^3 B has #=p.  Try random d.
# n = 7 mod 8 => sqrt(g) = g^((n+1)/4) mod n for QR g.
import re, random, sys
from math import gcd
import gmpy2

sys.setrecursionlimit(100000)

HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

txt = open("output.txt").read()
d_ = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", txt)}
n, e, c = d_["n"], d_["e"], d_["c"]

def tsqrt(a, nn):
    """sqrt for nn = 3 mod 4 (here 7 mod 8): a^((nn+1)/4)."""
    x = pow(a, (nn + 1) // 4, nn)
    return x if x * x % nn == a % nn else None

# ---- integer root of H mod n ----
DH = HB * HB - 4 * HC
sDH = tsqrt(DH % n, n)
if sDH is None:
    # fall back: full Tonelli-Shanks
    s, dd = 0, n - 1
    while dd % 2 == 0: dd //= 2; s += 1
    z = 2
    while gmpy2.jacobi(z, n) != -1: z += 1
    cc = pow(z, dd, n); x = pow(DH % n, (dd + 1) // 2, n); t = pow(DH % n, dd, n); m = s
    while t != 1:
        i, tt = 1, t * t % n
        while tt != 1: tt = tt * tt % n; i += 1
        b2 = pow(cc, 1 << (m - i - 1), n)
        x = x * b2 % n; t = t * b2 * b2 % n; cc = b2 * b2 % n; m = i
    sDH = x
assert sDH * sDH % n == DH % n
inv2 = (n + 1) // 2
j0 = (sDH - HB) * inv2 % n
assert (j0 * j0 + HB * j0 + HC) % n == 0, "j0 not a root of H"
print("j0 root of H mod n OK, bits:", j0.bit_length())

ti = pow(1728 - j0, -1, n)
A0 = 3 * j0 % n * ti % n
B0 = 2 * j0 % n * ti % n

def mul(P, Q, A, B, nn):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % nn == 0: return None
    num = (y2 - y1) % nn; den = (x2 - x1) % nn
    g = pow(den, -1, nn)  # ValueError -> factor
    m = num * g % nn
    x3 = (m * m - x1 - x2) % nn
    y3 = (m * (x1 - x3) - y1) % nn
    return (x3, y3)

def scalar(P, k, A, B, nn):
    R = None
    while k:
        if k & 1: R = mul(R, P, A, B, nn)
        P = mul(P, P, A, B, nn); k >>= 1
    return R

def try_curve(A, B, rng, tries=6):
    for _ in range(tries):
        while True:
            x0 = rng.randrange(2, n)
            g = (x0 * x0 * x0 + A * x0 + B) % n
            gg = gcd(g, n)
            if 1 < gg < n: return gg
            if gg != 1: continue
            if pow(g, (n - 1) // 2, n) != 1: continue
            y0 = tsqrt(g, n)
            if y0 is None: continue
            break
        P = (x0, y0)
        try:
            Q = scalar(P, n, A, B, n)
        except ValueError:
            # non-invertible denominator during n*P: gcd gives factor
            # recompute stepwise to extract it
            return None
        if Q is None:
            return n  # n*P = O mod n (shouldn't happen)
        # Q affine means Z invertible mod n -> no info; but if Z==0 mod p,
        # the inverse would have failed. So success signal is the ValueError.
    return None

def factor_via_cm():
    rng = random.Random(12345)
    for trial in range(40):
        if trial == 0:
            d = 1
        else:
            d = rng.randrange(2, n)
        A = d * d % n * A0 % n
        B = d * d % n * d % n * B0 % n
        for _ in range(4):
            x0 = rng.randrange(2, n)
            g = (pow(x0, 3, n) + A * x0 + B) % n
            gg = gcd(g, n)
            if 1 < gg < n: return gg
            if gg != 1 or pow(g, (n - 1) // 2, n) != 1: continue
            y0 = tsqrt(g, n)
            if y0 is None: continue
            P = (x0, y0)
            # scalar multiply, catching non-invertible denominators
            R = None
            try:
                k = n
                while k:
                    if k & 1: R = mul(R, P, A, B, n)
                    P = mul(P, P, A, B, n); k >>= 1
            except ValueError:
                # a denominator was 0 mod p, nonzero mod q -> gcd = p
                # recompute the failing step to recover the denominator
                return recover(R, P, A, B, n)
            if R is None:
                f = n
                return f
    return None

def recover(R, P, A, B, nn):
    # brute: redo last doubling/addition chain is messy; instead gcd of
    # (x_P - x_R) etc. Simplest: try gcds of coordinate differences.
    cands = []
    if R is not None:
        x1, y1 = R; x2, y2 = P
        cands += [x2 - x1, y2 - y1, x2 + x1]
    for v in cands:
        f = gcd(v % nn, nn)
        if 1 < f < nn: return f
    return None

f = factor_via_cm()
print("factor result:", "found" if f and 1 < f < n else f)
if f and 1 < f < n:
    p = f; q = n // p
    print("p bits:", p.bit_length(), "q bits:", q.bit_length(),
          "primes:", gmpy2.is_prime(p), gmpy2.is_prime(q))
    m = pow(c, pow(e, -1, (p - 1) * (q - 1)), n)
    flag = m.to_bytes((m.bit_length() + 7) // 8, "big").decode()
    print("flag:", flag)
    open("flag_rsa_backdoor.txt", "w").write(flag)
else:
    print("NOT SOLVED by CM-over-Z/n")

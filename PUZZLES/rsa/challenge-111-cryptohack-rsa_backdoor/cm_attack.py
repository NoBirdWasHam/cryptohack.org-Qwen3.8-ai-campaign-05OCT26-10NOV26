#!/usr/bin/env python3
"""
RSA Backdoor Viability - CryptoHack rsa_backdoor

p = (427 s^2 + 1)/4  =>  4p = 1 + 427 s^2, so p is represented by the
PRINCIPAL form [1,1,107] of discriminant -427 (h(-427)=2).  For the CM
elliptic curves whose j-invariant is a root of the Hilbert class polynomial
H_{-427}, the trace of Frobenius over F_p is t = 2a+b = 1 (principal
representation p = a^2+ab+107b^2, a=(1-s)/2, b=s), i.e. #E(F_p) = p.

Build E over R = (Z/n)[x]/(H(x)).  Mod p:  R/pR = F_p x F_p and BOTH curve
components have order p, so for any point P in E(R):  n*P = O mod p, the
Z-coordinate of n*P is 0 mod p, and gcd(coeffs of Z, n) = p.
(Atkin-Morain style factoring via complex multiplication.)

Point on E(R): pick x0 in R, g = x0^3+A x0+B.  If Norm(g) is a QR mod n then
g is a square in both components; sqrt via Tonelli-Shanks on the norm:
   x^2 = Norm(g) mod n,  y = g * x / Norm(g)   =>  y*y = g   (identity in R).
"""
import sys, random
from math import gcd
from sympy import jacobi_symbol

sys.setrecursionlimit(100000)   # statement hint

# H_{-427}(x) = x^2 + HB x + HC   (gp: polclass(-427))
HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

# ---------------- ring R = (Z/n)[x]/(x^2 + HB x + HC) ----------------
def radd(u, v, n): return ((u[0]+v[0]) % n, (u[1]+v[1]) % n)
def rsub(u, v, n): return ((u[0]-v[0]) % n, (u[1]-v[1]) % n)
def rmul(u, v, n):
    a, b = u; c, d = v
    ad_bc = (a*d + b*c) % n
    bd = (b*d) % n
    return ((a*c - HB*ad_bc + HC*bd) % n, (ad_bc - HB*bd) % n)
def rsq(u, n): return rmul(u, u, n)
def rnorm(u, n):
    a, b = u
    return (a*a - a*b*HB + b*b*HC) % n     # (a+b x)(a+b x'), x+x'=-HB, xx'=HC
def rinv(u, n):
    a, b = u
    N = rnorm(u, n)
    g = pow(N, -1, n)                      # may raise -> gcd(N,n) is a factor
    return ((a - b*HB) * g % n, (-b) * g % n)

def tsqrt(a, n):
    """sqrt of a mod odd n, a a QR mod n, gcd(a,n)=1 (Tonelli-Shanks)."""
    if a == 0: return 0
    s, d = 0, n - 1
    while d % 2 == 0: d //= 2; s += 1
    z = 2
    while jacobi_symbol(z, n) != -1: z += 1
    c = pow(z, d, n)
    x = pow(a, (d + 1) // 2, n)
    t = pow(a, d, n)
    m = s
    while t != 1:
        i, tt = 1, t * t % n
        while tt != 1:
            tt = tt * tt % n; i += 1
        b2 = pow(c, 1 << (m - i - 1), n)
        x = x * b2 % n; t = t * b2 * b2 % n; c = b2 * b2 % n; m = i
    return x

# ---------------- E/R : y^2 = x^3 + A x + B,  j = x ----------------
class CMCurve:
    def __init__(self, n):
        self.n = n
        j = (0, 1)
        ti = rinv(rsub((1728, 0), j, n), n)
        jti = rmul(j, ti, n)
        self.A = rmul((3, 0), jti, n)
        self.B = rmul((2, 0), jti, n)

    def on_curve(self, P):
        X, Y, Z = P; n = self.n
        Z2 = rsq((Z, 0), n)
        lhs = rsq((Y, 0), n)
        rhs = radd(rmul(rsq((X, 0), n), (Z, 0), n),
                   radd(rmul(self.A, rmul((X, 0), Z2, n), n),
                        rmul(self.B, Z2, n), n), n)
        return lhs == rhs

    def add(self, P, Q):
        """P1+Q2 on weighted projective (X:Y:Z), x=X/Z, y=Y/Z.
        M = Y2 Z1 - Y1 Z2 ; N = X2 Z1 - X1 Z2
        Z3 = N^2 (Z1+Z2) - M^2
        X3 = M N (X1 Z2 + X2 Z1) - M^3 - N^2 Y1 Z2
        Y3 = M N (Y1 Z2 + Y2 Z1) - M^3 - N^2 Y1 Z2 - N Z3"""
        n = self.n
        X1, Y1, Z1 = P; X2, Y2, Z2 = Q
        M = rsub(rmul((Y2, 0), (Z1, 0), n), rmul((Y1, 0), (Z2, 0), n), n)
        N = rsub(rmul((X2, 0), (Z1, 0), n), rmul((X1, 0), (Z2, 0), n), n)
        N2 = rsq(N, n); M2 = rsq(M, n); M3 = rmul(M2, M, n)
        Z3 = rsub(rmul(N2, radd((Z1, 0), (Z2, 0), n), n), M2, n)
        t = rsub(rmul(M, N, n), N2, n)                      # MN - N^2
        X3 = rsub(rmul(t, radd(rmul((X1, 0), (Z2, 0), n),
                               rmul((X2, 0), (Z1, 0), n), n), n),
                  rmul(N2, rmul((Y1, 0), (Z2, 0), n), n), n)
        Y3 = rsub(rmul(t, radd(rmul((Y1, 0), (Z2, 0), n),
                               rmul((Y2, 0), (Z1, 0), n), n), n),
                  rmul(N, Z3, n), n)
        return (X3, Y3, Z3)

    def mul(self, P, k):
        R = (0, 1, 0)   # O
        while k:
            if k & 1: R = self.add(R, P)
            P = self.add(P, P); k >>= 1
        return R

def find_point(E, n, rng):
    """random x0 in R with Norm(x0^3+A x0+B) a QR mod n; return P on E(R)."""
    while True:
        x0 = (rng.randrange(n), rng.randrange(n))
        g = radd(radd(rmul(rsq(x0, n), x0, n), rmul(E.A, x0, n), n), (E.B[0], E.B[1]), n)
        N = rnorm(g, n)
        if gcd(N, n) != 1:
            raise ZeroDivisionError("gcd(N,n)=%d" % gcd(N, n))
        if pow(N, (n - 1) // 2, n) != 1:
            continue
        xs = tsqrt(N, n)
        y = rmul(g, (xs, 0), n)
        y = rmul(y, rinv((N, 0), n), n)
        assert rmul(y, y, n) == g
        P = (x0, y, (1, 0))
        assert E.on_curve(P)
        return P

def factor(n, seed=1):
    rng = random.Random(seed)
    E = CMCurve(n)
    P = find_point(E, n, rng)
    R = E.mul(P, n)
    for z in R[2]:
        f = gcd(z, n)
        if 1 < f < n:
            return f
    return None

# ----------------------------- self-test --------------------------------
def make_instance(bits_p_lo, bits_p_hi, qbits, seed):
    from Crypto.Util.number import getPrime, isPrime
    rng = random.Random(seed)
    while True:
        s = rng.randrange(2**bits_p_lo, 2**bits_p_hi)
        t = 427*s*s + 1
        if t % 4 == 0 and isPrime(t//4):
            p = t//4; break
    q = getPrime(qbits)
    return p, q, p*q

if __name__ == "__main__":
    import time
    print("self-test 128-bit p, 160-bit q ...")
    t0 = time.time()
    p, q, n = make_instance(62, 64, 160, 42)
    f = factor(n, seed=7)
    print("factor found:", f, "correct:", f in (p, q), "time %.1fs" % (time.time()-t0))

# Coppersmith unknown-modulus (beta=1/2, d=1): root of x+Yc mod p|N, r < Xb.
import math
import sympy
from sympy import ZZ, QQ
from fpylll import IntegerMatrix, LLL

def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out

def coppersmith_factor(N, Yc, Xb, m=8):
    """return list of candidate factors of N"""
    f = [Yc % N, 1]
    fm = [1]
    for _ in range(m):
        fm = poly_mul(fm, f)
    dim = 2 * m
    B = IntegerMatrix(dim, dim)
    fpow = [1]
    for i in range(m):
        for k, c in enumerate(fpow):
            B[i, k] = (N ** (m - i)) * c * (Xb ** k)
        fpow = poly_mul(fpow, f)
    for i in range(m):
        for k, c in enumerate(fm):
            if k + i < dim:
                B[m + i, k + i] = c * (Xb ** (k + i))
    LLL.reduction(B)
    x = sympy.symbols("x")
    cands = []
    for ri in range(dim):
        coeffs = [int(v) for v in B[ri]]
        if not any(coeffs):
            continue
        d = max(i for i, c in enumerate(coeffs) if c)
        P = sum(sympy.Integer(c) * (Xb ** (d - i)) * x ** i for i, c in enumerate(coeffs))
        fac = sympy.factor(P.as_expr(), domain=ZZ)
        parts = fac.as_ordered_factors() if fac.is_Mul else [fac]
        for part in parts:
            pe = sympy.Poly(part, x, domain=ZZ)
            if pe.degree() == 1:
                a1, a0 = pe.nth(1), pe.nth(0)
                if a0 % a1 == 0:
                    rv = int(-a0 // a1)
                    cands.append(math.gcd(N, (Yc + rv) % N))
        if any(1 < c < N for c in cands):
            break
    return [c for c in cands if 1 < c < N], 1

if __name__ == "__main__":
    import random, gmpy2
    random.seed(2)
    p = int(gmpy2.next_prime((1 << 1023) | 7))
    q = int(gmpy2.next_prime((1 << 1024) - 33))
    N = p * q
    r_true = random.randrange(1 << 127)
    j = random.randrange(1 << 1020, 1 << 1024)
    Yc = (j * p - r_true) % N
    facs, deg = coppersmith_factor(N, Yc, 1 << 130, m=8)
    print("gcd degree:", deg, "factors:", [f == p or f == q for f in facs], "FACTORED:", (p in facs or q in facs))

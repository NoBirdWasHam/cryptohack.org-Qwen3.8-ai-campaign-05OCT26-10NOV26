import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy
from sympy import ZZ
from cop3 import coppersmith_factor, poly_mul
from fpylll import IntegerMatrix, LLL

random.seed(2)
p = int(sympy.nextprime((1 << 1023) | 7))
q = int(sympy.nextprime((1 << 1024) - 33))
N = p * q
r_true = random.randrange(1 << 127)
j = random.randrange(1 << 1020, 1 << 1024)
Yc = (j * p - r_true) % N
Xb = 1 << 130
m = 8
f = [Yc, 1]
fm = [1]
for _ in range(m): fm = poly_mul(fm, f)
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
for ri in range(3):
    coeffs = [int(v) for v in B[ri]]
    d = max(i for i, c in enumerate(coeffs) if c)
    P = sum(sympy.Integer(c) * (Xb ** (d - i)) * x ** i for i, c in enumerate(coeffs))
    fac = sympy.factor(P, domain=ZZ)
    print("row", ri, "degree", d, "factor:", fac.as_expr().as_ordered_factors() if fac.is_Mul else fac)
    # check linear factor
    for part in (fac.as_ordered_factors() if fac.is_Mul else [fac]):
        pe = sympy.Poly(part, x, domain=ZZ)
        if pe.degree() == 1:
            r = -pe.nth(0) // pe.nth(1)
            print("   linear root:", r, "== r_true?", r == r_true, "gcd:", math.gcd(N, (Yc + int(r)) % N) in (p, q))

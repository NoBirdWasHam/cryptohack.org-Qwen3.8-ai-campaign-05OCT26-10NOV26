import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cop2 import poly_mul
from fpylll import IntegerMatrix, LLL
import random, gmpy2, math

random.seed(2)
p = int(gmpy2.next_prime((1 << 1023) | 7))
q = int(gmpy2.next_prime((1 << 1024) - 33))
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
z0 = r_true / Xb
for ri in range(dim):
    coeffs = [int(v) for v in B[ri]]
    if not any(coeffs): continue
    norm = math.isqrt(sum(c*c for c in coeffs))
    val = sum(c * (r_true ** i) * (Xb ** (dim - 1 - i)) for i, c in enumerate(coeffs))
    # G(r) should be 0 mod p^m for lattice vectors? check mod p
    valp = val % p
    print(ri, "norm_bits", norm.bit_length(), "G(r)%p==0:", valp == 0, "G(r) bits", abs(val).bit_length())

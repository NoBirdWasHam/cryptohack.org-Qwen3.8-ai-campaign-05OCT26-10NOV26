import solve_coppersmith_port as S
import math, random
from sympy import isprime
random.seed(1234)
def gp(b):
    while True:
        c = random.getrandbits(b) | (1 << (b-1)) | 1
        if isprime(c): return c
p,q = gp(512), gp(512)
n = p*q; D = 63**14
hint = math.isqrt(D*D*p) + math.isqrt(D*D*q)
pAs = S.p_approx_from_hint(hint, D, n)
for i,a in enumerate(pAs):
    print(i, "bits", a.bit_length(), "|p-a|=", (p-a).bit_length(), "|q-a|=", (q-a).bit_length(), "pA+pAq-n", ((p-a)*(q-a)).bit_length())
pr, r = S.factor_from_approx(n, pAs[0], 2**180)
print("returned factor == p?", pr==p, "== q?", pr==q)
print("root bits:", r.bit_length() if r else None, " p - pAs0 bits:", (p-pAs[0]).bit_length())

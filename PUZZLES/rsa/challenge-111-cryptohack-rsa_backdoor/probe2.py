import re, gmpy2
from math import gcd
txt = open("output.txt").read()
d = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", txt)}
n, e, c = d["n"], d["e"], d["c"]
print("n bits:", n.bit_length())
r = gmpy2.isqrt(n)
print("is square:", r*r == n)
print("n mod 427:", n % 427, " q mod 427 should be 4n mod 427 =", (4*n) % 427)
print("n mod 8:", n % 8)
# Jacobi symbols
for a in (-7, 61, -427, -1, 2, 3, 5, 7, 61, 427):
    print(f"Jacobi({a},n) =", gmpy2.jacobi(a, n))

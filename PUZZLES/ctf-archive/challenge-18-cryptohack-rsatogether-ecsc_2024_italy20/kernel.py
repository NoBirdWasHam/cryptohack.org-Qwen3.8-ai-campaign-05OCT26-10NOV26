# Exact left-kernel of the 101x100 staircase A[k][j] = k^j (j<=min(k,99)), k=1..101.
# w (integers, dim-1) with sum_k w_k k^j = 0 for j=0..99. Save as kernel.json
import json, time, sys
sys.set_int_max_str_digits(10**6)
from sympy import Matrix
from math import gcd
from functools import reduce

t0 = time.time()
rows = list(range(1, 102))          # k = 1..101
cols = list(range(100))             # j = 0..99
A = Matrix([[ (k**j if j <= min(k, 99) else 0) for j in cols] for k in rows])
# exact left kernel via nullspace of A^T (dim 1)
ns = A.T.nullspace()
print("nullspace dim:", len(ns))
assert len(ns) == 1
from sympy import Rational
Lc = 1
for v in ns[0]:
    Lc = Lc * v.q // gcd(Lc, v.q)
w = [int(v * Lc) for v in ns[0]]
g = reduce(gcd, [abs(v) for v in w])
w = [v // g for v in w]
ok = all(sum(w[k-1] * (k**j) for k in range(max(j,1), 102)) == 0 for j in range(100))
print("kernel exact ok:", ok, "time:", round(time.time()-t0, 1))
print("w bits max:", max(abs(v).bit_length() for v in w))
L = 1
for i in range(2, 103):
    L = L * i // gcd(L, i)
print("L bits:", L.bit_length())
mu = []
for k in range(1, 102):
    beta = (-1)**(k-1) * (k+1)
    assert (L * w[k-1]) % beta == 0
    mu.append((L * w[k-1]) // beta)
print("mu bits max:", max(abs(v).bit_length() for v in mu))
json.dump({"w": [str(v) for v in w], "mu": [str(v) for v in mu], "L": str(L)}, open("kernel.json", "w"))
print("saved kernel.json")

import random, time, math

import fpylll
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam

random.seed(42)
n = 40
a = [random.randint(2**60, 2**62 - 1) for _ in range(n)]
x = [random.randint(0, 1) for _ in range(n)]
pop = sum(x)
t = sum(xi * ai for xi, ai in zip(x, a))
print("n", n, "pop", pop, "t bits", t.bit_length(), "a bits max/min", max(a).bit_length(), min(a).bit_length())


def scan(R, n, a, t, tag):
    found = []
    for i in range(R.nrows):
        last = int(R[i, n])
        if last != 0:
            continue
        xs = [int(R[i, j]) for j in range(n)]
        if all(e in (0, 1) for e in xs):
            if sum(e * w for e, w in zip(xs, a)) == t:
                found.append((i, xs))
    print(tag, "candidates with 0/1 & dot==t:", len(found))
    return found


def clos(n, a, t, N):
    B = IntegerMatrix(n + 1, n + 1)
    for i in range(n):
        B[i, i] = 1
        B[i, n] = N * a[i]
    B[n, n] = N * t
    return B


N = 1 << (n // 2)
B = clos(n, a, t, N)
t0 = time.time()
R = lll_reduction(B)
print("LLL time", round(time.time() - t0, 2))
f = scan(R, n, a, t, "(CLOS N=2^n/2)")
if f:
    print("   match equals x?", f[0][1] == x, "row", f[0][0])
else:
    for i in range(6):
        last = int(R[i, n])
        xs = [int(R[i, j]) for j in range(n)]
        nrm = sum(e * e for e in xs) + last * last
        print("   row", i, "last:", last, "first8:", xs[:8], "norm2:", nrm)
    t0 = time.time()
    Rb = bkz_reduction(B, BKZParam(50))
    print("BKZ(50) time", round(time.time() - t0, 2))
    f = scan(Rb, n, a, t, "(CLOS BKZ50)")
    if f:
        print("   match equals x?", f[0][1] == x, "row", f[0][0])

N2 = math.isqrt(n) + 2
B2 = clos(n, a, t, N2)
t0 = time.time()
R2 = lll_reduction(B2)
print("LLL(N=sqrt) time", round(time.time() - t0, 2))
f = scan(R2, n, a, t, "(CLOS N=sqrt)")
if f:
    print("   match equals x?", f[0][1] == x)

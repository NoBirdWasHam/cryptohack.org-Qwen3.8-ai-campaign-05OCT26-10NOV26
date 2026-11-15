# tg8: cubic/quartic chars on 2/3/4/9-division data; determinacy vs x mod 2,3,4,9. p=1289.
from collections import defaultdict
from functools import reduce
p = 1289
rows = []
for ln in open("small3.out"):
    if ln.startswith("ROW"):
        _, x, a4, a6 = ln.split()
        rows.append((int(x) % 36, int(a4) % p, int(a6) % p))

def jac(z): return pow(z % p, (p - 1) // 2, p)
def q4(z): return pow(z % p, (p - 1) // 4, p)
def mulF(x, y): return ((x[0]*y[0] - 3*x[1]*y[1]) % p, (x[0]*y[1] + x[1]*y[0]) % p)
def powF(x, e):
    r = (1, 0)
    while e:
        if e & 1: r = mulF(r, x)
        x = mulF(x, x); e >>= 1
    return r
def q3F(z): return powF(z, (p*p - 1) // 3)
def q4F(z): return powF(z, (p*p - 1) // 4)
w3 = ((p - 1) // 2, (p + 1) // 2)
assert powF(w3, 3) == (1, 0)

_SQ = {}
for _r in range(p): _SQ[_r*_r % p] = _r
def sqrt_p(v): return _SQ.get(v % p)

def polymod(A, B):
    A = A[:]
    lbI = pow(B[-1], p-2, p)
    while len(A) >= len(B):
        f = A[-1]*lbI % p
        for i in range(len(B)): A[len(A)-len(B)+i] = (A[len(A)-len(B)+i] - f*B[i]) % p
        A.pop()
        while A and not A[-1] and len(A) >= len(B): A.pop()
    return A
def pres(A, B):
    r_ = 1
    while len(B) > 1:
        if not any(B): return 0
        M = len(A) - len(B); N = len(B) - 1
        r_ = r_ * pow(B[-1], M, p) % p * pow(-1, M*N, p) % p
        A = polymod(A, B); A, B = B, A
    return r_ % p
def discf(c):
    n = len(c) - 1
    d = [((n-i)*c[i]) % p for i in range(n)]
    return pres(c, d) % p

def divpoly_at(n, r, a4, a6):
    y2 = (r**3 + a4*r + a6) % p
    a_, b_, c_ = 1, (2*r) % p, (3*r**4 + 6*a4*r**2 + 12*a6*r - a4*a4) % p
    if n == 1: return 1 % p
    if n == 2: return b_
    if n == 3: return c_
    d_ = (4*((r**6 + 5*a4*r**4 + 20*a6*r**3 - 5*a4*a4*r*r - 4*a4*a6*r - 8*a6*a6 - a4**3) % p)) % p
    if n == 4: return d_
    for k in range(5, n+1):
        e_ = (4*a4*b_*d_ + 6*r*b_*d_*d_ - c_*c_*c_*c_) % p
        if k & 1: e_ = e_ * pow(2*y2, p-2, p) % p
        a_, b_, c_, d_ = b_, c_, d_, e_
    return d_

def psi4v(r, a4, a6):
    return (r**6 + 5*a4*r**4 + 20*a6*r**3 - 5*a4*a4*r*r - 4*a4*a6*r - 8*a6*a6 - a4**3) % p

vals = {}
def put(nm, x, v): vals.setdefault(nm, {})[x] = v

for x, a4, a6 in rows:
    Dv = (-16 * (4*a4**3 + 27*a6**2)) % p
    put("q4_D", x, q4(Dv))
    put("jac_D", x, jac(Dv))
    rs = [r for r in range(p) if (3*r**4 + 6*a4*r**2 + 12*a6*r - a4*a4) % p == 0]
    put("npsi3_Fp", x, len(rs))
    dq = discf([3, 0, (6*a4) % p, (12*a6) % p, (-a4*a4) % p])
    put("q4_Disc3", x, q4(dq)); put("jac_Disc3", x, jac(dq))
    xT = xS = None
    for r in rs:
        f = (r**3 + a4*r + a6) % p
        if jac(f) == 1: xT = r
        elif f: xS = r
    if xS is not None:
        fS = (xS**3 + a4*xS + a6) % p
        b = sqrt_p(-fS * pow(3, p-2, p))
        if b is not None:
            yS = (0, b)
            put("c3_yS", x, q3F(yS)); put("q4F_yS", x, q4F(yS))
    if xT is not None and xS is not None:
        put("q4_xTmxS", x, q4(xT - xS)); put("jac_xTmxS", x, jac(xT - xS))
    rs6 = [r for r in range(p) if psi4v(r, a4, a6) == 0]
    put("npsi4_Fp", x, len(rs6))
    if rs6: put("q4_prodpsi4", x, q4(reduce(lambda A,B_: A*B_ % p, rs6, 1)))
    put("q4_Disc4", x, q4(discf([1,0,(5*a4)%p,(20*a6)%p,(-5*a4*a4)%p,(-4*a4*a6)%p,(-8*a6*a6-a4**3)%p])))
    rs9 = [r for r in range(p) if divpoly_at(9, r, a4, a6) == 0 and divpoly_at(3, r, a4, a6) != 0 and (r**3 + a4*r + a6) % p != 0]
    put("npsi9_exact_Fp", x, len(rs9))
    if rs9:
        pr9 = reduce(lambda A,B_: A*B_ % p, rs9, 1)
        put("q4_prodpsi9", x, q4(pr9)); put("jac_prodpsi9", x, jac(pr9))

def test(nm):
    v = vals[nm]; xs = sorted(v)
    if any(v[x] is None for x in xs): return
    for m in (2,3,4,9):
        t = defaultdict(set)
        for x in xs: t[x % m].add(v[x])
        if all(len(s) == 1 for s in t.values()) and len(set(map(str, t.values()))) > 1:
            print(f"*** {nm}: DETERMINED by x mod {m}: {sorted((k, next(iter(s))) for k,s in t.items())}")

for nm in sorted(vals): test(nm)
print("sample:", {nm: dict(list(vals[nm].items())[:4]) for nm in vals})
print("done")

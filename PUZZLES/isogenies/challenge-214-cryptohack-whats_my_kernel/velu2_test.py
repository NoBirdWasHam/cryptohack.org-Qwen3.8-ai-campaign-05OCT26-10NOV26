#!/usr/bin/env python
"""Systematic verification of the Vélu 2-isogeny machinery over F_97.

Ground truth: x'(P) computed by DIRECT addition: x + x(P+R) + x(P-2R... x(P-R)) - 2 x_R.
Then fit the closed forms and check consistency + homomorphism.
"""
p = 97
# E: y^2 = x^3 + ax + b; find a 2-torsion point. Try a = -2, b = 3: roots of x^3-2x+3?
# Simpler: force a root: take E: y^2 = x^3 + a x + b with b = -(r^3 + a r) for chosen r -> (r,0) 2-torsion.
r = 7
a = -2 % p
b = (-(r**3 + a * r)) % p
print(f"E: y^2 = x^3 + {a} x + {b} (mod {p}), forced 2-torsion R = ({r}, 0)")

def add(P, Q, aa, bb):
    if P is None: return Q
    if Q is None: return P
    x1, y1, x2, y2 = P
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3*x1*x1 + aa) * pow(2*y1, p-2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p-2, p) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def f(x):  return (x*x*x + a*x + b) % p
def fp(x): return (3*x*x + a) % p

u, v = r, 0
R = (u, 0)
# sanity: 2R = O
assert add(R, R, a, b) is None, "R not order 2"

pts = [(x, y) for x in range(p) for y in range(p) if (y*y - f(x)) % p == 0]
print("domain affine points:", len(pts), " (|E| =", len(pts)+1, ")")
assert (len(pts) + 1) % 2 == 0

# ground-truth x-map by direct addition
def X_true(P):
    x = P[0]
    PR = add(P, R, a, b)
    if PR is None:  # P = R (kernel) or P+R = O (P = R)
        return None
    return (P[0] + PR[0] + PR[0] - 2*u) % p   # P-R = P+R since R=-R... careful:
# wait: P - R = P + (-R) = P + R (R = -R, 2-torsion). So x(P-R) = x(P+R).
# Vélu: x' = x + (x(P+R) - x_R) + (x(P-R) - x_R) = x + 2 x(P+R) - 2 x_R
def Xof(P):
    PR = add(P, R, a, b)
    if PR is None: return None
    return (P[0] + 2*PR[0] - 2*u) % p

# closed form: 2(v^2 + f(x))/(u-x)^2 - x - 4u
def X_closed(x):
    d = (u - x) % p
    if d == 0: return None
    return (2*f(x)*pow(d*d, p-2, p) - x - 4*u) % p

bad = 0
for P in pts:
    xt = Xof(P)
    xc = X_closed(P[0])
    if xt != xc:
        bad += 1
        if bad < 5: print("MISMATCH at", P, xt, xc)
print("closed x-map mismatches:", bad, "/", len(pts))

# y-map: fit y'^2 = k2 * y^2 * (dx'/dx)^2 = X^3 + ap X + bp
# dx'/dx of closed form: [2 f'(x) d + 4 f(x)]/d^3 - 1, d = u-x
def dxdx(x):
    d = (u - x) % p
    num = (2*fp(x)*d + 4*f(x)) % p
    return (num*pow(pow(d, 3, p), p-2, p) - 1) % p

rows = []
for P in pts:
    x, y = P
    X = X_closed(x)
    if X is None: continue
    rows.append((P, X, dxdx(x)))

# unknowns k2, ap, bp:  k2 * y^2 * d^2 = X^3 + ap X + bp
# use 3 points with distinct X
distinct = []
seen = set()
for P, X, d in rows:
    if X not in seen:
        seen.add(X); distinct.append((P, X, d))
(P1, X1, d1), (P2, X2, d2), (P3, X3, d3) = distinct[0], distinct[1], distinct[2]
A1 = (P1[1]**2 * d1*d1) % p; A2 = (P2[1]**2 * d2*d2) % p; A3 = (P3[1]**2 * d3*d3) % p
W1 = X1**3 % p; W2 = X2**3 % p; W3 = X3**3 % p
# k2*A1 - W1 = ap X1 + bp ; etc.
den12 = (X1 - X2) % p
solutions = []
for k2 in range(p):
    # ap from eq1 - eq2: k2(A1-A2) - (W1-W2) = ap (X1-X2)
    ap = ((k2*(A1-A2) % p - (W1-W2)) * pow(den12, p-2, p)) % p
    bp = (k2*A1 - W1 - ap*X1) % p
    if (k2*A3 - W3 - ap*X3) % p == 0:
        solutions.append((k2, ap, bp))
print("fits (k2, ap, bp):", solutions)

if solutions:
    k2, ap, bp = solutions[0]
    bad = 0
    for P, X, d in rows:
        lhs = (k2 * P[1]*P[1] % p * d*d) % p
        rhs = (X*X*X + ap*X + bp) % p
        if lhs != rhs: bad += 1
    print("y^2-identity off rows:", bad, "/", len(rows))
    # homomorphism: need k (not k2): y' = y*d/k, k^2 = k2
    # find k: sqrt(k2)
    k = None
    for cand in range(p):
        if cand*cand % p == k2: k = cand; break
    print("k =", k)
    cinv = pow(k, p-2, p)
    def phi(P):
        if P is None: return None
        x, y = P
        X = X_closed(x)
        if X is None: return None   # kernel point
        return (X, (y * dxdx(x) % p) * cinv % p)
    import random; random.seed(7)
    ho = 0; n = 0
    for _ in range(500):
        P = random.choice(pts); Q = random.choice(pts)
        S = add(P, Q, a, b)
        Lp = phi(S)
        Rp = add(phi(P), phi(Q), ap, bp)
        n += 1
        if (Lp is None and Rp is None) or (Lp is not None and Rp is not None and Lp == Rp):
            ho += 1
    print(f"HOMOLOGY exact: {ho}/{n}")
    print("codomain: y^2 = x^3 +", ap, "x +", bp, "(mod", p, ")")

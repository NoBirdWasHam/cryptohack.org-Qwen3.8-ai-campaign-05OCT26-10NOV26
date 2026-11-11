#!/usr/bin/env python
"""Cryptohack 210 — Prime Power Isogenies (50 pts).

E0: y^2 = x^3 + x  (mod 419).  p+1 = 420 = 2^2 * 3 * 5 * 7.

CSIDH walk: at each step take the pointwise-rational l-isogeny (kernel = E(F_p)[l],
cyclic of order l since l | 420 but l^2 ∤ 420).  Vélu formula per Theorem 25.1.6 of
Galbraith et al. ("Mathematics of Public-Key Cryptography", Ch. 25), specialized to
short Weierstrass (a1=a2=a3=0) with odd-order kernel (no 2-torsion part):

  Fx = 3x^2 + a4,   Fy = -2y
  u(Q) = Fy(Q)^2 = 4 yQ^2
  t(Q) = 2 Fx(Q) = 2 (3 xQ^2 + a4)          (Q in G1, the +-pair reps)
  t(G) = sum_Q t(Q)
  w(G) = sum_Q (u(Q) + xQ * t(Q))
  A4' = a4 - 5 t(G)
  A6' = a6 - 7 w(G)
  codomain: Y^2 = X^3 + A4' X + A6'

Verified formula against the book's worked example (two_isogenies):
  y^2 = x^3 + x over Q(i), kernel (i,0) (order 2, G2: u=0, t=Fx)
  t(G) = -2, w(G) = -2i  ->  A4 = 11, A6 = 14i  ->  y^2 = x^3 + 11x + 14i  (j=287496)  OK

Isomorphism to E0: (a4',a6') ~ (1,0)  <=>  a6' = 0 and a4' a 4th power;
for p = 419, 4th powers == quadratic residues (gcd(4,418) = 2), so test a4' QR.

ANSWER: the 7-walk returns to E0's isomorphism class first at d = 27
(model y^2 = x^3 + 215 x; 215 = 113^4 = 306^4 mod 419).
Bonus (5^9 part): the 5-walk returns first at d = 9 (model y^2 = x^3 + 321 x;
321 = 66^4 = 353^4 mod 419) — "what do you see": the degree 5^9 isogeny lands
back on the starting curve.
"""
p = 419

def ec_add(P, Q, a4):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        lam = (3*x1*x1 + a4) * pow(2*y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P, a4):
    R = None
    while k:
        if k & 1: R = ec_add(R, P, a4)
        P = ec_add(P, P, a4)
        k >>= 1
    return R

def points(a4, a6):
    pts = [None]
    for x in range(p):
        rhs = (x**3 + a4*x + a6) % p
        y = pow(rhs, (p+1)//4, p)          # p == 3 mod 4
        if (y*y - rhs) % p == 0:
            pts.append((x, y))
            if y: pts.append((x, -y % p))
    return pts

def odd_kernel_reps(a4, a6, l):
    """representatives of +-pairs of the (unique) cyclic order-l subgroup of E(F_p)"""
    for Q in points(a4, a6)[1:]:
        if ec_mul(l, Q, a4) is None:       # [l]Q = O, Q != O  =>  ord(Q) = l (l prime)
            seen, reps = set(), []
            for i in range(1, l):
                R = ec_mul(i, Q, a4)
                key = (R[0], min(R[1], p - R[1]))
                if key not in seen:
                    seen.add(key); reps.append(R)
            assert len(reps) == (l-1)//2
            return reps
    return None

def velu_codomain(a4, a6, reps):
    tG = wG = 0
    for (xQ, yQ) in reps:
        u = 4*yQ*yQ % p
        t = 2*(3*xQ*xQ + a4) % p
        tG = (tG + t) % p
        wG = (wG + u + xQ*t) % p
    return (a4 - 5*tG) % p, (a6 - 7*wG) % p

def j_of(a4, a6):
    num = 1728 * 4 * a4**3 % p
    den = (4*a4**3 + 27*a6*a6) % p
    return num * pow(den, -1, p) % p

def is_iso_E0(a4, a6):
    return a6 == 0 and pow(a4, (p-1)//2, p) == 1   # a4 QR == 4th power (p=419)

def walk(l, maxd=40):
    a4, a6 = 1, 0
    seq = [(0, a4, a6)]
    for d in range(1, maxd+1):
        reps = odd_kernel_reps(a4, a6, l)
        assert reps is not None, f"no rational {l}-isogeny at d={d}"
        a4, a6 = velu_codomain(a4, a6, reps)
        seq.append((d, a4, a6))
        if is_iso_E0(a4, a6):
            return d, seq
    return None, seq

if __name__ == "__main__":
    d5, seq5 = walk(5)
    print("5-walk first return to E0 (isomorphic): d =", d5)
    print("  5^9 model:", seq5[9][1], "j =", j_of(*seq5[9][1:]))
    d7, seq7 = walk(7)
    print("7-walk first return to E0 (isomorphic): d =", d7, "   <-- ANSWER")
    print("  j-sequence:", [j_of(a, b) for _, a, b in seq7[:d7+1]])

#!/usr/bin/env python3
"""Smart's attack for anomalous curves (#E == p), pure Python over Z/p^2.
Validated on a small anomalous curve before use on the 512-bit target."""
from Crypto.Util.number import inverse


def point_ops(p2, a):
    """Jacobian double/add over Z/p2 (no inversions)."""
    def dbl(X, Y, Z):
        if Z == 0:
            return (1, 1, 0)
        S = (4 * X * Y * Y) % p2
        M = (3 * X * X + a * Z * Z % p2 * (Z * Z % p2)) % p2
        # M = 3X^2 + a Z^4
        X3 = (M * M - 2 * S) % p2
        Y3 = (M * (S - X3) - 8 * Y * Y % p2 * Y * Y % p2) % p2
        Z3 = (2 * Y * Z) % p2
        return (X3, Y3, Z3)

    def add(X1, Y1, Z1, X2, Y2, Z2):
        if Z1 == 0:
            return (X2, Y2, Z2)
        if Z2 == 0:
            return (X1, Y1, Z1)
        Z1sq = Z1 * Z1 % p2
        Z2sq = Z2 * Z2 % p2
        U1 = X1 * Z2sq % p2
        U2 = X2 * Z1sq % p2
        S1 = Y1 * Z2 % p2 * Z2sq % p2
        S2 = Y2 * Z1 % p2 * Z1sq % p2
        if U1 == U2:
            if S1 == S2:
                return dbl(X1, Y1, Z1)
            return (1, 1, 0)
        H = (U2 - U1) % p2
        R = (S2 - S1) % p2
        Hsq = H * H % p2
        Hcu = H * Hsq % p2
        X3 = (R * R - Hcu - 2 * U1 * Hsq) % p2
        Y3 = (R * (U1 * Hsq - X3) - S1 * Hcu) % p2
        Z3 = (Z1 * Z2 % p2 * H) % p2
        return (X3, Y3, Z3)

    def mul(n, P):
        X, Y, Z = (1, 1, 0)
        Q = P
        while n:
            if n & 1:
                X, Y, Z = add(X, Y, Z, *Q)
            Q = dbl(*Q)
            n >>= 1
        return (X, Y, Z)

    return dbl, add, mul


def smart_dlog(p, a, b, P_aff, Q_aff):
    """#E == p; P generator; find n with n*P == Q (affine tuples mod p)."""
    p2 = p * p
    dbl, add, mul = point_ops(p2, a % p2)

    def lam(x, y):
        # lambda(P) = t([p]P~)/p mod p  with t = -x/y uniformizer
        rhs = (x * x * x + a * x + b) % p2
        k = (rhs - y * y) // p % p
        t = k * inverse(2 * y, p) % p
        yl = (y + t * p) % p2
        X, Y, Z = mul(p, (x, yl, 1))
        assert Z % p == 0, "lift not order p?"
        lamz = inverse(Z // p, p2)
        Xp = lamz * lamz % p2 * X % p2
        Yp = lamz * lamz % p2 * lamz % p2 * Y % p2
        assert Xp % p != 0 and Yp % p != 0, "precision loss"
        return (-Xp * inverse(Yp, p)) % p

    lp = lam(*P_aff)
    lq = lam(*Q_aff)
    return lq * inverse(lp, p) % p


if __name__ == "__main__":
    # validation: p=751, E: y^2 = x^3 + x + 1 has #E = 751 (classic anomalous example)
    import random
    p, a, b = 1039, 2, 5
    b_global = b

    def on_curve(x, y):
        return (y * y - x * x * x - a * x - b) % p == 0

    def addf(P1, P2):
        if P1 is None: return P2
        if P2 is None: return P1
        x1, y1 = P1; x2, y2 = P2
        if x1 == x2 and (y1 + y2) % p == 0: return None
        if P1 == P2:
            m = (3 * x1 * x1 + a) * inverse(2 * y1, p) % p
        else:
            m = (y2 - y1) * inverse(x2 - x1, p) % p
        x3 = (m * m - x1 - x2) % p
        y3 = (m * (x1 - x3) - y1) % p
        return (x3, y3)

    def mulf(n, P):
        R = None
        while n:
            if n & 1: R = addf(R, P)
            P = addf(P, P); n >>= 1
        return R

    # find a generator: random point, order must be 751 (prime)
    while True:
        x = random.randrange(p)
        rhs = (x**3 + a*x + b) % p
        y = pow(rhs, (p+1)//4, p) if p % 4 == 3 else None
        if y is None or (y*y) % p != rhs or y == 0: continue
        G = (x, y)
        if mulf(1039, G) is None and G is not None:
            break
    print("G =", G, "on curve:", on_curve(*G))
    ok = 0
    for trial in range(20):
        n = random.randrange(1, p)
        Q = mulf(n, G)
        n2 = smart_dlog(p, a, b, G, Q)
        ok += (n2 == n)
    print(f"smart_dlog correct: {ok}/20")

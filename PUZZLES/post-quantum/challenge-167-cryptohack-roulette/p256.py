# Minimal P-256 arithmetic (None = point at infinity), affine.
P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A = -3
N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
G = (GX, GY)

def inv(x, m=P):
    return pow(x, -1, m)

def add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1; x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % P == 0: return None
        l = (3*x1*x1 + A) * inv(2*y1) % P
    else:
        l = (y2 - y1) * inv(x2 - x1) % P
    x3 = (l*l - x1 - x2) % P
    y3 = (l*(x1 - x3) - y1) % P
    return (x3, y3)

def mul(k, pt):
    r = None
    while k:
        if k & 1: r = add(r, pt)
        pt = add(pt, pt)
        k >>= 1
    return r

import random, gmpy2, sys
from math import gcd
from Crypto.Util.number import getPrime, isPrime
HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

def tsqrt(a, nn):
    x = pow(a, (nn + 1) // 4, nn)
    return x if x * x % nn == a % nn else None

class BadDen(Exception):
    def __init__(self, den): self.den = den

def add(P, Q, A, B, nn):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % nn == 0: raise BadDen((2 * y1) % nn)
        den = (2 * y1) % nn; num = (3 * x1 * x1 + A) % nn
    else:
        den = (x2 - x1) % nn; num = (y2 - y1) % nn
    try: g = pow(den, -1, nn)
    except ValueError: raise BadDen(den)
    m = num * g % nn
    return ((m*m - x1 - x2) % nn, (m*(x1 - (m*m-x1-x2)%nn) - y1) % nn)

def factor(n, seed=1, trials=40):
    rng = random.Random(seed)
    DH = (HB*HB - 4*HC) % n
    sDH = tsqrt(DH, n)
    if sDH is None: return "DH-not-QR"
    j0 = (sDH - HB) * ((n+1)//2) % n
    if (j0*j0 + HB*j0 + HC) % n != 0: return "j0-not-root"
    ti = pow(1728 - j0, -1, n)
    A0 = 3*j0 % n * ti % n; B0 = 2*j0 % n * ti % n
    for trial in range(trials):
        d = 1 if trial == 0 else rng.randrange(2, n)
        d2 = d*d % n
        A = d2*A0 % n; B = d2*d % n*B0 % n
        for _ in range(3):
            x0 = rng.randrange(2, n)
            g = (pow(x0,3,n) + A*x0 + B) % n
            gg = gcd(g, n)
            if 1 < gg < n: return gg
            if gg != 1 or pow(g,(n-1)//2,n) != 1: continue
            y0 = tsqrt(g, n)
            if y0 is None: continue
            P=(x0,y0); R=None; k=n
            try:
                while k:
                    if k&1: R=add(R,P,A,B,n)
                    P=add(P,P,A,B,n); k>>=1
            except BadDen as ex:
                f = gcd(ex.den, n)
                if 1 < f < n: return f
            if R is None: return "O-mod-n"
    return None

rng = random.Random(7)
ok = fail = 0
for it in range(6):
    while True:
        s = rng.randrange(2**62, 2**64)
        t = 427*s*s + 1
        if t % 4 == 0 and isPrime(t//4): p = t//4; break
    while True:
        q = getPrime(160)
        n = p*q
        if gmpy2.jacobi(-427, n) == 1: break  # match real instance: H splits mod q
    f = factor(n, seed=100+it)
    good = f in (p, q)
    ok += good; fail += (not good)
    print(f"inst{it}: p={p} f={f} good={good}")
print("ok:", ok, "fail:", fail)

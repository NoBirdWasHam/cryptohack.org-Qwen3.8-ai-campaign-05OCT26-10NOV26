#!/usr/bin/env python3
"""exceptional_twisted_mind local probe: ladder correctness over Z/p^2 + p-adic leak test."""
from Crypto.Util.number import GCD, inverse
import random

modulus = 13407807929942597099574024998205846127479365820592393377723561443721764030029777567070168776296793595356747829017949996650141749605031603191442486002224009
p0 = 115792089237316195423570985008687907853269984665640564039457584007913129639747
a = -3
b = 152961
order = 115792089237316195423570985008687907853233080465625507841270369819257950283813

# --- server ladder verbatim (modulus = p0^2) ---
def dbl(P1):
    X1, Z1 = P1
    XX = X1**2 % modulus
    ZZ = Z1**2 % modulus
    A = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % modulus
    aZZ = a * ZZ % modulus
    X3 = ((XX - aZZ) ** 2 - 2 * b * A * ZZ) % modulus
    Z3 = (A * (XX + aZZ) + 4 * b * ZZ**2) % modulus
    return (X3, Z3)

def diffadd(P1, P2, x0):
    X1, Z1 = P1; X2, Z2 = P2
    X1Z2 = X1 * Z2 % modulus
    X2Z1 = X2 * Z1 % modulus
    Z1Z2 = Z1 * Z2 % modulus
    T = (X1Z2 + X2Z1) * (X1 * X2 + a * Z1Z2) % modulus
    Z3 = (X1Z2 - X2Z1) ** 2 % modulus
    X3 = (2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % modulus
    return (X3, Z3)

def scalarmult(scalar, x0):
    R0 = (x0, 1); R1 = dbl(R0)
    n = scalar.bit_length()
    pbit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit = pbit ^ bit
        if pbit: R0, R1 = R1, R0
        R1 = diffadd(R0, R1, x0)
        R0 = dbl(R0)
        pbit = bit
    if bit: R0 = R1
    if GCD(R0[1], modulus) != 1: return "Infinity"
    return R0[0] * inverse(R0[1], modulus) % modulus

# --- reference: affine over F_p (curve) ---
def addf(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p0 == 0: return None
    m = (3*x1*x1 + a) * inverse(2*y1, p0) % p0 if P1 == P2 else (y2-y1) * inverse(x2-x1, p0) % p0
    x3 = (m*m - x1 - x2) % p0
    return (x3, (m*(x1-x3) - y1) % p0)

def mulf(n, P):
    R = None
    while n:
        if n & 1: R = addf(R, P)
        P = addf(P, P); n >>= 1
    return R

# find x0 on curve (t QR)
def tonelli_like(n):
    # p0 % 4 == 3
    r = pow(n, (p0+1)//4, p0)
    return r if r*r % p0 == n % p0 else None

random.seed(7)
x0 = None
while True:
    cand = random.randrange(2, p0)
    t = (cand**3 + a*cand + b) % p0
    y = tonelli_like(t)
    if y: x0 = cand; break
P = (x0, tonelli_like((x0**3 + a*x0 + b) % p0))
print("x0 =", x0)

# 1) ladder mod p vs reference x([k]P) for small k
ok = 0
for k in range(2, 30):
    r = scalarmult(k, x0)
    ref = mulf(k, P)
    ok += (ref is not None and r != "Infinity" and r % p0 == ref[0])
print(f"ladder mod-p correct on-curve: {ok}/28")

# 2) ladder mod p^2 vs canonical-lift reference? compute reference over Z/p^2 affine
p2 = modulus
def addf2(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if (x1 - x2) % p0 == 0 and (y1 + y2) % p0 == 0: return None  # O (Z ~ 0 mod p)
    if x1 == x2 and y1 == y2:
        den = (2 * y1) % p2
        m = (3 * x1 * x1 + a) * inverse(den, p2) % p2
    else:
        den = (x2 - x1) % p2
        if GCD(den, p2) != 1:
            return "SING"
        m = (y2 - y1) * inverse(den, p2) % p2
    x3 = (m*m - x1 - x2) % p2
    return (x3, (m*(x1-x3) - y1) % p2)

# canonical lift of P: y~ = y + t p with t = ((x0^3+a x0+b) - y^2)/p / (2y)
rhs = (x0**3 + a*x0 + b) % p2
tt = (((rhs - P[1]**2) // p0) * inverse(2 * P[1], p0)) % p0
yl = (P[1] + tt * p0) % p2
Pc = (x0, yl)
print("canonical lift on curve mod p2:", (yl*yl - x0**3 - a*x0 - b) % p2 == 0)

def mulf2(n, Pt):
    R = None
    while n:
        if n & 1:
            R2 = addf2(R, Pt)
            if R2 == "SING": return "SING"
            R = R2
        Pt2 = addf2(Pt, Pt)
        if Pt2 == "SING": return "SING"
        Pt = Pt2; n >>= 1
    return R

for k in [3, 5, 9, 17]:
    r = scalarmult(k, x0)
    ref = mulf2(k, Pc)
    if ref == "SING" or ref is None or r == "Infinity":
        print(f"k={k}: degenerate ref={ref} r={r}"); continue
    delta = (r - ref[0]) % p2
    print(f"k={k}: ladder==canon-lift-ref: {delta == 0}  delta/p={delta // p0 if delta % p0 == 0 else 'NOT-div-p'}")

# 3) p-adic linearity: v(k) = ((resp - resp^p ... ))/p mod p — test additivity
def padic_part(resp):
    v = resp
    vp = pow(v, p0, p2)
    w = v * inverse(vp, p2) % p2
    return (w - 1) // p0 % p0

vals = []
for k in [2, 3, 4, 5, 11, 100]:
    r = scalarmult(k, x0)
    if r == "Infinity": print(k, "Infinity"); continue
    vals.append((k, padic_part(r)))
print("padic parts (k, w):", vals[:6])
if len(vals) >= 3:
    k1, w1 = vals[0]; k2, w2 = vals[1]
    print("additive? w(2)+w(3)==w(5):", (w1+w2)%p0 == vals[3][1], " w(2)+w(2)==w(4):", (2*w1)%p0 == vals[2][1])

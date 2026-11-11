import re, random, sys
src = open("13418.py").read()
p = int(re.search(r"modulus\s*=\s*(\d+)", src).group(1))
a = int(re.search(r"^a\s*=\s*(-?\d+)", src, re.M).group(1))
b = int(re.search(r"^b\s*=\s*(\d+)", src, re.M).group(1))
order = int(re.search(r"^order\s*=\s*(\d+)", src, re.M).group(1))
print("p bits:", p.bit_length(), "order bits:", order.bit_length(), flush=True)
Bi = pow(b, -1, p)
O = None
def f(x): return (x*x*x + a*x*x + x) * Bi % p
def legendre(n): return pow(n % p, (p-1)//2, p)
def sqrt_mod(n):
    n %= p
    if n == 0: return 0
    if legendre(n) != 1: return None
    # p % 4 == 3 fast path
    return pow(n, (p+1)//4, p)
def pdbl(P):
    if P is O: return O
    x, y = P
    if y == 0: return O
    lam = (3*x*x + 2*a*x + 1) * pow(2*y, -1, p) % p
    x3 = (lam*lam*Bi - a - 2*x) % p
    return (x3, (lam*(x-x3) - y) % p)
def padd(P, Q):
    if P is O: return Q
    if Q is O: return P
    x1,y1 = P; x2,y2 = Q
    if x1 == x2:
        return O if (y1+y2) % p == 0 else pdbl(P)
    lam = (y2-y1) * pow(x2-x1, -1, p) % p
    x3 = (lam*lam*Bi - a - x1 - x2) % p
    return (x3, (lam*(x1-x3) - y1) % p)
def pmul(k, P):
    R = O
    while k:
        if k & 1: R = padd(R, P)
        P = pdbl(P); k >>= 1
    return R
# verify affine model against server dbl (projective)
def sdbl(X1, Z1):
    XX = X1**2 % p; ZZ = Z1**2 % p
    A = 2 * ((X1+Z1)**2 - XX - ZZ) % p
    aZZ = a * ZZ % p
    X3 = ((XX - aZZ)**2 - 2*b*A*ZZ) % p
    Z3 = (A*(XX + aZZ) + 4*b*ZZ**2) % p
    return X3 * pow(Z3, -1, p) % p
rng = random.Random(1)
tries = 0
while True:
    x = rng.randrange(2, p)
    y = sqrt_mod(f(x))
    tries += 1
    if y: break
    if tries > 2000:
        print("NO curve points in 2000 tries -> curve degenerate or model wrong", flush=True)
        # count legendre stats
        lr = sum(1 for _ in range(200) if legendre(f(rng.randrange(2,p))) == 1)
        print("legendre==1 rate:", lr, "/200", flush=True)
        sys.exit(1)
P = (x, y)
print(f"curve point found after {tries} tries; on-curve check:",
      (b*P[1]*P[1] - (P[0]**3 + a*P[0]**2 + P[0])) % p == 0, flush=True)
print("dbl model match:", sdbl(P[0], 1) == pdbl(P)[0], flush=True)
# Hasse sanity: order vs p
print("order < p?", order < p, " order/p ~ 2^-?", (p//order).bit_length()-1, flush=True)
# test: is (p+1)P == O (supersingular t=0)?
print("testing (p+1)P...", flush=True)
print("(p+1)P == O?", pmul(p+1, P) is O, flush=True)
# test smooth S annihilates P (curve order smooth?)
import sympy
S = 1
for q in sympy.primerange(2, 2000):
    e = 1
    while q**(e+1) < 10**9: e += 1
    S *= q**e
print("S bits:", S.bit_length(), "testing S*P...", flush=True)
print("S*P == O?", pmul(S, P) is O, flush=True)
# twist test: x with f(x) non-residue; emulate twist scalar mult via affine on E^d?
# simpler: use the SERVER ladder model (projective, x-only) on a twist x0 and test m*x0 == O via Z==0
def sxz(X1, Z1):  # returns projective dbl
    XX = X1**2 % p; ZZ = Z1**2 % p
    A = 2 * ((X1+Z1)**2 - XX - ZZ) % p
    aZZ = a * ZZ % p
    X3 = ((XX - aZZ)**2 - 2*b*A*ZZ) % p
    Z3 = (A*(XX + aZZ) + 4*b*ZZ**2) % p
    return (X3, Z3)
def sdiff(X1, Z1, X2, Z2, x0):
    X1Z2 = X1*Z2 % p; X2Z1 = X2*Z1 % p; Z1Z2 = Z1*Z2 % p
    T = (X1Z2 + X2Z1) * (X1*X2 + a*Z1Z2) % p
    Z3 = (X1Z2 - X2Z1)**2 % p
    X3 = (2*T + 4*b*Z1Z2**2 - x0*Z3) % p
    return (X3, Z3)
def ladder(scalar, x0):
    R0 = (x0, 1); R1 = sxz(*R0)
    n = scalar.bit_length(); pbit = 0; bit = 0
    for i in range(n-2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit: R0, R1 = R1, R0
        R1 = sdiff(*R0, *R1, x0)
        R0 = sxz(*R0)
        pbit = bit
    if bit: R0 = R1
    return R0
# find twist x0
xt = rng.randrange(2, p)
while legendre(f(xt)) == 1:
    xt = rng.randrange(2, p)
print("testing twist point S*x0 == O (Z==0)?", flush=True)
R = ladder(S, xt)
print("twist S*x0 Z==0?", R[1] == 0, flush=True)
R2 = ladder(p+1, xt)
print("twist (p+1)*x0 Z==0?", R2[1] == 0, flush=True)

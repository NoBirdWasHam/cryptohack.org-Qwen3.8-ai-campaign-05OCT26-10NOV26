# kaitenzushi (HackTM CTF) - first-principles solve
# n = pq, x_i^2 + e*y_i^2 = n, hints: R*x, R*y as 1337-bit reals.
from fractions import Fraction
from math import gcd, isqrt
from Crypto.Util.number import long_to_bytes, inverse, isPrime
import mpmath as mp

def parse_line(line):
    key, _, val = line.partition("=")
    return key.strip(), val.strip()

lines = open("output.txt").read().strip().splitlines()
d = {}
for ln in lines:
    k, v = parse_line(ln)
    d[k] = v
n = int(d["n"]); c = int(d["c"])

def parse_vec(s):
    s = s.strip().strip("()")
    parts = [p.strip() for p in s.split(",")]
    return [Fraction(p) for p in parts]

xp = parse_vec(d["x"]); yp = parse_vec(d["y"])

Sy_f = yp[0]**2 + yp[1]**2
Sy = round(Sy_f)
assert abs(Sy_f - Sy) < Fraction(1, 10**3), "Sy error too big"
Sx_f = xp[0]**2 + xp[1]**2
# Sx integer? error ~2^199, not exact; use it to get e
e_num = 2*n*Sy_f.denominator - (Sx_f.numerator * Sy)  # careful: compute exactly
# e = (2n - Sx)/Sy with Sx approx: do rational math
e_frac = (Fraction(2*n) - Sx_f) / Fraction(Sy)
assert abs(e_frac - round(e_frac)) < Fraction(1, 10**50)
e = round(e_frac)
print("e bits:", e.bit_length(), "prime:", isPrime(e), "gcd:", gcd(e, 4) )

# E1 - E2 = 0  =>  A*cos2t + B*sin2t = 0 with
# A = x1p^2 - x2p^2 + e*(y1p^2 - y2p^2),  B = 2*(x1p*x2p + e*y1p*y2p)
A = (xp[0]**2 - xp[1]**2) + e*(yp[0]**2 - yp[1]**2)
B = 2*(xp[0]*xp[1] + e*yp[0]*yp[1])

mp.mp.dps = 500
def f2m(fr):
    return mp.mpf(fr.numerator) / mp.mpf(fr.denominator)
Am, Bm = f2m(A), f2m(B)
D = mp.hypot(Am, Bm)
cos2t =  Bm / D
sin2t = -Am / D
t = mp.atan2(sin2t, cos2t) / 2
ct = mp.cos(t); st = mp.sin(t)

def rnd(fr_m):
    return int(mp.nint(fr_m))
x1 = rnd(ct*f2m(xp[0]) + st*f2m(xp[1]))
x2 = rnd(-st*f2m(xp[0]) + ct*f2m(xp[1]))
y1 = rnd(ct*f2m(yp[0]) + st*f2m(yp[1]))
y2 = rnd(-st*f2m(yp[0]) + ct*f2m(yp[1]))
print("check E1:", x1*x1 + e*y1*y1 == n, "E2:", x2*x2 + e*y2*y2 == n)

cands = []
X, Y = (x1, x2), (y1, y2)
for _ in range(4):
    X = (X[1], -X[0]); Y = (Y[1], -Y[0])
    cands.append((X[0], X[1], Y[0], Y[1]))
# also the direct one
cands.insert(0, (x1, x2, y1, y2))
good = [t for t in cands if t[0]**2 + e*t[2]**2 == n and t[1]**2 + e*t[3]**2 == n]
print("int-check candidates:", len(good))

M = x1*x2 + e*y1*y2
Nc = x2*y1 - x1*y2
p = gcd(M, Nc)
if not (1 < p < n):
    M2 = x1*x2 - e*y1*y2
    p = gcd(M2, Nc) if abs(Nc)>0 else 0
print("p found:", 1 < p < n, "bits:", p.bit_length() if p>1 else 0)
q = n // p
assert p * q == n and isPrime(p) and isPrime(q)
dE = inverse(e, (p-1)*(q-1))
Xv = pow(c, dE, n)
for (a,b,g,h) in cands:
    if a<=0 or b<=0 or g<=0 or h<=0: continue
    m = Xv ^ a ^ g ^ b ^ h
    if m <= 0: continue
    msg = long_to_bytes(m)
    try:
        s = msg.decode("utf-8")
        if "flag" in s or "FLAG" in s or "{" in s:
            print("FLAG:", s)
    except Exception:
        pass

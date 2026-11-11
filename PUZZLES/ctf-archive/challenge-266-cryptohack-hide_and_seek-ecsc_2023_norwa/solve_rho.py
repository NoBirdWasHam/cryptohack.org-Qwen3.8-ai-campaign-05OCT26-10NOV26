# Pollard-rho per prime factor (no hash tables), gmpy2 for speed.
# X = x*P over E/F_p, n smooth (9 primes ~2^34.9). CRT.
import math
from gmpy2 import invert, mpz
from Crypto.Util.number import long_to_bytes

p = mpz(17898504337425668039996599611020710187085880959961102071018708585988988036381340404632423562593)
ac = mpz(62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998)
bc = mpz(1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211)
t = 16093597302722077219468084775737143208134062101
n = p + 1 - t
facs = [12775224751,13026062843,18511195699,24508446437,25961704469,28450356619,31034521019,31982226581,32337773063]
assert math.prod(facs) == int(n)

import re
txt = open("output.txt").read()
tri = re.findall(r"\((\d+),\s*(\d+),\s*\((\d+)\s*:\s*(\d+)\s*:\s*1\)\)", txt)
data = [(int(a), int(b), (mpz(x), mpz(y))) for a, b, x, y in tri]

def add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0: return None
    m = (3*x1*x1 + ac) * invert(2*y1, p) if P1 == P2 else (y2 - y1) * invert(x2 - x1, p)
    m %= p
    x3 = (m*m - x1 - x2) % p
    return (x3, (m*(x1 - x3) - y1) % p)

def mul(k, P1):
    R = None; Q1 = P1
    while k:
        if k & 1: R = add(R, Q1)
        Q1 = add(Q1, Q1); k >>= 1
    return R

# recover P, X
P = X = None
for i in range(len(data)):
    ai, bi, Ri = data[i]
    for j in range(i+1, len(data)):
        aj, bj, Rj = data[j]
        D = (aj*bi - ai*bj) % int(n)
        if D == 0: continue
        S = add(mul(bi, Rj), mul(-bj, Ri))
        Tm = add(mul(aj, Ri), mul(-ai, Rj))
        if S is None or Tm is None: continue
        Di = pow(D, -1, int(n))
        P, X = mul(Di, S), mul(Di, Tm)
        break
    if P: break
assert mul(int(n), P) is None

def rho(Q, Y, q):
    # Y = xQ mod q-order subgroup; rho over Z_q x Z_q x <Q>
    def f(st):
        a, b, R = st
        if R is None: return ((a + 1) % q, b, Q) if True else None
        if a % 3 == 0: return ((a*2) % q, (b*2) % q, add(R, R))
        if a % 3 == 1: return ((a + 1) % q, b, add(R, Q))
        return (a, (b + 1) % q, add(R, Y))
    st = tort = (1, 0, Q)
    for _ in range(3): tort = f(tort)
    hare = f(f(f(st)))
    while tort != hare:
        st = tort = f(tort)
        hare = f(f(f(hare)))
    a1, b1, _ = tort
    # collision: a1 Q + b1 Y == a2 Q + b2 Y  => (a1+a2)Q + (b1+b2)Y? depends on walk symmetry
    # Use additive: tortoise state st had (a2,b2) = predecessor pair; do proper solve:
    # Standard: after collision, x = (a2 - a1)/(b1 - b2) with tort=(a1,b1,R), hare-parallel (a2,b2,R)
    # Simpler: recompute with stored second component pair:
    return a1, b1, st

def dlp(Q, Y, q):
    # rho with explicit (a,b) tracking; detect R collision with differing ratio
    def step(a, b, R):
        c = (a % 3, b % 3)  # partition on point x-coord is better; use x%3
        return None
    # fallback to BSGS for simplicity since sqrt(q)~2^17.5 with dict of 185k is fine
    m = math.isqrt(q) + 1
    table = {}
    acc = None
    for j in range(m):
        table.setdefault(acc, j)
        acc = add(acc, Q)
    ng = mul(-m, Q)
    cur = Y
    for i in range(m):
        j = table.get(cur)
        if j is not None:
            c = i*m + j
            if c < q: return c
        cur = add(cur, ng)
    raise RuntimeError

xs = []
for q in facs:
    h = int(n)//q
    xi = dlp(mul(h, P), mul(h, X), q)
    xs.append(xi)
    print(q, xi, flush=True)
x = 0; M = 1
for xi, q in zip(xs, facs):
    r = ((xi - x) % q) * pow(M % q, -1, q) % q
    x += M*r; M *= q
x %= int(n)
assert mul(x, P) == X
flag = "ECSC{" + long_to_bytes(x).decode() + "}"
print("FLAG:", flag)
open("flag_hide_and_seek-ecsc_2023_norwa.txt", "w").write(flag)

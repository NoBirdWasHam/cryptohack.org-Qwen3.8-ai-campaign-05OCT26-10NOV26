#!/usr/bin/env python3
# challenge-219 CSIDH key exchange: shared = [a+b]E0 class-group walk, answer = Montgomery A.
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad
import random

ells = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
        71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139,
        149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223,
        227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293,
        307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 587]
P = 1
for l in ells: P *= l
p = 4 * P - 1
assert p % 4 == 3
a_priv = [-1, -2, -3, -3, -2, -3, -3, 0, 2, -1, 2, -1, -2, -3, 1, 2, 1, 2, 0, 0, 1, -1, 0, 2, -1, 0, 0, 0, 1, -1, -3, 1, -1, -3, -3, 2, 2, 1, -1, -1, 1, 0, 1, 1, 1, -2, 2, 2, -2, -2, 0, 0, 2, 0, -1, -3, -2, -2, 0, -1, -3, -1, -2, -3, -2, 2, 1, 1, -2, 0, 1, -1, -3, 2]
b_priv = [-1, -1, 0, 1, 2, 0, 2, -1, -3, 1, 0, -2, -2, 2, -1, -2, -3, -3, -3, 2, 2, 2, -2, -1, 1, -2, 0, -3, -1, 1, -1, -1, -3, -1, -2, 1, -1, -2, -3, 1, 0, -1, 1, 2, 2, 0, 0, -1, -2, -2, 1, -1, 1, 1, 1, 1, 0, 0, 0, -3, -2, -1, 2, 0, -3, -2, 1, 1, -2, -1, -1, 2, 0, 1]
exps = [x + y for x, y in zip(a_priv, b_priv)]
IV = bytes.fromhex("daf6cd181775664b099609789fb564c9")
CT = bytes.fromhex("3dd92e255c8e677f4a92226d09f56e2b2f567052ffd4f6f60200018454a83affc2e694c2bf2ad27da38f7f49b6e89928")

def sqrt_p(c):
    w = pow(c, (p + 1) // 4, p)
    return w if (w * w - c) % p == 0 else None

def add(Pt, Qt, a):
    if Pt is None: return Qt
    if Qt is None: return Pt
    x1, y1 = Pt; x2, y2 = Qt
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if Pt == Qt:
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        m = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (m * m - x1 - x2) % p
    return (x3, (m * (x1 - x3) - y1) % p)

def mul(Pt, n, a):
    R = None; Q = Pt
    while n:
        if n & 1: R = add(R, Q, a)
        Q = add(Q, Q, a); n >>= 1
    return R

def rand_point(a, b, rng):
    while True:
        x = rng.randrange(1, p)
        c = (x * x * x + a * x + b) % p
        y = sqrt_p(c)
        if y is not None and c % p != 0:
            return (x, y)

def kernel_gen(a, b, l, rng):
    # #E = p+1 (supersingular, trace 0); l | p+1, l^2 -/-> p+1 -> E(F_p)[l] cyclic
    n = (p + 1) // l
    while True:
        Pp = rand_point(a, b, rng)
        Q = mul(Pp, n, a)
        if Q is not None:
            assert mul(Q, l, a) is None
            return Q

def velu_step(a, b, l, rng):
    # Galbraith 25.1.6 short-Weierstrass (validated vs PARI on prime_power 27 steps)
    Q = kernel_gen(a, b, l, rng)
    S_t = 0; S_u = 0
    for k in range(1, (l - 1) // 2 + 1):
        x, y = mul(Q, k, a)
        t = 2 * (3 * x * x + a) % p
        u = 4 * y * y % p
        S_t = (S_t + t) % p
        S_u = (S_u + u + x * t) % p
    return (a - 5 * S_t) % p, (b - 7 * S_u) % p

# fixed nonsquare d for twists
d = 2
while pow(d, (p - 1) // 2, p) != p - 1: d += 1
print("nonsquare d =", d)

def twist(a, b):
    return d * d % p * a % p, d * d % p * d % p * b % p

import os
rng = random.Random(0xC51D)
if os.path.exists("walk_cache.txt"):
    a, b = (int(x) for x in open("walk_cache.txt").read().split())
    steps = -1
else:
  a, b = 1, 0
  steps = 0
  for l, e in zip(ells, exps):
    if e == 0: continue
    if e > 0:
        for _ in range(e):
            a, b = velu_step(a, b, l, rng); steps += 1
    else:
        for _ in range(-e):
            a, b = twist(a, b)
            a, b = velu_step(a, b, l, rng); steps += 1
            a, b = twist(a, b)
  open("walk_cache.txt", "w").write(f"{a} {b}")
print("walk done, steps =", steps)
print("final a4 =", a)
print("final a6 =", b)

# Montgomery A: 2-torsion roots of x^3+ax+b. p = 4*prod-1 with 3|prod => p = 2 (mod 3),
# so cubing is a bijection mod p: Cardano works with a plain cube root.
assert p % 3 == 2
def cbrt(u):  # unique cube root mod p (p = 2 mod 3)
    return pow(u, (2 * p - 1) // 3, p)
def sqrt_p2(c):
    w = sqrt_p(c)
    return w
Dc = (b * b % p + 4 * pow(a, 3, p) * pow(27, -1, p)) % p
sD = sqrt_p(Dc)
assert sD is not None, "Cardano sqrt failed"
U = (-b + sD) * pow(2, -1, p) % p
u = cbrt(U)
assert u != 0
v0 = (u - a * pow(3 * u, -1, p)) % p
# v0 is one root; factor (x-v0) out of x^3+ax+b -> x^2 + v0 x + (v0^2 + a)
B2, C2 = v0 % p, (v0 * v0 + a) % p
Dq = (B2 * B2 - 4 * C2) % p
sq = sqrt_p(Dq)
roots = [v0]
if sq is not None:
    roots.append((-B2 + sq) * pow(2, -1, p) % p)
    roots.append((-B2 - sq) * pow(2, -1, p) % p)
roots = [r % p for r in roots]
assert all((r**3 + a * r + b) % p == 0 for r in roots), "root check failed"
print("2-torsion roots:", roots)
cands = []
for v in roots:
    c2 = (3 * v * v + a) % p
    w = sqrt_p(c2)
    if w is not None and w != 0:
        A = 3 * v % p * pow(w, -1, p) % p
        cands.append(A)
print("Montgomery candidates:", cands)

def try_A(A):
    for desc, s in (("A", str(A)), ("-A", str((-A) % p))):
        key = SHA256.new(data=s.encode()).digest()
        try:
            pt = unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(CT), 16)
        except Exception:
            continue
        if b"crypto" in pt:
            print(f"FLAG via {desc}={s}: {pt.decode()}")
            open("flag.txt", "wb").write(pt)
            return True
    return False

for A in cands:
    if try_A(A): break
else:
    print("no candidate decrypted; try twist convention d=-1 or other roots")

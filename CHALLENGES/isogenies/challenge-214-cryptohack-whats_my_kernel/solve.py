#!/usr/bin/env python
"""whats_my_kernel (70 pts): SIDH public key, recover kernel.

Structure of source.sage:
  l_a, l_b = 2, 3; e_a, e_b = 216, 137; p = 2^216*3^137 - 1 (385-bit prime)
  E: y^2 = x^3 + 1 over F_{p^2} = F_p[i]
  P_a, Q_a = 3^137 * gens  -> Z/2^216-basis of E[2^216]
  (bug in source: P_b, Q_b := c_a*P, c_a*Q = P_a, Q_a  -- the "Bob" points
   are the SAME as Alice's generators)
  n = bytes_to_long(FLAG[7:-1])   (19 hex digits = 76 bits)
  R = P_a + n*Q_a ;  phi = isogeny with kernel R   (deg = 2^216 if n odd)
  Public key: E_A = codomain, P_B = phi(P_a), Q_B = phi(Q_a)

Key relation (phi is a homomorphism, R in kernel):
    P_B + n*Q_B = phi(R) = O        in E_A

So m := ECDLP_{P_B}(Q_B) satisfies P_B = -m... : P_B + n Q_B = O and Q_B = m P_B
  =>  (1 + n*m) P_B = O  =>  n*m = -1 (mod 2^216)  =>  n = -m^{-1} mod 2^216.

m is a discrete log in the cyclic 2-group E_A[2^216] with the promise
n < 2^76. In a cyclic 2-group the log is extracted BIT BY BIT (each bit costs
one scalar multiplication by a power of 2 -- no BSGS):
  bit k of m:  t_k = 2^{e-1-k} * (h - (m mod 2^k)*g)  in  {O, 2^{e-1}*g}.
"""
import re

# ---------- parse output.txt ----------
txt = open("output.txt", encoding="utf-8").read()

pm = re.search(r"Finite Field in i of size (\d+)\^2", txt)
p = int(pm.group(1))
assert p == (2**216 * 3**137 - 1), "p mismatch"

am = re.search(r"E_A = Elliptic Curve defined by y\^2 = x\^3 \+ \((\d+)\*i\+(\d+)\)\*x \+ \((\d+)\*i\+(\d+)\)", txt)
aA = (int(am.group(2)), int(am.group(1)))   # (real, imag)
bA = (int(am.group(4)), int(am.group(3)))

def parse_point(name):
    m = re.search(name + r" = \((\d+)\*i \+ (\d+) : (\d+)\*i \+ (\d+) : 1\)", txt)
    x = (int(m.group(2)), int(m.group(1)))
    y = (int(m.group(4)), int(m.group(3)))
    return (x, y)

PB = parse_point("phi_a\\(P_b\\)")
QB = parse_point("phi_a\\(Q_b\\)")
print(f"p = {p} ({p.bit_length()} bits)")
print(f"E_A: y^2 = x^3 + ({aA[0]}+{aA[1]}i) x + ({bA[0]}+{bA[1]}i)")

# ---------- F_p2 + EC (affine; O = None) ----------
def f2(a, b=0):
    if isinstance(a, tuple):
        return (a[0] % p, a[1] % p)
    return (a % p, b % p)
def _n(x):
    return x if isinstance(x, tuple) else f2(x)
def f2_add(a, b):
    a, b = _n(a), _n(b)
    return ((a[0]+b[0]) % p, (a[1]+b[1]) % p)
def f2_sub(a, b):
    a, b = _n(a), _n(b)
    return ((a[0]-b[0]) % p, (a[1]-b[1]) % p)
def f2_neg(a):
    a = _n(a)
    return ((-a[0]) % p, (-a[1]) % p)
def f2_mul(a, b):
    a, b = _n(a), _n(b)
    return ((a[0]*b[0]-a[1]*b[1]) % p, (a[0]*b[1]+a[1]*b[0]) % p)
def f2_inv(a):
    d = pow(a[0]*a[0] + a[1]*a[1], p-2, p)
    return ((a[0]*d) % p, (-a[1]*d) % p)
def f2_div(a, b):
    a, b = _n(a), _n(b)
    return f2_mul(a, f2_inv(b))
def f2_eq(a, b):
    return a[0] == b[0] and a[1] == b[1]

ONE, I = (1, 0), (0, 1)

def on_curve(P, a, b):
    if P is None: return True
    x, y = P
    return f2_eq(f2_mul(y, y), f2_add(f2_add(f2_mul(f2_mul(x, x), x), f2_mul(a, x)), b))

def ec_add(P, Q, a, b):
    if P is None: return Q
    if Q is None: return P
    x1, y1, x2, y2 = P[0], P[1], Q[0], Q[1]
    if f2_eq(x1, x2):
        if f2_eq(f2_add(y1, y2), (0, 0)): return None
        lam = f2_div(f2_add(f2_mul(3, f2_mul(x1, x1)), a), f2_mul(2, y1))
    else:
        lam = f2_div(f2_sub(y2, y1), f2_sub(x2, x1))
    x3 = f2_sub(f2_sub(f2_mul(lam, lam), x1), x2)
    y3 = f2_sub(f2_mul(lam, f2_sub(x1, x3)), y1)
    return (x3, y3)

def ec_sub(P, Q, a, b):
    return ec_add(P, (Q[0], f2_neg(Q[1])) if Q is not None else None, a, b)

def ec_mul(P, n, a, b):
    R = None
    while n:
        if n & 1: R = ec_add(R, P, a, b)
        P = ec_add(P, P, a, b)
        n >>= 1
    return R

a, b = aA, bA
assert on_curve(PB, a, b), "P_B not on E_A"
assert on_curve(QB, a, b), "Q_B not on E_A"
print("P_B, Q_B on E_A: OK")

# ---------- order checks ----------
e = 216
print("computing 2^216 * P_B ...", end=" ", flush=True)
assert ec_mul(PB, 2**e, a, b) is None, "P_B order does not divide 2^216"
print("OK (order divides 2^216)")
print("computing 2^216 * Q_B ...", end=" ", flush=True)
assert ec_mul(QB, 2**e, a, b) is None, "Q_B order does not divide 2^216"
print("OK (order divides 2^216)")

# ---------- 2-adic discrete log: Q_B = m * P_B ----------
g, h = PB, QB
s = ec_mul(g, 2**(e-1), a, b)   # order-2 element 2^{e-1} * g
assert s is not None and ec_mul(s, 2, a, b) is None, "2^{e-1}*g must have order 2"

m = 0
Gk = None  # (m mod 2^k) * g, maintained incrementally
two_k_g = g  # 2^k * g
for k in range(e):
    H = ec_sub(h, Gk, a, b) if Gk is not None else h
    t = ec_mul(H, 2**(e-1-k), a, b)
    if t is None:
        bit = 0
    else:
        assert f2_eq(t, s), f"bit extraction broke at k={k}: t not in {{O, s}}"
        bit = 1
    if k % 32 == 0:
        print(f"  bit {k:3d} = {bit}   (m so far = {m:#x})")
    m |= bit << k
    Gk = ec_add(Gk, two_k_g, a, b) if bit else Gk
    two_k_g = ec_add(two_k_g, two_k_g, a, b)
print(f"m = ECDLP = {m} = {m:#x}")
assert ec_mul(g, m, a, b) == h or f2_eq(ec_mul(g, m, a, b), h), "ECDLP verification failed"
print("ECDLP verified: m*P_B == Q_B")

# ---------- n = -m^{-1} mod 2^216 ----------
assert m % 2 == 1, "m even -> relation (1+n*m)*P_B=O impossible for 2-power order"
n = (-pow(m, -1, 2**e)) % 2**e
print(f"n = -m^-1 mod 2^216 = {n} = {n:#x}  (bits: {n.bit_length()})")
assert n < 2**76, "n not in 76-bit flag range -- re-examine assumptions"

# ---------- full verification: P_B + n*Q_B == O ----------
chk = ec_add(PB, ec_mul(QB, n, a, b), a, b)
assert chk is None, f"VERIFICATION FAILED: P_B + n*Q_B != O ({chk})"
print("VERIFICATION OK: P_B + n*Q_B = O  (kernel relation holds exactly)")

flag = "crypto{%019x}" % n
print(f"\nFLAG = {flag}")

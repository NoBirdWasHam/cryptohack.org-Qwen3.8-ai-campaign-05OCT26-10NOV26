#!/usr/bin/env python3
# twisted_mind: verify the x-only (X,Z) ladder on OFF-CURVE x0 equals x([k]P') on the
# quadratic twist E': y^2 = x^3 + a x + b over F_p[s]/(s^2 = t), t = x0^3+a*x0+b nonresidue.
p = 2**192 - 237
a = -3
b = 1379137549983732744405137513333094987949371790433997718123

def rhs(x): return (x*x*x + a*x + b) % p
def leg(x): return pow(x % p, (p-1)//2, p)

# --- server ladder (verbatim) ---
def dbl(P1):
    X1, Z1 = P1
    XX = X1**2 % p; ZZ = Z1**2 % p
    A = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % p
    aZZ = a * ZZ % p
    X3 = ((XX - aZZ) ** 2 - 2 * b * A * ZZ) % p
    Z3 = (A * (XX + aZZ) + 4 * b * ZZ**2) % p
    return (X3, Z3)
def diffadd(P1, P2, x0):
    X1, Z1 = P1; X2, Z2 = P2
    X1Z2 = X1 * Z2 % p; X2Z1 = X2 * Z1 % p; Z1Z2 = Z1 * Z2 % p
    T = (X1Z2 + X2Z1) * (X1 * X2 + a * Z1Z2) % p
    Z3 = (X1Z2 - X2Z1) ** 2 % p
    X3 = (2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % p
    return (X3, Z3)
def scalarmult(scalar, x0):
    R0 = (x0, 1); R1 = dbl(R0)
    n = scalar.bit_length(); pbit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit = pbit ^ bit
        if pbit: R0, R1 = R1, R0
        R1 = diffadd(R0, R1, x0)
        R0 = dbl(R0)
        pbit = bit
    if bit: R0 = R1
    if R0[1] == 0: return "Infinity"
    return R0[0] * pow(R0[1], -1, p) % p

# --- F_{p^2} arithmetic with s^2 = t ---
class Fp2:
    __slots__ = ("u", "v", "t")
    def __init__(s_, u, v, t): s_.u, s_.v, s_.t = u % p, v % p, t
    def __add__(s_, o):
        if isinstance(o, int): o = Fp2(o, 0, s_.t)
        return Fp2(s_.u+o.u, s_.v+o.v, s_.t)
    def __sub__(s_, o):
        if isinstance(o, int): o = Fp2(o, 0, s_.t)
        return Fp2(s_.u-o.u, s_.v-o.v, s_.t)
    def __mul__(s_, o):
        if isinstance(o, int): o = Fp2(o, 0, s_.t)
        return Fp2(s_.u*o.u + s_.t*s_.v*o.v, s_.u*o.v + s_.v*o.u, s_.t)
    def inv(s_):
        n = (s_.u*s_.u - s_.t*s_.v*s_.v) % p
        ni = pow(n, -1, p)
        return Fp2(s_.u*ni % p, -s_.v*ni % p, s_.t)
    def __truediv__(s_, o): return s_ * o.inv()
    def __rmul__(s_, c): return Fp2(s_.u*c, s_.v*c, s_.t)
    def __eq__(s_, o): return s_.u % p == o.u % p and s_.v % p == o.v % p
    def sq(s_): return s_ * s_
    def neg(s_): return Fp2(-s_.u, -s_.v, s_.t)
    def is_fp(s_): return s_.v % p == 0

def pt_double(P):
    x, y = P
    l = (x*x*3 + a) / (2 * y)
    xr = l*l - 2*x
    yr = l*(x - xr) - y
    return (xr, yr)
def pt_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2).is_zero(): return None
        return pt_double(P)
    l = (y2 - y1) / (x2 - x1)
    xr = l*l - x1 - x2
    yr = l*(x1 - xr) - y1
    return (xr, yr)
def Fp2_zero(x): return x.u % p == 0 and x.v % p == 0
Fp2.is_zero = lambda s_: s_.u % p == 0 and s_.v % p == 0
def pt_mul(k, P):
    R = None; Q = P
    while k:
        if k & 1: R = pt_add(R, Q)
        Q = pt_double(Q); k >>= 1
    return R

# find an off-curve x0 (t nonresidue)
x0 = 5
while leg(rhs(x0)) != p-1: x0 += 1
t = rhs(x0)
print("off-curve x0 =", x0, " t nonresidue ✓")
Pp = (Fp2(x0,0,t), Fp2(0,1,t))   # (x0, s), s^2 = t
ok = 0
for k in range(2, 41):   # k=1 hits the server's UnboundLocalError edge case (bit_length<2)
    R = pt_mul(k, Pp)
    xf = R[0].u if R is not None else None
    assert R is None or R[0].is_fp(), f"x not in F_p at k={k}"
    xv = xf % p if R is not None else "Infinity"
    lv = scalarmult(k, x0)
    if xv == lv: ok += 1
    else: print(f"k={k}: ladder={lv} twist={xv} MISMATCH")
print(f"ladder == twist-scalarmult for {ok}/40 k-values")

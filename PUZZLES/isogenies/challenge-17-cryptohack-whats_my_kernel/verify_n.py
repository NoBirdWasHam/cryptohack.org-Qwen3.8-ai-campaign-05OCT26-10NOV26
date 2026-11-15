#!/usr/bin/env python
"""whats_my_kernel — part 2: pin down the real n and GOLD-verify.

Part 1 (solve.py) found m = ECDLP_{P_B}(Q_B) with m*P_B == Q_B (verified),
and c216 = -m^{-1} mod 2^216 = 0x77686f6f... = ASCII "whoops_this_was_just_a_dlog".

The true private key n (< 2^76) satisfies (1 + n*m)*P_B = O. With s = v2(ord(P_B)):
  n = c216 (mod 2^s).  If s >= 76:  n = c216 mod 2^76  (unique).
GOLD check: build the full 2^216 isogeny of E_0 with kernel P_a + n*Q_a
(216 successive 2-isogenies, Vélu closed form) and compare the final
codomain equation with the public E_A.  Exact coefficient match => n correct.
"""
import re

txt = open("output.txt", encoding="utf-8").read()
p = int(re.search(r"Finite Field in i of size (\d+)\^2", txt).group(1))
assert p == (2**216 * 3**137 - 1)

def parse_point(name):
    m = re.search(name + r" = \((\d+)\*i \+ (\d+) : (\d+)\*i \+ (\d+) : 1\)", txt)
    return ((int(m.group(2)), int(m.group(1))), (int(m.group(4)), int(m.group(3))))

PB = parse_point(r"phi_a\(P_b\)")
QB = parse_point(r"phi_a\(Q_b\)")
Pa = parse_point("P_a")
Qa = parse_point("Q_a")

am = re.search(r"E_A = Elliptic Curve defined by y\^2 = x\^3 \+ \((\d+)\*i\+(\d+)\)\*x \+ \((\d+)\*i\+(\d+)\)", txt)
aA = (int(am.group(2)), int(am.group(1)))
bA = (int(am.group(4)), int(am.group(3)))
a0, b0 = (0, 0), (1, 0)   # E_0: y^2 = x^3 + 1

def f2(a, b=0):
    if isinstance(a, tuple): return (a[0] % p, a[1] % p)
    return (a % p, b % p)
def _n(x): return x if isinstance(x, tuple) else f2(x)
def f2_add(a, b): a,b=_n(a),_n(b); return ((a[0]+b[0])%p,(a[1]+b[1])%p)
def f2_sub(a, b): a,b=_n(a),_n(b); return ((a[0]-b[0])%p,(a[1]-b[1])%p)
def f2_neg(a): a=_n(a); return ((-a[0])%p,(-a[1])%p)
def f2_mul(a, b): a,b=_n(a),_n(b); return ((a[0]*b[0]-a[1]*b[1])%p,(a[0]*b[1]+a[1]*b[0])%p)
def f2_inv(a): d=pow(a[0]*a[0]+a[1]*a[1],p-2,p); return ((a[0]*d)%p,(-a[1]*d)%p)
def f2_div(a, b): a,b=_n(a),_n(b); return f2_mul(a,f2_inv(b))
def f2_eq(a, b): return a[0]==b[0] and a[1]==b[1]
ONE,I = (1,0),(0,1)

def on_curve(P, a, b):
    if P is None: return True
    x,y = P
    return f2_eq(f2_mul(y,y), f2_add(f2_add(f2_mul(f2_mul(x,x),x), f2_mul(a,x)), b))

def ec_add(P, Q, a, b):
    if P is None: return Q
    if Q is None: return P
    x1,y1,x2,y2 = P[0],P[1],Q[0],Q[1]
    if f2_eq(x1,x2):
        if f2_eq(f2_add(y1,y2),(0,0)): return None
        lam = f2_div(f2_add(f2_mul(3,f2_mul(x1,x1)),a), f2_mul(2,y1))
    else:
        lam = f2_div(f2_sub(y2,y1), f2_sub(x2,x1))
    x3 = f2_sub(f2_sub(f2_mul(lam,lam),x1),x2)
    y3 = f2_sub(f2_mul(lam,f2_sub(x1,x3)),y1)
    return (x3,y3)

def ec_mul(P, n, a, b):
    R = None
    while n:
        if n & 1: R = ec_add(R,P,a,b)
        P = ec_add(P,P,a,b)
        n >>= 1
    return R

assert on_curve(Pa, a0, b0) and on_curve(Qa, a0, b0), "P_a,Qa not on E_0"
assert on_curve(PB, aA, bA) and on_curve(QB, aA, bA), "P_B,Q_B not on E_A"

# ---------- m (recompute, reuse solve.py's verified value) ----------
# from solve.py: m = 0xeac325184e820daac7ca1ea989e8002c894189e01e93b0e199c3a9
m = 0xeac325184e820daac7ca1ea989e8002c894189e01e93b0e199c3a9
assert f2_eq(ec_mul(PB, m, aA, bA), QB), "m*P_B != Q_B"
print(f"m = {m:#x}  (m*P_B == Q_B verified)")

c216 = (-pow(m, -1, 2**216)) % 2**216
ascii_str = bytes.fromhex(format(c216, '056x')).decode()
print(f"c216 = {c216:#x}")
print(f"c216 as ASCII: {ascii_str!r}")

# ---------- order of P_B (binary search on s) ----------
def has_order_2s(s):
    return ec_mul(PB, 2**s, aA, bA) is None

lo, hi = 1, 216
while lo < hi:
    mid = (lo + hi) // 2
    if has_order_2s(mid):
        hi = mid
    else:
        lo = mid + 1
s = lo
print(f"v2(ord(P_B)) = s = {s}")
if s >= 76:
    n = c216 % 2**76
    print(f"s >= 76: unique candidate n = c216 mod 2^76 = {n:#x} = {n} ({n.bit_length()} bits)")
else:
    print(f"s = {s} < 76: n = c216 mod 2^{s} + k*2^{s}, 2^{76-s} candidates")
    n = c216 % 2**76  # try k=0 first (low 76 bits)

# ---------- GOLD check: Vélu 2^216 isogeny, kernel P_a + n*Q_a ----------
def velu2_step(Ea, Eb, R):
    """Degree-2 Vélu isogeny with kernel {O, R, -R}. Returns (a', b', phi).
    Closed forms (y^2 = x^3 + a x + b, R = (u, v), 2R = O, f(x) = x^3+ax+b):
      x'(x) = 2(v^2 + f(x)) / (u - x)^2 - u
      dx'/dx = [ 2 f'(x)(u-x) + 4(v^2 + f(x)) ] / (u-x)^3,  f'(x) = 3x^2 + a
      y' = y * dx'/dx
      =>  RHS'(X) = f(x) * [ 2 f'(x)(u-x) + 4(v^2 + f(x)) ]^2 / (u-x)^6
    (a', b') fitted by evaluating the identity at sample x's (sign-agnostic)."""
    a, b = Ea, Eb
    u, v = R
    v2 = f2_mul(v, v)
    def f_of(x):
        return f2_add(f2_add(f2_mul(f2_mul(x, x), x), f2_mul(a, x)), b)
    def Xof(x):
        y2 = f_of(x)
        d = f2_sub(u, x)
        return f2_sub(f2_div(f2_mul(2, f2_add(v2, y2)), f2_mul(d, d)), u), y2
    def rhsval(x):
        y2 = f_of(x)
        fp = f2_add(f2_mul(3, f2_mul(x, x)), a)
        d = f2_sub(u, x)
        num1 = f2_add(f2_mul(2, f2_mul(fp, d)), f2_mul(4, f2_add(v2, y2)))
        num = f2_mul(f2_mul(y2, f2_mul(num1, num1)), 1)
        d2 = f2_mul(d, d)
        den = f2_mul(f2_mul(d2, d2), d2)
        return f2_div(num, den)
    samples = [(5, 1), (7, 1), (11, 1), (13, 1), (17, 1)]
    rows = []
    for sr, si in samples:
        x = f2(sr, si)
        X, _ = Xof(x)
        rows.append((X, rhsval(x)))
    (X1, V1), (X2, V2) = rows[0], rows[1]
    ap = f2_div(f2_sub(V2, V1), f2_sub(X2, X1))   # a' = (V2-V1)/(X2-X1)
    bp = f2_sub(V1, f2_mul(ap, X1))               # b' = V1 - a' X1
    for X, V in rows:
        got = f2_add(f2_add(f2_mul(f2_mul(X, X), X), f2_mul(ap, X)), bp)
        assert f2_eq(got, V), f"codomain fit failed at X={X}"
    def phi(P):
        if P is None: return None
        x, y = P
        y2 = f_of(x)
        d = f2_sub(u, x)
        fp = f2_add(f2_mul(3, f2_mul(x, x)), a)
        num1 = f2_add(f2_mul(2, f2_mul(fp, d)), f2_mul(4, f2_add(v2, y2)))
        num = f2_mul(f2_mul(y, num1), 1)
        den = f2_mul(f2_mul(d, d), d)
        yp = f2_div(num, den)
        X, _ = Xof(x)
        return (X, yp)
    return ap, bp, phi

print("building 2^216 isogeny (216 Vélu 2-steps) with kernel P_a + n*Q_a ...")
a, b = a0, b0
R = ec_add(Pa, ec_mul(Qa, n, a0, b0), a0, b0)
assert R is not None
assert ec_mul(R, 2**216, a0, b0) is None, "kernel order check"
assert ec_mul(R, 2**215, a0, b0) is not None, "kernel order must be exactly 2^216 (n odd)"
Rk = R
for step in range(216):
    # kernel point for this 2-step: 2^(215-step) * Rk  (order 2)
    K = ec_mul(Rk, 2**(215 - step), a, b)
    assert K is not None and ec_add(K, K, a, b) is None, f"kernel point not order 2 at step {step}"
    a, b, phi = velu2_step(a, b, K)
    Rk = phi(Rk)
    if step % 32 == 0:
        print(f"  step {step:3d}  Rk = {ec_mul(Rk, 2**(215-step+1-1), a, b) is None}")
assert Rk is None, "Rk should map to O"
print(f"final codomain: a' = {a[0]}+{a[1]}i   b' = {b[0]}+{b[1]}i")
print(f"public E_A:      a  = {aA[0]}+{aA[1]}i   b  = {bA[0]}+{bA[1]}i")
match = f2_eq(a, aA) and f2_eq(b, bA)
print(f"CODEMATCH = {match}")
if match:
    print(f"\nGOLD VERIFICATION PASSED. n = {n} = {n:#x}")
    print(f"FLAG = [flag value withheld — real-flag strings live only under FLAGS/]}}")

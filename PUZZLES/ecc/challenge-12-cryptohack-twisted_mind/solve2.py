#!/usr/bin/env python3
# twisted_mind SOLVE: x-only ladder leaks k on BOTH E and its quadratic twist.
# k mod S (smooth part of #E, 102b) + k mod S' (smooth part of #E', 101.5b)
# -> lcm > N -> unique k in [0, N/2]; verify x([k]P)==A1 locally; get_flag.
import json, socket, math

p = 2**192 - 237
a = -3
b = 1379137549983732744405137513333094987949371790433997718123
N  = 6277101735386680763835789423072729104060819681027498877478
NE = 6277101735386680763835789423342603728143891207900570147842  # twist order
S_FACTS  = {2:1, 11:1, 269:1, 2985973:1, 1631363213:1, 123462957881:1}
SP_FACTS = {2:1, 3:3, 1607:1, 693493:1, 1483406443:1, 40202856427:1}
S  = 1
for q, e in S_FACTS.items():  S  *= q**e
SP = 1
for q, e in SP_FACTS.items(): SP *= q**e

def rhs(x): return (x*x*x + a*x + b) % p
def leg(x): return pow(x % p, (p-1)//2, p)
def sqrt_fp(x):
    r = pow(x, (p+1)//4, p)
    return r if r*r % p == x % p else None

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
    def __rmul__(s_, c): return Fp2(s_.u*c, s_.v*c, s_.t)
    def __eq__(s_, o): return s_.u % p == o.u % p and s_.v % p == o.v % p
    def inv(s_):
        n = (s_.u*s_.u - s_.t*s_.v*s_.v) % p
        ni = pow(n, -1, p)
        return Fp2(s_.u*ni % p, -s_.v*ni % p, s_.t)
    def __truediv__(s_, o): return s_ * o.inv()

def DIV(u, v):
    if isinstance(u, Fp2): return u / v if not isinstance(v, int) else u / Fp2(v, 0, u.t)
    return u * pow(v % p, -1, p) % p

def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        z = y1 + y2
        if (z == 0) if isinstance(z, int) else z.is_zero(): return None
        return pdbl(P)
    l = DIV(y2 - y1, x2 - x1)
    xr = l*l - x1 - x2
    return (xr, l*(x1 - xr) - y1)
def pdbl(P):
    if P is None: return None
    x, y = P
    l = DIV(3*x*x + a, 2*y)
    xr = l*l - 2*x
    return (xr, l*(x - xr) - y)
def pmul(k, P):
    R = None
    while k:
        if k & 1: R = padd(R, P)
        P = pdbl(P); k >>= 1
    return R
def is_zero(z): return z == 0 if isinstance(z, int) else z.is_zero()
Fp2.is_zero = lambda s_: s_.u % p == 0 and s_.v % p == 0

def bsgs(g, h, qe):
    """x in [0,qe) with [x]g = h (g of order qe)."""
    m = math.isqrt(qe) + 1
    table = {}
    j_g = None
    for j in range(m):
        key = None if j_g is None else (j_g[0], j_g[1])
        if key not in table: table[key] = j
        j_g = padd(j_g, g)
    mg = pmul(m, g)
    neg = (mg[0], -mg[1] if isinstance(mg[1], int) else mg[1].neg()) if mg else None
    gamma = h
    for i in range(m):
        key = None if gamma is None else (gamma[0], gamma[1])
        if key in table:
            x = i*m + table[key]
            if x < qe and pmul(x, g) == h: return x
        gamma = padd(gamma, neg)
    raise RuntimeError("bsgs fail")

def pohlig(P, T, M, facts):
    """k mod (prod q^e) given T = [k]P, using projections of order q^e."""
    res, mods = 0, []
    for q, e in facts.items():
        qe = q**e
        c = M // qe
        g = pmul(c, P)
        h = pmul(c, T)
        x = bsgs(g, h, qe)
        res = res + x * (res*0 + 1) * 0 + x  # placeholder replaced by CRT below
        res = x if not mods else crt_pair(res, math.prod(q2**e2 for q2, e2 in facts.items() if q2 < q) if False else mods_m(res, mods), x, qe)
        break  # (loop rewritten below)
    raise RuntimeError("unused")

def crt_pair(r1, m1, r2, m2):
    g = math.gcd(m1, m2)
    if (r2 - r1) % g: return None
    lcm = m1 // g * m2
    x = (r1 + m1 * pow(m1 // g, -1, m2 // g) * ((r2 - r1) // g)) % lcm
    return x, lcm

def pohlig(P, T, M, facts):
    out = []
    for q, e in facts.items():
        qe = q**e
        c = M // qe
        g = pmul(c, P); h = pmul(c, T)
        x = bsgs(g, h, qe)
        out.append((x, qe))
        print(f"  q={q}^{e}: k mod q^e = {x}", flush=True)
    r, m = 0, 1
    for x, qe in out:
        r, m = crt_pair(r, m, x, qe)
    return r, m

# ---- live session ----
s = socket.create_connection(("socket.cryptohack.org", 13416), timeout=30)
f = s.makefile("rwb")
print(f.readline().decode().strip())

x_on = 3
while leg(rhs(x_on)) != 1: x_on += 1
y_on = sqrt_fp(rhs(x_on))
x_tw = 5   # off-curve (t nonresidue), verified locally
r1 = json.loads((f.write(json.dumps({"option":"get_pubkey","x0":x_on}).encode()+b"\n"), f.flush(), f.readline())[2])
A1 = int(r1["pubkey"])
r2 = json.loads((f.write(json.dumps({"option":"get_pubkey","x0":x_tw}).encode()+b"\n"), f.flush(), f.readline())[2])
A2 = int(r2["pubkey"])
print("A1 =", A1, "\nA2 =", A2, flush=True)

# E side: full points
P  = (x_on, y_on)
y1 = sqrt_fp(rhs(A1))
T1 = (A1, y1)
print("PH on E (mod S):", flush=True)
rS, mS = pohlig(P, T1, N, S_FACTS)
# twist side over F_{p^2}
t_tw = rhs(x_tw)
Pp  = (Fp2(x_tw,0,t_tw), Fp2(0,1,t_tw))
# target y: y^2 = rhs(A2) in F_p; on twist y = w*s with w^2 = rhs(A2)/t
w = sqrt_fp(rhs(A2) * pow(t_tw, -1, p) % p)
Tp  = (Fp2(A2,0,t_tw), Fp2(0,w,t_tw))
print("PH on E' (mod S'):", flush=True)
rSP, mSP = pohlig(Pp, Tp, NE, SP_FACTS)

L = mS * mSP // math.gcd(mS, mSP)
print("lcm(S,S') bits:", L.bit_length(), " N bits:", N.bit_length())
cands = []
for s1 in (rS, (-rS) % mS):
    for s2 in (rSP, (-rSP) % mSP):
        cc = crt_pair(s1, mS, s2, mSP)
        if cc is None: continue
        c0, ll = cc
        for c in (c0, c0 - ll):
            if 0 <= c <= N//2:
                # local verify: x([c]P) == A1
                R = pmul(c, P)
                if R is not None and R[0] % p == A1:
                    cands.append(c)
cands = sorted(set(cands))
print("candidates:", cands, flush=True)

got = None
for c in cands:
    resp = json.loads((f.write(json.dumps({"option":"get_flag","privkey":str(c)}).encode()+b"\n"), f.flush(), f.readline())[2])
    print("try", c, "->", resp, flush=True)
    if "flag" in resp: got = resp["flag"]; break
f.close(); s.close()
print("FLAG:", got)

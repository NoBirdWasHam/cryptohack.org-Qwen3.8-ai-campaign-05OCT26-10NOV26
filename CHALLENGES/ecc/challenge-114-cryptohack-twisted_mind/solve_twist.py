#!/usr/bin/env python3
# twisted_mind SOLVE (timeout-aware): x-only ladder leaks k on E AND its twist.
# BSGS tables precomputed BEFORE connecting; live phase = 2 queries + giant steps + get_flag.
import json, socket, math, time

p = 2**192 - 237
a = -3
b = 1379137549983732744405137513333094987949371790433997718123
N  = 6277101735386680763835789423072729104060819681027498877478
NE = 6277101735386680763835789423342603728143891207900570147842
S_FACTS  = {2:1, 11:1, 269:1, 2985973:1, 1631363213:1, 123462957881:1}
SP_FACTS = {2:1, 3:3, 1607:1, 693493:1, 1483406443:1, 40202856427:1}

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
    def __hash__(s_): return hash((s_.u, s_.v))
    def inv(s_):
        n = (s_.u*s_.u - s_.t*s_.v*s_.v) % p
        ni = pow(n, -1, p)
        return Fp2(s_.u*ni % p, -s_.v*ni % p, s_.t)
    def __truediv__(s_, o): return s_ * o.inv()
    def is_zero(s_): return s_.u % p == 0 and s_.v % p == 0
    def neg(s_): return Fp2(-s_.u, -s_.v, s_.t)

def DIV(u, v):
    if isinstance(u, Fp2): return u / (v if not isinstance(v, int) else Fp2(v, 0, u.t))
    return u * pow(v % p, -1, p) % p
def NEG(y): return -y if isinstance(y, int) else y.neg()
def RED(z): return z % p if isinstance(z, int) else z
def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        z = y1 + y2
        if (z % p == 0) if isinstance(z, int) else z.is_zero(): return None
        return pdbl(P)
    l = DIV(y2 - y1, x2 - x1)
    xr = RED(l*l - x1 - x2)
    return (xr, RED(l*(x1 - xr) - y1))
def pdbl(P):
    if P is None: return None
    x, y = P
    if (y == 0) if isinstance(y, int) else y.is_zero(): return None
    l = DIV(3*x*x + a, 2*y)
    xr = RED(l*l - 2*x)
    return (xr, RED(l*(x - xr) - y))
def pmul(k, P):
    R = None
    while k:
        if k & 1: R = padd(R, P)
        P = pdbl(P); k >>= 1
    return R

def crt_pair(r1, m1, r2, m2):
    g = math.gcd(m1, m2)
    if (r2 - r1) % g: return None
    lcm = m1 // g * m2
    x = (r1 + m1 * pow(m1 // g, -1, m2 // g) * ((r2 - r1) // g)) % lcm
    return x, lcm

def build_table(g, qe):
    m = math.isqrt(qe) + 1
    table = {}
    j_g = None
    for j in range(m):
        key = None if j_g is None else (j_g[0], j_g[1])
        if key not in table: table[key] = j
        j_g = padd(j_g, g)
    return m, table
def giant(g, h, qe, m, table):
    mg = pmul(m, g)
    step = (mg[0], NEG(mg[1])) if mg else None
    gamma = h
    for i in range(m + 1):
        key = None if gamma is None else (gamma[0], gamma[1])
        j = table.get(key)
        if j is not None:
            x = i*m + j
            if x < qe and pmul(x, g) == h: return x
        gamma = padd(gamma, step)
    raise RuntimeError("bsgs fail")

def prep(P, M, facts):
    out = []
    for q, e in facts.items():
        qe = q**e
        c = M // qe
        g = pmul(c, P)
        assert g is not None, f"degenerate projection q={q}: base point misses factor {q}"
        assert pmul(qe // q, g) is not None, f"base point order misses full q^{e} for q={q}"
        m, table = build_table(g, qe)
        out.append((qe, c, g, m, table))
        print(f"  table q^e={qe}: m={m}", flush=True)
    return out
def solve_residues(pre, T):
    r, m0 = 0, 1
    for qe, c, g, m, table in pre:
        h = pmul(c, T)
        x = giant(g, h, qe, m, table)
        r, m0 = crt_pair(r, m0, x, qe)
    return r, m0

# fixed base points (tables built pre-connection); base point must cover all of S
x_on = 3
while True:
    while leg(rhs(x_on)) != 1: x_on += 1
    y_on = sqrt_fp(rhs(x_on))
    P = (x_on, y_on)
    try:
        print("precomputing E-side tables:", flush=True)
        preE = prep(P, N, S_FACTS)
        break
    except AssertionError as ex:
        print("reject x_on =", x_on, ":", ex, flush=True)
        x_on += 1
x_tw = 5
t0 = time.time()
while True:
    while leg(rhs(x_tw)) != p-1: x_tw += 1
    t_tw = rhs(x_tw)
    Pp = (Fp2(x_tw,0,t_tw), Fp2(0,1,t_tw))
    try:
        print("precomputing twist-side tables:", flush=True)
        preT = prep(Pp, NE, SP_FACTS)
        break
    except AssertionError as ex:
        print("reject x_tw =", x_tw, ":", ex, flush=True)
        x_tw += 1
print(f"precompute done in {time.time()-t0:.0f}s", flush=True)

# ---- live ----
s = socket.create_connection(("socket.cryptohack.org", 13416), timeout=180)
f = s.makefile("rwb")
for _ in range(3):   # 3-line banner
    print(f.readline().decode().strip())
f.write(json.dumps({"option":"get_pubkey","x0":x_on}).encode()+b"\n"); f.flush()
A1 = int(json.loads(f.readline())["pubkey"])
f.write(json.dumps({"option":"get_pubkey","x0":x_tw}).encode()+b"\n"); f.flush()
A2 = int(json.loads(f.readline())["pubkey"])
print("A1 =", A1, "\nA2 =", A2, flush=True)

y1 = sqrt_fp(rhs(A1))
T1 = (A1, y1)
w = sqrt_fp(rhs(A2) * pow(t_tw, -1, p) % p)
Tp = (Fp2(A2,0,t_tw), Fp2(0,w,t_tw))

rS, mS = solve_residues(preE, T1)
print("k mod S =", rS, f"({mS.bit_length()}b) t={time.time()-t0:.0f}s", flush=True)
rSP, mSP = solve_residues(preT, Tp)
print("k mod S' =", rSP, f"({mSP.bit_length()}b) t={time.time()-t0:.0f}s", flush=True)

cands = []
for s1 in (rS, (-rS) % mS):
    for s2 in (rSP, (-rSP) % mSP):
        cc = crt_pair(s1, mS, s2, mSP)
        if cc is None: continue
        c0, ll = cc
        for c in (c0, c0 - ll):
            if 0 <= c <= N//2:
                R = pmul(c, P)
                if R is not None and R[0] % p == A1:
                    cands.append(c)
cands = sorted(set(cands))
print("candidates:", cands, flush=True)

got = None
for c in cands:
    f.write(json.dumps({"option":"get_flag","privkey":str(c)}).encode()+b"\n"); f.flush()
    resp = json.loads(f.readline())
    print("try", c, "->", resp, flush=True)
    if "flag" in resp: got = resp["flag"]; break
f.close(); s.close()
print("FLAG:", got)

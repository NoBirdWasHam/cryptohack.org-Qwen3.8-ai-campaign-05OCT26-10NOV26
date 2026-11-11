#!/usr/bin/env python3
# evil_twisted_mind — composite modulus, two-twist attack, extension-field BSGS.
# p = q1*q2; #E(Fq1)=order(prime), #twist(Fq1)=T1s*T1big; #E(Fq2)=E2(prime),
# #twist(Fq2)=S2s*R2. x0 = (R2*T1big)*xR with xR on twist over BOTH qi:
#   ord_q1(x0)|T1s (96b), ord_q2(x0)|S2s (97b). Oracle Y=x(k*x0).
# Per prime factor pp: BSGS in E(F_q^2) between G=(N/pp)*P0 and H=k*G -> k mod pp.
# CRT over 8 primes (2^193 > order) -> k exactly. Verify x(k*x0)==Y, submit.
import re, math, random, socket, json, ast

src = open("13418.py").read()
p = int(re.search(r"modulus\s*=\s*(\d+)", src).group(1))
a = -3
b = int(re.search(r"^b\s*=\s*(\d+)", src, re.M).group(1))
order = int(re.search(r"^order\s*=\s*(\d+)", src, re.M).group(1))
T1s_primes = [1965293129, 3945014767, 6911909839]
S2s_primes = [17, 1789, 8984179, 9381319, 83816652113]
T1s = math.prod(T1s_primes); S2s = math.prod(S2s_primes)
T1big = 89250943167080667773197903811
R2 = 22324892568046125682687618733
A_mul = R2 * T1big

def sxz(X1, Z1, m):
    XX = X1*X1 % m; ZZ = Z1*Z1 % m
    A2 = 2*((X1+Z1)**2 - XX - ZZ) % m
    aZZ = a*ZZ % m
    X3 = ((XX - aZZ)**2 - 2*b*A2*ZZ) % m
    Z3 = (A2*(XX + aZZ) + 4*b*ZZ*ZZ) % m
    return (X3, Z3)
def sdiff(X1, Z1, X2, Z2, xd, m):
    X1Z2 = X1*Z2 % m; X2Z1 = X2*Z1 % m; Z1Z2 = Z1*Z2 % m
    T = (X1Z2 + X2Z1)*(X1*X2 + a*Z1Z2) % m
    Z3 = (X1Z2 - X2Z1)**2 % m
    X3 = (2*T + 4*b*Z1Z2**2 - xd*Z3) % m
    return (X3, Z3)
def ladder_full(scalar, x0, m):
    if scalar == 0: return (1, 0)
    R0 = (x0, 1); R1 = sxz(*R0, m)
    n = scalar.bit_length(); pbit = 0; bit = 0
    for i in range(n-2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit: R0, R1 = R1, R0
        R1 = sdiff(*R0, *R1, x0, m)
        R0 = sxz(*R0, m)
        pbit = bit
    if bit: R0 = R1
    return R0
def ladder(scalar, x0, m):
    X, Z = ladder_full(scalar, x0, m)
    return None if Z == 0 else X * pow(Z, -1, m) % m
def legendre(n, q): return pow(n % q, (q-1)//2, q)
# server ladder implements x-only arithmetic on E: y^2 = x^3 + a*x + b  (a=-3)
def fval(x, m): return (x**3 + a*x + b) % m

# ---- factor p ----
rng = random.Random(2024)
while True:
    X, Z = ladder_full(order, rng.randrange(2, p), p)
    g = math.gcd(Z, p)
    if g not in (1, p): break
q1, q2 = sorted((g, p//g))
assert q1*q2 == p
print("factored p", flush=True)

# ---- x0 with full smooth order on both twists ----
def find_nr(q):
    while True:
        x = rng.randrange(2, q)
        if legendre(fval(x, q), q) == q-1: return x
for attempt in range(20):
    x1 = find_nr(q1); x2 = find_nr(q2)
    xR = (x1 * q2 * pow(q2, -1, q1) + x2 * q1 * pow(q1, -1, q2)) % p
    x0 = ladder(A_mul, xR, p)
    if x0 is None: continue
    if ladder(T1s, x0 % q1, q1) is not None: continue
    if ladder(S2s, x0 % q2, q2) is not None: continue
    ok = all(ladder(T1s//pp, x0 % q1, q1) is not None for pp in T1s_primes) and \
         all(ladder(S2s//pp, x0 % q2, q2) is not None for pp in S2s_primes)
    if ok: break
else:
    raise SystemExit("could not build x0")
print("x0 ready", flush=True)

# ---- oracle (connect LAST: server 60s timeout) ----
import os
HOST = os.environ.get("ETM_HOST", "socket.cryptohack.org")
PORT = int(os.environ.get("ETM_PORT", "13418"))
def connect():
    s = socket.create_connection((HOST, PORT), timeout=30)
    f = s.makefile("rwb")
    def send(o):
        f.write((json.dumps(o)+"\n").encode()); f.flush()
        return json.loads(f.readline().decode())
    banner = b""
    while banner.count(b"\n") < 3:
        ln = f.readline()
        if not ln: break
        banner += ln
    Y = int(send({"option": "get_pubkey", "x0": str(x0)})["pubkey"])
    return s, send, Y
# ---- quadratic extension F_q[i]/(i^2 = zq) ----
def make_ext(q):
    zq = 2
    while legendre(zq, q) != q-1: zq += 1
    def mul(P, Q):
        u, v = P; w, z = Q
        return ((u*w + zq*v*z) % q, (u*z + v*w) % q)
    def add(P, Q): return ((P[0]+Q[0]) % q, (P[1]+Q[1]) % q)
    def sub(P, Q): return ((P[0]-Q[0]) % q, (P[1]-Q[1]) % q)
    def neg(P): return ((-P[0]) % q, (-P[1]) % q)
    def inv(P):
        u, v = P
        d = (u*u - zq*v*v) % q
        di = pow(d, -1, q)
        return (u*di % q, (-v)*di % q)
    def smul(c, P):  # c int
        return (c*P[0] % q, c*P[1] % q)
    O = None
    def dbl(P):  # y^2 = x^3 + a x + b over F_q2
        if P is O: return O
        x, y = P
        if y == (0, 0): return O
        num = add(smul(3, mul(x, x)), (a % q, 0))
        lam = mul(num, inv(smul(2, y)))
        x3 = sub(mul(lam, lam), smul(2, x))
        y3 = sub(mul(lam, sub(x, x3)), y)
        return (x3, y3)
    def padd(P, Q):
        if P is O: return Q
        if Q is O: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            return O if y1 == neg(y2) else dbl(P)
        lam = mul(sub(y2, y1), inv(sub(x2, x1)))
        x3 = sub(sub(mul(lam, lam), (0, 0)), add(x1, x2))
        y3 = sub(mul(lam, sub(x1, x3)), y1)
        return (x3, y3)
    def pmul(k, P):
        R = O
        while k:
            if k & 1: R = padd(R, P)
            P = dbl(P); k >>= 1
        return R
    # sqrt in F_q2 via Tonelli-Shanks (generic)
    def sqrt_ext(w):
        if w == (0, 0): return (0, 0)
        # find non-residue g in F_q2: w^((q^2-1)/2) == -1
        e = (q*q - 1) // 2
        def powe(P, n):
            r = (1, 0)
            while n:
                if n & 1: r = mul(r, P)
                P = mul(P, P); n >>= 1
            return r
        g = (rng.randrange(1, q), rng.randrange(1, q))
        while True:
            g = ((g[0] + 1) % q, g[1])
            if g == (0, 0): g = (1, 1)
            if powe(g, e) == (q-1, 0): break
        Q = q - 1; S = 0
        while Q % 2 == 0: Q //= 2; S += 1
        c = powe(g, Q); t = powe(w, Q); r = powe(w, (Q+1)//2)
        while t != (1, 0):
            i = 0; t2 = t
            while t2 != (1, 0): t2 = mul(t2, t2); i += 1
            bb = powe(c, 1 << (S-i-1))
            c = mul(bb, bb); t = mul(t, c); r = mul(r, bb); S = i
        return r
    def sqrt_q(n):
        n %= q
        if n == 0: return 0
        if legendre(n, q) != 1: return None
        if q % 4 == 3: return pow(n, (q+1)//4, q)
        Q = q-1; S = 0
        while Q % 2 == 0: Q //= 2; S += 1
        z = 2
        while legendre(z, q) != q-1: z += 1
        m, c, t, r = S, pow(z, Q, q), pow(n, Q, q), pow(n, (Q+1)//2, q)
        while t != 1:
            i = 0; t2 = t
            while t2 != 1: t2 = t2*t2 % q; i += 1
            bb = pow(c, 1 << (m-i-1), q)
            m, c, t, r = i, bb*bb % q, t*bb*bb % q, r*bb % q
        return r
    def lift(xc):
        # point on E(F_q2) with x=xc: y^2 = f(xc); x as ext-field element
        xc = (xc % q, 0)
        n = fval(xc[0], q)
        t2 = n * pow(zq, -1, q) % q
        if legendre(t2, q) == 1:
            t = sqrt_q(t2)
            if t is not None:
                return (xc, (0, t))
        y = sqrt_ext((n, 0))
        return (xc, y)
    return dict(q=q, O=O, padd=padd, dbl=dbl, pmul=pmul, lift=lift, neg=neg)

def baby_table(E, G, pp):
    m = math.isqrt(pp) + 1
    table = {}
    cur = E["O"]
    for j in range(m):
        if cur not in table:
            table[cur] = j
        cur = E["padd"](cur, G)
    step = E["pmul"](m, G)
    return table, m, step

def giant(E, H, table, m, step, pp):
    q = E["q"]
    nstep = (step[0], ((-step[1][0]) % q, (-step[1][1]) % q))
    cur = H
    for i in range(m+1):
        if cur in table:
            return (i*m + table[cur]) % pp
        cur = E["padd"](cur, nstep)
    return None

# precompute per-prime data (P0 lifts, G points, baby tables) BEFORE connecting
jobs = []
for side, q, N, primes, x0c in (("q1", q1, T1s, T1s_primes, x0 % q1),
                                 ("q2", q2, S2s, S2s_primes, x0 % q2)):
    E = make_ext(q)
    P0 = E["lift"](x0c)
    # sanity: P0 on curve and N*P0 == O
    assert E["pmul"](N, P0) is E["O"]
    for pp in primes:
        c = N // pp
        G = E["pmul"](c, P0)
        tb, m, step = baby_table(E, G, pp)
        jobs.append((side, E, pp, G, tb, m, step))
        print(f"baby table {side} pp={pp} m={m}", flush=True)

s, send, Y = connect()
print("pubkey:", str(Y)[:40], "...", flush=True)
residues = {}
for side, E, pp, G, tb, m, step in jobs:
    q = E["q"]
    Hfull = E["lift"](Y % q)
    c = (T1s if side == "q1" else S2s) // pp
    Hs = E["pmul"](c, Hfull)
    d = giant(E, Hs, tb, m, step, pp)
    assert d is not None, f"bsgs failed pp={pp}"
    residues[pp] = d   # = eps_side * k mod pp (lift sign unknown; x-only can't tell)
    print(f"{side} pp={pp}: d={d}", flush=True)

def crt(res, primes):
    k = 0; M = 1
    for pp in primes:
        r = res[pp] % pp
        t = (r - k) * pow(M % pp, -1, pp) % pp
        k += M * t; M *= pp; k %= M
    return k, M

r1 = {pp: residues[pp] for pp in T1s_primes}
r2 = {pp: residues[pp] for pp in S2s_primes}
# x(k*x0)==Y holds for 4 classes (independent +- per CRT component).
# get_flag has NO attempt limit -> submit all four, priv is among them.
cands = set()
Mc = None
for s1 in (1, -1):
    for s2 in (1, -1):
        a1 = {pp: (s1 * r1[pp]) % pp for pp in T1s_primes}
        a2 = {pp: (s2 * r2[pp]) % pp for pp in S2s_primes}
        kc, Mc = crt({**a1, **a2}, T1s_primes + S2s_primes)
        Xv, Zv = ladder_full(kc, x0, p)
        xv = Xv * pow(Zv, -1, p) % p
        assert xv == Y, f"candidate {s1},{s2} fails x-verify"
        cands.add(kc); cands.add(Mc - kc)
cands = sorted(c for c in cands if 0 < c < Mc)
# privkey = raw 24-byte u < 2^192: try small-first
cands.sort()
print("candidates:", len(cands), [c.bit_length() for c in cands], flush=True)
k = None
for cand in cands:
    resp = send({"option": "get_flag", "privkey": cand})
    print("try", str(cand)[:24], "->", str(resp)[:120], flush=True)
    mm = re.search(r"crypto\{[^}]+\}", str(resp))
    if mm:
        k = cand
        open("flag.txt", "w").write(mm.group(0) + "\n")
        print("FLAG:", mm.group(0), flush=True)
        break
assert k is not None, "no candidate accepted"
s.close()

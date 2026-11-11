#!/usr/bin/env python
# evil_twisted_mind v3: ladder runs on OUR x0 with a=-3,b=1 on server modulus.
# Find prime p' ~ 2^251 with S | (p'+1), S = prod r^e smooth, S > 2*ORDER (~2^192).
# Each connection: x0 of order r^e | S -> leak k mod r^e (x-only PH with full-point model).
# CRT over the coprime r^e -> recover privkey (< ORDER/2 ~ 2^190). Submit same session.
import socket, json, sys, random
from Crypto.Util.number import isPrime

ORDER = 4782850957738000717885060297297408935631027604045525430677
A, B = -3, 1
HOST, PORT = "socket.cryptohack.org", 13418
O_PT = None

def curve_eq(x, p):
    return (x*x*x + (A - 2*B)*x*x + x) % p

def sqrt_mod(n, p):
    n %= p
    if n == 0: return 0
    if pow(n, (p-1)//2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p+1)//4, p)
    q = p - 1; s = 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q+1)//2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2*t2 % p; i += 1
        bb = pow(c, 1 << (m-i-1), p)
        m, c, t, r = i, bb*bb % p, t*bb*bb % p, r*bb % p
    return r

def pdbl(P, p):
    x, y = P
    if y == 0: return O_PT
    lam = (3*x*x + 2*(A - 2*B)*x + 1) * pow(2*y, -1, p) % p
    x3 = (lam*lam - (A - 2*B) - 2*x) % p
    y3 = (lam*(x - x3) - y) % p
    return (x3, y3)

def padd(P, Q, p):
    if P is O_PT: return Q
    if Q is O_PT: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return O_PT
        return pdbl(P, p)
    lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam*lam - (A - 2*B) - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def pmul(k, P, p):
    if k < 0: return pmul(-k, (P[0], (-P[1]) % p), p)
    R = O_PT
    while k:
        if k & 1: R = padd(R, P, p)
        P = pdbl(P, p)
        k >>= 1
    return R

def server_dbl(P, p, b):
    X1, Z1 = P
    XX = X1**2 % p; ZZ = Z1**2 % p
    AA = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % p
    aZZ = A * ZZ % p
    X3 = ((XX - aZZ) ** 2 - 2 * b * AA * ZZ) % p
    Z3 = (AA * (XX + aZZ) + 4 * b * ZZ**2) % p
    return (X3, Z3)

def server_diffadd(P1, P2, x0, p, b):
    X1, Z1 = P1; X2, Z2 = P2
    X1Z2 = X1 * Z2 % p; X2Z1 = X2 * Z1 % p; Z1Z2 = Z1 * Z2 % p
    T = (X1Z2 + X2Z1) * (X1 * X2 + A * Z1Z2) % p
    Z3 = (X1Z2 - X2Z1) ** 2 % p
    X3 = (2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % p
    return (X3, Z3)

def server_mul(scalar, x0, p, b):
    R0 = (x0 % p, 1); R1 = server_dbl(R0, p, b)
    n = scalar.bit_length(); pbit = 0; bit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit: R0, R1 = R1, R0
        R1 = server_diffadd(R0, R1, x0, p, b)
        R0 = server_dbl(R0, p, b)
        pbit = bit
    if bit: R0 = R1
    X, Z = R0
    if Z % p == 0: return None
    return X * pow(Z, -1, p) % p

def build_smooth(target_bits, primes):
    rng = random.Random(2024)
    S = 1; fac = {}
    while S.bit_length() < target_bits:
        r = rng.choice(primes)
        e = 1
        while S.bit_length() + r.bit_length() <= target_bits and rng.random() < 0.6:
            e += 1
            if (r**e).bit_length() * 2 > target_bits: break
        S *= r**e
        fac[r] = fac.get(r, 0) + e
        if S.bit_length() > target_bits + 6:
            # trim
            while S.bit_length() > target_bits and fac:
                r2 = max(fac)
                S //= r2; fac[r2] -= 1
                if fac[r2] == 0: del fac[r2]
    return S, fac

def find_curve(target_bits=205):
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71]
    rng = random.Random(7)
    tries = 0
    while tries < 4000:
        tries += 1
        S, fac = build_smooth(target_bits, primes)
        if max(fac) > 2**14: continue
        # p' = S*t - 1 ~ 2^251
        tbits = 251 - S.bit_length()
        if tbits < 8: continue
        for _ in range(400):
            t = rng.getrandbits(tbits) | 1
            p = S * t - 1
            if p.bit_length() != 251: continue
            if isPrime(p, 8):
                return p, S, fac
    raise RuntimeError("no curve found")

CACHE = "etm3_curve.json"
try:
    cj = json.load(open(CACHE))
    p, S = int(cj[0]), int(cj[1])
    fac = {int(k): v for k, v in cj[2].items()}
except Exception:
    p, S, fac = find_curve()
    json.dump([str(p), str(S), fac], open(CACHE, "w"))
print("p' found; S bits:", S.bit_length(), "fac:", fac, flush=True)

# verify #E = p+1 on samples
rng = random.Random(3)
done = 0
while done < 3:
    x = rng.randrange(2, p)
    y = sqrt_mod(curve_eq(x, p), p)
    if y is None: continue
    done += 1
    assert pmul(p + 1, (x, y), p) is O_PT, "not supersingular/order p+1"
# ladder model check
assert server_mul(2, x, p, 1) == pdbl((x, y), p)[0]
print("curve + ladder model verified", flush=True)

def point_on_curve(x, p):
    return sqrt_mod(curve_eq(x, p), p)

def find_point_order(pe, r, p):
    # random x on E, multiply by (p+1)/pe -> point of order pe (prob 1-1/r)
    rng = random.Random(pe)
    while True:
        x = rng.randrange(2, p)
        y = sqrt_mod(curve_eq(x, p), p)
        if y is None: continue
        R = pmul((p + 1) // pe, (x, y), p)
        if R is O_PT: continue
        if pmul(pe, R, p) is O_PT and pmul(pe // r, R, p) is not O_PT:
            return R

def recover_residue(Qx, P0, pe, r, p):
    # k mod pe up to sign; try both lifts of Q
    y = sqrt_mod(curve_eq(Qx, p), p)
    if y is None: return None
    G = pmul(pe // r, P0, p)  # order r
    # x-values of order-r subgroup <G>: {i*G}
    xs = {}
    cur = O_PT
    for i in range(r):
        key = None if cur is O_PT else cur[0]
        xs.setdefault(key, i)  # x identifies ±i
        cur = padd(cur, G, p)
    for lift in (y, (-y) % p):
        Q = (Qx, lift)
        kj = 0
        ok = True
        for j in range(int(pe.bit_length() and __import__('math').islog(pe, r)) if False else 0, 10**9):
            e = j
            if r**e > pe: break
            R = pmul(pe // (r ** (e + 1)), padd(Q, pmul(-kj, P0, p), p), p)
            key = None if R is O_PT else R[0]
            if key not in xs:
                ok = False; break
            d = xs[key]  # ±digit
            dj = (d * pow(r ** e, -1, r)) % r if False else d % r
            # R = digit * (pe/r^{e+1})*... careful: R in <G'>, G' order r; xs maps x->i mod r up to sign
            # digit ambiguity ±: try both
            for cand in {dj, (-dj) % r}:
                kj2 = kj + cand * (r ** e)
                R2 = pmul(pe // (r ** (e + 1)), padd(Q, pmul(-kj2, P0, p), p), p)
                if R2 is O_PT:
                    kj = kj2
                    break
            else:
                ok = False; break
        if ok:
            # verify up to sign
            if server_mul(kj, P0[0], p, 1) == Qx or server_mul((-kj) % pe, P0[0], p, 1) == Qx:
                return kj if server_mul(kj, P0[0], p, 1) == Qx else (-kj) % pe
    return None

# NOTE: recover_residue above is convoluted; simpler: brute digits with direct test.
def recover_residue2(Qx, P0, pe, r, p):
    y = sqrt_mod(curve_eq(Qx, p), p)
    if y is None: return None
    for lift in (y, (-y) % p):
        Q = (Qx, lift)
        kj = 0
        ok = True
        e = 0
        while r ** e < pe:
            step = r ** e
            # digit d in [0,r): check (Q - (kj + d*step)*P0) * (pe / r^{e+1}) == O
            found = None
            for d in range(r):
                R = pmul(pe // (r ** (e + 1)), padd(Q, pmul(-(kj + d * step), P0, p), p), p)
                if R is O_PT:
                    found = d; break
            if found is None:
                ok = False; break
            kj += found * step
            e += 1
        if ok:
            # Q should equal ±kj*P0
            if server_mul(kj, P0[0], p, 1) == Qx:
                return kj
            neg = (-kj) % pe
            if server_mul(neg, P0[0], p, 1) == Qx:
                return neg
    return None

class Session:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=15)
        self.s.settimeout(25)
        self.buf = b""
        self.readobj()
    def readobj(self):
        while True:
            try:
                o = json.loads(self.buf.decode())
                self.buf = self.buf[len(json.dumps(o)):]
                return o
            except Exception:
                d = self.s.recv(65536)
                if not d: return None
                self.buf += d
    def pubkey(self, x0):
        self.s.sendall((json.dumps({"option": "get_pubkey", "x0": str(x0)}) + "\n").encode())
        o = self.readobj()
        if "pubkey" not in o: raise RuntimeError(str(o))
        return int(o["pubkey"])
    def flag(self, privkey):
        self.s.sendall((json.dumps({"option": "get_flag", "privkey": privkey}) + "\n").encode())
        return self.readobj()
    def close(self):
        try: self.s.close()
        except Exception: pass

# precompute one point per prime power
pe_list = []
for r, e in fac.items():
    pe = r ** e
    P0 = find_point_order(pe, r, p)
    pe_list.append((r, e, pe, P0))
print("points ready for", [(r, e) for r, e, _, _ in pe_list], flush=True)

import itertools
best = None
for attempt in range(6):
    sess = Session()
    residues = []
    try:
        for r, e, pe, P0 in pe_list:
            Qx = sess.pubkey(P0[0])
            kj = recover_residue2(Qx, P0, pe, r, p)
            if kj is None:
                raise RuntimeError(f"recover failed r={r}")
            residues.append((kj, pe))
        # CRT
        x = 0; M = 1
        for kj, pe in residues:
            m = M
            t = ((kj - x) % pe) * pow(m % pe, -1, pe) % pe
            x += M * t
            M *= pe
        cands = {x % ORDER, (-x) % ORDER}
        for g in cands:
            o = sess.flag(g)
            print("guess", str(g)[:14], "->", str(o)[:90], flush=True)
            if o and "flag" in o:
                open("flag.txt", "w").write(o["flag"])
                print("FLAG:", o["flag"], flush=True)
                best = o["flag"]
                break
    except Exception as ex:
        print("attempt", attempt, "err:", ex, flush=True)
    sess.close()
    if best: break
print("done", flush=True)

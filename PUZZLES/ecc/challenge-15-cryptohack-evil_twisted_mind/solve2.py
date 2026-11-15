#!/usr/bin/env python
# evil_twisted_mind v2: server runs Montgomery ladder (a=-3,b=1) on ANY x0 we send.
# Choose prime p=2^251-c with #E: y^2=x^3-5x^2+x equal p+1=2^251 (smooth).
# x0 of order 2^200 -> ladder leaks k mod 2^200 per connection; CRT over ~10 conns.
import socket, json, sys, random
from Crypto.Util.number import isPrime

ORDER = 4782850957738000717885060297297408935631027604045525430677
A, B = -3, 1
HOST, PORT = "socket.cryptohack.org", 13418
O_PT = None

def curve_eq(x, p):
    return (x*x*x + (A - 2*B)*x*x + x) % p   # b*y^2 = x^3 + (a-2b)x^2 + x, b=1

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
    # b*y^2 = x^3 + (a-2b)x^2 + x with b=1: lam = (3x^2 + 2(a-2b)x + 1) / (2y)
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

def find_curve():
    c = 1
    while True:
        p = (1 << 251) - c
        if isPrime(p, 12):
            rng = random.Random(1)
            good = True
            done = 0
            while done < 4:
                x = rng.randrange(2, p)
                y = sqrt_mod(curve_eq(x, p), p)
                if y is None: continue
                done += 1
                if pmul(p + 1, (x, y), p) is not O_PT:
                    good = False; break
            if good:
                return p
        c += 1

CACHE = "etm_curve.json"
try:
    p = int(open(CACHE).read())
except Exception:
    p = find_curve()
    open(CACHE, "w").write(str(p))
print("curve prime found (2^251-c), #E=p+1 verified", flush=True)

# sanity: our full-point dbl agrees with server ladder dbl
rng = random.Random(5)
while True:
    x = rng.randrange(2, p)
    y = sqrt_mod(curve_eq(x, p), p)
    if y is not None: break
P = (x, y)
assert server_mul(2, P[0], p, 1) == pdbl(P, p)[0], "ladder/model mismatch"
assert server_mul(3, P[0], p, 1) == padd(pdbl(P, p), P, p)[0], "3P mismatch"
print("ladder model verified against full-point arithmetic", flush=True)

# order-2 x: root of x^2 + (a-2b)x + 1 = x^2 -5x + 1
disc = (A - 2*B)**2 - 4
sq = sqrt_mod(disc, p)
xG = (- (A - 2*B) + sq) * pow(2, -1, p) % p
assert curve_eq(xG, p) == 0

# x0 of exact order 2^200
rng = random.Random(99)
while True:
    x = rng.randrange(2, p)
    y = sqrt_mod(curve_eq(x, p), p)
    if y is None: continue
    P2 = pmul(1 << 51, (x, y), p)
    if P2 is O_PT: continue
    if pmul(1 << 199, P2, p) is O_PT: continue
    P0 = P2
    x0 = P0[0]
    assert server_mul(1 << 200, x0, p, 1) is None
    break
print("x0 of order 2^200 ready", flush=True)

def recover_k_mod(Qx, P0, p):
    y = sqrt_mod(curve_eq(Qx, p), p)
    if y is None: return None
    for lift in (y, (-y) % p):
        Q = (Qx, lift)
        kj = 0
        ok = True
        for j in range(200):
            R = pmul(1 << (199 - j), padd(Q, pmul(-kj, P0, p), p), p)
            if R is O_PT:
                bj = 0
            elif R[1] == 0:
                bj = 1
            else:
                ok = False; break
            if bj: kj += 1 << j
        if ok and server_mul(kj, x0, p, 1) == Qx:
            return kj
    return None

def session_round(x0):
    s = socket.create_connection((HOST, PORT), timeout=15)
    s.settimeout(25)
    buf = b""
    def readobj():
        nonlocal buf
        while True:
            try:
                o = json.loads(buf.decode())
                buf = buf[len(json.dumps(o)):]
                return o
            except Exception:
                d = s.recv(65536)
                if not d: return None
                buf += d
    readobj()
    s.sendall((json.dumps({"option": "get_pubkey", "x0": str(x0)}) + "\n").encode())
    o = readobj()
    s.close()
    if "pubkey" not in o:
        raise RuntimeError(f"unexpected: {o}")
    return int(o["pubkey"])

acc = None
M = 1 << 200
nconn = 0
while M <= 2 * ORDER and nconn < 16:
    try:
        Qx = session_round(x0)
    except Exception as ex:
        print("conn err", ex, flush=True)
        continue
    nconn += 1
    k200 = recover_k_mod(Qx, P0, p)
    if k200 is None:
        print("conn recover failed", flush=True)
        continue
    if acc is None:
        acc = k200
    else:
        Minv = pow(M % (1 << 200), -1, 1 << 200) if M % (1 << 200) else None
        # M is a power of two >= 2^200; inverse mod 2^200 doesn't exist!
        # mixed-radix base 2^200: acc = sum a_i 2^{200 i}; new residue r: a_m = (r - acc_low)?? 
        # acc mod 2^200 must equal r mod 2^200 -> consistency check only; need coprime moduli!
        # FIX: use moduli 2^200 from DIFFERENT bits? all same modulus -> no CRT gain.
        raise RuntimeError("CRT flaw: same modulus each conn")
    print("conn", nconn, "k mod 2^200:", str(k200)[:16], flush=True)

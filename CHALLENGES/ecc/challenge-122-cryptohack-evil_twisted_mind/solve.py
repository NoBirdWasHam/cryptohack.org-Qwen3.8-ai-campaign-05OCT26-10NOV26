#!/usr/bin/env python
# evil_twisted_mind: server runs Montgomery ladder with a=-3 on ANY x0 we send.
# We choose p = 2^251 - c prime and b with E: y^2 = x^3 - 3x^2 + x supersingular
# => #E = p+1 = 2^251 (smooth). Recover privkey mod 2^200 per connection (up to
# sign), CRT across ~10 connections, submit.
import socket, json, sys, random
from Crypto.Util.number import isPrime

MOD_SERVER = 22940775619019322596732579295592937688786860238433707977002010287174316620572298541233055185492572749161011953122651
ORDER = 4782850957738000717885060297297408935631027604045525430677
A = -3
HOST, PORT = "socket.cryptohack.org", 13418

def find_curve():
    c = 1
    while True:
        p = (1 << 251) - c
        if isPrime(p):
            b = 1
            while True:
                # supersingular test: trace t = 0 <=> #E = p+1. Cheap proxy:
                # for p = 3 mod 4, a=0 curve y^2=x^3+Ax is SS when... just test
                # 2^200 * P == O for random x on curve-or-twist:
                ok = True
                for x in (2, 3, 5, 7):
                    if not has_point(x, p, b):
                        continue
                    R = mont_mul(1 << 200, x, p, b)
                    if R is not None:
                        ok = False
                        break
                if ok:
                    # verify nontrivial: 2^199 * x != O for some x
                    good = False
                    for x in (2, 3, 5, 7):
                        if not has_point(x, p, b): continue
                        R = mont_mul(1 << 199, x, p, b)
                        if R is None:
                            good = True
                            break
                    if good:
                        return p, b
                b += 1
                if b > 50: break
        c += 1

def has_point(x, p, b):
    # exists y: y^2 = x^3 + (a-2b)x^2 + x  (Montgomery form with our dbl/diffadd params)
    # Our formulas correspond to: b*y^2 = x^3 + a*x^2 + x  (standard Montgomery).
    rhs = (x*x*x + A*x*x + x) % p
    return pow(rhs, (p - 1) // 2, p) in (0, 1)

def dbl(P, p, b):
    X1, Z1 = P
    XX = X1**2 % p
    ZZ = Z1**2 % p
    AA = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % p
    aZZ = A * ZZ % p
    X3 = ((XX - aZZ) ** 2 - 2 * b * AA * ZZ) % p
    Z3 = (AA * (XX + aZZ) + 4 * b * ZZ**2) % p
    return (X3, Z3)

def diffadd(P1, P2, x0, p, b):
    X1, Z1 = P1
    X2, Z2 = P2
    X1Z2 = X1 * Z2 % p
    X2Z1 = X2 * Z1 % p
    Z1Z2 = Z1 * Z2 % p
    T = (X1Z2 + X2Z1) * (X1 * X2 + A * Z1Z2) % p
    Z3 = (X1Z2 - X2Z1) ** 2 % p
    X3 = (2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % p
    return (X3, Z3)

def mont_mul(scalar, x0, p, b):
    # replicate server ladder exactly (it returns affine X/Z; Z==0 -> infinity)
    R0 = (x0 % p, 1)
    R1 = dbl(R0, p, b)
    n = scalar.bit_length()
    pbit = 0
    bit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit:
            R0, R1 = R1, R0
        R1 = diffadd(R0, R1, x0, p, b)
        R0 = dbl(R0, p, b)
        pbit = bit
    if bit:
        R0 = R1
    X, Z = R0
    if Z % p == 0:
        return None
    return X * pow(Z, -1, p) % p

def session_round(x0, p, b):
    s = socket.create_connection((HOST, PORT), timeout=15)
    s.settimeout(20)
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
    o = readobj()  # welcome
    s.sendall((json.dumps({"option": "get_pubkey", "x0": str(x0)}) + "\n").encode())
    o = readobj()
    s.close()
    if "pubkey" not in o:
        raise RuntimeError(f"unexpected: {o}")
    return int(o["pubkey"])

CACHE = "etm_curve.json"
try:
    cj = json.load(open(CACHE))
    p, b = int(cj[0]), int(cj[1])
except Exception:
    p, b = find_curve()
    json.dump([str(p), str(b)], open(CACHE, "w"))
print("curve p=2^251-c ok, b =", b, flush=True)

# find x0 of exact order 2^200
rng = random.Random(99)
while True:
    x0 = rng.randrange(2, p)
    if not has_point(x0, p, b):
        continue
    if mont_mul(1 << 200, x0, p, b) is not None:
        continue
    G199 = mont_mul(1 << 199, x0, p, b)
    if G199 is None:
        continue
    break
print("x0 found:", str(x0)[:30], "...", flush=True)

# collect residues k mod 2^200 (up to sign) from several connections
residues = []
for conn in range(12):
    Q = session_round(x0, p, b)
    # bit extraction: k mod 2^200 up to sign
    H = Q
    k = 0
    G = mont_mul(1 << 199, x0, p, b)  # element of order 2 (x-coord)
    ok = True
    for j in range(200):
        e = 199 - j
        Hj = mont_mul(1 << e, H, p, b) if e else H
        # Hj is either O (bit 0) or G (bit 1)
        if Hj is None:
            bj = 0
        elif Hj == G:
            bj = 1
        else:
            print("  anomaly at bit", j, "conn", conn, flush=True)
            ok = False
            break
        k += bj << j
        if bj:
            H = mont_mul((1 << j) + 1, H, p, b) if j else mont_mul(2, H, p, b)
            # H <- 2^j (H - k_j*G): subtract k_j*G then double j times
            # do explicitly: H1 = H - kG via ladder? x-only subtraction of order-2 elt:
            # subtracting G (order 2, x_G): x(P - G) = x(P + G) since G=-G. So add G:
            # x-only add by order-2 point: use diffadd with known x0? simpler: 
            # P+G: since G has order 2, P+G = P-G, x(P+G) computable via ladder only if we know x(P+G)... 
            # Use formula: for Montgomery, x(P+G) with x(G)=xG: from diffadd(P,G,x(P))... 
            # We'll just recompute H from scratch below instead.
            ok = False
            break
    if not ok:
        # fallback: brute per-bit via full recomputation
        # recover k by iterative: k_j known; H_j = (k - k_j)/2^j * x0 ; test bit via 2^(199-j)*H_j
        k = 0
        for j in range(200):
            # H_j = ((k - k_j) / 2^j) * x0 ; compute as 2^(200-j)?? unknown k... 
            # Instead: Qj = (2^(199-j)) * (Q - k_j*x0) ; but Q - k_j*x0 needs x-only subtraction of known multiple:
            # subtraction of k_j*x0 from Q: x(Q - R) with x(R) known requires y-sign -> NOT x-only possible in general.
            # BUT we can compute 2^(199-j)*Q and 2^(199-j)*k_j*x0 separately and ADD? x-only addition also needs sign.
            # Workaround: test bit via equality of x-coords: x(2^(199-j)*(Q - k_j x0)) equals x(2^(199-j)*Q - k_j*2^(199-j)*x0)...
            # sign issue again. Use the order-2 trick: 2^(199-j)*Q = k_j*G' + (bit)*G' where G' order 2 -> x is one of TWO values.
            A1 = mont_mul(1 << (199 - j), Q, p, b)
            # x(k_j*G') : k_j known; G' = 2^199*x0 = G (order2). k_j*G' mod 2 = k_j & 1? no: k_j*G' = (k_j mod 2)*G
            # since G order 2. So x = O if (k_j&1)==0 else G. But bit j depends on (k - k_j)/2^j parity = bit j of k. 
            # x(2^(199-j)*Q) = x((k mod 2^{j+1})/2^j * G + 2*...) = x( bit_j * G ) -> O or G. k_j&1 already encodes bit0 only.
            # Actually 2^(199-j)*Q = (k mod 2^{j+1}) * G = (k_j + bit_j*2^j)*G = (k_j mod 2)*G + bit_j*(2^j G) = (k_j&1)*G.
            # that kills bit j>0! need larger order base: use x0 itself order 2^200: 
            # 2^(199-j)*Q has order 2^{j+1}... I overcomplicated: standard bit test needs sign. Use pair of x-values.
            break
        raise RuntimeError("x-only bit extraction needs the two-x trick; implement next")
    residues.append(k)
    print("conn", conn, "k mod 2^200 =", str(k)[:20], flush=True)
    if len(residues) >= 10:
        break
print("residues:", len(residues))

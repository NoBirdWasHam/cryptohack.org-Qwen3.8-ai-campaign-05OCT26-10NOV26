#!/usr/bin/env python3
"""
CryptoHack 'Ticket Maestro' (snark-maestro / ticket_maestro-cryptohack2024).

Vuln: Groth16 proof malleability. The verifier checks only
    e(A,B) == e(alpha,beta) * e(L,delta) * e(C,gamma)
so for any r != 0, (rA, r^{-1}B, C) is a valid proof of the SAME statement.
Ticket id = blake2b(digest || serialized proof) differs -> double-spend.

Econ: start 10, BuyTicket -2, Redeem +1, BuyFlag -20.
Buy one ticket, redeem it, then re-randomize it 11+ times to reach 20.
"""
import socket, json, random, sys

HOST, PORT = "archive.cryptohack.org", 26896

# BN254 base/curve order
p = 0x30644E72E131A029B85045B68181585D97816A916871CA8D3C208C16D87CFD47
n = 0x30644E72E131A029B85045B68181585D2833E84879B9709143E1F593F0000001

# ---------- G1 (over Fp) ----------
def g1_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        m = 3 * x1 * x1 % p * pow(2 * y1, p - 2, p) % p
    else:
        m = (y2 - y1) % p * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def g1_mul(k, P):
    R = None
    while k:
        if k & 1: R = g1_add(R, P)
        P = g1_add(P, P); k >>= 1
    return R

# ---------- Fq2 = Fp[u]/(u^2+1) ----------
def f2_add(a, b): return ((a[0]+b[0]) % p, (a[1]+b[1]) % p)
def f2_sub(a, b): return ((a[0]-b[0]) % p, (a[1]-b[1]) % p)
def f2_mul(a, b):
    return ((a[0]*b[0] - a[1]*b[1]) % p, (a[0]*b[1] + a[1]*b[0]) % p)
def f2_inv(a):
    nrm = pow((a[0]*a[0] + a[1]*a[1]) % p, p-2, p)
    return (a[0]*nrm % p, (-a[1]*nrm) % p)

# ---------- G2 (over Fq2) ----------
def g2_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if f2_add(y1, y2) == (0, 0): return None
        m = f2_mul(f2_mul(x1, x1), f2_inv(f2_add(y1, y1)))
        m = f2_mul((3, 0), m)
    else:
        m = f2_mul(f2_sub(y2, y1), f2_inv(f2_sub(x2, x1)))
    x3 = f2_sub(f2_sub(f2_mul(m, m), x1), x2)
    y3 = f2_sub(f2_mul(m, f2_sub(x1, x3)), y1)
    return (x3, y3)

def g2_mul(k, P):
    R = None
    while k:
        if k & 1: R = g2_add(R, P)
        P = g2_add(P, P); k >>= 1
    return R

# ---------- ark-serialize 0.3.0 COMPRESSED (LE, SWFlags in top 2 bits of last byte) ----------
# bit7 = "y > -y" (positive), bit6 = infinity. G2: flags on last byte of c1;
# Fq2 ordering compares (c1, c0) lexicographically (ark-ff 0.3.0 quadratic_extension.rs).
def le32(x): return x.to_bytes(32, "little")
def un32(b): return int.from_bytes(b, "little")

B2 = None  # twist b' = 3/(9+u), set lazily
def twist_b():
    global B2
    if B2 is None: B2 = f2_mul((3, 0), f2_inv((9, 1)))
    return B2

def sqrt_fp(a):
    assert p % 4 == 3
    r = pow(a, (p + 1) // 4, p)
    if r * r % p != a % p: raise ValueError("no sqrt")
    return r

def sqrt_f2(z):
    # complex method, mirrors ark-ff 0.3.0 QuadExtField::sqrt
    z0, z1 = z
    if z1 == 0: return (sqrt_fp(z0), 0)
    norm = (z0 * z0 + z1 * z1) % p
    alpha = sqrt_fp(norm)
    two_inv = pow(2, p - 2, p)
    delta = (alpha + z0) * two_inv % p
    if pow(delta, (p - 1) // 2, p) != 1:  # QNR
        delta = (delta - alpha) % p
    c0 = sqrt_fp(delta)
    c1 = z1 * two_inv % p * pow(c0, p - 2, p) % p
    r = (c0, c1)
    if f2_mul(r, r) != z: raise ValueError("no sqrt in Fq2")
    return r

def fp_positive(y): return y > (p - y) % p  # y > -y as integers
def f2_positive(y):
    ny = ((p - y[0]) % p, (p - y[1]) % p)
    return (y[1], y[0]) > (ny[1], ny[0])  # (c1,c0) lex

def parse_g1(bs):
    last = bs[31]
    positive = (last >> 7) & 1 == 1
    assert (last >> 6) & 1 == 0, "infinity not supported"
    x = un32(bs[:31] + bytes([last & 0x3F]))
    y = sqrt_fp((x * x % p * x + 3) % p)
    # ark-ec: keep y iff (y < -y) XOR positive  =>  negate iff (y < -y) == positive
    if (y < (p - y) % p) == positive: y = (p - y) % p
    return (x, y)

def parse_g2(bs):
    c0 = un32(bs[0:32])
    last = bs[63]
    positive = (last >> 7) & 1 == 1
    assert (last >> 6) & 1 == 0, "infinity not supported"
    c1 = un32(bs[32:63] + bytes([last & 0x3F]))
    x = (c0, c1)
    y = sqrt_f2(f2_add(f2_mul(x, f2_mul(x, x)), twist_b()))
    if f2_lt(y) == positive: y = ((p - y[0]) % p, (p - y[1]) % p)
    return (x, y)

def f2_lt(y):  # y < -y under (c1,c0) lex order
    ny = ((p - y[0]) % p, (p - y[1]) % p)
    return (y[1], y[0]) < (ny[1], ny[0])

def ser_g1(P):
    x, y = P
    b = bytearray(le32(x))
    if fp_positive(y): b[31] |= 0x80
    return bytes(b)

def ser_g2(P):
    (x0, x1), _ = P
    b = bytearray(le32(x1))
    if f2_positive(P[1]): b[31] |= 0x80
    return le32(x0) + bytes(b)

def parse_proof(hexstr):
    bs = bytes.fromhex(hexstr)
    assert len(bs) == 128, f"unexpected proof length {len(bs)}"
    return parse_g1(bs[0:32]), parse_g2(bs[32:96]), parse_g1(bs[96:128])

def ser_proof(a, b, c):
    return (ser_g1(a) + ser_g2(b) + ser_g1(c)).hex()

def malleabilize(hexstr, r):
    a, b, c = parse_proof(hexstr)
    a2 = g1_mul(r, a)
    b2 = g2_mul(pow(r, n-2, n), b)   # r^{-1} mod n
    return ser_proof(a2, b2, c)

# ---------- protocol ----------
class Rem:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=60)
        self.f = self.s.makefile("rwb")
    def line(self):
        return json.loads(self.f.readline().decode())
    def req(self, obj):
        self.f.write((json.dumps(obj) + "\n").encode()); self.f.flush()
        return self.line()

def main():
    rem = Rem(HOST, PORT)
    print("hello:", rem.line())

    t = rem.req("BuyTicket")
    proof0 = t["Ticket"]["proof"]
    print("bought ticket, proof len(hex) =", len(proof0))

    print("redeem original:", rem.req({"Redeem": {"proof": proof0}}))

    forged = 0
    while True:
        bal = rem.req("Balance")["Balance"]
        if bal >= 20:
            break
        rr = random.randrange(2, n-1)
        fp = malleabilize(proof0, rr)
        resp = rem.req({"Redeem": {"proof": fp}})
        if "GoodTicket" not in resp:
            print("FORGE FAILED:", resp); sys.exit(1)
        forged += 1
        bal2 = rem.req("Balance")["Balance"]
        print(f"forged redeem #{forged} ok (balance now {bal2})")

    print("final balance:", rem.req("Balance"))
    flag = rem.req("BuyFlag")
    print("FLAG RESP:", flag)
    if "Flag" in flag:
        open("flag_snark-maestro.txt", "w").write(flag["Flag"] + "\n")
        print("FLAG:", flag["Flag"])

if __name__ == "__main__":
    main()

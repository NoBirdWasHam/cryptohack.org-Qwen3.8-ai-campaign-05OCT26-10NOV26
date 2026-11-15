#!/usr/bin/env python3
# An Exceptional Twisted Mind (CryptoHack, socket 13417)
#
# Attack (p-adic, Smart-style via [N]-annihilation of the Teichmuller part):
#   Server returns r = x([k]P~) mod p^2 for our chosen x0 (P~ = point on E/Z_p^2
#   with x = x0; if f(x0) is a QR mod p it lifts to E, else to the twist - the
#   x-only ladder is the same rational function either way).
#   Lift r to a full point Q~ = (r, sqrt(f(r))) mod p^2 (f(r) is a QR mod p^2
#   because r = x of a genuine point mod p). Then Q~ = +- [k]P~ in E(Z/p^2).
#   For any R~ in E(Z/p^2) with R~bar of order N: [N]R~ lies in E_1 = ker(red),
#   and E_1 is ADDITIVE mod p^2 (formal group has no degree-2 term since a1=a3=0).
#   Define u(R~) = t([N]R~)/p in Z/p where t = -x/y is the formal parameter.
#   Then u(Q~) = +- k * u(P~) mod p  =>  k = +- u(Q)/u(P) mod p.
#   Computing u without touching E_1: [N]R~ = R~ + [N-1]R~ is the degenerate
#   chord x1 = x0 + p*d', y1 = -y0 + ... ; working out t = -x/y to first order
#   in p gives  u = d' * (y0 - y1)^{-1} mod p  with d' = (x0 - x1)/p mod p.
#   The +- (sqrt sign) is exactly the min(k, N-k) ambiguity -> submit both.
import sys, json, socket, time, random
from Crypto.Util.number import inverse

p = (1 << 256) - 189
p2 = p * p
a = -3
b = 152961
N = 115792089237316195423570985008687907853233080465625507841270369819257950283813

def f2(x):
    return (x**3 + a * x + b) % p2

def sqrt_p(v):
    s = pow(v % p, (p + 1) // 4, p)
    assert (s * s - v) % p == 0, "not a QR mod p"
    return s

def sqrt_p2(v):
    y0 = sqrt_p(v)
    d = (v - y0 * y0) % p2
    assert d % p == 0
    t = (d // p) * inverse(2 * y0, p) % p
    return (y0 + t * p) % p2

def add_aff(A, B):
    """affine addition mod p^2; assumes non-degenerate (result not in E_1)."""
    if A is None: return B
    if B is None: return A
    x1, y1 = A; x2, y2 = B
    if A == B:
        lam = (3 * x1 * x1 + a) * inverse(2 * y1, p2) % p2
    else:
        if x1 == x2:
            assert (y1 + y2) % p2 == 0
            return None
        lam = (y2 - y1) * inverse(x2 - x1, p2) % p2
    x3 = (lam * lam - x1 - x2) % p2
    y3 = (lam * (x1 - x3) - y1) % p2
    return (x3, y3)

def mul_aff(m, P):
    R = None
    while m:
        if m & 1: R = add_aff(R, P)
        P = add_aff(P, P); m >>= 1
    return R

def u_of(x0, y0):
    """u = t([N]P~)/p mod p for P~ = (x0,y0) with P~bar of order N."""
    x1, y1 = mul_aff(N - 1, (x0 % p2, y0))
    assert x1 % p == x0 % p and (y1 + y0) % p == 0, "sanity: [N-1]P~ = -P~ mod p"
    d = ((x0 - x1) % p2) // p
    nu = (y0 - y1) % p
    return (d % p) * inverse(nu, p) % p

def attack(x0, r):
    P = (x0 % p2, sqrt_p2(f2(x0)))
    Q = (r % p2, sqrt_p2(f2(r)))
    uP = u_of(*P)
    uQ = u_of(*Q)
    assert uP != 0, "degenerate x0 (Teichmuller lift); pick another"
    k1 = uQ * inverse(uP, p) % p
    return [k1, (p - k1) % p]

def priv_of(k):
    return min(k % N, (N - k) % N)

def pick_x0():
    x = 2
    while True:
        try:
            sqrt_p((x**3 + a * x + b) % p)
            return x
        except AssertionError:
            x += 1

# ---------------- server ladder clone (local sim / verification) ------------
def dbl_l(P1):
    X1, Z1 = P1
    XX = X1**2 % p2; ZZ = Z1**2 % p2
    A = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % p2
    aZZ = a * ZZ % p2
    X3 = ((XX - aZZ) ** 2 - 2 * b * A * ZZ) % p2
    Z3 = (A * (XX + aZZ) + 4 * b * ZZ**2) % p2
    return (X3, Z3)

def diffadd_l(P1, P2, x0):
    X1, Z1 = P1; X2, Z2 = P2
    X1Z2 = X1 * Z2 % p2; X2Z1 = X2 * Z1 % p2; Z1Z2 = Z1 * Z2 % p2
    T = (X1Z2 + X2Z1) * (X1 * X2 + a * Z1Z2) % p2
    Z3 = (X1Z2 - X2Z1) ** 2 % p2
    X3 = (2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % p2
    return (X3, Z3)

def scalarmult(scalar, x0):
    from math import gcd
    R0 = (x0, 1); R1 = dbl_l(R0)
    n = scalar.bit_length(); pbit = 0; bit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit: R0, R1 = R1, R0
        R1 = diffadd_l(R0, R1, x0)
        R0 = dbl_l(R0)
        pbit = bit
    if bit: R0 = R1
    if gcd(R0[1], p2) != 1:
        return "Infinity"
    return R0[0] * inverse(R0[1], p2) % p2

def solve_local(trials=10):
    x0 = pick_x0()
    ok = 0
    for _ in range(trials):
        k = random.randrange(1, N)
        r = scalarmult(k, x0)
        cands = attack(x0, r)
        target = priv_of(k)
        guesses = {priv_of(c) for c in cands}
        if target in guesses:
            ok += 1
        else:
            print("FAIL k=", k, "cands=", cands)
    print(f"local sim: {ok}/{trials} recovered")

def live():
    x0 = pick_x0()
    s = socket.create_connection(("socket.cryptohack.org", 13417), timeout=25)
    fp = s.makefile("rw", newline="\n")
    banner = [fp.readline() for _ in range(3)]
    print("banner:", banner)
    fp.write(json.dumps({"option": "get_pubkey", "x0": str(x0)}) + "\n"); fp.flush()
    resp = json.loads(fp.readline())
    print("pubkey resp:", str(resp)[:120])
    r = int(resp["pubkey"])
    cands = attack(x0, r)
    guesses = sorted({priv_of(c) for c in cands})
    print("guesses:", guesses)
    for g in guesses:
        fp.write(json.dumps({"option": "get_flag", "privkey": int(g)}) + "\n"); fp.flush()
        out = json.loads(fp.readline())
        print("get_flag:", out)
        if "flag" in out:
            print("FLAG:", out["flag"])
            with open("flag_exceptional_twisted_mind.txt", "w") as fh:
                fh.write(out["flag"] + "\n")
            break
    s.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sim":
        solve_local()
    else:
        live()

# d-phi-enc (HackTM CTF 2023): recover phi via poly GCD, then decrypt.
import re
from Crypto.Util.number import long_to_bytes

src = open("output.txt").read()
N, ENC_D, ENC_PHI, ENC_FLAG = map(int, re.findall(r"= (\d+)", src))

def monic(a, n):
    lb = a[0]
    g = pow(lb, -1, n) if _inv_ok(lb, n) else None
    if g is None:
        raise ValueError(f"non-invertible pivot {lb}")
    return [c * g % n for c in a]

def _inv_ok(x, n):
    from math import gcd
    return gcd(x, n) == 1

def poly_mod(a, b, n):
    """a mod b (high-to-low lists), b monic over Z/n."""
    a = a[:]
    db = len(b) - 1
    while len(a) - 1 >= db and any(a):
        f = a[0]
        if f:
            a = [(a[i] - f * (b[i] if i < len(b) else 0)) % n for i in range(len(a))]
        a = a[1:]
    return a or [0]

def gcd_poly(a, b, n):
    a, b = monic(a, n), monic(b, n)
    while any(b):
        r = poly_mod(a, b, n)
        a, b = b, monic(r, n) if any(r) else [0]
    return a

# phi is the unique common root mod n of:
#   g(x)  = x^3 - enc_phi
#   f_k(x)= (k x + 1)^3 - 27*enc_d   for the true k = (3d-1)/phi in {1,2}
# Reduce f_k using x^3 = enc_phi -> quadratic q2; then gcd with g.
found = None
for k in (1, 2):
    c = (1 + pow(k, 3) * ENC_PHI - 27 * ENC_D) % N
    q2 = [(3 * k * k) % N, (3 * k) % N, c]
    g3 = [1, 0, 0, (-ENC_PHI) % N]
    try:
        # first reduce g3 mod q2, then gcd
        r1 = poly_mod(g3, monic(q2, N), N)
        d1 = gcd_poly(q2, r1, N) if any(r1) else monic(q2, N)
        if len(d1) == 2:
            phi = (-d1[1]) % N
            # verify: phi^3 == enc_phi mod N and (k*phi+1) % 3 == 0
            if pow(phi, 3, N) == ENC_PHI % N:
                found = (k, phi)
                break
    except ValueError as ex:
        print("glitch:", ex)

assert found, "no linear gcd factor found"
k, phi = found
print("k =", k, "phi =", phi)

d = (k * phi + 1) // 3
assert d * 3 % phi == 1 % phi and 3 * d - 1 == k * phi
S = N - phi + 1  # p+q
disc = S * S - 4 * N
import gmpy2
root = gmpy2.isqrt(disc)
assert root * root == disc
p = (S + int(root)) // 2
q = N // p
assert p * q == N and (p - 1) * (q - 1) == phi
print("factored OK:", p * q == N, "phi match:", (p-1)*(q-1) == phi)

m = pow(ENC_FLAG, d, N)
flag = long_to_bytes(m)
print("FLAG:", flag.decode())
open("flag_d-phi-enc-hacktm_ctf2023.txt", "w").write(flag.decode())

#!/usr/bin/env python3
# bespoke (105) v2: Franklin-Reiter in (Z/N)[x]. f_i = (a_i x + b_i)^11 - c_i mod N.
# Monic-ize (divide by a_i^11), then Euclid with monic long division over Z/N
# (valid over any ring when divisor is monic). gcd -> x - m.
import json, socket

def polymod(f, g, N):
    # f, g lists high->low, g monic; return f mod g over Z/N
    f = f[:]; dg = len(g) - 1
    while len(f) >= len(g) and any(f):
        if len(f) < len(g): break
        c = f[0]
        if c:
            for i in range(len(g)):
                f[i] = (f[i] - c * g[i]) % N
        f = f[1:]
    return f

def monic(f, N):
    inv = pow(f[0], -1, N)
    return [c * inv % N for c in f]

s = socket.create_connection(("socket.cryptohack.org", 13386), timeout=30)
f = s.makefile("rwb")
f.readline()
qs = []
for i in range(3):
    f.write((json.dumps({"option": "get_flag"}) + "\n").encode()); f.flush()
    r = json.loads(f.readline().decode())
    a, b = r["padding"]; c = int(r["encrypted_flag"]); N = int(r["modulus"])
    # (a x + b)^11 - c expanded mod N, monic: x^11 + sum C(11,k) b^k a^(11-k)... monic-ize
    from math import comb
    coeffs = [comb(11, k) * pow(b, k, N) * pow(a, 11 - k, N) % N for k in range(12)]
    coeffs[-1] = (coeffs[-1] - c) % N
    qs.append(monic(coeffs, N))

g1, g2 = qs[0], qs[1]
import sys
while len(g2) > 2:
    r = polymod(g1, g2, N)
    # trim leading zeros
    while r and r[0] == 0: r = r[1:]
    if not r:
        print("gcd exhausted?!"); sys.exit(1)
    g1 = g2
    try:
        g2 = monic(r, N)
    except ValueError:
        print("non-invertible lc -> factored N? lc:", r[0], "gcd:", __import__('math').gcd(r[0], N))
        sys.exit(1)
    print("deg", len(g2) - 1, flush=True)
# g2 = x + k  => m = -k mod N
m = (-g2[1]) % N
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print("FLAG:", flag.decode(errors="replace"))
f.close(); s.close()

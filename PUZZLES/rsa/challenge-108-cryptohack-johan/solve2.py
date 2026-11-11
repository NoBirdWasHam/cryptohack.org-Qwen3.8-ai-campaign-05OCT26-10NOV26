#!/usr/bin/env python
# johan: 7 encryptions e=3, distinct N, template emails differing in a small field.
# Franklin-Reiter: for m2 = m1 + d, gcd((x+d)^3-c2, x^3-c1) mod n has root m1.
import re
from math import gcd
from Crypto.Util.number import long_to_bytes

txt = open('output.txt').read()
blocks = re.findall(r"n = (\d+)\ne = (\d+)\nc = (\d+)", txt)
ns = [int(b[0]) for b in blocks]; cs = [int(b[2]) for b in blocks]
print("n bits:", [n.bit_length() for n in ns])

def poly_mod(f, g, n):
    # f mod g over Z/nZ, f,g lists low->high
    f = f[:]
    dg = len(g) - 1
    inv = None
    # try to invert leading coeff of g
    lc = g[dg] % n
    try:
        inv = pow(lc, -1, n)
    except ValueError:
        return None  # non-invertible: skip
    while len(f) >= len(g) and f:
        if not f: break
        shift = len(f) - len(g)
        coef = (f[-1] * inv) % n
        for i in range(len(g)):
            f[shift + i] = (f[shift + i] - coef * g[i]) % n
        while f and f[-1] == 0:
            f.pop()
    return f

def poly_gcd(f, g, n):
    while g:
        r = poly_mod(f, g, n)
        if r is None: return None
        f, g = g, r
    return f

def try_pair(i, j, maxd):
    n = ns[i]; c1 = cs[i]; c2 = cs[j]
    # f = x^3 - c1 ; g = (x+d)^3 - c2
    f = [-c1 % n, 0, 0, 1]
    for d in list(range(1, maxd + 1)) + list(range(-maxd, 0)):
        g = [pow(d, 3, n) - c2 % n, 3 * d * d % n, 3 * d % n, 1]
        r = poly_gcd(g[:], f[:], n)
        if r is not None and len(r) == 2:
            m1 = (-r[0] * pow(r[1], -1, n)) % n
            if pow(m1, 3, n) == c1:
                return m1, d
    return None, None

for i in range(7):
    for j in range(i + 1, 7):
        m1, d = try_pair(i, j, 20000)
        if m1:
            print(f"PAIR {i},{j} d={d}")
            print("m_i:", long_to_bytes(m1))
            print("m_j:", long_to_bytes((m1 + d) % ns[i]))
            break
    else:
        continue
    break
print("scan done")

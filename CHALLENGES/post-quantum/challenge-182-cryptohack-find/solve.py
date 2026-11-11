#!/usr/bin/env python
# Find the Lattice (100 pt, post-quantum) — solver
#
# Protocol: h = g*f^{-1} mod q, e = (r*h + m) mod q,  f,g < sqrt(q/2), m = flag.
#
# Attack: the relation  h*f = g + s'*q  implies  (g, f) = f*(h,1) - s'*(q,0),
# so the private key vector (g, f) is a SHORT VECTOR of the 2D lattice
#     L = < (h, 1), (q, 0) >  (det = q ~ 2^512, random min ~ 2^255.8,
#     while ||(g,f)|| ~ 2^255 -> (g,f) is the SVP).
# 2D Gaussian reduction is optimal: it returns (g, f) exactly.
# Then decrypt with the protocol's own decrypt():
#     a = (f*e) % q ;  m = a * f^{-1} mod g
#
# Pure Python — no fpylll/sage needed for 2D.

import math

q = 7638232120454925879231554234011842347641017888219021175304217358715878636183252433454896490677496516149889316745664606749499241420160898019203925115292257
h = 2163268902194560093843693572170199707501787797497998463462129592239973581462651622978282637513865274199374452805292639586264791317439029535926401109074800
e = 5605696495253720664142881956908624307570671858477482119657436163663663844731169035682344974286379049123733356009125671924280312532755241162267269123486523


def gauss2(v1, v2, max_iter=100000):
    """2D Gaussian reduction (dot-product nearest-plane). Returns (short, other)."""
    v1 = [v1[0], v1[1]]
    v2 = [v2[0], v2[1]]
    for _ in range(max_iter):
        n1 = v1[0] * v1[0] + v1[1] * v1[1]
        n2 = v2[0] * v2[0] + v2[1] * v2[1]
        if n2 < n1:
            v1, v2, n1, n2 = v2, v1, n2, n1
        dot = v2[0] * v1[0] + v2[1] * v1[1]
        m = dot / n1
        rm = math.floor(m + 0.5)
        v2 = [v2[0] - rm * v1[0], v2[1] - rm * v1[1]]
        if -0.5 < m < 0.5:
            break
    n1 = v1[0] * v1[0] + v1[1] * v1[1]
    n2 = v2[0] * v2[0] + v2[1] * v2[1]
    if n2 < n1:
        v1, v2 = v2, v1
    return v1, v2


# --- 1) SVP of L = <(h,1), (q,0)> -> (g, f) ---
short, other = gauss2((h, 1), (q, 0))
g, f = short[0], short[1]
if g < 0 or f < 0:  # sign fix (SVP unique up to sign)
    g, f = -g, -f
print(f"shortest vector of L: ({g}, {f})  norm~{int(math.sqrt(g*g + f*f)).bit_length()} bits")

# --- 2) verify all structural constraints ---
assert (h * f) % q == g, "key relation h*f == g (mod q) failed"
assert 2 <= f < math.isqrt(q // 2), "f out of range"
assert math.isqrt(q // 4) <= g < math.isqrt(q // 2), "g out of range"
assert math.gcd(f, g) == 1, "gcd(f,g) != 1"
print("all structural checks passed")

# --- 3) decrypt with the protocol's own decrypt() ---
a = (f * e) % q
m = a * pow(f, -1, g) % g
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print("flag:", flag.decode())

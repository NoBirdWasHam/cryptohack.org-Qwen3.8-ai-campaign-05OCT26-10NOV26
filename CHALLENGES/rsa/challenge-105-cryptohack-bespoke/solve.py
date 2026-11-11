#!/usr/bin/env python3
# bespoke (105): server returns c=(a*m+b)^11 mod N with fresh random (a,b) per query,
# SAME m (the flag) and same N within a session. Franklin-Reiter related message:
# 11 queries -> gcd of (a_i x + b_i)^11 - c_i over Q -> linear -> root = m.
import json, socket
from fractions import Fraction
from sympy import Poly, ZZ, gcd as sgcd, ZZ as ZZm
from sympy.abc import x

s = socket.create_connection(("socket.cryptohack.org", 13386), timeout=30)
f = s.makefile("rwb")
hello = f.readline()
polys = []
N = None
for i in range(11):
    f.write((json.dumps({"option": "get_flag"}) + "\n").encode()); f.flush()
    r = json.loads(f.readline().decode())
    a, b = r["padding"]; c = int(r["encrypted_flag"]); N = int(r["modulus"])
    polys.append(Poly((a*x + b)**11 - c, x, domain=ZZ))
g = polys[0]
for p_ in polys[1:]:
    g = sgcd(g, p_)
    print("after", "deg", g.degree(), flush=True)
    if g.degree() == 1:
        break
co = g.all_coeffs()   # [A, B]
m = (-Fraction(int(co[1]), 1) / Fraction(int(co[0]), 1))
assert m.denominator == 1
M = int(m.numerator)
flag = M.to_bytes((M.bit_length()+7)//8, 'big')
print("FLAG:", flag.decode(errors="replace"))
f.close(); s.close()

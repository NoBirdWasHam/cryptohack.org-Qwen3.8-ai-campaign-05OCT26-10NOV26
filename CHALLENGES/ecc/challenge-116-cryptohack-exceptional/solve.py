#!/usr/bin/env python3
"""exceptional: anomalous curve (#E == p, 512-bit) -> Smart attack -> AES-CBC flag."""
import re, ast
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.number import inverse
from smart_test import smart_dlog

p = 0xa15c4fb663a578d8b2496d3151a946119ee42695e18e13e90600192b1d0abdbb6f787f90c8d102ff88e284dd4526f5f6b6c980bf88f1d0490714b67e8a2a2b77
a = 0x5e009506fcc7eff573bc960d88638fe25e76a9b6c7caeea072a27dcd1fa46abb15b7b6210cf90caba982893ee2779669bac06e267013486b22ff3e24abae2d42
b = 0x2ce7d1ca4493b0977f088f6d30d9241f8048fdea112cc385b793bce953998caae680864a7d3aa437ea3ffd1441ca3fb352b0b710bb3f053e980e503be9a7fece
b_x = 0x7f0489e4efe6905f039476db54f9b6eac654c780342169155344abc5ac90167adc6b8dabacec643cbe420abffe9760cbc3e8a2b508d24779461c19b20e242a38
b_y = 0xdd04134e747354e5b9618d8cb3f60e03a74a709d4956641b234daa8a65d43df34e18d00a59c070801178d198e8905ef670118c15b0906d3a00a662d3a2736bf

txt = open("output.txt").read()
Gm = re.search(r"Generator: \((\d+) : (\d+) : 1\)", txt)
Am = re.search(r"Public Key: \((\d+) : (\d+) : 1\)", txt)
Dm = re.search(r"\{'iv': '([0-9a-f]+)', 'encrypted_flag': '([0-9a-f]+)'\}", txt)
G = (int(Gm.group(1)), int(Gm.group(2)))
A = (int(Am.group(1)), int(Am.group(2)))
iv = bytes.fromhex(Dm.group(1)); ct = bytes.fromhex(Dm.group(2))
print("points parsed; on-curve checks:",
      (G[1]**2 - G[0]**3 - a*G[0] - b) % p == 0,
      (A[1]**2 - A[0]**3 - a*A[0] - b) % p == 0,
      (b_y**2 - b_x**3 - a*b_x - b) % p == 0)

nA = smart_dlog(p, a, b, G, A)
print("nA =", nA)

# affine scalar mult nA * B over F_p
def addf(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0: return None
    m = (3*x1*x1 + a) * inverse(2*y1, p) % p if P1 == P2 else (y2-y1) * inverse(x2-x1, p) % p
    x3 = (m*m - x1 - x2) % p
    return (x3, (m*(x1-x3) - y1) % p)

def mulf(n, P):
    R = None
    while n:
        if n & 1: R = addf(R, P)
        P = addf(P, P); n >>= 1
    return R

# verify: nA * G == A
print("verify nA*G == A:", mulf(nA, G) == A)
S = mulf(nA, (b_x, b_y))
secret = S[0]
key = sha1(str(secret).encode("ascii")).digest()[:16]
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
s = pt.decode(errors="ignore")
i = s.find("crypto{")
print("FLAG:", s[i:s.find("}", i)+1] if i >= 0 else repr(pt))

#!/usr/bin/env python
# norandom: k_i = sha1(d||h_i) ~160 bits << q(256). k_i = a_i*d + b_i mod q
# => k vector is small in coset b + L, L = <a, qZ^3>. Babai CVP -> k -> d -> Q = d^{-1}T.
from hashlib import sha1
from fractions import Fraction
import re, ast

def bytes_to_long(b): return int.from_bytes(b, "big")

# P-256
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
A = -3
B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b

def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        l = (3*x1*x1 + A) * pow(2*y1, -1, p) % p
    else:
        l = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (l*l - x1 - x2) % p
    y3 = (l*(x1 - x3) - y1) % p
    return (x3, y3)
def pmul(k, P):
    R = None
    while k:
        if k & 1: R = padd(R, P)
        P = padd(P, P); k >>= 1
    return R

txt = open("output.txt").read()
hidden = ast.literal_eval(re.search(r"Hidden flag: (\(.*?\))", txt).group(1))
pub = ast.literal_eval(re.search(r"Public key: (\(.*?\))", txt).group(1))
msgs = [b'I have hidden the secret flag as a point of an elliptic curve using my private key.',
        b'The discrete log...']  # placeholder
sigs = re.findall(r"\{'msg': '([^']*)', 'r': '([^']*)', 's': '([^']*)'\}", txt)
print("sigs:", len(sigs))
r = [int(x[1], 16) for x in sigs]
s = [int(x[2], 16) for x in sigs]
h = [bytes_to_long(sha1(x[0].encode()).digest()) for x in sigs]

a = [r[i] * pow(s[i], -1, n) % n for i in range(3)]
b = [h[i] * pow(s[i], -1, n) % n for i in range(3)]

# integer LLL (dimension 4, entries 256-bit) — simple implementation
def lll(B, delta=Fraction(99, 100)):
    B = [list(map(int, row)) for row in B]
    m = len(B)
    def gso(B):
        Bs = []
        mu = [[Fraction(0)]*m for _ in range(m)]
        for i in range(m):
            v = [Fraction(x) for x in B[i]]
            for j in range(i):
                num = sum(Fraction(B[i][k])*Bs[j][k] for k in range(len(v)))
                den = sum(Bs[j][k]*Bs[j][k] for k in range(len(v)))
                mu[i][j] = num/den if den else Fraction(0)
                v = [v[k] - mu[i][j]*Bs[j][k] for k in range(len(v))]
            Bs.append(v)
        return Bs, mu
    k = 1
    while k < m:
        Bs, mu = gso(B)
        for j in range(k-1, -1, -1):
            q_ = round(mu[k][j])
            if q_ != 0:
                B[k] = [B[k][t] - q_*B[j][t] for t in range(len(B[k]))]
        Bs, mu = gso(B)
        n1 = sum(x*x for x in Bs[k]); n0 = sum(x*x for x in Bs[k-1])
        if n1 >= (delta - mu[k][k-1]**2) * n0:
            k += 1
        else:
            B[k], B[k-1] = B[k-1], B[k]
            k = max(k-1, 1)
    return B

Bmat = [[a[0], a[1], a[2]], [n,0,0], [0,n,0], [0,0,n]]
R = lll(Bmat)
print("LLL done")

# Babai nearest plane on reduced basis R (rank 3, 4 rows) — drop zero rows
R = [row for row in R if any(row)]
def babai(R, target):
    # Gram-Schmidt of R
    Bs = []
    for i in range(len(R)):
        v = [Fraction(x) for x in R[i]]
        for j in range(i):
            num = sum(Fraction(R[i][k])*Bs[j][k] for k in range(3))
            den = sum(Bs[j][k]*Bs[j][k] for k in range(3))
            mu = num/den if den else Fraction(0)
            v = [v[k] - mu*Bs[j][k] for k in range(3)]
        Bs.append(v)
    w = [Fraction(t) for t in target]
    coeffs = [0]*len(R)
    for i in reversed(range(len(R))):
        num = sum(w[k]*Bs[i][k] for k in range(3))
        den = sum(Bs[i][k]*Bs[i][k] for k in range(3))
        c = round(num/den) if den else 0
        coeffs[i] = c
        w = [w[k] - c*Fraction(R[i][k]) for k in range(3)]
    v = [sum(coeffs[i]*R[i][k] for i in range(len(R))) for k in range(3)]
    return v

target = [-bi for bi in b]
v = babai(R, target)
k = [v[i] + b[i] for i in range(3)]
print("k sizes:", [abs(ki).bit_length() for ki in k])
for ki in k:
    assert abs(ki) < 2**165, "k too big — CVP failed"

d = (s[0]*k[0] - h[0]) * pow(r[0], -1, n) % n
assert pmul(d, (Gx, Gy)) == pub, "d does not match pubkey"
T = hidden
Q = pmul(pow(d, -1, n), T)
flag = (Q[0].to_bytes(32, "big")).lstrip(b"\x00")
print("FLAG:", flag)
open("flag.txt", "wb").write(flag)

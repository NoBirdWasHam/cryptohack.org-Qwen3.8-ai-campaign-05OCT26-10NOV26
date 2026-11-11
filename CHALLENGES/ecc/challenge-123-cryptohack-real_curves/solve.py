#!/usr/bin/env python3
# CryptoHack "real_curves" solver.
# The "elliptic curve" is over R: y^2 = x^3 - x. The real locus identity component
# is the circle R/omega*Z via x=ellip(u), y=-ellip'(u)/2 (omega = 2*int_1^inf dt/(2 sqrt(t^3-t))
#   = pi/agm(1,sqrt(2))).
# P = N*G  =>  N*u_G - k*omega = u_P  for some integer k, with N,k < ~2^128.
# u_P is known to ~155+ digits (mpmath dps=200 rounding of the source's double-and-add),
# u_G and omega to arbitrary precision. This is a CVP: find (N,k) with
# |N*U - k*W - V| tiny, solved with a Kannan-embedding lattice + LLL.
import json
from fractions import Fraction
from mpmath import mp, mpf, sqrt, quad, inf

mp.dps = 320

d = json.load(open('output.txt'))
gx, gy = mpf(d['gx']), mpf(d['gy'])
px, py = mpf(d['px']), mpf(d['py'])

half = quad(lambda s: 1/sqrt((s*s+1)*(s*s+2)), [0, inf])
omega = 2*half  # = pi/agm(1,sqrt(2))

def u_of(pt):
    x, y = pt
    u = quad(lambda s: 2*s/(2*sqrt((x+s*s)**3-(x+s*s))), [0, inf])
    return u if y > 0 else omega - u

uG = u_of((gx, gy))
uP = u_of((px, py))

Pb = 700
U = int(uG*2**Pb); W = int(omega*2**Pb); V = int(uP*2**Pb)
c = 2**190

def lll(B):
    B = [list(map(Fraction, row)) for row in B]
    n = len(B)
    dot = lambda u, v: sum(a*b for a, b in zip(u, v))
    def gs(B):
        Bs = []; mu = [[Fraction(0)]*n for _ in range(n)]
        for i in range(n):
            v_ = list(B[i])
            for j in range(len(Bs)):
                mu[i][j] = dot(B[i], Bs[j])/dot(Bs[j], Bs[j])
                v_ = [a-b for a, b in zip(v_, [mu[i][j]*t for t in Bs[j]])]
            Bs.append(v_)
        return Bs, mu
    Bs, mu = gs(B)
    k = 1
    while k < n:
        for j in range(k-1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a-q*b for a, b in zip(B[k], B[j])]
                Bs, mu = gs(B)
        if dot(Bs[k], Bs[k]) >= Fraction(3, 4)*dot(Bs[k-1], Bs[k-1]):
            k += 1
        else:
            B[k], B[k-1] = B[k-1], B[k]
            Bs, mu = gs(B)
            k = max(k-1, 1)
    return [[int(x) for x in row] for row in B]

B = [[1, 0, U, 0], [0, 1, -W, 0], [0, 0, V, c]]
cands = []
for row in lll(B):
    if abs(row[3]) == c:
        N = row[0] if row[3] == -c else -row[0]
        if 0 < N < 2**128:
            cands.append(N)
print("candidates:", cands)

# verify against the real curve relation, then decrypt
from Crypto.Cipher import AES
iv = bytes.fromhex(d['iv'])
ct = bytes.fromhex(d['ciphertext'])
for N in cands:
    key = N.to_bytes(16, 'big')
    pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    print(N, pt)

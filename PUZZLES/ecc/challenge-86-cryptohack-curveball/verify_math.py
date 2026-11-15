#!/usr/bin/env python3
"""Curveball (CryptoHack ECC course) — local math verification before the socket attack.

Vuln: server sets  g = Point(x, y, curve=P256)  from MY 'generator', no validation,
      then Q = g * d and matches Q against its trusted-cert cache.
Attack: send generator g = Q_bing (Bing's trusted public key) and d = n + 1 (P256 order + 1).
      Then Q = (n+1) * Q_bing = Q_bing + n*Q_bing = Q_bing + O = Q_bing  -> matches Bing -> flag.
      (n * Q_bing == O because Q_bing = d_bing * G and n * G == O.)
No DLP, no curve change — purely the "you trust my generator" bug.
"""
# P256 (secp256r1 / NIST P-256) parameters
P  = 2**256 - 2**224 + 2**192 + 2**96 - 1
A  = P - 3  # -3
B  = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
N  = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551  # correct secp256r1 order
GX = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
GY = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
O = None  # point at infinity

Qbx = 0x3B827FF5E8EA151E6E51F8D0ABF08D90F571914A595891F9998A5BD49DFA3531
Qby = 0xAB61705C502CA0F7AA127DEC096B2BBDC9BD3B4281808B3740C320810888592A

def inv(x, m): return pow(x, -1, m)
def add(Pt, Qt):
    if Pt is None: return Qt
    if Qt is None: return Pt
    x1,y1=Pt; x2,y2=Qt
    if x1==x2:
        if (y1+y2)%P==0: return None
        lam=(3*x1*x1+A)*inv(2*y1,P)%P
    else:
        lam=(y2-y1)*inv(x2-x1,P)%P
    x3=(lam*lam-x1-x2)%P
    return (x3,(lam*(x1-x3)-y1)%P)
def mul(k, Pt):
    R=None
    while k>0:
        if k&1: R=add(R,Pt)
        Pt=add(Pt,Pt); k>>=1
    return R
def oncurve(Pt):
    x,y=Pt
    return (y*y - (x**3+A*x+B))%P==0

G=(GX,GY); Qb=(Qbx,Qby)
print("G on curve:      ", oncurve(G))
print("Q_bing on curve: ", oncurve(Qb))
print("n*G == O:        ", mul(N,G) is None)
print("n*Q_bing == O:   ", mul(N,Qb) is None)
print("(n+1)*Q_bing == Q_bing: ", mul(N+1,Qb) == Qb)
print("\n=> if all True, attack Q = (n+1)*Q_bing = Q_bing lands in the Bing cache.")

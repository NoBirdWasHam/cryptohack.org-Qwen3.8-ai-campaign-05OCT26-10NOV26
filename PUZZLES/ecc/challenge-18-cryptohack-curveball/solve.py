#!/usr/bin/env python3
"""Curveball (CryptoHack ECC course) — socket attack.

Vuln: server sets  g = Point(x, y, curve=P256)  from MY 'generator', no validation,
      then Q = g * d and matches Q against its trusted-cert cache.
Attack: send generator g = Q_bing (Bing's trusted public key) and d = n + 1 (P256 order + 1).
      Q = (n+1) * Q_bing = Q_bing + n*Q_bing = Q_bing + O = Q_bing  -> Bing cache -> flag.
      (n * Q_bing == O since Q_bing = d_bing * G and n * G == O.)  No DLP, no curve change.
Protocol: one JSON object over the socket. Keys: private_key, host, curve, generator [x,y].
"""
import socket, json

# secp256r1 (P-256)
P  = 2**256 - 2**224 + 2**192 + 2**96 - 1
A  = P - 3
B  = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
N  = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551  # correct order
Qbx = 0x3B827FF5E8EA151E6E51F8D0ABF08D90F571914A595891F9998A5BD49DFA3531
Qby = 0xAB61705C502CA0F7AA127DEC096B2BBDC9BD3B4281808B3740C320810888592A

def inv(x,m): return pow(x,-1,m)
def add(Pt,Qt):
    if Pt is None: return Qt
    if Qt is None: return Pt
    x1,y1=Pt;x2,y2=Qt
    if x1==x2:
        if (y1+y2)%P==0: return None
        lam=(3*x1*x1+A)*inv(2*y1,P)%P
    else: lam=(y2-y1)*inv(x2-x1,P)%P
    x3=(lam*lam-x1-x2)%P
    return (x3,(lam*(x1-x3)-y1)%P)
def mul(k,Pt):
    R=None
    while k>0:
        if k&1: R=add(R,Pt)
        Pt=add(Pt,Pt); k>>=1
    return R

# pre-flight: confirm the attack identity locally (independent of the server)
assert mul(N, (Qbx,Qby)) is None, "n*Q_bing != O — order/point wrong"
assert mul(N+1, (Qbx,Qby)) == (Qbx,Qby), "(n+1)*Q_bing != Q_bing"
print("local pre-flight: n*Q_bing==O and (n+1)*Q_bing==Q_bing  OK")

s = socket.create_connection(("socket.cryptohack.org", 13382), timeout=60)
f = s.makefile("rb")
banner = f.readline().decode().strip()
print("banner:", banner)

payload = {
    "private_key": N + 1,
    "host": "www.bing.com",
    "curve": "secp256r1",
    "generator": [Qbx, Qby],   # g = Q_bing  =>  Q = (n+1)*Q_bing = Q_bing
}
s.sendall(json.dumps(payload).encode())
# read the response
import select
data = b""
while True:
    ready = select.select([f], [], [], 10)[0]
    if not ready:
        break
    chunk = f.read(4096)
    if not chunk:
        break
    data += chunk
print("RESPONSE:", data.decode(errors="replace"))
s.close()

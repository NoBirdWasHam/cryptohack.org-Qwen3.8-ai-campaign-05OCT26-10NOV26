#!/usr/bin/env python3
# challenge-218 abelian_sidh: phi_hat o phi = [deg] => shared = [2^216 * 3^137] G. Pure EC scalar mult.
import re
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

q = 66755491218549620204451278063200785887258235588279474221852899550437797658031
ea, eb = 216, 137
p = (2**ea) * (3**eb) * q - 1

# F_{p^2}: z = (re, im) meaning re + im*i, i^2 = -1
def zmul(a, b):
    return ((a[0]*b[0] - a[1]*b[1]) % p, (a[0]*b[1] + a[1]*b[0]) % p)
def zinv(a):
    n = pow((a[0]*a[0] + a[1]*a[1]) % p, p-2, p)
    return (a[0]*n % p, (-a[1]) * n % p)
def zsub(a, b): return ((a[0]-b[0]) % p, (a[1]-b[1]) % p)
def zadd(a, b): return ((a[0]+b[0]) % p, (a[1]+b[1]) % p)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and zadd(y1, y2) == (0, 0): return None
    if P == Q:
        m = zadd(zmul((3, 0), zmul(x1, x1)), (1, 0)); m = zmul(m, zinv(zmul((2, 0), y1)))
    else:
        m = zmul(zsub(y2, y1), zinv(zsub(x2, x1)))
    x3 = zsub(zsub(zmul(m, m), x1), x2)
    y3 = zsub(zmul(m, zsub(x1, x3)), y1)
    return (x3, y3)

def mul(P, n):
    R = None; Q = P
    while n:
        if n & 1: R = add(R, Q)
        Q = add(Q, Q); n >>= 1
    return R

txt = open("output.txt").read()
def parse_pt(s):
    m = re.search(r"\((\d+)\*i \+ (\d+), (\d+)\*i \+ (\d+)\)", s)
    return ((int(m.group(2)), int(m.group(1))), (int(m.group(4)), int(m.group(3))))
G = parse_pt(txt.split("G = ")[1].split("\n")[0])
GA = parse_pt(txt.split("G_A = ")[1].split("\n")[0])
GB = parse_pt(txt.split("G_B = ")[1].split("\n")[0])
iv = bytes.fromhex(re.search(r"iv = ([0-9a-f]+)", txt).group(1))
ct = bytes.fromhex(re.search(r"ct = ([0-9a-f]+)", txt).group(1))

# sanity: on-curve check y^2 = x^3 + x
def oncurve(P):
    x, y = P
    return zmul(y, y) == zadd(zmul(zmul(x, x), x), x)
print("G on curve:", oncurve(G), "GB on curve:", oncurve(GB))
# sanity: G_A == [2^216]G and G_B == [3^137]G (dual collapse hypothesis)
print("GA == [2^ea]G :", mul(G, 2**ea) == GA)
print("GB == [3^eb]G :", mul(G, 3**eb) == GB)

ss = mul(G, 2**ea * 3**eb)
x, y = ss
def zstr(z):
    r, i = z
    if i == 0: return str(r)
    if r == 0: return f"{i}*i"
    return f"{i}*i + {r}"
xs, ys = zstr(x), zstr(y)
variants = [f"( {xs} : {ys} : 1 )", f"({xs} : {ys} : 1)", f"( {xs} : {ys} : 1", f"({xs}, {ys})"]
for s in variants:
    key = SHA256.new(data=s.encode()).digest()
    try:
        pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
    except Exception:
        print("no pad:", s[:40]); continue
    print("dec:", pt[:70])
    if b"crypto" in pt:
        open("flag.txt", "wb").write(pt)
        print("FLAG:", pt.decode())
        break

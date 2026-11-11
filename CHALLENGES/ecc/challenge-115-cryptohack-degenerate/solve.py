#!/usr/bin/env python3
# degenerate: Edwards law degenerates on {(0,y)} -> (0,y1)+(0,y2)=(0,y1y2) = F_p^* with base 11.
# p-1 smooth -> Pohlig-Hellman DLP -> n_a -> secret = y_b^{n_a} -> AES-CBC.
import gmpy2
from hashlib import sha1
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes

p = 110791754886372871786646216601736686131457908663834453133932404548926481065303
FACTORS = [2, 33682721, 33964681, 42126503, 46340641, 49189373, 49309751, 50173309, 56252591, 58172209, 62285989]
y_a = 109790246752332785586117900442206937983841168568097606235725839233151034058387
y_b = 45290526009220141417047094490842138744068991614521518736097631206718264930032
iv = bytes.fromhex("31068e75b880bece9686243fa4dc67d0")
ct = bytes.fromhex("e2ef82f2cde7d44e9f9810b34acc885891dad8118c1d9a07801639be0629b186dc8a192529703b2c947c20c4fe5ff2c8")
g = 11

def bsgs_base(gq, hq, q):
    m = gmpy2.isqrt(q) + 1
    table = {}
    e = 1
    for j in range(m):
        table.setdefault(int(e), j)
        e = e * gq % p
        e = int(e)
    gamma = hq
    f = pow(int(gq), int(m), p)
    for i in range(m):
        if gamma in table:
            return (table[gamma] - i * m) % q
        gamma = int(gamma) * f % p
    return None

# CRT accumulate
res, mod = 0, 1
for q in FACTORS:
    gq = pow(g, (p - 1) // q, p)
    hq = pow(y_a, (p - 1) // q, p)
    xq = bsgs_base(gq, hq, q)
    assert xq is not None, q
    assert pow(g, xq, p) == pow(y_a, xq, p) or True
    # verify projection
    assert pow(pow(g, xq, p), (p - 1) // q, p) == hq, f"proj fail q={q}"
    # CRT: res = xq mod q, res = res mod mod
    t = (xq - res) * pow(mod, -1, q) % q
    res += mod * t
    mod *= q
print("n_a =", res, "modulus bits", mod.bit_length())
assert pow(g, res, p) == y_a, "DLP verify failed"
secret = pow(y_b, res, p)
key = sha1(str(secret).encode("ascii")).digest()[:16]
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
s = pt.decode(errors="ignore")
i = s.find("crypto{")
print("FLAG:", s[i:s.find("}", i) + 1] if i >= 0 else repr(pt))

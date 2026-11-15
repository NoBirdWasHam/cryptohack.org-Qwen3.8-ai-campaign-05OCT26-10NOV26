import sys, os, json, secrets
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "authentification-2"))
from gcm.gcm import GCM
from gcm.utils import bytes_to_bits

P128 = (1 << 128) - 1

def gmul(a, b):  # GF(2^128)/(x^128+x^7+x^2+x+1); bit k of int = coeff of alpha^(127-k)
    # work in coefficient space: c[j] = coeff alpha^j = bit (127-j)
    res = 0
    aa = a
    # carryless in int-space is tricky due to reversed bits; do bit-space schoolbook on ints
    # interpret: int bit k <-> alpha^(127-k). Multiply via byte->poly: poly deg d coeff
    # alpha^j -> position k=127-j. a<<i in alpha-space (mult by alpha^i) = int >> i... but
    # shifting right drops bits. Instead convert to normal-order ints (bit j = alpha^j):
    def rev(x):
        y = 0
        for i in range(128):
            if (x >> i) & 1:
                y |= 1 << (127 - i)
        return y
    A = rev(a); B = b if False else rev(b)
    r = 0
    for i in range(128):
        if (B >> i) & 1:
            r ^= A << i
    # reduce: alpha^128 = alpha^7+alpha^2+alpha+1
    for d in range(254, 127, -1):
        if (r >> d) & 1:
            r ^= (1 << (d - 128 + 7)) | (1 << (d - 128 + 2)) | (1 << (d - 128 + 1)) | (1 << (d - 128))
    return rev(r)

def to_int(bs): return int.from_bytes(bs, "big")
def to_bytes(v): return v.to_bytes(16, "big")

if __name__ == "__main__":
    d = GCM(b"\x00"*16, b"\x00"*12)
    import random
    ok = 0
    for _ in range(200):
        X = secrets.token_bytes(16); Y = secrets.token_bytes(16)
        mine = to_bytes(gmul(to_int(X), to_int(Y)))
        theirs = d.mul(X, Y)
        ok += (mine == theirs)
    print(f"mul matches theirs: {ok}/200")
    # check model: S = ghash(buf,H) == C1 H^4 + C2 H^3 + C3 H^2 + L H ?
    from math import ceil
    from Crypto.Cipher import AES
    for t in range(5):
        key = secrets.token_bytes(16)
        g = GCM(key, b"\x00"*12)
        u = "u"
        P = json.dumps({"username": u, "role": "guest"}).encode()
        C = g.gctr(g.iv + b"\x00\x00\x00\x01", P)
        u_pad = 16*ceil(len(C)/16) - len(C)
        buf = C + b"\x00"*u_pad + (0).to_bytes(8,"big") + (len(C)*8).to_bytes(8,"big")
        S = g.ghash(buf, g.H)
        blocks = [to_int(buf[i:i+16]) for i in range(0, len(buf), 16)]
        h = to_int(g.H)
        pred = 0
        for bcoef in blocks:
            pred = gmul(pred, h) ^ bcoef
        pred = gmul(pred, h)
        print("quartic horner == ghash:", to_bytes(pred) == S)
        # also as polynomial value: C1 h^4+..
        hh1 = gmul(gmul(gmul(gmul(blocks[0], h), h), h), h)
        hh2 = gmul(gmul(gmul(blocks[1], h), h), h)
        hh3 = gmul(gmul(blocks[2], h), h)
        hh4 = gmul(blocks[3], h)
        val = hh1 ^ hh2 ^ hh3 ^ hh4
        print("poly value == ghash:  ", to_bytes(val) == S)

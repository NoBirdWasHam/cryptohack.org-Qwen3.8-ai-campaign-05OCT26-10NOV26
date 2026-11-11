#!/usr/bin/env python
# lcg2 (198, misc, 150pts) -- full solver.
# LCG: x_{i+1} = a*x_i + b (mod 2^48), a=0x1337deadbeef (odd), b=0xb.
# Output = top 8 bits of state; refresh() reseeds every 16 states.
#
# get_a_challenge emits 48 bytes on block boundaries:
#   plaintext = [v9..v16][w1..w8]   (v = greeting block tail, w = key block head)
#   key       = [w9..w16][k1..k8]   (w tail, k = iv block head)
#   IV        = [k9..k16][i1..i8]   (k tail, i = next block head)
# => key[0:8] = top(w9..w16): recover w1 from top(w1..w8)=plaintext[8:16], FORWARD 8.
# => key[8:16]= top(k1..k8):  recover k9 from top(k9..k16)=IV[0:8],    BACKWARD 8 (a invertible).
import socket, json, itertools
import numpy as np
from Crypto.Cipher import AES
import sympy as sp

HOST = "socket.cryptohack.org"
PORT = 13396
a = 0x1337deadbeef
b = 0xb
N = 48
L = N - 8            # 40 low bits
mod = 2 ** N

def f(x):   return (a * x + b) % mod
def finv(x): return ((x - b) * pow(a, -1, mod)) % mod
def top(x):  return x >> (N - 8)

def recover_first(h, a, b, m=8):
    """h[i]=top byte of consecutive states x_0..x_{m-1}; return x_0.
    B8 lattice: B[i][0]=a^i, B[i][j]=a^{i-j}*2^48 (1<=j<=i), else 0.
    t[i]=h[i]*2^40 - c[i], c[i]=b*sum_{j<i}a^j mod 2^48.
    Find integer u with (B u - t) mod 2^48 in [0,2^40) for all i.
    Fast: exact Babai + numpy int64 (B mod M) + small R window + simulate-verify."""
    M = 2 ** N
    c = [0]*m
    for i in range(m):
        S_i = (pow(a, i) - 1) // (a - 1)
        c[i] = (b * S_i) % M
    B = sp.zeros(m, m)
    for i in range(m):
        B[i, 0] = pow(a, i, M)
        for j in range(1, i+1):
            B[i, j] = (pow(a, i-j, M) * M)
    t = sp.Matrix([h[i]*(2**L) - c[i] for i in range(m)])
    Bred = (B.T.lll()).T
    # exact Babai (fast)
    BRT = Bred.T
    G = (BRT * Bred).inv() * (BRT * t)
    u0 = [int((sp.Rational(G[i]) + sp.Rational(1, 2)).__floor__()) for i in range(m)]
    # numpy int64 eval (B mod M)
    Bm = np.zeros((m, m), dtype=np.int64)
    for i in range(m):
        for j in range(m):
            Bm[i, j] = int(Bred[i, j]) % M
    tvec = np.array([int(t[i]) for i in range(m)], dtype=np.int64)
    best = None
    for R in (1, 2, 3, 6):
        for dc in itertools.product(range(-R, R+1), repeat=m):
            u = np.array([u0[i]+dc[i] for i in range(m)], dtype=np.int64)
            r = (Bm @ u - tvec) % M
            if (r < 2**L).all():
                val = int(np.dot(r - 2**(L-1), r - 2**(L-1)))
                if best is None or val < best[0]:
                    best = (val, int((Bm @ u)[0]) % M)
        if best is not None:
            break
    if best is None:
        return None
    x0 = best[1]
    x = x0
    for i in range(m):
        if top(x) != h[i]:
            return None
        x = f(x)
    return x0

def next_obj(buf, sock):
    idx = buf.find(b'{')
    if idx < 0:
        data = sock.recv(65536)
        if not data:
            return None, buf
        return next_obj(buf + data, sock)
    try:
        obj, end = json.JSONDecoder().raw_decode(buf[idx:].decode('utf-8', 'ignore'))
        return obj, buf[:idx]
    except json.JSONDecodeError:
        data = sock.recv(65536)
        if not data:
            return None, buf
        return next_obj(buf + data, sock)

def main():
    s = socket.create_connection((HOST, PORT), timeout=60)
    buf = b''
    # no greeting on this server; request a fresh challenge immediately
    s.sendall(json.dumps({"option": "get_a_challenge"}).encode() + b"\n")
    obj, buf = next_obj(buf, s)
    print("challenge keys:", list(obj.keys()))
    pt = bytes.fromhex(obj["plaintext"])
    iv = bytes.fromhex(obj["IV"])
    print("plaintext:", pt.hex())
    print("IV:       ", iv.hex())

    # key[0:8] from plaintext[8:16] (=top w1..w8): recover w1, advance 8 to w9, collect 8
    w_top = list(pt[8:16])
    w1 = recover_first(w_top, a, b)
    assert w1 is not None, "w1 recovery failed"
    xs = w1
    for _ in range(8):
        xs = f(xs)                 # reach w9
    key0 = bytearray()
    for _ in range(8):
        key0.append(top(xs))
        xs = f(xs)
    # key[8:16] from IV[0:8] (=top k9..k16), backward 8
    k_top = list(iv[0:8])
    k9 = recover_first(k_top, a, b)
    assert k9 is not None, "k9 recovery failed"
    key8 = bytearray()
    xs = k9
    for _ in range(8):
        xs = finv(xs)
        key8.insert(0, top(xs))
    key = bytes(key0) + bytes(key8)
    print("recovered key:", key.hex())

    ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pt)
    print("ciphertext:   ", ct.hex())
    s.sendall(json.dumps({"option": "validate", "ciphertext": ct.hex()}).encode() + b"\n")
    obj, buf = next_obj(buf, s)
    print("RESULT:", obj.get("msg", obj))

if __name__ == "__main__":
    main()

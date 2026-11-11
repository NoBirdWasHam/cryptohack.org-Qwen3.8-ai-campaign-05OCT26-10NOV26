#!/usr/bin/env python
# checkpoint: invalid-curve attack on ECDH service. Server never validates Q on P-256.
# Use E'': y^2 = x^3 + a*x (b=0) over F_p, #E'' = p+1 (p = P-256 prime, p = 3 mod 4).
# p+1 = 2^96 * 7 * 274177 * (42-digit factors). Oracle: get_test_message under sha256(str(x(sQ))).
# PH-style oracle queries recover s mod l^e for every prime power; CRT -> s; decrypt FLAG.
import socket, json, re, hashlib
from Crypto.Cipher import AES

p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
     0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)
O = None

def padd(P, Q):
    if P is O: return Q
    if Q is O: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return O
        lam = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def pmul(k, P):
    R = O
    while k:
        if k & 1: R = padd(R, P)
        P = padd(P, P); k >>= 1
    return R

def on_E(x, y):
    return (y*y - (x*x*x + a*x)) % p == 0

# ---- socket ----
s = socket.create_connection(("socket.cryptohack.org", 13419), timeout=20)
s.settimeout(15)
buf = b""
def readmsg():
    global buf
    d = s.recv(65536)
    if not d: return None
    buf += d
    try:
        obj = json.loads(buf.decode())
        buf = b""
        return obj
    except Exception:
        return None   # partial / non-final

# read the before_input banner (may arrive in pieces until first JSON)
banner = ""
while True:
    d = s.recv(65536)
    if not d: break
    banner += d.decode(errors="replace")
    if "server->client" in banner and "\n" in banner[banner.find("server->client"):]:
        # wait for the final newline of banner
        tail = banner[banner.rfind("server->client"):]
        if tail.count("\n") >= 1 and "}{" not in banner:
            # banner ends with newline after hex line
            if banner.rstrip().endswith(tuple("0123456789abcdef")) or "\n" in tail[tail.find(":")+1:]:
                if banner.rstrip().endswith(tuple("0123456789abcdef")):
                    break
print("BANNER:", banner[:400])
m = re.search(r"client->server : Point\((\d+), (\d+)\)", banner)
client_pub = (int(m.group(1)), int(m.group(2)))
m = re.search(r"server->client : Point\((\d+), (\d+)\)", banner)
P_server = (int(m.group(1)), int(m.group(2)))
m = re.search(r"server->client : ([0-9a-f]+)", banner)
flag_ct = bytes.fromhex(m.group(1))
print("client_pub ok, P_server ok, flag_ct", len(flag_ct), "bytes")

def send(obj):
    s.sendall((json.dumps(obj) + "\n").encode())

def exchange_and_test(Q, candidates):
    """Send Q for key exchange, fetch test ciphertext, test candidate x-values."""
    send({"option": "start_key_exchange", "Qx": hex(Q[0]), "Qy": hex(Q[1]),
          "ciphersuite": "ECDHE_P256_WITH_AES_128"})
    # drain until we see the success/error msg
    while True:
        m = readmsg()
        if m is not None and "msg" in m: break
    send({"option": "get_test_message"})
    ct = None
    while True:
        m = readmsg()
        if m is None: continue
        if "msg" in m and re.fullmatch(r"[0-9a-f]+", m["msg"] or ""):
            ct = bytes.fromhex(m["msg"]); break
        if "msg" in m:  # error text
            return None
    target = b"SERVER_TEST_MESSAGE"
    for xc in candidates:
        if xc is None: continue
        key = hashlib.sha256(str(xc).encode()).digest()[:16]
        try:
            pt = AES.new(key, AES.MODE_CBC, ct[:16]).decrypt(ct[16:])
        except Exception:
            continue
        if pt.rstrip(bytes(range(17))) == target or pt.startswith(target):
            return xc
    return None

# ---- factorization of p+1 (filled after PARI run) ----
import json as _j
FAC = _j.load(open("p1_factors.json"))  # list of [l, e]

def find_point_of_order(le_pow, l):
    """point on E'' of exact order l^e"""
    N = p + 1
    cof = N // le_pow
    import random
    rng = random.Random(1234)
    for _ in range(10000):
        x = rng.randrange(2, p)
        y2 = (x*x*x + a*x) % p
        y = pow(y2, (p+1)//4, p)
        if (y*y) % p != y2: continue
        R = (x, y)
        Q = pmul(cof, R)
        if Q is O: continue
        if pmul(l, Q) is not O or l == 2 and pmul(2, Q) is not O:
            pass
        # verify exact order l^e
        if pmul(le_pow, Q) is O and pmul(le_pow//l, Q) is not O:
            return Q
    raise RuntimeError("no point")

residues = []
modulus = 1
for l, e in FAC:
    le = l**e
    print(f"== l={l} e={e} ({le.bit_length()} bits)", flush=True)
    Q = find_point_of_order(le, l)
    assert on_E(*Q)
    x = 0
    for k in range(1, e+1):
        Qk = pmul(le // l**k, Q)
        cands = [(x + j * l**(k-1)) for j in range(l)]
        pts = [pmul(c, Qk) for c in cands]
        xc_tested = [None if Pt is O else Pt[0] for Pt in pts]
        hit = exchange_and_test(Qk, xc_tested)
        if hit is None:
            raise RuntimeError(f"oracle miss l={l} k={k}")
        x = cands[xc_tested.index(hit)]
        print(f"   s mod {l}^{k} = {x}", flush=True)
    residues.append((x, le))
    modulus *= le

# CRT
from functools import reduce
def crt(pairs):
    x = 0; m = 1
    for r, mod in pairs:
        t = ((r - x) * pow(m, -1, mod)) % mod
        x += m * t
        m *= mod
    return x % m, m
sval, M = crt(residues)
print("s mod M, M bits:", M.bit_length(), "s =", sval, flush=True)
assert sval < 2**256
# verify: s * G == P_server
assert pmul(sval, G) == P_server, "s wrong!"
print("s VERIFIED against server pubkey")
shared = pmul(sval, client_pub)
key = hashlib.sha256(str(shared[0]).encode()).digest()[:16]
pt = AES.new(key, AES.MODE_CBC, flag_ct[:16]).decrypt(flag_ct[16:])
pt = pt.rstrip(bytes(range(17)))
print("FLAG:", pt)
open("flag.txt", "wb").write(pt)

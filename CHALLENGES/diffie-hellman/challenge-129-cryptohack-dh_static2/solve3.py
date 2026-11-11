#!/usr/bin/env python
# dh_static2 path2: p prime ~272 bits with ord_p(2)=q B-smooth, q>2^257.
# Send {p, g=2, A=2}; B2 = 2^b mod p; PH -> b (exact, b<2^256<q); shared1 = A_alice^b mod P0.
import socket, json, hashlib, random, os
from Crypto.Cipher import AES
from Crypto.Util.number import isPrime

def session(payload):
    s = socket.create_connection(("socket.cryptohack.org", 13378), timeout=15)
    s.settimeout(12)
    buf = b""
    def readline():
        nonlocal buf
        try:
            while b"\n" not in buf:
                d = s.recv(65536)
                if not d: return None
                buf += d
        except Exception:
            if buf.strip():
                out = buf.split(b"\n", 1)[0]
                buf = buf.split(b"\n", 1)[1] if b"\n" in buf else b""
                return out.decode().strip()
            return None
        line, buf = buf.split(b"\n", 1)
        return line.decode().strip()
    got = []
    for _ in range(4):
        l = readline()
        if l is None: break
        got.append(l)
    resp = None
    if payload:
        s.sendall((json.dumps(payload) + "\n").encode())
        resp = readline()
    s.close()
    return got, resp

def parse(lines):
    out = {}
    for l in lines:
        i = l.find("{")
        if i < 0: continue
        try: o = json.loads(l[i:])
        except Exception: continue
        out.update({k: v for k, v in o.items()})
    return out

CACHE = "smooth_prime2.json"
if os.path.exists(CACHE):
    pp = json.load(open(CACHE))
    p, q = int(pp[0]), int(pp[1]); fac = {int(k): v for k, v in pp[2].items()}; kk = int(pp[3])
else:
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    rng = random.Random(7)
    p = q = None; fac = None
    found = False
    kk = None
    for trial in range(200000):
        f = {}; q = 1
        while q.bit_length() < 2052:
            r = rng.choice(primes); f[r] = f.get(r,0)+1; q *= r
        if q.bit_length() > 2062: continue
        for ktry in range(4000):
            k = 2*ktry + 1
            cand = k*q + 1
            if cand.bit_length() < 2052: continue
            if not isPrime(cand, 12): continue
            G = pow(2, k, cand)          # order q with prob ~1-1/q
            if pow(G, q, cand) != 1: continue
            ok = True
            for r in f:
                if pow(G, q//r, cand) == 1: ok = False; break
            if ok:
                p, fac, kk = cand, f, k; found = True; break
        if found: break
    assert p, "search failed"
    json.dump([str(p), str(q), fac, str(kk)], open(CACHE, "w"))
if not os.path.exists(CACHE):
    pass
print("p bits", p.bit_length(), "q bits", q.bit_length(), flush=True)

got, _ = session(None)
ph = parse(got)
P0 = int(ph["p"], 16); A_al = int(ph["A"], 16); iv = ph["iv"]; ct = ph["encrypted"]

got2, resp = session({"p": hex(p), "g": "0x2", "A": "0x2"})
print("resp:", str(resp)[:120], flush=True)
o = json.loads(resp[resp.find("{"):])
B2 = int(o["B"], 16)

# Pohlig-Hellman: C = B2^k = G^b with G=2^k of order q (smooth)
G = pow(2, kk, p)
C = pow(B2, kk, p)
def dlog_small(gv, hv, r):
    cur = 1
    for d in range(r):
        if cur == hv: return d
        cur = cur * gv % p
    raise ValueError

x = 0; modulus = 1
for r, e in sorted(fac.items()):
    re_ = r**e
    xj = 0
    gq = pow(G, q//r, p)
    for jj in range(e):
        c = C * pow(G, -xj, p) % p
        c = pow(c, q // r**(jj+1), p)
        d = dlog_small(gq, c, r)
        xj = (xj + d * r**jj) % (r**(jj+1))
    t = ((xj - x) * pow(modulus, -1, re_)) % re_
    x = x + modulus * t
    modulus *= re_
b = x
assert pow(G, b, p) == C, "dlog verify failed"
print("b =", b, flush=True)

s = pow(A_al, b, P0)
key = hashlib.sha1(str(s).encode()).digest()[:16]
pt = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv)).decrypt(bytes.fromhex(ct))
print("PT:", pt)
if b"crypto" in pt:
    open("flag.txt", "w").write(pt.decode(errors="replace"))

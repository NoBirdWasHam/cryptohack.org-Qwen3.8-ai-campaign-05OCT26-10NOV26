#!/usr/bin/env python
# dh_static2 probe2: find p ~2060 bits, p = k*q+1, q B-smooth ~2^260, ord_p(2^k)=q.
# Send {p, g=2, A=2}; if Bob answers with B -> 2060-bit p accepted; PH then gives b mod q.
import socket, json, random, os, sys
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

SMALL = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113]
def sieve_ok(cand):
    for sp in SMALL:
        if cand % sp == 0: return False
    return True

CACHE = "probe2_prime.json"
if os.path.exists(CACHE):
    pp = json.load(open(CACHE))
    p, q, kk = int(pp[0]), int(pp[1]), int(pp[2])
    fac = {int(k): v for k, v in pp[3].items()}
else:
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    rng = random.Random(11)
    p = q = kk = None; fac = None
    for trial in range(100000):
        f = {}; q = 1
        while q.bit_length() < 260:
            r = rng.choice(primes); f[r] = f.get(r,0)+1; q *= r
        if q.bit_length() > 268: continue
        for ktry in range(400000):
            k = (rng.getrandbits(rng.choice([1795,1796,1797,1798,1799,1800,1801,1802,1803,1804,1805])) | 1)
            cand = k*q + 1
            if cand.bit_length() < 2055 or cand.bit_length() > 2068: continue
            if not sieve_ok(cand): continue
            if not isPrime(cand, 6): continue
            G = pow(2, k, cand)
            if pow(G, q, cand) != 1: continue
            ok = True
            for r in f:
                if pow(G, q//r, cand) == 1: ok = False; break
            if ok:
                p, fac, kk = cand, f, k; break
        if p: break
    assert p, "search failed"
    json.dump([str(p), str(q), str(kk), fac], open(CACHE, "w"))
print("p bits", p.bit_length(), "q bits", q.bit_length(), "k bits", kk.bit_length(), flush=True)

got, _ = session(None)
ph = {}
for l in got:
    i = l.find("{")
    if i >= 0:
        try: ph.update(json.loads(l[i:]))
        except Exception: pass
P0 = int(ph["p"], 16); A_al = int(ph["A"], 16); iv = ph["iv"]; ct = ph["encrypted"]
got2, resp = session({"p": hex(p), "g": "0x2", "A": "0x2"})
print("resp:", str(resp)[:160], flush=True)
if resp and '"B"' in resp:
    o = json.loads(resp[resp.find("{"):])
    json.dump({"P0": str(P0), "A": str(A_al), "iv": iv, "ct": ct, "B2": str(int(o["B"], 16))},
              open("probe2_data.json", "w"))
    print("GOT B2 — 2060-bit p accepted", flush=True)

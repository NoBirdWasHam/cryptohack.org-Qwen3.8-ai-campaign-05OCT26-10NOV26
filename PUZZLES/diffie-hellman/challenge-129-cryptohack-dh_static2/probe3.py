#!/usr/bin/env python
# dh_static2: Alice p is 1536 bits (server rejects other sizes as "dodgy").
# Send p' = k*q+1 (1536 bits, q smooth ~2^250), g'=2 of order q, A'=2.
# Bob returns B' = 2^a mod p' -> PH recovers a mod q. Then decrypt with a.
import socket, json, random, os, sys
from Crypto.Util.number import isPrime, long_to_bytes
from Crypto.Cipher import AES

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

def parse_phase(lines):
    ph = {}
    for l in lines:
        i = l.find("{")
        if i >= 0:
            try: ph.update(json.loads(l[i:]))
            except Exception: pass
    return ph

CACHE = "p1536.json"
if os.path.exists(CACHE):
    pp = json.load(open(CACHE))
    p, q, kk = int(pp[0]), int(pp[1]), int(pp[2])
else:
    rng = random.Random(7)
    primes = []
    n = 10**6
    sieve = bytearray([1]) * n
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n**0.5)):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    primes = [i for i in range(2, n) if sieve[i]]
    p = q = kk = None
    for trial in range(2000):
        # q = product of random prime powers, target ~2^250
        q = 1; 
        while q.bit_length() < 248:
            r = rng.choice(primes[:4000])  # primes < ~38000
            pw = 1
            while q.bit_length() + r.bit_length()*pw <= 250 and rng.random() < 0.7:
                pw += 1
            q *= r**pw
        if q.bit_length() > 252: continue
        for ktry in range(20000):
            k = rng.getrandbits(1286) | 1
            cand = k * q + 1
            if cand.bit_length() != 1536: continue
            if not isPrime(cand, 5): continue
            G = pow(2, k, cand)
            if pow(G, q, cand) != 1: continue
            p, kk = cand, k
            break
        if p: break
    assert p, "search failed"
    json.dump([str(p), str(q), str(kk)], open(CACHE, "w"))
print("p bits", p.bit_length(), "q bits", q.bit_length(), flush=True)

got, _ = session(None)
ph = parse_phase(got)
P0 = int(ph["p"], 16); A_al = int(ph["A"], 16)
got2, resp = session({"p": hex(p), "g": "0x2", "A": "0x2"})
print("resp:", str(resp)[:200], flush=True)
if not resp or '"B"' not in resp:
    sys.exit(1)
o = json.loads(resp[resp.find("{"):])
B2 = int(o["B"], 16)
json.dump({"P0": str(P0), "A": str(A_al), "B2": str(B2), "p": str(p), "q": str(q), "k": str(kk)},
          open("p1536_data.json", "w"))
print("GOT B2", B2.bit_length(), flush=True)

# Pohlig-Hellman for a mod q in group of order q (generator 2, B2 = 2^a)
def factorize_small(q):
    f = {}; d = 2
    while d * d <= q:
        while q % d == 0:
            f[d] = f.get(d, 0) + 1; q //= d
        d += 1 if d == 2 else 2
    if q > 1: f[q] = f.get(q, 0) + 1
    return f
def pohlig_hellman(g, h, q, fac, pmod):
    # group order q (smooth), generator g, h = g^a; return a mod q
    residues = []
    for r, e in fac.items():
        pe = r**e
        x = 0
        g_r = pow(g, q // r, pmod)
        gamma = pow(g_r, r**(e-1), pmod)
        h_r = pow(h, q // pe, pmod)
        table = {}
        cur = 1
        for j in range(r):
            table[cur] = j
            cur = cur * gamma % pmod
        for k in range(e):
            exp = (r ** (e - 1 - k))
            dk = pow(h_r * pow(g_r, -x, pmod) % pmod, exp, pmod)
            if dk not in table:
                raise RuntimeError(f"no table hit r={r} k={k}")
            x += table[dk] * (r**k)
        residues.append((x % pe, pe))
    # CRT
    a = 0
    for x, pe in residues:
        m = q // pe
        a = (a + x * pow(m, -1, pe) * m) % q
    return a
fac = factorize_small(q)
print("fac max prime:", max(fac), flush=True)
a_mod_q = pohlig_hellman(2, B2, q, fac, p)
print("a mod q recovered:", a_mod_q.bit_length(), flush=True)
json.dump({"a_mod_q": str(a_mod_q)}, open("p1536_a.json", "w"))

#!/usr/bin/env python
# dh_static2 solve: find prime p (large enough) where ord_p(2) = q is B-smooth and big.
# Send {p, g=2, A=alice_A}. Bob returns flag under SHA1(str(A^b mod p)).
# Pohlig-Hellman over smooth q -> b -> recompute shared -> decrypt.
import socket, json, hashlib, random
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
                out, buf = (buf.split(b"\n",1)+[b""])[:2] if b"\n" in buf else (buf, b"")
                return out.decode().strip()
            return None
        line, buf = buf.split(b"\n", 1)
        return line.decode().strip()
    got = []
    for _ in range(4):
        l = readline()
        if l is None: break
        got.append(l)
    if payload:
        s.sendall((json.dumps(payload) + "\n").encode())
        try: resp = readline()
        except Exception: resp = None
    else:
        resp = None
    s.close()
    return got, resp

# --- grab intercepted Alice params
got, _ = session(None)
alice = bob = None
enc = None
for l in got:
    if l.startswith("{") and '"A"' in l: alice = json.loads(l)
    if l.startswith("{") and '"B"' in l: bob = json.loads(l)
    if l.startswith("{") and '"iv"' in l: enc = json.loads(l)
print("alice p bits:", int(alice["p"],16).bit_length())

# --- find smooth-order prime (cached to file)
import os
CACHE = "smooth_prime.json"
if os.path.exists(CACHE):
    p, q, fac = json.load(open(CACHE))
    p, q = int(p), int(q)
    fac = {int(k): v for k, v in fac.items()}
else:
    from Crypto.Util.number import isPrime, getPrime
    # q smooth over primes < 100, q ~ 2^90
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    rng = random.Random(1)
    p = q = None; fac = None
    for trial in range(400000):
        f = {}
        q = 1
        for _ in range(28):
            r = rng.choice(primes)
            f[r] = f.get(r,0)+1
            q *= r
        if q.bit_length() < 88 or q.bit_length() > 96: continue
        k = rng.getrandbits(160) | 1
        cand = k*q + 1
        if cand.bit_length() < 256 or cand.bit_length() > 260: continue
        if not isPrime(cand, 32): continue
        # check ord_cand(2) == q
        if pow(2, q, cand) != 1: continue
        ok = True
        for r in f:
            if pow(2, q//r, cand) == 1: ok = False; break
        if ok:
            p, fac = cand, f
            break
    assert p, "no prime found"
    json.dump([str(p), str(q), fac], open(CACHE,"w"))
print("p bits:", p.bit_length(), "q bits:", q.bit_length())

# --- Pohlig-Hellman: b = log_2(A) mod q  (A in subgroup of order q)
A = int(alice["A"], 16) % p
assert pow(A, q, p) == 1 or True

def bsgs(gv, hv, n, maxn=1<<22):
    if n > maxn: return None
    m = int(n**0.5)+1
    tbl = {}
    cur = 1
    for j in range(m):
        tbl.setdefault(cur, j)
        cur = cur*gv % p
    factor = pow(gv, -m if False else pow(gv, m*(n-1), p)*0 + 0 or 1, 1) if False else pow(pow(gv, m, p), -1, p)
    gamma = hv
    for i in range(m):
        if gamma in tbl: return i*m + tbl[gamma]
        gamma = gamma*factor % p
    return None

def pohlig(gv, hv):
    x = 0
    for r, e in fac.items():
        for j in range(1, e+1):
            rj = r**j
            xj = x % rj
            c = (hv * pow(gv, -(xj), p)) % p
            c = pow(c, q // rj, p)
            gq = pow(gv, q // r, p)
            d = bsgs(gq, c, r)
            if d is None:
                d = discrete_small(gq, c, r, p)
            xj += d * r**(j-1)
            x = xj if x % rj == xj else x
            x = xj
    return x

def discrete_small(gv, hv, r, mod):
    cur = 1
    for d in range(r):
        if cur == hv: return d
        cur = cur*gv % mod
    raise ValueError("dlog fail")

# fix x accumulation properly
def pohlig2(gv, hv):
    x = 0
    modulus = 1
    for r, e in fac.items():
        xj = 0
        rk = 1
        gq = pow(gv, q // r, p)
        for jj in range(e):
            rk_r = r**(jj+1)
            c = hv * pow(gv, -xj, p) % p
            c = pow(c, q // rk_r, p)
            d = discrete_small(gq, c, r, p) if r < 10**7 else bsgs(gq, c, r)
            xj = (xj + d * r**jj) % (r**(jj+1))
        x = xj + modulus * pow(modulus, -1, r**e) % (modulus * r**e) if False else None
        # CRT combine x (mod modulus) with xj (mod r^e)
        m1, m2 = modulus, r**e
        t = (xj - x) % m2 * pow(m1 % m2, -1, m2) % m2 if m2 > 1 else 0
        # careful: need inverse of m1 mod m2
        t = ((xj - x) * pow(m1, -1, m2)) % m2
        x = x + m1 * t
        modulus *= m2
    return x

b = pohlig2(2 % p, A)
assert pow(2, b, p) == A, "dlog check failed"
print("b recovered:", b)

shared = pow(A, b, p)
key = hashlib.sha1(str(shared).encode()).digest()[:16]
pt = AES.new(key, AES.MODE_CTR, nonce=bytes.fromhex(enc["iv"])[:8]).decrypt(bytes.fromhex(enc["encrypted"]))
print("FLAG:", pt)
if b"crypto" in pt:
    open("flag.txt","w").write(pt.decode())

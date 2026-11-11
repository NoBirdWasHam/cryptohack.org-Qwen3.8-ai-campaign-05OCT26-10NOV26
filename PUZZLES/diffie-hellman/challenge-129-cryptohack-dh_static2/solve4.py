#!/usr/bin/env python
# dh_static2 v4: Bob's static b leaked via B=2^b mod p_crafted with ord_p(2) smooth.
# Fix vs solve3: A=4 (A=2 rejected by range check). p = k*q+1, q product of ~2^38 primes.
import socket, json, time, random, sys
from math import gcd
from Crypto.Util.number import long_to_bytes
from gmpy2 import is_prime as isPrime
from Crypto.Cipher import AES
import hashlib

HOST, PORT = "socket.cryptohack.org", 13378

def session(payload, tries=3):
    err = None
    for _ in range(tries):
        try:
            s = socket.create_connection((HOST, PORT), timeout=25); s.settimeout(6)
            buf = b""
            # tolerant read: collect until quiet, then parse JSON from buffer
            deadline = time.time() + 12
            while time.time() < deadline:
                try:
                    d = s.recv(65536)
                except socket.timeout:
                    if b"{" in buf: break
                    continue
                except Exception:
                    break
                if not d: break
                buf += d
                if b"\n" in buf and b"}" in buf: break
            got = [x for x in buf.decode(errors="replace").split("\n") if x.strip()]
            resp = None
            if payload is not None:
                s.settimeout(20)
                s.sendall((json.dumps(payload) + "\n").encode())
                resp = b""
                deadline = time.time() + 20
                while time.time() < deadline:
                    try:
                        d = s.recv(65536)
                    except socket.timeout:
                        if resp: break
                        continue
                    except Exception:
                        break
                    if not d: break
                    resp += d
                    if b"}" in resp: break
                resp = resp.decode(errors="replace").strip()
            s.close(); return got, resp
        except Exception as e:
            err = e; time.sleep(20)
    return None, f"<fail {err}>"

def parse(lines):
    ph = {}
    for l in lines or []:
        i = l.find("{")
        if i >= 0:
            try: ph.update(json.loads(l[i:]))
            except Exception: pass
    return ph

# ---------- Pohlig-Hellman for g=2 with known smooth order ----------
def bsgs(g, h, n, mod=None):
    mod = mod or n
    import math
    m = int(math.isqrt(n)) + 1
    table = {}
    cur = 1
    for j in range(m):
        if cur not in table: table[cur] = j
        cur = cur * g % mod
    gm = pow(g, m, mod)
    gm = pow(gm, -1, mod)  # giant step multiplies by g^{-m}
    x = h
    for i in range(m):
        if x in table:
            return i * m + table[x]
        x = x * gm % mod
    return None

def pohlig_hellman(g, h, n, fac):
    # g order n (n smooth, fac dict), return x with g^x = h mod p... work mod p
    x = 0; crt_mod = 1
    for r, e in fac.items():
        pe = r ** e
        gi = pow(g, n // pe, P); hi = pow(h, n // pe, P)
        xi = bsgs(gi, hi, pe, P)
        if xi is None: return None
        xi %= pe
        t = ((xi - x) * pow(crt_mod, -1, pe)) % pe
        x = x + crt_mod * t
        crt_mod *= pe
    return x % crt_mod

def order_of_2(P):
    # ord_P(2) given factorization of P-1
    fac = {}
    m = P - 1
    for r in FACQ:
        while m % r == 0:
            fac[r] = fac.get(r, 0) + 1; m //= r
    assert m == 1, "cofactor left"
    o = P - 1
    for r in fac:
        while o % r == 0 and pow(2, o // r, P) == 1:
            o //= r
    fac_o = {}
    for r in fac:
        v = 0; t = o
        while t % r == 0: v += 1; t //= 1 if False else r
        if v: fac_o[r] = v
    return o, fac_o

def make_prime(bits_q=1000, rng=None):
    # q = product of distinct random primes ~2^38; p = k*q+1 prime
    while True:
        qs = []
        q = 1
        while q.bit_length() < bits_q:
            r = random.getrandbits(38) | 1
            if isPrime(r):
                qs.append(r); q *= r
        for kt in range(2, 40000, 2):  # kt EVEN: q odd -> kt*q+1 odd (odd kt made it always even!)
            P = kt * q + 1
            if P.bit_length() < 900: continue
            if isPrime(P):
                facq = {r: 1 for r in qs}
                mm = kt
                f = 2
                while f * f <= mm:
                    while mm % f == 0:
                        facq[f] = facq.get(f, 0) + 1; mm //= f
                    f += 1
                if mm > 1: facq[mm] = facq.get(mm, 0) + 1
                return P, q, facq, kt
        # retry q

def main():
    global P, FACQ
    # 1) capture real session
    got, _ = session(None)
    ph = parse(got)
    if "p" not in ph:
        print("capture failed:", got); return
    P0 = int(ph["p"], 16); G0 = int(ph["g"], 16); A0 = int(ph["A"], 16)
    iv = ph["iv"]; ct = ph["encrypted"]
    print("captured p0 bits", P0.bit_length(), flush=True)

    congr = []
    L = 1
    t0 = time.time()
    for attempt in range(6):
        if L > 2**2050: break
        print('generating prime...', flush=True)
        P, q, FACQ, kt = make_prime()
        print('prime ready', P.bit_length(), 'kt', kt, flush=True)
        o, fac_o = order_of_2(P)
        if o.bit_length() < 900:
            continue
        got2, resp = session({"p": hex(P), "g": "0x2", "A": "0x4"})
        print("send attempt", attempt, "->", str(resp)[:100], flush=True)
        if not resp or '"B"' not in resp:
            time.sleep(10); continue
        o2 = json.loads(resp[resp.find("{"):])
        B = int(o2["B"], 16)
        x = pohlig_hellman(2, B, o, fac_o)
        if x is None:
            print("PH failed", flush=True); time.sleep(10); continue
        # B=2^b -> b ≡ x mod o
        g0 = gcd(o, L)
        if x % g0 != (congr[-1][0] if False else 0) and False: pass
        # consistency vs previous
        ok = True
        for (xo, mo) in congr:
            if x % gcd(mo, o) != xo % gcd(mo, o):
                ok = False; break
        if not ok:
            print("INCONSISTENT b, skipping", flush=True); time.sleep(10); continue
        congr.append((x, o))
        L = L * o // gcd(L, o)
        print(f"b mod {o.bit_length()}-bit order recovered; lcm bits={L.bit_length()} t={time.time()-t0:.0f}", flush=True)
        time.sleep(8)
    if L <= 2**2050 or not congr:
        print("INSUFFICIENT lcm bits:", L.bit_length()); return
    # CRT all
    x = 0; M = 1
    for (xo, mo) in congr:
        Mi = M * mo // gcd(M, mo)
        # combine x ≡ xo mod mo, x ≡ current mod M
        g = gcd(M, mo)
        assert (xo - x) % g == 0
        lcmv = M // g * mo
        x = (x + M * ((xo - x) // g * pow(M // g, -1, mo // g) % (mo // g))) % lcmv
        M = lcmv
    b = x
    print("b bits", b.bit_length(), flush=True)
    shared = pow(A0, b, P0)
    key = hashlib.sha1(str(shared).encode()).digest()[:16]
    pt = AES.new(key, AES.MODE_CTR, nonce=bytes.fromhex(iv)[:8]).decrypt(bytes.fromhex(ct))
    print("PT:", pt, flush=True)

main()

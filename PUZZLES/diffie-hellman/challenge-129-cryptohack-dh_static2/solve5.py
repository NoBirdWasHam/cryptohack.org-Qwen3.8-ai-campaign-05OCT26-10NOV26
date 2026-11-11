#!/usr/bin/env python
# dh_static2 v5: p = 2*R*S+1 (2048b, R 256-bit prime, S smooth ~1790b, fully factored).
# g=2: B = 2^b mod p. PH over the S-part of ord_p(2) leaks b mod S WITHOUT knowing ord:
#   for pe | S: gi = 2^{n/pe}, hi = B^{n/pe} (n = 2RS multiple of ord) -> b mod pe.
# Two sessions with independent S,S' -> CRT b mod lcm > 2^2048 -> shared = A0^b mod P0.
import socket, json, time, random, sys
from math import gcd
from Crypto.Util.number import long_to_bytes
from Crypto.Cipher import AES
import hashlib
from gmpy2 import is_prime, is_probab_prime

HOST, PORT = "socket.cryptohack.org", 13378

def session(payload, tries=3):
    err = None
    for _ in range(tries):
        try:
            s = socket.create_connection((HOST, PORT), timeout=25); s.settimeout(8)
            buf = b""
            while True:
                d = s.recv(65536)
                if not d: break
                buf += d
                if b"\n" in buf: break
            got = buf.decode(errors="replace")
            resp = None
            if payload is not None:
                s.settimeout(20)
                s.sendall((json.dumps(payload) + "\n").encode())
                resp = b""
                while True:
                    d = s.recv(65536)
                    if not d: break
                    resp += d
                    if b"}" in resp: break
                resp = resp.decode(errors="replace").strip()
            s.close(); return got, resp
        except Exception as e:
            err = e; time.sleep(15)
    return None, f"<fail {err}>"

def parse(txt):
    ph = {}
    i = txt.find("{")
    while i >= 0:
        j = txt.find("}", i)
        try:
            o = json.loads(txt[i:j+1])
            for k in ("p","g","A","B","iv","encrypted"):
                if k in o: ph[k] = o[k]
        except Exception:
            pass
        i = txt.find("{", j+1)
    return ph

small = [n for n in range(3, 2000) if is_prime(n)]

def build():
    while True:
        R = (1 << 255) | random.getrandbits(255) | 1
        if not is_prime(R):
            continue
        S = 1; facS = {}
        while S.bit_length() < 1790:
            f = random.choice(small)
            S *= f; facS[f] = facS.get(f, 0) + 1
        p = 2 * R * S + 1
        if p.bit_length() != 2048:
            continue
        if is_probab_prime(p, 12):
            return p, R, S, facS

def bsgs(g, h, n, mod):
    import math
    m = int(math.isqrt(n)) + 1
    table = {}
    cur = 1
    for j in range(m):
        if cur not in table: table[cur] = j
        cur = cur * g % mod
    gm = pow(pow(g, m, mod), -1, mod)
    x = h
    for i in range(m):
        if x in table:
            return i * m + table[x]
        x = x * gm % mod
    return None

def ph_partial(B, p, n, facS):
    # return b mod S given B = 2^b mod p, n = 2RS (multiple of ord), facS full fac of S
    x = 0; crt = 1
    for f, e in facS.items():
        pe = f ** e
        gi = pow(2, n // pe, p); hi = pow(B, n // pe, p)
        if gi == 1:
            continue  # pe not in ord_p(2): no info from this pe
        xi = bsgs(gi, hi, pe, p)
        if xi is None:
            return None
        assert pow(gi, pe, p) == 1 and pow(gi, pe // f, p) != 1
        xi %= pe
        t = ((xi - x) * pow(crt, -1, pe)) % pe
        x += crt * t; crt *= pe
    return x, crt

def crt_pair(x1, m1, x2, m2):
    g = gcd(m1, m2)
    if (x2 - x1) % g: return None
    lcm = m1 // g * m2
    t = ((x2 - x1) // g * pow(m1 // g, -1, m2 // g)) % (m2 // g)
    return (x1 + m1 * t) % lcm

def main():
    got0, _ = session(None)
    if not got0: print("capture failed"); return
    ph0 = parse(got0)
    if "p" not in ph0: print("no p in:", got0[:200]); return
    P0 = int(ph0["p"], 16); A0 = int(ph0["A"], 16)
    iv = ph0["iv"]; ct = ph0["encrypted"]
    print("captured P0", P0.bit_length(), flush=True)

    x = 0; M = 1
    for attempt in range(6):
        if M > 2**2050: break
        p, R, S, facS = build()
        got, resp = session({"p": hex(p), "g": "0x2", "A": "0x4"})
        print(f"session {attempt}: p built, resp:", str(resp)[:90], flush=True)
        if not resp or '"B"' not in resp:
            time.sleep(10); continue
        obj, _ = json.JSONDecoder().raw_decode(resp[resp.find("{"):])
        B = int(obj["B"], 16)
        n = 2 * R * S
        res = ph_partial(B, p, n, facS)
        if res is None:
            print("PH failed", flush=True); time.sleep(10); continue
        # sanity: 2^xs == B on the S-part
        x2, m2 = res
        comb = crt_pair(x, M, x2, m2) if M != 1 else x2
        if M != 1 and comb is None:
            print("CRT inconsistent, skipping", flush=True); time.sleep(10); continue
        if M == 1:
            x, M = x2, m2
        else:
            x, M = comb, M // gcd(M, m2) * m2
        print(f"  b mod S ok; lcm bits now {M.bit_length()}", flush=True)
        time.sleep(6)
    if M <= 2**2050:
        print("INSUFFICIENT bits:", M.bit_length()); return
    b = x
    print("b bits", b.bit_length(), flush=True)
    open("b_recovered.txt","w").write(str(b))
    # verify b against Bob on the ORIGINAL group: B0 should equal g0^b mod P0
    gotv, respv = session({"p": hex(P0), "g": ph0.get("g","0x2"), "A": "0x4"})
    try:
        objv, _ = json.JSONDecoder().raw_decode(respv[respv.find("{"):])
        B0 = int(objv["B"], 16)
        G0 = int(ph0.get("g","0x2"), 16)
        print("b VERIFIED:", pow(G0, b, P0) == B0, flush=True)
    except Exception as e:
        print("verify session failed:", e, str(respv)[:80], flush=True)
    shared = pow(A0, b, P0)
    cands = {
      "sha1_dec16": hashlib.sha1(str(shared).encode()).digest()[:16],
      "sha256_dec": hashlib.sha256(str(shared).encode()).digest()[:16],
      "sha1_bytes": hashlib.sha1(long_to_bytes(shared)).digest()[:16],
      "sha256_bytes": hashlib.sha256(long_to_bytes(shared)).digest()[:16],
      "sha1_hex": hashlib.sha1(hex(shared).encode()).digest()[:16],
    }
    for name, key in cands.items():
        for nlen in (8, 16):
            try:
                pt = AES.new(key, AES.MODE_CTR, nonce=bytes.fromhex(iv)[:nlen]).decrypt(bytes.fromhex(ct))
                tag = "  <<< FLAG" if b"crypto{" in pt or b"CH{" in pt else ""
                print(name, nlen, ":", pt[:60], tag, flush=True)
            except Exception as e:
                print(name, nlen, "ERR", e, flush=True)

main()

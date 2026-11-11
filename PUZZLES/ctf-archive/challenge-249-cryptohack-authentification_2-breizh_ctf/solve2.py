#!/usr/bin/env python3
"""authentification_2-breizh_ctf solver (final).

Bug (provided gcm/gcm.py): encrypt()/decrypt() use gctr(J0, P) instead of
NIST's gctr(inc(J0), P) => the first data keystream block equals the tag
mask E(J0). One known-plaintext guest token (we pick the username) yields:
    E(J0)  = C[0:16] ^ P[0:16]
    S_obs  = T ^ E(J0)              (exact GHASH value of our own ciphertext)
    S_obs  = X1*H^4 + X2*H^3 + X3*H^2 + L*H   (quartic in H; 4 tag blocks)
Solve the univariate quartic over GF(2^128) (gcd with z^q - z, Cantor-
Zassenhaus split, Artin-Schreier for quadratic factors) -> <=4 candidate H,
verified against the token's own GHASH. Then forge
    {"username": "admin", "role": "super_admin"}
with the known keystream prefix: C' = P' ^ ks, T' = GHASH_H(C') ^ E(J0).
verif_token only checks role == super_admin + tag -> flag.
"""
import sys, os, json, re, secrets
from math import ceil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "authentification-2"))
from gcm.gcm import GCM, BLOCK_LEN

IV = b"\x00" * 12
DUMMY = GCM(b"\x00" * 16, IV)   # for ghash() with explicit H
Q = (1 << 128) - 1
ID = 1 << 127   # multiplicative identity alpha^0 in this bit-reversed int rep

# ---------- GF(2^128) = GF(2)[a]/(a^128+a^7+a^2+a+1); int bit k <-> a^(127-k)
def rev(x):
    y = 0
    for i in range(128):
        if (x >> i) & 1:
            y |= 1 << (127 - i)
    return y

def gmul(a, b):
    A = rev(a); B = rev(b)
    r = 0
    for i in range(128):
        if (B >> i) & 1:
            r ^= A << i
    for d in range(254, 127, -1):
        if (r >> d) & 1:
            r ^= (1 << (d - 121)) | (1 << (d - 126)) | (1 << (d - 127)) | (1 << (d - 128))
    return rev(r)

def fpow(a, e):
    r = ID
    while e:
        if e & 1: r = gmul(r, a)
        a = gmul(a, a); e >>= 1
    return r

def finv(a): return fpow(a, Q - 1)
def to_i(bs): return int.from_bytes(bs, "big")
def to_b(v): return v.to_bytes(16, "big")

# ---------- dense polynomials over GF(2^128), low->high
def pdeg(p):
    i = len(p) - 1
    while i > 0 and p[i] == 0: i -= 1
    return i

def ptrim(p): return p[:pdeg(p) + 1]

def pmod(a, m):
    m = list(m); dm = pdeg(m); lm = finv(m[dm])
    a = list(a) + [0] * (dm - len(a) if len(a) < dm else 0)
    while pdeg(a) >= dm:
        d = pdeg(a)
        c = gmul(a[d], lm)
        for j in range(dm + 1):
            a[d - dm + j] ^= gmul(c, m[j])
    return a[:dm]

def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y: r[i + j] ^= gmul(x, y)
    return r

def pdivexact(a, m):
    a = list(a); dm = pdeg(m); lm = finv(m[dm])
    q = [0] * max(1, pdeg(a) - dm + 1)
    while pdeg(a) >= dm and any(a):
        d = pdeg(a); c = gmul(a[d], lm)
        q[d - dm] ^= c
        for j in range(dm + 1):
            a[d - dm + j] ^= gmul(c, m[j])
    return q

def pgcd(a, b):
    a = list(a); b = list(b)
    while any(b):
        a, b = b, pmod(a, b)
    d = pdeg(a)
    inv = finv(a[d])
    return [gmul(c, inv) for c in a[:d + 1]]

def phpow(base, e, m):
    r = [ID]
    b = pmod(list(base), m)
    while e:
        if e & 1: r = pmod(pmul(r, b), m)
        b = pmod(pmul(b, b), m)
        e >>= 1
    return r

def as_root(d):
    """Y with Y^2+Y = d over GF(2^128) (needs Tr(d)=0; m=128 even)."""
    e = gmul(d, d)          # d^2
    s = 0
    for _ in range(64):     # exponents 2^1, 2^3, ..., 2^127
        s ^= e
        e = gmul(gmul(e, e), gmul(e, e))   # e^4
    assert gmul(s, s) ^ s == d, "AS failed"
    return s

def split_roots(g):
    g = ptrim(g)
    d = pdeg(g)
    if d == 0: return []
    if d == 1: return [g[0]]                       # z + c -> root c
    if d == 2:
        u, v = g[1], g[2]
        if u == 0:
            s = fpow(v, 1 << 127)                  # double root sqrt(v)
            return [s]
        Y = as_root(gmul(v, finv(gmul(u, u))))
        return sorted({gmul(u, Y), gmul(u, Y ^ 1)})
    for _ in range(200):
        s = secrets.randbits(128)
        A = phpow([s, 1], Q // 3, g)               # (z+s)^((q-1)/3) mod g
        A = ptrim(A)
        p1 = pgcd(g, ptrim([A[0] ^ ID] + A[1:]))
        a2 = ptrim(pmod(ptrim(pmul(A, A) + A + [ID]), g))
        p2 = pgcd(g, a2)
        facs = [p for p in (p1, p2) if 0 < pdeg(p) < d]
        if facs:
            rest = pdivexact(g, pmul(p1, p2))
            if 0 < pdeg(rest) < d: facs.append(rest)
            roots = []
            for f in facs: roots += split_roots(f)
            return sorted(set(roots))
    raise RuntimeError("CZ failed to split")

def field_roots(f):
    f = ptrim(list(f))
    d = pdeg(f)
    if d == 0: return []
    inv = finv(f[d]); f = [gmul(c, inv) for c in f[:d + 1]]
    F = [0, 1]
    for _ in range(128):
        F = pmod(pmul(F, F), f)                    # z^(2^128) mod f
    z = [0, 1]
    fz = pmod(z, f)                                 # z mod f (deg f >= 1)
    n = max(len(F), len(fz))
    h = [(F + [0] * n)[i] ^ (fz + [0] * n)[i] for i in range(n)]
    g = pgcd(f, ptrim(h))
    return split_roots(g)

# ---------- attack
def tag_buf(C):
    u = BLOCK_LEN * ceil(len(C) / BLOCK_LEN) - len(C)
    return C + b"\x00" * u + (0).to_bytes(8, "big") + (len(C) * 8).to_bytes(8, "big")

def horner(blocks, h):
    pred = 0
    for b in blocks:
        pred = gmul(pred, h) ^ b
    return gmul(pred, h)

def recover_H(C, P, T):
    ks = bytes(a ^ b for a, b in zip(P, C))
    E_J0 = ks[:16]
    S_obs = to_i(bytes(t ^ e for t, e in zip(T, E_J0)))
    buf = tag_buf(C)
    blocks = [to_i(buf[i:i + 16]) for i in range(0, len(buf), 16)]
    # f(z) = X1 z^4 + X2 z^3 + X3 z^2 + L z + S_obs (low->high; blocks=[X1..X4])
    f = ptrim([S_obs] + blocks[::-1])
    cands = []
    for H in field_roots(f):
        if horner(blocks, H) != S_obs:
            continue
        Hb = to_b(H)
        if DUMMY.ghash(buf, Hb) == to_b(S_obs):
            cands.append(Hb)
    return cands, ks

def forge_with(Hb, ks, target_pt):
    Cn = bytes(p ^ k for p, k in zip(target_pt, ks))
    Sn = DUMMY.ghash(tag_buf(Cn), Hb)
    Tn = bytes(s ^ e for s, e in zip(Sn, ks[:16]))
    return Cn.hex() + ";" + Tn.hex()

TARGET = json.dumps({"username": "admin", "role": "super_admin"}).encode()
USER = "u" * 12   # json len 45: 4 tag blocks (quartic), keystream >= len(TARGET)
TOKEN_PT = json.dumps({"username": USER, "role": "guest"}).encode()
assert len(TOKEN_PT) <= 48 and len(TOKEN_PT) >= len(TARGET), (len(TOKEN_PT), len(TARGET))

def attack_from_token(tok):
    C = bytes.fromhex(tok.split(";")[0]); T = bytes.fromhex(tok.split(";")[1])
    cands, ks = recover_H(C, TOKEN_PT, T)
    return [forge_with(Hb, ks, TARGET) for Hb in cands]

FLAG_RE = re.compile(r"[A-Za-z0-9_]{2,16}\{[^{}\n]{3,200}\}")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    if mode == "local":
        from crypto import build_token, verif_token
        ok = 0; nroots = []
        trials = 10
        for t in range(trials):
            key = secrets.token_bytes(16)
            tok = build_token(key, USER, "guest")
            cands = attack_from_token(tok)
            nroots.append(len(cands))
            won = any(verif_token(key, ft) for ft in cands)
            ok += won
            print(f"trial {t}: roots={len(cands)} win={won}")
        print(f"local: {ok}/{trials}; root counts {nroots}")
        return
    import requests
    base = sys.argv[2] if len(sys.argv) > 2 else "http://archive.cryptohack.org:59670"
    s = requests.Session()
    pw = secrets.token_hex(8)
    for attempt in range(8):
        try:
            try:
                s.get(f"{base}/reset-db", timeout=15)
            except Exception:
                pass
            r = s.post(f"{base}/register", data={"username": USER, "password": pw}, timeout=15)
            if r.status_code == 403:
                s.get(f"{base}/reset-db", timeout=15)
                s.post(f"{base}/register", data={"username": USER, "password": pw}, timeout=15)
            r = s.post(f"{base}/login", data={"username": USER, "password": pw},
                       allow_redirects=False, timeout=15)
            tok = r.cookies["auth"]
        except Exception as e:
            print(f"[{attempt}] fetch failed: {e}"); continue
        try:
            forgs = attack_from_token(tok)
        except Exception as e:
            print(f"[{attempt}] attack failed: {e}"); continue
        print(f"[{attempt}] {len(forgs)} candidate forgeries")
        for ft in forgs:
            try:
                r = s.get(f"{base}/admin", cookies={"auth": ft}, timeout=15)
            except Exception as e:
                print("admin err", e); break
            if "Well played" in r.text:
                m = FLAG_RE.search(r.text)
                print("FLAG:", m.group(0) if m else r.text)
                return
        print(f"[{attempt}] no flag (key rotated by others? retrying)")
    print("NO FLAG after retries"); sys.exit(1)

if __name__ == "__main__":
    main()

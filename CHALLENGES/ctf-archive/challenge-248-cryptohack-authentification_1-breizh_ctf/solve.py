#!/usr/bin/env python3
"""
authentification_1-breizh_ctf solver.
Vuln: intern's GCM never increments the counter (encrypt uses J0 as first CTR block)
and uses E(J0) as the tag mask -> E(J0) == ks[0:16] == P[0:16]^C[0:16] (known plaintext).
Recover H = GHASH key as a root of low-degree poly over GF(2^128), forge super_admin token.
Usage: python3 solve.py [--remote http://archive.cryptohack.org:61277]
"""
import os, sys, random
from json import dumps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "authentification-1"))
from gcm import GCM, IV_LEN, BLOCK_LEN, xor  # noqa: E402
from gcm.utils import bytes_to_bits, bits_to_bytes  # noqa: E402

# ---------------- GF(2^128): fast int mul, cross-verified against the intern's ------
_DUMMY = GCM(b"\x00" * 16, b"\x00" * IV_LEN)
_R = 0xe1 << 120

def _slow_mul(X, Y):
    return _DUMMY.mul(X, Y)

def gf_mul(X, Y):
    x = int.from_bytes(X, "big"); y = int.from_bytes(Y, "big")
    z = 0; v = y
    for i in range(127, -1, -1):
        if (x >> i) & 1:
            z ^= v
        v = (v >> 1) ^ _R if v & 1 else v >> 1
    return z.to_bytes(16, "big")

for _ in range(500):  # must match the intern's implementation exactly
    _a, _b = os.urandom(16), os.urandom(16)
    assert gf_mul(_a, _b) == _slow_mul(_a, _b), "GF mul mismatch vs intern impl"

def gf_sqr(x): return gf_mul(x, x)

def gf_inv(x):  # x^(2^128-2), generic square-and-multiply
    ONE = b"\x80" + b"\x00" * 15  # GCM bit-reflected identity (MSB = x^0)
    res, base, e = ONE, x, (1 << 128) - 2
    while e:
        if e & 1:
            res = gf_mul(res, base)
        base = gf_sqr(base)
        e >>= 1
    return res

# ---------------- poly arithmetic over GF(2^128), coeffs little-endian --------------
def p_strip(p):
    p = list(p)
    while len(p) > 1 and p[-1] == b"\x00" * 16:
        p.pop()
    return p

def p_deg(p): return len(p_strip(p)) - 1

def p_monic(p):
    p = p_strip(p)
    lc = p[-1]
    if lc == b"\x80" + b"\x00" * 15:
        return p
    inv = gf_inv(lc)
    return [gf_mul(c, inv) for c in p]

def p_add(a, b):
    n = max(len(a), len(b))
    return p_strip([xor(a[i] if i < len(a) else b"\x00" * 16,
                         b[i] if i < len(b) else b"\x00" * 16) for i in range(n)])

def p_mul(a, b):
    res = [b"\x00" * 16] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai != b"\x00" * 16:
            for j, bj in enumerate(b):
                if bj != b"\x00" * 16:
                    res[i + j] = xor(res[i + j], gf_mul(ai, bj))
    return p_strip(res)

def p_square(a):
    res = [b"\x00" * 16] * (2 * len(a) - 1)
    for i, ai in enumerate(a):
        res[2 * i] = gf_sqr(ai)
    return p_strip(res)

def p_mod(a, m):  # m monic
    a = p_strip(a)
    while p_deg(a) >= p_deg(m) and a != [b"\x00" * 16]:
        d = p_deg(a) - p_deg(m)
        coef = a[-1]
        a = p_add(a, [b"\x00" * 16] * d + [gf_mul(coef, c) for c in m])
    return a

def p_gcd(a, b):
    a, b = p_monic(a), p_monic(b)
    zero = [b"\x00" * 16]
    while b != zero:
        a, b = b, p_monic(p_mod(a, b))
    return a

def p_all_roots_in_F(f, max_deg=5):
    """All roots of f in GF(2^128): g=gcd(f, x^(2^128)+x), split squarefree g by abs trace."""
    f = p_monic(f)
    r = [b"\x00" * 16, b"\x80" + b"\x00" * 15]  # x
    for _ in range(128):
        r = p_mod(p_square(r), f)
    g = p_gcd(f, p_add(r, [b"\x00" * 16, b"\x80" + b"\x00" * 15]))
    roots, todo = [], []
    if p_deg(g) >= 1:
        todo.append(p_monic(g))
    # split off linear factors directly
    todo2 = []
    for h in todo:
        if p_deg(h) == 1:
            roots.append(h[0])  # x + c -> root c (char 2)
        else:
            todo2.append(h)
    while todo2:
        h = todo2.pop()
        if p_deg(h) == 1:
            roots.append(h[0]); continue
        done = False
        for _ in range(40):
            a = os.urandom(16)
            while a == b"\x00" * 16: a = os.urandom(16)
            term = p_mod([b"\x00" * 16, a], h)
            T = [b"\x00" * 16]
            for _ in range(128):  # absolute trace GF(2^128)/GF(2), evaluated mod h
                T = p_add(T, term)
                term = p_mod(p_square(term), h)
            s1 = p_gcd(h, T)
            if 0 < p_deg(s1) < p_deg(h):
                todo2.append(s1)
                todo2.append(p_monic(_p_div(h, s1)))
                done = True
                break
        if not done:
            raise RuntimeError("splitting failed for deg %d" % p_deg(h))
    return roots

def _p_div(a, b):  # exact division, b monic
    a, b = p_strip(a), p_monic(b)
    q = [b"\x00" * 16] * max(1, p_deg(a) - p_deg(b) + 1)
    while p_deg(a) >= p_deg(b) and a != [b"\x00" * 16]:
        d = p_deg(a) - p_deg(b)
        coef = a[-1]
        q[d] = coef
        a = p_add(a, [b"\x00" * 16] * d + [gf_mul(coef, c) for c in b])
    return q

# ---------------- attack ----------------
def ghash_with(H, buf):
    Y = b"\x00" * BLOCK_LEN
    for i in range(0, len(buf), BLOCK_LEN):
        Y = gf_mul(xor(Y, buf[i:i + BLOCK_LEN]), H)
    return Y

def build_buf(C):
    u = BLOCK_LEN * ((len(C) + 15) // 16) - len(C)
    return C + b"\x00" * u + (0).to_bytes(8, "big") + (len(C) * 8).to_bytes(8, "big")

def recover_H(P, C, tag):
    S = xor(tag, xor(P[:16], C[:16]))  # GHASH(buf,H) = tag ^ E(J0), E(J0)=ks0
    buf = build_buf(C)
    blocks = [buf[i:i + BLOCK_LEN] for i in range(0, len(buf), BLOCK_LEN)]
    f = [S] + blocks[::-1]  # const S, leading block * x^m
    cands = p_all_roots_in_F(f)
    good = [H for H in cands if ghash_with(H, buf) == S]
    if not good:
        raise RuntimeError("no H candidate verifies GHASH")
    return good  # may be >1 root -> resolve against server oracle

def forge(P, C, tag, new_pt):
    if len(new_pt) > len(P):
        raise ValueError("forged token longer than known keystream")
    ks = xor(P, C)
    Cn = xor(new_pt, ks[:len(new_pt)])
    out = []
    for H in recover_H(P, C, tag):
        tag_n = xor(ghash_with(H, build_buf(Cn)), ks[:16])
        out.append(Cn.hex() + ";" + tag_n.hex())
    return out

def attack_session(get_token):
    user = "a" * 12
    P = dumps({"username": user, "role": "guest"}).encode()
    cthex, taghex = get_token(user)
    C, tag = bytes.fromhex(cthex), bytes.fromhex(taghex)
    assert xor(P, C) is not None
    forged = forge(P, C, tag, dumps({"username": "a", "role": "super_admin"}).encode())
    return forged

# ---------------- local simulation ----------------
def test_local():
    from crypto import build_token, verif_token
    for t in range(3):
        key = os.urandom(BLOCK_LEN)
        user = "a" * 12
        tok = build_token(key, user, "guest")
        P = dumps({"username": user, "role": "guest"}).encode()
        cthex, taghex = tok.split(";")
        C, tag = bytes.fromhex(cthex), bytes.fromhex(taghex)
        ks0 = xor(P[:16], C[:16])
        assert xor(tag, ks0) == None or True
        forged_list = forge(P, C, tag, dumps({"username": "a", "role": "super_admin"}).encode())
        assert verif_token(key, tok) == False, "guest token should not verify"
        assert any(verif_token(key, fg) for fg in forged_list), "a forged token must verify"
        print(f"local test {t}: OK ({len(forged_list)} H candidates, one verifies)")

# ---------------- remote ----------------
def attack_remote(url):
    import requests, re, time
    s = requests.Session()
    for attempt in range(6):
        s.get(url + "/reset-db", timeout=30)
        user = "a" * 12
        r = s.post(url + "/register", data={"username": user, "password": "pw"}, timeout=30)
        if r.status_code == 403:
            time.sleep(2); continue
        r = s.post(url + "/login", data={"username": user, "password": "pw"},
                   allow_redirects=False, timeout=30)
        if "auth" not in r.cookies:
            print("login failed:", r.status_code); time.sleep(2); continue
        tok = r.cookies["auth"]
        if tok.startswith('"'):
            tok = tok.strip('"').replace("\\073", ";")
        cthex, taghex = tok.split(";")
        P = dumps({"username": user, "role": "guest"}).encode()
        C, tag = bytes.fromhex(cthex), bytes.fromhex(taghex)
        forged_list = forge(P, C, tag, dumps({"username": "a", "role": "super_admin"}).encode())
        for i, fg in enumerate(forged_list):
            c2, t2 = fg.split(";")
            # ';' in a cookie value must go over the wire quoted with octal escape
            hdr = 'auth="%s\\073%s"' % (c2, t2)
            r = requests.get(url + "/admin", headers={"Cookie": hdr}, timeout=30)
            m = re.search(r"[A-Za-z0-9!-~_-]*\{[^{}]*\}", r.text)
            if m and "Well played" in r.text:
                print("FLAG:", m.group(0))
                return m.group(0)
            print(f"candidate {i}: no flag ({r.text[-120:]!r})")
        time.sleep(2)
    return None

if __name__ == "__main__":
    if "--remote" in sys.argv:
        attack_remote(sys.argv[sys.argv.index("--remote") + 1])
    else:
        test_local()

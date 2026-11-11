#!/usr/bin/env python3
"""Attack: attacker-chosen n = 3^484 (cyclic smooth-order group),
choose e AFTER seeing suffix via 2-adic... no: Pohlig-Hellman DLP in <SIG mod n>.
Digest = 00 01 FF^58 00 || SHA1-DigestInfo || SHA1(msg)  (verified vs live server)."""
import hashlib, re, secrets
from Crypto.Util.number import bytes_to_long, long_to_bytes

BIT = 768
DI = bytes.fromhex("3021300906052b0e03021a05000414")  # SHA1 DigestInfo (15B)

def em(msg, em_len=96):
    t = DI + hashlib.sha1(msg).digest()
    ps = em_len - len(t) - 3
    return b"\x00\x01" + b"\xff"*ps + b"\x00" + t

A_TOP = int.from_bytes(em(b"")[:76], "big")  # top 76 bytes, hash-independent

def target_from_h(h):  # h = 20-byte sha1 digest
    return A_TOP * 2**160 + int.from_bytes(h, "big")

# ---------- group: (Z/p^k)*, cyclic, order p^(k-1)*(p-1), smooth ----------
def pick_modulus(SIG):
    for p in (5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if SIG % p:
            k = 1
            while p**k < 2**761: k += 1
            return p, k, p**k
    raise RuntimeError("no small prime works")

def factor_smooth(M):
    fac = {}
    d = 2
    while d*d <= M:
        while M % d == 0: fac[d] = fac.get(d,0)+1; M//=d
        d += 1
    if M > 1: fac[M] = fac.get(M,0)+1
    return fac

def order_of(g, n, M):
    ordm = M
    for q in factor_smooth(M):
        while ordm % q == 0 and pow(g, ordm//q, n) == 1:
            ordm //= q
    return ordm

def dlog_smooth(g, t, n, ordm):
    """DLP in cyclic subgroup <g> of smooth order ordm; t must be in <g>."""
    res = []
    for q, a in factor_smooth(ordm).items():
        qa = q**a
        gq = pow(g, ordm//qa, n); tq = pow(t, ordm//qa, n)
        gamma = pow(gq, qa//q, n)
        table = {}
        acc = 1
        for d in range(q):
            table[acc] = d; acc = acc*gamma % n
        x = 0
        for j in range(a):
            hj = pow(tq * pow(gq, -x, n) % n, qa//(q**(j+1)), n)
            if hj not in table: return None
            x += table[hj] * q**j
        res.append((x, qa))
    # CRT (coprime moduli)
    r, mm = 0, 1
    for ri, mi in res:
        r += mm * (((ri - r) % mi) * pow(mm % mi, -1, mi) % mi)
        mm *= mi
    return r % mm

# ---------- gates ----------
BTC_PAT = re.compile("^Please send all my money to ([1-9A-HJ-NP-Za-km-z]+)$")
ALPHA = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58(raw):
    n = int.from_bytes(raw, "big")
    s = ""
    while n: n, r = divmod(n, 58); s = ALPHA[r] + s
    return "1"*(len(raw) - len(raw.lstrip(b"\x00"))) + s

def btc_addr(payload20):
    raw = b"\x00" + payload20
    ck = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[:4]
    return base58(raw + ck)

def gate_msgs(i, suffix):
    """yield (msg, full_message_bytes) candidates for gate i."""
    if i == 0:
        c = 0
        while True:
            x = str(c); c += 1
            core = f"This is a test{x}for a fake signature."
            yield core + suffix, core
    elif i == 1:
        c = 0
        while True:
            n = c; s = ""
            while True:
                s = chr(ord('a') + n % 26) + s
                n //= 26
                if n == 0: break
            c += 1
            core = f"My name is {s} and I own CryptoHack.org"
            yield core + suffix, core
    else:
        while True:
            addr = btc_addr(secrets.token_bytes(20))
            core = f"Please send all my money to {addr}"
            yield core + suffix, core

PATTERNS = [
    re.compile(r"^This is a test(.*)for a fake signature.$").match,
    re.compile(r"^My name is ([a-zA-Z\s]+) and I own CryptoHack.org$").match,
    BTC_PAT.match,
]

def solve(SIG, suffix, verbose=True):
    p, k, n = pick_modulus(SIG)
    M = (p-1) * p**(k-1)
    g = SIG % n
    ordm = order_of(g, n, M)
    if verbose: print(f"[+] p={p} k={k} n_bits={n.bit_length()} ord_bits={ordm.bit_length()}")
    shares = []
    for i in range(3):
        cnt = 0
        for msg, core in gate_msgs(i, suffix):
            cnt += 1
            if not PATTERNS[i](core):
                raise RuntimeError(f"regex fail gate {i}: {core!r}")
            t = target_from_h(hashlib.sha1(msg.encode()).digest())
            if pow(t, ordm, n) != 1:
                continue
            e = dlog_smooth(g, t, n, ordm)
            if e is None or e == 0:
                continue
            assert pow(g, e, n) == t
            if verbose: print(f"[+] gate {i}: tries={cnt} e_bits={e.bit_length()}")
            shares.append(i)
            yield i, e, msg
            break

if __name__ == "__main__":
    # ---- local simulation of the server claim logic ----
    from Crypto.Util.number import getPrime, inverse
    print("simulating server...")
    p, q = getPrime(384), getPrime(384)
    Ns = p*q; phi = (p-1)*(q-1); Es = 65537; Ds = inverse(Es, phi)
    MSG = b'We are MAINT-ACCOUNT and Jack and we own CryptoHack.org'
    SIGs = pow(bytes_to_long(em(MSG)), Ds, Ns)
    suffix = secrets.token_hex(32)
    FLAG = b"crypto{test_flag_local_simulation}"
    shares = [secrets.token_bytes(len(FLAG)) for _ in range(2)]
    last = FLAG
    for s in shares: last = bytes(x^y for x,y in zip(last,s))
    shares.append(last)
    ok = 0
    nmod = pick_modulus(SIGs)[2]
    for i, e, msg in solve(SIGs, suffix):
        digest = em(msg.encode())
        if bytes_to_long(digest) == pow(SIGs, e, nmod) and PATTERNS[i](msg[:-len(suffix)]):
            ok += 1
    rec = bytes(x^y^z for x,y,z in zip(*shares))
    print("claims passed:", ok, "recovered:", rec)
    assert ok == 3 and rec == FLAG
    print("LOCAL SIM OK")

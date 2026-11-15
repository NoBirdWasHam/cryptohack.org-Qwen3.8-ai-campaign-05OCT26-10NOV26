"""2d_dlog (CryptoHack, 40 pts) — 2D Pohlig-Hellman, 2-adic lifting.

Recovered instance parameters (from the 4 given points; the visible source.sage
is a template with different exponents):
  p = 2^127 - 1  (prime),  F = F_p(i), i^2 = -1
  E: y^2 = x^3 + x   (a = 1, b = 0, j = 1728, supersingular since p ≡ 3 mod 4)
  #E(F_{p^2}) = (p+1)^2 = 2^254;  P, Q have order 2^127
Task: (a,b,c,d) with R = [a]P + [b]Q, S = [c]P + [d]Q  (mod 2^127).
From gen_pubkey: kernel = P + [n]Q  ->  n is one of (a,b) (or its 2^127-complement).
Flag: try crypto{str(n)} directly AND AES-CTR(iv, ct) with keys derived from n.
"""
import re, hashlib

P = (1 << 127) - 1
E = 127  # 2-primary exponent

text = open(r"~\Practice_runs\cryptohack_org\challenge-209-cryptohack-2d_dlog\output.txt", encoding="utf-8").read()
def coord(c):
    c = c.strip()
    m = re.match(r"^(-?\d+)\*i\s*([+-])\s*(\d+)$", c)
    if m:
        im = int(m.group(1)) % P
        re_ = int(m.group(3)) % P if m.group(2) == "+" else (-int(m.group(3))) % P
        return (re_, im)
    m = re.match(r"^(-?\d+)$", c)
    if m: return (int(m.group(1)) % P, 0)
    raise ValueError(c)
pts = {}
for name in "PQRS":
    m = re.search(name + r"\s*=\s*(\(.*?:\s*1\))", text)
    mm = re.match(r"\((.*?)\s*:\s*(.*?)\s*:\s*1\)\s*$", m.group(1).strip())
    pts[name] = (coord(mm.group(1)), coord(mm.group(2)))
iv = bytes.fromhex(re.search(r"iv\s*=\s*'([0-9a-f]+)'", text).group(1))
ct = bytes.fromhex(re.search(r"ct\s*=\s*'([0-9a-f]+)'", text).group(1))

# ---------- F_{p^2} ----------
def f2_add(x, y): return ((x[0]+y[0]) % P, (x[1]+y[1]) % P)
def f2_sub(x, y): return ((x[0]-y[0]) % P, (x[1]-y[1]) % P)
def f2_neg(x): return ((-x[0]) % P, (-x[1]) % P)
def f2_mul(x, y): return ((x[0]*y[0]-x[1]*y[1]) % P, (x[0]*y[1]+x[1]*y[0]) % P)
def f2_inv(x):
    d = (x[0]*x[0]+x[1]*x[1]) % P
    di = pow(d, P-2, P)
    return ((x[0]*di) % P, (-x[1]*di) % P)
def f2_div(x, y): return f2_mul(x, f2_inv(y))
def f2_eq(x, y): return x[0] == y[0] and x[1] == y[1]
ONE = (1, 0)

# ---------- EC: y^2 = x^3 + x ----------
O = None
def ec_add(Pt, Qt):
    if Pt is O: return Qt
    if Qt is O: return Pt
    (x1, y1), (x2, y2) = Pt, Qt
    if x1 == x2:
        if y1 == y2:
            if y1 == (0, 0):
                return O  # 2-torsion point: vertical tangent, 2P = O
            lam = f2_div(f2_add(f2_mul((3 % P, 0), f2_mul(x1, x1)), ONE), f2_mul((2 % P, 0), y1))  # (3x^2+1)/(2y)
        else:
            return O
    else:
        lam = f2_div(f2_sub(y2, y1), f2_sub(x2, x1))
    x3 = f2_sub(f2_mul(lam, lam), f2_add(x1, x2))
    y3 = f2_sub(f2_mul(lam, f2_sub(x1, x3)), y1)
    return (x3, y3)
def ec_neg(Pt):
    if Pt is O: return O
    return (Pt[0], f2_neg(Pt[1]))
def ec_mul(k, Pt):
    R, Q = O, Pt
    while k:
        if k & 1: R = ec_add(R, Q)
        Q = ec_add(Q, Q)
        k >>= 1
    return R

# ---------- self tests ----------
def oncurve(pt):
    if pt is O: return True
    x, y = pt
    return f2_eq(f2_mul(y, y), f2_add(f2_mul(x, f2_mul(x, x)), x))
assert all(oncurve(pts[k]) for k in "PQRS"), "points not on y^2=x^3+x"
assert ec_mul(1 << E, pts["P"]) is O and ec_mul(1 << E, pts["Q"]) is O
assert ec_mul(1 << (E-1), pts["P"]) is not O
print("arithmetic validated: [2^127]P = O, [2^127]Q = O, order exact")

# ---------- 2D dlog via 2-adic lifting ----------
def dlog2d(T, Pt, Qt, e=E):
    P1 = ec_mul(1 << (e-1), Pt)   # order 2
    Q1 = ec_mul(1 << (e-1), Qt)
    cand = {O: (0, 0), P1: (1, 0), Q1: (0, 1), ec_add(P1, Q1): (1, 1)}
    a = b = 0
    A = O  # accumulated [a]Pt + [b]Qt
    for k in range(e):
        D = ec_add(T, ec_neg(A))              # = 2^k * (a_{k+1} Pt + b_{k+1} Qt)
        Dk = ec_mul(1 << (e-k-1), D)          # in {O, P1, Q1, P1+Q1}
        ab = cand.get(Dk)
        assert ab is not None, f"level {k}: {Dk} not a candidate"
        if ab[0]:
            A = ec_add(A, ec_mul(1 << k, Pt))
            a += 1 << k
        if ab[1]:
            A = ec_add(A, ec_mul(1 << k, Qt))
            b += 1 << k
    assert ec_add(ec_mul(a, Pt), ec_mul(b, Qt)) == T
    return a, b

a, b = dlog2d(pts["R"], pts["P"], pts["Q"])
c, d = dlog2d(pts["S"], pts["P"], pts["Q"])
print(f"R = [{a}]P + [{b}]Q")
print(f"S = [{c}]P + [{d}]Q")
print(f"(a,b,c,d) = ({a}, {b}, {c}, {d})")

# ---------- flag candidates ----------
def aes_attempts(n):
    from Crypto.Cipher import AES
    seeds = {
        "sha256(str(n))": hashlib.sha256(str(n).encode()).digest(),
        "n.to_bytes(16,big)": n.to_bytes(16, "big"),
        "n.to_bytes(32,big)": n.to_bytes(32, "big"),
        "sha256(a,b,c,d csv)": hashlib.sha256(f"{a},{b},{c},{d}".encode()).digest(),
        "sha256(abcd 16B concat)": hashlib.sha256(
            a.to_bytes(16,'big') + b.to_bytes(16,'big') + c.to_bytes(16,'big') + d.to_bytes(16,'big')).digest(),
        "sha256(str concat)": hashlib.sha256(
            (str(a)+str(b)+str(c)+str(d)).encode()).digest(),
        "str concat zero-pad 32": (f"{a}{b}{c}{d}".encode() + b"\0"*32)[:32],
        "sha256(flag-cand)": hashlib.sha256(f"crypto{{{n}}}".encode()).digest(),
        "md5(str(n))*2": hashlib.md5(str(n).encode()).digest() * 2,
    }
    hits = []
    for kname, key in seeds.items():
        for ks in (16, 32):
            if len(key) != ks: continue
            pt_ = AES.new(key[:ks], AES.MODE_CTR, nonce=iv[:15], initial_value=iv[15:]).encrypt(ct)
            if b"crypto{" in pt_[:40]:
                hits.append((kname, ks, pt_))
    return hits

cands = []
for name, v in (("a", a), ("b", b), ("c", c), ("d", d)):
    cands += [(name, v), (name, (1 << E) - v)]

found = None
for name, n in cands:
    hits = aes_attempts(n)
    if hits:
        for kname, ks, pt_ in hits:
            print(f"HIT key={kname} ks={ks} (n from {name}): {pt_!r}")
            found = pt_
    else:
        print(f"n from {name}: {n}  -> direct flag candidate: crypto{{{n}}}")
print("done; found =", found[:64] if found else None)

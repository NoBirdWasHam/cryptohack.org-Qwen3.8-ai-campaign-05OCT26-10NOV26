# GLP420 (HackTM 2023) solver: ternary-key ring-LWE key recovery via CVP + forgery y=0
# Run with: ~/tools/crypto-ctf/venv/Scripts/python.exe solve.py [--local]
import sys, socket, hashlib
from random import randrange
from Crypto.Util.number import bytes_to_long, long_to_bytes

q = 8383489
n = 420
b = 16383
w = 3
MSG = b"sign me!"

def centered(v): 
    v %= q
    return v - q if v > q // 2 else v

def mul(p, r):  # multiplication mod x^n - 1, coeffs any ints
    o = [0] * n
    for j, rj in enumerate(r):
        if rj:
            for i in range(n):
                o[(i + j) % n] += p[i] * rj
    return [x % q for x in o]

def polyhash(poly, m):
    h = hashlib.sha256()
    for i in range(n):
        h.update(long_to_bytes(int(poly[i]) % q, 3))
    h.update(m)
    return h.digest()

def hash2poly(h):
    hi = bytes_to_long(h)
    return [((1 << i) & hi != 0) for i in range(n)]

def encode(poly):
    return b"".join(long_to_bytes(int(poly[i]) % q, 3) for i in range(n))

def decode(bs):
    assert len(bs) == 3 * n
    return [bytes_to_long(bs[i:i+3]) for i in range(0, 3 * n, 3)]

def verify_real(m, z1, z2, c, t, a):
    for z in (z1, z2):
        for i in range(n):
            if min(z[i] % q, q - z[i] % q) > b - w:
                return False
    az = mul(a, z1)
    u = [(az[i] + z2[i] - mul(t, c)[i]) % q for i in range(n)]
    d = hash2poly(polyhash(u, m))
    return d == c

# ---- polynomial arithmetic over F_q for ring inverse ----
def poly_inv_mod(p, modpoly):  # extended euclid, p invertible mod modpoly
    def trim(a):
        a = a[:]
        while len(a) > 1 and a[-1] == 0: a.pop()
        return a
    def polydivmod(a, bb):  # returns (quo, rem) over F_q
        a = [x % q for x in a]; bb = trim(bb[:])
        if len(bb) == 1 and bb[0] == 0: raise ZeroDivisionError
        rb = trim(bb[:])[:]
        qd = [0] * max(len(a) - len(rb) + 1, 1)
        for k in range(len(a) - len(rb), -1, -1):
            c = a[k + len(rb) - 1] * pow(rb[-1], q - 2, q) % q
            qd[k] = c
            for t_ in range(len(rb)):
                a[k + t_] = (a[k + t_] - c * rb[t_]) % q
        return qd, trim(a)
    r0, r1 = trim(modpoly[:]), trim([x % q for x in p])
    s0, s1 = [0], [1]
    while not (len(r1) == 1 and r1[0] == 0):
        qq, rr = polydivmod(r0, r1)
        r0, r1 = r1, rr
        ss = [(s0[i] if i < len(s0) else 0) - sum(qq[j] * s1[i-j] for j in range(len(qq)) if i-j >= 0) for i in range(len(s0)+len(qq))]
        s0, s1 = s1, [x % q for x in ss]
    if not (len(r0) == 1):
        raise ValueError("not invertible")
    inv = pow(r0[0], q - 2, q)
    return [x * inv % q for x in s0]

def circulant_cvp_solve(a, t):
    """recover ternary s,e with t = a*s + e mod (x^n-1, q) via CVP."""
    from fpylll import IntegerMatrix, CVP, BKZ
    M = IntegerMatrix(2 * n, n)
    for k in range(n):
        for j in range(n):
            M[k, j] = centered(a[(k - j) % n])
    from fpylll import IntegerMatrix, LLL, CVP
    import time as _t
    for i in range(n):
        M[n + i, i] = q
    target = [centered(t[i]) for i in range(n)]
    t0 = _t.time()
    LLL.reduction(M)
    print("LLL done in %.1fs" % (_t.time() - t0), flush=True)
    rows = [[int(M[i, j]) for j in range(n)] for i in range(2 * n)]
    rows = [r for r in rows if any(r)]
    print("nonzero rows:", len(rows), flush=True)
    B = IntegerMatrix(len(rows), n)
    for i, r in enumerate(rows):
        for j in range(n):
            B[i, j] = r[j]
    t0 = _t.time()
    v = CVP.babai(B, target)
    print("Babai done in %.1fs" % (_t.time() - t0), flush=True)
    e = [target[i] - int(v[i]) for i in range(n)]
    ec = [centered(x) for x in e]
    if max(map(abs, ec)) > 1:
        raise RuntimeError("CVP error not ternary: %s" % (sorted(map(abs, ec))[-5:]))
    te = [(t[i] - ec[i]) % q for i in range(n)]
    x_pow_n_minus_1 = [0] * (n + 1); x_pow_n_minus_1[n] = 1; x_pow_n_minus_1[0] = -1
    a_inv = poly_inv_mod(a, x_pow_n_minus_1)
    s = mul(te, a_inv)
    sc = [centered(x) for x in s]
    if max(map(abs, sc)) > 1:
        raise RuntimeError("s not ternary")
    return sc, ec

def forge(a, t):
    s, e = circulant_cvp_solve(a, t)
    zero = [0] * n
    c = hash2poly(polyhash(zero, MSG))
    z1 = mul(s, c)
    z2 = mul(e, c)
    return z1, z2, c

def selftest():
    a = [randrange(1, q) for _ in range(n)]
    s = [randrange(-1, 2) for _ in range(n)]
    e = [randrange(-1, 2) for _ in range(n)]
    t = [(mul(a, s)[i] + e[i]) % q for i in range(n)]
    z1, z2, c = forge(a, t)
    ok = verify_real(MSG, z1, z2, c, t, a)
    print("SELFTEST verify =", ok)
    return ok

if __name__ == "__main__":
    if "--local" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sock = socket.create_connection(("archive.cryptohack.org", 26931), timeout=30)
    f = sock.makefile("rwb")
    def readline():
        line = f.readline()
        if not line: raise EOFError("server closed")
        print("S:", line.decode().strip()[:120])
        return line.decode()
    l1 = readline(); l2 = readline()
    a = decode(bytes.fromhex(l1.split("=")[1].strip()))
    t = decode(bytes.fromhex(l2.split("=")[1].strip()))
    print("a[0..3]:", a[:4], " t[0..3]:", t[:4])
    z1, z2, c = forge(a, t)
    assert verify_real(MSG, z1, z2, c, t, a), "local verify failed"
    for z in (z1, z2, c):
        f.write(encode(z).hex().encode() + b"\n")
    f.flush()
    resp = readline()
    print("RESP:", resp)
    f.close(); sock.close()

# GLP420 (HackTM 2023) final solver.
# Run: ~/tools/crypto-ctf/venv/Scripts/python.exe solve_v3.py [--local]
# Needs ./lll.exe next to it (gcc -O3 -march=native -o lll.exe lll.c).
import sys, os, socket, hashlib, subprocess, tempfile, threading
_BABAI_LOCK = threading.Lock()
from random import randrange
from Crypto.Util.number import bytes_to_long, long_to_bytes

q = 8383489
n = 420
b = 16383
w = 3
MSG = b"sign me!"
HERE = os.path.dirname(os.path.abspath(__file__))

def centered(v):
    v %= q
    return v - q if v > q // 2 else v

def mul(p, r):  # mod x^420-1
    o = [0] * n
    for j, rj in enumerate(r):
        if rj:
            for i in range(n):
                o[(i + j) % n] += p[i] * rj
    return [x % q for x in o]

def polyhash(poly, msg):
    h = hashlib.sha256()
    for i in range(n):
        h.update(long_to_bytes(int(poly[i]) % q, 3))
    h.update(msg)
    return h.digest()

def hash2poly(h):
    hi = bytes_to_long(h)
    return [((1 << i) & hi != 0) for i in range(n)]

def encode(poly):
    return b"".join(long_to_bytes(int(poly[i]) % q, 3) for i in range(n))

def decode(bs):
    assert len(bs) == 3 * n
    return [bytes_to_long(bs[i:i+3]) for i in range(0, 3 * n, 3)]

def verify_full(msg, z1, z2, c, t, a):
    for z in (z1, z2):
        for i in range(n):
            if min(z[i] % q, q - z[i] % q) > b - w:
                return False
    u = [(mul(a, z1)[i] + z2[i] - mul(t, c)[i]) % q for i in range(n)]
    return hash2poly(polyhash(u, msg)) == c

def my_lll(rows, tag="x"):
    d = len(rows)
    fn = os.path.join(HERE, "_lat_%s_%d.in" % (tag, os.getpid()))
    with open(fn, "w") as f:
        f.write("%d\n" % d)
        for r in rows:
            f.write(" ".join(map(str, r)) + "\n")
    out = subprocess.check_output([os.path.join(HERE, "lll.exe"), fn], timeout=580).decode()
    os.remove(fn)
    return [list(map(int, l.split())) for l in out.split("\n") if l.strip()]

def component(a, t, sign, tag="x"):
    """fold by x^210 = sign; LLL (C) + Babai (fpylll fp64) -> (u, e_fold)."""
    from fpylll import IntegerMatrix, CVP
    d = n // 2
    af = [(a[k] + sign * a[k + d]) % q for k in range(d)]
    tf = [(t[k] + sign * t[k + d]) % q for k in range(d)]
    M = [[0] * d for _ in range(d)]
    for k in range(d):
        for mm in range(d):
            if k >= mm:
                M[k][mm] = centered(af[k - mm])
            else:
                M[k][mm] = centered(sign * af[d + k - mm])
    rows = []
    for k in range(d):
        r = [0] * (2 * d)
        r[k] = 1
        for r2 in range(d):
            r[d + r2] = M[r2][k]
        rows.append(r)
    for k in range(d):
        r = [0] * (2 * d)
        r[d + k] = q
        rows.append(r)
    red = my_lll(rows, tag)
    B = IntegerMatrix(len(red), len(red[0]))
    for i in range(len(red)):
        for j in range(len(red[0])):
            B[i, j] = red[i][j]
    target = [0] * d + [centered(x) for x in tf]
    with _BABAI_LOCK:
        v = CVP.babai(B, target)
    diff = [int(target[i]) - int(v[i]) for i in range(2 * d)]
    u = [centered(-x) for x in diff[:d]]
    ef = [centered(x) for x in diff[d:]]
    if max(map(abs, u)) > 2 or max(map(abs, ef)) > 2:
        raise RuntimeError("component Babai failed (sign=%d)" % sign)
    return u, ef

def recover_s(a, t):
    res = {}
    ths = [threading.Thread(target=lambda sgn=sgn, tag=tag: res.__setitem__(
        sgn, component(a, t, sgn, tag))) for sgn, tag in ((1, "p"), (-1, "m"))]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    u, _ = res[1]
    vv, _ = res[-1]
    s = [0] * n
    for k in range(n // 2):
        s[k] = (u[k] + vv[k]) // 2
        s[k + n // 2] = (u[k] - vv[k]) // 2
    if max(map(abs, s)) > 1 or any(u[k] + vv[k] != 2 * s[k] for k in range(n // 2)):
        raise RuntimeError("recovered s not ternary")
    e = [centered(t[i] - mul(a, s)[i]) for i in range(n)]
    if max(map(abs, e)) > 1:
        raise RuntimeError("derived e not ternary")
    return s, e

def forge(a, t):
    s, e = recover_s(a, t)
    zero = [0] * n
    c = hash2poly(polyhash(zero, MSG))
    return mul(s, c), mul(e, c), c, s, e

def selftest():
    ok_all = True
    for trial in range(2):
        a = [randrange(1, q) for _ in range(n)]
        s = [randrange(-1, 2) for _ in range(n)]
        e = [randrange(-1, 2) for _ in range(n)]
        t = [(mul(a, s)[i] + e[i]) % q for i in range(n)]
        z1, z2, c, s2, e2 = forge(a, t)
        ok = (s2 == s) and (e2 == e) and verify_full(MSG, z1, z2, c, t, a)
        print("trial", trial, "exact =", s2 == s and e2 == e, "verify =", ok, flush=True)
        ok_all = ok_all and ok
    return ok_all

if __name__ == "__main__":
    if "--local" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sock = socket.create_connection(("archive.cryptohack.org", 26931), timeout=60)
    f = sock.makefile("rwb")
    def readline():
        line = f.readline()
        if not line: raise EOFError("server closed")
        print("S:", line.decode().strip()[:120], flush=True)
        return line.decode()
    l1 = readline(); l2 = readline()
    a = decode(bytes.fromhex(l1.split("=")[1].strip()))
    t = decode(bytes.fromhex(l2.split("=")[1].strip()))
    z1, z2, c, s, e = forge(a, t)
    assert verify_full(MSG, z1, z2, c, t, a), "local verify failed"
    for z in (z1, z2, c):
        f.write(encode(z).hex().encode() + b"\n")
    f.flush()
    resp = readline()
    print("RESP:", resp, flush=True)
    f.close(); sock.close()

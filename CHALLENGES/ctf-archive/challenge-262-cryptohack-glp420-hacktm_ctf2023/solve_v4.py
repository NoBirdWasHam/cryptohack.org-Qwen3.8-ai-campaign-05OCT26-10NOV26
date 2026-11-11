# GLP420 (HackTM 2023) final solver — no fpylll; LLL+Babai via lll2.exe.
# Run: ~/tools/crypto-ctf/venv/Scripts/python.exe solve_v4.py [--live]
import sys, os, socket, hashlib, subprocess, threading
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

def llldiff(rows, target, tag):
    N = len(rows)
    fn = os.path.join(HERE, "_lat_%s.in" % tag)
    ft = os.path.join(HERE, "_tgt_%s.in" % tag)
    with open(fn, "w") as f:
        f.write("%d\n" % N)
        for r in rows:
            f.write(" ".join(map(str, r)) + "\n")
    with open(ft, "w") as f:
        f.write(" ".join(map(str, target)) + "\n")
    out = subprocess.check_output([os.path.join(HERE, "lll2.exe"), fn, ft], timeout=560).decode()
    return list(map(int, out.split()))

def component(a, t, sign, tag):
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
    target = [0] * d + [centered(x) for x in tf]
    diff = llldiff(rows, target, tag)
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
        if (u[k] + vv[k]) % 2 or (u[k] - vv[k]) % 2:
            raise RuntimeError("parity")
        s[k] = (u[k] + vv[k]) // 2
        s[k + n // 2] = (u[k] - vv[k]) // 2
    if max(map(abs, s)) > 1:
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

def live():
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
    return resp

if __name__ == "__main__":
    if "--live" in sys.argv:
        live()
    else:
        sys.exit(0 if selftest() else 1)

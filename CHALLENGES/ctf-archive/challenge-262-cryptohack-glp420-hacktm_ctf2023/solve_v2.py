# GLP420 (HackTM 2023) solver.
# Scheme: R = Z_q[x]/(x^420-1), t = a*s + e, s,e ternary. Given (a,t), forge on b"sign me!".
# Attack: CRT-split R via x^420-1 = prod_{zeta^4=1}(x^105 - zeta) over Z_q (q = 8383489 = 1 mod 4).
#   In each component the folded secret/err (4-term zeta-folded sums of ternary coeffs, entries
#   in [-4,4]) stays tiny: CVP lattice dim 210, det q^105, GH ~1.7e4, target norm ~24
#   => LLL + Babai is exact. Recover folded s in all 4 components, inverse DFT (CRT) -> s.
# Forgery: y1=y2=0 -> c = hash2poly(sha256(encode(0)||m)); z1 = s*c, z2 = e*c;
#   then a*z1 + z2 - t*c = 0, so verify's hash round-trips; |z| ~< 300 << 16380.
# Run: ~/tools/crypto-ctf/venv/Scripts/python.exe solve.py [--local]
import sys, socket, hashlib
from random import randrange
from Crypto.Util.number import bytes_to_long, long_to_bytes

q = 8383489
n = 420
m = 105
b = 16383
w = 3
MSG = b"sign me!"

def centered(v):
    v %= q
    return v - q if v > q // 2 else v

def mul(p, r, mod_zeta=1, deg=n):  # ring product mod x^deg - mod_zeta
    o = [0] * deg
    for j in range(deg):
        rj = r[j]
        if rj:
            for i in range(deg):
                if i + j < deg:
                    o[i + j] += p[i] * rj
                else:
                    o[i + j - deg] += p[i] * rj * mod_zeta
    return [x % q for x in o]

def polyhash(poly, msg, deg=n):
    h = hashlib.sha256()
    for i in range(deg):
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

def sqrt_mod(v, p):
    v %= p
    if pow(v, (p - 1) // 2, p) != 1:
        raise ValueError("non-residue")
    tt, rr = (p - 1), 0
    while tt % 2 == 0:
        tt //= 2; rr += 1
    zz = 2
    while pow(zz, (p - 1) // 2, p) != p - 1:
        zz += 1
    cc, x = pow(zz, tt, p), pow(v, (tt + 1) // 2, p)
    ex = pow(v, tt, p)
    while ex != 1:
        tt2, ee = ex, 0
        while tt2 != 1:
            tt2 = tt2 * tt2 % p; ee += 1
        bb = pow(cc, 1 << (rr - ee - 1), p)
        cc = bb * bb % p
        x = x * bb % p
        ex = ex * cc % p
        rr = rr - ee - 1
    return x

def component(a, t, sign):
    """fold a,t by x^210 = sign into Z_q[x]/(x^210 - sign); recover folded (u,v) via LLL+Babai."""
    from fpylll import IntegerMatrix, LLL, CVP
    d = n // 2  # 210
    af = [(a[k] + sign * a[k + d]) % q for k in range(d)]
    tf = [(t[k] + sign * t[k + d]) % q for k in range(d)]
    # M[k][mm] = mult-by-af mod x^d - sign
    M = [[0] * d for _ in range(d)]
    for k in range(d):
        for mm in range(d):
            if k >= mm:
                M[k][mm] = centered(af[k - mm])
            else:
                M[k][mm] = centered(sign * af[d + k - mm])
    # L = {(u,v) : v - M u in q Z^d}; basis rows (e_k | M[:,k]) and (0 | q e_k)
    Lm = IntegerMatrix(2 * d, 2 * d)
    for k in range(d):
        Lm[k, k] = 1
        for r2 in range(d):
            Lm[k, d + r2] = M[r2][k]
    for k in range(d):
        Lm[d + k, d + k] = q
    target = [0] * d + [centered(tf[k]) for k in range(d)]
    LLL.reduction(Lm, method="fast")
    v = CVP.babai(Lm, target)
    diff = [int(target[i]) - int(v[i]) for i in range(2 * d)]
    u = [centered(-x) for x in diff[:d]]
    ef = [centered(x) for x in diff[d:]]
    if max(map(abs, u)) > 2 or max(map(abs, ef)) > 2:
        raise RuntimeError("component Babai failed (sign=%d)" % sign)
    return u, ef

def recover_s(a, t):
    u, _ = component(a, t, 1)    # u_k = s_k + s_{k+210}
    vv, _ = component(a, t, -1)  # v_k = s_k - s_{k+210}
    s = [0] * n
    for k in range(n // 2):
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
    for trial in range(3):
        a = [randrange(1, q) for _ in range(n)]
        s = [randrange(-1, 2) for _ in range(n)]
        e = [randrange(-1, 2) for _ in range(n)]
        t = [(mul(a, s)[i] + e[i]) % q for i in range(n)]
        z1, z2, c, s2, e2 = forge(a, t)
        ok = (s2 == s) and (e2 == e) and verify_full(MSG, z1, z2, c, t, a)
        print("trial", trial, "exact-key =", s2 == s and e2 == e, "verify =", ok, flush=True)
        ok_all = ok_all and ok
    return ok_all

if __name__ == "__main__":
    if "--local" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sock = socket.create_connection(("archive.cryptohack.org", 26931), timeout=30)
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

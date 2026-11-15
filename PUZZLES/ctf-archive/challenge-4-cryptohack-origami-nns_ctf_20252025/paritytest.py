# End-to-end synthetic check mirroring source.sage EXACTLY (0/1 polys, same bit order),
# then decrypts via the 4-variant scan logic (same as patched solve7 try_vec).
import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
n, q = 512, 127

def cm(a, b):
    o = [0] * n
    nz = [(j, bj) for j, bj in enumerate(b) if bj]
    for i, ai in enumerate(a):
        if ai:
            for j, bj in nz:
                o[(i + j) % n] += ai * bj
    return o

def rp(d, rng):
    v = [0] * n
    for i in rng.sample(range(n), d):
        v[i] = 1
    return v

# ---- polynomial inverse of a mod (x^n-1) over Z_q via extended euclid ----
def polyinv(a, q):
    x_n_1 = [0] * (n + 1); x_n_1[0] = -1 % q; x_n_1[n] = 1
    def trim(p):
        p = p[:]
        while len(p) > 1 and p[-1] == 0: p.pop()
        return p
    def deg(p): return len(p) - 1
    t0, t1 = [0], a[:]
    r0, r1 = x_n_1[:], a[:]
    while any(r1):
        rr = r0[:]
        inv = pow(r1[-1], q - 2, q)
        quot = [0] * max(1, deg(rr) - deg(r1) + 1)
        while deg(rr) >= deg(r1) and any(rr):
            d = deg(rr) - deg(r1)
            c = rr[-1] * inv % q
            quot[d] = c
            for i in range(len(r1)):
                rr[d + i] = (rr[d + i] - c * r1[i]) % q
            rr = trim(rr)
        r0, r1 = r1, rr
        t = t0[:] + [0] * (len(t1) + len(quot))
        for i, c in enumerate(quot):
            if c:
                for j, tv in enumerate(t1):
                    t[i + j] = (t[i + j] - c * tv) % q
        t0, t1 = t1, trim(t)
    if deg(r0) != 0 or r0[0] % q != 1:
        return None
    return t1

def gf2_solve_unit(fbits, B):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c - i) % n] & 1: bits |= 1 << i
        rows.append([bits, B[c] & 1])
    piv = {}
    for r in rows:
        while r[0]:
            col = (r[0] & -r[0]).bit_length() - 1
            if col in piv:
                r[0] ^= piv[col][0]; r[1] ^= piv[col][1]
            else:
                piv[col] = r; break
        if not r[0] and r[1]:
            return None
    x = 0
    for col in range(n - 1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        val = t
        rest = bits & ~(1 << col)
        while rest:
            c = (rest & -rest).bit_length() - 1
            val ^= (x >> c) & 1
            rest &= rest - 1
        if val: x |= 1 << col
    return x

def try_f(fvec, gvec, ct):
    if sum(abs(c) for c in fvec) + 2 * sum(abs(c) for c in gvec) >= q: return None
    if sum(1 for c in fvec if c) % 2 == 0: return None
    A = [x % q for x in cm(fvec, ct)]
    B = [a & 1 for a in A]
    x = gf2_solve_unit([abs(c) & 1 for c in fvec], B)
    if x is None: return None
    return long_to_bytes(x)

rng = random.Random(12345)
flag = b"NNS{parity_test_round_trip_flag_for_decrypt_check!}"
assert len(flag) * 8 <= n
val = bytes_to_long(flag)
m = [(val >> i) & 1 for i in range(n)]
f = rp(35, rng); g = rp(35, rng); r = rp(22, rng)
h = polyinv(f, q)
assert h is not None, "f not a unit mod q"
h2 = cm(h, g)          # h2 = g/f
hr = cm(h2, r)
ct = [(2 * hr[i] + m[i]) % q for i in range(n)]
S = [2 * a + b for a, b in zip(cm(g, r), cm(f, m))]
print("max S coeff:", max(S), "(needs <127), min:", min(S))
A = [x % q for x in cm(f, ct)]
print("lift [0,q) == S exactly:", A == S)
for tag, fv, gv in (
    ("f,g", f, g),
    ("neg", [-c for c in f], [-c for c in g]),
    ("swap", g, f),
    ("swapneg", [-c for c in g], [-c for c in f]),
):
    out = try_f(fv, gv, ct)
    status = "MATCH" if out == flag else ("None" if out is None else "WRONG " + repr(out[:24]))
    print(tag, "->", status)

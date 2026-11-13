# Local replica of quo_vadis.sage protocol in pure Python (no Sage needed).
# Prints the same sage-style modulus strings; serves on 127.0.0.1:$QUO_PORT.
import os, sys, socket, secrets, random, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from quo_core import Tower, Nest, TField, prod

FLAG = os.environ.get("FLAG", "ECSC{local_sim_test_flag}")

class GF2:
    N = 1
    def ensure_tab(self): pass
    def mmul(self, a, b): return (a & b) & 1
    def mpow(self, x, e): return x
    def minv(self, x): return 1
    def frob(self, x): return x & 1
    def from_mask(self, m): return m & 1

def zero_struct(lvl):
    return 0 if lvl < 0 else tuple(zero_struct(lvl - 1) for _ in range(DS_CUR[lvl]))

DS_CUR = []

def is_one(c, lvl):
    if lvl < 0: return c == 1
    if c == 0: return False
    o = one_struct(lvl)
    return c == o

def one_struct(lvl):
    if lvl < 0: return 1
    return tuple(one_struct(lvl - 1) if i == 0 else zero_struct(lvl - 1) for i in range(DS_CUR[lvl]))

def is_zero(c, lvl):
    return c == 0 if lvl < 0 else all(is_zero(x, lvl - 1) for x in c)

def fmt(c, lvl, bar):
    """format element of level-lvl field (or GF2 at -1) sage-style."""
    if lvl < 0:
        return str(c & 1)
    v = f"b{lvl}" + ("bar" if bar else "")
    terms = []
    for d in range(len(c) - 1, -1, -1):
        cd = c[d]
        if is_zero(cd, lvl - 1):
            continue
        if d == 0:
            terms.append(fmt(cd, lvl - 1, True))
            continue
        if is_one(cd, lvl - 1):
            cs = ""
        else:
            s = fmt(cd, lvl - 1, True)
            if "+" in s:
                s = "(" + s + ")"
            cs = s + "*"
        terms.append(f"{cs}{v}" + (f"^{d}" if d > 1 else ""))
    return " + ".join(terms) if terms else "0"

def prime_factors(n):
    out, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            out.add(d); n //= d
        d += 1
    if n > 1: out.add(n)
    return out

def irr_test(F, d, Nl):
    """Rabin irreducibility of F=f[y] monic deg d over GF(2^{Nl})."""
    x = [0, 1]
    def xpow2(E):
        r = [0, 1]
        for _ in range(E):
            r = F.sqmod(r)
        return r
    for p in prime_factors(d):
        r = xpow2(Nl * d // p)
        r[1] ^= 1
        g = F.gcd(F.f, r)
        if len(F.trim(g)) - 1 > 0:
            return False
    r = xpow2(Nl * d)
    r[1] ^= 1
    return not F.trim(r)

def rand_struct(lvl, rng):
    if lvl < 0:
        return rng.randrange(2)
    return tuple(rand_struct(lvl - 1, rng) for _ in range(DS_CUR[lvl]))

def gen_irreducible(ds, lvl, rng):
    """random monic irreducible degree ds[lvl] over level-(lvl-1) field.
    Returns list of coefficient structs (len d+1, monic last)."""
    d = ds[lvl]
    while True:
        m = [rand_struct(lvl - 1, rng) for _ in range(d)] + [None]
        m[d] = tuple(one_struct(lvl - 1) if i == 0 else zero_struct(lvl - 1) for i in range(ds[lvl - 1])) if lvl > 0 else 1
        # build tower up to lvl to test
        tmods = []
        ok = True
        # need actual lower mods; pass in via closure below
        return m  # placeholder, real test done in build_ext

def build_ext_lines(k, ds, rng):
    """returns (lines, mods) like server's build_ext; prints lines."""
    DS_CUR[:] = ds
    mods = []
    lines = []
    for lvl in range(len(ds)):
        d = ds[lvl]
        while True:
            m = [rand_struct(lvl - 1, rng) for _ in range(d)] + [
                one_struct(lvl - 1) if lvl > 0 else 1
            ]
            if lvl == 0:
                tw = GF2()
            else:
                tw = Tower(ds[:lvl], mods[:lvl])
            fbits = [0 if is_zero(m[j], lvl - 1) else (
                tw.to_mask(m[j]) if lvl > 0 else 1) for j in range(d + 1)]
            F = TField(tw, fbits)
            if irr_test(F, d, prod(ds[:lvl]) if lvl > 0 else 1):
                break
        lines.append(fmt(m, lvl, False))
        mods.append(m)
    for L in lines:
        print(L, flush=True)
    return lines, mods

def gen_g(D, rng):
    while True:
        bits = rng.randrange(1 << D) | (1 << D) | 1
        gd = [(bits >> i) & 1 for i in range(D + 1)]
        tw = GF2()
        F = TField(tw, gd)
        if irr_test(F, D, 1):
            return gd

def tolist(el, lvl):
    if lvl < 0:
        return [el & 1]
    out = []
    for c in el:
        out.extend(tolist(c, lvl - 1))
    return out

def fromlist(xs, lvl):
    if lvl < 0:
        return next(xs) & 1
    return tuple(fromlist(xs, lvl - 1) for _ in range(DS_CUR[lvl]))

def serve(conn):
    f = conn.makefile("rw", buffering=1)
    def P(s): print(s, flush=True); f.write(str(s) + "\n")
    def R(): return f.readline().strip()
    K = []
    CHALS = [(2, [2, 3]), (8, [2, 3]), (8, [2, 3, 5]), (32, [3, 4, 5]), (64, [4, 3, 5])]
    rng = random.Random()
    for (k, ds) in CHALS:
        global DS_CUR
        DS_CUR[:] = ds
        D = prod(ds)
        p = 2 ** k
        lines, mods = build_ext_lines(k, ds, rng)
        for L in lines:
            f.write(L + "\n")
        f.flush()
        gd = gen_g(D, rng)
        print(fmt(gd, 0, False), flush=True)
        f.write(fmt(gd, 0, False) + "\n"); f.flush()
        N1 = Nest(ds, mods, p)
        L = len(ds) - 1
        pt1 = tuple(rand_struct_bits(k, ds, rng) for _ in range(0))  # placeholder
        # random element of R1: ints mod p flattened -> nest
        flat = [secrets.randbelow(p) for _ in range(D)]
        def rec(flat, lvl):
            if lvl < 0: return flat[0] % p
            blk = prod(ds[:lvl])
            return tuple(rec(flat[i * blk:(i + 1) * blk], lvl - 1) for i in range(ds[lvl]))
        pt1 = rec(flat, L)
        P(",".join(map(str, N1.flatten(pt1))))
        poly = [secrets.randbelow(3) - 1 for _ in range(1024)]
        N2 = Nest([D], [gd], p)
        xs = iter(int(t) for t in R().split(","))
        pt2 = tuple(next(xs) % p for _ in range(D))
        v2 = N2.eval_int_poly(pt2, poly)
        P(",".join(map(str, N2.flatten(v2))))
        v1 = N1.eval_int_poly(pt1, poly)
        K.extend(N1.flatten(v1))
    cipher = AES.new(hashlib.sha256("||".join(map(str, K)).encode()).digest(), AES.MODE_CBC)
    P(cipher.iv.hex() + " " + cipher.encrypt(pad(FLAG.encode(), AES.block_size)).hex())
    f.close(); conn.close()

if __name__ == "__main__":
    port = int(os.environ.get("QUO_PORT", "23999"))
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(1)
    sys.stderr.write(f"sim listening on {port}\n"); sys.stderr.flush()
    conn, _ = s.accept()
    serve(conn)

# quo_vadis core: parse Sage GF-tower moduli, GF(2^D) tower (bitmask), Nest rings over Z/2^k,
# CZ root finding via absolute F2-trace, Hensel, linear algebra over Z/2^k.
import re, random

def prod(xs):
    r = 1
    for x in xs: r *= x
    return r

# ---------------- parsing Sage GF-tower poly strings ----------------
def split_top(s, sep):
    parts, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == sep and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip() != '']

def parse_poly_str(s, lvl, bar):
    """dict deg->coeff; coeff int(0/1) at lvl==0 else nested dict.
    Terms not containing the current variable are all parts of the constant
    coefficient (sage prints compound constant coeffs flat, e.g. 'b1 + b0bar + 1')."""
    d = {}
    s = s.strip()
    if not s: return d
    vname = f'b{lvl}' + ('bar' if bar else '')
    pat = re.compile(re.escape(vname) + r'(?:\^(\d+))?')
    zero_terms = []
    for term in split_top(s, '+'):
        deg = None; cstrs = []
        for f in split_top(term, '*'):
            f = f.strip()
            m = pat.fullmatch(f)
            if m and deg is None: deg = int(m.group(1) or 1)
            else: cstrs.append(f)
        if deg is None:
            zero_terms.append(term.strip())
            continue
        if not cstrs:
            c = 1
        elif lvl == 0:
            assert all(cs == '1' for cs in cstrs), term
            c = 1
        else:
            cs = '*'.join(cstrs)
            if cs.startswith('(') and cs.endswith(')'):
                cs = cs[1:-1]
            c = parse_poly_str(cs, lvl - 1, True)
        assert deg not in d
        d[deg] = c
    if zero_terms:
        if lvl == 0:
            if sum(1 for t in zero_terms if t) % 2:
                assert 0 not in d
                d[0] = 1
        else:
            d[0] = parse_poly_str(' + '.join(zero_terms), lvl - 1, True)
    return d

def coeff_struct(c, level, ds):
    """element of ring at 'level' as nested tuples of bits; level==-1 -> int."""
    if level < 0:
        return int(c) & 1
    if isinstance(c, int):
        c = {0: c} if c else {}
    return tuple(coeff_struct(c.get(i, 0), level - 1, ds) for i in range(ds[level]))

def modulus_from_line(line, lvl, ds):
    d = parse_poly_str(line, lvl, False)
    return [coeff_struct(d.get(i, 0), lvl - 1, ds) for i in range(ds[lvl] + 1)]

# ---------------- GF(2) tower, bitmask elements ----------------
class Tower:
    def __init__(self, ds, mods):
        self.ds = list(ds); self.L = len(ds); self.N = prod(ds)
        self.mods = [tuple(m[i] for i in range(ds[l] + 1)) for l, m in enumerate(mods)]
        self._z = {}; self._o = {}; self.tab = None

    def zero(self, lvl):
        if lvl < 0: return 0
        if lvl not in self._z:
            self._z[lvl] = tuple(self.zero(lvl - 1) for _ in range(self.ds[lvl]))
        return self._z[lvl]

    def one(self, lvl):
        if lvl < 0: return 1
        if lvl not in self._o:
            self._o[lvl] = tuple(self.one(lvl - 1) if i == 0 else self.zero(lvl - 1)
                                 for i in range(self.ds[lvl]))
        return self._o[lvl]

    def add(self, x, y, lvl):
        if lvl < 0: return x ^ y
        return tuple(self.add(x[i], y[i], lvl - 1) for i in range(self.ds[lvl]))

    def mul(self, x, y, lvl):
        if lvl < 0: return x & y
        z = self.zero(lvl)
        if x == z or y == z: return z
        d = self.ds[lvl]; mod = self.mods[lvl]; zl = self.zero(lvl - 1)
        full = [zl] * (2 * d - 1)
        for i in range(d):
            if x[i] == zl: continue
            for j in range(d):
                if y[j] == zl: continue
                full[i + j] = self.add(full[i + j], self.mul(x[i], y[j], lvl - 1), lvl - 1)
        for t in range(2 * d - 2, d - 1, -1):
            c = full[t]
            if c == zl: continue
            for j in range(d):
                mj = mod[j]
                if mj == zl: continue
                full[t - d + j] = self.add(full[t - d + j], self.mul(c, mj, lvl - 1), lvl - 1)
        return tuple(full[:d])

    def pow(self, x, e, lvl=None):
        lvl = self.L - 1 if lvl is None else lvl
        r = self.one(lvl); b = x
        while e:
            if e & 1: r = self.mul(r, b, lvl)
            b = self.mul(b, b, lvl); e >>= 1
        return r

    def gen_at(self, lvl):
        return tuple(self.zero(lvl - 1) if i != 1 else self.one(lvl - 1)
                     for i in range(self.ds[lvl]))

    def flatten(self, el, lvl=None):
        lvl = self.L - 1 if lvl is None else lvl
        if lvl == 0:
            return [int(b) & 1 for b in el]
        out = []
        for c in el:
            out.extend(self.flatten(c, lvl - 1))
        return out

    def to_mask(self, el):
        m = 0
        for i, b in enumerate(self.flatten(el)):
            if b: m |= 1 << i
        return m

    def from_mask(self, m):
        return self._fm(m, self.L - 1)

    def _fm(self, m, lvl):
        if lvl == 0:
            return tuple((m >> i) & 1 for i in range(self.ds[0]))
        block = prod(self.ds[:lvl])
        return tuple(self._fm((m >> (i * block)) & ((1 << block) - 1), lvl - 1)
                     for i in range(self.ds[lvl]))

    # bitmask (top-level field) arithmetic -- structure constants, O(D^2) build
    def ensure_tab(self):
        if self.tab is not None: return
        n = self.N
        basis = [self._fm(1 << i, self.L - 1) for i in range(n)]
        M = [[self.to_mask(self.mul(basis[i], basis[j], self.L - 1)) for j in range(n)]
             for i in range(n)]
        self.tab = M                      # tab[i][j] = mask of e_i*e_j
        nbytes = (n + 7) // 8
        TBL = []
        for i in range(n):
            Mi = M[i]; Ti = []
            for t in range(nbytes):
                tt = [0] * 256
                for m in range(1, 256):
                    lb = m & -m
                    bit = lb.bit_length() - 1
                    prev = tt[m ^ lb]
                    idx = 8 * t + bit
                    tt[m] = prev ^ (Mi[idx] if idx < n else 0)
                Ti.append(tt)
            TBL.append(Ti)
        self.TBL = TBL
        S = [M[i][i] for i in range(n)]   # Frobenius squaring masks
        ST = []
        for t in range(nbytes):
            tt = [0] * 256
            for m in range(1, 256):
                lb = m & -m
                bit = lb.bit_length() - 1
                idx = 8 * t + bit
                tt[m] = tt[m ^ lb] ^ (S[idx] if idx < n else 0)
            ST.append(tt)
        self.ST = ST

    def mmul(self, a, b):
        self.ensure_tab()
        T_ = self.TBL
        if not a or not b: return 0
        res = 0; i = 0; A = a
        while A:
            if A & 1:
                Ti = T_[i]; t = 0; B = b
                while B:
                    res ^= Ti[t][B & 0xFF]
                    B >>= 8; t += 1
            A >>= 1; i += 1
        return res

    def mpow(self, x, e):
        r = 1; b = x
        while e:
            if e & 1: r = self.mmul(r, b)
            b = self.mmul(b, b); e >>= 1
        return r

    def minv(self, x):
        return self.mpow(x, (1 << self.N) - 2)

    def frob(self, m):
        self.ensure_tab()
        if not m: return 0
        res = 0; t = 0; ST = self.ST
        while m:
            res ^= ST[t][m & 0xFF]
            m >>= 8; t += 1
        return res

# ---------------- T[x] mod monic f ----------------
class TField:
    def __init__(self, tw, f):
        self.tw = tw
        self.f = self.trim(f)
        self.n = len(self.f) - 1
        self.RED = self._build_red()

    def trim(self, p):
        p = list(p)
        while p and p[-1] == 0: p.pop()
        return p

    def _build_red(self):
        n = self.n
        RED = [self.f[:n][:]]           # x^n mod f
        for t in range(1, n):
            prev = RED[t - 1]
            cur = ([0] + prev)[:n] + [0] * max(0, n - len(prev) - 1)
            cur = ([0] + prev[:n])
            cur = cur[:n]
            # above shift keeps degree < n automatically? x*prev has deg <= n-1+1 = n
            c = ([0] + prev)[n] if len([0] + prev) > n else 0
            cur = ([0] + prev)[:n]
            if c:
                for j in range(n):
                    if self.f[j]:
                        cur[j] ^= self.tw.mmul(c, self.f[j])
            RED.append(cur)
        return RED

    def mulmod(self, p, q):
        n = self.n
        full = [0] * (2 * n)
        for i, a in enumerate(p):
            if not a: continue
            for j, b in enumerate(q):
                if b: full[i + j] ^= self.tw.mmul(a, b)
        for t in range(2 * n - 2, n - 1, -1):
            c = full[t]
            if not c: continue
            red = self.RED[t - n]
            for j in range(n):
                if red[j]: full[j] ^= self.tw.mmul(c, red[j])
        return full[:n]

    def sqmod(self, p):
        n = self.n
        out = [0] * n
        for i, a in enumerate(p):
            if not a: continue
            fa = self.tw.frob(a)
            if 2 * i < n:
                out[2 * i] ^= fa
            else:
                red = self.RED[2 * i - n]
                for j in range(n):
                    if red[j]: out[j] ^= self.tw.mmul(fa, red[j])
        return out

    def addp(self, p, q):
        n = max(len(p), len(q))
        out = [0] * n
        for i in range(n):
            a = p[i] if i < len(p) else 0
            b = q[i] if i < len(q) else 0
            out[i] = a ^ b
        return out

    def scale(self, p, c):
        return [self.tw.mmul(a, c) if a else 0 for a in p]

    def evalp(self, p, x):
        r = 0
        for a in reversed(p):
            r = self.tw.mmul(r, x) ^ a
        return r

    def monic(self, p):
        p = self.trim(p)
        if not p: return []
        return self.scale(p, self.tw.minv(p[-1]))

    def pmod(self, p, gn):
        p = list(self.trim(p)); m = len(gn) - 1
        if m == 0: return []
        while p and len(p) - 1 >= m:
            c = p[-1]
            if c:
                for j in range(m + 1):
                    p[len(p) - 1 - m + j] ^= self.tw.mmul(c, gn[j])
            p.pop()
            while p and p[-1] == 0: p.pop()
        return p

    def div_exact(self, p, g):
        g = self.monic(g)
        p = list(self.trim(p)); m = len(g) - 1
        q = [0] * max(1, len(p) - m)
        while p and len(p) - 1 >= m:
            c = p[-1]
            if c:
                q[len(p) - 1 - m] ^= c
                for j in range(m + 1):
                    p[len(p) - 1 - m + j] ^= self.tw.mmul(c, g[j])
            p.pop()
            while p and p[-1] == 0: p.pop()
        assert not p, "division not exact"
        return self.trim(q) if self.trim(q) else [0]

    def gcd(self, f, g):
        g = self.monic(self.trim(g))
        while g:
            r = self.pmod(f, g)
            f, g = g, self.monic(r) if r else []
        return self.monic(self.trim(f)) if self.trim(f) else []

def cz_roots(gbits, tw, rng=None):
    rng = rng or random.Random(0xC0FFEE)
    n = gbits.bit_length() - 1
    f = [(gbits >> i) & 1 for i in range(n + 1)]
    F = TField(tw, f)

    def split(poly):
        poly = F.monic(poly)
        deg = len(poly) - 1
        if deg == 1:
            return [poly[0]]
        tries = 0
        while True:
            tries += 1
            assert tries < 200, "CZ stuck"
            a = [rng.getrandbits(tw.N) for _ in range(deg)]
            b = list(a); cur = list(a)
            for _ in range(tw.N - 1):
                cur = F.sqmod(cur)
                b = F.addp(b, cur)
            gg = F.gcd(poly, F.trim(b))
            dg = len(gg) - 1
            if 0 < dg < deg:
                break
        other = F.div_exact(poly, gg)
        return split(gg) + split(other)

    return split(f)

def cz_one_root(gbits, tw, rng=None):
    """CZ splitting with early exit: return bitmask of ONE root of gbar in the tower."""
    rng = rng or random.Random(0xC0FFEE)
    n = gbits.bit_length() - 1
    f = [(gbits >> i) & 1 for i in range(n + 1)]
    F = TField(tw, f)

    def one(poly):
        poly = F.monic(poly)
        deg = len(poly) - 1
        if deg == 1:
            return poly[0]
        tries = 0
        while True:
            tries += 1
            assert tries < 500, "CZ stuck"
            a = [rng.getrandbits(tw.N) for _ in range(deg)]
            b = list(a); cur = list(a)
            for _ in range(tw.N - 1):
                cur = F.sqmod(cur)
                b = F.addp(b, cur)
            gg = F.gcd(poly, F.trim(b))
            dg = len(gg) - 1
            if 0 < dg < deg:
                return gg[0] if dg == 1 else one(gg)
    return one(f)

# ---------------- Nest ring over Z/p ----------------
class Nest:
    def __init__(self, ds, mods, p):
        self.ds = list(ds); self.L = len(ds); self.p = p
        self.mods = [tuple(m) for m in mods]
        self._z = {}; self._o = {}

    def zero(self, lvl):
        if lvl < 0: return 0
        if lvl not in self._z:
            self._z[lvl] = tuple(self.zero(lvl - 1) for _ in range(self.ds[lvl]))
        return self._z[lvl]

    def one(self, lvl):
        if lvl < 0: return 1
        if lvl not in self._o:
            self._o[lvl] = tuple(self.one(lvl - 1) if i == 0 else self.zero(lvl - 1)
                                 for i in range(self.ds[lvl]))
        return self._o[lvl]

    def add(self, x, y, lvl):
        if lvl < 0: return (x + y) % self.p
        return tuple(self.add(x[i], y[i], lvl - 1) for i in range(self.ds[lvl]))

    def sub(self, x, y, lvl):
        if lvl < 0: return (x - y) % self.p
        return tuple(self.sub(x[i], y[i], lvl - 1) for i in range(self.ds[lvl]))

    def mul(self, x, y, lvl):
        if lvl < 0: return (x * y) % self.p
        z = self.zero(lvl)
        if x == z or y == z: return z
        d = self.ds[lvl]; mod = self.mods[lvl]; zl = self.zero(lvl - 1)
        full = [zl] * (2 * d - 1)
        for i in range(d):
            if x[i] == zl: continue
            for j in range(d):
                if y[j] == zl: continue
                full[i + j] = self.add(full[i + j], self.mul(x[i], y[j], lvl - 1), lvl - 1)
        for t in range(2 * d - 2, d - 1, -1):
            c = full[t]
            if c == zl: continue
            for j in range(d):
                mj = mod[j]
                if mj == zl: continue
                full[t - d + j] = self.sub(full[t - d + j], self.mul(c, mj, lvl - 1), lvl - 1)
        return tuple(full[:d])

    def scale(self, x, n, lvl):
        n %= self.p
        if lvl < 0: return (x * n) % self.p
        return tuple(self.scale(xi, n, lvl - 1) for xi in x)

    def eval_int_poly(self, theta, coeffs):
        L = self.L - 1
        r = self.zero(L)
        for c in reversed(coeffs):
            r = self.mul(r, theta, L)
            if c:
                r = self.add(r, self.scale(self.one(L), c, L), L)
        return r

    def flatten(self, el, lvl=None):
        lvl = self.L - 1 if lvl is None else lvl
        if lvl == 0:
            return [int(x) % self.p for x in el]
        out = []
        for c in el:
            out.extend(self.flatten(c, lvl - 1))
        return out

def solve_mod2k(cols, b, p):
    n = len(b)
    A = [[cols[c][r] % p for c in range(n)] for r in range(n)]
    bb = [v % p for v in b]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if A[r][col] & 1:
                piv = r; break
        assert piv is not None, "no odd pivot"
        A[col], A[piv] = A[piv], A[col]
        bb[col], bb[piv] = bb[piv], bb[col]
        invp = pow(A[col][col], -1, p)
        Ac = A[col]
        for r in range(n):
            if r == col or not A[r][col]: continue
            Ar = A[r]
            f = A[r][col] * invp % p
            for j in range(col, n):
                if Ac[j]:
                    Ar[j] = (Ar[j] - f * Ac[j]) % p
            bb[r] = (bb[r] - f * bb[col]) % p
    return [(bb[r] * pow(A[r][r], -1, p)) % p for r in range(n)]

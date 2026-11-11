# Attack for rsa_secret_sharing-wacon2022 (CryptoHack archive).
# Method (re-derived from the scheme math; recipe outline from author's blog,
# textbook-style reference allowed per AAR):
#   * we control stream1: choose a=x=b=1 -> LCG1_j = j (roll indices leak through
#     n mod q = u*v, factoring small ints gives roll positions T of all 8 primes).
#   * per n_i (indices u,v):  n == (L2_u q + u)(L2_v q + v)  (mod q^2)
#         -> v*L2_u + u*L2_v == (n - u*v)/q  (mod q)
#     with L2_j = C*g^j + D (g=a2): vector (C,D,-1) orthogonal to
#     (v g^u + u g^v, u+v, R_i) in F_q^3.  Four n -> any 3x3 det = 0 ->
#     sparse polys in g; gcd + roots -> g; 2x2 solve -> (C,D). Verify via q^2.
#   * n' = (n - (L2_u q+u)(L2_v q+v))/q^2 exact;  L3_u v + L3_v u == n' (mod q)
#     -> identical det trick -> L3 values. Then all 8 primes known exactly.
# No Coppersmith needed.
import random

# ---------- dense poly over F_q (lists low->high) ----------
def p_strip(p):
    while p and p[-1] == 0:
        p.pop()
    return p

def p_deg(p):
    return len(p) - 1

def p_mod(f, g, q):
    """f mod g over F_q, g non-zero."""
    r = f[:]
    dg = len(g) - 1
    linv = pow(g[-1], q - 2, q)
    gg = [c * linv % q for c in g]
    i = len(r) - 1
    while i >= dg:
        c = r[i]
        if c:
            j = i - dg
            rr = r
            sec = rr[j:j + dg]
            ggh = gg
            rr[j:j + dg] = [(x - c * y) % q for x, y in zip(sec, ggh)]
            r[i] = 0
        i -= 1
    return p_strip(r[:dg]) if dg > 0 else []

def p_gcd(f, g, q, stop_deg=40):
    """Euclid over F_q; early exit once remainder degree small, then
    completes -- returns the true gcd either way."""
    r0, r1 = f[:], g[:]
    if r0 == []:
        r0, r1 = r1, r0
    if r1 == []:
        return p_strip(r0)
    while r1 and len(r1) - 1 > stop_deg:
        r0, r1 = r1, p_mod(r0, r1, q)
    while r1:
        r0, r1 = r1, p_mod(r0, r1, q)
    c = pow(r0[-1], q - 2, q)
    return [x * c % q for x in r0]

def poly_from_terms(terms, q):
    """terms: dict exp->coeff -> dense list."""
    if not terms:
        return []
    d = max(terms)
    p = [0] * (d + 1)
    for e, c in terms.items():
        p[e] = (p[e] + c) % q
    return p_strip(p)

def eval_poly(p, x, q):
    r = 0
    for c in reversed(p):
        r = (r * x + c) % q
    return r

def p_mulmod(a, b, m, q):
    """(a*b) mod m over F_q."""
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    r[i + j] = (r[i + j] + ai * bj) % q
    return p_mod(r, m, q)

def p_powmod(base, e, m, q):
    res = [1]
    b = base[:]
    while e:
        if e & 1:
            res = p_mulmod(res, b, m, q)
        b = p_mulmod(b, b, m, q)
        e >>= 1
    return res

def p_derive(p, q):
    out = []
    for i in range(1, len(p)):
        out.append((i * p[i]) % q)
    return p_strip(out)

def p_divexact(f, g, q):
    """Exact polynomial division f/g over F_q (assumes g | f)."""
    f = f[:]
    g = g[:]
    p_strip(f)
    p_strip(g)
    if g == []:
        raise ZeroDivisionError("div by zero poly")
    df, dg = len(f) - 1, len(g) - 1
    if df < dg:
        return []
    ginv = pow(g[-1], q - 2, q)
    r = f[:]
    Q = [0] * (df - dg + 1)
    for i in range(df, dg - 1, -1):
        c = r[i] * ginv % q
        Q[i - dg] = c
        if c:
            base = i - dg
            for k in range(dg + 1):
                r[base + k] = (r[base + k] - c * g[k]) % q
    return p_strip(Q)

# ---------- fast polynomial arithmetic over F_q ----------
def _pad_add(x, y):
    if len(x) < len(y):
        x, y = y, x
    r = x[:]
    for i in range(len(y)):
        r[i] += y[i]
    return r

def m_mul(a, b):
    """Full product over Z (no reduction), Karatsuba."""
    n, m2 = len(a), len(b)
    if n == 0 or m2 == 0:
        return []
    if n < m2:
        a, b, n, m2 = b, a, m2, n
    if m2 <= 40:
        r = [0] * (n + m2 - 1)
        for i in range(n):
            ai = a[i]
            if ai:
                for j in range(m2):
                    r[i + j] += ai * b[j]
        return r
    mid = (n + 1) // 2
    a0, a1 = a[:mid], a[mid:]
    b0, b1 = b[:mid], b[mid:]
    z0 = m_mul(a0, b0)
    z2 = m_mul(a1, b1) if b1 else []
    z1 = m_mul(_pad_add(a0, a1), _pad_add(b0, b1))
    for i in range(len(z0)):
        z1[i] -= z0[i]
    for i in range(len(z2)):
        z1[i] -= z2[i]
    r = [0] * max(len(z0), mid + len(z1), 2 * mid + len(z2), n + m2 - 1)
    for i in range(len(z0)):
        r[i] = z0[i]
    for i in range(len(z1)):
        r[mid + i] += z1[i]
    for i in range(len(z2)):
        r[2 * mid + i] += z2[i]
    return r[: n + m2 - 1]

def m_mul_trunc(a, b, k):
    """Low k coeffs of a*b (Karatsuba-aware, safe via full mul slice)."""
    if not a or not b:
        return []
    a = a[:k]
    b = b[:k]
    return m_mul(a, b)[:k]

class Reducer:
    """Fast mod-m over F_q with cached reversed inverse."""
    def __init__(self, m, q):
        self.m = [c % q for c in m]
        self.q = q
        self.dg = len(m) - 1
        # monic normalize
        self.minv_lc = pow(self.m[-1], q - 2, q)
        self.m = [c * self.minv_lc % q for c in self.m]
        # rev(m) monic-low: m_rev = reversed coeffs
        self.mrev = list(reversed(self.m))  # low coeff = leading (1 after monic)
        self._inv = [pow(self.mrev[0], q - 2, q)]
        self._pow = 0
    def inv_mrev(self, k):
        # inverse of self.mrev mod x^k, Newton doubling
        q = self.q
        u = self._inv
        cur = 1
        while cur < k:
            nxt = min(2 * cur, k)
            # u = u*(2 - mrev*u) mod x^nxt
            t = m_mul_trunc(self.mrev, u, nxt)
            t = [-x for x in t]
            t[0] = (t[0] + 2) % q
            u = [x % q for x in m_mul_trunc(u, t, nxt)]
            cur = nxt
        self._inv = u
        return u
    def rem(self, r):
        """r mod self.m over F_q, deg r < 2*dg expected."""
        q = self.q
        r = [x % q for x in r]
        p_strip(r)
        n = len(r) - 1
        if n < self.dg:
            return r
        d = n - self.dg
        inv = self.inv_mrev(d + 1)
        rrev = list(reversed(r))
        Q = m_mul_trunc(rrev, inv, d + 1)
        # Q is rev(quotient): reverse back to low->high order
        Q = list(reversed(Q))
        # remainder = r - Q*m, keep low dg coeffs
        qm = m_mul(Q, self.m)
        out = []
        for i in range(self.dg):
            out.append((r[i] - (qm[i] if i < len(qm) else 0)) % q)
        p_strip(out)
        if len(out) - 1 >= self.dg:
            return self.rem(out)
        return out

def p_powmod_fast(base, e, m, q, red=None):
    red = red or Reducer(m, q)
    res = [1]
    b = [x % q for x in base]
    red_rem = red.rem
    mm = m_mul
    while e:
        if e & 1:
            res = red_rem(mm(res, b))
        e >>= 1
        if e:
            b = red_rem(mm(b, b))
    return res

def roots_general(p, q):
    """All roots in F_q of poly p (low->high). Always intersect with X^q - X
    first (fast powmod for big degree), then CZ with self-check/retry."""
    p = p_strip(p[:])
    if len(p) < 2:
        return []
    if len(p) - 1 > 40:
        xq = p_powmod_fast([0, 1], q, p, q)
    else:
        xq = p_powmod([0, 1], q, p, q)
    # X^q - X: subtract X (coeff of x^1), not the constant term
    while len(xq) < 2:
        xq.append(0)
    xq[1] = (xq[1] - 1) % q
    p_strip(xq)
    p = p_gcd(p, xq, q, stop_deg=10**9)
    p = p_strip(p[:])
    if len(p) < 2:
        return []
    s = len(p) - 1  # p now splits into s distinct linear factors over F_q
    for sd in range(1, 6):
        rts = _roots_cz(p, q, seed=1337 * sd)
        if len(rts) == s:
            return sorted(set(rts))
    return sorted(set(rts))

def _roots_cz(p, q, seed=1337):
    import random as _random
    rng = _random.Random(seed)
    p = p_strip(p[:])
    if len(p) < 2:
        return []
    roots = []
    hp = p_derive(p, q)
    if hp:
        g = p_gcd(p, hp, q, stop_deg=10**9)
        if len(g) > 1:
            p = p_divexact(p, g, q)
    p = p_strip(p[:])
    if len(p) < 2:
        return []
    linv = pow(p[-1], q - 2, q)
    p = [x * linv % q for x in p]
    stack = [p]
    while stack:
        f = p_strip(stack.pop()[:])
        d = len(f) - 1
        if d <= 0:
            continue
        if d == 1:
            roots.append((-f[0]) % q)
            continue
        if d == 2:
            roots += roots_small_poly(f, q)
            continue
        split = False
        for _ in range(100):
            r = p_strip([rng.randrange(q) for _ in range(d)])
            if len(r) < 1:
                continue
            z = p_powmod(r, (q - 1) // 2, f, q)
            z0 = z[:]
            z0[0] = (z0[0] - 1) % q
            p_strip(z0)
            g = p_strip(p_gcd(f, z0, q, stop_deg=10**9)[:])
            if 0 < len(g) - 1 < d:
                stack.append(g)
                stack.append(p_divexact(f, g, q))
                split = True
                break
    return sorted(set(roots))

def roots_small_poly(p, q):
    """roots of poly deg<=2 over F_q (linear/quadratic direct)."""
    p = p_strip(p[:])
    d = len(p) - 1
    if d <= 0:
        return []
    if d == 1:
        return [(-p[0] * pow(p[1], q - 2, q)) % q]
    if d == 2:
        A, B, C = p[2], p[1], p[0]  # A x^2 + B x + C
        disc = (B * B - 4 * A * C) % q
        s = tonelli(disc, q)
        if s is None:
            return []
        inv = pow(2 * A, q - 2, q)
        return sorted({((-B + s) * inv) % q, ((-B - s) * inv) % q})
    return roots_general(p, q)

def tonelli(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, b * b % p, t * b * b % p, R * b % p
    return min(R, p - R)

# ---------- index recovery ----------
def find_indices(n, q, hi=30000):
    """n mod q = u*v exactly (u<v, both <= hi). Return list of (u,v)."""
    r = n % q
    out = []
    u = 1
    while u * u <= r and u <= hi:
        if r % u == 0:
            v = r // u
            if u < v <= hi:
                out.append((u, v))
        u += 1
    return out

# ---------- LCG recovery from 4 pair-equations ----------
def recover_stream(pairs, l1, Rlist, q):
    """For each i: unknown stream S_j = C*g^j + D satisfies
       R_i = l1v*S_u + l1u*S_v = C*(l1v g^u + l1u g^v) + D*(l1u+l1v).
       pairs: [(u,v)], l1: dict j->value, Rlist: [R_i].
       yields candidates (a, C, D) verified on all equations."""
    P = []  # sparse term dicts per eq: exp -> coeff
    Qs, Rs = [], []
    for (u, v), R in zip(pairs, Rlist):
        l1u, l1v = l1[u], l1[v]
        terms = {}
        terms[u] = (terms.get(u, 0) + l1v) % q
        terms[v] = (terms.get(v, 0) + l1u) % q
        P.append(terms)
        Qs.append((l1u + l1v) % q)
        Rs.append(R % q)

    def det3(i, j, k):
        # c_i P_i + c_j P_j + c_k P_k with cofactors from Q,R
        ci = (Qs[j] * Rs[k] - Qs[k] * Rs[j]) % q
        cj = -(Qs[i] * Rs[k] - Qs[k] * Rs[i]) % q
        ck = (Qs[i] * Rs[j] - Qs[j] * Rs[i]) % q
        terms = {}
        for idx, c in ((i, ci), (j, cj), (k, ck)):
            if c == 0:
                continue
            for e, cc in P[idx].items():
                terms[e] = (terms.get(e, 0) + c * cc) % q
        return poly_from_terms(terms, q)

    d1 = det3(0, 1, 2)
    d2 = det3(0, 1, 3)
    h = p_gcd(d1, d2, q)
    for tri in ((0, 2, 3), (1, 2, 3)):
        if len(h) < 2:
            break
        h = p_gcd(h, det3(*tri), q)
    cands = roots_general(h, q)
    sols = []
    for g in cands:
        if not (1 <= g < q):
            continue
        # solve for C,D using two independent equations
        found = None
        for i in range(4):
            for j in range(i + 1, 4):
                Pi = eval_poly(poly_from_terms(P[i], q), g, q)
                Pj = eval_poly(poly_from_terms(P[j], q), g, q)
                det = (Pi * Qs[j] - Pj * Qs[i]) % q
                if det == 0:
                    continue
                C = (Rs[i] * Qs[j] - Rs[j] * Qs[i]) * pow(det, q - 2, q) % q
                D = (Pi * Rs[j] - Pj * Rs[i]) % q * pow(det, q - 2, q) % q
                ok = all((C * eval_poly(poly_from_terms(P[t], q), g, q) + D * Qs[t] - Rs[t]) % q == 0 for t in range(4))
                if ok:
                    found = (g, C, D)
                    break
            if found:
                break
        if found:
            sols.append(found)
    return sols

# ---------- top level ----------
def solve_instance(q, ns, verbose=True):
    """q prime, ns = [n1..n4]. Stream1 = identity (we sent 1,1,1).
       Returns (primes list, pairs) or None."""
    # 1) indices
    import itertools
    cand_list = [find_indices(n, q) for n in ns]
    if any(len(c) == 0 for c in cand_list):
        if verbose: print("no index pair found for an n")
        return None
    combos = []
    for combo in itertools.product(*cand_list):
        Tc = [x for pr in combo for x in pr]
        if len(set(Tc)) == 8 and sorted(Tc) == Tc:
            combos.append(list(combo))
    if verbose: print("index combos:", len(combos))
    for pairs in combos:
        out = _solve_with_pairs(q, ns, pairs, verbose)
        if out:
            return out
    if verbose: print("no combo solved")
    return None

def _solve_with_pairs(q, ns, pairs, verbose=True):
    T = [x for pr in pairs for x in pr]
    if verbose: print("roll indices:", pairs)
    l1 = {}
    for (u, v) in pairs:
        l1[u] = u % q
        l1[v] = v % q
    # 2) LCG2
    R2 = [((n - l1[u] * l1[v]) // q) % q for n, (u, v) in zip(ns, pairs)]
    sols2 = recover_stream(pairs, l1, R2, q)
    if not sols2:
        if verbose: print("no consistent a2")
        return None
    for (a2, C2, D2) in sols2:
        # NOTE: mod-q^k filters are tautological w.r.t. the linear equations;
        # the only sound test is the full product pu*pv == n. Enumerate.
        L2 = {j: (C2 * pow(a2, j, q) + D2) % q for j in T}
        R3 = []
        ok = True
        for n, (u, v) in zip(ns, pairs):
            low = (L2[u] * q + u) * (L2[v] * q + v)
            if (n - low) % (q * q) != 0:
                ok = False
                break
            R3.append(((n - low) // (q * q)) % q)
        if not ok:
            continue
        sols3 = recover_stream(pairs, l1, R3, q)
        for (a3, C3, D3) in sols3:
            primes = []
            for (u, v) in pairs:
                lu = (C3 * pow(a3, u, q) + D3) % q
                lv = (C3 * pow(a3, v, q) + D3) % q
                pu = lu * q * q + L2[u] * q + u
                pv = lv * q * q + L2[v] * q + v
                primes.append((pu, pv))
            if all(pu * pv == n for (pu, pv), n in zip(primes, ns)):
                if verbose:
                    print("a2 =", a2, "C2 =", C2, "D2 =", D2)
                    print("a3 =", a3, "C3 =", C3, "D3 =", D3)
                return primes
    if verbose: print("no product-consistent solution")
    return None

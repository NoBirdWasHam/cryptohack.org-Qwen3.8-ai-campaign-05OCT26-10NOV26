# DNG Asiacrypt'00 EXACT transcription (paper PDF obtained 2026-11-01,
# https://link.securer... link.springer.com/content/pdf/10.1007/3-540-44448-3_2.pdf):
#  f = 1 + x(A - y - z), A=N+1 ; root (k,p,q), yz=N
#  g_{k,i,b} = e^{m-k} x^i y^a z^b f^k   k=0..m-1, i=1..m-k, b=0,1
#  h_{k,j}   = e^{m-k} y^{a+j} f^k       k=0..m,   j=0..t
#  primary = h_{m,j}. Reduce ONLY mixed yz^? products: (v,w)->(v-min,w-min, N^min).
#  Row order: g by k, i, b then h by k, j -> each row introduces exactly ONE new
#  pure monomial x^u y^v or x^u z^w (paper Sec 4.1) -> square lower-triangular,
#  det = e^{Ce} X^{Cx} Y^{Cy} Z^{Cz}  (Eq.4/Appendix A). Gate: m=3,t=1,a=1 -> e^40 X^40 Y^34 Z^4.
import sys, math, random, re
import gmpy2
from fpylll import IntegerMatrix, LLL
from flint import fmpz_mat

def pmul(p, q):
    r = {}
    for (a1,b1,c1), v1 in p.items():
        for (a2,b2,c2), v2 in q.items():
            k = (a1+a2, b1+b2, c1+c2)
            r[k] = r.get(k, 0) + v1*v2
    return {k: v for k, v in r.items() if v}

def ppow(f, s):
    r = {(0,0,0): 1}
    for _ in range(s): r = pmul(r, f)
    return r

def red_yz(poly):
    out = {}
    for (u, v, w), c in poly.items():
        m = min(v, w)
        key = (u, v-m, w-m)
        val = c * (poly.get("__N__", 1) if False else 1)
        out[key] = out.get(key, 0) + (c, m)  # store (coeff, Npower)
        out[key] = out[key] if isinstance(out[key], list) else out[key]
    # simpler below
    return out

def reduce_rows(N, rows_raw):
    rows = []
    for raw in rows_raw:
        acc = {}
        for (u, v, w), (c, npow) in raw.items():
            key = (u, v, w)
            acc[key] = acc.get(key, [0, 0])
            acc[key][0] += c
            # N-powers: track separately by folding immediately instead
        rows.append(acc)
    return rows

def make_rows(N, e, m, t, a):
    A = N + 1
    f = {(0,0,0): 1, (1,0,0): A, (1,1,0): -1, (1,0,1): -1}
    fp = {s: ppow(f, s) for s in range(m+1)}
    def red(poly):  # fold yz -> N immediately
        out = {}
        for (u, v, w), c in poly.items():
            mm = min(v, w)
            key = (u, v-mm, w-mm)
            out[key] = out.get(key, 0) + c * (N**mm)
        return {k: v for k, v in out.items() if v}
    def row(poly3, factor):
        return red({k: v*factor for k, v in poly3.items()})
    rows = []
    for k in range(m):
        for i in range(1, m-k+1):
            for b in (0, 1):
                rows.append(row({(u+i, v+a, w+b): c for (u,v,w), c in fp[k].items()}, e**(m-k)))
    for k in range(m+1):
        for j in range(t+1):
            rows.append(row({(u, v+a+j, w): c for (u,v,w), c in fp[k].items()}, e**(m-k)))
    return rows

def coeffs_list(rows):
    cols = {}
    for r in rows:
        for k in r: cols[k] = 1
    return sorted(cols)  # any fixed order

def pivots(rows):
    """paper order: each row introduces exactly one new monomial; return pivot per row."""
    seen = set(); piv = []
    for r in rows:
        new = [k for k in r if k not in seen]
        if len(new) != 1: return None, (len(new), r)
        piv.append(new[0]); seen.add(new[0])
    return piv, None

def build(N, e, m, t, a, xb, yb=256, zb=768):
    rows = make_rows(N, e, m, t, a)
    piv, bad = pivots(rows)
    if piv is None:
        raise RuntimeError(f"pivot check failed: row introduces {bad[0]} new monomials")
    cols = coeffs_list(rows)
    if len(cols) != len(rows):
        raise RuntimeError(f"not square: {len(cols)} cols vs {len(rows)} rows")
    X, Y, Z = 1 << xb, 1 << yb, 1 << zb
    ci = {c: i for i, c in enumerate(cols)}
    n = len(rows)
    M = IntegerMatrix(n, n)
    for ri, r in enumerate(rows):
        for (u, v, w), c in r.items():
            M[ri, ci[(u, v, w)]] = c * (X**u) * (Y**v) * (Z**w)
    return M, cols, ci, rows

def bl(x):
    x = abs(int(x))
    if x == 0: return 0
    b = x.bit_length()
    return b - 1 + math.log2(float(x >> (b-53)) / (1 << 53)) if b > 53 else math.log2(float(x))

def det_of(M):
    n = M.nrows
    A = fmpz_mat(n, n, [int(M[r, c]) for r in range(n) for c in range(n)])
    return int(A.det())

def coeff_exponents(N, e, m, t, a, verbose=True):
    """Per-row diagonal in (e,X,Y,Z,N) exponent form -> exact vol exponents (Eq.4 check)."""
    rows = make_rows(N, e, m, t, a)
    names = []
    for k in range(m):
        for i in range(1, m-k+1):
            for b in (0, 1): names.append(("g", k, i, b))
    for k in range(m+1):
        for j in range(t+1): names.append(("h", k, j, 0))
    seen = set(); tot = {"e": 0, "N": 0}
    mon = {"X": 0, "Y": 0, "Z": 0}
    bad = 0
    for nm, rw in zip(names, rows):
        new = [k for k in rw if k not in seen]
        if len(new) != 1:
            if verbose: print("  !! row", nm, "introduces", len(new), "cols")
            bad += 1
            seen |= set(rw); continue
        piv = new[0]; seen |= set(rw)
        co = abs(rw[piv])
        ne = 0
        while co % e == 0 and co > 1:
            co //= e; ne += 1
        nN = 0
        while co % N == 0 and co > 1:
            co //= N; nN += 1
        if co != 1:
            if verbose: print(f"  !! non-monic diag {nm} piv {piv} rest={co}")
            bad += 1
        tot["e"] += ne; tot["N"] += nN
        mon["X"] += piv[0]; mon["Y"] += piv[1]; mon["Z"] += piv[2]
    if verbose:
        print(f"  diag exponents: e^{tot['e']} N^{tot['N']} X^{mon['X']} Y^{mon['Y']} Z^{mon['Z']}  bad={bad} r={len(rows)}")
    return tot, mon, bad

def formula_bits(m, t, a, L, xb, yb, zb):
    def exact(a_):
        Ce = m*(m+1)*(4*m+3*t+5)//6 + ((m*(m+1)*(4*m+3*t+5)) % 6)/6
        return Ce
    Ce = m*(m+1)*(4*m+3*t+5)/6
    Cx = Ce
    if a >= 0:
        Cy = (m**3 + 3*(a+t+1)*m**2 + (3*t**2+6*a*t+3*a**2+6*a+6*t+2)*m + (3*t**2+6*a*t+3*a**2+4*a+3*t-a))/6
        Cz = (m**3 - 3*(a-1)*m**2 + (3*a**2-6*a+2)*m + (3*a**2-2*a-a**3))/6
    else:
        Cy = (m**3 + 3*(a+t+1)*m**2 + (3*t**2+6*a*t+3*a**2+6*a+6*t+2)*m + (3*t**2+6*a*t+3*a**2+3*a+3*t))/6
        Cz = (m**3 - 3*(a-1)*m**2 + (3*a**2-6*a+2)*m + (3*a**2-3*a))/6
    r = (m+1)*(m+t+1)
    tot = Ce*L + Cx*xb + Cy*yb + Cz*zb
    return m*r*L - tot, r, (Ce, Cx, Cy, Cz)

def attack(N, e, m, t, a, xb, yb=256, zb=768, verbose=True, kp=None):
    L = math.log2(float(e))
    marg, r, Cs = formula_bits(m, t, a, L, xb, yb, zb)
    if verbose: print(f"[m={m},t={t},a={a},X=2^{xb}] r={r} formula margin/vec={marg/r:.1f}", flush=True)
    if marg/r < -600: return None
    M, cols, ci, rows = build(N, e, m, t, a, xb, yb, zb)
    r = M.nrows
    if r <= 80:
        d = det_of(M)
        db = bl(d)
        volm = m*r*L - db
        if verbose: print(f"  det^{1/r}={db/r:.1f} e^m={m*L:.1f} det-margin/vec={volm/r:.1f}", flush=True)
        if volm/r < -600: return None
    else:
        if verbose: print("  det check skipped (large r)", flush=True)
    LLL.reduction(M, delta=0.99)
    X, Y, Z = 1 << xb, 1 << yb, 1 << zb
    hbound = m*L - 0.5*math.log2(r)
    polys = []
    for ri in range(r):
        rowv = [int(M[ri, c]) for c in range(r)]
        if all(v == 0 for v in rowv): continue
        l2 = 0.5*bl(sum(v*v for v in rowv))
        if l2 >= hbound: continue
        poly = {}; ok = True
        for c, v in enumerate(rowv):
            if v:
                (u, vv, w) = cols[c]
                wgt = (X**u)*(Y**vv)*(Z**w)
                if v % wgt: ok = False; break
                poly[(u, vv, w)] = v // wgt
        if not ok: continue
        yform = all(vv >= w for (u, vv, w) in poly)
        zform = all(w >= vv for (u, vv, w) in poly)
        if kp is not None:
            k_, p_ = kp
            val = sum(c*(k_**u)*(p_**(vv-w))*(N**w) for (u, vv, w), c in poly.items()) if yform else None
            if yform and val != 0: continue
        polys.append((l2, poly, yform, zform))
    polys.sort(key=lambda z: z[0])
    if verbose: print(f"  below-HG candidates: {len(polys)}", flush=True)
    def to_uni(poly):
        """z = N/y as Laurent in y, then shift to Z[x,y]; vanishing at (k,p) preserved."""
        H = {}
        for (u, vv, w), c in poly.items():
            key = (u, vv - w); mult = N**w
            H[key] = H.get(key, 0) + c * mult
        D = min(v for (u, v) in H) if H else 0
        if D < 0:
            H = {(u, v - D): c for (u, v), c in H.items()}
        return {k: v for k, v in H.items() if v}
    unis = []
    for l2, p_, yf, zf in polys:
        H = to_uni(p_)
        if kp is not None:
            k_, p_2 = kp
            val = sum(c * (k_**u) * (p_2**v) for (u, v), c in H.items())
            if val != 0: continue
        unis.append(H)
    from resultant_lib import resultant_x
    from fractions import Fraction

    def res_var(H1, H2, keep):
        """Resultant eliminating the other variable; returns poly dict in exponent of `keep`.
        H as {(ax, ay): c}; keep='x' eliminates y (resultant over Z[x])."""
        idx = 1 if keep == 'x' else 1 - 1 if keep == 'y' else 0
        oth = 1 - idx
        def coeffs(H, dv):
            d = {}
            for (ax, ay), v in H.items():
                if (ax, ay)[idx] == dv:
                    d[(ax, ay)[oth]] = d.get((ax, ay)[oth], 0) + v
            return {k: v for k, v in d.items() if v}
        d1 = max((t[idx] for t in H1), default=0); d2 = max((t[idx] for t in H2), default=0)
        if d1 + d2 == 0: return None
        n = d1 + d2
        c1 = [coeffs(H1, i) for i in range(d1 + 1)]
        c2 = [coeffs(H2, i) for i in range(d2 + 1)]
        if not c1[0] or not c2[0]:
            pass  # degree drop handled by Sylvester giving zero/padded det anyway
        rows = []
        for i in range(d2):
            row = [{} for _ in range(n)]
            for j in range(d1 + 1):
                row[i + j] = dict(c1[j])
            rows.append(row)
        for i in range(d1):
            row = [{} for _ in range(n)]
            for j in range(d2 + 1):
                row[i + j] = dict(c2[j])
            rows.append(row)
        return sylv_det_generic(rows)

    def sylv_det_generic(rows):
        def pmul(p, q):
            r = {}
            for k1, v1 in p.items():
                for k2, v2 in q.items():
                    r[k1 + k2] = r.get(k1 + k2, 0) + v1 * v2
            return {k: v for k, v in r.items() if v}
        def psub(p, q):
            r = dict(p)
            for k, v in q.items():
                r[k] = r.get(k, 0) - v
            return {k: v for k, v in r.items() if v}
        def pdiv(p, q):
            q = dict(q); dn = max(q); res = {}; r = dict(p)
            while r and max(r) >= dn:
                hn = max(r); co = r[hn] // q[dn]; sh = hn - dn
                res[sh] = res.get(sh, 0) + co
                for kd, vd in q.items():
                    r[kd + sh] = r.get(kd + sh, 0) - co * vd
                r = {k2: v2 for k2, v2 in r.items() if v2}
            if r: raise ZeroDivisionError("non-exact")
            return res
        n = len(rows)
        A = [row[:] for row in rows]
        sign = 1; prev = {0: 1}
        for kk in range(n - 1):
            piv = None
            for rr in range(kk, n):
                if A[rr][kk]:
                    piv = rr; break
            if piv is None: return {}
            if piv != kk:
                A[kk], A[piv] = A[piv], A[kk]; sign = -sign
            p0 = A[kk][kk]
            for i2 in range(kk + 1, n):
                for j2 in range(kk + 1, n):
                    num = psub(pmul(A[i2][j2], p0), pmul(A[i2][kk], A[kk][j2]))
                    if prev != {0: 1}: num = pdiv(num, prev)
                    A[i2][j2] = num
            prev = p0
        det = A[n - 1][n - 1]
        if sign < 0: det = {k: -v for k, v in det.items()}
        return {k: v for k, v in det.items() if v}

    def poly_gcd_frac(P, Q):
        """gcd over Q[x] of dicts {exp: coeff}; returns monic-ish (primitive) dict or {}."""
        def to_f(P):
            return {k: Fraction(v) for k, v in P.items() if v}
        def trim(P):
            P = {k: v for k, v in P.items() if v}
            return P
        def pdiv_f(P, Q):
            P = trim(P); Q = trim(Q)
            if not P: return {}
            dq = max(Q); cq = Q[dq]
            R = dict(P); Qd = {}
            while R and max(R) >= dq:
                dr = max(R); co = R[dr] / cq; sh = dr - dq
                for kd, vd in Q.items():
                    R[kd + sh] = R.get(kd + sh, Fraction(0)) - co * vd
                R = trim(R)
            return R
        P = to_f(P); Q = to_f(Q)
        if not P or not Q: return {}
        # normalize: make primitive integer content 1 (divide by gcd of numerators/lcms of denoms)
        def prim(P):
            from math import gcd as ig
            from functools import reduce
            num = [v.numerator for v in P.values()]
            den = [v.denominator for v in P.values()]
            L = 1
            for dd in den: L = L * dd // g2(L, dd)
            ints = [v * L for v in P.values()]
            gg = 0
            for v in ints: gg = ig(gg, int(v))
            return {k: (v / L) / gg * (gg / gg) for k, v in zip(sorted(P), sorted(P))} if False else None
        def g2(a, b):
            from math import gcd as ig
            return ig(a, b)
        # simple PRS (fractions, degrees small)
        while Q:
            R = pdiv_f(P, Q)
            P, Q = Q, R
        if not P: return {}
        dq = max(P)
        return {k: v / P[dq] for k, v in P.items()}

    def factor_from_k(k):
        if k <= 0: return None
        try:
            inv = pow(k, -1, e)
        except ValueError:
            return None
        base = (e - inv) % e
        for phi_c in (base, base + e, base + 2 * e):
            s = N + 1 - phi_c
            if s <= 0: continue
            disc = s * s - 4 * N
            if disc < 0: continue
            sd = int(gmpy2.isqrt(disc))
            if sd * sd != disc: continue
            pp = (s + sd) // 2
            if pp > 1 and N % pp == 0:
                return pp
        return None

    def pm(S, l):
        r = {e: c % l for e, c in S.items()}
        return {e: c for e, c in r.items() if c}
    def pdiv_mod(P, Q, l):
        P = dict(P); dq = max(Q); iq = pow(Q[dq], -1, l)
        while P and max(P) >= dq:
            dr = max(P); co = P[dr] * iq % l; sh = dr - dq
            for kd, vd in Q.items():
                P[kd + sh] = (P.get(kd + sh, 0) - co * vd) % l
            P = {k: v for k, v in P.items() if v % l}
        return P
    def pdiv_quo(P, Q, l):
        P = dict(P); dq = max(Q); iq = pow(Q[dq], -1, l); res = {}
        while P and max(P) >= dq:
            dr = max(P); co = P[dr] * iq % l; sh = dr - dq
            res[sh] = (res.get(sh, 0) + co) % l
            for kd, vd in Q.items():
                P[kd + sh] = (P.get(kd + sh, 0) - co * vd) % l
            P = {k: v for k, v in P.items() if v % l}
        return {k: v for k, v in res.items() if v}
    def gcd_mod(S1, S2, l):
        A = pm(S1, l); B = pm(S2, l)
        if not A or not B: return None
        while B:
            A, B = B, pdiv_mod(A, B, l)
        if not A: return None
        da = max(A); ia = pow(A[da], -1, l)
        return {e: c * ia % l for e, c in A.items()}

    def res_y_mod(H1, H2, l):
        """Res_y over F_l[x]: dict x-exp -> coeff mod l; roots are x-vals where common y-root."""
        def coeffs(H, dv):
            d = {}
            for (ax, ay), v in H.items():
                if ay == dv: d[ax] = (d.get(ax, 0) + v) % l
            return {k: v for k, v in d.items() if v}
        c1all = {t[1] for t in H1}; c2all = {t[1] for t in H2}
        if not c1all or not c2all: return None
        ylo1, yhi1 = min(c1all), max(c1all); ylo2, yhi2 = min(c2all), max(c2all)
        d1 = yhi1 - ylo1; d2 = yhi2 - ylo2
        n = d1 + d2
        if n == 0: return None
        c1 = [coeffs(H1, i) for i in range(ylo1, yhi1 + 1)]
        c2 = [coeffs(H2, i) for i in range(ylo2, yhi2 + 1)]
        rows = []
        for i in range(d2):
            row = [{} for _ in range(n)]
            for j in range(d1 + 1): row[i + j] = dict(c1[j])
            rows.append(row)
        for i in range(d1):
            row = [{} for _ in range(n)]
            for j in range(d2 + 1): row[i + j] = dict(c2[j])
            rows.append(row)
        def pm_(p, q):
            r = {}
            for k1, v1 in p.items():
                for k2, v2 in q.items():
                    r[k1 + k2] = (r.get(k1 + k2, 0) + v1 * v2) % l
            return {k: v for k, v in r.items() if v}
        def ps_(p, q):
            r = dict(p)
            for k, v in q.items(): r[k] = (r.get(k, 0) - v) % l
            return {k: v for k, v in r.items() if v}
        def pd_(p, q):
            q = {k: v % l for k, v in q.items() if v % l}
            dn = max(q); iq = pow(q[dn], -1, l); res = {}; r = dict(p)
            while r and max(r) >= dn:
                hn = max(r); co = r[hn] * iq % l; sh = hn - dn
                res[sh] = (res.get(sh, 0) + co) % l
                for kd, vd in q.items():
                    r[kd + sh] = (r.get(kd + sh, 0) - co * vd) % l
                r = {k2: v2 for k2, v2 in r.items() if v2 % l}
            if r: raise ZeroDivisionError("non-exact")
            return res
        A = [row[:] for row in rows]
        sign = 1; prev = {0: 1}
        for kk in range(n - 1):
            piv = None
            for rr in range(kk, n):
                if A[rr][kk]:
                    piv = rr; break
            if piv is None: return {}
            if piv != kk:
                A[kk], A[piv] = A[piv], A[kk]; sign = -sign
            p0 = A[kk][kk]
            for i2 in range(kk + 1, n):
                for j2 in range(kk + 1, n):
                    num = ps_(pm_(A[i2][j2], p0), pm_(A[i2][kk], A[kk][j2]))
                    if prev != {0: 1}: num = pd_(num, prev)
                    A[i2][j2] = num
            prev = p0
        det = A[n - 1][n - 1]
        if sign < 0: det = {k: (-v) % l for k, v in det.items()}
        return {k: v % l for k, v in det.items() if v % l}

    if verbose: print(f"  unis for extraction: {len(unis)}", flush=True)
    seen = set(); ded = []
    for H in unis:
        key = frozenset(H.items())
        if key not in seen:
            seen.add(key); ded.append(H)
    unis = ded
    def content_reduce(H):
        g = 0
        for c in H.values(): g = gmpy2.gcd(g, c)
        if g > 1: H = {k: v // g for k, v in H.items()}
        return H
    unis = [content_reduce(H) for H in unis]
    globals()['_LAST_UNIS'] = unis
    globals()['_LAST_KP'] = kp
    globals()['_LAST_NE'] = (N, e)
    llist = []
    ll = 2**61 - 1
    for _ in range(24):
        ll = int(gmpy2.next_prime(ll)); llist.append(ll); ll += 2
    residues = []
    for li in llist:
        if len(unis) < 3: break
        Qs = [{t: c % li for t, c in H.items()} for H in unis[:6]]
        Ss = []
        for (i, j) in ((0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3), (0, 4), (1, 4), (2, 5), (3, 4)):
            if j >= len(Qs): continue
            try: S = res_y_mod(Qs[i], Qs[j], li)
            except Exception: S = None
            if S and max(S, default=0) > 0: Ss.append((i, j, S))
        if len(Ss) < 2: continue
        ri = None; info = []
        for a_ in range(len(Ss)):
            for b_ in range(a_ + 1, len(Ss)):
                ia, ja, Sa = Ss[a_]; ib, jb, Sb = Ss[b_]
                if len({ia, ja} & {ib, jb}) == 0: continue
                A_, B_ = Sa, Sb
                for layer in range(3):
                    C = gcd_mod(A_, B_, li)
                    if verbose and li in llist[:1] and a_ == 0 and b_ <= 2:
                        print(f"    dbg pair({ia},{ja})&({ib},{jb}) L{layer} Cdeg={max(C, default=-2)} Adeg={max(A_, default=-1)}", flush=True)
                    if not C or max(C, default=0) == 0: break
                    if max(C, default=0) == 1:
                        ri = (-C[0] * pow(C[1], -1, li)) % li; break
                    try:
                        Ta = pdiv_quo(A_, C, li); Tb = pdiv_quo(B_, C, li)
                    except Exception:
                        break
                    if not Ta or not Tb: break
                    if max(Ta) == 1:
                        ri = (-Ta[0] * pow(Ta[1], -1, li)) % li; break
                    if max(Tb) == 1:
                        ri = (-Tb[0] * pow(Tb[1], -1, li)) % li; break
                    G2 = gcd_mod(Ta, Tb, li)
                    if G2 and max(G2, default=0) == 1:
                        ri = (-G2[0] * pow(G2[1], -1, li)) % li; break
                    info.append((max(C), max(Ta), max(Tb)))
                    A_, B_ = Ta, Tb
                if ri is not None: break
            if ri is not None: break
        if verbose and li in llist[:2]:
            print(f"   l0: Ss={len(Ss)} layers={info[:4]} ri={'yes' if ri is not None else 'NO'}", flush=True)
        if ri is None: continue
        residues.append((ri, li))
        def crt(sub):
            K = 0; M = 1
            for (r_, l_) in sub:
                t = ((r_ - K) % l_) * pow(M % l_, -1, l_) % l_
                K += M * t; M *= l_; K %= M
            return K, M
        if len(residues) >= 5:
            cands = [crt(residues)]
            for skip in range(len(residues)):
                cands.append(crt([r for idx_, r in enumerate(residues) if idx_ != skip]))
            for (K, M) in cands:
                if M < (1 << 320): continue
                for tt in range(3):
                    g = factor_from_k((K - tt * M) % M) if tt else factor_from_k(K)
                    if g:
                        if verbose: print(f"  FACTOR via CRT-k {len(bin(K))-2}b", flush=True)
                        return g
    # exact Res_x route: R(y) has roots p AND q (symmetry); exact integer roots via flint
    from flint import fmpz_poly
    for (i, j) in [(0,1),(0,2),(1,2),(0,3),(2,3),(1,3),(1,4),(2,4)]:
        if j >= len(unis): continue
        try:
            R = res_var(unis[i], unis[j], 'y')
        except Exception:
            continue
        R = {e: c for e, c in (R or {}).items() if c}
        if not R or max(R, default=0) < 1:
            continue
        s = min(R)
        Rp = {e - s: c for e, c in R.items()}
        try:
            P = fmpz_poly([Rp.get(t, 0) for t in range(max(Rp) + 1)])
            rts = P.roots()
        except Exception as ex:
            if verbose: print(f"  Res_x({i},{j}) roots err {repr(ex)[:70]}", flush=True)
            continue
        if verbose: print(f"  Res_x({i},{j}) y^{s}: {len(rts)} roots", flush=True)
        for rt, mult in rts:
            try:
                n_ = int(rt)
            except Exception:
                continue
            if n_ > 1 and N % n_ == 0 and n_ < N:
                if verbose: print(f"  FACTOR via exact Res_x root {len(bin(n_))-2}b pair({i},{j})", flush=True)
                return n_
    return None

def synth(dbits, seed, ms):
    random.seed(seed)
    def rprime(bits):
        return int(gmpy2.next_prime(random.getrandbits(bits) | (1 << (bits-1)) | 1))
    p, q = rprime(256), rprime(768)
    N = p*q; phi = (p-1)*(q-1)
    while True:
        d = rprime(dbits)
        if dbits != 300 or d > N**0.292: break
    e = int(pow(d, -1, phi))
    k_ = (d*e-1)//phi
    print(f"synth d={dbits}b", flush=True)
    for (m, t, a) in ms:
        try:
            g = attack(N, e, m, t, a, dbits, kp=(k_, p))
        except Exception as ex:
            print("  fail:", repr(ex)[:110], flush=True); continue
        if g and N % g == 0:
            print(f"SYNTH d={dbits} OK m={m},t={t},a={a} exact={g in (p,q)}", flush=True)
            return (m, t, a)
    print(f"SYNTH d={dbits} ALL FAIL", flush=True)
    return None

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "detcheck"
    if mode == "detcheck":
        import gmpy2, random
        random.seed(1)
        def rprime(b): return int(gmpy2.next_prime(random.getrandbits(b)|(1<<(b-1))|1))
        p, q = rprime(256), rprime(768); N=p*q; e=rprime(1023)
        M, cols, ci, rows = build(N, e, 3, 1, 1, 192)
        d = abs(det_of(M))
        want = (e**40)*(2**(40*192))*(2**(34*256))*(2**(4*768))
        print("det == e^40 X^40 Y^34 Z^4 :", d == want)
        if d != want:
            print("det bits:", bl(d), "want bits:", bl(want))
    elif mode == "gate192":
        synth(192, 20261101, [(3,1,1),(4,2,0),(4,2,1),(5,3,0),(5,3,-1) if False else (5,3,1)])
    elif mode == "synth300":
        synth(300, 20261102, [(5,3,0),(6,3,0),(6,4,0),(6,4,1),(7,4,0),(7,4,1)])
    else:
        txt = open("output.txt").read()
        N = int(re.search(r"N = 0x([0-9a-f]+)", txt).group(1), 16)
        e = int(re.search(r"e = 0x([0-9a-f]+)", txt).group(1), 16)
        c = int(re.search(r"c = 0x([0-9a-f]+)", txt).group(1), 16)
        g = None
        cfgs = [(6,4,0),(6,4,1),(7,4,0),(7,6,0),(7,4,1),(8,5,0),(8,7,0),(9,7,0)]
        for (m, t, a) in cfgs:
            marg, r, Cs = formula_bits(m, t, a, math.log2(float(e)), 300, 256, 768)
            print(f"cfg m={m},t={t},a={a}: r={r} margin/vec={marg/r:.1f}", flush=True)
            if marg/r < -400: continue
            try:
                g = attack(N, e, m, t, a, 300)
            except Exception as ex:
                print("  err:", repr(ex)[:120], flush=True); continue
            if g: break
        if g:
            p, q = (g, N//g) if g < N//g else (N//g, g)
            phi = (p-1)*(q-1)
            d = int(pow(e, -1, phi))
            from Crypto.Util.number import long_to_bytes
            flag = long_to_bytes(pow(c, d, N))
            print("FLAG:", flag.decode(errors="replace"), flush=True)
            open("flag_found.txt", "w").write(flag.decode(errors="replace"))
        else:
            print("FAILED", flush=True)

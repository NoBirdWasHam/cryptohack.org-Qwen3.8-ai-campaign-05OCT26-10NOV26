"""Port of Connor M's Unbalanced-ICCAthens sage solver to fpylll.

Lattice over Z[x,y,z]/(yz - N):
  f = C + x*(A - y - z),  A = N+1  (C=2 per original writeup; root x0=2k makes
  f(root) = 2*(ed) divisible by e; C=1 gives root x0=k)
  rows: e^(m-k) * x^i * y^a * z^b * f^k   for k<m, 1<=i<=m-k, b in {0,1}
        e^(m-k) * y^(a+j) * f^k           for k<=m, 0<=j<=t   (a=0)
  monomial bounds: x:2^Xb, y:2^Yb (p), z:2^Zb (q)
After LLL: reconstruct vanishing polys, add (y*z - N), Groebner over QQ,
univariate factor -> integer root -> check p | N.
"""
from fpylll import IntegerMatrix, LLL
import re, sys, time

# ---------- poly in Z[x,y,z]/(yz-N), dict {(a,b,c): coeff} with b*c==0 ----------
def pnorm(p, N, a, b, c):
    """reduce yz -> N"""
    while b > 0 and c > 0:
        p -= b if b < c else c  # placeholder
    return p

def pmul(f, g, N):
    # reduce min(b,c) yz factors into N^t at monomial level
    out = {}
    for (a1, b1, c1), v1 in f.items():
        for (a2, b2, c2), v2 in g.items():
            a = a1 + a2
            b = b1 + b2
            c = c2 + c1 if False else c1 + c2
            t = b if b < c else c
            coeff = v1 * v2 * (N ** t)
            key = (a, b - t, c - t)
            out[key] = out.get(key, 0) + coeff
    return {k: v for k, v in out.items() if v}

def ppow(f, k, N):
    r = {(0, 0, 0): 1}
    for _ in range(k):
        r = pmul(r, f, N)
    return r

def padd(*fs):
    out = {}
    for f in fs:
        for k, v in f.items():
            out[k] = out.get(k, 0) + v
    return {k: v for k, v in out.items() if v}

def pmulsc(f, s):
    return {k: v * s for k, v in f.items() if v * s}

def pshift(f, a=0, b=0, c=0):
    return {(ka + a, kb + b, kc + c): v for (ka, kb, kc), v in f.items()}


def build_lattice(N, e, m, t, a, bounds, C=2):
    A = N + 1
    f = {(0, 0, 0): C, (1, 0, 0): A, (1, 1, 0): -1, (1, 0, 1): -1}
    fpow = [ppow(f, k, N) for k in range(m + 1)]
    Em = [e ** (m - k) for k in range(m + 1)]
    rows = []
    for k in range(m):
        for i in range(1, m - k + 1):
            for b in range(2):
                rows.append(pshift(pmulsc(fpow[k], Em[k]), a=i, b=0, c=b))
    for k in range(m + 1):
        for j in range(t + 1):
            rows.append(pshift(pmulsc(fpow[k], Em[k]), a=0, b=a + j, c=0))
    # monomial set
    mons = sorted({m_ for r in rows for m_ in r})
    D = len(mons)
    print(f"rows={len(rows)} monomials={D}")
    if D != len(rows):
        print("NON-SQUARE", len(rows), D)
    W = [2 ** (bounds[0] * a_ + bounds[1] * b_ + bounds[2] * c_) for (a_, b_, c_) in mons]
    B = IntegerMatrix(len(rows), D)
    for r, poly in enumerate(rows):
        for j, mon in enumerate(mons):
            if mon in poly:
                B[r, j] = poly[mon] * W[j]
    return mons, W, B


def solve(N, e, c, m, t, a, bounds, C=2, verbose=True):
    mons, W, B = build_lattice(N, e, m, t, a, bounds, C)
    t0 = time.time()
    LLL.reduction(B)
    if verbose:
        print("LLL done in %.1fs, dim=%d" % (time.time() - t0, B.nrows))
    # reconstruct ALL reduced rows (exact division by column scales), sort by norm
    em2 = (e ** m) ** 2
    good = []
    for r in range(B.nrows):
        w, n2, poly = 0, 0, {}
        for j, mon in enumerate(mons):
            v = B[r, j]
            if v == 0:
                continue
            if v % W[j] != 0:
                n2 = None
                break
            cf = v // W[j]
            poly[mon] = cf
            w += 1
            n2 += cf * cf * W[j] * W[j]
        if n2 is not None:
            good.append((n2, poly))
    good.sort(key=lambda x: x[0])
    nhg = sum(1 for n2, _ in good if n2 * len(mons) < em2)
    if verbose:
        print(f"{nhg}/{len(good)} rows pass strict HG bound (norm < e^m/sqrt(w))")
    # extraction
    from sympy import QQ, groebner, Poly
    from sympy.abc import x, y, z
    import flint

    def to_sympy(poly, vs=(x, y, z)):
        terms = [v * vs[0] ** aa * vs[1] ** bb * vs[2] ** cc for (aa, bb, cc), v in poly.items()]
        return sum(terms, 0)

    rowsp = [to_sympy(g) for _, g in good]
    yzN = y * z - N
    # prefixes: all rows first (like the original), then decreasing
    tried = set()
    for cnt in [len(rowsp), 30, 12, 8, 6, 5, 4, 3, 2]:
        if cnt in tried or cnt < 2:
            continue
        tried.add(cnt)
        polys = rowsp[:cnt] + [yzN]
        try:
            G = groebner(polys, x, y, z, domain=QQ, order="lex")
        except Exception:
            continue
        uni = None
        for g in G:
            v = g.free_symbols
            if len(v) == 1:
                uvar = list(v)[0]
                uni = Poly(g, uvar, domain=QQ)
                break
        if uni is None:
            continue
        try:
            from math import lcm
            dens = [cc.q if hasattr(cc, "q") else 1 for cc in uni.all_coeffs()]
            L = lcm(*dens)
            fl = flint.fmpz_poly([int(cc * L) for cc in uni.all_coeffs()])
        except Exception:
            continue
        # integer roots: try exact rational via sympy first (cheap polys)
        cands = []
        try:
            rt = fl.nroots(prec=6000)
            for r_ in rt:
                if not r_.imag.is_zero():
                    continue
                rr = int(r_.real)
                for adj in range(-3, 4):
                    p_ = rr + adj
                    if p_ > 1 and N % p_ == 0:
                        cands.append(p_)
        except Exception:
            pass
        if not cands:
            # exact fallback: integer root isolation on cleared-denominator poly
            try:
                Pz = Poly(uni.all_coeffs(), uni.gens, domain=QQ)
                for r_ in Pz.real_roots():
                    if r_.is_rational:
                        p_ = int(r_)
                    else:
                        continue
                    if p_ > 1 and N % p_ == 0:
                        cands.append(p_)
            except Exception:
                pass
        if cands:
            if verbose:
                print(f"root via {cnt} rows + yzN, var={uvar}")
            return (cnt, sorted(set(cands)))
    return None


def run(N, e, c, m, t, a, bounds, C=2):
    res = solve(N, e, c, m, t, a, bounds, C)
    if not res:
        print("FAILED to find p")
        return None
    cnt, cands = res
    p = None
    q = None
    for cand in cands:
        if N % cand == 0:
            q_ = N // cand
            from flint import fmpz
            if fmpz(q_).is_prime() and fmpz(cand).is_prime() and cand * q_ == N:
                p, q = cand, q_
                break
    if p is None:
        print("candidate not a prime factor:", cands)
        return None
    print("RECOVERED p*q == N:", p * q == N)
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m_ = pow(c, d, N)
    from Crypto.Util.number import long_to_bytes
    flag = long_to_bytes(m_)
    print("FLAG:", flag)
    return flag


if __name__ == "__main__":
    txt = open(r"~/AppData/Local/hermes/cache/scratch/unbal/output.txt").read()
    N = int(re.search(r"N = (0x[0-9a-f]+)", txt).group(1), 16)
    e = int(re.search(r"e = (0x[0-9a-f]+)", txt).group(1), 16)
    c = int(re.search(r"c = (0x[0-9a-f]+)", txt).group(1), 16)
    if sys.argv[1:] and sys.argv[1] == "toy":
        from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
        flag = b"FLAG-REDACTED-SEE-FLAGS-MIRROR"
        p_, q_ = getPrime(64), getPrime(192)
        N, e = p_ * q_, None
        phi = (p_ - 1) * (q_ - 1)
        while True:
            d_ = getPrime(75)
            if d_ > N ** 0.292:
                break
        e = pow(d_, -1, phi)
        c = pow(bytes_to_long(flag), e, N)
        print("toy p,q,d,k:", p_, q_, d_, (e * d_ - 1) // phi)
        run(N, e, c, 5, 5, 0, (76, 64, 192), C=2)
    else:
        run(N, e, c, 5, 5, 0, (300, 256, 768), C=2)

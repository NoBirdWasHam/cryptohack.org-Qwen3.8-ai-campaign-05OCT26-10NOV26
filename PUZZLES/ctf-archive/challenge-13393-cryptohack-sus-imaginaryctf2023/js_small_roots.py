# Canonical HG / Jochemsz-Stevenhagen bivariate small_roots on F1 = x*(x^2+x+1)*y - N
# (VALIDATION 2026-11-05 "ONE next move"; control-toy-first per poly-ring-toolkit [R09] discipline.)
#
# EXACT-root bookkeeping: lattice L = < f, N^m > truncated to window
#   rows: N^{m-k} * x^a y^b * f^k , k=0..m, (a,b) in triangle a+b<=t,
# built in shifted-scaled vars x = p0 + X*x', y = r0 + Y*y'. Since f vanishes OVER Z at the
# true root (exact root!), EVERY lattice vector g satisfies g(p,r) = 0 mod N^m.
# Howgrave-Graham then proves g(p,r) = 0 over Z whenever ||g||_1 < N^m (coefficients in the
# shifted-scaled basis, |x'|,|y'| <= 1 on the root set).
# g is USEFUL iff g not divisible by f in Q[x,y] -> Res_y(f,g) has x'-root (p-p0)/X.
import sys, time, math
from math import comb
from fractions import Fraction
from fpylll import IntegerMatrix, LLL

# ---------------- polynomial helpers ----------------
def pmul2(A, B):
    C = {}
    for (i1, j1), c1 in A.items():
        if not c1: continue
        for (i2, j2), c2 in B.items():
            if c2:
                k = (i1 + i2, j1 + j2)
                C[k] = C.get(k, 0) + c1 * c2
    return C

def ppow2(A, k):
    R = {(0, 0): 1}
    for _ in range(k):
        R = pmul2(R, A)
    return R

def spow1(c0, s, e):
    # (c0 + s*z)^e -> {i: coeff}
    return {i: comb(e, i) * c0 ** (e - i) * s ** i for i in range(e + 1)}

def shifted_f(N, p0, r0, X, Y):
    # f = x^3*y + x^2*y + x*y - N, x = p0 + X x', y = r0 + Y y'
    fS = {}
    ys = spow1(r0, Y, 1)
    for xp in (3, 2, 1):
        xs = spow1(p0, X, xp)
        for i, ci in xs.items():
            for j, cj in ys.items():
                fS[(i, j)] = fS.get((i, j), 0) + ci * cj
    fS[(0, 0)] = fS.get((0, 0), 0) - N
    return fS

def build_lattice(N, p0, r0, X, Y, m, t):
    # Truncated ideal <f, N^m> over window (0..Dx)x(0..Dy):
    #   k=0 rows: N^m * x^a y^b, all a<=Dx, b<=Dy
    #   k>=1 rows: N^{m-k} * f^k * x^a y^b, a <= max(Dx-3k,0), b <= max(Dy-k,0)
    # (t kept in signature: window Dx=3m+t, Dy=m+t as before)
    fS = shifted_f(N, p0, r0, X, Y)
    Dx = 3 * m + t
    Dy = m + t
    rows = []
    for k in range(m + 1):
        base = ppow2(fS, k)
        Np = N ** (m - k)
        amax = max(Dx - 3 * k, 0)
        bmax = max(Dy - k, 0)
        for a in range(amax + 1):
            xa = {(i, 0): c for i, c in spow1(p0, X, a).items()}
            for b in range(bmax + 1):
                yb = {(0, j): c for j, c in spow1(r0, Y, b).items()}
                P = pmul2(pmul2(base, xa), yb)
                if any(i > Dx or j > Dy for (i, j) in P):
                    raise RuntimeError("window too small")
                P = {ij: c * Np for ij, c in P.items() if c}
                if P:
                    rows.append(P)
    monos = [(i, j) for i in range(Dx + 1) for j in range(Dy + 1)]
    est_rows = sum((max(Dx - 3 * k, 0) + 1) * (max(Dy - k, 0) + 1) for k in range(m + 1))
    if est_rows > 600:
        raise RuntimeError(f"skip: {est_rows} rows > 600 cap")
    idx = {mn: q for q, mn in enumerate(monos)}
    w = len(monos)
    M = IntegerMatrix(len(rows), w)
    for ri, P in enumerate(rows):
        for ij, c in P.items():
            M[ri, idx[ij]] = c
    return M, monos, fS

# ---------------- row analysis ----------------
def l1_norm(M, ri):
    s = 0
    for ci in range(M.ncols):
        v = int(M[ri, ci])
        if v: s += abs(v)
    return s

def row_poly(M, ri, monos):
    d = {}
    for ci, mn in enumerate(monos):
        v = int(M[ri, ci])
        if v: d[mn] = v
    return d

def eval2(d, xf, yf):
    s = Fraction(0)
    for (i, j), c in d.items():
        term = c
        if i: term *= (xf ** i)
        if j: term *= (yf ** j)
        s += term
    return s

def div_exact_f(d, fS):
    # True iff d in ideal(fS) over Q[x,y]; fS y-linear with leading monomial (dx,1)
    dxmax = max(i for (i, j), c in fS.items() if j == 1 and c)
    lc = Fraction(fS[(dxmax, 1)])
    R = {k: Fraction(v) for k, v in d.items()}
    while True:
        cands = [ij for ij, v in R.items() if v != 0 and ij[1] >= 1 and ij[0] >= dxmax]
        if not cands:
            break
        ij = max(cands, key=lambda tt: (tt[0], tt[1]))
        q = R[ij] / lc
        sh = (ij[0] - dxmax, ij[1] - 1)
        for tt, c in fS.items():
            key = (tt[0] + sh[0], tt[1] + sh[1])
            R[key] = R.get(key, Fraction(0)) - q * c
    return all(v == 0 for v in R.values())

def resultant_y(fS, g):
    # fS = A(x') y' + B(x'); Res_y(f,g) = sum_j g_j * (-B)^j * A^{dg-j}
    fA, fB = {}, {}
    for (i, j), c in fS.items():
        if j == 1: fA[i] = fA.get(i, 0) + c
        elif j == 0: fB[i] = fB.get(i, 0) + c
        else: raise ValueError("f not y-linear")
    if not g: return {}
    dg = max(j for (_, j) in g.keys())
    gj = {}
    for (i, j), c in g.items():
        gj.setdefault(j, {})[i] = c
    def pm(P, Q):
        C = {}
        for i1, c1 in P.items():
            for i2, c2 in Q.items():
                C[i1 + i2] = C.get(i1 + i2, 0) + c1 * c2
        return C
    negB = {i: -c for i, c in fB.items()}
    total = {}
    for j in range(dg + 1):
        term = gj.get(j, {})
        if not term: continue
        Bj, Aj = {(0, 0): 1}, {(0, 0): 1}
        for _ in range(j): Bj = pm(Bj, negB)
        for _ in range(dg - j): Aj = pm(Aj, fA)
        tt = pm(pm(term, Bj), Aj)
        for kk, vv in tt.items(): total[kk] = total.get(kk, 0) + vv
    return total

def rat_roots(R1):
    # integer/rational roots of univariate {i: c}; exact interval isolation (robust)
    import sympy
    x = sympy.symbols('x')
    if not R1: return []
    p = sum(c * x ** i for i, c in R1.items() if c)
    out = []
    try:
        pf = sympy.Poly(p, x, domain='QQ')
        for iv in pf.real_roots():
            try:
                interval = iv.get_interval(40)
                a, b = interval.a, interval.b   # exact Rational bounds
            except Exception:
                try:
                    v = sympy.nsimplify(iv.evalf(60))
                    a = b = sympy.Rational(str(v))
                except Exception:
                    continue
            import math as _m
            c_lo = -((-a.q and a.numerator * -1) // a.q) if False else -((-a.numerator) // a.q)  # ceil(a)
            c_hi = b.numerator // b.q  # floor(b)
            for cand in range(c_lo - 1, c_hi + 2):
                if pf.eval(cand) == 0 and cand not in out:
                    out.append(cand)
    except Exception:
        pass
    if not out:
        try:
            pf = sympy.Poly(p, x, domain='QQ')
            for fac, mult in pf.factor_list()[1]:
                if fac.degree() == 1:
                    rc = sympy.Poly(fac, x, domain='QQ').nth(0)
                    lcv = sympy.Poly(fac, x, domain='QQ').LC()
                    val = sympy.Rational(-rc, lcv) if rc != 0 else sympy.Integer(0)
                    if val.q == 1 and int(val) not in out:
                        out.append(int(val))
        except Exception:
            pass
    return out

# ---------------- main attempt ----------------
def js_attempt(N, p0, r0, X, Y, m, t, p_true=None, r_true=None, time_limit=None):
    t0 = time.time()
    M, monos, fS = build_lattice(N, p0, r0, X, Y, m, t)
    LLL.reduction(M)
    Nm = N ** m
    logN = math.log2(N) if N < 2 ** 4096 else float(N.bit_length())
    Nm_bits = logN * m
    res = {"shape": (m, t), "dim": (M.nrows, M.ncols), "found": None,
           "min_l1_all_bits": None, "min_l1_useful_bits": None,
           "hg_margin_useful_bits": None, "vanish_useful_found": False,
           "n_zero_rows": 0}
    best_all, best_useful = None, None
    for ri in range(M.nrows):
        if time_limit and time.time() - t0 > time_limit:
            res["timeout"] = True
            break
        norm = l1_norm(M, ri)
        if norm == 0:
            res["n_zero_rows"] += 1
            continue
        if best_all is None or norm < best_all: best_all = norm
        g = row_poly(M, ri, monos)
        useful = not div_exact_f(g, fS)
        if not useful:
            continue
        if best_useful is None or norm < best_useful: best_useful = norm
        vanish = False
        if p_true is not None:
            xf = Fraction(p_true - p0, X)
            yf = Fraction(r_true - r0, Y)
            vanish = (eval2(g, xf, yf) == 0)
            if vanish:
                res["vanish_useful_found"] = True
        if (norm < Nm) or vanish:
            res["_nres"] = res.get("_nres", 0) + 1
            if res["_nres"] > 8:
                continue
            R1 = resultant_y(fS, g)
            for xv in rat_roots(R1):
                x0 = p0 + X * xv
                if x0 <= 1: continue
                D = x0 * (x0 * x0 + x0 + 1)
                if D > 1 and N % D == 0:
                    res["found"] = x0
                    break
            if res["found"]:
                break
    res["min_l1_all_bits"] = best_all.bit_length() if best_all else None
    res["min_l1_useful_bits"] = best_useful.bit_length() if best_useful else None
    if best_useful is not None:
        res["hg_margin_useful_bits"] = math.log2(best_useful) - Nm_bits
    return res

# ---------------- toys ----------------
def make_toy(Lp, Lr, seed=0):
    import random, sympy
    rnd = random.Random(0xC0FFEE + seed)
    while True:
        p = int(sympy.nextprime(rnd.randrange(2 ** (Lp - 1), 2 ** Lp)))
        if sympy.isprime(p * p + p + 1):
            break
    r = int(sympy.nextprime(rnd.randrange(2 ** (Lr - 1), 2 ** Lr)))
    while not sympy.isprime(r):
        r = int(sympy.nextprime(r + 1))
    return p, p * p + p + 1, r

def toy_params(p, r):
    Lp = p.bit_length(); Lr = r.bit_length()
    p0 = 2 ** (Lp - 1) + 2 ** (Lp - 2); X = 2 ** (Lp - 2)
    r0 = 2 ** (Lr - 1) + 2 ** (Lr - 2); Y = 2 ** (Lr - 2)
    return p0, X, r0, Y

def run_toy(Lp, Lr, shapes, tag=""):
    p, q, r = make_toy(Lp, Lr)
    N = p * q * r
    p0, X, r0, Y = toy_params(p, r)
    print(f"[toy {tag} {Lp}/{2*Lp}/{Lr}] N={N.bit_length()}b log2(XY)={math.log2(X*Y):.1f} "
          f"(JS exact-root heuristic needs X*Y <~ N^(2/4) = {N.bit_length()/2:.1f})", flush=True)
    for (m, t) in shapes:
        t0 = time.time()
        try:
            res = js_attempt(N, p0, r0, X, Y, m, t, p_true=p, r_true=r, time_limit=120)
        except Exception as ex:
            print(f"  (m={m},t={t}) EXC {ex}", flush=True)
            continue
        print(f"  (m={m},t={t}) dim={res['dim']} found={res['found']} "
              f"vanish_useful={res['vanish_useful_found']} minL1all={res['min_l1_all_bits']}b "
              f"minL1useful={res['min_l1_useful_bits']}b HGMarginUseful={res['hg_margin_useful_bits']} "
              f"{time.time()-t0:.1f}s", flush=True)
        if res['found'] == p:
            print("  -> TOY SOLVED BY LATTICE (p found, D = p(p^2+p+1) | N)", flush=True)
            return True
    return False

def load_real():
    d = {}
    path = "~/Practice_runs/cryptohack_org/challenge-13393-cryptohack-sus-imaginaryctf2023/output.txt"
    for line in open(path):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            d[k.strip()] = int(v.strip())
    return d['n'], d['e'], d['c']

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "toys"
    if mode == "toys":
        ok1 = run_toy(40, 30, [(2, 2), (3, 2), (3, 3), (4, 3), (5, 4), (6, 4)], tag="inside-threshold")
        ok2 = run_toy(40, 96, [(3, 3), (5, 4)], tag="just-outside")
        print("VALIDATION:", "PASS" if ok1 else "FAIL", "| just-outside solved:", ok2, flush=True)
    elif mode == "realratio":
        run_toy(60, 180, [(2, 2), (3, 2), (3, 3), (4, 3), (5, 4)], tag="real-ratios")
    elif mode == "real":
        n, e, c = load_real()
        p0 = 2 ** 511 + 2 ** 510; X = 2 ** 509
        r0 = 2 ** 1535 + 2 ** 1534; Y = 2 ** 1534
        print(f"n bits={n.bit_length()} log2(XY)={math.log2(X*Y):.1f} "
              f"N^(2/4) bits={n.bit_length()/2:.1f}", flush=True)
        for (m, t) in [(2, 2), (3, 2), (3, 3), (4, 3)]:
            t0 = time.time()
            try:
                res = js_attempt(n, p0, r0, X, Y, m, t, time_limit=300)
            except Exception as ex:
                print(f"  (m={m},t={t}) EXC {ex}", flush=True); continue
            print(f"  (m={m},t={t}) dim={res['dim']} found={res['found']} "
                  f"minL1all={res['min_l1_all_bits']}b minL1useful={res['min_l1_useful_bits']}b "
                  f"HGMarginUseful_bits={res['hg_margin_useful_bits']} {time.time()-t0:.1f}s", flush=True)

# Pure-Python + fpylll port of the CANONICAL Jochemsz-May (PKC 2007, Sect. 2.2) integer
# multivariate small_roots, as implemented in jvdsn/crypto-attacks shared/small_roots/
# jochemsz_may_integer.py (reference fetched 2026-11-06; unmodified algorithm logic).
# Citations: [R37] Jochemsz & May PKC'07; [R38] jvdsn/crypto-attacks (reference impl);
# poly-ring-toolkit [R09]. Control-toy-first discipline per poly-ring-toolkit.
#
# Applied to F1(x,y) = x(x^2+x+1)y - n, exact root (p, r), MIDPOINT shift x=p0+u, y=r0+v.
import sys, time, math
from fractions import Fraction
from fpylll import IntegerMatrix, LLL

# ---- 2-var poly dicts {(i,j): int} ----
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
    from math import comb
    return {i: comb(e, i) * c0 ** (e - i) * s ** i for i in range(e + 1)}

def shifted_f(N, p0, r0):
    # F1(p0+u, r0+v) = A(u) v + B(u)
    fS = {}
    for xp in (3, 2, 1):
        xs = spow1(p0, 1, xp)
        for i, ci in xs.items():
            fS[(i, 1)] = fS.get((i, 1), 0) + ci
    # note: x(x^2+x+1) = x^3+x^2+x ; A(u) = (p0+u)^3+(p0+u)^2+(p0+u)
    fS[(0, 1)] = fS.get((0, 1), 0) + 0
    A = {i: c for (i, j), c in fS.items() if j == 1}
    B = {i: c * r0 for i, c in A.items()}
    B[0] = B.get(0, 0) - N
    P = {(i, 1): c for i, c in A.items()}
    for i, c in B.items():
        P[(i, 0)] = P.get((i, 0), 0) + c
    return P

# ---- strategies (ref jochemsz_may_integer.py) ----
def basic_SM(fsupp_pow, m):
    # S = monomials of f^{m-1}; M = monomials of f^m
    S = set(ppow2(fsupp_pow, m - 1).keys()) if m >= 1 else set()
    M = set(ppow2(fsupp_pow, m).keys())
    return S, M

def extended_SM(fsupp_pow, m, t1, t2):
    if m < 1:
        return set(), set()
    S = set()
    for mono in ppow2(fsupp_pow, m - 1):
        for j1 in range(t1 + 1):
            for j2 in range(t2 + 1):
                S.add((mono[0] + j1, mono[1] + j2))
    M = set()
    for mono in S:
        for tt in fsupp_pow:
            M.add((mono[0] + tt[0], mono[1] + tt[1]))
    return S, M

def _guard_roots(R1, cap_bits=8192):
    mx = max((abs(c).numerator if isinstance(c, Fraction) else abs(c)).bit_length()
             for c in R1.values()) if R1 else 0
    if mx > cap_bits:
        return []
    return rat_roots(R1)

def integer_multivariate(N, p0, r0, X, Y, m, strategy="basic", t=(0, 0), time_limit=None):
    """Returns dict with found roots / stats. Exact-integer-root JM on shifted F1."""
    t0 = time.time()
    fS = shifted_f(N, p0, r0)
    a0 = fS[(0, 0)]
    fsupp = {ij: 1 for ij in fS}
    if a0 == 0:
        raise RuntimeError("shift hit a root")
    if strategy == "basic":
        S, M = basic_SM(fS, m)
    else:
        S, M = extended_SM(fS, m, t[0], t[1])
    if not S:
        return {"error": "empty S"}
    l1 = max(i for (i, j) in S)
    l2 = max(j for (i, j) in S)
    from math import gcd
    W = 2
    while gcd(a0, W) != 1:
        W += 1
    Xb = X
    while gcd(a0, Xb) != 1:
        Xb += 1
    Yb = Y
    while gcd(a0, Yb) != 1:
        Yb += 1
    R = W * (Xb ** l1) * (Yb ** l2)
    cinv = pow(a0 % R, -1, R)
    f_ = {ij: (cinv * c) % R for ij, c in fS.items() if (cinv * c) % R}
    # shifts
    shifts = []
    monos = set()
    for s in S:
        g = pmul2(f_, {s: 1})
        g = {ij: c * (Xb ** (l1 - s[0])) * (Yb ** (l2 - s[1])) for ij, c in g.items()}
        shifts.append(g)
        monos.update(g.keys())
    for mm in M:
        if mm not in S:
            g = {mm: R}
            shifts.append(g)
            monos.add(mm)
    monos = sorted(monos)
    idx = {mn: q for q, mn in enumerate(monos)}
    rows = []
    for g in shifts:
        rows.append([(c * (Xb ** i) * (Yb ** j) if (c * (Xb ** i) * (Yb ** j)) else 0)
                     for (i, j), c in g.items()])
    Mm = IntegerMatrix(len(rows), len(monos))
    for ri, g in enumerate(shifts):
        for (i, j), c in g.items():
            Mm[ri, idx[(i, j)]] = c * (Xb ** i) * (Yb ** j)
    if time_limit and time.time() - t0 > time_limit:
        return {"error": "timeout-build"}
    LLL.reduction(Mm)
    w = len(monos)
    R2 = R * R
    useful = []
    hg_pass = 0
    min_scaled_log2 = None
    for ri in range(Mm.nrows):
        num = 0        # norm^2 over SCALED entries (reference semantics)
        nz = 0
        cs = {}
        for ci in range(w):
            v = int(Mm[ri, ci])
            if v == 0:
                continue
            nz += 1
            num += v * v
            cs[monos[ci]] = v
        if nz == 0:
            continue
        lg = math.log2(num)
        if min_scaled_log2 is None or lg < min_scaled_log2:
            min_scaled_log2 = lg
        if num * nz >= R2:
            continue
        g = {}
        ok = True
        for (i, j), v in cs.items():
            sc = (Xb ** i) * (Yb ** j)
            if v % sc != 0:
                ok = False
                break
            g[(i, j)] = v // sc
        if not ok:
            continue
        hg_pass += 1
        useful.append(g)
    res = {"shape": (m, strategy, t), "dim": (Mm.nrows, w), "hg_pass": hg_pass,
           "l": (l1, l2), "R_bits": math.log2(R), "found": None,
           "min_scaled_log2": min_scaled_log2, "n_useful": len(useful)}
    # root extraction: Res_v(f_, g) for each HG-passing g not divisible by f
    for g in useful:
        if div_exact_f(g, {ij: Fraction(c) for ij, c in f_.items()}):
            continue
        R1 = resultant_y_v({ij: Fraction(c) for ij, c in f_.items()}, g)
        for u0 in _guard_roots(R1):
            p_c = p0 + u0
            if p_c > 1:
                D = p_c * (p_c * p_c + p_c + 1)
                if D > 1 and N % D == 0:
                    res["found"] = p_c
                    return res
    return res

# reuse helpers from js_small_roots
from js_small_roots import div_exact_f, rat_roots

def resultant_y_v(fS, g):
    # fS = A(z) w + B(z), w = v; Res = sum_j g_j (-B)^j A^{dg-j}; Fractions fine
    fA, fB = {}, {}
    for (i, j), c in fS.items():
        if j == 1: fA[i] = fA.get(i, 0) + c
        elif j == 0: fB[i] = fB.get(i, 0) + c
        else: raise ValueError("not v-linear")
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

if __name__ == "__main__":
    from js_small_roots import make_toy, toy_params, load_real
    mode = sys.argv[1] if len(sys.argv) > 1 else "toys"
    def run(tag, Lp, Lr, shapes):
        p, q, r = make_toy(Lp, Lr)
        N = p * q * r
        p0, X, r0, Y = toy_params(p, r)
        print(f"[{tag} {Lp}/{2*Lp}/{Lr}] N={N.bit_length()}b log2(XY)={math.log2(X*Y):.1f} "
              f"th~N^0.5={math.log2(N)/2:.1f}", flush=True)
        for shp in shapes:
            t0 = time.time()
            try:
                res = integer_multivariate(N, p0, r0, X, Y, shp[0], shp[1] if len(shp) > 1 else "basic",
                                           shp[2] if len(shp) > 2 else (0, 0), time_limit=280)
            except Exception as ex:
                print(f"  {shp} EXC {ex}", flush=True); continue
            print(f"  {shp} dim={res.get('dim')} hgp={res.get('hg_pass')} R={res.get('R_bits')} "
                  f"found={res.get('found')} {time.time()-t0:.1f}s", flush=True)
            if res.get("found") == p:
                print("  -> SOLVED (control OK)", flush=True)
                return True
        return False
    if mode == "toys":
        ok = run("JM basic", 40, 30, [(2,), (3,), (4,), (5,), (6,)])
        ok = run("JM ext", 40, 30, [(2, "ext", (1, 1)), (3, "ext", (1, 1)), (3, "ext", (2, 1))]) or ok
        print("VALIDATION:", "PASS" if ok else "FAIL", flush=True)
    elif mode == "realratio":
        run("JM real-ratios", 60, 180, [(2,), (3,), (4,), (3, "ext", (1, 1))])
    elif mode == "real":
        n, e, c = load_real()
        p0 = 2 ** 511 + 2 ** 510; X = 2 ** 509
        r0 = 2 ** 1535 + 2 ** 1534; Y = 2 ** 1534
        print(f"n={n.bit_length()}b log2(XY)={math.log2(X*Y):.1f}", flush=True)
        for shp in [(2,), (3,), (4,), (5,), (3, "ext", (1, 1)), (2, "ext", (2, 1))]:
            t0 = time.time()
            try:
                res = integer_multivariate(n, p0, r0, X, Y, shp[0], shp[1] if len(shp) > 1 else "basic",
                                           shp[2] if len(shp) > 2 else (0, 0), time_limit=300)
            except Exception as ex:
                print(f"  {shp} EXC {ex}", flush=True); continue
            print(f"  {shp} dim={res.get('dim')} hgp={res.get('hg_pass')} R_bits={res.get('R_bits')} "
                  f"minScaled2log2={res.get('min_scaled_log2')} HGneed<{2*(res.get('R_bits') or 0):.0f} "
                  f"nuseful={res.get('n_useful')} found={res.get('found')} {time.time()-t0:.1f}s", flush=True)

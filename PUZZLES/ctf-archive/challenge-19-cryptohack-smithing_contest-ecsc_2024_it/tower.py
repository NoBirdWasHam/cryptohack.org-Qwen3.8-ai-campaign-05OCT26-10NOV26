# Tower + ate pairing replicating challenge Sage setup (pure python + gmpy2).
# Fp2 = Fp[a]/(a^2 - g2); Fp6 = Fp2[w]/(w^3-eps); Fp12 = Fp6[z]/(z^2-w); w=z^2, z^6=eps.
import gmpy2, hashlib
_ginv = gmpy2.invert
_iroot = gmpy2.iroot
# gmpy2 has NO mulmod/addmod/submod -- plain % n arithmetic:
def _mm(a, b, n): return (a * b) % n
def _am(a, b, n): return (a + b) % n
def _sm(a, b, n): return (a - b) % n

P    = 239019556058548081539763731767358519973
PRIME = P
B11  = 11
G1   = (1, 133660577740454676305948404600566797994)
EPSA = 50853858759521010453592688907791911225
EPSB = 156893423039651253351316307339945502422
G2X  = (218728496724280042701446122970647661523, 100774561144590475569157120930767342387)
G2Y  = (211093354487559124632805793736258741445, 115367896606755692925113233629944781384)

def _iroot4(n):
    x = int(n ** 0.25)
    while (x + 1) ** 4 <= n: x += 1
    while x ** 4 > n: x -= 1
    return x
UU = _iroot4(P // 36)
while 36*UU**4 - 36*UU**3 + 24*UU**2 - 6*UU + 1 > P: UU -= 1
while 36*(UU+1)**4 - 36*(UU+1)**3 + 24*(UU+1)**2 - 6*(UU+1) + 1 <= P: UU += 1
assert 36*UU**4 - 36*UU**3 + 24*UU**2 - 6*UU + 1 == P, "P not BN minus-form prime"
T_TRACE = 6*UU*UU + 1
N = P + 1 - T_TRACE
assert gmpy2.is_prime(N)
# true #E'(Fp2) for the order-6 twist over Fp2: trace = (t2 + sqrt(3(4p^2-t2^2)))/2
_h_tau = (T_TRACE*T_TRACE - 2*P + int(gmpy2.isqrt(3*(4*P*P - (T_TRACE*T_TRACE-2*P)**2)))) // 2
H2 = (P*P + 1 - _h_tau) // N  # true cofactor (scalar mod #E' -- do NOT reduce mod P)

# ---------------- Fp2 ----------------
T2, N2 = P-1, 1   # a^2 = T2*a + N2  i.e. a^2 + a - 1 = 0 (only model where G2 on-curve & n*G2=O)
CHI = 1
F20 = (0, 0); F21 = (1, 0)
def f2(a0, a1=0): return (a0 % P, a1 % P)
def f2add(x, y): return (_am(x[0], y[0], P), _am(x[1], y[1], P))
def f2sub(x, y): return (_sm(x[0], y[0], P), _sm(x[1], y[1], P))
def f2neg(x): return ((P - x[0]) % P, (P - x[1]) % P)
def f2mul(x, y):
    a, b = x; c, d = y
    return ((_mm(a, c, P) + _mm(_mm(b, d, P), N2, P)) % P, (_mm(a, d, P) + _mm(b, c, P) + _mm(_mm(b, d, P), T2, P)) % P)
def f2sq(x): return f2mul(x, x)
def f2inv(x):
    a, b = x
    d = int(_ginv((_mm(a, a, P) + _mm(_mm(a, b, P), T2, P) - _mm(_mm(b, b, P), N2, P)) % P, P))
    return (_mm(_am(a, _mm(b, T2, P), P), d, P), (P - _mm(b, d, P)) % P)
def f2mulk(x, k):
    k %= P
    return (_mm(x[0], k, P), _mm(x[1], k, P))
def f2zero(x): return x[0] == 0 and x[1] == 0
def f2pow(x, e):
    r = F21
    for bit in bin(e)[2:]:
        r = f2sq(r)
        if bit == '1': r = f2mul(r, x)
    return r
EPS = None; C2 = None

# ---------------- E(Fp2): y^2 = x^3 + C2 (= 11/eps) ----------------
def e2_double(T):
    x, y = T
    lam = f2mul(f2mulk(f2sq(x), 3), f2inv(f2mulk(y, 2)))
    x3 = f2sub(f2sq(lam), f2mulk(x, 2))
    return (x3, f2sub(f2mul(f2sub(x, x3), lam), y))
def e2_add(T, S):
    if T is None: return S
    if S is None: return T
    x1, y1 = T; x2, y2 = S
    if x1 == x2:
        if f2zero(f2add(y1, y2)): return None
        return e2_double(T)
    lam = f2mul(f2sub(y2, y1), f2inv(f2sub(x2, x1)))
    x3 = f2sub(f2sub(f2sq(lam), x1), x2)
    return (x3, f2sub(f2mul(f2sub(x1, x3), lam), y1))
def e2_mul(k, T):
    if k == 0: return None
    if k < 0: return e2_mul(-k, (T[0], f2neg(T[1])))
    R = None
    for bit in bin(k)[2:]:
        if R is not None: R = e2_add(R, R)
        if bit == '1': R = T if R is None else e2_add(R, T)
    return R
def e2_neg(T): return None if T is None else (T[0], f2neg(T[1]))
def e2_oncurve(T): return f2eqv(f2sq(T[1]), f2add(f2mul(f2sq(T[0]), T[0]), C2))
def f2eqv(x, y): return x[0] == y[0] and x[1] == y[1]
def fp_sqrt(a):
    # Tonelli-Shanks mod P (P % 4 == 1 here); None if non-residue
    a %= P
    if a == 0: return 0
    if pow(a, (P - 1) // 2, P) != 1: return None
    if P % 4 == 3: return int(pow(a, (P + 1) // 4, P))
    q = P - 1; s = 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (P - 1) // 2, P) != P - 1: z += 1
    m, c, t, r = s, pow(z, q, P), pow(a, q, P), pow(a, (q + 1) // 2, P)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % P; i += 1
            if i == m: return None
        b = pow(c, 1 << (m - i - 1), P)
        m, c, t, r = i, b * b % P, t * b * b % P, r * b % P
    return int(r)

def f2sqrt(x):
    # general basis a^2=T2 a+N2: solve (c+d a)^2 = r. d=0 branch + quadratic in W=d^2:
    # (T2^2+4N2) W^2 + (-2 T2 r1 - 4 r0) W + r1^2 = 0 ; c = (r1 - T2 W)/(2d)
    r0, r1 = x
    if r0 == 0 and r1 == 0: return [(0, 0)]
    out = []
    if r1 == 0:
        c = fp_sqrt(r0)
        if c is not None: out += [(c, 0), ((P - c) % P, 0)]
    Aq = (T2*T2 + 4*N2) % P
    Bq = (-2*T2*r1 - 4*r0) % P
    Cq = _mm(r1, r1, P)
    s = fp_sqrt(_sm(_mm(Bq, Bq, P), _mm(_mm(4, Aq, P), Cq, P), P))
    if s is not None:
        inv2A = int(_ginv(_mm(2, Aq, P), P))
        for sq in {s % P, (-s) % P}:
            W = _am(_sm(0, Bq, P), sq, P) * inv2A % P
            w = fp_sqrt(W)
            if w is None: continue
            for d in {w % P, (-w) % P} if w else set():
                c = _mm(_sm(r1, _mm(T2, W, P), P), int(_ginv(_mm(2, d, P), P)), P)
                root = (c, d)
                if f2eqv(f2sq(root), x) and root not in out: out.append(root)
    return out

def e2_lift_xs(x0):
    # all points on E(Fp2) with x=x0 (x0 an Fp element embedded)
    rhs = f2add(f2mul(f2mul((x0 % P, 0), (x0 % P, 0)), (x0 % P, 0)), C2)
    return [((x0 % P, 0), r) for r in f2sqrt(rhs)]

def H0(uid, flip=False):
    # replicate challenge PKG.H0: iterate x0, lift_x on E(Fp2), cofactor mult
    # flip=True picks the opposite y-root (sage lift_x root-choice calibration)
    x0 = int.from_bytes(hashlib.sha256(uid.encode()).digest(), 'big') % P
    tried = 0
    while True:
        x0 += 1
        tried += 1
        if tried > 100000:
            raise RuntimeError('H0: no lift after %d tries' % tried)
        lps = e2_lift_xs(x0)
        if not lps: continue
        lp = sorted(lps, key=lambda T: (T[1][0], T[1][1]))[-1 if flip else 0]
        Pp = e2_mul(H2, lp)
        if Pp is not None and e2_mul(N, Pp) is None:
            return Pp
def Hm(msg_bytes):
    # server H(): sha256(x).digest()[:curve.bytes] where bytes=ceil(128/8)=16
    return int.from_bytes(hashlib.sha256(msg_bytes).digest()[:16], 'big') % N

# ---------------- E(Fp) helpers ----------------
def e1_double(T):
    x, y = T
    lam = _mm(3, _mm(x, x, P), P) * int(_ginv(_am(_mm(2, y, P), 0, P), P)) % P
    lam = _mm(_mm(3, _mm(x, x, P), P), int(_ginv(_mm(2, y, P), P)), P)
    x3 = _sm(_mm(lam, lam, P), _am(x, x, P), P)
    return (x3, _sm(_mm(lam, _sm(x, x3, P), P), y, P))
def e1_add(T, S):
    if T is None: return S
    if S is None: return T
    x1, y1 = T; x2, y2 = S
    if x1 == x2:
        if (y1 + y2) % P == 0: return None
        return e1_double(T)
    lam = _mm(_sm(y2, y1, P), int(_ginv(_sm(x2, x1, P), P)), P)
    x3 = _sm(_sm(_mm(lam, lam, P), x1, P), x2, P)
    return (x3, _sm(_mm(lam, _sm(x1, x3, P), P), y1, P))
def e1_mul(k, T):
    if k == 0: return None
    if k < 0: return e1_mul(-k, (T[0], (P - T[1]) % P))
    R = None
    for bit in bin(k)[2:]:
        if R is not None: R = e1_add(R, R)
        if bit == '1': R = T if R is None else e1_add(R, T)
    return R
def e1_oncurve(T): return (T[1]*T[1] - T[0]**3 - B11) % P == 0

# ---------------- Fp6 / Fp12 ----------------
F60 = (F20, F20, F20); F61 = (F21, F20, F20)
def f6mul(x, y):
    x0, x1, x2 = x; y0, y1, y2 = y
    v0 = f2mul(x0, y0); v1 = f2mul(x1, y1); v2 = f2mul(x2, y2)
    c0 = f2add(v0, f2mul(EPS, f2sub(f2mul(f2add(x1, x2), f2add(y1, y2)), f2add(v1, v2))))
    c1 = f2add(f2sub(f2mul(f2add(x0, x1), f2add(y0, y1)), f2add(v0, v1)), f2mul(EPS, v2))
    c2 = f2add(f2sub(f2sub(f2mul(f2add(x0, x2), f2add(y0, y2)), v0), v2), v1)
    return (c0, c1, c2)
def f6add(x, y): return (f2add(x[0], y[0]), f2add(x[1], y[1]), f2add(x[2], y[2]))
def f6sub(x, y): return (f2sub(x[0], y[0]), f2sub(x[1], y[1]), f2sub(x[2], y[2]))
def f6mulw(x):
    c0, c1, c2 = x
    return (f2mul(EPS, c2), c0, c1)
def f6inv(x):
    a0, a1, a2 = x
    m00, m01, m02 = a0, f2mul(EPS, a2), f2mul(EPS, a1)
    m10, m11, m12 = a1, a0, f2mul(EPS, a2)
    m20, m21, m22 = a2, a1, a0
    A = f2sub(f2mul(m11, m22), f2mul(m12, m21))
    B = f2sub(f2mul(m10, m22), f2mul(m12, m20))
    Cc = f2sub(f2mul(m10, m21), f2mul(m11, m20))
    d = f2add(f2sub(f2mul(m00, A), f2mul(m01, B)), f2mul(m02, Cc))
    di = f2inv(d)
    return (f2mul(A, di), f2neg(f2mul(B, di)), f2mul(Cc, di))
F120 = (F60, F60); F121 = (F61, F60)
def f12mul(x, y):
    a0, a1 = x; b0, b1 = y
    v0 = f6mul(a0, b0); v1 = f6mul(a1, b1)
    c0 = f6add(v0, f6mulw(v1))
    c1 = f6sub(f6mul(f6add(a0, a1), f6add(b0, b1)), f6add(v0, v1))
    return (c0, c1)
def f12sq(x): return f12mul(x, x)
def f12add(x, y): return (f6add(x[0], y[0]), f6add(x[1], y[1]))
def f12sub(x, y): return (f6sub(x[0], y[0]), f6sub(x[1], y[1]))
def f12neg(x): return (f6sub(F60, x[0]), f6sub(F60, x[1]))
def f12inv(x):
    n = f6sub(f6mul(x[0], x[0]), f6mulw(f6mul(x[1], x[1])))
    ni = f6inv(n)
    return (f6mul(x[0], ni), f6sub(F60, f6mul(x[1], ni)))
def f12eq(x, y): return x == y
def f12mulf2(x, c): return (tuple(f2mul(a, c) for a in x[0]), tuple(f2mul(a, c) for a in x[1]))
def f12fromf2(c): return ((c, F20, F20), F60)
def f12fromi(k): return f12fromf2(f2(k % P))
def f12_pow(x, e):
    r = F121
    for bit in bin(e)[2:]:
        r = f12sq(r)
        if bit == '1': r = f12mul(r, x)
    return r
def f12_basis(x):
    (a0, a1, a2), (b0, b1, b2) = x
    return [a0, b0, a1, b1, a2, b2]
def _f12_from_basis(b): return ((b[0], b[2], b[4]), (b[1], b[3], b[5]))
def _f2_powp(c, k):
    if k % 2 == 0: return c
    return ((_am(c[0], _mm(c[1], T2, P), P)) % P, (P - c[1]) % P)   # conj: a -> T2 - a
MBASE = None; LAM = None
def frob_setup():
    global LAM, MBASE
    z = (F60, F61)
    zp = f12_pow(z, P)
    b = f12_basis(zp)
    assert b[0] == F20 and b[2] == F20 and b[3] == F20 and b[4] == F20 and b[5] == F20, "tower mismatch: z^p not lam*z"
    LAM = b[1]
    # (w^a z^b)^{p^k} = D_k^(2a+b) * w^a z^b  with D_k = prod_{i<k} conj^i(LAM)
    D = [F21] * 7
    D[1] = LAM
    for k in range(2, 7):
        D[k] = f2mul(D[k - 1], _f2_powp(LAM, k - 1))
    MBASE = []
    for k in range(1, 7):
        row = [F21]
        for j in range(1, 6):
            row.append(f2mul(row[-1], D[k]))
        MBASE.append(row)
def f12_powp(x, k):
    b = f12_basis(x)
    row = MBASE[k - 1]
    return _f12_from_basis([f2mul(_f2_powp(b[j], k), row[j]) for j in range(6)])

# ---------------- pairing ----------------
def phi(Q):
    qx, qy = Q
    X = ((F20, qx, F20), F60)      # z^2 * qx
    Y = (F60, (F20, qy, F20))      # z^3 * qy
    return (X, Y)
def d12_double(T):
    xt, yt = T
    lam = f12mul(f12mulf2(f12sq((xt, F60)) if False else (xt, F60), F21) if False else (xt, F60), F60)
    raise RuntimeError
def _dbl(T):
    xt, yt = T
    lam = f12mul(f12mul(f12fromi(3), f12sq(xt)), f12inv(f12mul(f12fromi(2), yt)))
    x3 = f12sub(f12sq(lam), f12add(xt, xt))
    y3 = f12sub(f12mul(f12sub(xt, x3), lam), yt)
    return (x3, y3), lam
def _add(T, S):
    xt, yt = T; xs, ys = S
    lam = f12mul(f12sub(ys, yt), f12inv(f12sub(xs, xt)))
    x3 = f12sub(f12sub(f12sq(lam), xt), xs)
    y3 = f12sub(f12mul(f12sub(xt, x3), lam), yt)
    return (x3, y3), lam
def miller(Ql, Peval, s):
    # value at Peval of f_{s,Ql}; loop doubles Ql (sage: Q._miller_(P, T))
    xq, yq = Peval
    f = F121
    T = Ql
    for bit in bin(s)[3:]:
        T2, lam = _dbl(T)
        lnum = f12sub(f12sub(yq, T[1]), f12mul(lam, f12sub(xq, T[0])))
        f = f12mul(f12sq(f), f12mul(lnum, f12inv(f12sub(xq, T2[0]))))
        T = T2
        if bit == '1':
            T2, lam = _add(T, Ql)
            lnum = f12sub(f12sub(yq, T[1]), f12mul(lam, f12sub(xq, T[0])))
            f = f12mul(f, f12mul(lnum, f12inv(f12sub(xq, T2[0]))))
            T = T2
    return f
def ate(P, Q):
    f = miller(phi(Q), (f12fromi(P[0]), f12fromi(P[1])), T_TRACE - 1)
    w1 = f12mul(f12_powp(f, 6), f12inv(f))
    w2 = f12mul(f12_powp(w1, 2), w1)
    return f12_pow(w2, (PRIME**4 - PRIME**2 + 1) // N)

# ---------------- init ----------------
def discover():
    global EPS, C2
    EPS = (EPSB, EPSA)
    C2 = f2mulk(f2inv(EPS), B11)
    assert e2_oncurve((G2X, G2Y)), "G2 not on curve in fixed model"
    frob_setup()

if __name__ == "__main__":
    import time
    discover()
    print("model a^2=-a+1  u =", UU, " N prime ok")
    print("n*G1==O:", e1_mul(N, G1) is None)
    print("n*G2==O:", e2_mul(N, (G2X, G2Y)) is None)
    frob_setup()
    zz = (F60, F61)
    assert f12_pow(zz, P) == f12_powp(zz, 1)
    assert f12_pow(zz, P*P) == f12_powp(zz, 2)
    print("frob ok")
    t0 = time.time()
    gT = ate(G1, (G2X, G2Y))
    print("ate time %.1fs" % (time.time() - t0))
    print("gT!=1:", not f12eq(gT, F121))
    print("gT^n==1:", f12eq(f12_pow(gT, N), F121))
    a = 0xdeadbeefcafe1234
    lhs = ate(e1_mul(a, G1), (G2X, G2Y))
    rhs = f12_pow(gT, a)
    print("bilinear1:", f12eq(lhs, rhs))
    b = 0xfeedface5
    lhs2 = ate(G1, e2_mul(b, (G2X, G2Y)))
    print("bilinear2:", f12eq(lhs2, f12_pow(gT, b)))
    qa = H0('admin'); qb = H0('smithy')
    print("H0 ok:", qa != qb, e2_mul(N, qa) is None, e2_mul(N, qb) is None)
    print("total %.1fs" % (time.time() - t0))

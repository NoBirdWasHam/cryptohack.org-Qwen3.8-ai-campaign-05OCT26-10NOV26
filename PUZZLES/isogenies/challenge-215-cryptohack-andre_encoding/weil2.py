# Weil pairing e_n(P,Q) over F_{p^2}=F_p[i]/(i^2+1), Miller's algorithm.
# e_n(P,Q) = f_P((Q+R)-(R)) / f_Q((P+R)-(R)), R random, nP=nQ=O.
import sys, random

def load_params():
    txt = open("params.gp").read()
    d = {}
    for line in txt.splitlines():
        line = line.strip().rstrip(";")
        if "=" in line and not line.startswith("//"):
            k, v = line.split("=", 1)
            v = v.strip()
            if v.isdigit():
                d[k.strip()] = int(v)
    return d

P = load_params()["PVAL"]
A2 = P * P

# Fp2 elements as (re, im): value = re + im*i, i^2 = -1
def f2inv(z):
    a, b = z
    den = pow(a * a + b * b, -1, P)
    return (a * den % P, (-b) * den % P)

def f2mul(z, w):
    a, b = z; c, d = w
    return ((a * c - b * d) % P, (a * d + b * c) % P)

def f2sqr(z): return f2mul(z, z)
def f2add(z, w): return ((z[0] + w[0]) % P, (z[1] + w[1]) % P)
def f2sub(z, w): return ((z[0] - w[0]) % P, (z[1] - w[1]) % P)
def f2neg(z): return ((-z[0]) % P, (-z[1]) % P)
def f2eq(z, w): return z[0] == w[0] and z[1] == w[1]
def f2pow(z, e):
    r = (1, 0)
    while e:
        if e & 1: r = f2mul(r, z)
        z = f2sqr(z); e >>= 1
    return r

# curve y^2 = x^3 + a4 x + a6 over Fp2; point None = O
def add(Eq, Pp, Qp):
    a4 = Eq
    if Pp is None: return Qp
    if Qp is None: return Pp
    x1, y1 = Pp; x2, y2 = Qp
    if f2eq(x1, x2):
        if f2eq(y1, f2neg(y2)): return None
        lam = f2mul(f2add(f2mul((3, 0), f2mul(x1, x1)), (Eq[0], Eq[1])), f2inv(f2mul((2, 0), y1)))
    else:
        lam = f2mul(f2sub(y1, y2), f2inv(f2sub(x1, x2)))
    x3 = f2sub(f2sub(f2sqr(lam), x1), x2)
    y3 = f2sub(f2mul(lam, f2sub(x1, x3)), y1)
    return (x3, y3)

def line_val(Pp, Qp, S):
    # value at S of line through Pp,Qp (tangent if equal); vertical handled by caller
    x1, y1 = Pp; x2, y2 = Qp
    if f2eq(x1, x2):
        if f2eq(y1, f2neg(y2)):
            # vertical line x - x1
            return f2sub(S[0], x1)
        lam = f2mul(f2add(f2mul((3, 0), f2mul(x1, x1)), (CURVE_A4[0], CURVE_A4[1])), f2inv(f2mul((2, 0), y1)))
        nu = f2sub(y1, f2mul(lam, x1))
        return f2sub(f2sub(S[1], f2mul(lam, S[0])), nu)
    lam = f2mul(f2sub(y1, y2), f2inv(f2sub(x1, x2)))
    nu = f2sub(y1, f2mul(lam, x1))
    return f2sub(f2sub(S[1], f2mul(lam, S[0])), nu)

CURVE_A4 = None

def miller_eval(Eq, Pp, n, S1, S2):
    """f_{P,n} evaluated at divisor (S1)-(S2); nP=O. Returns f(S1)/f(S2)."""
    global CURVE_A4
    CURVE_A4 = Eq
    fnum, fden = (1, 0), (1, 0)
    T = None
    bits = bin(n)[2:]
    for ch in bits:
        # double step: f <- f^2 * l_{T,T}/v_{2T}
        if T is not None:
            T2 = add(Eq, T, T)
            fnum = f2mul(f2sqr(fnum), line_val(T, T, S1)); fden = f2mul(f2sqr(fden), line_val(T, T, S2))
            if T2 is not None:
                fnum = f2mul(fnum, f2sub(S2[0], T2[0])); fden = f2mul(fden, f2sub(S1[0], T2[0]))
            T = T2
        if ch == '1':
            if T is None:
                T = Pp
            else:
                TP = add(Eq, T, Pp)
                fnum = f2mul(fnum, line_val(T, Pp, S1)); fden = f2mul(fden, line_val(T, Pp, S2))
                if TP is not None:
                    fnum = f2mul(fnum, f2sub(S2[0], TP[0])); fden = f2mul(fden, f2sub(S1[0], TP[0]))
                T = TP
    return f2mul(fnum, f2inv(fden))

def weil(Eq, Pp, Qp, n, rng):
    global CURVE_A4
    CURVE_A4 = Eq
    while True:
        Rx = (rng.randrange(P), rng.randrange(P))
        rhs = f2add(f2add(f2pow(Rx, 3), f2mul(Eq, Rx)), (1, 0))
        # need sqrt in Fp2: try random squares via norm trick; simpler: pick R = [k]Qp-ish fallback
        # Instead: build R by adding random multiples of Pp,Qp and a known point.
        break
    # build R as [r1]Pp + [r2]Qp + [r3]G where G = B (passed via globals)
    G = GLOBAL_G
    for _ in range(40):
        r1, r2, r3 = rng.randrange(1, n), rng.randrange(1, n), rng.randrange(1, n)
        R = add(Eq, add(Eq, mul(Eq, Pp, r1), mul(Eq, Qp, r2)), mul(Eq, G, r3))
        if R is None: continue
        QpR = add(Eq, Qp, R); PpR = add(Eq, Pp, R)
        if QpR is None or PpR is None: continue
        try:
            num = miller_eval(Eq, Pp, n, QpR, R)
            den = miller_eval(Eq, Qp, n, PpR, R)
            val = f2mul(num, f2inv(den))
        except ValueError:
            continue
        # Weil pairing value must satisfy val^n == 1; sanity check
        if f2eq(f2pow(val, n), (1, 0)):
            return val
        # else retry with new R (bad R hitting support)
    return None

def mul(Eq, Pp, k):
    R = None; Q = Pp
    while k:
        if k & 1: R = add(Eq, R, Q)
        Q = add(Eq, Q, Q); k >>= 1
    return R

def main():
    import json
    ct = json.load(open("output.txt"))
    prm = load_params()
    PVAL = prm["PVAL"]; LVAL = prm["LVAL"]
    rng = random.Random(12345)
    out = []
    for idx, e in enumerate(ct):
        Ax = tuple(e["P"]["x"]); Ay = tuple(e["P"]["y"])
        Bx = tuple(e["Q"]["x"]); By = tuple(e["Q"]["y"])
        RA = f2sub(f2sqr(Ay), f2pow(Ax, 3)); RB = f2sub(f2sqr(By), f2pow(Bx, 3))
        a4 = f2mul(f2sub(RA, RB), f2inv(f2sub(Ax, Bx)))
        A = (Ax, Ay); B = (Bx, By)
        global GLOBAL_G
        GLOBAL_G = B
        U = 37 * LVAL * (PVAL + 1)
        while U % 2 == 0: U //= 2
        v2 = 0
        for k in range(7, 0, -1):
            sc = U * 2 ** (71 - k)
            Xk = mul(a4, A, sc); Yk = mul(a4, B, sc)
            if Xk is None:
                v2 = k; break
            w = weil(a4, Xk, Yk, 2 ** k, rng)
            if w is not None and f2eq(w, (1, 0)):
                v2 = k; break
        out.append(v2)
        print(f"byte {idx+1}: v2={v2}", flush=True)
    json.dump(out, open("v2out.json", "w"))

GLOBAL_G = None
if __name__ == "__main__":
    main()

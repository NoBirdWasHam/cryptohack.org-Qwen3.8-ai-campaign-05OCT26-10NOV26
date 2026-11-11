# Bivariate Coppersmith over Z for f(x,y) = (x^2+x+1)*y - n, root (p, r).
# Region: layers k=0..m, multipliers x^i y^j with 2*(i+2j) <= S*(m-k).
# Validation on same-ratio toy (60/120/180 -> N~360 bits).
import sys
from fpylll import IntegerMatrix, LLL
import sympy

x, y = sympy.symbols('x y')

def make_toy():
    from Crypto.Util.number import getPrime, isPrime
    while True:
        p = getPrime(60)
        q = p*p + p + 1
        if isPrime(q): return p, q, getPrime(180)

def region(m, S):
    gens = []
    for k in range(m+1):
        for j in range(m-k+1):
            for i in range(m-k+1):
                if 2*(i + 2*j) <= S*(m-k):
                    gens.append((k,i,j))
    return gens

def fpow_coeffs(k, i, j, N, m):
    # f^k = (h(x)*y - N)^k = sum_l C(k,l) h(x)^l y^l (-N)^(k-l)
    hpow = [{0:1}]
    for _ in range(k):
        prev = hpow[-1]; na = {}
        for a,ca in prev.items():
            for e in range(3):
                na[a+e] = na.get(a+e,0) + ca
        hpow.append(na)
    from math import comb
    Ns = pow(N, m-k)
    d = {}
    for l in range(k+1):
        cl = comb(k,l) * pow(-N, k-l)
        if not cl: continue
        for a,ca in hpow[l].items():
            key = (a+i, j+l)
            d[key] = d.get(key,0) + ca*cl*Ns
    return d, i, j

def poly_div_f(g, N):
    """g dict (a,b)->coeff. f=(x^2+x+1)y-N. Return quotient if g is multiple of f, else None."""
    deg = max(b for b in g)
    gs = {}
    for (a,b),c in g.items(): gs.setdefault(b, {})[a] = c
    q = {}
    prev = None
    for deg2 in range(deg, -1, -1):
        gd = {a:c for a,c in gs.get(deg2, {}).items() if c}
        if deg2 == deg:
            rem = dict(gd); b = {}
            for a in sorted(rem, reverse=True):
                if rem[a]:
                    d = a-2
                    b[d] = rem[a]
                    for e in range(3): rem[d+e] = rem.get(d+e,0) - b[d]
                    rem[a] = 0
            if any(rem.values()): return None
            prev = b
            for a,c in b.items():
                if c: q[(a, deg2-1)] = c
        else:
            t = {}
            for a,c in prev.items():
                for e in range(3): t[a+e] = t.get(a+e,0) + c
            for a,c in gd.items(): t[a] = t.get(a,0) - c
            b2 = {}
            for a,c in t.items():
                if c % N: return None
                if c//N: b2[a] = c//N
            prev = b2
            for a,c in b2.items(): q[(a,deg2-1)] = c
    g0 = {a:c for a,c in gs.get(0, {}).items() if c}
    t = {}
    for a,c in prev.items():
        for e in range(3): t[a+e] = t.get(a+e,0) + c
    if t != g0: return None
    return q

def resultant_f_g(g, N):
    G = sum(c*x**a*y**b for (a,b),c in g.items())
    f = (x**2+x+1)*y - N
    return sympy.resultant(sympy.expand(f), sympy.expand(G), y)

def run(N, X, Y, root, m, S):
    gens = region(m, S)
    rowd = []
    for (k,i,j) in gens:
        d,_,_ = fpow_coeffs(k,i,j,N,m)
        rowd.append({kk:c for kk,c in d.items() if c})
    mons = sorted({mm for d in rowd for mm in d})
    t, ncols = len(rowd), len(mons)
    if t > ncols: return dict(status="fat", t=t, ncols=ncols)
    idx = {mm:i for i,mm in enumerate(mons)}
    A = IntegerMatrix(t, ncols)
    for ri,d in enumerate(rowd):
        for (a,b),c in d.items():
            A[ri, idx[(a,b)]] = c * pow(X,a) * pow(Y,b)
    LLL.reduction(A)
    px, ry = root
    found = []
    for ri in range(t):
        coeffs = {}; ok = True
        for ci in range(ncols):
            v = int(A[ri,ci])
            if v:
                (a,b) = mons[ci]; s = pow(X,a)*pow(Y,b)
                if v % s: ok=False; break
                coeffs[(a,b)] = v//s
        if not ok or not coeffs: continue
        val = sum(c*pow(px,a)*pow(ry,b) for (a,b),c in coeffs.items())
        if val != 0: continue
        if poly_div_f(coeffs, N) is not None: continue
        P = resultant_f_g(coeffs, N)
        if P == 0: continue
        Pv = P.subs(x, px)
        found.append(ri)
        if Pv == 0:
            return dict(status="WON", m=m, S=S, t=t, ri=ri, deg=len(coeffs))
    return dict(status="none", m=m, S=S, t=t, ncols=ncols, zeros=len(found))

if __name__ == "__main__":
    p,q,r = make_toy()
    N = p*q*r
    print("toy bits", p.bit_length(), q.bit_length(), r.bit_length(), flush=True)
    X, Y = 2**60, 2**180
    for S in (2,3,4):
        for m in (3,4,5,6,7,8):
            res = run(N, X, Y, (p,r), m, S)
            print(S, m, res, flush=True)
            if res.get("status")=="WON": sys.exit(0)

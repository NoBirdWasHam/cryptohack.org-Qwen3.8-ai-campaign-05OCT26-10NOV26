# Bivariate Coppersmith over Z for f(x,y) = (x^2+x+1)*y - n, root (p,r).
# Shifted box: p = p0+x, r = r0+y with |x|<=X, |y|<=Y (widths).
# Region: (k,i,j): row scale N^(m-k)*(X^2Y)^k*X^i*Y^j <= N^m * 2^-T.
# Validated here on same-ratio toy (60/180), then used on real instance.
from fpylll import IntegerMatrix, LLL
from math import comb
import sys

def poly_mul(A, B):
    C = {}
    for (a,b),ca in A.items():
        if not ca: continue
        for (c,d),cb in B.items():
            if not cb: continue
            C[(a+c,b+d)] = C.get((a+c,b+d),0) + ca*cb
    return C

def poly_pow(base, k):
    out = {(0,0):1}
    for _ in range(k): out = poly_mul(out, base)
    return out

def build_rows(fshift, N, m, Xbits, Ybits, Lbits, T):
    # fshift: dict (a,b)->coeff of f in shifted vars
    rows = []
    for k in range(m+1):
        fp = poly_pow(fshift, k) if k else {(0,0):1}
        Nsk = pow(N, m-k)
        budget = (Lbits - 2*Xbits - Ybits)*k - T   # Xbits*i + Ybits*j <= budget
        for j in range(m+1):
            if Ybits*j > budget: break
            for i in range(m+1):
                if Xbits*i > budget - Ybits*j: break
                row = {}
                for (a,b),c in fp.items():
                    row[(a+i,b+j)] = c*Nsk
                rows.append(row)
    return rows

def lll_find(fshift, N, X, Y, root, rows):
    mons = sorted({mm for r in rows for mm in r})
    t, ncols = len(rows), len(mons)
    if t < 3: return None, "too few rows"
    idx = {mm:i for i,mm in enumerate(mons)}
    A = IntegerMatrix(t, ncols)
    for ri,d in enumerate(rows):
        for (a,b),c in d.items():
            A[ri, idx[(a,b)]] = c * pow(X,a) * pow(Y,b)
    LLL.reduction(A)
    (px, ry) = root
    Xbits = X.bit_length()-1 if X & (X-1)==0 else X.bit_length()
    def unscale(ri):
        g = {}; 
        for ci in range(ncols):
            v = int(A[ri,ci])
            if v:
                (a,b) = mons[ci]; s = pow(X,a)*pow(Y,b)
                if v % s: return None
                g[(a,b)] = v//s
        return g
    for ri in range(t):
        g = unscale(ri)
        if not g: continue
        val = sum(c*pow(px,a)*pow(ry,b) for (a,b),c in g.items())
        if val != 0: continue
        # not a multiple of f?
        P = resultant_y(fshift, g, N)
        if P is None or P == 0: continue
        return g, P
    return None, "no usable vector"

import sympy
SX, SY = sympy.symbols('x y')

def to_sympy(d, shiftx=0, shifty=0):
    G = sum(c*(SX+shiftx)**a*(SY+shifty)**b for (a,b),c in d.items())
    return sympy.expand(G)

def resultant_y(fshift, g, N):
    F = sum(c*SX**a*SY**b for (a,b),c in fshift.items())
    G = sum(c*SX**a*SY**b for (a,b),c in g.items())
    return sympy.resultant(sympy.expand(F), sympy.expand(G), SY)

def make_toy():
    from Crypto.Util.number import getPrime, isPrime
    while True:
        p = getPrime(60)
        if isPrime(p*p+p+1):
            r = getPrime(180)
            return p, p*p+p+1, r

def solve(p_, q_, r_):
    N = p_*q_*r_
    L = N.bit_length()
    # shifted box
    p0 = 3<< (p_.bit_length()-2) if p_.bit_length()>=2 else 1
    r0 = 3<< (r_.bit_length()-2)
    X = 1 << (p_.bit_length()-1)
    Y = 1 << (r_.bit_length()-1)
    # ensure roots inside box
    assert p_-p0 < X and r_-r0 < Y
    Xb, Yb = X.bit_length()-1, Y.bit_length()-1
    q0 = p0*p0+p0+1
    # f' = (x^2 + (2p0+1)x + q0)(y + r0) - N
    h2 = {(0,0): q0, (1,0): 2*p0+1, (2,0): 1}
    fshift = poly_mul(h2, {(0,0): r0, (0,1): 1})
    fshift[(0,0)] = fshift.get((0,0),0) - N
    for m in (4,5,6,8,10):
        for T in (30,15):
            rows = build_rows(fshift, N, m, Xb, Yb, L, T)
            g, res = lll_find(fshift, N, X, Y, (p_-p0, r_-r0), rows)
            print(f"m={m} T={T} rows={len(rows)} -> {res if g is None else 'USABLE'}", flush=True)
            if g is not None:
                # find integer root of P(x) in (-X, X): P(p-p0)=0
                P = res
                cand = []
                for rt in sympy.nroots(P, n=12, maxsteps=200):
                    if abs(rt.as_real_imag()[1]) > 1e-6: continue
                    xv = int(round(float(rt.as_real_imag()[0])))
                    cand.append(xv)
                for xv in set(cand):
                    pc = p0 + xv
                    if pc > 1 and N % pc == 0:
                        print("FOUND p =", pc)
                        return pc
                print("candidates:", cand)
    return None

if __name__ == "__main__":
    p,q,r = make_toy()
    print("toy", p.bit_length(), q.bit_length(), r.bit_length(), "p=", p, flush=True)
    got = solve(p,q,r)
    print("toy solved:", got == p)

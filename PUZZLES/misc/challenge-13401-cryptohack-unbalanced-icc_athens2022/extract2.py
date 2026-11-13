# Extract w0 (root, 0<=w<2^254) from two vanishing bivariate polys h1(u,w), h2(u,w):
# R(w) = resultant_u(h1,h2) over GF(l); factor -> linear roots; CRT over primes; verify p|N.
import sympy
from fractions import Fraction

def hmod(row, ell, X, Y):
    u, w = sympy.symbols('u w')
    expr = 0
    for (i, j), v in row.items():
        if not v:
            continue
        num = int((Fraction(v) * (1)).numerator)
        den = int((Fraction(v) * (1)).denominator)
        c = (num % ell) * pow(den % ell, -1, ell) % ell
        if c:
            expr += c * u**i * w**j
    return sympy.Poly(expr, u, w, domain=sympy.GF(ell))

def roots_for_prime(h1, h2, ell, X, Y):
    P1 = hmod(h1, ell, X, Y)
    P2 = hmod(h2, ell, X, Y)
    u = sympy.symbols('u')
    w = sympy.symbols('w')
    R = sympy.resultant(P1.as_expr(), P2.as_expr(), u)
    Rw = sympy.Poly(sympy.expand(R), w, domain=sympy.GF(ell))
    if Rw.is_zero:
        return None
    roots = set()
    fl = sympy.factor_list(Rw.as_expr(), modulus=ell)
    for fac, mult in fl[1]:
        Pf = sympy.Poly(fac, w, domain=sympy.GF(ell))
        if Pf.degree() == 1:
            a = int(Pf.all_coeffs()[0]) % ell
            b = int(Pf.all_coeffs()[-1]) % ell
            roots.add((-b * pow(a, -1, ell)) % ell)
        elif Pf.degree() <= 3:
            # brute-force small-degree roots via explicit formula fallback: use gf roots
            pass
    return sorted(roots)

def crt(pairs):
    from sympy.ntheory.modular import crt as scrt
    ms = [p for p, r in pairs for _ in [0]][::1]
    return scrt([p for p, _ in pairs], [r for _, r in pairs])

def extract(hs, X, Y, N, ell_list, w_bound=1 << 254, tag=''):
    per = []
    for ell in ell_list:
        rs = roots_for_prime(hs[0], hs[1], ell, X, Y)
        if rs is None or len(rs) == 0:
            print(tag, 'prime', ell, 'no linear roots', flush=True)
            return None
        if len(rs) > 4:
            print(tag, 'prime', ell, 'too many roots', len(rs), flush=True)
            return None
        per.append((ell, rs))
    # forward CRT tree
    state = [(0, 1)]  # (r mod M)
    for ell, rs in per:
        new = []
        for r, M in state:
            for r2 in rs:
                # solve x = r mod M, x = r2 mod ell
                t = ((r2 - r) * pow(M % ell, -1, ell)) % ell
                new.append((r + M * t, M * ell))
        state = new
    out = []
    for r, M in state:
        w0 = r
        if w0 >= w_bound:
            continue
        p = (1 << 255) + 2 * w0 + 1
        if p > 1 and (N is None or N % p == 0):
            out.append(p)
    return out

if __name__ == '__main__':
    # self-test: h1,h2 vanish at random (u0,w0)
    import random
    random.seed(5)
    X, Y = 1 << 300, 1 << 254
    u0 = random.randrange(1 << 299, 1 << 300)
    w0 = random.randrange(1 << 253, 1 << 254)
    u, w = sympy.symbols('u w')
    # two Q-independent polys vanishing: a1(u-u0)+b1(w-w0) etc with big coeffs
    import math
    def bigrow(a, b, cc):
        # a*u + b*w + cc with cc = -a*u0 - b*w0
        return {(1,0): Fraction(a), (0,1): Fraction(b), (0,0): Fraction(-a*u0 - b*w0)}
    h1 = bigrow(2**700, 3**400, 5)
    h2 = bigrow(7, 11*2**300, 13)
    ells = [2305843009211596801, 2305843009211596821, 2305843009210785797, 2305843009211596871, 2305843009211596911]
    # need actual primes; use sympy
    ells = [sympy.nextprime(2**60 + i*7) for i in range(5)]
    ps = extract([h1, h2], X, Y, None, ells)
    print('candidates:', ps)

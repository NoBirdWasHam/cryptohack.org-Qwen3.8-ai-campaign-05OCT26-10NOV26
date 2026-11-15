# Port of Sage's univariate Coppersmith small_roots (polynomial_modn_dense_ntl.pyx,
# May-thesis lattice) to pure Python + fpylll. Solves 1337crypt (nn=241).
# Technique provenance: official DUCTF exploit.sage (x^2 - hint*x + D^2*sqrt(n) ->
# p_approx; f = x + p_approx mod n, small_roots X=2^590 beta=0.4 eps=1/32) +
# Sage's own small_roots source for the exact lattice/param construction.
import sys, ast, math, time
from fractions import Fraction
from fpylll import IntegerMatrix, LLL
from sympy import Poly, ZZ, symbols
from sympy.ntheory import factorint, isprime

x = symbols('x')

# ---------- poly helpers (ascending coeff lists over ZZ) ----------
def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                r[i + j] += ai * bj
    return r

def ppow(a, k):
    r = [1]
    while k:
        if k & 1:
            r = pmul(r, a)
        a = pmul(a, a)
        k >>= 1
    return r

def pscale(a, c):
    return [c * t for t in a]

def pshift(a, k):  # multiply by x^k
    return [0] * k + a

def strip(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a

# ---------- small_roots (May 2003 / as in sage polynomial_modn_dense_ntl) ----------
def small_roots(N, f, X, beta, epsilon):
    """f: monic poly (ascending coeff list) with a root x0, |x0|<=X, mod b|N, b>=N^beta.
    Returns candidate integer roots (signed)."""
    d = len(f) - 1
    assert f[-1] == 1
    bb, ee = Fraction(beta), Fraction(epsilon)
    m = math.ceil(max(bb**2 / (d * ee), 7 * bb / d))
    t = math.floor(d * m * (1 / bb - 1))
    print(f"[params] delta={d} m={m} t={t} X=2^{X.bit_length()-1 if X & (X-1) == 0 else '?'} beta={beta} eps={epsilon}")
    rows = []
    fm_cache = {}
    for i in range(m):          # N^(m-i) * f^i   (j in range(d), d=1 -> j=0)
        rows.append(pscale(ppow(f, i), N ** (m - i)))
    fmax = ppow(f, m)
    for i in range(t):          # x^i * f^m
        rows.append(pshift(fmax, i))
    w = len(rows)
    ncols = d * m + max(d, t)
    assert len(rows) <= ncols * d or True
    M = IntegerMatrix(w, ncols, int_type='mpz')
    Xp = [1] * ncols
    for j in range(1, ncols):
        Xp[j] = Xp[j - 1] * X
    for r, row in enumerate(rows):
        for j, c in enumerate(row[:ncols]):
            M[r, j] = c * Xp[j]
    # cheap margin: compute det in log space from triangular pivots instead
    piv = []
    for r in range(m):
        deg = d * r
        piv.append(math.log2(N ** (m - r)) + deg * math.log2(X))
    for i in range(t):
        piv.append((m + i) * math.log2(X))
    margin = sum(piv) / w - m * 0.5 * math.log2(N)
    print(f"[lattice] dim={w}x{ncols}  HG margin: det^(1/w)~2^{sum(piv)/w:.0f} vs b^m~2^{m*0.5*math.log2(N):.0f} (+{margin:.0f} bits slack)")
    t0 = time.time()
    LLL.reduction(M, delta=0.99)
    print(f"[lattice] LLL done in {time.time()-t0:.1f}s")
    cands = set()
    hs = []
    for r in range(w):
        b = [int(M[r, j]) for j in range(ncols)]
        h = []
        ok = True
        for j in range(ncols):
            if b[j] % Xp[j]:
                ok = False
                break
            h.append(b[j] // Xp[j])
        if not ok:
            continue
        h = strip(h)
        if all(t == 0 for t in h):
            continue
        hs.append((r, h))
    print(f"[rows] {len(hs)} integral lattice polys")

    def horner(fl, t):
        acc = 0
        for cf in reversed(fl):
            acc = acc * t + cf
        return acc

    # --- modular root extraction + CRT (sympy ZZ gcd/factor is unreliable at these coeff sizes) ---
    import numpy as np
    from sympy import nextprime

    def rootset_inter(hs_, ell):
        common = None
        for _, h in hs_[:5]:
            coeffs = [c % ell for c in h]
            idx = np.arange(ell, dtype=np.int64)
            acc = np.full(ell, coeffs[-1], dtype=np.int64)
            for cf in reversed(coeffs[:-1]):
                acc = (acc * idx + cf) % ell
            rs = set(int(v) for v in idx[acc == 0])
            common = rs if common is None else (common & rs)
            if not common:
                break
        return common or set()

    npr = (X.bit_length() + 19) // 20 + 2
    primes = []
    pp = 2**20 + 3
    while len(primes) < npr:
        pp = int(nextprime(pp))
        primes.append(pp)
        pp += 1
    M = 1
    cands = [0]
    for ell in primes:
        rs = rootset_inter(hs, ell)
        if not cands or not rs:
            cands = []
            break
        inv = pow(M % ell, -1, ell)
        new = []
        modM_half = (M * ell) // 2
        for r0 in cands:
            r0l = r0 % ell
            for rl in rs:
                t = ((rl - r0l) * inv) % ell
                r = r0 + M * t
                if r > modM_half:
                    r -= M * ell
                if abs(r) <= X:
                    new.append(r)
        M *= ell
        cands = sorted(set(new))
        if not cands:
            break
    # exact verification over ZZ
    verified = set()
    for c in cands:
        if sum(1 for _, h in hs[:5] if horner(h, c) == 0) >= 2:
            verified.add(c)
    print(f"[roots] M=2^{M.bit_length()}, {len(cands)} surviving, verified: {[str(c)[:24] for c in verified]}")
    return verified

# ---------- 1337crypt pipeline ----------
def parse_output(path):
    hint = D = n = None
    c = None
    with open(path) as fh:
        txt = fh.read()
    i = txt.index('c = ')
    hint = int(txt[txt.index('hint = ')+7: txt.index('\nD = ')])
    D = int(txt[txt.index('D = ')+4: txt.index('\nn = ')])
    n = int(txt[txt.index('n = ')+4: txt.index('\nc = ')])
    c = ast.literal_eval(txt[i+4:])
    return hint, D, n, c

def p_approx_from_hint(hint, D, n):
    disc = hint * hint - 4 * D * D * math.isqrt(n)
    s = math.isqrt(disc)
    r1 = (hint - s) // 2
    r2 = (hint + s) // 2
    out = []
    for r in (r1, r2):
        out.append((r * r) // (D * D))
        out.append((r // D) ** 2)
    return out  # candidate p_approx values (dedupe at use)

def factor_from_approx(n, pA, X, beta=Fraction(2,5), eps=Fraction(1,32)):
    f = [pA, 1]  # x + pA (monic)
    roots = small_roots(n, f, X, beta, eps)
    for r in sorted(roots, key=abs):
        if abs(r) > X:
            continue
        g = math.gcd(n, pA + r)
        if 1 < g < n and n % g == 0 and isprime(g) and isprime(n // g):
            return g, r
    return None, None

def decrypt_bits(n, p, c):
    q = n // p
    bits = ''.join('1' if pow(ci, (p - 1) // 2, p) == 1 else '0' for ci in c)
    val = int(bits, 2)
    return val.to_bytes((val.bit_length() + 7) // 8, 'big')

def selftest(synthetic_bits=1337, X=2**590):
    import random
    random.seed(1234)
    def gp():
        while True:
            cand = random.getrandbits(synthetic_bits) | (1 << (synthetic_bits - 1)) | 1
            if isprime(cand):
                return cand
    while True:
        p, q = gp(), gp()
        if p == q: continue
        n = p * q
        if n.bit_length() != 2 * synthetic_bits: continue
        break
    D = 63 ** 14
    # generator used int(D*sqrt(p)+D*sqrt(q)); floor variants are within 1 => same delta scale
    hint = math.isqrt(D * D * p) + math.isqrt(D * D * q)
    pAs = p_approx_from_hint(hint, D, n)
    print(f"[selftest] p bits={p.bit_length()} pA candidates (4):", [a.bit_length() for a in pAs])
    seen = set()
    for pA in pAs:
        if pA in seen: continue
        seen.add(pA)
        d = p - pA
        print(f"[selftest] |p-pA| ~ 2^{abs(d).bit_length() if d else 0}  sign={'+' if d>=0 else '-'}")
        pr, r = factor_from_approx(n, pA, X)
        if pr:
            print(f"[selftest] RECOVERED p: {'OK' if pr in (p,q) else 'WRONG'}")
            return pr in (p, q)
    print("[selftest] FAILED")
    return False

if __name__ == '__main__':
    if sys.argv[1] == 'selftest-small':
        sys.exit(0 if selftest(512, 2**180) else 1)
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest(1337, 2**590) else 1)
    path = sys.argv[1] if len(sys.argv) > 1 else 'output.txt'
    hint, D, n, c = parse_output(path)
    print(f"[data] n={n.bit_length()} bits, hint={hint.bit_length()} bits, D={D} ({D.bit_length()} bits), len(c)={len(c)}")
    pAs = []
    for a in p_approx_from_hint(hint, D, n):
        if a not in pAs:
            pAs.append(a)
    for pA in pAs:
        print(f"[try] p_approx bits={pA.bit_length()}")
        p, r = factor_from_approx(n, pA, 2**590)
        if p:
            q = n // p
            print(f"[+] p = {p}")
            print(f"[+] p*q == n : {p*q == n}, |delta| = 2^{abs(r).bit_length()} (r = p - p_approx)")
            flag = decrypt_bits(n, p, c)
            print(f"[?] flag bytes ({len(flag)}): {flag!r}")
            break
    else:
        print("[-] no candidate p_approx yielded a factor")

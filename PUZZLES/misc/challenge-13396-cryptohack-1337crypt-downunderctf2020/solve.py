# 1337crypt (DownUnderCTF): factor n from hint = floor(D*(sqrt(p)+sqrt(q))); then GM-style bits.
# p = p0+u, q = q0+v, |u|,|v| <= X ~ 2^59x. f(u,v)=uv+q0u+p0v+c0 vanishes EXACTLY at (u0,v0),
# so every lattice poly in ideal (f,n^m) vanishes mod n^m there. Rows n^{m-j} f^j * mono(deg<=D-2j),
# LLL, HG test ||h(Xu,Xv)||_2 < n^m/sqrt(w) => h(u0,v0)=0 over Z.
# Resultant of h with f (linear in v) kills v -> R(u) with root u0; gcd(R1,R2) -> u0; p0+u0 | n.
import re, sys, math
sys.set_int_max_str_digits(10**7)
import gmpy2
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

txt = open('output.txt').read()
hint = int(re.search(r'hint = (\d+)', txt).group(1))
D = int(re.search(r'D = (\d+)', txt).group(1))
n = int(re.search(r'n = (\d+)', txt).group(1))
c = eval(re.search(r'c = (\[.*\])', txt, re.S).group(1))
assert D == 63**14

S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
t0 = (S_lo + S_hi)//2
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
print("dS bits", (S_hi-S_lo).bit_length(), "| p-q bits", d0.bit_length(),
      "| amplif", t0.bit_length()-d0.bit_length(), flush=True)
p0 = (t0 + d0)//2
q0 = n // p0
c0 = p0*q0 - n
dSb = (S_hi-S_lo+2).bit_length()
amp = max(0, t0.bit_length()-d0.bit_length()+1)
X = 1 << (dSb + amp + 4)
Y = X
print("root bound X = 2^", X.bit_length(), "| c0 bits", abs(c0).bit_length(), flush=True)
assert abs(c0).bit_length() < (p0+q0).bit_length() + 30, "c0 too big: p0/q0 assumption off"

u, v = sp.symbols('u v')
fexpr = u*v + q0*u + p0*v + c0
fmon = {(1,1): 1, (1,0): q0, (0,1): p0, (0,0): c0}
FP = {}
def fpow(k):
    if k in FP: return FP[k]
    out = {(0,0): 1}
    for _ in range(k):
        nxt = {}
        for ma, va in out.items():
            for mb, vb in fmon.items():
                m = (ma[0]+mb[0], ma[1]+mb[1]); nxt[m] = nxt.get(m, 0) + va*vb
        out = nxt
    FP[k] = out
    return out

def build(m, Dd):
    # rectangular box a,b<=K(=Dd); rows n^{m-j} g^j u^i v^k, i,k <= K-j
    K = Dd
    mons = sorted([(a,b) for a in range(K+1) for b in range(K+1)])
    idx = {mm:i for i,mm in enumerate(mons)}
    w = len(mons)
    rows = []
    for j in range(m+1):
        if j > K: break
        Np = n**(m-j)
        for i2 in range(K-j+1):
            for k2 in range(K-j+1):
                row = [0]*w
                for (ia, ib), vv in fpow(j).items():
                    ma, mb = ia+i2, ib+k2
                    if ma <= K and mb <= K:
                        row[idx[(ma,mb)]] += vv * Np * X**ma * Y**mb
                rows.append(row)
    M = IntegerMatrix(len(rows), w)
    for i, r in enumerate(rows):
        for jj, val in enumerate(r):
            if val: M[i, jj] = val
    M = lll_reduction(M, delta=0.99)
    thr = Fraction(n**m) / (Fraction(math.isqrt(w)+1))
    cands = []
    fails = 0
    for i in range(M.nrows):
        nr2 = sum(int(M[i, jj])**2 for jj in range(w))
        if Fraction(nr2) < thr*thr:
            fails = 0
            h = sp.Rational(0)
            nz = False
            for jj in range(w):
                val = int(M[i, jj])
                if val:
                    nz = True
                    (a, b) = mons[jj]
                    h += sp.Rational(val, 2**((a+b)*int(math.log2(X)))) * u**a * v**b
            if not nz:
                continue
            num = sp.numer(sp.expand(sp.together(h)))
            if sp.Poly(num, u, v).total_degree() > 0:
                cands.append(num)
        else:
            fails += 1
            if fails >= 5:
                break
    return cands

found = None
for (m, Dd) in [(8,6),(9,6),(10,6),(9,7),(10,7),(11,8),(12,8)]:
    print("try m=", m, "D=", Dd, flush=True)
    cands = build(m, Dd)
    print("  HG-passing rows:", len(cands), flush=True)
    if len(cands) < 2:
        continue
    Rs = []
    vf = -(q0*u + c0)/(u + p0)
    for h in cands:
        hp = sp.Poly(sp.expand(h), u, v)
        dv = hp.degree(v)
        R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
        R = sp.Poly(R, u)
        if R.degree() >= 1:
            Rs.append(R)
    print("  nonzero resultants:", len(Rs), "degs:", [r.degree() for r in Rs][:8], flush=True)
    if not Rs:
        continue
    pool = []
    if len(Rs) >= 2:
        g = sp.gcd(Rs[0], Rs[1])
        i = 2
        while g.degree() > 40 and i < len(Rs):
            g = sp.gcd(g, Rs[i]); i += 1
        if g.degree() >= 1:
            g = sp.Poly(sp.sqf_part(g.as_expr()), u)
            pool.append(g)
    print("  pool degs:", [pp.degree() for pp in pool], flush=True)
    for g in pool:
        if g.degree() == 1:
            a1, a0 = g.all_coeffs()
            if sp.Rational(a0, a1).is_Integer:
                rc = int(-a0/a1)
                for pp in (p0+rc, p0-rc):
                    if pp > 1 and n % pp == 0:
                        found = pp
        if found: break
        try:
            fac = sp.factor(g.as_expr())
        except Exception as e:
            print("   factor fail:", str(e)[:100], flush=True)
            continue
        for f1 in sp.Mul.make_args(fac):
            P = sp.Poly(f1, u)
            if P.degree() == 1:
                a1, a0 = P.all_coeffs()
                if sp.Rational(a0, a1).is_Integer:
                    rc = int(-a0/a1)
                    for pp in (p0+rc, p0-rc):
                        if pp > 1 and n % pp == 0:
                            found = pp
        if found: break
    if found: break

if not found:
    print("FAILED"); sys.exit(1)
p_ = found; q_ = n // p_
print("FACTORED", p_.bit_length(), q_.bit_length(), p_*q_ == n, flush=True)
bits = [1 if pow(ci, (p_-1)//2, p_) == 1 else 0 for ci in c]
val = int(''.join(map(str, bits)), 2)
flag = val.to_bytes((val.bit_length()+7)//8, 'big')
print("FLAG:", flag)
open('flag_1337crypt-downunderctf2020.txt', 'w').write(flag.decode(errors='replace'))

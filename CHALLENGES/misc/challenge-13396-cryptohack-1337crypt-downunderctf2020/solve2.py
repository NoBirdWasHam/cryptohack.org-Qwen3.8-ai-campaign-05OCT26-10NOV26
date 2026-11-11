# solve2.py — finish key recovery from bivariate-Coppersmith resultants FAST.
# Same lattice build as solve.py (m=8,D=6 produced 48 HG-passing rows, 12 nonzero
# resultants in run1.log). Root extraction replaced: dump R polys -> pari gcd ->
# modular root-intersection CRT -> integer root u0 -> p = p0+u0.
import re, sys, math, os, subprocess, time
sys.set_int_max_str_digits(10**7)
import gmpy2
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

t_start = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(HERE, 'output.txt')).read()
hint = int(re.search(r'hint = (\d+)', txt).group(1))
D = int(re.search(r'D = (\d+)', txt).group(1))
n = int(re.search(r'n = (\d+)', txt).group(1))
c = eval(re.search(r'c = (\[.*\])', txt, re.S).group(1))
assert D == 63**14

S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
t0 = (S_lo + S_hi)//2
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
p0 = (t0 + d0)//2
q0 = n // p0
c0 = p0*q0 - n
dSb = (S_hi-S_lo+2).bit_length()
amp = max(0, t0.bit_length()-d0.bit_length()+1)
X = 1 << (dSb + amp + 4)
Y = X
print("p0 bits", p0.bit_length(), "| X = 2^", X.bit_length(), "| c0 bits", abs(c0).bit_length(), flush=True)

u, v = sp.symbols('u v')
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
    for i in range(M.nrows):
        nr2 = sum(int(M[i, jj])**2 for jj in range(w))
        if Fraction(nr2) >= thr*thr:
            continue
        h = sp.Rational(0); nz = False
        for jj in range(w):
            val = int(M[i, jj])
            if val:
                nz = True
                (a, b) = mons[jj]
                h += sp.Rational(val, 2**((a+b)*594)) * u**a * v**b
        if not nz: continue
        num = sp.numer(sp.expand(sp.together(h)))
        if sp.Poly(num, u, v).total_degree() > 0:
            cands.append(num)
    return cands

def resultants(cands):
    vf = -(q0*u + c0)/(u + p0)
    Rs = []
    for h in cands:
        hp = sp.Poly(sp.expand(h), u, v)
        dv = hp.degree(v)
        R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
        R = sp.Poly(R, u)
        if R.degree() >= 1:
            Rs.append(R.as_expr())
    return Rs

def dump_poly(pexpr, fname):
    P = sp.Poly(pexpr, u)
    with open(fname, 'w') as fh:
        for co in P.all_coeffs()[::-1]:   # ascending
            fh.write(str(int(co)) + "\n")

GP = r"~\tools\gp64.exe"

def gp_run(script, timeout=2400):
    p = subprocess.run([GP, "-q"], input=script, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.stderr.strip()

def roots_mod_p(poly_expr, p):
    """all roots in GF(p) of squarefree part via gcd with x^p-x"""
    R = sp.Poly(poly_expr, u, modulus=p)
    if R.degree() < 1: return set()
    xpx = sp.Poly(u**p - u, u, modulus=p)
    g = sp.gcd(R, xpx)
    out = set()
    for f1, e in g.factor_list()[1]:
        if f1.degree() == 1:
            a1, a0 = f1.all_coeffs()
            out.add(int((-a0 * sp.invert(a1, p)) % p))
    return out

def solve_with(m, Dd):
    print("build m=", m, "D=", Dd, flush=True)
    cands = build(m, Dd)
    print("  HG rows:", len(cands), flush=True)
    if len(cands) < 2: return None
    Rs = resultants(cands)
    print("  Rs:", len(Rs), "degs:", sorted(set(int(sp.Poly(r,u).degree()) for r in Rs)), flush=True)
    if not Rs: return None
    for i, r in enumerate(Rs): dump_poly(r, os.path.join(HERE, f"r{i}.txt"))
    k = min(len(Rs), 6)
    gscript = 'default(parisize,"2G");\n'
    for i in range(k):
        gscript += f'P{i}=Pol(Vec(read("{os.path.join(HERE, f"r{i}.txt").replace(chr(92), "/")}")));\n'
    gscript += 'g=P0;\n'
    for i in range(1, k):
        gscript += 'g=content(g);g=P0*0;\n' if False else f'g=pollred(gcd(g,P{i}));\n'
    gscript += 'g=sqfree(g);print("GCDDEG ",poldegree(g));\n'
    gscript += 'G=Vec(g);for(i=1,#G,print(G[i]));\n'
    out, err = gp_run(gscript)
    print("  gp:", out.split("\n")[0], err[:200], flush=True)
    lines = out.split("\n")
    degline = lines[0]
    coeffs = [int(x) for x in lines[1:] if x.strip()]
    if "GCDDEG" not in degline or not coeffs: return None
    gdeg = int(degline.split()[1])
    print("  gcd deg:", gdeg, flush=True)
    gexpr = sum(sp.Integer(cc)*u**i for i, cc in enumerate(coeffs))
    # modular root intersection
    cands_r = None; M = 1
    for p in sp.primerange(5, 500):
        rp = roots_mod_p(gexpr, p)
        if cands_r is None:
            cands_r = {r % p for r in rp}; M = p
            if not cands_r: break
            continue
        new = set()
        rset = set(rp)
        for a in cands_r:
            ra = a % p
            if ra in rset:
                # CRT: x = a mod M, x = ra mod p
                t = ((ra - a) * int(gmpy2.invert(M, p))) % p
                new.add((a + M*t) % (M*p))
        cands_r = new; M *= p
        print(f"   p={p} |cands|={len(cands_r)} Mbits={M.bit_length()}", flush=True)
        if not cands_r: return None
        if M > 4*X: break
    for a in (cands_r or []):
        for u0 in (a, a - M):
            for pp in (p0 + u0, p0 - u0):
                if pp > 1 and n % pp == 0:
                    return pp
    # also try sign-flipped resultant (u -> root could be negative branch)
    return None

found = None
for (m, Dd) in [(8,6),(9,6),(8,7)]:
    try:
        found = solve_with(m, Dd)
    except Exception as e:
        import traceback; traceback.print_exc()
    if found: break
    print("  elapsed", int(time.time()-t_start), flush=True)

if not found:
    print("FAILED"); sys.exit(1)
p_ = found; q_ = n // p_
print("FACTORED", p_.bit_length(), q_.bit_length(), p_*q_ == n, flush=True)
bits = [1 if pow(ci, (p_-1)//2, p_) == 1 else 0 for ci in c]
val = int(''.join(map(str, bits)), 2)
flag = val.to_bytes((val.bit_length()+7)//8, 'big')
print("FLAG:", flag)
open(os.path.join(HERE, 'flag_1337crypt-downunderctf2020.txt'), 'wb').write(flag)

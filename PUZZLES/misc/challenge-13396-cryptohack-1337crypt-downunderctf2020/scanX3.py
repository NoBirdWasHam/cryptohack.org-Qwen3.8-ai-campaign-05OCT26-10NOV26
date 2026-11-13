# scanX.py — for X in (600,620,650): build lattice, HG rows, resultants, dump;
# then pari gcd + modular root intersection -> p | n? Print verdict per X.
import re, sys, math, os, subprocess, time
sys.set_int_max_str_digits(10**7)
import gmpy2
from fractions import Fraction
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

HERE = os.path.dirname(os.path.abspath(__file__))
GP = r"~\tools\gp64.exe"
txt = open(os.path.join(HERE, 'output.txt')).read()
hint = int(re.search(r'hint = (\d+)', txt).group(1))
D = int(re.search(r'D = (\d+)', txt).group(1))
n = int(re.search(r'n = (\d+)', txt).group(1))
c = eval(re.search(r'c = (\[.*\])', txt, re.S).group(1))
S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
t0 = (S_lo + S_hi)//2
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
p0 = (t0 + d0)//2
q0 = n // p0
c0 = p0*q0 - n
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

def roots_mod_p(gexpr, p):
    R = sp.Poly(gexpr, u, modulus=p)
    if R.degree() < 1: return set()
    g = sp.gcd(R, sp.Poly(u**p - u, u, modulus=p))
    out = set()
    for f1, e in g.factor_list()[1]:
        if f1.degree() == 1:
            a1, a0 = f1.all_coeffs()
            out.add(int((-a0 * sp.invert(a1, p)) % p))
    return out

def extract(tag, Mbits=670):
    k = 6
    scr = ['default(parisize,"2G");']
    for i in range(k):
        scr.append(f'P{i}=Pol(Vec(readvec("{os.path.join(HERE, f"sx{i}.txt").replace(chr(92),"/")}")));')
    scr.append('g=P0;')
    for i in range(1, k):
        scr.append(f'g=gcd(g,P{i});')
    scr.append('g=g/content(g);')
    scr.append('print1("GCDDEG ",poldegree(g),"\\n");')
    scr.append('forprime(p=5,1500, my(rs=polrootsmod(g,p)); print1("R ",p); for(i=1,#rs,print1(" ",lift(rs[i]))); print1("\\n"); );')
    scr.append('quit();')
    pr = subprocess.run([GP, "-q"], input="\n".join(scr), capture_output=True, text=True, timeout=2400)
    lines = pr.stdout.splitlines()
    if not lines or "GCDDEG" not in lines[0]:
        print(tag, "gp fail:", pr.stderr[:150], flush=True); return None
    deg = int(lines[0].split()[1])
    print(tag, "gcd deg", deg, flush=True)
    rootmap = {}
    for L in lines[1:]:
        parts = L.split()
        if parts and parts[0] == 'R':
            rootmap[int(parts[1])] = set(int(x) for x in parts[2:])
    cands = None; M = 1
    for pr2 in sorted(rootmap):
        rp = rootmap[pr2]
        if cands is None:
            cands = set(rp); M = pr2
        else:
            new = set()
            for a in cands:
                ra = a % pr2
                if ra in rp:
                    t = ((ra - a) * int(gmpy2.invert(M, pr2))) % pr2
                    new.add(a + M*t)
            cands = new; M *= pr2
        if not cands:
            print(tag, "intersection EMPTY at", pr2, flush=True); return None
        if M.bit_length() > Mbits: break
    for a in cands:
        for u0 in (a % M, a % M - M):
            for pp in (p0 + u0, p0 - u0):
                if pp > 1 and n % pp == 0:
                    return pp
    print(tag, "no divisor among", len(cands), "cands", flush=True)
    return None

for XBITS in (617, 618, 619):
    EBITS = 27
    E = 1 << EBITS
    S_lo = (hint*hint - (2*hint*E + E*E) - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n)) - 1) // D**2
    S_hi = ((hint+E)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
    t0 = (S_lo + S_hi)//2
    d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
    p0 = (t0 + d0)//2
    q0 = n // p0
    c0 = p0*q0 - n
    fmon.clear(); FP.clear()
    fmon.update({(1,1): 1, (1,0): q0, (0,1): p0, (0,0): c0})
    X = 1 << XBITS; Y = X
    print(f"XBITS={XBITS}", flush=True)
    m, K = 8, 6
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
    M2 = IntegerMatrix(len(rows), w)
    for i2, r in enumerate(rows):
        for jj, val in enumerate(r):
            if val: M2[i2, jj] = val
    M2 = lll_reduction(M2, delta=0.99)
    thr = Fraction(n**m) / (Fraction(math.isqrt(w)+1))
    cands = []
    for i2 in range(M2.nrows):
        nr2 = sum(int(M2[i2, jj])**2 for jj in range(w))
        if Fraction(nr2) >= thr*thr: continue
        rr = [int(M2[i2, jj]) for jj in range(w)]
        if all(x == 0 for x in rr): continue
        h = sp.Rational(0)
        for jj in range(w):
            val = rr[jj]
            if val:
                (a, b) = mons[jj]
                h += sp.Rational(val, X**(a+b)) * u**a * v**b
        num = sp.numer(sp.expand(sp.together(h)))
        if sp.Poly(num, u, v).total_degree() > 0:
            cands.append(num)
    vf = -(q0*u + c0)/(u + p0)
    Rs = []
    for h in cands:
        hp = sp.Poly(sp.expand(h), u, v)
        dv = hp.degree(v)
        R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
        R = sp.Poly(R, u)
        if R.degree() >= 1:
            Rs.append(R)
    print(f"X={XBITS}: pass={len(cands)} Rs={len(Rs)}", flush=True)
    found = None
    if len(Rs) >= 2:
        for i2, R in enumerate(Rs[:6]):
            with open(os.path.join(HERE, f"sx{i2}.txt"), 'w') as fh:
                for co in R.all_coeffs()[::-1]:
                    fh.write(str(int(co)))
                    fh.write(chr(10))
        found = extract(f"[X=2^{XBITS}]", Mbits=XBITS+2)
    if found:
        p_ = found; q_ = n // p_
        print("FACTORED at X", XBITS, p_.bit_length(), p_*q_ == n, flush=True)
        bits = [1 if pow(ci, (p_-1)//2, p_) == 1 else 0 for ci in c]
        val = int(''.join(map(str, bits)), 2)
        flag = val.to_bytes((val.bit_length()+7)//8, 'big')
        print("FLAG:", flag, flush=True)
        open(os.path.join(HERE, 'flag_1337crypt-downunderctf2020.txt'), 'wb').write(flag)
        break
print("SCAN DONE", flush=True)

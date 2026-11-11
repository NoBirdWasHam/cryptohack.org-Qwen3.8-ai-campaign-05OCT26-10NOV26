# 1337crypt (DownUnderCTF 2020) - CryptoHack archive
# Step 1: hint = floor(D*(sqrt(p)+sqrt(q))) -> t = p+q known within ~2h/D^2 (< N^{1/4})
#         -> p0 ~ larger prime (via s0 = isqrt(t0^2-4n)), q0 = n//p0
# Step 2: FHKLS bivariate-linear lattice on f(x,y)=xy + q0*x + p0*y + (p0*q0-n)=0,
#         root (x,y) both ~ N^{1/4} sized. LLL -> 2+ vanishing polys -> eliminate -> exact (x,y).
# Step 3: decrypt Goldwasser-Micali bits: legendre(c,p) = -1 iff b=0  (since legendre(x,p)=-1).
import re, ast, gmpy2
from fractions import Fraction
from fpylll import IntegerMatrix, LLL

def factor_from_hint(h, D, n, bits=600):
    S2 = int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))          # floor(2 D^2 sqrt(n))
    lo = (h*h - S2 - 2*h) // D**2 - 4
    hi = (h*h - S2 + 2*h) // D**2 + 4                    # interval containing t=p+q
    t0 = (h*h - S2 + h) // D**2
    E  = (hi - lo)
    s0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
    p0 = (t0 + s0) // 2                                   # ~ max(p,q)
    q0 = int(n) // p0
    X = Y = 1 << (int(E).bit_length() + 4)                # both |x|,|y| < ~E
    cols = [1, X, Y, X*Y]
    c0 = p0*q0 - int(n)
    rows = [ [c0,  q0*X, p0*Y, X*Y],
             [int(n), 0, 0, 0],
             [0, int(n)*X, 0, 0],
             [0, 0, int(n)*Y, 0] ]
    M = IntegerMatrix.from_matrix(rows)
    LLL.reduction(M)
    polys = []
    for i in range(M.nrows):
        v = [int(M[i,j]) for j in range(4)]
        if all(x==0 for x in v): continue
        polys.append([Fraction(v0, cc) for v0, cc in zip(v, cols)])
    # pairwise elimination of xy -> linear relations a*x+b*y+c=0
    def lin(P, Q):
        a1,b1,c1,d1 = P; a2,b2,c2,d2 = Q
        f = d1*a2 - d2*a1; e = d1*b2 - d2*b1; g = d1*c2 - d2*c1
        if (f,e,g) == (Fraction(0),Fraction(0),Fraction(0)): return None
        return (f,e,g)
    rels = []
    for i in range(len(polys)):
        for j in range(i+1, len(polys)):
            Lr = lin(polys[i], polys[j])
            if Lr is None: continue
            # normalize + dedupe by cross-multiplication
            norm = Lr
            if not any(any(r[0]*norm[1]==norm[0]*r[1] and r[0]*norm[2]==norm[0]*r[2] and r[1]*norm[2]==norm[1]*r[2] for r in [norm]) for norm in [Lr]):
                pass
            dup = False
            for r in rels:
                if r[0]*Lr[1]==Lr[0]*r[1] and r[0]*Lr[2]==Lr[0]*r[2] and r[1]*Lr[2]==Lr[1]*r[2]:
                    dup = True; break
            if not dup: rels.append(Lr)
    cands = set()
    # two independent linear relations -> exact x
    for i in range(len(rels)):
        for j in range(len(rels)):
            if i==j: continue
            a1,b1,c1 = rels[i]; a2,b2,c2 = rels[j]
            den = a1*b2 - a2*b1
            if den == 0: continue
            x = (b1*c2 - b2*c1)/den
            y = (c1*a2 - c2*a1)/den
            if x.denominator==1 and y.denominator==1:
                cands.add((int(x), int(y)))
    # fallback: one linear rel + f
    P, Q, R = None, None, None
    for (a,b,c) in rels:
        if b != 0:
            P,Q,R = a,b,c; break
    if P is not None and not cands:
        # y = -(P x + R)/Q ; plug into f(x,y)=xy+q0 x + p0 y + c0 = 0
        # x*(-(Px+R)/Q) + q0 x + p0*(-(Px+R)/Q) + c0 = 0 ; *Q:
        # -P x^2 - R x + q0 Q x - p0 P x - p0 R + c0 Q = 0
        A = -P; B = -R + q0*Q - p0*P; C = -p0*R + c0*Q
        disc = B*B - 4*A*C
        if disc >= 0:
            sd = gmpy2.isqrt(gmpy2.mpz(disc.numerator)/disc.denominator) if disc.denominator==1 else None
            sd = gmpy2.isqrt(gmpy2.mpz(disc.numerator)*disc.denominator)
            for sgn in (1,-1):
                for num in (sd.numerator*1,):
                    x = Fraction(-B.numerator*int(disc.denominator) + sgn*int(num), 2*A.numerator*int(disc.denominator)) if A.denominator==1 else None
                    # simpler: evaluate roots via Fraction arithmetic
            # redo cleanly
            def roots(A,B,C):
                disc = B*B - 4*A*C
                dn = disc.numerator; dd = disc.denominator
                sd = gmpy2.isqrt(gmpy2.mpz(dn*dd))
                if sd*sd != dn*dd: return []
                s = Fraction(int(sd))
                return [(-B+s)/(2*A), (-B-s)/(2*A)]
            for x in roots(A,B,C):
                if x.denominator==1:
                    xv=int(x); yv = -(P*x+R)/Q
                    if yv.denominator==1: cands.add((xv,int(yv)))
    for (x,y) in cands:
        for p_ in (p0+x, p0-x):
            if p_ > 1 and int(n) % p_ == 0:
                return p_, int(n)//p_, t0, E
    return None, None, t0, E

# ---- toy self-test ----
import random
def toy(bits=300):
    p = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits)) | 1)
    q = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits)) | 1)
    D = 63**14
    n = p*q
    import decimal
    decimal.getcontext().prec = bits+200
    dp = decimal.Decimal(int(p)).sqrt(); dq = decimal.Decimal(int(q)).sqrt()
    hint = int(D*dp + D*dq)
    t = p+q
    a,b,t0,E = factor_from_hint(hint, D, n)
    print(f"TOY {bits}b: t={int(t).bit_length()}b err={int(E).bit_length() if E else 0}b  solved={sorted([a,b])==sorted([p,q])}")
    return sorted([a,b])==sorted([p,q])

for bits in (300, 400):
    assert toy(bits)

# ---- real instance ----
txt = open('output.txt').read()
hint = int(re.search(r'hint = (\d+)', txt).group(1))
D    = int(re.search(r'D = (\d+)', txt).group(1))
n    = int(re.search(r'n = (\d+)', txt).group(1))
c    = ast.literal_eval(re.search(r'c = (\[.*\])', txt).group(1))
assert D == 63**14
a, b, t0, E = factor_from_hint(hint, D, n)
if a is None:
    print("FACTOR FAILED, t0 bits", int(t0).bit_length(), "err bits", int(E).bit_length())
    raise SystemExit(1)
p, q = (a, b) if a > b else (b, a)
print("factored:", int(p).bit_length(), int(q).bit_length(), "prod ok:", p*q == n)

bits = []
for ci in c:
    bits.append(1 if int(pow(ci, (p-1)//2, p)) == 1 else 0)
val = int(''.join(map(str,bits)), 2)
flag = val.to_bytes((val.bit_length()+7)//8, 'big')
print("FLAG:", flag)
open('flag_1337crypt-downunderctf2020.txt','w').write(flag.decode())

from gmpy2 import mpz
import json, re, math

L = 1
for i in range(1, 256):
    L = math.lcm(L, i)
p = mpz(37) * (mpz(2) ** 64) * L - 1

def fadd(a,b): return ((a[0]+b[0])%p, (a[1]+b[1])%p)
def fsub(a,b): return ((a[0]-b[0])%p, (a[1]-b[1])%p)
def fneg(a): return ((-a[0])%p, (-a[1])%p)
def fmul(a,b): return ((a[0]*b[0]-a[1]*b[1])%p, (a[0]*b[1]+a[1]*b[0])%p)
def fsq(a): return ((a[0]*a[0]-a[1]*a[1])%p, (2*a[0]*a[1])%p)
def fdiv(a,b):
    nb = (b[0]*b[0]+b[1]*b[1]) % p
    inv = pow(nb, -1, p)
    return fmul(a, fmul((b[0], (-b[1])%p), (inv, 0)))

# ---- field arithmetic self-tests (independent identities) ----
import random
random.seed(7)
def rand(): return (random.randrange(p), random.randrange(p))
ok_assoc = ok_dist = ok_norm = ok_sq = True
for _ in range(50):
    x, y, z = rand(), rand(), rand()
    if fmul(fmul(x,y),z) != fmul(x,fmul(y,z)): ok_assoc = False
    if fmul(fadd(x,y),z) != fadd(fmul(x,z),fmul(y,z)): ok_dist = False
    if fmul(x,(x[0],(-x[1])%p)) != ((x[0]*x[0]+x[1]*x[1])%p, 0): ok_norm = False
    if fsq(x) != fmul(x,x): ok_sq = False
print("assoc:", ok_assoc, " distrib:", ok_dist, " norm:", ok_norm, " sq==mul:", ok_sq)

# independent complex-multiplication reference via 2x2 matrix
def fmul_ref(a,b):
    # (a0+a1 i)(b0+b1 i) computed with python int, mod p at the very end
    r0 = (a[0]*b[0] - a[1]*b[1]) % p
    r1 = (a[0]*b[1] + a[1]*b[0]) % p
    return (r0, r1)
bad = 0
for _ in range(50):
    x, y = rand(), rand()
    if fmul(x,y) != fmul_ref(x,y): bad += 1
print("fmul vs ref mismatches:", bad)

# ---- now the j-invariant debug ----
ct = json.load(open("output.txt"))
def ptj(entry):
    return ((mpz(entry["x"][0]) % p, mpz(entry["x"][1]) % p),
            (mpz(entry["y"][0]) % p, mpz(entry["y"][1]) % p))
A = ptj(ct[0]["P"]); B = ptj(ct[0]["Q"])
def rhs(pt):
    x, y = pt
    return fsub(fsq(y), fmul(fmul(x,x), x))
RA, RB = rhs(A), rhs(B)
den = fsub(A[0], B[0])
a4 = fdiv(fsub(RA, RB), den)
a6 = fsub(RA, fmul(a4, A[0]))
print("a4 == (0,0)?", a4 == (mpz(0),0))
a42 = fsq(a4)
a43 = fmul(a42, a4)
a62 = fsq(a6)
four = (mpz(4),0); two7 = (mpz(27),0); c1728 = (mpz(1728),0); c48 = (mpz(48),0); c16n = (-mpz(16),0)
print("a4^3 == 0?", a43 == (mpz(0),0))
numj = fmul(fmul(a43, four), c1728)
denj = fadd(fmul(a43, four), fmul(a62, two7))
print("numj == 0?", numj == (mpz(0),0))
print("denj == 0?", denj == (mpz(0),0))
j = fdiv(numj, denj)
print("j == 0?", j == (mpz(0),0))
print("a4*a6:", fmul(a4,a6) == (mpz(0),0))
# independent: c4, c6, Delta, j = c4^3 / Delta
c4 = fmul(a4, c48)
c6 = fmul(fmul(a6, c48), (-mpz(18),0))   # c6 = -864 a6
Delta = fmul(c16n, fadd(fmul(a43, four), fmul(a62, two7)))
j2 = fdiv(fmul(fmul(c4,c4),c4), Delta)
print("j2 (c4^3/Delta) == 0?", j2 == (mpz(0),0), " j == j2?", j == j2)

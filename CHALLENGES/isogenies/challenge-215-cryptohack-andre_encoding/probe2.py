"""Pure gmpy2 probe: no ec2 reuse. Verify domain points, codomain recovery, j-invariant."""
from gmpy2 import mpz, isqrt
import json, re, math

L = 1
for i in range(1, 256):
    L = math.lcm(L, i)
p = mpz(37) * (mpz(2) ** 64) * L - 1
print("p bits:", p.bit_length())

# F_p^2 as (a,b) = a + b i, i^2 = -1, pure gmpy2
def fadd(a,b): return ((a[0]+b[0])%p, (a[1]+b[1])%p)
def fsub(a,b): return ((a[0]-b[0])%p, (a[1]-b[1])%p)
def fneg(a): return ((-a[0])%p, (-a[1])%p)
def fmul(a,b): return ((a[0]*b[0]-a[1]*b[1])%p, (a[0]*b[1]+a[1]*b[0])%p)
def fsq(a): return ((a[0]*a[0]-a[1]*a[1])%p, (2*a[0]*a[1])%p)
def fdiv(a,b):
    nb = (b[0]*b[0]+b[1]*b[1]) % p
    inv = pow(nb, -1, p)
    return fmul(a, fmul((b[0], -b[1]%p), (inv, 0)))

src = open("source.sage").read()
def parse_pt(var):
    m = re.search(var + r" = E\((.+?), 1\)", src, re.S)
    parts = m.group(1).split(",")
    def coeff(part):
        mm = re.match(r"\s*(\d+)\*i \+ (\d+)\s*$", part)
        return (mpz(mm.group(2)) % p, mpz(mm.group(1)) % p)
    return (coeff(parts[0]), coeff(parts[1]))
P = parse_pt("P"); Q = parse_pt("Q")

def on_plain(pt):  # y^2 = x^3 + 1
    x, y = pt
    return fsq(y) == fadd(fmul(fmul(x,x),x), (mpz(1), 0))
def on_sage(pt):   # y^2 + y = x^3 + 1
    x, y = pt
    return fadd(fsq(y), y) == fadd(fmul(fmul(x,x),x), (mpz(1), 0))

print("P on y2=x3+1:", on_plain(P), " Q on y2=x3+1:", on_plain(Q))
print("P on y2+y=x3+1:", on_sage(P), " Q on y2+y=x3+1:", on_sage(Q))

# raw parse of ct[0]
ct = json.load(open("output.txt"))
print("num ct entries:", len(ct))
def ptj(entry):
    return ((mpz(entry["x"][0]) % p, mpz(entry["x"][1]) % p),
            (mpz(entry["y"][0]) % p, mpz(entry["y"][1]) % p))
A = ptj(ct[0]["P"]); B = ptj(ct[0]["Q"])
print("A == P?", A == P, " B == Q?", B == Q)
print("A on y2=x3+1 (domain):", on_plain(A), " B on domain:", on_plain(B))

# 2x2 recovery: a4*(xA - xB) = (yA^2 - xA^3) - (yB^2 - xB^3)
def rhs(pt):
    x, y = pt
    return fsub(fsq(y), fmul(fmul(x,x), x))
RA, RB = rhs(A), rhs(B)
den = fsub(A[0], B[0])
print("xA == xB?", den == (mpz(0), 0))
a4 = fdiv(fsub(RA, RB), den)
a6 = fsub(RA, fmul(a4, A[0]))
print("a4:", str(a4[0])[:24], "...+ i*...", str(a4[1])[:24])
print("a6:", str(a6[0])[:24], "...+ i*...", str(a6[1])[:24])
def on_cod(pt):
    x, y = pt
    return fsq(y) == fadd(fmul(fmul(x,x),x), fadd(fmul(a4,x), a6))
print("A on recovered codomain:", on_cod(A), " B on recovered codomain:", on_cod(B))

# j = 1728 * 4 a4^3 / (4 a4^3 + 27 a6^2)
a43 = fmul(fmul(a4,a4),a4)
a62 = fsq(a6)
num = fmul(fmul(a43, mpz(4)), mpz(1728))
denj = fadd(fmul(a43, mpz(4)), fmul(a62, mpz(27)))
j = fdiv(num, denj)
print("j(codomain) == 0?", j == (mpz(0), 0))
print("a4*a6 == 0?", fmul(a4,a6) == (mpz(0), 0))

# check the two j=0 special forms:
cA = rhs(A); cB = rhs(B)
print("yA^2-xA^3 == yB^2-xB^3 (a4=0 form)?", cA == cB)
if cA != cB:
    a4b = fdiv(fsub(cA, cB), fsub(A[0], B[0]))
    print("a4 (from 2pt) == a4 (from rhs-diff)?", a4b == a4)
    # y^2 = x^3 + a4 x + a6: check a6 from each point
    a6a = fsub(cA, fmul(a4, A[0])); a6b = fsub(cB, fmul(a4, B[0]))
    print("a6 consistent:", a6a == a6b)

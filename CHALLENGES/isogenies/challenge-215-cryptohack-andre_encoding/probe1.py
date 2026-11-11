import ec2 as E
import json, re
from gmpy2 import mpz

p = E.p
src = open("source.sage").read()
def parse_pt(var):
    m = re.search(var + r" = E\((.+?), 1\)", src, re.S)
    parts = m.group(1).split(",")
    def coeff(part):
        mm = re.match(r"\s*(\d+)\*i \+ (\d+)\s*$", part)
        im_c, re_c = int(mm.group(1)), int(mm.group(2))
        return (re_c % p, im_c % p)
    return (coeff(parts[0]), coeff(parts[1]))
P = parse_pt("P"); Q = parse_pt("Q")

def sage_curve_check(pt):
    # y^2 + y = x^3 + 1
    x, y = pt
    lhs = E.fadd(E.fsq(y), y)
    rhs = E.fadd(E.fmul(E.fmul(x,x),x), (1,0))
    return E.feq(lhs, rhs) if hasattr(E,'feq') else (lhs == rhs)

def plain_curve_check(pt):
    # y^2 = x^3 + 1
    x, y = pt
    return E.fsq(y) == E.fadd(E.fmul(E.fmul(x,x),x), (1,0))

print("P on y^2+y=x^3+1 (Sage curve):", sage_curve_check(P))
print("Q on y^2+y=x^3+1 (Sage curve):", sage_curve_check(Q))
print("P on y^2=x^3+1 (ec2 model):", plain_curve_check(P))
print("Q on y^2=x^3+1 (ec2 model):", plain_curve_check(Q))

# j-invariant of recovered codomain
cod = json.load(open("codomain.json"))
a4 = (cod["a4"][0] % p, cod["a4"][1] % p)
a6 = (cod["a6"][0] % p, cod["a6"][1] % p)
num = E.fmul(E.fmul((4,0), E.fmul(E.fmul(a4,a4),a4)), (1728,0))
den = E.fadd(E.fmul(E.fmul((4,0), E.fmul(E.fmul(a4,a4),a4)), (27,0)), E.fmul(E.fmul((27,0), E.fsq(a6))))
j = E.fdiv(num, den)
print("j(codomain) == 0?", j == (0,0))
print("a4*a6 == 0?", E.fmul(a4,a6) == (0,0))

# cross-check fmul against gmpy2 complex-like arithmetic: (a+bi)(c+di)
import random
random.seed(1)
ok = True
for _ in range(200):
    a=(random.randrange(p), random.randrange(p)); b=(random.randrange(p), random.randrange(p))
    c1 = (a[0]*b[0]-a[1]*b[1]) % p; c2 = (a[0]*b[1]+a[1]*b[0]) % p
    g1 = (mpz(a[0])*mpz(b[0]) - mpz(a[1])*mpz(b[1])) % p
    g2 = (mpz(a[0])*mpz(b[1]) + mpz(a[1])*mpz(b[0])) % p
    if (c1,c2) != (int(g1),int(g2)): ok=False; break
print("fmul vs gmpy2 (200 random):", ok)

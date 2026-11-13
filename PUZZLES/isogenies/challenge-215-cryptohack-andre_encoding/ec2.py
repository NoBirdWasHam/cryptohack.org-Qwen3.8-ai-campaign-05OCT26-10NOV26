"""F_p^2 EC toolkit for andre_encoding (y^2 = x^3 + 1 over F_p(i), i^2=-1).
Sage EllipticCurve(F, [0,1]) == [a4,a6] convention. Pure Python bignums; p is 432 bits.
"""
import json, math
from functools import lru_cache

def lcm(a, b): return a // math.gcd(a, b) * b

L = 1
for i in range(1, 256):
    L = lcm(L, i)
p = 37 * (2 ** 64) * L - 1
P1 = p + 1  # = 37 * 2^64 * L
ORDER2 = (p + 1) ** 2  # claimed #E

print("p bits:", p.bit_length())
print("p+1 = 37*2^64*L:", P1 == 37 * (2 ** 64) * L)

# ---- F_p^2 : (a,b) = a + b*i, i^2 = -1 ----
def f0(a): return (a % p, 0)
def fadd(a, b): return ((a[0] + b[0]) % p, (a[1] + b[1]) % p)
def fsub(a, b): return ((a[0] - b[0]) % p, (a[1] - b[1]) % p)
def fneg(a): return ((-a[0]) % p, (-a[1]) % p)      # field NEGATION: -(a0+a1 i)
def fconj(a): return (a[0] % p, (-a[1]) % p)        # field CONJUGATE: a0 - a1 i
def fmul(a, b): return ((a[0]*b[0] - a[1]*b[1]) % p, (a[0]*b[1] + a[1]*b[0]) % p)
def fsq(a): return ((a[0]*a[0] - a[1]*a[1]) % p, (2*a[0]*a[1]) % p)
def fdiv(a, b):
    # a / b = a * conj(b) / N(b)
    nb = (b[0]*b[0] + b[1]*b[1]) % p
    inv = pow(nb, -1, p)
    return fmul(a, fmul(fconj(b), (inv, 0)))

def from_pair(pr): return (pr[0] % p, pr[1] % p)

# ---- EC over F_p^2 : y^2 = x^3 + 1 (a4=0, a6=1) ----
O = None  # identity

def ec_on_curve(pt):
    if pt is O: return True
    x, y = pt
    rhs = fadd(fmul(fmul(x, x), x), (1 % p, 0))  # x^3 + 1  (Sage [a4,a6]=[0,1])
    return fsq(y) == rhs

def ec_add(A, B):
    if A is O: return B
    if B is O: return A
    ax, ay = A; bx, by = B
    if ax == bx:
        if (ay[0] + by[0]) % p == 0 and (ay[1] + by[1]) % p == 0:
            return O
        # double
        num = fmul(fmul((3 % p, 0), ax), ax)  # 3x^2 (a4=0)
        den = fadd(ay, ay)
        m = fdiv(num, den)
    else:
        m = fdiv(fsub(by, ay), fsub(bx, ax))
    nx = fsub(fsub(fsq(m), ax), bx)  # lambda^2 - x1 - x2 (a4=0)
    ny = fsub(fmul(m, fsub(ax, nx)), ay)
    return (nx, ny)

def ec_neg(A):
    if A is O: return O
    x, y = A
    return (x, fneg(y))

def ec_mul(k, A):
    if k == 0 or A is O: return O
    if k < 0: k = -k  # assume k >= 0 here
    R = O
    addend = A
    while k:
        if k & 1: R = ec_add(R, addend)
        addend = ec_add(addend, addend)
        k >>= 1
    return R

def ec_eq(A, B):
    if A is O and B is O: return True
    if A is O or B is O: return False
    return A[0] == B[0] and A[1] == B[1]

if __name__ == "__main__":
    import re, time
    # parse generator points from source.sage: E(re_im*i + re, im_im*i + im, 1)
    src = open("source.sage").read()
    def parse_pt(var):
        m = re.search(var + r" = E\((.+?), 1\)", src, re.S)
        body = m.group(1)
        parts = body.split(",")
        # each part: A*i + B
        def coeff(part):
            mm = re.match(r"\s*(\d+)\*i \+ (\d+)\s*$", part)
            im_c, re_c = int(mm.group(1)), int(mm.group(2))
            return (re_c % p, im_c % p)
        return (coeff(parts[0]), coeff(parts[1]))
    P = parse_pt("P")
    Q = parse_pt("Q")
    print("P on curve:", ec_on_curve(P))
    print("Q on curve:", ec_on_curve(Q))

    # group-law self-test (fast): associativity spot checks + order-1/2 identities
    def selftest():
        ok = True
        R = ec_add(P, Q); S = ec_add(ec_add(P, P), Q)
        ok &= ec_eq(ec_add(R, ec_neg(P)), Q)            # (P+Q)-P == Q
        ok &= ec_eq(ec_add(ec_add(P, Q), ec_neg(Q)), P)  # (P+Q)-Q == P
        ok &= ec_eq(ec_add(ec_mul(2, P), ec_neg(P)), P)  # 2P - P == P
        ok &= ec_eq(ec_add(P, ec_neg(P)), O)             # P + (-P) == O
        ok &= ec_on_curve(ec_add(P, Q))                  # sum stays on curve
        ok &= ec_on_curve(ec_add(P, P))
        return ok
    print("group-law selftest:", selftest())
    if not selftest():
        print("ABORT: group law inconsistent")
        raise SystemExit(1)

    # factorization of p+1 = 37 * 2^64 * L
    def factor_pp1():
        from sympy import factorint
        return dict(factorint(P1))
    fac = factor_pp1()
    primes = sorted(fac.keys())
    print("num prime factors of p+1:", len(primes), "largest:", max(primes))

    # order of a point via prime-power projection:
    # R_l = ((p+1)^2 / l^{2k}) * R has pure l-power order l^{v_l(ord R)}
    def point_order(R, tag=""):
        o = 1
        for l in primes:
            proj = ORDER2 // (l ** (2 * fac[l]))
            Rl = ec_mul(proj, R)
            e = 0
            cur = Rl
            cap = 2 * fac[l] + 2
            while cur is not O and e < cap:
                cur = ec_mul(l, cur)
                e += 1
            if cur is not O:
                raise RuntimeError(f"{tag}: l={l} order loop did not converge (points on wrong curve?)")
            o *= l ** e
        print(f"{tag} order bits: {o.bit_length()}")
        return o
    t0 = time.time()
    oP = point_order(P, "P")
    oQ = point_order(Q, "Q")
    print("order time: %.1fs" % (time.time() - t0))
    print("oP == (p+1)^2:", oP == ORDER2, " oQ == (p+1)^2:", oQ == ORDER2)
    print("oP == (p+1):", oP == P1)

    # first ciphertext points: on E (j=1728)?
    ct = json.load(open("output.txt"))
    A = (from_pair(ct[0]["P"]["x"]), from_pair(ct[0]["P"]["y"]))
    B = (from_pair(ct[0]["Q"]["x"]), from_pair(ct[0]["Q"]["y"]))
    print("ct[0] P on E:", ec_on_curve(A))
    print("ct[0] Q on E:", ec_on_curve(B))

"""Recover b for one ciphertext byte by computing the order of A=phi(P) on the codomain.

ord(A) should equal 37*L/b (isogeny of degree 2^64*b maps P (order m=37*2^64*L) to a point
of order m / gcd(m, 2^64 b) = 37*L/b).  Then b = 37*L / ord(A).

We compute ord(A) via prime-power projection using M = (37*2^32*L)^2 = 37^2 * 2^64 * L^2,
a known multiple of the codomain order for every byte b (since #E' = M/b).
"""
import ec2 as F
import json, math, re, time
from functools import lru_cache

p = F.p
L = 1
for i in range(1, 256):
    L = math.lcm(L, i)
M37 = 37
M = M37*M37 * (2**64) * L*L   # multiple of #E' for all bytes
m = p + 1
print("M bits:", M.bit_length(), " M == m^2?", M == m*m)

# ---- codomain EC over F_{p^2}: y^2 = x^3 + a4 x + a6 ----
cod = json.load(open("codomain.json"))
a4 = (cod["a4"][0] % p, cod["a4"][1] % p)
a6 = (cod["a6"][0] % p, cod["a6"][1] % p)
O = None

def on_curve(pt):
    if pt is O: return True
    x, y = pt
    rhs = F.fadd(F.fadd(F.fmul(F.fmul(x,x), x), F.fmul(a4, x)), a6)
    return F.fsq(y) == rhs

def add(A, B):
    if A is O: return B
    if B is O: return A
    ax, ay = A; bx, by = B
    if ax == bx:
        if (ay[0]+by[0]) % p == 0 and (ay[1]+by[1]) % p == 0:
            return O
        num = F.fadd(F.fmul(F.fmul((3%p,0), ax), ax), a4)
        den = F.fadd(ay, ay)
        sl = F.fdiv(num, den)
    else:
        sl = F.fdiv(F.fsub(by, ay), F.fsub(bx, ax))
    nx = F.fsub(F.fsub(F.fsq(sl), ax), bx)
    ny = F.fsub(F.fmul(sl, F.fsub(ax, nx)), ay)
    return (nx, ny)

def neg(A):
    if A is O: return O
    x, y = A
    return (x, F.fneg(y))

def mul(k, A):
    if k == 0 or A is O: return O
    if k < 0: return neg(mul(-k, A))
    R = O; addend = A
    while k:
        if k & 1: R = add(R, addend)
        addend = add(addend, addend)
        k >>= 1
    return R

def eq(A, B):
    if A is O and B is O: return True
    if A is O or B is O: return False
    return A[0]==B[0] and A[1]==B[1]

# recover A, B from ct[0]
ct = json.load(open("output.txt"))
A = ((ct[0]["P"]["x"][0]%p, ct[0]["P"]["x"][1]%p),
     (ct[0]["P"]["y"][0]%p, ct[0]["P"]["y"][1]%p))
B = ((ct[0]["Q"]["x"][0]%p, ct[0]["Q"]["x"][1]%p),
     (ct[0]["Q"]["y"][0]%p, ct[0]["Q"]["y"][1]%p))
print("A on codomain:", on_curve(A), " B on codomain:", on_curve(B))

# primes and exponents in M = 37^2 * 2^64 * L^2
def v_l(n, l):
    e = 0
    while n % l == 0:
        n //= l; e += 1
    return e
primes = []
n = L
d = 2
tmp = L
for d in range(2, 256):
    if L % d == 0:
        # is d prime?
        if all(d % q for q in range(2, int(d**0.5)+1)):
            primes.append(d)
exps = {37: 2, 2: 64}
for l in primes:
    exps[l] = 2 * v_l(L, l)
all_primes = sorted(set([37,2] + primes))
print("num primes:", len(all_primes), " max exp:", max(exps.values()))

# ---- prime-power projection for order of A ----
t0 = time.time()
ordA = 1
detail = {}
for l in all_primes:
    e = exps[l]
    # R_l = (M / l^e) * A  -> has order dividing l^e
    coeff = M // (l**e)
    Rl = mul(coeff, A)
    # find exact order (pure l-power)
    cnt = 0
    cur = Rl
    cap = e + 1
    while cur is not O and cnt < cap:
        cur = mul(l, cur)
        cnt += 1
    if cur is not O:
        print(f"  WARN l={l}: did not converge (cnt={cnt})")
    ordA *= l**cnt
    detail[l] = cnt
    if cnt:
        print(f"  l={l}: v={cnt} (exp in M was {e})  [elapsed {time.time()-t0:.1f}s]")
print("ord(A) bits:", ordA.bit_length())
print("ord(A) == 37*L/b for some byte?")
target = 37 * L
for b in range(1, 256):
    if target % b == 0 and target // b == ordA:
        print(f"  => b = {b}  (byte {bytes([b])!r})")
        break
else:
    # maybe ord(A) divides 37*L/b (not equal); find b such that ordA | 37*L/b
    cands = [b for b in range(1,256) if (37*L//b) % ordA == 0]
    print("  no exact match; b with ordA | 37*L/b:", cands)
print("total time: %.1fs" % (time.time()-t0))

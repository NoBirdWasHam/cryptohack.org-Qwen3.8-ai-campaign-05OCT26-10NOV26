"""andre_encoding final solve.

Setup: E/F_p2: y^2=x^3+1, #E(F_p2)=m^2, m=p+1=37*2^64*L. Per flag byte b:
  d=2^64*b, R=(37L/b)(P+sQ) generates kernel, phi:E->E'=E/<R>, ct=(phi(P),phi(Q)).
On E': X'=(37L/b')A, Y'=(37L/b')B satisfies X' + s Y' = O  <=>  (37L/b')(P+sQ) in <R>
  <=> b' | b   (deterministic: component-1 congruence j*b'' = b mod l^{>v_l(b)} unsolvable).
Membership test per prime l of N*=37^2*2^64*L^2 (universal multiple of #E'):
  project X',Y' to l-primary part; X_l in <Y_l> iff ord(Y_l)*X_l = O (rank<=2 l-group).
Then b = prod l^{k_l}. Validate first 7 bytes == 'crypto{'.
"""
from gmpy2 import mpz
import json, math, sys, time

L = 1
for i in range(1, 256):
    L = math.lcm(L, i)
p = mpz(37) * (mpz(2) ** 64) * mpz(L) - 1
m = p + 1
Nstar = mpz(37*37) * (mpz(2) ** 64) * mpz(L*L)

def fadd(a,b): return ((a[0]+b[0])%p, (a[1]+b[1])%p)
def fsub(a,b): return ((a[0]-b[0])%p, (a[1]-b[1])%p)
def fneg(a): return ((-a[0])%p, (-a[1])%p)
def fmul(a,b): return ((a[0]*b[0]-a[1]*b[1])%p, (a[0]*b[1]+a[1]*b[0])%p)
def fsq(a): return ((a[0]*a[0]-a[1]*a[1])%p, (2*a[0]*a[1])%p)
def fdiv(a,b):
    nb = (b[0]*b[0]+b[1]*b[1]) % p
    inv = pow(nb, -1, p)
    return fmul(a, fmul((b[0], (-b[1])%p), (inv, 0)))

O = None
class Curve:
    def __init__(s, a4, a6): s.a4, s.a6 = a4, a6
    def on(s, pt):
        if pt is O: return True
        x,y = pt
        return fsq(y) == fadd(fadd(fmul(fmul(x,x),x), fmul(s.a4,x)), s.a6)
    def add(s, A, B):
        if A is O: return B
        if B is O: return A
        ax,ay = A; bx,by = B
        if ax == bx:
            if (ay[0]+by[0])%p == 0 and (ay[1]+by[1])%p == 0: return O
            sl = fdiv(fadd(fmul(fmul((mpz(3),0),ax),ax), s.a4), fadd(ay,ay))
        else:
            sl = fdiv(fsub(by,ay), fsub(bx,ax))
        nx = fsub(fsub(fsq(sl),ax),bx)
        ny = fsub(fmul(sl,fsub(ax,nx)),ay)
        return (nx,ny)
    def mul(s, k, A):
        if A is O or k == 0: return O
        if k < 0: return s.mul(-k, (A[0], fneg(A[1])))
        R = O; ad = A
        k = int(k)
        while k:
            if k & 1: R = s.add(R, ad)
            ad = s.add(ad, ad)
            k >>= 1
        return R

def is_prime(n):
    return all(n % q for q in range(2, int(n**0.5)+1))
primes = [d for d in range(2, 256) if is_prime(d)] + [37]
primes = sorted(set(primes))
def v_l(nn, l):
    e = 0
    while nn % l == 0: nn //= l; e += 1
    return e
# exponents in Nstar = 37^2 * 2^64 * L^2
expN = {l: (64 if l == 2 else (2 if l == 37 else 0) + 2*v_l(L, l)) for l in primes}
print("primes:", len(primes), flush=True)

ct = json.load(open("output.txt"))
def ptj(e): return ((mpz(e["x"][0]) % p, mpz(e["x"][1]) % p),
                    (mpz(e["y"][0]) % p, mpz(e["y"][1]) % p))

def recover_curve(A, B):
    def rhs(pt):
        x,y = pt
        return fsub(fsq(y), fmul(fmul(x,x),x))
    RA, RB = rhs(A), rhs(B)
    den = fsub(A[0], B[0])
    if den == (mpz(0), 0): return None
    a4 = fdiv(fsub(RA, RB), den)
    a6 = fsub(RA, fmul(a4, A[0]))
    return Curve(a4, a6)

def passes_prime(C, A, B, l, k):
    """candidate b'' = l^k : X''=(37L/l^k)A etc.; test X_l in <Y_l>."""
    base = mpz(37*L)
    e = expN[l]
    coeff = base * (Nstar // (mpz(l) ** (e + k)))
    X = C.mul(coeff, A); Y = C.mul(coeff, B)
    # order of Y (a power of l)
    kk = 0; cur = Y
    while cur is not O and kk <= e + k + 2:
        cur = C.mul(l, cur); kk += 1
    if cur is not O:
        return None  # anomaly: order not an l-power within bound
    # need l^kk * X == O
    Xl = X
    for _ in range(kk):
        Xl = C.mul(l, Xl)
    return Xl is O

t0 = time.time()
flag = []
for idx, entry in enumerate(ct):
    A = ptj(entry["P"]); B = ptj(entry["Q"])
    if A == (mpz(0), mpz(0)) and B == (mpz(0), mpz(0)):
        flag.append(0); print(idx, "O-point byte 0", flush=True); continue
    C = recover_curve(A, B)
    if C is None or not C.on(A) or not C.on(B):
        print(idx, "CURVE RECOVERY FAILED", flush=True); flag.append(63); continue
    b = 1
    anom = []
    for l in primes:
        if l ** 1 > 255 // b and l > 1:
            pass
        k = 0
        while True:
            r = passes_prime(C, A, B, l, k + 1)
            if r is None:
                anom.append((l, k+1)); break
            if r:
                k += 1
                if b * (l ** (k)) > 255: break
            else:
                break
        if k:
            b *= l ** k
    # sanity: b must satisfy all prime tests; recheck composite membership cheaply
    flag.append(b)
    ch = chr(b) if 32 <= b < 127 else "?"
    print(f"byte {idx}: b={b} {ch!r} anom={anom} [{time.time()-t0:.0f}s]", flush=True)

s = "".join(chr(x) for x in flag)
print("FLAG:", s, flush=True)
print("prefix ok:", s.startswith("crypto{"), flush=True)
with open("flag_candidate.txt", "w") as f:
    f.write(s + "\n")

# E2E validation of the attack chain on a small instance (prime_length=56)
import sys, math
from collections import namedtuple
from Crypto.Util.number import getPrime, isPrime, getRandomRange
from Crypto.Cipher import AES
Complex = namedtuple("Complex", ["re", "im"])
def complex_mult(c1, c2, modulus):
    return Complex((c1.re*c2.re - c1.im*c2.im) % modulus, (c1.re*c2.im + c1.im*c2.re) % modulus)
def complex_pow(c, exp, modulus):
    result = Complex(1, 0)
    while exp > 0:
        if exp & 1: result = complex_mult(result, c, modulus)
        c = complex_mult(c, c, modulus); exp >>= 1
    return result
def generate_params(prime_length):
    while True:
        p = getPrime(prime_length)
        if p % 4 == 3:
            if p % 3 == 2:
                q, r = (p-1)//2, (p+1)//12
                if isPrime(q) and isPrime(r): break
            else:
                q, r = (p-1)//6, (p+1)//4
                if isPrime(q) and isPrime(r): break
    n = p**2; order = p*q*r
    while True:
        re = getRandomRange(1, n); im = getRandomRange(1, n)
        g = complex_pow(Complex(re, im), 24, n)
        if (complex_pow(g, order, n) == Complex(1,0) and
            all(complex_pow(g, order//x, n) != Complex(1,0) for x in (p,q,r))):
            return g, order, n, p, q, r

PL = int(sys.argv[1]) if len(sys.argv)>1 else 56
g, order, n, p, q, r = generate_params(PL)
k = getRandomRange(0, 2**256)
pk = complex_pow(g, k, n)
print("p bits:", p.bit_length(), "p%12:", p%12)

def cmul(a,b,m): return ((a[0]*b[0]-a[1]*b[1])%m, (a[0]*b[1]+a[1]*b[0])%m)
def cpow(a,e,m):
    rr=(1,0)
    while e:
        if e&1: rr=cmul(rr,a,m)
        a=cmul(a,a,m); e>>=1
    return rr
gp_ = cpow(g, order//p, n)
ug = (((gp_[0]-1)//p) % p, (gp_[1]//p) % p)
X = cpow(pk, order//p, n)
uX = (((X[0]-1)//p) % p, (X[1]//p) % p)
norm = (ug[0]**2+ug[1]**2) % p
ninv = pow(norm, p-2, p)
uginv = (ug[0]*ninv % p, (-ug[1])*ninv % p)
k0 = (uX[0]*uginv[0] - uX[1]*uginv[1]) % p
assert k % p == k0, "k0 FAIL"
print("k0 ok")
gn = (g[0]**2+g[1]**2) % n
ginv = (g[0]*pow(gn,-1,n)%n, (-g[1])*pow(gn,-1,n)%n)
T = cmul(pk, cpow(ginv, k0, n), n)
aq = cpow(g, p*r, n)
tq = cpow(T, r, n)
assert (tq[1] % p) == 0 and (aq[1] % p) == 0, "not in F_p!"
base, tgt = aq[0] % p, tq[0] % p
from sympy.ntheory import discrete_log
c1q = discrete_log(p, tgt, base)  # log in F_p* (order 2q; result mod 2q?)
print("c1q (mod q check via pow):", pow(base, c1q, p) == tgt)
kreal_c1 = (k - k0) // p
for cand in [c1q % q, c1q]:
    pass
t_try = 0
c1max = (2**256-1-k0)//p
found = False
c1q = c1q % q
while True:
    c1 = c1q + q*t_try
    if c1 > c1max or t_try > 5000000: break
    if c1 == kreal_c1:
        print("FOUND c1 at t =", t_try); found=True; break
    t_try += 1
print("candidates tried:", t_try, "found:", found)
# also verify c1q correct
print("c1q check:", kreal_c1 % q == c1q)

# quick diagnostic: run port machinery on synthetic 512-bit case, print row polys
import solve_coppersmith_port as S
import math, time
from fractions import Fraction
from fpylll import IntegerMatrix, LLL
from sympy import Poly, ZZ, symbols
x = symbols('x')
import random
random.seed(1234)
def gp(b):
    while True:
        c = random.getrandbits(b) | (1 << (b-1)) | 1
        if __import__('sympy').isprime(c): return c
p,q = gp(512), gp(512)
n = p*q
D = 63**14
hint = math.isqrt(D*D*p) + math.isqrt(D*D*q)
pAs = S.p_approx_from_hint(hint, D, n)
pA = pAs[0]
print("delta bits:", (p-pA).bit_length(), "sign", 1 if p>=pA else -1)
N, f, X = n, [pA,1], 2**180
d=1; m=6; t=9
rows = [S.pscale(S.ppow(f,i), N**(m-i)) for i in range(m)]
fmax = S.ppow(f,m)
rows += [S.pshift(fmax,i) for i in range(t)]
w=15; ncols=15
M = IntegerMatrix(w,ncols,int_type='mpz')
Xp=[1]*ncols
for j in range(1,ncols): Xp[j]=Xp[j-1]*X
for r,row in enumerate(rows):
    for j,c in enumerate(row[:ncols]): M[r,j]=c*Xp[j]
t0=time.time(); LLL.reduction(M, delta=0.99); print("LLL", time.time()-t0)
for r in range(w):
    b=[int(M[r,j]) for j in range(ncols)]
    if all(t_ % Xp[j_]==0 for j_,t_ in enumerate(b)):
        h=S.strip([b[j]//Xp[j] for j in range(ncols)])
        normsq = sum(v*v for v in [int(M[r,j]) for j in range(ncols)])
        print(f"row {r}: deg {len(h)-1} coeffs_bits {[abs(v).bit_length() for v in h][:4]}...")
        t0=time.time()
        P=Poly(h, x, domain=ZZ)
        fl = P.factor_list()
        print(f"   factor_list in {time.time()-t0:.1f}s -> {[(len(f.all_coeffs()),mu) for f,mu in fl[1]]}")
        t0=time.time()
        rts = P.real_roots()
        print(f"   real_roots in {time.time()-t0:.1f}s: {[str(rr)[:15] for rr in rts][:6]}")
        for rr in rts:
            if getattr(rr,'is_rational',False) and rr.q==1:
                g = math.gcd(N, pA+int(rr))
                print("   INT ROOT", int(rr), "-> gcd factor?", 1<g<N)
    else:
        print(f"row {r}: NOT integral after descale")

# raw-int check: do LLL polys vanish at x0? (ascending coeff lists, plain Python)
import solve_coppersmith_port as S
import math, random
from fpylll import IntegerMatrix, LLL
random.seed(1234)
from sympy import isprime
def gp(b):
    while True:
        c = random.getrandbits(b) | (1 << (b-1)) | 1
        if isprime(c): return c
p,q = gp(512), gp(512)
n = p*q; D = 63**14
hint = math.isqrt(D*D*p) + math.isqrt(D*D*q)
pA = S.p_approx_from_hint(hint, D, n)[0]
x0 = p - pA
print("x0 =", x0)
N, X = n, 2**180
m,t = 6,9
rows = [S.pscale(S.ppow([pA,1],i), N**(m-i)) for i in range(m)]
fmax = S.ppow([pA,1],m)
rows += [S.pshift(fmax,i) for i in range(t)]
w=15; ncols=15
M = IntegerMatrix(w,ncols,int_type='mpz')
Xp=[1]*ncols
for j in range(1,ncols): Xp[j]=Xp[j-1]*X
for r,row in enumerate(rows):
    for j,c in enumerate(row[:ncols]): M[r,j]=c*Xp[j]
LLL.reduction(M, delta=0.99)
def horner(fl, t):
    acc=0
    for cf in reversed(fl): acc = acc*t + cf
    return acc
for r in range(4):
    b=[int(M[r,j]) for j in range(ncols)]
    h=[b[j]//Xp[j] for j in range(ncols)]
    v = horner(h, x0)
    print(f"P{r}: h(x0)==0? {v==0}, |h(x0)| bits {abs(v).bit_length() if v else 0}")

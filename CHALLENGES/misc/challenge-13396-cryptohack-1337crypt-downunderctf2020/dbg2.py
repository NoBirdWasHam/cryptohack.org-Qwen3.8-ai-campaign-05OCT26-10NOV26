# does the ported lattice vanish at x0?
import solve_coppersmith_port as S
import math, random
from fpylll import IntegerMatrix, LLL
from sympy import Poly, ZZ, symbols, gcd as sgcd
x = symbols('x')
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
print("x0 bits:", x0.bit_length(), "sign", "+" if x0>=0 else "-")
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
Ps=[]
for r in range(w):
    b=[int(M[r,j]) for j in range(ncols)]
    h=S.strip([b[j]//Xp[j] for j in range(ncols)])
    Ps.append(Poly(h, x, domain=ZZ))
# exact h(x0) for first rows
for r in range(3):
    v = Ps[r].eval(x0)
    print(f"P{r}: deg {Ps[r].degree()} h(x0)==0? {v==0}   h(x0) bits {abs(int(v)).bit_length() if v else 0}")
g = sgcd(Ps[0], Ps[1])
print("gcd(P0,P1) deg:", g.degree(), [str(c)[:12] for c in g.all_coeffs()])
g2 = sgcd(Ps[0], Ps[2])
print("gcd(P0,P2) deg:", g2.degree())
# is (x-x0) a factor of P0 over ZZ?
d = Poly([ -x0, 1], x, domain=ZZ)
print("P0 mod (x-x0) ==0 ?", (Ps[0].div(d)[1]==0))
# smallest-norm row check
norms = [ (sum(int(M[r,j])**2 for j in range(ncols)), r) for r in range(w)]
norms.sort()
print("shortest rows:", [(nr.bit_length(), r) for nr,r in norms[:5]])

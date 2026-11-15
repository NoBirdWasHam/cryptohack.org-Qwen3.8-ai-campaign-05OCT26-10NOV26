import random, time
from fpylll import IntegerMatrix, LLL, BKZ

random.seed(1234)
bits = 512
n = (random.getrandbits(bits//2)<<1|1) * (random.getrandbits(bits//2<<1 & (bits-1)|1 if False else bits//2)<<1|1) if False else None
p = random.getrandbits(bits//2) | 1 | (1<<255)
q = random.getrandbits(bits//2) | 1
n = p*q
print('n bits', n.bit_length())
m = random.randrange(2, n)
N = 40
C2 = 1 << (n.bit_length() - 16)
c = 5 * C2 // 2
R, X = [], []
while len(R) < N:
    r = random.randrange(1, n)
    x = r*m % n
    if 2*C2 <= x < 3*C2:
        R.append(r); X.append(x)
import math
print('gcds', [math.gcd(r,n) for r in R[:3]])
kappa = C2//2
err_true = [x - c for x in X]
print('max |err|', max(abs(e) for e in err_true), 'kappa', kappa)

B = IntegerMatrix(N+1, N)
for j in range(N): B[0,j] = R[j]
for i in range(N): B[i+1,i] = n
LLL.reduction(B, delta=0.99)
print('is_reduced B:', LLL.is_reduced(B))

E = IntegerMatrix(N+2, N+1)
for i in range(N+1):
    for j in range(N): E[i,j] = B[i,j]
for j in range(N): E[N+1,j] = c
E[N+1,N] = kappa

def norms(M):
    out = []
    for i in range(M.nrows):
        out.append(sum(int(M[i,j])**2 for j in range(M.ncols)))
    return min(out)
print('min norm E before BKZ', norms(E).bit_length()/2)
BKZ.reduction(E, BKZ.EasyParam(40))
print('min norm E after BKZ', norms(E).bit_length()/2, 'true sol norm', sum(e*e for e in err_true+[kappa]).bit_length()/2)

# manual membership check: is (X-c, kappa) in lattice E? i.e. solve coeff vector? skip; just brute extraction
found = None
for i in range(N+2):
    a = int(E[i,N])
    if abs(a) != kappa: continue
    sgn = 1 if a>0 else -1
    err = [int(E[i,j])*sgn for j in range(N)]
    for mode in (1,-1):
        v = [c + mode*err[j] for j in range(N)]
        if all(2*C2 <= x < 3*C2 for x in v):
            found = (mode, v)
    if found: break
print('found?', bool(found))
if found:
    v = found[1]
    mm = v[0]*pow(R[0],-1,n)%n
    print('match:', mm==m)

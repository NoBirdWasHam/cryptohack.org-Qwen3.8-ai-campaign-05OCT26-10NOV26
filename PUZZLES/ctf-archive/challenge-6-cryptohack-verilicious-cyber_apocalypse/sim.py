# Mini sim: same lattice/CVP pipeline on small params to validate glue.
import random, time
from fpylll import IntegerMatrix, LLL, BKZ

random.seed(1234)
bits = 512
n = 1
while n.bit_length() < bits:
    n = random.getrandbits(bits) | 1
    if n % 30030 == 0: n = 0
# make n a product of two random primes for realism (any odd n fine)
n = (random.getrandbits(bits//2)<<1|1) * (random.getrandbits(bits//2)<<1|1)
m = random.randrange(2, n)
N = 40
C2 = 1 << (n.bit_length() - 16)   # keep same ratio width ~ n/2^15.5
c = 5 * C2 // 2
R = []
while len(R) < N:
    r = random.randrange(1, n)
    if 2*C2 <= r*m % n < 3*C2:
        R.append(r)
t0 = time.time()
B = IntegerMatrix(N+1, N)
for j in range(N): B[0,j] = R[j]
for i in range(N): B[i+1,i] = n
LLL.reduction(B, delta=0.99)
kappa = C2//2
E = IntegerMatrix(N+1, N+1)
for i in range(N+1):
    for j in range(N): E[i,j] = B[i,j]
for j in range(N): E[N,j] = c
E[N,N] = kappa
BKZ.reduction(E, BKZ.EasyParam(40))
found = None
for i in range(N+1):
    if abs(E[i,N]) == kappa:
        sgn = 1 if E[i,N] > 0 else -1
        err = [E[i,j]*sgn for j in range(N)]
        for mode in (1,-1):
            v = [c + mode*err[j] for j in range(N)]
            if all(2*C2 <= x < 3*C2 for x in v):
                found = v; break
    if found: break
if found is None:
    print('FAIL: solution vector not surfaced'); raise SystemExit
mm = found[0]*pow(R[0],-1,n)%n
print('match:', mm == m, 'time', time.time()-t0)

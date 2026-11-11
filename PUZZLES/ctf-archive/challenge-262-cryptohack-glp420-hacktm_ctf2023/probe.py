import time
from random import randrange
from solve_v2 import q, n, m, centered
q_ = q
a = [randrange(1, q_) for _ in range(n)]
s = [randrange(-1, 2) for _ in range(n)]
e = [randrange(-1, 2) for _ in range(n)]
from solve_v2 import mul
t = [(mul(a, s)[i] + e[i]) % q_ for i in range(n)]
zeta = 1
t0 = time.time()
af = [sum(zeta**j * a[k + j*m] for j in range(4)) % q_ for k in range(m)]
tf = [sum(zeta**j * t[k + j*m] for j in range(4)) % q_ for k in range(m)]
M = [[centered(af[k-mm]) if k >= mm else centered(zeta*af[m+k-mm]) for mm in range(m)] for k in range(m)]
print("fold %.1fs" % (time.time()-t0), flush=True)
from fpylll import IntegerMatrix, LLL, CVP
t0 = time.time()
Lm = IntegerMatrix(2*m, 2*m)
for k in range(m):
    Lm[k, k] = 1
    for r2 in range(m):
        Lm[k, m+r2] = M[r2][k]
for k in range(m):
    Lm[m+k, m+k] = q_
print("build %.1fs" % (time.time()-t0), flush=True)
target = [0]*m + [centered(tf[k]) for k in range(m)]
t0 = time.time()
LLL.reduction(Lm)
print("LLL %.1fs" % (time.time()-t0), flush=True)
t0 = time.time()
v = CVP.babai(Lm, target)
print("babai %.1fs" % (time.time()-t0), flush=True)
diff = [int(target[i]) - int(v[i]) for i in range(2*m)]
sf = [centered(-x) for x in diff[:m]]
ef = [centered(x) for x in diff[m:]]
print("maxabs s_fold", max(map(abs,sf)), " e_fold", max(map(abs,ef)))

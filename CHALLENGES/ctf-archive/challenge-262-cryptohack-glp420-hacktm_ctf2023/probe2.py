import time
from random import randrange, seed
from solve_v2 import q, n, centered, mul, twelve_roots
seed(1)
a = [randrange(1, q) for _ in range(n)]
s = [randrange(-1, 2) for _ in range(n)]
e = [randrange(-1, 2) for _ in range(n)]
t = [(mul(a, s)[i] + e[i]) % q for i in range(n)]
zetas = twelve_roots()
zeta = zetas[1]
d = 35
nf = 12
zp = [pow(zeta, j, q) for j in range(nf)]
af = [sum(zp[j] * a[k + j*d] for j in range(nf)) % q for k in range(d)]
tf = [sum(zp[j] * t[k + j*d] for j in range(nf)) % q for k in range(d)]
M = [[centered(af[k-mm]) if k >= mm else centered(zeta*af[d+k-mm]) for mm in range(d)] for k in range(d)]
from fpylll import IntegerMatrix, LLL, CVP, GSO
Lm = IntegerMatrix(2*d, 2*d)
for k in range(d):
    Lm[k, k] = 1
    for r2 in range(d):
        Lm[k, d+r2] = M[r2][k]
for k in range(d):
    Lm[d+k, d+k] = q
target = [0]*d + [centered(x) for x in tf]
t0 = time.time()
LLL.reduction(Lm)
print("LLL %.2fs" % (time.time()-t0))
g = GSO(Lm)
norms = [g[i][i] for i in range(2*d)]
print("min/max GS norm^2: %.1f / %.1f" % (min(norms), max(norms)))
# true folded target for reference
s_fold = [sum(zp[j]*s[k+j*d] for j in range(nf)) for k in range(d)]
e_fold = [sum(zp[j]*e[k+j*d] for j in range(nf)) for k in range(d)]
print("true norms:", sum(x*x for x in s_fold+e_fold) ** .5, "max", max(map(abs, s_fold+e_fold)))
v = CVP.babai(Lm, target)
diff = [int(target[i]) - int(v[i]) for i in range(2*d)]
sf = [centered(-x) for x in diff[:d]]
ef = [centered(x) for x in diff[d:]]
print("babai max:", max(map(abs, sf+ef)))
print("exact:", sf == [sum(pow(zeta,j,q)*s[k+j*d] for j in range(nf)) for k in range(d)])

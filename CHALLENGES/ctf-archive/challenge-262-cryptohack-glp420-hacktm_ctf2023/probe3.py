import sys, time
from random import randrange
from solve_v2 import q, n, centered, mul
a = [randrange(1,q) for _ in range(n)]
s = [randrange(-1,2) for _ in range(n)]
e = [randrange(-1,2) for _ in range(n)]
t = [(mul(a,s)[i]+e[i])%q for i in range(n)]
from fpylll import IntegerMatrix, LLL, CVP
d = n//2; sign=1
af=[(a[k]+sign*a[k+d])%q for k in range(d)]
tf=[(t[k]+sign*t[k+d])%q for k in range(d)]
M=[[centered(af[k-mm]) if k>=mm else centered(sign*af[d+k-mm]) for mm in range(d)] for k in range(d)]
Lm=IntegerMatrix(2*d,2*d)
for k in range(d):
    Lm[k,k]=1
    for r2 in range(d): Lm[k,d+r2]=M[r2][k]
for k in range(d): Lm[d+k,d+k]=q
target=[0]*d+[centered(x) for x in tf]
utrue=[s[k]+s[k+d] for k in range(d)]
etrue=[e[k]+e[k+d] for k in range(d)]
meth, ft, prec = sys.argv[1], (sys.argv[2] or None), int(sys.argv[3])
t0=time.time()
LLL.reduction(Lm, method=meth, float_type=ft, precision=prec)
print("%s/%s/%s LLL %.1fs" % (meth, ft, prec, time.time()-t0), flush=True)
v=CVP.babai(Lm,target)
diff=[int(target[i])-int(v[i]) for i in range(2*d)]
u=[centered(-x) for x in diff[:d]]
ef=[centered(x) for x in diff[d:]]
print("max", max(map(abs,u+ef)), "exact:", u==utrue and ef==etrue, flush=True)

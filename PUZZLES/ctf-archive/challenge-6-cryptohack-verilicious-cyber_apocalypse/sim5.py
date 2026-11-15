import random, time, math
from fpylll import IntegerMatrix, LLL, BKZ
random.seed(7)
bits=512
p=random.getrandbits(bits//2)|3|(1<<255)
while True:
    q=random.getrandbits(bits//2)|3
    if __import__('math').gcd(p,q)==1 and (p*q).bit_length()==bits: n=p*q; break
m=random.randrange(2,n)
N=64
C2=1<<(n.bit_length()-16); c=(5*C2)//2; kappa=C2//2
R=[]
while len(R)<N:
    r=random.randrange(1,n)
    if math.gcd(r,n)!=1: continue
    if 2*C2<=r*m%n<3*C2: R.append(r)
inv=pow(R[0],-1,n)
t0=time.time()
B=IntegerMatrix(N,N)
for j in range(N): B[0,j]=R[j]*inv%n
B[0,0]=1
for i in range(1,N): B[i,i]=n
LLL.reduction(B, delta=0.99)
E=IntegerMatrix(N+1,N+1)
for i in range(N):
    for j in range(N): E[i,j]=B[i,j]
for j in range(N): E[N,j]=c
E[N,N]=kappa
BKZ.reduction(E, BKZ.EasyParam(40))
best=None
for i in range(N+1):
    a=int(E[i,N])
    if abs(a)!=kappa: continue
    sgn=1 if a>0 else -1
    err=[int(E[i,j])*sgn for j in range(N)]
    for mode in (1,-1):
        v=[c+mode*err[j] for j in range(N)]
        if all(2*C2<=x<3*C2 for x in v): best=v; break
    if best: break
print('surfaced:', bool(best), time.time()-t0)
if best:
    print('match:', best[0]*inv%n==m)

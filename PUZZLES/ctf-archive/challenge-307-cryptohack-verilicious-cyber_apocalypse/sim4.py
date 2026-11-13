import random, time
from fractions import Fraction
from fpylll import IntegerMatrix, LLL, CVP
random.seed(1234)
bits=512
p=random.getrandbits(bits//2)|3|(1<<255)
while True:
    q=random.getrandbits(bits//2)|3
    n=p*q
    if n.bit_length()==bits and __import__('math').gcd(p,q)==1: break
m=random.randrange(2,n)
N=40
C2=1<<(n.bit_length()-16); c=(5*C2)//2; kappa=C2//2
R=[]
while len(R)<N:
    r=random.randrange(1,n)
    if __import__('math').gcd(r,n)!=1: continue
    if 2*C2<=r*m%n<3*C2: R.append(r)
inv=pow(R[0],-1,n)
t0=time.time()
B=IntegerMatrix(N,N)
for j in range(N): B[0,j]=R[j]*inv%n
B[0,0]=1
for i in range(1,N): B[i,i]=n
LLL.reduction(B, delta=0.99)
tgt=[c]*N
r2=(N+1)*kappa*kappa
sol=CVP.closest_vector(B, tgt, radius=Fraction(r2))
print('CVP returned', type(sol), time.time()-t0)
v=[int(x) for x in sol] if sol is not None else None
print('box ok:', v is not None and all(2*C2<=x<3*C2 for x in v))
if v: 
    mm=v[0]*inv%n
    print('match:', mm==m)

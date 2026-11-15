import random, sympy, sys
print("start", flush=True)
p=22940775619019322596732579295592937688786860238433707977002010287174316620572298541233055185492572749161011953122651
A,B=-3,2697448053935541741976221051345108825177671050689533270507
Bi=pow(B,-1,p)
a2=A*Bi%p; a4=Bi
O=None
print("consts ok; p mod 4 =", p%4, flush=True)
def sqrt_mod(n,p):
    n%=p
    if n==0: return 0
    if pow(n,(p-1)//2,p)!=1: return None
    if p%4==3: return pow(n,(p+1)//4,p)
    q=p-1;s=0
    while q%2==0: q//=2;s+=1
    z=2
    while pow(z,(p-1)//2,p)!=p-1: z+=1
    m,c,t,r=s,pow(z,q,p),pow(n,q,p),pow(n,(q+1)//2,p)
    while t!=1:
        i=0;t2=t
        while t2!=1: t2=t2*t2%p;i+=1
        bb=pow(c,1<<(m-i-1),p); m,c,t,r=i,bb*bb%p,t*bb*bb%p,r*bb%p
    return r
def f(x): return (x*x*x+A*x*x+x)*Bi%p
def pdbl(P):
    if P is O: return O
    x,y=P
    if y==0: return O
    lam=(3*x*x+2*A*x+1)*pow(2*y,-1,p)%p
    x3=(lam*lam*Bi - A - 2*x)%p
    return (x3,(lam*(x-x3)-y)%p)
def padd(P,Q):
    if P is O: return Q
    if Q is O: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        return O if (y1+y2)%p==0 else pdbl(P)
    lam=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(lam*lam*Bi - A - x1 - x2)%p
    return (x3,(lam*(x1-x3)-y1)%p)
def pmul(k,P):
    R=O
    while k:
        if k&1: R=padd(R,P)
        P=pdbl(P); k>>=1
    return R
rng=random.Random(1)
tries=0
while True:
    x=rng.randrange(2,p)
    y=sqrt_mod(f(x),p)
    tries+=1
    if y: break
    if tries>1000: print("no point in 1000 tries", flush=True); sys.exit(1)
P=(x,y)
print("point found after", tries, flush=True)
assert (P[1]*P[1]-f(P[0]))%p==0, "not on curve"
def sdbl(X1,Z1):
    XX=X1*X1%p;ZZ=Z1*Z1%p
    AA=2*((X1+Z1)**2-XX-ZZ)%p
    aZZ=A*ZZ%p
    X3=((XX-aZZ)**2-2*B*AA*ZZ)%p
    Z3=(AA*(XX+aZZ)+4*B*ZZ*ZZ)%p
    return X3*pow(Z3,-1,p)%p
m1=sdbl(P[0],1); m2=pdbl(P)[0]
print("dbl match:", m1==m2, flush=True)
if m1!=m2:
    # try alternate model: maybe server curve is y^2 = x^3 + (a-2b)x^2 + x style? test variants
    print("model mismatch — investigate", flush=True); sys.exit(2)
print("testing (p+1)P...", flush=True)
print("(p+1)P == O?", pmul(p+1,P) is O, flush=True)
S=1
for q in sympy.primerange(2,1000):
    e=1
    while q**(e+1)<10**6: e+=1
    S*=q**e
print("S bits:",S.bit_length(),"testing S*P...", flush=True)
print("S*P==O?",pmul(S,P) is O, flush=True)
ord_=4782850957738000717885060297297408935631027604045525430677
print("ord*P==O?", pmul(ord_,P) is O, flush=True)
print("(2(p+1)-ord)P==O?", pmul(2*(p+1)-ord_,P) is O, flush=True)

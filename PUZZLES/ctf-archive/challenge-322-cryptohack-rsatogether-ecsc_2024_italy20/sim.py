import random, sys, os
from math import comb, gcd
from functools import reduce
from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
random = random.SystemRandom()
flag = b"ECSC{testflag_sim}"
NB = int(sys.argv[1]) if len(sys.argv)>1 else 512
p=getPrime(NB//2); q=getPrime(NB//2); n=p*q; phi=(p-1)*(q-1); e=65537
d=pow(e,-1,phi)
def eval_poly(poly,x,nn): return sum(pow(x,i,nn)*poly[i] for i in range(len(poly)))%nn
poly=[d]+[random.getrandbits(NB) for _ in range(99)]
def create_shares(m):
    pl=poly[:m]; ys=[eval_poly(pl,i,phi) for i in range(1,m+1)]
    coeff=[(((-1)**(i-1))*comb(m,i)) for i in range(1,m+1)]
    sh=[(c*y)%phi for c,y in zip(coeff,ys)]
    return sh.pop(m-2)
yours={m:create_shares(m) for m in range(2,103)}
# sanity: product = c^d (yours + friends)
m=7; c=12345
pl=poly[:m]; ys=[eval_poly(pl,i,phi) for i in range(1,m+1)]
coeff=[(((-1)**(i-1))*comb(m,i)) for i in range(1,m+1)]
sh=[(cc*y)%phi for cc,y in zip(coeff,ys)]
tot=pow(c,sum(sh),n)
print("product=c^d:", tot==pow(c,d,n))
# ---- ATTACK ----
L=reduce(lambda a,b:a*b//gcd(a,b), range(2,103))
G=0
for m2 in range(2,103):
    G += (m2-1)*comb(101,m2-1)*(L//m2)*yours[m2]
print("G bits:", G.bit_length(), "sign", (G>0)-(G<0))
C0=round(G/n) if G>0 else round((-G)//n)
found=None
for C in (range(max(1,C0-3),C0+4) if G>0 else range(1,10)):
    if G%C: continue
    ph=G//C
    ssum=n-ph+1; D=ssum*ssum-4*n
    if D>0:
        r=isqrt=int(D**0.5) if D < 10**30 else None
        import gmpy2
        if gmpy2.is_square(D):
            rr=int(gmpy2.isqrt(D)); pp=(ssum-rr)//2
            if pp*(ssum-pp)==n: found=(ph,pp); break
print("FOUND phi:", found is not None)
if found:
    ph,pp=found
    qq=n//pp
    dd=pow(e,-1,(pp-1)*(qq-1))
    print("phi match:", ph==(pp-1)*(qq-1))
    pad=bytes(random.randbytes((NB-8)//8-len(flag)))+flag
    ct=pow(bytes_to_long(pad),e,n)
    print("flag:", long_to_bytes(pow(ct,dd,n))[-25:])

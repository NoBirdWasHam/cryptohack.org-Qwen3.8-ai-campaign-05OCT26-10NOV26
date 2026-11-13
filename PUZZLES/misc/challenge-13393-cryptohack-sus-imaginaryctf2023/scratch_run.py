
from gmpy2 import isqrt, is_square, iroot, gcd, invert, mpz
import time
N=None;e=None;c=None
for line in open('output.txt'):
    line=line.strip()
    if line.startswith('n ='): N=int(line.split('=')[1])
    if line.startswith('e ='): e=int(line.split('=')[1])
    if line.startswith('c ='): c=int(line.split('=')[1])
print('bits n', N.bit_length(), 'bits c', c.bit_length(), 'e', e)
# 1) deep plain Fermat on n: b^2 - N square?
t0=time.time()
b=isqrt(N-1)+1
found=False
it=0; MAX=2**21
while it<MAX:
    t=b*b-N
    if is_square(t):
        print('FERMAT HIT b=',b, 'factors:', b-isqrt(t), b+isqrt(t)); found=True; break
    b+=1; it+=1
print('fermat done iters',it,'t',round(time.time()-t0,1),'hit',found)
# 2) r poly-in-p probes: p ~ iroot(N, 6) etc
for d in (3,4,5,6,7):
    p0=iroot(N,d)[0]
    for p in range(p0-5,p0+6):
        if p>2 and N % (p*(p*p+p+1))==0:
            print('POLY HIT',d,p)
print('poly probe done')
# 3) Wiener e/N
from fractions import Fraction
def cf(a,b):
    out=[]
    while b:
        q=a//b; out.append(q); a,b=b,a-q*b
    return out
num,den=N,e
convs=cf(num,den)
h1,h2=1,num; k1,k2=0,1
def wiener_check(k,d):
    if d<=0 or k<=0: return
    if (e*d-1)%k: return
    phi=(e*d-1)//k
    if phi>=N: return
    # S2-S1 = N-1-phi ; cubic x^3 - S1 x^2 + (S1-T) x - N ; try S1 range around 2^512+2^1024+2^1536
    T=N-1-phi
    import math
    lo=0; hi=T+ (1<<1600)
    # S1 unknown ~ p+q+r <= 2^1537; S2 = S1+T ; check f(S1)=S1^3 - S1^2*S1?? define g(S1)=S1^3 - S1*S1... brute small tweak:
    S1approx=T  # placeholder
    return phi
import gmpy2
for q in convs[:80]:
    h3=q*h2+h1; k3=q*k2+k1; h1,h2=h2,h3; k1,k2=k2,k3
    if k1<=0: continue
    if (e*h1-1)%k1: continue
    phi=(e*h1-1)//k1
    if 0<phi<N:
        T=N-1-phi  # = S2 - S1
        # cubic x^3 - S1 x^2 + (S1-T) x - N has roots p,q,r; search S1 near r (dominant ~2^1535): S1 ~ r+q+p
        r0=iroot(N,3)[0]
        hit=False
        for S1 in range(max(1,r0-300000), r0+300000, 1):
            S2=S1-T
            # f(S1) must be 0 mod? try rational root: roots divide N; check gcd trick: evaluate cubic at divisor? too heavy; instead check discriminant via solving: use gcd(x^3-S1x^2+(S1-T)x-N, x^? ) skip
            pass
print('wiener loop done')
# 4) gcd checks
print('gcd(c,N)=',gcd(c,N), 'N odd?', N&1, 'N mod3', N%3)
# 5) check N close to p^3*r structures: is 4N+1 square? (pq~r)
print('4N+1 square?', is_square(4*N+1))
# 6) N mod small primes to get r mod 3 etc
print('r mod 3 =', (2*N)%3)

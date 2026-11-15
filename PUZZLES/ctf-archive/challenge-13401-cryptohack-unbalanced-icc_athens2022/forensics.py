import re, math
from sympy import igcd
t=open('output.txt').read()
N=int(re.search(r'N = (0x[0-9a-f]+)',t).group(1),16)
e=int(re.search(r'e = (0x[0-9a-f]+)',t).group(1),16)
c=int(re.search(r'c = (0x[0-9a-f]+)',t).group(1),16)
print('bits', N.bit_length(), e.bit_length(), c.bit_length())
print('N mod 3,5,7:', N%3, N%5, N%7)
print('e/N ratio ~', math.log2(e/N))
print('gcd(e,N):', igcd(e,N), 'gcd(c,N):', igcd(c,N), 'gcd(c-e,N):', igcd(c-e,N))
print('tz N-1:', ((N-1)&-(N-1)).bit_length()-1, 'tz N+1:', ((N+1)&-(N+1)).bit_length()-1)
found=None
aa=math.isqrt(N)
if aa*aa<N: aa+=1
for i in range(500000):
    b2=aa*aa-N
    r=math.isqrt(b2)
    if r*r==b2:
        found=(aa,r); break
    aa+=1
print('fermat:', found)

def cf(nn,dd,n=60):
    a=[]
    while len(a)<n and dd:
        ai=nn//dd
        a.append(ai)
        nn,dd=dd,nn-ai*dd
    return a
def conv(a,i):
    p0,q0,p1,q1=0,1,1,0
    for j in range(i):
        p0,p1=p1,a[j]*p1+p0
        q0,q1=q1,a[j]*q1+q0
    return p1,q1

def wiener(M,tag):
    a=cf(e,M)
    for i in range(1,len(a)+1):
        k,d=conv(a,i)
        if k==0 or d<=0 or (e*d-1)%k: continue
        phi=(e*d-1)//k
        s=N-phi+1
        disc=s*s-4*N
        if disc>=0:
            r=math.isqrt(disc)
            if r*r==disc:
                p=(s-r)//2
                if p>1 and N%p==0:
                    print('HIT',tag,'k bits',k.bit_length(),'d bits',d.bit_length())
                    return (k,d,p)
    return None
r=None
for adj,tag in [(0,'N'),(1<<512,'N+2^512'),(-(1<<512),'N-2^512'),(1<<256,'N+2^256'),(-(1<<256),'N-2^256'),(1<<400,'N+2^400'),(-(1<<400),'N-2^400')]:
    r=wiener(N+adj,tag)
    if r: break
print('wiener scan done:', r)
if r and len(r)==3:
    p=r[2]; q=N//p; phi=(p-1)*(q-1)
    d=pow(e,-1,phi)
    from Crypto.Util.number import long_to_bytes
    print(long_to_bytes(pow(c,d,N)))

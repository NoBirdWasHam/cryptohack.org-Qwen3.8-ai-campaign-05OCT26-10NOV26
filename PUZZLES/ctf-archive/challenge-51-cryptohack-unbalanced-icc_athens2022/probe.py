import math, re, random
from fractions import Fraction
import sympy
from fpylll import IntegerMatrix, LLL
from reallat import make_f, build
from Crypto.Util.number import getPrime
random.seed(2)
t=open('output.txt').read()
Nr=int(re.search(r'N = (0x[0-9a-f]+)',t).group(1),16)
er=int(re.search(r'e = (0x[0-9a-f]+)',t).group(1),16)
p=getPrime(256); q=getPrime(768); N=p*q; phi=(p-1)*(q-1)
while True:
    d=getPrime(300)
    if d>N**0.292: break
e=pow(d,-1,phi); k=(e*d-1)//phi
X,Y=1<<300,1<<254
f=make_f(N)
B,cols=build(f,e,X,Y,m=2,c=2)
LLL.reduction(B,delta=0.999)
norms=sorted((math.log2(sum(int(B[r,j])**2 for j in range(B.ncols)))/2.0, r)
             for r in range(B.nrows) if any(int(B[r,j]) for j in range(B.ncols)))
print('rank', len(norms), 'dims', B.nrows, B.ncols)
for b2,r in norms[:6]:
    row={}
    for ci,(i,j) in enumerate(cols):
        v=int(B[r,ci])
        if v: row[(i,j)]=v
    # unscaled poly value at root
    u0,w0=k,(p-(1<<255)-1)//2
    val=sum(c*(u0**i)*(w0**j) for (i,j),c in row.items())
    nz=sorted(((math.log2(abs(c))+(i*math.log2(X))+(j*math.log2(Y)))/1.0, (i,j)) for (i,j),c in row.items())
    print(f'--- row norm {b2:.1f}')
    print('   scaled coords bits:', [(pos, round(bb,0)) for bb,pos in nz[-4:]])
    print('   value bits:', val.bit_length() if val else 'ZERO', ' mod e^2 ==0:', val%(e*e)==0 if val else '-')
    if val:
        v2=abs(val)
        # v = (e^2)*t? 
        t2=v2//(e*e)
        print('   |val| vs e^2:', round(math.log2(v2),1), 'vs', round(math.log2(e*e),1), 'ratio bits', round(math.log2(v2+1)-math.log2(e*e),2))

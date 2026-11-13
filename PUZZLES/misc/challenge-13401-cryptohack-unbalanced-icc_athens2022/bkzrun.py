import math, re, sys, time
from fractions import Fraction
from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
from reallat import make_f, build
from extract2 import extract
import itertools
t=open('output.txt').read()
N=int(re.search(r'N = (0x[0-9a-f]+)',t).group(1),16)
e=int(re.search(r'e = (0x[0-9a-f]+)',t).group(1),16)
c=int(re.search(r'c = (0x[0-9a-f]+)',t).group(1),16)
X,Y=1<<300,1<<254
f=make_f(N)
B,cols=build(f,e,X,Y,m=2,c=2)
bound=(e**2).bit_length()-1-0.5*math.log2(B.ncols)
t0=time.time()
blk=int(sys.argv[1]) if len(sys.argv)>1 else 35
to=int(sys.argv[2]) if len(sys.argv)>2 else 1500
try:
    FPLLL.set_precision('mpfr')
except Exception as ex:
    print('prec', ex)
BKZ.reduction(B, BKZ.EasyParam(blk, 0.999, timeout=to))
rows=[]
norms=[]
for r in range(B.nrows):
    s=sum(int(B[r,j])**2 for j in range(B.ncols))
    if s: norms.append((s.bit_length()/2.0, r))
norms.sort()
print('BKZ', blk, 'min', round(norms[0][0],1), 'bound', round(bound,1), 'time', int(time.time()-t0))
good=[]
for b2,r in norms:
    if b2>=bound: break
    row={}
    for ci,(i,j) in enumerate(cols):
        v=int(B[r,ci])
        if v: row[(i,j)]=Fraction(v,(X**i)*(Y**j))
    good.append(row)
print('under bound rows:', len(good))
ells=[]
v=2**61
while len(ells)<6:
    import sympy
    v=sympy.nextprime(v+31); ells.append(int(v))
ps=None
for a,b in itertools.combinations(range(min(len(good),10)),2):
    try:
        ps=extract([good[a],good[b]],X,Y,N,ells)
    except Exception:
        ps=None
    if ps: break
print('candidates:', ps)
if ps:
    from Crypto.Util.number import long_to_bytes
    for p_ in ps:
        q_=N//p_
        d=pow(e,-1,(p_-1)*(q_-1))
        print('FLAG:', long_to_bytes(pow(c,d,N)))
        open('flag_unbalanced-icc_athens2022.txt','wb').write(long_to_bytes(pow(c,d,N)))

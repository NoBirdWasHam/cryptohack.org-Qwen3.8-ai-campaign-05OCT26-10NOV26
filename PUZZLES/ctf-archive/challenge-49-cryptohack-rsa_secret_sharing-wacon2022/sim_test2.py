# Simulate the WACON server at tiny scale; test bivariate HG factoring with
# LSBs (1/3 of bits) of BOTH primes known.
import random, sys
from Crypto.Util.number import getPrime, isPrime
from fpylll import IntegerMatrix, LLL

QB = 60
q = getPrime(QB)

class LCG:
    def __init__(s,a,x,b): s.a,s.x,s.b=a%q,x%q,b%q
    def fetch(s):
        r=s.x; s.x=(s.a*s.x+s.b)%q; return r

a=random.randint(1,q-1); x=random.randint(1,q-1); b=random.randint(1,q-1)
L1=LCG(a,x,b); L2=LCG(random.randint(1,q-1),random.randint(1,q-1),random.randint(1,q-1)); L3=LCG(random.randint(1,q-1),random.randint(1,q-1),random.randint(1,q-1))
def roll(): return L3.fetch()*q*q + L2.fetch()*q + L1.fetch()
pr=[]
while len(pr)<2:
    p=roll()
    if isPrime(p): pr.append(p)
p1,p2=pr
n=p1*p2
A=p1%q; B=p2%q
U=(p1-A)//q; V=(p2-B)//q
print("p bits",p1.bit_length(),"n bits",n.bit_length(),"u bits",U.bit_length())

from sympy import symbols, resultant
X,Y=symbols('X Y')
def build(s):
    mono=[(i,j) for i in range(s+2) for j in range(s+2)]
    midx={m:k for k,m in enumerate(mono)}
    rows=[]
    for i in range(s+1):
        for j in range(s+1):
            w=n**max(0,s-i-j)
            row=[0]*len(mono)
            row[midx[(i+1,j+1)]]=q*q*w
            row[midx[(i+1,j)]]=q*B*w
            row[midx[(i,j+1)]]=q*A*w
            row[midx[(i,j)]]= (A*B-n)*w
            rows.append(row)
    M=IntegerMatrix.from_iterable(len(rows),len(mono),[v for r in rows for v in r])
    LLL.reduction(M)
    polys=[]
    for r in range(M.nrows):
        d={mono[k]:int(M[r][k]) for k in range(len(mono)) if int(M[r][k])!=0}
        if d: polys.append(d)
    return polys
def ev(p,x,y):
    t=0
    for (i,j),c in p.items(): t+=c*x**i*y**j
    return t
def to_sym(p):
    e=0
    for (i,j),c in p.items(): e+=c*X**i*Y**j
    return e

done=False
for s in (2,3,4):
    polys=build(s)
    van=[p for p in polys if ev(p,U,V)==0]
    print("s",s,"polys",len(polys),"exact-vanishing",len(van))
    for i in range(len(van)):
        for j in range(i+1,len(van)):
            try:
                r=resultant(to_sym(van[i]),to_sym(van[j]),Y)
                poly=r.as_poly(X)
                if not poly: continue
                for rt in poly.real_roots():
                    if rt.is_Rational and rt.q==1 and 0<int(rt)< (1<<140):
                        u=int(rt)
                        if (n % (A+q*u))==0:
                            print("SOLVED s=",s,"factor",A+q*u); done=True; break
                if done: break
            except Exception: pass
        if done: break
    if done: break
print("done",done)

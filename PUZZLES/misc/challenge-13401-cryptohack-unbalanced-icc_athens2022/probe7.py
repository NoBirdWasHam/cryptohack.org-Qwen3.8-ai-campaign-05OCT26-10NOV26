import sys; sys.path.insert(0,".")
import math, random, gmpy2
import dng4
from fpylll import IntegerMatrix, LLL
from resultant_lib import resultant_x

random.seed(20261101)
def rprime(b): return int(gmpy2.next_prime(random.getrandbits(b)|(1<<(b-1))|1))
p,q = rprime(256), rprime(768); N=p*q; phi=(p-1)*(q-1)
d=rprime(192); e=int(pow(d,-1,phi)); k_=(d*e-1)//phi
m,t,a = 4,2,0
N_,e_ = N,e
rows = dng4.make_rows(N_,e_,m,t,a)
cols = dng4.coeffs_list(rows)
M, cols2, ci, rows2 = dng4.build(N_,e_,m,t,a,192)
LLL.reduction(M, delta=0.99)
L=math.log2(float(e)); r=M.nrows
hb = m*L-0.5*math.log2(r)
X,Y,Z=1<<192,1<<256,1<<768
yf=[];zf=[];mx=0;nonv=0
for ri in range(r):
    rv=[int(M[ri,c]) for c in range(r)]
    if all(v==0 for v in rv): continue
    l2=0.5*dng4.bl(sum(v*v for v in rv))
    if l2>=hb: continue
    poly={}
    ok=True
    for c,v in enumerate(rv):
        if v:
            (u,vv,w)=cols[c]; wg=X**u*Y**vv*Z**w
            if v%wg: ok=False;break
            poly[(u,vv,w)]=v//wg
    if not ok: continue
    hasY=any(w==0 and vv>0 for (u,vv,w) in poly); hasZ=any(w>0 for (u,vv,w) in poly)
    allY=not hasZ
    allZ=all(vv==0 for (u,vv,w) in poly)
    if allY:
        val=sum(cc*(k_**u)*(p**vv) for (u,vv,w),cc in poly.items())
        if val==0: yf.append((l2,poly))
        else: nonv+=1
    elif allZ: zf.append((l2,poly))
    else: mx+=1
print("yform-vanish",len(yf),"zform",len(zf),"mixed",mx,"yform-nonvanish",nonv)
if yf:
    l2,po=yf[0]
    dx=max(u for u,v,w in po); dy=max(v for u,v,w in po)
    print("first yform l2",round(l2),"degx",dx,"degy",dy,"nterm",len(po))
def touni(poly):
    H={}
    for (u,vv,w),c in poly.items():
        H[(u,vv)]=H.get((u,vv),0)+c
    return {k:v for k,v in H.items() if v}
U=[touni(po) for (_,po) in yf]
for i in range(min(6,len(U))):
    for j in range(i+1,min(6,len(U))):
        try:
            res=resultant_x(U[i],U[j])
        except Exception as ex:
            print(f"pair {i},{j} EXC {repr(ex)[:70]}"); continue
        if not res: print(f"pair {i},{j}: ZERO resultant (dependent)"); continue
        c0=res.get(0,0)
        g=int(gmpy2.gcd(N,abs(c0))) if c0 else 0
        print(f"pair {i},{j}: res degY={max(res)} c0bits={dng4.bl(c0) if c0 else 0} gcd={g.bit_length() if g else 0}")
        if 1<g<N: print("FACTOR FOUND", g==p or g==q); sys.exit(0)

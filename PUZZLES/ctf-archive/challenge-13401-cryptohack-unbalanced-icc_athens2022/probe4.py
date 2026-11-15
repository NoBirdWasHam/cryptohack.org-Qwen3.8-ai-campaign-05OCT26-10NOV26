import sys; sys.path.insert(0,".")
import math, dng3
from fpylll import IntegerMatrix, LLL
import gmpy2, random
random.seed(20261101)
def rprime(b): return int(gmpy2.next_prime(random.getrandbits(b)|(1<<(b-1))|1))
p,q=rprime(256),rprime(768); N=p*q; phi=(p-1)*(q-1)
d=rprime(192); e=int(pow(d,-1,phi)); k_=(d*e-1)//phi
rows,_ = dng3.region_rows(N,e,3,192,256)
M,mons = dng3.build_matrix(rows,192,256)
LLL.reduction(M, delta=0.99)
X=1<<192; Y=1<<256
hb = 3*math.log2(float(e)) - 0.5*math.log2(M.ncols)
print("hbound", round(hb,1))
for r in range(M.nrows):
    rowv=[int(M[r,c]) for c in range(M.ncols)]
    s2=sum(v*v for v in rowv)
    l2 = 0.5*dng3.bl(s2)
    # decode
    poly={}; ok=True
    for ci,v in enumerate(rowv):
        if v:
            u,vd = mons[ci]; wgt=X**u*Y**vd
            if v % wgt: ok=False; break
            poly[(u,vd)]=v//wgt
    if not ok:
        print(r, f"l2={l2:.0f} decode-fail"); continue
    val=sum(c*(k_**u)*(p**vd) for (u,vd),c in poly.items())
    vv = dng3.bl(val) if val else -1
    print(r, f"l2={l2:.0f} valbits={vv:.0f} vanishes={val==0}")

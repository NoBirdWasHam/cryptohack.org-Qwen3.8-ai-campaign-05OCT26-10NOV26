# probe: on toy f2=(u^2+u+1)v-n, find ANY short lattice vector with true value 0 at (p, rp).
import sympy, sys
from fpylll import IntegerMatrix, LLL
import lat_v4 as V

p=sympy.nextprime(2**59)
while not sympy.isprime(p*p+p+1): p=sympy.nextprime(p+1)
q=p*p+p+1; r=sympy.nextprime(2**179); N=p*q*r
X=2**60; Y=2**242
u0=p; v0=r*p
print("probe toy2", N.bit_length(), "N^m bits base", N.bit_length(), flush=True)
for m in (1,2,3):
  for (tmax,bmax,W) in [(6,2,0),(10,3,0),(12,4,0),(8,2,3),(12,3,4)]:
    try:
        M,cols=V.build(N,X,Y,m,tmax,bmax,W)
        LLL.reduction(M,delta=0.99)
        zeros=[]
        for i in range(min(40,M.nrows)):
            cv=[int(M[i,j]) for j in range(M.ncols)]
            if not any(cv): continue
            val=0
            for c,(I,K) in zip(cv,cols):
                if c: val += c*pow(u0,I)*pow(v0,K)
            if val==0:
                P=0
                for c,(I,K) in zip(cv,cols):
                    if c: P+=c*V.X_**I*V.Y_**K
                rr=V.extract(N,P)
                zeros.append((i,rr))
                if rr and p in rr:
                    print("SUCCESS m,t,b,W",m,tmax,bmax,W,"row",i,rr); sys.exit(0)
        print(m,tmax,bmax,W,"zero-rows:",[z[0] for z in zeros][:8],"with roots:",[z for z in zeros if z[1]][:2],flush=True)
    except Exception as ex:
        print(m,tmax,bmax,W,"err",type(ex).__name__,str(ex)[:80],flush=True)
print("probe done")

# Grid driver: report min UB vs N^m per parameter set on toy, attempt recovery.
import sympy, itertools, sys
import lat_toy3 as L

p=sympy.nextprime(2**59)
while not sympy.isprime(p*p+p+1): p=sympy.nextprime(p+1)
q=p*p+p+1; r=sympy.nextprime(2**179); N=p*q*r
X=2**60; Y=2**181
rtrue=r
print("toy",N.bit_length(),p.bit_length(),r.bit_length(),"TRUE",p, flush=True)
from fpylll import LLL
import lat_toy3
best=None
for m in (1,2,3):
  for t in (3,5,7):
    for d2 in (1,2):
      for B in (1,2):
        A=t+ (2 if B==2 else 1)
        try:
            M,cols=L.build(N,X,Y,m,t,d2,A,B)
            LLL.reduction(M,delta=0.99)
            minUB=None; hit=None
            for i in range(M.nrows):
                cvec=[int(M[i,j]) for j in range(M.ncols)]
                if not any(cvec): continue
                UB=sum(abs(c)*(X**I)*(Y**K) for c,(I,K) in zip(cvec,cols) if c)
                if minUB is None or UB<minUB: minUB=UB
                if UB < N**m and hit is None:
                    P=0
                    for c,(I,K) in zip(cvec,cols):
                        if c: P+=c*x**I*y**K if False else c*L.x**I*L.y**K
                    val=int(P.subs({L.x:p,L.y:rtrue}))
                    if val==0:
                        rr=L.extract_roots(N,P)
                        if rr: hit=rr
            print(m,t,d2,A,B,"minUB bits",minUB.bit_length(),"N^m bits",(N**m).bit_length(),"HIT" if hit else "",flush=True)
            if hit and p in hit:
                print("SUCCESS",hit); sys.exit(0)
        except Exception as ex:
            print(m,t,d2,A,B,"err",type(ex).__name__,str(ex)[:70],flush=True)
print("grid done no success")

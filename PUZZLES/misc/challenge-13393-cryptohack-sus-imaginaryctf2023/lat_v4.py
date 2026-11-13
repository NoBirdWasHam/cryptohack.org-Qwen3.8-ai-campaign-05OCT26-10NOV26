# v4: reparam (u,v)=(p, rp): f = (u^2+u+1)v - n. HG rows with triangular monomial regions.
import sympy, sys
from fpylll import IntegerMatrix, LLL
X_,Y_ = sympy.symbols('u v')
F2 = [(2,1,1),(1,1,1),(0,1,1),(0,0,-1)]   # u^2 v + u v + v - n (const scaled per call)

def build(N,X,Y,m,tmax,bmax,W):
    # rows: x^a y^b f^k N^{m-k}, k=1..m, (a,b): a + W*b <= (m-k)*tmax? use a<=tmax*(m-k), b<=max(0,bmax*(m-k)) hmm triangle:
    supp=[(i,j,w) for (i,j,w) in F2]
    supp=[(i,j,(-N if (i,j)==(0,0) else w)) for (i,j,w) in supp]
    rows=[]; cols=set()
    fpow={(0,0):1}
    fps=[]
    for k in range(1,m+1):
        nd={}
        for (i,j),c in fpow.items():
            for (u,vv,w) in supp:
                key=(i+u,j+vv); nd[key]=nd.get(key,0)+c*w
        fpow=nd; fps.append(fpow)
    for k in range(1,m+1):
        for a in range(0,(m-k)*tmax+1):
            for b in range(0, bmax+1):
                if W and a + W*b > (m-k)*tmax: continue
                for (i,j),c in fps[k-1].items():
                    if not c: continue
                    pass
                poly={}
                for (i,j),c in fps[k-1].items():
                    if c: poly[(i+a,j+b)] = c*(N**(m-k))
                rows.append(poly); cols.update(poly)
    for a in range(tmax+1):
        for b in range(bmax+1):
            if W and a+W*b>tmax: continue
            rows.append({(a,b):N**m}); cols.update([(a,b)])
    cols=sorted(cols); ci={c:i for i,c in enumerate(cols)}
    M=IntegerMatrix(len(rows),len(cols))
    for r,poly in enumerate(rows):
        for (I,K),c in poly.items():
            M[r,ci[(I,K)]] = c*X**I*Y**K
    return M,cols

def extract(N,P):
    P=sympy.expand(P)
    if P==0: return []
    dY=sympy.degree(P,Y_)
    A=sympy.Poly(X_**2+X_+1,X_)
    res=0
    for j in range(dY+1):
        pj=sympy.Poly(sympy.expand(P.coeff(Y_,j)),X_)
        res=res+(pj*(N**j)*(A**(dY-j))).as_expr()
    R=sympy.Poly(sympy.expand(res),X_)
    out=[]
    if R.is_zero: return out
    fac=sympy.factor(R)
    terms=fac.args if fac.is_Mul else [fac]
    for fct in terms:
        try:
            if sympy.degree(fct,X_)==1:
                r0=next(iter(sympy.roots(sympy.Poly(fct,X_)).keys()))
                if r0.is_Integer:
                    rr=int(r0)
                    if rr>1 and N%(rr*rr+rr+1)==0: out.append(rr)
        except Exception: pass
    return out

if __name__=="__main__":
    p=sympy.nextprime(2**59)
    while not sympy.isprime(p*p+p+1): p=sympy.nextprime(p+1)
    q=p*p+p+1; r=sympy.nextprime(2**179); N=p*q*r
    X=2**60; Y=2**242
    print("toy2",N.bit_length(),p.bit_length(),r.bit_length(),"TRUE",p,flush=True)
    for m in (2,1):
      for tmax in (4,6,8,10,12):
        for bmax in (1,2,3):
          for W in (0,3):
            try:
                M,cols=build(N,X,Y,m,tmax,bmax,W)
                LLL.reduction(M,delta=0.99)
                minUB=None;hit=None
                for i in range(M.nrows):
                    cv=[int(M[i,j]) for j in range(M.ncols)]
                    if not any(cv): continue
                    UB=sum(abs(c)*X**I*Y**K for c,(I,K) in zip(cv,cols) if c)
                    if minUB is None or UB<minUB: minUB=UB
                    if UB<N**m and hit is None:
                        P=0
                        for c,(I,K) in zip(cv,cols):
                            if c: P+=c*X_**I*Y_**K
                        rr=extract(N,P)
                        if rr: hit=rr
                print(m,tmax,bmax,W,"minUB",minUB.bit_length(),"N^m",(N**m).bit_length(),"HIT" if hit else "",flush=True)
                if hit and p in hit: print("SUCCESS",hit); sys.exit(0)
            except Exception as ex:
                print(m,tmax,bmax,W,"err",type(ex).__name__,str(ex)[:70],flush=True)
    print("v4 grid no success")

# HG bivariate small roots v3: with N^m monomial rows. Toy validation.
import sympy
from fpylll import IntegerMatrix, LLL
x,y = sympy.symbols('x y')

def build(N,X,Y,m,t,d2,A,B):
    fsupp=[(3,1,1),(2,1,1),(1,1,1),(0,0,-N)]
    rows=[]; cols=set()
    def add(poly):
        rows.append(poly); cols.update(poly)
    for k in range(1,m+1):
        tk = t if k==m else (m-k)*t
        bk = d2 if k==m else (m-k)*d2
        fp={(0,0):1}
        for _ in range(k):
            nd={}
            for (i,j),c in fp.items():
                for (u,v,w) in fsupp:
                    key=(i+u,j+v); nd[key]=nd.get(key,0)+c*w
            fp=nd
        for a in range(tk+1):
            for b in range(bk+1):
                poly={}
                for (i,j),c in fp.items():
                    if c: poly[(i+a,j+b)] = c * (N**(m-k) if k<m else 1)
                add(poly)
    for a in range(A+1):
        for b in range(B+1):
            add({(a,b): N**m})
    cols=sorted(cols); ci={c:i for i,c in enumerate(cols)}
    M=IntegerMatrix(len(rows), len(cols))
    for r,poly in enumerate(rows):
        for (I,K),c in poly.items():
            M[r, ci[(I,K)]] = c * X**I * Y**K
    return M, cols

def extract_roots(N,P):
    P=sympy.expand(P)
    dY=sympy.degree(P,y) if P!=0 else -1
    if dY<0: return []
    A=x**3+x**2+x
    res=0
    for j in range(dY+1):
        pj=sympy.Poly(sympy.expand(P.coeff(y,j)),x)
        res = res + (pj*(N**j)*(sympy.Poly(A,x)**(dY-j))).as_expr()
    R=sympy.Poly(sympy.expand(res),x)
    out=[]
    if R.is_zero: return out
    fac=sympy.factor(R)
    terms = fac.args if fac.is_Mul else [fac]
    for fct in terms:
        try:
            if sympy.degree(fct,x)==1:
                r0=next(iter(sympy.roots(sympy.Poly(fct,x)).keys()))
                if r0.is_Integer: out.append(int(r0))
        except Exception: pass
    return [rr for rr in out if rr>1 and N%(rr*(rr*rr+rr+1))==0]

def run(N,X,Y,m,t,d2,A,B,ptrue,maxv=24,verbose=False):
    M,cols=build(N,X,Y,m,t,d2,A,B)
    LLL.reduction(M, delta=0.99)
    rtrue=N//(ptrue*(ptrue**2+ptrue+1))
    for i in range(min(maxv,M.nrows)):
        cvec=[int(M[i,j]) for j in range(M.ncols)]
        UB=sum(abs(c)*(X**I)*(Y**K) for c,(I,K) in zip(cvec,cols) if c)
        if UB >= N**m: continue
        P=0
        for c,(I,K) in zip(cvec,cols):
            if c: P+=c*x**I*y**K
        val=int(P.subs({x:ptrue,y:rtrue}))
        if val!=0: continue   # not a true vanishing (shouldn't happen if UB bound right)
        rr=extract_roots(N,P)
        if rr:
            print("HIT",m,t,d2,A,B,"row",i,"roots",rr)
            return rr
    return None

if __name__=="__main__":
    p=sympy.nextprime(2**59)
    while not sympy.isprime(p*p+p+1): p=sympy.nextprime(p+1)
    q=p*p+p+1; r=sympy.nextprime(2**179); N=p*q*r
    X=2**60; Y=2**181
    print("toy",N.bit_length(),p.bit_length(),r.bit_length(),"TRUE p",p)
    found=False
    for (m,t,d2,A,B) in [(1,3,1,4,1),(1,4,1,5,1),(1,4,2,6,2),(1,5,1,6,1),(1,5,2,6,2),
                          (2,2,1,4,1),(2,3,1,4,1),(2,3,1,5,2),(2,3,2,5,2),(2,4,2,6,2)]:
        try:
            got=run(N,X,Y,m,t,d2,A,B,p)
            print((m,t,d2,A,B),"->",got)
            if got and p in got: found=True; break
        except Exception as ex:
            print((m,t,d2,A,B),"err",type(ex).__name__,str(ex)[:90])
    print("FOUND" if found else "none worked")

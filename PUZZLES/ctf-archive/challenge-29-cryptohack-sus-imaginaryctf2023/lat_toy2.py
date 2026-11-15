# HG bivariate small roots, v2: exact res + factor extraction + diagnostics.
import sympy, random
from fpylll import IntegerMatrix, LLL

FS = [(3,1,1),(2,1,1),(1,1,1),(0,0,-1)]

def build(N,X,Y,m,t,d2):
    fsupp=[(3,1,1),(2,1,1),(1,1,1),(0,0,-N)]
    cols=set(); rowdata=[]
    for k in range(1,m+1):
        for a in range(0,(m-k)*t+1):
            for b in range(0,(m-k)*d2+1):
                poly={(a,b):1}
                for _ in range(k):
                    nd={}
                    for (i,j),c in poly.items():
                        for (u,v,w) in fsupp:
                            key=(i+u,j+v); nd[key]=nd.get(key,0)+c*w
                    poly=nd
                if k<m:
                    for key in poly: poly[key]*=N**(m-k)
                rowdata.append(poly); cols|=set(poly)
    cols=sorted(cols); ci={c:i for i,c in enumerate(cols)}
    M=IntegerMatrix(len(rows:=rowdata), len(cols))
    for r,poly in enumerate(rowdata):
        for (I,K),c in poly.items():
            M[r, ci[(I,K)]] = c * X**I * Y**K
    return M, cols

x,y = sympy.symbols('x y')

def integer_root_roots(R, ptrue=None):
    roots=[]
    try:
        fac=sympy.factor(sympy.Poly(R,x))
        for fct,mult in fac.args:
            if sympy.degree(fct,x)==1:
                rt=sympy.roots(sympy.Poly(fct,x),x)
                roots += [r for r in rt]
    except Exception as ex:
        pass
    return roots

def extract(N, P):
    P=sympy.expand(P)
    dY=sympy.degree(P,y) if P!=0 else -1
    if dY<0: return
    A=x**3+x**2+x
    res=0
    for j in range(dY+1):
        pj=sympy.Poly(sympy.expand(P.coeff(y,j)),x)
        res=res+ (pj * (N**j) * (sympy.Poly(A,x)**(dY-j))).as_expr()
    R=sympy.Poly(sympy.expand(res),x)
    if R.is_zero: return
    for r in integer_root_roots(R):
        if r.is_Integer:
            rr=int(r)
            if rr>1 and N%(rr*(rr*rr+rr+1))==0:
                yield rr

def run(N,X,Y,m,t,d2, ptrue=None, label=""):
    M,cols=build(N,X,Y,m,t,d2)
    LLL.reduction(M, delta=0.99)
    for i in range(min(10,M.nrows)):
        P=0
        for j,(I,K) in enumerate(cols):
            if M[i,j]: P+=int(M[i,j])*x**I*y**K
        # diagnostic: evaluate at true root if known
        if ptrue is not None:
            rtrue=N//(ptrue*(ptrue*ptrue+ptrue+1))
            val=abs(int(sympy.expand(P).subs({x:ptrue,y:rtrue})))
            if i<3: print(label,"row",i,"|P(p,r)| bits",val.bit_length(),"N^m bits",(N**m).bit_length())
            if val==0:
                for rr in extract(N,P):
                    print(label,"RECOVERED",rr,"TRUE",ptrue, "match",rr==ptrue)
                    if rr==ptrue: return rr
    return None

if __name__=="__main__":
    random.seed(1)
    p=sympy.nextprime(2**59)
    while not sympy.isprime(p*p+p+1): p=sympy.nextprime(p+1)
    q=p*p+p+1; r=sympy.nextprime(2**179); N=p*q*r
    X=2**60; Y=2**181
    print("toy bits",N.bit_length(),p.bit_length(),r.bit_length())
    for (m,t,d2) in [(2,2,1),(2,3,1),(2,4,1),(2,4,2),(3,3,1),(3,4,1),(3,4,2)]:
        try:
            got=run(N,X,Y,m,t,d2,p,f"[{m},{t},{d2}]")
            if got: print("SUCCESS toy"); break
        except Exception as ex:
            print("err",m,t,d2,type(ex).__name__,str(ex)[:100])

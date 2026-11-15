# HG bivariate small roots: f(x,y)=A(x)*y - N, root (p,r). Validate on toy.
import itertools, math, random
from fpylll import IntegerMatrix, LLL

def build_lattice(N, X, Y, m, t, d2, verbose=True):
    # f(x,y) = y*(x^3+x^2+x) - N  : support {(1,1)->A*x*y terms: (3,1),(2,1),(1,1),(0,0)}
    fsupp = [(3,1,1),(2,1,1),(1,1,1),(0,0,-N)]
    # rows: x^a y^b f^k N^{m-k}, k=1..m, a+b*? region: a in 0..(m-k)*t, b in 0..(m-k)*d2
    # columns: all monomials (I,K) appearing
    cols=set(); rowdata=[]
    for k in range(1,m+1):
        for a in range(0, (m-k)*t + 1):
            for b in range(0, (m-k)*d2 + 1):
                # compute x^a y^b * f^k * N^{m-k} as dict (I,K)->coef
                poly={(a,b):1}
                for _ in range(k):
                    np_={}
                    for (i,j),c in poly.items():
                        for (u,v,w) in fsupp:
                            key=(i+u,j+v); np_[key]=np_.get(key,0)+c*w
                    poly=np_
                if k<m:
                    for key in poly: poly[key]*= N**(m-k)
                if not poly: continue
                rowdata.append((k,a,b,poly)); cols|=set(poly.keys())
    cols=sorted(cols)
    cidx={c:i for i,c in enumerate(cols)}
    rows=[]
    for (k,a,b,poly) in rowdata:
        r=[0]*len(cols)
        for (I,K),c in poly.items():
            r[cidx[(I,K)]] = c * (X**I) * (Y**K)
        rows.append(r)
    D=len(rows); C=len(cols)
    if verbose: print("lattice dim:",D,"x",C)
    M=IntegerMatrix(D,C)
    for i,r in enumerate(rows):
        for j,v in enumerate(r): M[i,j]=v
    return M, cols, cidx, rows

def shortpol(M, cols, cidx, X, Y, N, m):
    M2=M.dup(); LLL(M2, delta=0.99)
    out=[]
    for i in range(min(6,M2.nrows)):
        P={}
        for j,c in enumerate(cols):
            if M2[i,j]:
                P[c]=M2[i,j]
        # eval bound at (X,Y)
        s=sum(abs(v) for v in M2[i,:])
        out.append((s,P))
    return out

# ---------- toy ----------
import sympy
random.seed(12345)
p=sympy.nextprime(2**59)
while not sympy.isprime(p*p+p+1): p=sympy.nextprime(p+1)
q=p*p+p+1
r=sympy.nextprime(2**179)
N=p*q*r
X=2**62; Y=2**183
print("toy N bits",N.bit_length(),"p bits",p.bit_length(),"r bits",r.bit_length())

def try_lattice(m,t,d2):
    M,cols,cidx,rows=build_lattice(N,X,Y,m,t,d2)
    LLL.reduction(M, delta=0.99)
    # test shortest rows for integer roots via resultant with f
    import sympy
    x=sympy.symbols('x'); y=sympy.symbols('y')
    f = y*(x**3+x**2+x)-N
    for i in range(min(8,M.nrows)):
        P=sympy.Integer(0)
        for j,(I,K) in enumerate(cols):
            if M[i,j]: P += sympy.Integer(M[i,j]) * x**I * y**K
        # resultant in y
        R=sympy.resultant(sympy.Poly(P,x,y), sympy.Poly(f,x,y), y)
        if R.is_zero: continue
        R=sympy.Poly(R,x)
        for rt in R.nroots(n=20):
            if abs(rt.imag) if hasattr(rt,'imag') else abs(complex(rt).imag):
                continue
        cands=set()
        for rt in R.nroots(n=25):
            cr=complex(rt)
            if abs(cr.imag)>1e-6: continue
            rr=round(cr.real)
            if rr>0 and rr*(rr*rr+rr+1)!=0 and N%(rr*(rr*rr+rr+1))==0:
                print("RECOVERED p=",rr, "m,t,d2",m,t,d2); return rr
    return None

for (m,t,d2) in [(2,2,1),(2,3,1),(2,4,1),(2,4,2),(3,2,1),(3,3,1)]:
    print("try",m,t,d2)
    try:
        got=try_lattice(m,t,d2)
        if got: print("SUCCESS",got); break
    except Exception as ex:
        print("err",type(ex).__name__,str(ex)[:120])

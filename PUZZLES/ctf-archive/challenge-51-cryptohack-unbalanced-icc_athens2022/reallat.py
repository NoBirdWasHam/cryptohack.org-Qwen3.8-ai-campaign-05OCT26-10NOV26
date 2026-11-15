# REAL instance: shifted lattice G(u, 2^255+2w+1) mod e; BKZ-40; find vanishing rows
# via resultant-free linear trick: short rows h1,h2 vanishing at root (checked by:
# for each candidate w from N's factors? NO: verify by: gcd approach below).
# Extraction: from vanishing rows (once >=2), resultant over GF(l) CRT, p|N verify.
import math, re, sys, pickle
from fractions import Fraction
import sympy
from fpylll import IntegerMatrix, LLL, BKZ

t = open('output.txt').read()
N = int(re.search(r'N = (0x[0-9a-f]+)', t).group(1), 16)
e = int(re.search(r'e = (0x[0-9a-f]+)', t).group(1), 16)
c = int(re.search(r'c = (0x[0-9a-f]+)', t).group(1), 16)

def make_f(N):
    u,w=sympy.symbols('u w')
    P=(1<<255)+2*w+1
    Gx=sympy.expand(u*(P-1)*(N-P)+P)
    f={}
    for mon,co in Gx.as_coefficients_dict().items():
        du=int(sympy.degree(mon,u)) if mon!=1 else 0
        dw=int(sympy.degree(mon,w)) if mon!=1 else 0
        if mon==1: du=dw=0
        f[(du,dw)]=int(f.get((du,dw),0))+int(co)
    return f

def build(f, M, X, Y, m=2, c=2):
    def ppow(ff, mm):
        r={(0,0):1}
        for _ in range(mm):
            out={}
            for (i1,j1),c1 in r.items():
                for (i2,j2),c2 in ff.items():
                    kk=(i1+i2,j1+j2); out[kk]=out.get(kk,0)+c1*c2
            r=out
        return r
    fp=[{k: v*(M**tt) for k,v in ppow(f,m-tt).items()} for tt in range(m+1)]
    polys=[]
    for tt in range(m+1):
        g=fp[tt]; D=m+c*tt
        for a in range(D+1):
            for b in range(D-a+1):
                polys.append({(i+a,j+b):cc for (i,j),cc in g.items()})
    cols=sorted({k for p in polys for k in p})
    ci={k:i for i,k in enumerate(cols)}
    B=IntegerMatrix(len(polys),len(cols))
    for r,p in enumerate(polys):
        for (i,j),v in p.items():
            B[r,ci[(i,j)]]=int(v)*(X**i)*(Y**j)
    return B,cols

def rows_of(B, cols, X, Y):
    out=[]
    for r in range(B.nrows):
        row={}
        any_=False
        for ci,(i,j) in enumerate(cols):
            v=int(B[r,ci])
            if v:
                any_=True
                row[(i,j)]=Fraction(v,(X**i)*(Y**j))
        if any_: out.append(row)
    return out

if __name__=='__main__':
    f=make_f(N); X,Y=1<<300,1<<254
    m=int(sys.argv[1]) if len(sys.argv)>1 else 2
    cc=int(sys.argv[2]) if len(sys.argv)>2 else 2
    bkz=int(sys.argv[3]) if len(sys.argv)>3 else 40
    B,cols=build(f,e,X,Y,m=m,c=cc)
    bound=((e**m)).bit_length()-1-0.5*math.log2(len(cols))
    print(f'config m={m} c={cc} bkz={bkz}: {B.nrows}x{B.ncols} bound={bound:.1f}', flush=True)
    if bkz: BKZ.reduction(B, BKZ.EasyParam(bkz, timeout=1200))
    else: LLL.reduction(B, delta=0.999)
    best=9e9
    rows=rows_of(B,cols,X,Y)
    # dump all rows sorted by norm bits
    norms=[]
    for r in range(B.nrows):
        s=sum(int(B[r,jj])**2 for jj in range(B.ncols))
        if s: norms.append((s.bit_length()/2.0, r))
    norms.sort()
    print('min scaled L2 bits:', f'{norms[0][0]:.1f}', 'bound', f'{bound:.1f}', flush=True)
    pickle.dump({'rows':rows,'cols':cols,'X':X,'Y':Y,'norms':norms[:10]},
                open(f'realrows_m{m}c{cc}b{bkz}.pkl','wb'))
    print('saved', f'realrows_m{m}c{cc}b{bkz}.pkl', flush=True)

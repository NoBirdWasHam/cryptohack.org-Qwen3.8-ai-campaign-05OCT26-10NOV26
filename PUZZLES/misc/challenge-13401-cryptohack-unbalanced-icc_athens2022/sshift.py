# s-shifted f^m lattice: f_s(u,w) = f(u - s, w) with s chosen so ALL coefficients gain
# e-divisibility where tunable ((1,1) coeff 2N-1-4s made ~small, (0,0) becomes e-multiple).
# value at shifted root (k+s, w0): = f(k,p) = epd => every lattice element (f_s)^m*H has
# value divisible by (ep)^m. HG bound (e*2^255)^m.
import math, re, sys, itertools
from fractions import Fraction
import sympy
from fpylll import IntegerMatrix, LLL, BKZ
from purelat import ppow
from extract2 import extract

t=open('output.txt').read()
N=int(re.search(r'N = (0x[0-9a-f]+)',t).group(1),16)
e=int(re.search(r'e = (0x[0-9a-f]+)',t).group(1),16)
c=int(re.search(r'c = (0x[0-9a-f]+)',t).group(1),16)

def s_value():
    # 4s = 2N-1 - 2e -> s=(N-e)/2 exact integers
    assert (2*N-2*e) % 4 == 0
    return (N-e)//2

def make_fs(N, s):
    u,w=sympy.symbols('u w')
    P=(1<<255)+2*w+1
    Gx=sympy.expand((u-s)*(P-1)*(N-P)+P)
    f={}
    for mon,co in Gx.as_coefficients_dict().items():
        du=int(sympy.degree(mon,u)) if mon!=1 else 0
        dw=int(sympy.degree(mon,w)) if mon!=1 else 0
        if mon==1: du=dw=0
        f[(du,dw)]=int(f.get((du,dw),0))+int(co)
    return f

def build_pure(f, X, Y, m, TH):
    fm = ppow(f, m)
    S = [(a,b) for a in range(0,14) for b in range(0,18) if 300*a+254*b <= TH]
    polys = [{(i+a,j+b):cc for (i,j),cc in fm.items() if cc} for (a,b) in S]
    cols = sorted({k for p in polys for k in p})
    ci = {k:i for i,k in enumerate(cols)}
    B = IntegerMatrix(len(polys), len(cols))
    for r,p in enumerate(polys):
        for (i,j),v in p.items():
            B[r, ci[(i,j)]] = int(v)*(X**i)*(Y**j)
    return B, cols

def run(m, TH, bkz=0, tag=''):
    s=s_value()
    X=1<<300; Y=1<<254
    f=make_fs(N,s)
    if tag=='show':
        print({k: math.log2(abs(v)) if v else 0 for k,v in sorted(f.items())})
        return
    B,cols=build_pure(f,X,Y,m,TH)
    M=(e*(1<<255))**m
    bound=M.bit_length()-1-0.5*math.log2(len(cols))
    if bkz: BKZ.reduction(B, BKZ.EasyParam(bkz,0.999,timeout=1200))
    else: LLL.reduction(B, delta=0.999)
    nz=[r for r in range(B.nrows) if any(int(B[r,j]) for j in range(B.ncols))]
    norms=sorted((math.log2(sum(int(B[r,j])**2 for j in range(B.ncols)))/2.0, r) for r in nz)
    print(f'm={m} TH={TH} bkz={bkz}: {B.nrows}x{B.ncols} r={len(nz)} min={norms[0][0]:.0f} bound={bound:.0f} margin={bound-norms[0][0]:.0f}', flush=True)
    good=[]
    for b2,r in norms:
        if b2>=bound: break
        row={}
        for ci,(i,j) in enumerate(cols):
            v=int(B[r,ci])
            if v: row[(i,j)]=Fraction(v,(X**i)*(Y**j))
        good.append(row)
    print('under-bound rows:', len(good), flush=True)
    if len(good)>=2:
        ells=[]; v=2**61
        while len(ells)<6:
            v=sympy.nextprime(v+31); ells.append(int(v))
        # shifted root: u0=k+s, w0=(p-2^255-1)/2 -> candidate p from w0
        for a,b in itertools.combinations(range(min(len(good),14)),2):
            try:
                # verify vanish with REAL root if we know p? use extract (it checks N%p)
                ps=extract([good[a],good[b]],X,Y,N,ells,ubound=1<<254)
            except Exception as ex:
                ps=None
            if ps:
                print('CAND p:', ps, flush=True)
                from Crypto.Util.number import long_to_bytes
                for p_ in ps:
                    try:
                        q=N//p_; d=pow(e,-1,(p_-1)*(q-1))
                        fl=long_to_bytes(pow(c,d,N))
                        print('FLAG:', fl, flush=True)
                        open('flag_unbalanced-icc_athens2022.txt','wb').write(fl)
                        return True
                    except Exception as ex:
                        print('bad', ex, flush=True)
    return False

if __name__=='__main__':
    if sys.argv[1]=='show':
        run(2,808,0,'show')
    else:
        done=False
        for m,TH,bkz in [(2,554,0),(2,808,0),(2,1062,0),(2,1316,0),(2,1570,0),(2,1824,0),(3,808,0),(3,1062,0),(3,1316,0)]:
            try:
                if run(m,TH,bkz): break
            except Exception as ex:
                print(m,TH,'ERR',ex, flush=True)

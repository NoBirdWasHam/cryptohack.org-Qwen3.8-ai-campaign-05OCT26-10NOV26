# Solve via pure f^m lattice: build, LLL/BKZ, collect under-bound rows (they vanish at root),
# extract w0 via resultants+CRT, verify p | N, decrypt flag.
import math, re, sys, itertools
from fractions import Fraction
import sympy
from fpylll import IntegerMatrix, LLL, BKZ
from purelat import ppow
from windowsolve import make_f2
from extract2 import extract

def load_real():
    t=open('output.txt').read()
    return (int(re.search(r'N = (0x[0-9a-f]+)',t).group(1),16),
            int(re.search(r'e = (0x[0-9a-f]+)',t).group(1),16),
            int(re.search(r'c = (0x[0-9a-f]+)',t).group(1),16))

def build_pure(f, X, Y, m, TH):
    fm = ppow(f, m)
    S = [(a,b) for a in range(0,12) for b in range(0,16) if 300*a+254*b <= TH]
    polys = [{(i+a,j+b):c for (i,j),c in fm.items() if c} for (a,b) in S]
    cols = sorted({k for p in polys for k in p})
    ci = {k:i for i,k in enumerate(cols)}
    B = IntegerMatrix(len(polys), len(cols))
    for r,p in enumerate(polys):
        for (i,j),v in p.items():
            B[r, ci[(i,j)]] = int(v)*(X**i)*(Y**j)
    return B, cols

def solve(N, e, c, m, TH, gb=0, gtop=0, bkz=0, verbose=True):
    X = 1<<300
    if gb:
        base=1<<255; step=1<<(255-gb); C=base+gtop*step+1; Y=step//2
        pmin=base+gtop*step
    else:
        C=(1<<255)+1; Y=1<<254; pmin=1<<255
    f=make_f2(N, C, Y)
    B, cols = build_pure(f, X, Y, m, TH)
    M=(e*pmin)**m
    bound=M.bit_length()-1-0.5*math.log2(len(cols))
    if bkz: BKZ.reduction(B, BKZ.EasyParam(bkz, 0.999, timeout=900))
    else: LLL.reduction(B, delta=0.999)
    good=[]
    norms=[]
    for r in range(B.nrows):
        s=sum(int(B[r,j])**2 for j in range(B.ncols))
        if s: norms.append((s.bit_length()/2.0, r))
    norms.sort()
    for b2,r in norms:
        if b2>=bound: break
        row={}
        for ci,(i,j) in enumerate(cols):
            v=int(B[r,ci])
            if v: row[(i,j)]=Fraction(v,(X**i)*(Y**j))
        good.append(row)
    if verbose:
        print(f'm={m} TH={TH} gb={gb} gtop={gtop}: min={norms[0][0]:.0f} bound={bound:.0f} under={len(good)}', flush=True)
    if len(good)<2: return None
    ells=[]; v=2**61
    while len(ells)<6:
        v=sympy.nextprime(v+31); ells.append(int(v))
    for a,b in itertools.combinations(range(min(len(good),12)),2):
        try:
            ps=extract([good[a],good[b]],X,Y,N,ells)
        except Exception:
            ps=None
        if ps:
            if verbose: print('candidates:', ps, flush=True)
            return ps
    return None

def finish(N,e,c,p):
    from Crypto.Util.number import long_to_bytes
    q=N//p
    d=pow(e,-1,(p-1)*(q-1))
    return long_to_bytes(pow(c,d,N))

if __name__=='__main__':
    if sys.argv[1]=='syn':
        import random
        from Crypto.Util.number import getPrime
        random.seed(7)
        p=getPrime(256); q=getPrime(768); N=p*q; phi=(p-1)*(q-1)
        while True:
            d=getPrime(300)
            if d>N**0.292: break
        e=pow(d,-1,phi)
        m=int(sys.argv[2]); TH=int(sys.argv[3])
        ps=solve(N,e,0,m,TH)
        print('TRUE:', p in ps if ps else False, flush=True)
        if ps and p in ps:
            print('flag check ok synthetic')
    else:
        N,e,c=load_real()
        m=int(sys.argv[2]); TH=int(sys.argv[3]); gb=int(sys.argv[4]) if len(sys.argv)>4 else 0
        g0=int(sys.argv[5]) if len(sys.argv)>5 else 0
        g1=int(sys.argv[6]) if len(sys.argv)>6 else (1<<gb if gb else 1)
        bkz=int(sys.argv[7]) if len(sys.argv)>7 else 0
        for gtop in range(g0,g1):
            ps=solve(N,e,c,m,TH,gb,gtop,bkz)
            if ps:
                for p_ in ps:
                    try:
                        fl=finish(N,e,c,p_)
                        print('FLAG:', fl, flush=True)
                        open('flag_unbalanced-icc_athens2022.txt','wb').write(fl)
                        sys.exit(0)
                    except Exception as ex:
                        print('bad p', ex, flush=True)
        print('no flag', flush=True)

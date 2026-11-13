# selfcheck4.py: synthetic sigma~3.4 1337-bit pair; hint corrupted by E=2^16;
# CORRECTED centering S=(hint±E)^2/D^2 - 2 sqrt n; lattice (8,6) X=2^615; full
# extraction (gp gcd + CRT + p|n). Tells us whether the noisy attack shape works
# at real geometry, and what |u0| looks like.
import math, random, sys, os, subprocess
sys.set_int_max_str_digits(10**7)
from fractions import Fraction
import gmpy2
import sympy as sp
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

HERE = os.path.dirname(os.path.abspath(__file__))
GP = r"~\tools\gp64.exe"
random.seed(int(time_.time()) if 'time_' in dir() else 5)
import time
random.seed(5)
while True:
    p = sp.nextprime(random.getrandbits(1337) | (1 << 1336) | 1)
    q = sp.nextprime((p * 11) // 20)
    if (1 << 1336) <= q < (1 << 1337) and 3 <= (p+q)//abs(p-q) <= 4: break
n = p*q
D = 63**14
D2 = D*D
import decimal
decimal.getcontext().prec = 4200
hint0 = int(D * (decimal.Decimal(p).sqrt() + decimal.Decimal(q).sqrt()))
E = 1 << 16
hint = hint0 + random.randrange(-E, E+1)
sn2 = int(gmpy2.isqrt(gmpy2.mpz(4)*n))
S_lo = ((hint-E)**2) // D2 - sn2 - 3
S_hi = ((hint+E)**2) // D2 - sn2 + 3
t0 = (S_lo+S_hi)//2
assert S_lo <= p+q <= S_hi, "S outside widened interval"
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
p0 = (t0+d0)//2; q0 = n//p0; c0 = p0*q0 - n
u0t = p - p0; v0t = q - q0
print("u0 bits", abs(u0t).bit_length(), "v0 bits", abs(v0t).bit_length(), flush=True)
X = 1 << 615; Y = X
u, v = sp.symbols('u v')
fmon = {(1,1):1,(1,0):q0,(0,1):p0,(0,0):c0}
FP={}
def fpow(k):
    if k in FP: return FP[k]
    out={(0,0):1}
    for _ in range(k):
        nxt={}
        for ma,va in out.items():
            for mb,vb in fmon.items():
                mm=(ma[0]+mb[0],ma[1]+mb[1]); nxt[mm]=nxt.get(mm,0)+va*vb
        out=nxt
    FP[k]=out; return out
m,K = 8,6
mons = sorted([(a,b) for a in range(K+1) for b in range(K+1)]); w=len(mons)
idx = {mm:i for i,mm in enumerate(mons)}
rows=[]
for j in range(m+1):
    if j > K: break
    Np = n**(m-j)
    for i2 in range(K-j+1):
        for k2 in range(K-j+1):
            row=[0]*w
            for (ia,ib),vv in fpow(j).items():
                ma, mb = ia+i2, ib+k2
                if ma<=K and mb<=K:
                    row[idx[(ma,mb)]] += vv*Np*X**(ma+mb)
            rows.append(row)
M = IntegerMatrix(len(rows), w)
for i,r in enumerate(rows):
    for jj,val in enumerate(r):
        if val: M[i,jj] = val
print("LLL...", flush=True)
M = lll_reduction(M, delta=0.99)
thr = Fraction(n**m)/(Fraction(math.isqrt(w)+1))
Rs=[]; nvan=0; ntot=0
vf = -(q0*u + c0)/(u + p0)
for i in range(M.nrows):
    nr2 = sum(int(M[i,jj])**2 for jj in range(w))
    if Fraction(nr2) >= thr*thr: continue
    rr=[int(M[i,jj]) for jj in range(w)]
    if all(x==0 for x in rr): continue
    h = sum(sp.Rational(rr[idx[(a,b)]], X**(a+b)) * u**a * v**b for (a,b) in mons if rr[idx[(a,b)]])
    hp = sp.Poly(sp.expand(h), u, v)
    if hp.total_degree() < 1: continue
    ntot += 1
    if sp.together(hp.as_expr().subs({u:u0t, v:v0t})) == 0: nvan += 1
    dv = hp.degree(v)
    R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
    R = sp.Poly(R, u)
    if R.degree() >= 1: Rs.append(R)
print(f"pass={ntot} vanish={nvan} Rs={len(Rs)}", flush=True)
if len(Rs) >= 2:
    g = sp.gcd(Rs[0], Rs[1])
    print("gcd01 deg", g.degree(), "rooted:", g.as_expr().subs(u,u0t)==0, flush=True)
    # quick CRT extraction on 6 Rs
    scr = ['default(parisize,"2G");']
    for i2 in range(6):
        with open(os.path.join(HERE, f"s4{i2}.txt"),'w') as fh:
            for co in Rs[i2].all_coeffs()[::-1]:
                fh.write(str(int(co))); fh.write(chr(10))
        scr.append(f'P{i2}=Pol(Vec(readvec("{os.path.join(HERE, f"s4{i2}.txt").replace(chr(92),"/")}")));')
    scr.append('g=gcd(gcd(gcd(gcd(P0,P1),P2),gcd(P3,P4))); g=gcd(g,P5); g=g/content(g);')
    scr.append('print1("GCDDEG ",poldegree(g),"\\n");')
    scr.append('forprime(pp=5,900, my(rs=polrootsmod(g,pp)); print1("R ",pp); for(i=1,#rs,print1(" ",lift(rs[i]))); print1("\\n"); );')
    scr.append('quit();')
    pr = subprocess.run([GP,"-q"], input="\n".join(scr), capture_output=True, text=True, timeout=2400)
    lines = pr.stdout.splitlines()
    print("gp head:", lines[0] if lines else pr.stderr[:120], flush=True)
    rootmap = {}
    for L in lines[1:]:
        parts = L.split()
        if parts and parts[0]=='R': rootmap[int(parts[1])] = set(int(x) for x in parts[2:])
    cands=None; MM=1
    for pp in sorted(rootmap):
        rp = rootmap[pp]
        if cands is None: cands=set(rp); MM=pp
        else:
            new=set()
            for a in cands:
                ra=a%pp
                if ra in rp:
                    t=((ra-a)*int(gmpy2.invert(MM,pp)))%pp
                    new.add(a+MM*t)
            cands=new; MM*=pp
        if not cands: print("EMPTY at", pp, flush=True); break
        if MM.bit_length() > 617: break
    hit=None
    for a in (cands or set()):
        for uu in (a%MM, a%MM-MM):
            for cc in (p0+uu, p0-uu, p0+uu+1, p0+uu-1, p0-uu+1, p0-uu-1):
                if cc>1 and n%cc==0: hit=cc
    print("SELF4 FACTORED:", bool(hit), flush=True)
print("SELFCHECK4 DONE", flush=True)

import cmath, math, random
from math import log
_z = cmath.exp(2j*math.pi/35)
def _g(r): return (r % 5 + r % 7) % 5
Mlist = list(range(96,161))
LP = {}
for m in Mlist:
    v=[0.0]*5
    for r in range(35):
        s=sum(((0.5+0.5*_z**k)**m)*_z**(-k*r) for k in range(35)).real/35
        v[_g(r)]+=max(s,0.0)
    tot=sum(v); LP[m]=[log(5*max(a,1e-12)/tot) for a in v]
CW={}
for m in Mlist:
    cw=[];acc=0
    for a in LP[m]: pass
    v=[math.exp(x)/5 for x in LP[m]]; tot=sum(v)
    for a in v: acc+=a/tot; cw.append(acc)
    CW[m]=cw
def draw_m(): return sum(random.getrandbits(1) for _ in range(256))
def stat(cnt): return max(sum(cnt[a]*LP[m][a] for a in range(5)) for m in Mlist)
def run(tmax=5000, hi=6.0, lo=-6.0, iters=3000):
    e0=e1=0; q0=0; q1=0
    for hyp in (0,1):
        for it in range(iters):
            cnt=[0]*5; m=draw_m() if hyp==0 else None
            t=0; dec=None
            while t<tmax:
                for _ in range(500):
                    if hyp==0:
                        u=random.random(); cw=CW[m]
                        import bisect; a=bisect.bisect(cw,u)
                    else: a=random.randrange(5)
                    cnt[a]+=1
                t+=500
                s=stat(cnt)
                if s>=hi: dec=0; break
                if s<=lo: dec=1; break
            if dec is None: dec = 0 if stat(cnt)>-1 else 1
            if hyp==0:
                q0+=t; e0 += (dec!=0)
            else:
                q1+=t; e1 += (dec!=1)
    print(f"tmax={tmax} hi={hi} lo={lo}: e0={e0/iters:.4f} e1={e1/iters:.4f} avgQ0={q0/iters:.0f} avgQ1={q1/iters:.0f}", flush=True)
run()
run(hi=8.0, lo=-8.0)
run(tmax=6000, hi=10.0, lo=-10.0)

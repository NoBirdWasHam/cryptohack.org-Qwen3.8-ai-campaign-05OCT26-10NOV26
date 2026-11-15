# C2 GLRT calibration: statistic = max_m sum_t log(5*p_m(out_t)). Monte Carlo tails + normal fit.
import cmath, math, random, bisect
from math import log, erf, sqrt
z = cmath.exp(2j*math.pi/35)
def g(r): return (r%5 + r%7)%5
Mlist = list(range(96, 161))
PV, CW, LP = {}, {}, {}
for m in Mlist:
    v = [0.0]*5
    for r in range(35):
        s = sum(((0.5+0.5*z**k)**m)*z**(-k*r) for k in range(35)).real/35
        v[g(r)] += max(s, 0.0)
    tot=sum(v); v=[a/tot for a in v]
    PV[m]=v; CW[m]=[]; acc=0
    for a in v: acc+=a; CW[m].append(acc)
    LP[m]=[log(5*a) for a in v]
def draw_m():
    return sum(random.getrandbits(1) for _ in range(256))
def stat(outs):
    cnt=[outs.count(a) for a in range(5)]
    return max(sum(cnt[a]*LP[m][a] for a in range(5)) for m in Mlist)
def sim(t, iters=1500):
    L0=[]; L1=[]
    for it in range(iters):
        m = draw_m(); cw = CW[m]
        outs = [bisect.bisect(cw, random.random()) for _ in range(t)]
        L0.append(stat(outs))
        L1.append(stat([random.randrange(5) for _ in range(t)]))
    mu0=sum(L0)/iters; sd0=(sum((x-mu0)**2 for x in L0)/iters)**.5
    mu1=sum(L1)/iters; sd1=(sum((x-mu1)**2 for x in L1)/iters)**.5
    c = (mu0/sd0**2 + mu1/sd1**2)/(1/sd0**2+1/sd1**2)
    Phi=lambda x: 0.5*(1+erf(x/sqrt(2)))
    e0 = Phi((c-mu0)/sd0)
    e1 = 1-Phi((c-mu1)/sd1)
    print(f"t={t} mu0={mu0:.1f} sd0={sd0:.1f} mu1={mu1:.1f} sd1={sd1:.1f} thresh={c:.1f} e0~{e0:.2e} e1~{e1:.2e}", flush=True)
for t in (1000, 2000):
    sim(t)

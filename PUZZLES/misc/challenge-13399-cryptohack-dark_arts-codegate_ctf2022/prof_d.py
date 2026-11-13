import os
from collections import Counter
import box_c3 as B

def gen_lists(D,n,T):
    gens=[]
    for i in range(n):
        w=[D[j][i]%5 for j in range(T)]
        gens.append([w[j]-5*(w[j]%2) for j in range(T)])
    for j in range(T):
        g=[0]*T; g[j]=10; gens.append(g)
    return gens

def mk_order(free,tight,mode):
    if mode=="tightlast": return free+tight
    T=len(free)+len(tight); order=[]; fi=ti=0; nf,nt=len(free),len(tight)
    for i in range(nt):
        target=(i+1)*nf//(nt+1)
        while fi<target: order.append(free[fi]); fi+=1
        order.append(tight[i])
    while fi<nf: order.append(free[fi]); fi+=1
    return order

for (n,T,seed) in ((16,88,2),(24,120,4),(32,144,7),(64,176,1)):
    k,D,b=B.make_instance(n,T,seed)
    gens=gen_lists(D,n,T)
    H1,d1=B.hnf_int([g for g in gens],T)
    tight=[j for j in range(T) if d1[j]==2]; free=[j for j in range(T) if d1[j]!=2]
    line=f"n={n} T={T} s={seed} pass1={dict(Counter(d1))}"
    for mode in ("tightlast","interleave"):
        order=mk_order(free,tight,mode)
        H,d=B.hnf_int([[g[c] for c in order] for g in gens],T)
        # branching per level: #box values v in [lo,hi] congruent base mod dv worst-case = dv<=5? compute max branch
        br=[min(5, dv if dv<5 else (5+dv-1)//dv ) if dv>0 else 5 for dv in d]
        # actual: candidates in 5 consecutive ints congruent to base mod dv = ceil(5/dv)
        cand=[-(-5//dv) if dv>0 else 5 for dv in d]
        line+=f" | {mode} pass2={dict(Counter(d))} prodmax={1 if cand else 0}"
        import math
        lg=sum(math.log2(c) for c in cand)
        line+=f" sumlog2(ceil5/d)={lg:.1f}"
    print(line, flush=True)

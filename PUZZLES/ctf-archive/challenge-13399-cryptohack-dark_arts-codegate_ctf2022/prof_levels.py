import os, time, sys
from collections import Counter
import box_c3 as B
os.environ["ORDER"]=sys.argv[3] if len(sys.argv)>3 else "interleave"
n,T,seed = (int(x) for x in sys.argv[1:4])
k,D,b = B.make_instance(n,T,seed)
# replicate box_solve internals with per-level counting
gens=B.__dict__
import importlib
# rebuild gens/order exactly as box_solve does
def gens_of(D,n,T):
    gens=[]
    for i in range(n):
        w=[D[j][i]%5 for j in range(T)]
        gens.append([w[j]-5*(w[j]%2) for j in range(T)])
    for j in range(T):
        g=[0]*T; g[j]=10; gens.append(g)
    return gens
gens=gens_of(D,n,T)
H1,d1=B.hnf_int([g for g in gens],T)
tight=[j for j in range(T) if d1[j]==2]; free=[j for j in range(T) if d1[j]!=2]
mode=os.environ["ORDER"]
if mode=="tightlast": order=free+tight
else:
    order=[];fi=ti=0;nf,nt=len(free),len(tight)
    for i in range(nt):
        target=(i+1)*nf//(nt+1)
        while fi<target: order.append(free[fi]); fi+=1
        order.append(tight[i])
    while fi<nf: order.append(free[fi]); fi+=1
H,d=B.hnf_int([[g[c] for c in order] for g in gens],T)
u=[2+4*bb for bb in b]; up=[u[j] for j in order]
lvl=Counter(); xs=[0]*T; vs=[0]*T; t0=time.time()
def dfs(p,carry):
    lvl[p]+=1
    if sum(lvl.values())>4_000_000: raise MemoryError
    if p==T: return
    dv=d[p]; base=carry[p]; lo,hi=up[p]-2,up[p]+2
    c=base%dv; v=lo+((c-lo)%dv)
    while v<=hi:
        x=(v-base)//dv; vs[p]=v
        for jj in range(p+1,T): carry[jj]+=x*H[p][jj]
        dfs(p+1,carry)
        for jj in range(p+1,T): carry[jj]-=x*H[p][jj]
        v+=dv
try: dfs(0,[0]*T)
except MemoryError: print("CAP")
print("mode",mode,f"n={n} T={T} total={sum(lvl.values())} {time.time()-t0:.0f}s")
print("d:", d)
for p in range(T):
    if lvl[p]: print(p, d[p], lvl[p])

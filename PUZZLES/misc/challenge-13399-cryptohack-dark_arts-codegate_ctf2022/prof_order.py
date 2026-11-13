import os, sys, time
from collections import Counter
import box_c3 as B

# monkey-divert: replicate box_solve but expose d dist + capped nodes for both orders
def probe(n,T,seed,order_mode,cap=3_000_000):
    os.environ["ORDER"]=order_mode
    k,D,b = B.make_instance(n,T,seed)
    t0=time.time()
    try:
        c,nodes,secs,d = B.box_solve(D,b,n,T,node_cap=cap)
        dist=Counter(d)
        return f"n={n} T={T} s={seed} {order_mode}: nodes={nodes} {secs:.1f}s nsol={len(c)} true={tuple(k) in c} d={dict(dist)}"
    except MemoryError:
        return f"n={n} T={T} s={seed} {order_mode}: CAP>{cap} {time.time()-t0:.0f}s"

for (n,T,seed) in ((16,88,2),(24,120,4),(32,144,7)):
    for om in ("interleave","tightlast"):
        print(probe(n,T,seed,om), flush=True)

import os, sys
for ordr in ("tightlast","interleave"):
    os.environ["ORDER"]=ordr
    import importlib, box_c3
    importlib.reload(box_c3)
    for (n,T,seed) in ((8,40,1),(10,56,3),(16,88,2),(24,120,4)):
        k,D,b = box_c3.make_instance(n,T,seed)
        c,nodes,secs,d = box_c3.box_solve(D,b,n,T)
        print(f"{ordr} n={n} T={T} seed={seed}: nodes={nodes} {secs:.2f}s true_in={tuple(k) in c} nsol={len(c)}", flush=True)

import time, box_c3 as B
for (n,T,seed) in ((8,40,1),(10,56,3),(16,88,2),(24,120,4),(32,144,7),(48,160,6),(64,176,1)):
    k,D,b=B.make_instance(n,T,seed)
    t0=time.time()
    try:
        c,nodes,secs,d=B.box_solve(D,b,n,T,node_cap=100_000_000)
        print(f"n={n} T={T} seed={seed}: nodes={nodes} {secs:.1f}s nsol={len(c)} true_in={tuple(k) in c} sol_correct={len(c)==1 and c[0]==tuple(k)}", flush=True)
    except MemoryError:
        print(f"n={n} T={T} seed={seed}: CAP {time.time()-t0:.0f}s", flush=True)

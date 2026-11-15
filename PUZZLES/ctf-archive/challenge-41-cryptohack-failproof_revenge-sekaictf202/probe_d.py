# (d) BKZ-35 mpfr-1400 (>= log2 max entry ~1188), max_time 240 chunked calls x8, profile per call
import json,time,os
from fpylll import IntegerMatrix, BKZ, GSO, FPLLL
from fpylll.fplll.bkz import bkz_reduction
FPLLL.set_threads(1)
D=os.path.dirname(os.path.abspath(__file__)); P=lambda f:os.path.join(D,f)
K=json.load(open(P("kannan3_ckpt.json")))
M=IntegerMatrix(249,505)
for i,row in enumerate(K):
    for j,v in enumerate(row): M[i,j]=v
def prof(tag):
    g=GSO.Mat(M,update=True); pr=[float(g.get_r(i,i))**2 for i in range(249)]
    p=sorted(x for x in pr if 0<x<1e300)
    print(f"{tag}: spread={(p[-1]/p[0])**(1/249):.5f} min={p[0]:.4g} nlev505={sum(1 for x in p if x<=505)} t={time.time()-T0:.0f}s", flush=True)
T0=time.time(); prof("pre")
for i in range(8):
    t=time.time()
    pr_=BKZ.EasyParam(35, delta=0.99, max_time=240, flags=BKZ.AUTO_ABORT)
    try:
        bkz_reduction(M, pr_, None, "mpfr", 1400)
        print(f"call{i} returned {time.time()-t:.0f}s", flush=True)
    except Exception as ex:
        print(f"call{i} EXC after {time.time()-t:.0f}s: {ex}", flush=True); break
    prof(f"post{i}")
json.dump([[int(M[i,j]) for j in range(505)] for i in range(249)], open(P("probe_d_basis.json"),"w"))

# (c) BKZ-45 'd' with AUTO_ABORT OFF (EasyParam default may abort tours early)
import json,time,os
from fpylll import IntegerMatrix, BKZ, GSO, FPLLL
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
p=BKZ.EasyParam(45, delta=0.99, flags=BKZ.AUTO_ABORT)  # XOR removes auto-abort
print("auto_abort:", p.auto_abort, "max_loops:", p.max_loops, "max_time:", p.max_time, flush=True)
try:
    BKZ.reduction(M,p); print(f"BKZ45-noabort returned {time.time()-T0:.0f}s", flush=True)
except Exception as ex:
    print(f"BKZ45-noabort EXC after {time.time()-T0:.0f}s: {ex}", flush=True)
prof("post")
json.dump([[int(M[i,j]) for j in range(505)] for i in range(249)], open(P("probe_c_basis.json"),"w"))

# (a) full BKZ-45, default float backend, on best ckpt
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
    print(f"{tag}: spread={(p[-1]/p[0])**(1/249):.5f} min={p[0]:.4g} nlev505={sum(1 for x in p if x<=505)}", flush=True)
prof("pre")
t=time.time(); p=BKZ.EasyParam(45, delta=0.99)
try:
    BKZ.reduction(M,p); print(f"BKZ45-d returned {time.time()-t:.0f}s", flush=True)
except Exception as ex:
    print(f"BKZ45-d EXC after {time.time()-t:.0f}s: {ex}", flush=True)
prof("post")
json.dump([[int(M[i,j]) for j in range(505)] for i in range(249)], open(P("probe_a_basis.json"),"w"))

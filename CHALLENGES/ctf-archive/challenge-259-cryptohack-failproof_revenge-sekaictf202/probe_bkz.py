# probe: is BKZ-35 doing real work on the resume ckpt? full reduction, no max_time, timed.
import json,time,math,os
from fpylll import IntegerMatrix, BKZ, GSO, FPLLL
FPLLL.set_threads(1)
D=os.path.dirname(os.path.abspath(__file__)); P=lambda f:os.path.join(D,f)
K=json.load(open(P("kannan4_b35.json")))
M=IntegerMatrix(249,505)
for i,row in enumerate(K):
    for j,v in enumerate(row): M[i,j]=v
def prof():
    g=GSO.Mat(M,update=True); pr=[float(g.get_r(i,i))**2 for i in range(249)]
    p=sorted(x for x in pr if 0<x<1e300)
    return (p[-1]/p[0])**(1/249), p[0], sum(1 for x in p if x<=505)
print("pre:", [f"{x:.4f}" if isinstance(x,float) else x for x in prof()], flush=True)
t=time.time(); p=BKZ.EasyParam(35, delta=0.99, verbosity=0)
try:
    BKZ.reduction(M,p)
    print(f"BKZ35-full returned in {time.time()-t:.0f}s status=OK", flush=True)
except Exception as ex:
    print(f"BKZ35-full raised after {time.time()-t:.0f}s: {ex}", flush=True)
print("post:", [f"{x:.4f}" if isinstance(x,float) else x for x in prof()], flush=True)

p=1289
rows=[]
for ln in open("small3.out"):
    if ln.startswith("ROW"):
        _,x,a4,a6=ln.split(); rows.append((int(x)%36,int(a4)%p,int(a6)%p))
def jac(z): return pow(z,(p-1)//2,p)
def q4(z): return pow(z,(p-1)//4,p)
i4=None
for g in range(2,50):
    v=pow(g,(p-1)//4,p)
    if v*v%p==p-1: i4=v; break
def lq4(z):
    v=q4(z)
    for k,r in enumerate([1,i4,p-1,p-i4]):
        if v==r: return k
    return None
print("x  jac_a4 jac_a6  lq4_a4 lq4_a6  D")
for x,a4,a6 in sorted(rows):
    print(f"{x:3d} {jac(a4):5d} {jac(a6):5d}  {lq4(a4) if a4 else '-'}    {lq4(a6) if a6 else '-'}   {(-16*(4*a4**3+27*a6**2))%p==0}")
# check: does jac(a6) depend on x mod 2? group
from collections import defaultdict
g=defaultdict(set)
for x,a4,a6 in rows: g[x%2].add(jac(a6))
print("jac_a6 by x%2:", dict(g))
g=defaultdict(set)
for x,a4,a6 in rows: g[x%4].add(lq4(a6) if a6 else None)
print("lq4_a6 by x%4:", dict(g))
g=defaultdict(set)
for x,a4,a6 in rows: g[x%4].add(lq4(a4) if a4 else None)
print("lq4_a4 by x%4:", dict(g))
g=defaultdict(set)
for x,a4,a6 in rows: g[x%2].add(jac(a4))
print("jac_a4 by x%2:", dict(g))

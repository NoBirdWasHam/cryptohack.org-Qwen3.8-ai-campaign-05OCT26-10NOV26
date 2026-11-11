import sys; sys.path.insert(0,".")
import math, random, gmpy2, dng4

# Build two polynomials with known common root (x0,y0), yz-free, then test res_var both ways
random.seed(7)
x0 = 12345678901234567
y0 = 987654321
# H1 = (x - x0) * (y - 3) + nothing => vanishes at (x0,3); use y0=3 small
A = {(1,0): 1, (0,0): -x0, (0,1): 1}          # x - x0 + y : vanishes where x0 = x+y -> root (x0-3,3)
# make two polys vanishing at (r, 3): P1 = x + y - r ; P2 = x^2 + y^2 - (r^2+9)
r = x0
P1 = {(1,0): 1, (0,1): 1, (0,0): -r}
P2 = {(2,0): 1, (0,2): 1, (0,0): -(r*r+9)}
sys.path.insert(0,".")
# call res_var via attack's closure: easier: replicate tiny version
def mk_res(H1,H2,keep):
    idx = 1 if keep=='x' else 0
    oth = 1-idx
    def coeffs(H,dv):
        d={}
        for (ax,ay),v in H.items():
            if (ax,ay)[idx]==dv: d[(ax,ay)[oth]]=d.get((ax,ay)[oth],0)+v
        return {k:v for k,v in d.items() if v}
    d1=max((t[idx] for t in H1),default=0); d2=max((t[idx] for t in H2),default=0)
    n=d1+d2
    c1=[coeffs(H1,i) for i in range(d1+1)]; c2=[coeffs(H2,i) for i in range(d2+1)]
    rows=[]
    for i in range(d2):
        row=[{} for _ in range(n)]
        for j in range(d1+1): row[i+j]=dict(c1[j])
        rows.append(row)
    for i in range(d1):
        row=[{} for _ in range(n)]
        for j in range(d2+1): row[i+j]=dict(c2[j])
        rows.append(row)
    return rows
rows = mk_res(P1,P2,'x')
print("rows keep=x:")
for rw in rows: print([{k:v for k,v in c.items()} for c in rw])

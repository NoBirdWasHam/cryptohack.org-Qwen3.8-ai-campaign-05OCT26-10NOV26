import itertools
p=1289
rows=[]
for ln in open("small3.out"):
    if ln.startswith("ROW"):
        _,x,a4,a6=ln.split(); rows.append((int(x)%36,int(a4)%p,int(a6)%p))
print("rows:",len(rows))
xs=sorted(set(r[0] for r in rows))
print("x values:",xs)
def jac(z): return pow(z,(p-1)//2,p)
def q4(z): return pow(z,(p-1)//4,p)
# Fp2 w^2=-3
def mulF(x,y): return ((x[0]*y[0]-3*x[1]*y[1])%p,(x[0]*y[1]+x[1]*y[0])%p)
def powF(x,e):
    r=(1,0)
    while e:
        if e&1: r=mulF(r,x)
        x=mulF(x,x); e>>=1
    return r
def q4F(z): return powF(z,(p*p-1)//4)
def q3F(z): return powF(z,(p*p-1)//3)
W=(0,1)
def D(a4,a6): return (-16*(4*a4**3+27*a6**2))%p
cands={}
for nm,f in [("a4",lambda a,b:a),("a6",lambda a,b:b),("D",D),("m48a4",lambda a,b:(-48*a)%p),
             ("a6+w",lambda a,b:(b,1)),("a4+w",lambda a,b:(a,1)),("D+w",lambda a,b:(D(a,b),1)),
             ("j+w",lambda a,b:((-48*a)**3*pow(D(a,b),p-2,p))%p, )]:
    cands["q4_"+nm]=lambda a,b,f=f: q4F(f(a,b)) if f(a,b) else (1,0)
    cands["q3_"+nm]=lambda a,b,f=f: q3F(f(a,b)) if f(a,b) else (1,0)
    cands["q2_"+nm]=lambda a,b,f=f: jac(f(a,b)[0] if isinstance(f(a,b),tuple) else f(a,b))
# homomorphism test: exists g (root of unity) with val(x)==g^x for all rows?
def test(name,f):
    vals={}
    for x,a4,a6 in rows:
        try: vals[x]=f(a4,a6)
        except Exception: return
    gset=set()
    for g in _gens(vals):
        if all(powv(g,x)==v for x,v in vals.items()): gset.add(g)
    if gset: print("*** MATCH",name,"g in",gset)
    else: print("   no   ",name,"distinct:",len(set(vals.values())))
def powv(g,x):
    if isinstance(g,tuple): return powF(g,x)
    return pow(g,x,p)
def _gens(vals):
    vs=set(vals.values())
    if all(isinstance(v,tuple) for v in vs):
        # candidates: any value^(-1)*other consistent: just try all values as g with x=1 anchor if present
        return [v for v in vs]
    return vs
for nm,f in cands.items(): test(nm,f)

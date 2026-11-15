import random, sys
sys.path.insert(0, ".")
from attack import poly_from_terms, eval_poly, p_gcd, p_mod, roots_general, p_strip, p_derive

# same instance as dbg2 (deterministic small case, hand-built)
q = getq = None
from Crypto.Util.number import getPrime
random.seed(99)
q = getPrime(80)
# rebuild streams exactly as dbg2 did (order of draws)
a2=random.randrange(1,q); x2=random.randrange(1,q); b2=random.randrange(1,q)
a3=random.randrange(1,q); x3=random.randrange(1,q); b3=random.randrange(1,q)
pairs=[(157,257),(276,424),(478,864),(886,1360)]
D2=b2*pow(a2-1,q-2,q)%q; C2=(x2-D2)%q
def L2(j): return (C2*pow(a2,j-1,q)+D2)%q
l1={u:u%q for u,_ in pairs}; l1.update({v:v%q for _,v in pairs})
R2=[(L2(u)*v+L2(v)*u)%q for u,v in pairs]

P=[];Qs=[];Rs=[]
for (u,v),R in zip(pairs,R2):
    P.append({u:v%q, v:u%q}); Qs.append((u+v)%q); Rs.append(R%q)
def det3(i,j,k):
    ci=(Qs[j]*Rs[k]-Qs[k]*Rs[j])%q
    cj=-(Qs[i]*Rs[k]-Qs[k]*Rs[i])%q
    ck=(Qs[i]*Rs[j]-Qs[j]*Rs[i])%q
    terms={}
    for idx,c in ((i,ci),(j,cj),(k,ck)):
        if c==0: continue
        for e,cc in P[idx].items():
            terms[e]=(terms.get(e,0)+c*cc)%q
    return poly_from_terms(terms,q)
d1=det3(0,1,2); d2=det3(0,1,3)
print("d1(a2)=",eval_poly(d1,a2,q)," d2(a2)=",eval_poly(d2,a2,q))
# NOTE: attack uses C*g^u form: P(g)=v*g^u+u*g^v, true L_j = C2 g^{j-1}+D
# => R = C2*g^{-1}(v g^u) ... check: v*L2(u)+u*L2(v) = v(C2 g^{u-1}+D)+u(C2 g^{v-1}+D)
#    = (C2/g)(v g^u + u g^v) + D(u+v).  So P(g)=v g^u+u g^v with C=C2/g: fine.
print("expect 0; if nonzero -> det3 bug")
h=p_gcd(d1[:],d2[:],q)
print("deg h:",len(h)-1, "h(a2):",eval_poly(h,a2,q))
if len(h)-1<=3: print(h)

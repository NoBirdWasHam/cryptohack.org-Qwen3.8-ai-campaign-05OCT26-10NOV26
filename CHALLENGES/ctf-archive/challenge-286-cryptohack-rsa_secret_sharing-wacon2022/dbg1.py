# Debug: step through LCG2 recovery on a mini sim with known ground truth.
import random, sys
sys.path.insert(0, ".")
from Crypto.Util.number import getPrime, isPrime
from attack import (find_indices, recover_stream, poly_from_terms, eval_poly,
                    p_gcd, roots_general, p_strip)

random.seed(20261029)
q = getPrime(80)
class LCG:
    def __init__(s,a,x,b): s.a,s.x,s.b=a%q,x%q,b%q
    def fetch(s):
        r=s.x; s.x=(s.a*s.x+s.b)%q; return r
L1=LCG(1,1,1)
a2=random.randrange(1,q); L2=LCG(a2,random.randrange(1,q),random.randrange(1,q))
a3=random.randrange(1,q); L3=LCG(a3,random.randrange(1,q),random.randrange(1,q))
def roll(): return L3.fetch()*q*q + L2.fetch()*q + L1.fetch()
pr=[]
while len(pr)<8:
    p=roll()
    if isPrime(p): pr.append(p)
ns=[pr[2*i]*pr[2*i+1] for i in range(4)]

pairs=[tuple(sorted((j for j in [None]))) for _ in []]  # placeholder
# find indices
cand=[find_indices(n,q) for n in ns]
print("cands:",cand)
import itertools
combo=None
for c in itertools.product(*cand):
    T=[x for pv in c for x in pv]
    if len(set(T))==8 and sorted(T)==T: combo=c; break
print("combo:",combo)
(u,v),(u2,v2),(u3,v3),(u4,v4)=[(a,b) for a,b in combo]
# true L2 values: ground truth stream values at those indices
# regenerate streams to find true C,D: we know x1,b,a2: fetch j value = a2^(j-1)x1 + b*(a2^(j-1)-1)/(a2-1)
L2s=LCG(a2,1,1)  # dummy
# recompute true stream from original L2 object state? easier: rebuild with same seed values
random.seed(20261029)
q2=getPrime(80)  # same q? getPrime uses random => same sequence
print("same q:",q2==q)
a2t=random.randrange(1,q); x2t=random.randrange(1,q); b2t=random.randrange(1,q)
a3t=random.randrange(1,q); x3t=random.randrange(1,q); b3t=random.randrange(1,q)
def L2v(j):
    if a2t==1: return (x2t+(j-1)*b2t)%q
    C=(x2t - b2t*pow(a2t-1,q-2,q))%q
    D=b2t*pow(a2t-1,q-2,q)%q
    return (C*pow(a2t,j-1,q)+D)%q
def L3v(j):
    if a3t==1: return (x3t+(j-1)*b3t)%q
    C=(x3t - b3t*pow(a3t-1,q-2,q))%q
    D=b3t*pow(a3t-1,q-2,q)%q
    return (C*pow(a3t,j-1,q)+D)%q
p_true=lambda j: L3v(j)*q*q + L2v(j)*q + j
ok=all(p_true(j)==pr[i] for i,j in enumerate([x for pv in combo for x in pv]))
print("ground-truth stream model OK:",ok)

l1={}
for (uu,vv) in combo: l1[uu]=uu; l1[vv]=vv
R2=[((n-l1[uu]*l1[vv])//q)%q for n,(uu,vv) in zip(ns,combo)]
# check linear relation
chk=all((L2v(uu)*vv+L2v(vv)*uu)%q==r for r,(uu,vv) in zip(R2,combo))
print("R2 linear relation holds:",chk)

# build sparse polys as recover_stream does, and evaluate d1,d2 at TRUE g=a2
P=[];Qs=[];Rs=[]
for (uu,vv),R in zip(combo,R2):
    terms={uu:vv%q, vv:uu%q}
    P.append(terms); Qs.append((uu+vv)%q); Rs.append(R%q)
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
print("deg d1,d2:",len(d1)-1,len(d2)-1)
print("d1(a2)==0:",eval_poly(d1,a2,q),"  d2(a2)==0:",eval_poly(d2,a2,q))
h=p_gcd(d1[:],d2[:],q)
print("deg gcd:",len(h)-1)
print("h(a2)==0:",eval_poly(h,a2,q))
if len(h)-1<=6:
    print("h coeffs:",h)
rts=roots_general(h,q)
print("roots_general:",rts[:10],"true a2:",a2t,"in roots:",a2t in rts)
sols=recover_stream(combo,l1,R2,q)
print("recover_stream sols:",[(str(g)[:20]) for g,C,D in sols],"true:",a2t)

# Debug v2: simulate recording TRUE roll indices and true a2/C2/D2.
import random, sys
sys.path.insert(0, ".")
from Crypto.Util.number import getPrime, isPrime
from attack import poly_from_terms, eval_poly, p_gcd, roots_general, recover_stream

random.seed(99)
q = getPrime(80)
class LCG:
    def __init__(s,a,x,b): s.a,s.x,s.b=a%q,x%q,b%q
    def fetch(s):
        r=s.x; s.x=(s.a*s.x+s.b)%q; return r
    def closed(s,j):  # value returned on j-th fetch (1-based)
        if s.a==1: return (s.x0+(j-1)*s.b)%q
        D=s.b*pow(s.a-1,q-2,q)%q
        C=(s.x0-D)%q
        return (C*pow(s.a,j-1,q)+D)%q
def patched(c):
    c.x0=c.x; return c
L1=patched(LCG(1,1,1))
a2=random.randrange(1,q); L2=patched(LCG(a2,random.randrange(1,q),random.randrange(1,q)))
a3=random.randrange(1,q); L3=patched(LCG(a3,random.randrange(1,q),random.randrange(1,q)))
idx=0; pr=[]; pairidx=[]
while len(pr)<8:
    idx+=1
    p=L3.closed(idx)*q*q + L2.closed(idx)*q + L1.closed(idx)
    if L3.closed(idx)*q*q + L2.closed(idx)*q + idx == p and isPrime(p): pr.append(p); pairidx.append(idx)
# sanity vs real fetch streams
ns=[pr[2*i]*pr[2*i+1] for i in range(4)]
pairs=[(pairidx[2*i],pairidx[2*i+1]) for i in range(4)]
print("true pairs:",pairs,"a2:",a2)
l1={}
for (u,v) in pairs: l1[u]=u%q; l1[v]=v%q
R2=[((n-l1[u]*l1[v])//q)%q for n,(u,v) in zip(ns,pairs)]
chk=all((L2.closed(u)*v+L2.closed(v)*u)%q==r for r,(u,v) in zip(R2,pairs))
print("R2 relation with true L2:",chk)
# NOTE attack assumes L_j = C g^j + D (g^{j} form); closed uses g^{j-1}: same family.
sols=recover_stream(pairs,l1,R2,q)
print("sols:",sols)
# --- internals ---
from attack import poly_from_terms, eval_poly, p_gcd, roots_general
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
print("deg d1,d2:",len(d1)-1,len(d2)-1,"| d1(a2):",eval_poly(d1,a2,q),"| d2(a2):",eval_poly(d2,a2,q))
h=p_gcd(d1[:],d2[:],q)
print("deg h:",len(h)-1,"| h(a2):",eval_poly(h,a2,q))
rts=roots_general(h[:],q)
print("roots:",rts,"| a2 in roots:",a2 in rts)
print("true a2:",a2)

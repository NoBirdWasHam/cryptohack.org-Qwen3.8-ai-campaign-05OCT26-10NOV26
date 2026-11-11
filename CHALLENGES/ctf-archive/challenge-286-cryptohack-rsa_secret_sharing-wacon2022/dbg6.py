# Deterministic repro with hardcoded primes; compare fast vs slow powmod on h.
import sys; sys.path.insert(0,".")
from attack import (poly_from_terms, eval_poly, p_gcd, p_strip, p_mod, p_powmod,
                    p_powmod_fast, roots_general, p_derive, Reducer)
q = 241880731940898086787946482398080037671963   # ~86-bit? make sure prime
from Crypto.Util.number import isPrime as _sp
if not _sp(q):
    q = 79234567890123456789012345678901234567  # fallback attempt
    while not _sp(q): q += 2
print("q bits:", q.bit_length())
# deterministic params (no RNG)
a2 = 123456789012345678901234567 % q
x2 = 42; b2 = 7
D2=b2*pow(a2-1,q-2,q)%q; C2=(x2-D2)%q
L2=lambda j:(C2*pow(a2,j-1,q)+D2)%q
pairs=[(900,1500),(1600,2100),(2300,2900),(3100,3600)]
P=[];Qs=[];Rs=[]
for (u,v) in pairs:
    R=(L2(u)*v+L2(v)*u)%q
    P.append({u:v%q,v:u%q}); Qs.append((u+v)%q); Rs.append(R)
def det3(i,j,k):
    ci=(Qs[j]*Rs[k]-Qs[k]*Rs[j])%q
    cj=-(Qs[i]*Rs[k]-Qs[k]*Rs[i])%q
    ck=(Qs[i]*Rs[j]-Qs[j]*Rs[i])%q
    terms={}
    for idx,c in ((i,ci),(j,cj),(k,ck)):
        if c==0: continue
        for e,cc in P[idx].items(): terms[e]=(terms.get(e,0)+c*cc)%q
    return poly_from_terms(terms,q)
d1=det3(0,1,2); d2=det3(0,1,3)
print("deg d1,d2:",len(d1)-1,len(d2)-1)
h=p_gcd(d1[:],d2[:],q)
print("deg h:",len(h)-1,"h(a2)==0:",eval_poly(h,a2,q)==0)
# X^q mod h: fast vs slow
xs=p_powmod([0,1],q,h[:],q)
xf=p_powmod_fast([0,1],q,h[:],q)
print("powmod fast==slow:",xs==xf)
for xq,tag in ((xs,'slow'),):
    while len(xq)<2: xq.append(0)
    xq[1]=(xq[1]-1)%q; p_strip(xq)
    inter=p_gcd(h[:],xq,q,stop_deg=10**9)
    print(tag,"deg inter:",len(inter)-1,"inter(a2)==0:",eval_poly(inter,a2,q)==0)
    rts=roots_general(h[:],q)
    print("roots_general deg<=2?" , "a2 in roots:", a2 in rts, "count:",len(rts))

"""ECLCG wall evidence suite (run: python3 check_wall_evidence.py), 2026-11-01.
1) synthetic real-size: gcd(14 triple-minors of D_i) == p exactly; |M|~2^619, |M/p|~2^308
2) exact identities: D_{i+1} = a D_i - f_i p (f_i = e_{i+1}-e_i, e_i=floor((a k_i+b)/p))
   and M_ctr(i) = p*(f_{i-1} D_i - f_i D_{i-1})   [explains c_i "dust" ~2^308 as
   cancellation residue of two ~2^618 products]
3) vacuity theorem (empirical side-note): field Groebner cannot encode p|M (see AAR proof).
"""
import random
from Crypto.Util.number import getPrime
from math import gcd
q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
random.seed(7)
p = getPrime(311); d = random.randrange(1,q)
a,b,x = [random.randrange(2,p) for _ in range(3)]
ks=[]; xx=x
for _ in range(17): xx=(a*xx+b)%p; ks.append(xx)
ts=[];us=[]
for k in ks:
    z=random.randrange(q); r=random.randrange(1,q)
    s=(z+r*d)%q*pow(k,-1,q)%q
    ts.append(z*pow(s,-1,q)%q); us.append(r*pow(s,-1,q)%q)
K=[(ts[i]+us[i]*d)%q for i in range(17)]
m=[(ks[i]-K[i])//q for i in range(17)]
assert all(0<=mm<2**56 and K[i]+mm*q==ks[i] for i,mm in enumerate(m))
D=[ks[i+1]-ks[i] for i in range(16)]
assert D==[K[i+1]-K[i]+(m[i+1]-m[i])*q for i in range(16)]
Mctr={i: D[i+1]*D[i-1]-D[i]*D[i] for i in range(1,15)}
g=0
for Mi in Mctr.values(): g=gcd(g,Mi)
assert g==p and all(Mi%p==0 for Mi in Mctr.values())
e=[(a*ks[i]+b)//p for i in range(16)]
f={i: e[i+1]-e[i] for i in range(15)}
assert all(D[i+1]==a*D[i]-f[i]*p for i in range(15))
assert all(Mctr[i]==p*(f[i-1]*D[i]-f[i]*D[i-1]) for i in range(1,15))
print("ALL ASSERTIONS PASS")
print("bit |M_ctr| :", sorted(Mi.bit_length() for Mi in Mctr.values()))
print("bit |M/p|   :", sorted((Mi//p).bit_length() for Mi in Mctr.values()))
lg = 256+16*56  # candidate (d, n_1..n_16) box bits
# P(all 14 minors share one 311-bit prime) ~ sum_{p'} p'^-14 ~ 2^(303-14*311); candidates 2^lg:
spur = lg + 303 - 14*311
print("n-form box bits", lg, "-> expected spurious ~ 2^%d (solution unique)" % spur)

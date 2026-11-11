import random, sys
sys.path.insert(0,".")
from attack import Reducer, p_mod
from Crypto.Util.number import getPrime
random.seed(7)
q=getPrime(342)
# replicate trial 0 of t_mul: dm=102 dr=199
dm=random.randint(5,400); print("dm",dm)
m=[random.randrange(q) for _ in range(dm)]+[1]
dr=random.randint(0,2*dm-1); print("dr",dr)
rr=[random.randrange(q) for _ in range(dr+1)]
red=Reducer(m,q)
a=red.rem(rr[:])
b=p_mod(rr[:],m,q)
print("match:",a==b, len(a), len(b))
# naive long division to see where it differs
def naive(r,m,q):
    r=r[:]; dg=len(m)-1
    linv=pow(m[-1],q-2,q); mm=[c*linv%q for c in m]
    for i in range(len(r)-1, dg-1, -1):
        c=r[i]
        if c:
            for k in range(dg+1):
                r[i-dg+k]=(r[i-dg+k]-c*mm[k])%q
    return r[:dg]
from attack import p_strip
c=naive(rr[:],m,q); p_strip(c)
print("naive==p_mod:",c==b)
# reproduce Q computation
r=[x%q for x in rr]; p_strip(r)
n=len(r)-1
d=n-red.dg
inv=red.inv_mrev(d+1)
rrev=list(reversed(r))
from attack import m_mul, m_mul_trunc
Q=m_mul_trunc(rrev,inv,d+1)
# naive quotient:
qq=rr[:]; dg=len(m)-1; linv=pow(m[-1],q-2,q); mm=[x*linv%q for x in m]
QQ=[0]*(d+1)
for i in range(len(qq)-1,dg-1,-1):
    c=qq[i]%q
    QQ[i-dg]=c
    for k in range(dg):
        qq[i-dg+k]=(qq[i-dg+k]-c*mm[k])%q
print("deg Q fast:",len(Q)-1,"naive:",len(QQ)-1)
bad=[i for i in range(d+1) if (Q[i] if i<len(Q) else 0)!=QQ[i]]
print("Q mismatch positions:",bad[:10],"count",len(bad))
print("inv len:",len(inv))
# check inv correctness: mrev*inv == 1 mod x^{d+1}
t=m_mul_trunc(list(reversed(mm)),inv,d+1)
p_strip(t)
print("mrev*inv:",t[:5],"... len",len(t))

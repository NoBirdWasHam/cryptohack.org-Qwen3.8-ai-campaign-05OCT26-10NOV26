import random, sys
sys.path.insert(0,".")
from attack import m_mul, m_mul_trunc, p_mod, Reducer, p_strip
from Crypto.Util.number import getPrime
random.seed(7)
q=getPrime(342)
# replay m_mul trials to sync RNG state
for trial in range(30):
    la=random.randint(1,random.choice([5,37,80,200,1500]))
    lb=random.randint(1,random.choice([5,37,80,200,1500]))
    a=[random.randrange(q) for _ in range(la)]
    b=[random.randrange(q) for _ in range(lb)]
trial=0
dm=random.randint(5,400); print("dm",dm)
m=[random.randrange(q) for _ in range(dm)]+[1]
dr=random.randint(0,2*dm-1); print("dr",dr)
rr=[random.randrange(q) for _ in range(dr+1)]
red=Reducer(m,q)
a=red.rem(rr[:])
b=p_mod(rr[:],m,q)
print("match:",a==b)
# naive monic long division
def naive(r,m,q):
    r=r[:]; dg=len(m)-1
    linv=pow(m[-1],q-2,q); mm=[c*linv%q for c in m]
    Q=[0]*(len(r)-dg) if len(r)>=dg else []
    for i in range(len(r)-1, dg-1, -1):
        c=r[i]
        if c:
            Q[i-dg]=c
            for k in range(dg+1):
                r[i-dg+k]=(r[i-dg+k]-c*mm[k])%q
    p_strip(r)
    return r[:dg], Q
mm_monic=[c*pow(m[-1],q-2,q)%q for c in m]
rem_naive, Qn = naive(rr[:], m, q)
r=[x%q for x in rr]; p_strip(r)
n=len(r)-1; d=n-red.dg
inv=red.inv_mrev(d+1)
rrev=list(reversed(r))
Qf=m_mul_trunc(rrev,inv,d+1)
print("deg r:",n,"dg:",red.dg,"d:",d)
print("len Qf",len(Qf),"len Qn",len(Qn))
bad=[i for i in range(max(len(Qf),len(Qn))) if (Qf[i] if i<len(Qf) else 0)!=(Qn[i] if i<len(Qn) else 0)]
print("Q bad:",bad[:8],"cnt",len(bad))
# verify inv
t=m_mul_trunc(red.mrev,inv,d+1); p_strip(t)
print("mrev*inv==1:",t==[1])
print("rem naive match p_mod:", rem_naive==b)
print("a:",len(a),"b:",len(b))

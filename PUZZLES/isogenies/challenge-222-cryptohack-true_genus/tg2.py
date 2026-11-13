import json, math
d = json.load(open(r"~/Practice_runs/cryptohack_org/challenge-222-cryptohack-true_genus/output.txt"))
ls=[3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,139]
p=2*math.prod(ls)-1
data=d["challenge_data"]
# find i: sqrt(-1) mod p
i=None
for g in range(2,100):
    v=pow(g,(p-1)//4,p)
    if (v*v)%p==p-1: i=v; break
print("i =",i)
def q4(z):  # returns log base i of z^((p-1)/4) in Z/4, z in Fp
    v=pow(z,(p-1)//4,p)
    if v==1: return 0
    if v==p-1: return 2
    if v==i: return 1
    if v==p-i: return 3
    return None  # not a 4th root (shouldn't happen)
def q2(z): return pow(z,(p-1)//2,p)  # +-1
def logq2(z): return 0 if z==1 else 1
res=[]
for k,inst in enumerate(data):
    a4A,a6A=inst["EA"]["a4"][0]%p,inst["EA"]["a6"][0]%p
    a4B,a6B=inst["EB"]["a4"][0]%p,inst["EB"]["a6"][0]%p
    a4C,a6C=inst["EC"]["a4"][0]%p,inst["EC"]["a6"][0]%p
    # quartic character logs of a6, a4, and discriminant-ish combos
    r={}
    for nm,(x,y,z) in {"a6":(a6A,a6B,a6C),"a4":(a4A,a4B,a4C)}.items():
        la,lb,lc=q4(x),q4(y),q4(z)
        r[nm+"q4"]=(la,lb,lc,(lc-la-lb)%4)
        r[nm+"q2"]=(logq2(q2(x)),logq2(q2(y)),logq2(q2(z)),(logq2(q2(z))-logq2(q2(y))-logq2(q2(x)))%2)
    res.append(r)
# summary: distribution of residual for each character
from collections import Counter
for key in ["a6q4","a4q4","a6q2","a4q2"]:
    c=Counter(r[key][3] for r in res)
    print(key, dict(c))

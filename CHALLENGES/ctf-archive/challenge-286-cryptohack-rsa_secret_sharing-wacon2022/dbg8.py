# true_sim WITH ground truth: if solve_instance fails, force the true combo.
import random, sys, time
sys.path.insert(0, ".")
from Crypto.Util.number import getPrime, isPrime
from attack import solve_instance, _solve_with_pairs

random.seed(31337)
q = getPrime(120)
class LCG:
    def __init__(s,a,x,b): s.a,s.x,s.b=a%q,x%q,b%q
    def fetch(s):
        r=s.x; s.x=(s.a*s.x+s.b)%q; return r
L1=LCG(1,1,1)
a2=random.randrange(1,q); L2=LCG(a2,random.randrange(1,q),random.randrange(1,q))
a3=random.randrange(1,q); L3=LCG(a3,random.randrange(1,q),random.randrange(1,q))
idx=0; pr=[]; ti=[]
while len(pr)<8:
    idx+=1
    p=L3.fetch()*q*q + L2.fetch()*q + L1.fetch()
    if isPrime(p): pr.append(p); ti.append(idx)
ns=[pr[2*i]*pr[2*i+1] for i in range(4)]
true_pairs=[(ti[2*i],ti[2*i+1]) for i in range(4)]
print("true pairs:",true_pairs,"a2:",a2,"a3:",a3)
out=solve_instance(q,ns,verbose=True)
print("solve_instance:", "OK" if out else "FAIL")
print("--- force true combo ---")
out2=_solve_with_pairs(q,ns,true_pairs,verbose=True)
print("forced:", "OK" if out2 else "FAIL")

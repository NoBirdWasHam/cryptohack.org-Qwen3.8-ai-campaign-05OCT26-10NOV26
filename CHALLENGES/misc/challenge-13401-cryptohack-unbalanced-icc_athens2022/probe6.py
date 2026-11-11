import sys; sys.path.insert(0,".")
import math, random, gmpy2
import dng4

random.seed(1)
def rprime(b): return int(gmpy2.next_prime(random.getrandbits(b)|(1<<(b-1))|1))
p,q=rprime(256),rprime(768); N=p*q; e=rprime(1023)
m,t,a=3,1,1; xb=192; L=float(e).bit_length()
rows = dng4.make_rows(N,e,m,t,a)
# name rows in order
names=[]
for k in range(m):
    for i in range(1,m-k+1):
        for b in (0,1): names.append(f"g{k},{i},{b}")
for k in range(m+1):
    for j in range(t+1): names.append(f"h{k},{j}")
seen=set()
tot_coeff=0
for nm,rw in zip(names,rows):
    piv=[k for k in rw if k not in seen][0]
    seen|=set(rw)
    co=abs(rw[piv])
    cb = dng4.bl(co)
    tot_coeff += cb
    print(f"{nm:10s} pivot {str(piv):12s} coeff_bits={cb:7.1f}")
print("sum coeff bits", tot_coeff)
want = 40*L
print("expected e-powers bits 40L =", want)
print("excess", tot_coeff - want)

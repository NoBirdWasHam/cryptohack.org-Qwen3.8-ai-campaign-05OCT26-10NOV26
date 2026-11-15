import sys; sys.path.insert(0,".")
import math, random, gmpy2
import dng4
from flint import fmpz_mat

random.seed(1)
def rprime(b): return int(gmpy2.next_prime(random.getrandbits(b)|(1<<(b-1))|1))
p,q=rprime(256),rprime(768); N=p*q; e=rprime(1023)
m,t,a=3,1,1
rows = dng4.make_rows(N,e,m,t,a)
print("nrows", len(rows))
seen=set(); dupcol=0
for ri,rw in enumerate(rows):
    new=[k for k in rw if k not in seen]
    seen |= set(rw)
    if len(new)!=1: print("row",ri,"new:",len(new), new[:6])
allcols=set()
for rw in rows: allcols|=set(rw)
print("cols total", len(allcols))
# mixed yz leftovers?
mixed=[c for c in allcols if c[1]>0 and c[2]>0]
print("mixed cols", len(mixed), mixed[:5])
# count by z degree
from collections import Counter
print("zdeg", Counter(c[2] for c in allcols))
print("ydeg", Counter(c[1] for c in allcols))
# check each col introduced exactly once (first row containing it)
first={}
for ri,rw in enumerate(rows):
    for k in rw:
        if k not in first: first[k]=ri
c=Counter(first.values()); print("rows introducing k cols:", Counter(c.values()))

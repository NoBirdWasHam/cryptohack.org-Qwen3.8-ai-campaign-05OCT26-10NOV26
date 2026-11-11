ns={}
for line in open('output.txt'):
    line=line.strip()
    if line: exec(line, ns)
n=ns['n']
print("n mod 3,9,27:", n%3, n%9, n%27)
# trial division to 10^6
from sympy import primerange
import math
d=1
smallfac=[]
for p in primerange(2,100000):
    if n%p==0: smallfac.append(p); n//=p  # multiplicity unlikely but fine
print("small factors:", smallfac, "reduced n bits", n.bit_length())
# squarefull check: is n divisible by a square of a prime?

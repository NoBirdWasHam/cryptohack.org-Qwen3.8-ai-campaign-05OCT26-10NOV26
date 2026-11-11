#!/usr/bin/env python
import sys; sys.set_int_max_str_digits(100000)
import gmpy2, re
from sympy.ntheory.modular import crt
txt=open('output.txt').read()
ns=[];cs=[]
for blk in re.split(r'\n\s*\n', txt.strip()):
    d={}
    for line in blk.splitlines():
        if '=' in line:
            k,v=line.split('=',1); d[k.strip()]=int(v.strip())
    if 'n' in d and 'c' in d: ns.append(d['n']); cs.append(d['c'])
M,l=crt(ns,cs)
print("M bits:", M.bit_length())
# verify M == c_i mod N_i
ok=all(M%ns[i]==cs[i] for i in range(len(ns)))
print("verify all residues:", ok)
r,exact=gmpy2.iroot(M,3)
print("exact cube:", exact)
if exact:
    flag=r.to_bytes((r.bit_length()+7)//8,'big')
    print("FLAG:", flag.decode())

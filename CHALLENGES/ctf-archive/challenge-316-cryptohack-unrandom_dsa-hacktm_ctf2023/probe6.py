#!/usr/bin/env python3
# Probe A: y determinism vs seed (deployed code may differ from leaked server.py)
import socket, random, math
import gmpy2
from gmpy2 import is_prime as gp

def conn(q,p,g,seed):
    s=socket.create_connection(("archive.cryptohack.org",2783),timeout=40)
    f=s.makefile("rw",encoding="utf-8",errors="replace")
    def ask(sub):
        d=""
        while sub not in d:
            c=f.read(1)
            if not c: return d+"<<EOF>>"
            d+=c
        return d
    out=""
    try:
        ask("q = "); f.write(str(q)+"\n"); f.flush()
        ask("p = "); f.write(str(p)+"\n"); f.flush()
        ask("g = "); f.write(str(g)+"\n"); f.flush()
        ask("hex"); f.write(seed+"\n"); f.flush()
        s.settimeout(40)
        while True:
            c=f.read(1)
            if not c: break
            out+=c
            if "sign = " in out: break
    except Exception as e:
        out+=f"<<{type(e).__name__}>>"
    s.close()
    return out

rng=random.Random(1234)
while True:
    q=rng.randrange(1<<159,1<<160)|1
    if gp(q): break
while True:
    sq=rng.getrandbits(1024-160-1)|1
    p=sq*q+1
    if p.bit_length()==1024 and gp(p) and gp(sq): break
fac=[q,sq]
for h in range(2,100):
    if all(pow(h,(p-1)//l,p)!=1 for l in [2]+[x for x in fac]): pass
# q composite factors unknown for h-test? p-1 = q*sq; q prime. factors: 2, q, sq, and any sq... sq prime.
h=2
while any(pow(h,(p-1)//l,p)==1 for l in (2,q,sq)): h+=1
g=pow(h,sq,p)
print("params ok", flush=True)
o1=conn(q,p,g,"1337")
o2=conn(q,p,g,"1337")
o3=conn(q,p,g,"beef")
print("A1:", o1[:150])
print("A2:", o2[:150])
print("A3:", o3[:150])
print("same seed same y:", o1==o2, "| diff seed diff y:", o1!=o3)

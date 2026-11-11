#!/usr/bin/env python
# Self-test: fabricate a 15-char flag, compute ct, run the SAME lattice solve, check recovery.
import gmpy2, ast, re
from gmpy2 import mpfr, get_context
get_context().precision=600
src=open('real_eisenstein_provided.py').read()
PRIMES=ast.literal_eval(re.search(r'PRIMES = (\[.+\])',src).group(1))
FLAG0=re.search(r'FLAG = "(.+?)"',src).group(1)
L=len(FLAG0); PRIMES=PRIMES[:L]
known={i:ord(c) for i,c in enumerate(FLAG0) if c!='?'}
unk=[i for i in range(L) if FLAG0[i]=='?']
m=len(unk)
sqrt_p=[mpfr(gmpy2.sqrt(mpfr(p))) for p in PRIMES]

# fabricate a known flag body (15 printable chars)
body="abcdefghij12345"
assert len(body)==m
flag=list(FLAG0)
for j,i in enumerate(unk): flag[i]=body[j]
flag="".join(flag)
print("FAKE FLAG:",flag)
h=sum(mpfr(ord(c))*sqrt_p[i] for i,c in enumerate(flag))
ct=int(h*mpfr(2)**256)
print("fake ct:",ct)

# --- now run the identical solve pipeline ---
h_known=sum(mpfr(known[i])*sqrt_p[i] for i in known)
Tw=mpfr(ct)/mpfr(2)**256-h_known
S=2**340
v=[int(round(sqrt_p[unk[j]]*S)) for j in range(m)]
w=int(round(Tw*S))
import sympy as sp
G=[]
for j in range(m):
    r=[0]*(m+1); r[j]=1; r[m]=v[j]; G.append(r)
G.append([0]*(m+1)); G[-1][m]=w
B=sp.Matrix(G).lll()
def n2(r): return sum(int(r[k])**2 for k in range(m+1))
rows=[B.row(i) for i in range(m+1)]
rows.sort(key=n2)
def recon(zz):
    h2=h_known+sum(mpfr(zz[j])*sqrt_p[unk[j]] for j in range(m))
    return int(h2*mpfr(2)**256)==ct
found=None
for r in rows:
    if not any(int(r[k])!=0 for k in range(m+1)): continue
    z=[int(r[k+1]) for k in range(m)]  # a-block = last m coords? NO
    # row layout: (e_j, v_j) => col 0..m-1 = a-block, col m = value. So a-block = first m coords
    za=[int(r[k]) for k in range(m)]
    for zz in (z,[-x for x in z], za,[-x for x in za]):
        if recon(zz): found=zz; break
    if found: break
print("recovered?", found is not None)
if found:
    out=list(FLAG0)
    for j,i in enumerate(unk): out[i]=chr(found[j])
    print("GOT:", "".join(out), " match:", "".join(out)==flag)
# print norms of reduced rows
print("reduced row norms (log2):", [ (n2(r).bit_length()) for r in rows][:16])

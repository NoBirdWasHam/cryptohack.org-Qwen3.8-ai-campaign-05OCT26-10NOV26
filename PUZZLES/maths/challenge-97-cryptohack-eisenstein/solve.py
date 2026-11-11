#!/usr/bin/env python
# real_eisenstein (97): h=sum_i ord(FLAG[i])*sqrt(PRIMES[i]); ct=floor(h*2^256).
# CVP in Z^15: find z in [32,126]^15 with sum z_j sqrt(p_j) in [Tw, Tw+2^-256), Tw=ct/2^256-h_known.
# Lattice (m+1 x m+1): rows g_j=(e_j, v_j) j=1..m, g_0=(0..0,D).  CVP target t=(0..0,w).
#   v_j=round(sqrt(p_j)*S), w=round(Tw*S), S=2^340, D=2^380.  Flag is the UNIQUE nearest
#   lattice point (norm ~2^84, gap 2^256 over near-relations). LLL + Babai recovers z.
import gmpy2, ast, re
from gmpy2 import mpfr, get_context
get_context().precision=600
src=open('real_eisenstein_provided.py').read()
ct=int(re.search(r'ciphertext: (\d+)',src).group(1))
PRIMES=ast.literal_eval(re.search(r'PRIMES = (\[.+\])',src).group(1))
FLAG0=re.search(r'FLAG = "(.+?)"',src).group(1)
L=len(FLAG0); PRIMES=PRIMES[:L]
sqrt_p=[mpfr(gmpy2.sqrt(mpfr(p))) for p in PRIMES]
known={i:ord(c) for i,c in enumerate(FLAG0) if c!='?'}
unk=[i for i in range(L) if FLAG0[i]=='?']
m=len(unk)
h_known=sum(mpfr(known[i])*sqrt_p[i] for i in known)
Tw=mpfr(ct)/mpfr(2)**256-h_known
S=2**340; D=2**380
v=[int(round(sqrt_p[unk[j]]*S)) for j in range(m)]
w=int(round(Tw*S))
import sympy as sp
G=[]
for j in range(m):
    row=[0]*(m+1); row[j]=1; row[m]=v[j]; G.append(row)   # (e_j, v_j)
G.append([0]*(m+1)); G[-1][m]=D                             # (0..0, D)
B=sp.Matrix(G).lll()
# Babai: nearest lattice point to t=(0..0,w)
t=sp.Matrix([0]*m+[w])
x=B.inv()*t                       # exact rationals (B is (m+1)x(m+1) invertible)
cand=[int(sp.floor(xi+sp.Rational(1,2))) for xi in x]       # round to nearest integer
P=B*sp.Matrix(cand)               # nearest lattice point
z=[int(P[j]) for j in range(m)]   # first m coords = flag coefficients
def recon(zz):
    h2=h_known+sum(mpfr(zz[j])*sqrt_p[unk[j]] for j in range(m))
    return int(h2*mpfr(2)**256)==ct
def in_box(zz): return all(32<=x<=126 for x in zz)
print("z:",z,"in_box",in_box(z),"recon",recon(z))
# local refinement: try +/-1 in each coord to fix any Babai off-by-one
best=z
def trylocal(zz):
    if in_box(zz) and recon(zz): return True
    return False
import itertools
if not recon(z):
    for d in (1,2):
        found=False
        # one-coordinate perturbations
        for j in range(m):
            for dd in range(-d,d+1):
                if dd==0: continue
                zz=z[:]; zz[j]+=dd
                if trylocal(zz): best=zz; found=True; break
            if found: break
        if found: break
print("refined recon:",recon(best))
out=list(FLAG0)
for j,i in enumerate(unk): out[i]=chr(best[j])
print("FLAG:","".join(out))

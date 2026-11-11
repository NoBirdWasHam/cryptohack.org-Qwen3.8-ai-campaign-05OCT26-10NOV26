import sys; sys.path.insert(0,".")
import math, dng3
from flint import fmpz_mat
import gmpy2, random
random.seed(5)
def rprime(b): return int(gmpy2.next_prime(random.getrandbits(b)|(1<<(b-1))|1))
p,q=rprime(256),rprime(768); N=p*q; phi=(p-1)*(q-1)
d=rprime(192); e=int(pow(d,-1,phi))
rows,_ = dng3.region_rows(N,e,3,192,256)
M,mons = dng3.build_matrix(rows,192,256)
print("n",M.nrows,"ncols",M.ncols)
detv,pd,tri = dng3.pivot_minor_det(M,rows,mons)
print("minor det bitlen",detv.bit_length(),"prod diag bitlen",pd.bit_length(),"tri",tri)
A = fmpz_mat(M.nrows,M.ncols,[int(M[r,c]) for r in range(M.nrows) for c in range(M.ncols)])
G = A*A.transpose()
gd = int(G.det())
print("gramdet bitlen",gd.bit_length(), "gramdet^(1/2n) bits", gd.bit_length()/(2*M.nrows))
rn=[max(abs(int(M[r,c])).bit_length() for c in range(M.ncols)) for r in range(M.nrows)]
print("row max-bit min/max", min(rn), max(rn))
print("minor det per-row", detv.bit_length()/M.nrows, "gram per-row", gd.bit_length()/(2*M.nrows))

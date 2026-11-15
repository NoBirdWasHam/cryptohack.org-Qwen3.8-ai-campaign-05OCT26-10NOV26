from sympy import Matrix, QQ
from math import gcd
from functools import reduce
rows=list(range(2,103))
A=Matrix(len(rows),100,lambda ii,jj:( ((-1)**(rows[ii]-2))*rows[ii]*((rows[ii]-1)**jj) if jj<=rows[ii]-1 else 0))
ns=A.T.nullspace()
print("dim:",len(ns))
v=ns[0].applyfunc(QQ)
import sympy
lams=[x.q for x in v]
Lc=sympy.lcm(lams)
M=[int(x*Lc) for x in v]
g=reduce(gcd,[abs(x) for x in M])
M=[x//g for x in M]
print("mu max bits:", max(x.bit_length() for x in M))
print("kernel ok:", all(sum(M[i]*A[i,j] for i in range(101))==0 for j in range(100)))
open("mu_kernel.txt","w").write(repr(M))

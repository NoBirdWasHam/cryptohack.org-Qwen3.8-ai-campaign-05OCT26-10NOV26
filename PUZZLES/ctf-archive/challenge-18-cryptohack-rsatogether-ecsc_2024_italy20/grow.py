from fractions import Fraction as F
# general: R = number of random coeffs; equations m=2..R+3 (R+2 eqs); unknowns d,r_1..r_R (R+1)
# kernel dim 1; set nu[R+3]=1; solve square system rows j=0..R (R+1 eqs) unknowns nu_2..nu_{R+2} (R+1)
def kernel(R):
    rows=list(range(2,R+4))
    A=[[ (F(((-1)**(m-2))*m*((m-1)**j)) if j<=m-1 else F(0)) for j in range(R+1)] for m in rows]
    # unknowns nu for rows 2..R+2 (indices 0..R), nu[R+3]=1 (index R+1)
    # equations: sum nu_m A[m][j]=0 -> M x = b with b_j = -A[last][j]
    M=[[A[i][j] for i in range(R+1)] for j in range(R+1)]
    b=[-A[R+1][j] for j in range(R+1)]
    # gaussian elimination
    n=R+1
    for c in range(n):
        piv=None
        for r in range(c,n):
            if M[r][c]!=0: piv=r;break
        if piv is None: continue
        M[c],M[piv]=M[piv],M[c]; b[c],b[piv]=b[piv],b[c]
        pv=M[c][c]
        M[c]=[x/pv for x in M[c]]; b[c]=b[c]/pv
        for r in range(n):
            if r!=c and M[r][c]!=0:
                fct=M[r][c]
                M[r]=[a-fct*bb for a,bb in zip(M[r],M[c])]; b[r]-=fct*b[c]
    return b
import sympy
for R in (5,10,15,20,25,30):
    v=kernel(R)
    Lc=sympy.lcm([x.denominator for x in v]+[1])
    ints=[int(x*Lc) for x in v]+[int(Lc)]
    from math import gcd
    from functools import reduce
    g=reduce(gcd,[abs(x) for x in ints])
    ints=[x//g for x in ints]
    print(R,"max mu bits:",max(abs(x).bit_length() for x in ints))

import re,gmpy2,random,decimal
from fractions import Fraction
from fpylll import IntegerMatrix, LLL
def toy(bits=300):
    p = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits)) | 1)
    q = gmpy2.next_prime(gmpy2.mpz(random.getrandbits(bits)) | 1)
    D = 63**14
    n = p*q
    decimal.getcontext().prec = bits+200
    hint = int(D*decimal.Decimal(int(p)).sqrt() + D*decimal.Decimal(int(q)).sqrt())
    S2 = int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))
    lo=(hint*hint-S2-2*hint)//D**2-4; hi=(hint*hint-S2+2*hint)//D**2+4
    t0=(hint*hint-S2+hint)//D**2; E=hi-lo
    print("t true?", int(p+q) >= lo and int(p+q)<=hi, "E bits", int(E).bit_length())
    s0=int(gmpy2.isqrt(gmpy2.mpz(t0)*t0-4*n))
    p0=(t0+s0)//2; q0=int(n)//p0
    print("x0 bits", (int(p)-p0).__abs__().bit_length() if int(max(p,q))-p0 else 0, "err", abs(int(max(p,q))-p0).bit_length(), abs(int(min(p,q))-q0).bit_length())
    X=Y=1<<(int(E).bit_length()+4)
    cols=[1,X,Y,X*Y]
    rows=[[p0*q0-int(n), q0*X, p0*Y, X*Y],[int(n),0,0,0],[0,int(n)*X,0,0],[0,0,int(n)*Y,0]]
    M=IntegerMatrix.from_matrix(rows)
    LLL.reduction(M)
    for i in range(4):
        print("row",i,[int(M[i,j]).bit_length() for j in range(4)])
toy(300)

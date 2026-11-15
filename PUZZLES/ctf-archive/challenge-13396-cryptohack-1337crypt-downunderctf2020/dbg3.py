# LLL quality control on the exact matrix shape
import math, random
from fpylll import IntegerMatrix, LLL
random.seed(7)
def ctl(bitsN, bitsX, m=6, t=9):
    N = (1 << bitsN) + 3**17
    pA = random.randrange(1 << (bitsN//2)) | 1
    X = 1 << bitsX
    # rows: N^(m-i) f^i (i<m), x^i f^m (i<t)
    def f_pow(i):
        c=[1]
        for _ in range(i):
            nc=[0]*(len(c)+1)
            for j,v in enumerate(c):
                nc[j]+=v*pA; nc[j+1]+=v
            c=nc
        return c
    rows=[]
    for i in range(m): rows.append([v*N**(m-i) for v in f_pow(i)])
    fm = f_pow(m)
    for i in range(t): rows.append([0]*i + fm)
    w=15; ncols=15
    M=IntegerMatrix(w,ncols,int_type='mpz')
    for r,row in enumerate(rows):
        for j,c in enumerate(row[:ncols]): M[r,j]=c*(X**j)
    piv=[(m-i)*bitsN + i*bitsX for i in range(m)] + [(m+i)*bitsX for i in range(t)]
    print(f"ctl bitsN={bitsN} X=2^{bitsX}: det^(1/w)=2^{sum(piv)/15:.0f}")
    before=[sum(int(M[r,j])**2 for j in range(ncols)).bit_length() for r in range(3)]
    LLL.reduction(M, delta=0.99)
    after=[sum(int(M[r,j])**2 for j in range(ncols)).bit_length() for r in range(3)]
    print("   first row norms (bits):", before, "->", after, " reduced?", LLL.is_reduced(M))
ctl(1024,180); ctl(1024,90); ctl(256,60); ctl(2674,590)

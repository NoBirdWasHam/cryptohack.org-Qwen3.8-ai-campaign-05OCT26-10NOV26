# determinant of k x k staircase minor: rows m=2..k+1, cols j=0..k-1 (A entries, drop sigma sign)
def bareiss(M):
    n=len(M); M=[r[:] for r in M]; sign=1; prev=1
    for k in range(n-1):
        if M[k][k]==0:
            for i in range(k+1,n):
                if M[i][k]!=0: M[k],M[i]=M[i],M[k]; sign=-sign; break
            else: return 0
        for i in range(k+1,n):
            for j in range(k+1,n):
                M[i][j]=(M[i][j]*M[k][k]-M[i][k]*M[k][j])//prev
        prev=M[k][k]
    return sign*M[n-1][n-1]
for k in (5,10,15,20,25,30,35,40,45,50):
    rows=list(range(2,2+k))
    A=[[rows[i]**j if j<=rows[i]-1 else 0 for j in range(k)] for i in range(k)]
    d=bareiss(A)
    print(k, "det bits:", abs(d).bit_length())

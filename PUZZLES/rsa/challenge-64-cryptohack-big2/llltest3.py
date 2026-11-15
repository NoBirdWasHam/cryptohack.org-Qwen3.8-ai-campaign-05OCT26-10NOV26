import math, time
from gmpy2 import mpz, isqrt

def build(N, e, X, Y, m=3, t=1):
    A = N + 1
    def pmul(a,b):
        o={}
        for (x,y),c in a.items():
            for (x2,y2),d in b.items():
                kk=(x+x2,y+y2); o[kk]=o.get(kk,0)+c*d
        return {k:v for k,v in o.items() if v}
    f={(1,0):mpz(A),(1,1):mpz(1),(0,0):mpz(1)}
    def ppow(poly,n):
        r={(0,0):mpz(1)}
        for _ in range(n): r=pmul(r,poly)
        return r
    shifts=[]
    for k in range(m+1):
        fk=ppow(f,k)
        for i in range(m-k+1):
            g=pmul(fk, {(i,0): mpz(1)})
            g=pmul(g, {(0,0): mpz(e**(m-k))})
            shifts.append(g)
    for j in range(1,t+1):
        for k in range(m//t*j, m+1):
            g=pmul(ppow(f,k), {(0,j): mpz(1)})
            g=pmul(g, {(0,0): mpz(e**(m-k))})
            shifts.append(g)
    monos=set()
    for s in shifts: monos.update(s.keys())
    monos=sorted(monos)
    bounds=lambda ab: (X**ab[0])*(Y**ab[1])
    L=[[shifts[r].get(cc,0)*bounds(cc) for cc in monos] for r in range(len(shifts))]
    return L, monos

def lll(B_in, delta_num=3, delta_den=4, cap=5000, verbose=False):
    """Canonical incremental LLL. B_in: list of mpz lists."""
    n=len(B_in); m=len(B_in[0])
    b=[list(map(mpz,row)) for row in B_in]
    def dot(u,v):
        s=mpz(0)
        for i in range(m): s+=u[i]*v[i]
        return s
    # initialize GS
    bp=[None]*n; lam=[mpz(0)]*n
    bp[0]=b[0][:]; lam[0]=dot(bp[0],bp[0])
    for i in range(1,n):
        bp[i]=b[i][:]
        for j in range(i):
            if lam[j]!=0:
                mu=(dot(bp[i],bp[j])*2+lam[j])//(2*lam[j])
                if mu: bp[i]=[bp[i][k]-mu*bp[j][k] for k in range(m)]
        lam[i]=dot(bp[i],bp[i])
    def swap(i):
        b[i],b[i+1]=b[i+1],b[i]
        bp[i],bp[i+1]=bp[i+1],bp[i]
        lam[i],lam[i+1]=lam[i+1],lam[i]
    i=0; it=0
    while i < n-1:
        it+=1
        if it>cap: print("  lll pass cap",flush=True); break
        # size reduce b[i+1] with respect to b[i]
        if lam[i]!=0:
            mu=(dot(bp[i+1],bp[i])*2+lam[i])//(2*lam[i])
            if mu:
                bp[i+1]=[bp[i+1][c]-mu*bp[i][c] for c in range(m)]
                b[i+1]=[b[i+1][c]-mu*b[i][c] for c in range(m)]
                lam[i+1]=dot(bp[i+1],bp[i+1])
        # LLL condition: lam[i+1] >= (1-1/4) lam[i] = (3/4) lam[i]
        if lam[i+1]*delta_den >= lam[i]*delta_num:
            i+=1
        else:
            swap(i)
            i = i-1 if i>=1 else 0
    return b, it

if __name__=="__main__":
    p=11227048386374621771175649743442169526805922745751610531569607663416378302561807690656370394330458335919244239976798600743588701676542461805061598571009923
    q=7866790440964395011005623971351568677139336343167390105188826934257986271072664643571727955882500173182140478082778193338086048035817634545367411924942763
    N=p*q; phi=(p-1)*(q-1)
    d=186493804207318317888355025415200212277761144340233864189538741099969492009806507
    e=pow(d,-1,phi)
    bl=e.bit_length()-1
    top=(e-(1<<bl))>>(bl-53); ratio=1.0+top/(1<<53); log2e=bl+math.log2(ratio)
    X=mpz(1)<<int(round(log2e*0.26)); Y=mpz(1)<<((N.bit_length()//2)+1)
    print("N bits",N.bit_length(),"e bits",e.bit_length(),"X bits",X.bit_length(),"Y bits",Y.bit_length())
    L,monos=build(N,e,X,Y,3,1)
    print("lattice",len(L),"x",len(monos),"max entry bits",max(x.bit_length() for row in L for x in row))
    t0=time.time()
    Lr,it=lll(L)
    print("LLL iters=%d time %.2fs"%(it,time.time()-t0),flush=True)

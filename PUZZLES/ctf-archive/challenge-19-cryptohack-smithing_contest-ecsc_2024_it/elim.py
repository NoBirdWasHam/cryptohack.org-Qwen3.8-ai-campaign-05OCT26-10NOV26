import json, random
p = 239019556058548081539763731767358519973

def trim(a):
    a=a[:]
    while len(a)>1 and a[-1]==0: a.pop()
    return a
def usub(a,b):
    n=max(len(a),len(b)); return [((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0))%p for i in range(n)]
def uadd(a,b):
    n=max(len(a),len(b)); return [((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%p for i in range(n)]
def umul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,ai in enumerate(a):
        if ai:
            for j,bj in enumerate(b): r[i+j]=(r[i+j]+ai*bj)%p
    return trim(r)
def udiv(a,b):
    assert any(b), 'div0'
    a=trim(a[:]); q=[0]*max(1,len(a)-len(b)+1)
    ib=pow(b[-1],p-2,p)
    while len(a)>=len(b) and any(a):
        c=a[-1]*ib%p; k=len(a)-len(b); q[k]=(q[k]+c)%p
        a=usub(a,[0]*k+[(c*v)%p for v in b]); a=trim(a)
    return q,a
def gcdp(a,b):
    a=trim(a[:]); b=trim(b[:])
    while not (len(b)==1 and b[0]==0):
        a,b=b,trim(udiv(a,b)[1])
    inv=pow(a[-1],p-2,p)
    return trim([(v*inv)%p for v in a])
def upowmod(bb,e,mod):
    r=[1]
    for bit in bin(e)[2:]:
        r=trim(udiv(umul(r,r),mod)[1])
        if bit=='1': r=trim(udiv(umul(r,bb),mod)[1])
    return r
def fp_sqrt(a):
    a%=p
    if a==0: return 0
    if pow(a,(p-1)//2,p)!=1: return None
    q=p-1;s=0
    while q%2==0:q//=2;s+=1
    z=2
    while pow(z,(p-1)//2,p)!=p-1:z+=1
    m,cc,t,r=s,pow(z,q,p),pow(a,q,p),pow(a,(q+1)//2,p)
    while t!=1:
        i=0;t2=t
        while t2!=1: t2=t2*t2%p;i+=1
        b=pow(cc,1<<(m-i-1),p); m,cc,t,r=i,b*b%p,t*b*b%p,r*b%p
    return int(r)
def roots_of(f):
    f=trim(f[:])
    if len(f)==1: return []
    if len(f)==2: return [(-f[0]*pow(f[1],p-2,p))%p]
    while True:
        z=[random.randrange(p),1]
        h=upowmod(z,(p-1)//2,f)
        gg=gcdp(h,[0,p-1])
        dg=len(gg)-1
        if 0<dg<len(f)-1:
            return roots_of(gg)+roots_of(trim(udiv(f,gg)[1]))

def eqs_for(X,Y,e,t0=None):
    """return F1,F2 as dict dn -> coefflist-in-t for general basis a^2=t a+n."""
    x0,x1=X; y0,y1=Y; e0,e1=e
    # (r,i) pairs with poly entries: dicts {(dt,dn):c}
    def add(A,B):
        r=dict(A)
        for k,v in B.items(): r[k]=(r.get(k,0)+v)%p
        return {k:v for k,v in r.items() if v}
    def mul(A,B):
        r={}
        for (i,j),u in A.items():
            for (k,l),v in B.items(): r[(i+k,j+l)]=(r.get((i+k,j+l),0)+u*v)%p
        return {k:v for k,v in r.items() if v}
    C=lambda v:{(0,0):v%p} if v%p else {}
    T={(1,0):1}; N={(0,1):1}
    def emul(P,Q):
        (pr,pi),(qr,qi)=P,Q
        real=add(mul(pr,qr), mul(N, mul(pi,qi)))
        imag=add(add(mul(pr,qi),mul(pi,qr)), mul(T,mul(pi,qi)))
        return (real,imag)
    Xp=(C(x0),C(x1)); Yp=(C(y0),C(y1)); ep=(C(e0),C(e1))
    X2=emul(Xp,Xp); X3=emul(X2,Xp); Y2=emul(Yp,Yp)
    neg=lambda P:({k:(-v)%p for k,v in P.items()} if P else {})
    D=(add(Y2[0],neg(X3[0])), add(Y2[1],neg(X3[1])))
    Nm=add(add(mul(ep[0],ep[0]), mul(T,mul(ep[0],ep[1]))), mul(C(-1),mul(N,mul(ep[1],ep[1]))))
    L=emul(D,(Nm,{}))
    # 11/eps = 11*(e0+t e1 - e1 a)/Nm  -> F = L - 11*(e0+T e1, -e1) = 0
    RHTr=add(mul(C(11),add(ep[0],mul(T,ep[1]))),{})
    RHTi=multiply=None
    RHTi=mul(C(-11),ep[1])
    F1=add(L[0],neg(RHTr)); F2=add(L[1],neg(RHTi))
    out={}
    for k,v in F1.items(): out.setdefault(k[1],{})[k[0]]=v
    out2={}
    for k,v in F2.items(): out2.setdefault(k[1],{})[k[0]]=v
    mx1=max(out)+1; mx2=max(out2)+1
    mdt=max(max(d) for d in list(out.values())+list(out2.values()))+1
    F1L=[ [out.get(i,{}).get(j,0) for j in range(mdt)] for i in range(mx1)]
    F2L=[ [out2.get(i,{}).get(j,0) for j in range(mdt)] for i in range(mx2)]
    return F1L,F2L   # coeffs[t][n-index]? store as list dn-> poly(t) list

def sylv_det(F1L,F2L,t0,D2=2):
    def ev(P): return sum(c*pow(t0,i,p) for i,c in enumerate(P))%p
    f=[ev(P) for P in F1L]; f+= [0]*(D2+1-len(f)); f=f[:D2+1]
    g=[ev(P) for P in F2L]; g+= [0]*(D2+1-len(g)); g=g[:D2+1]
    rows=[]
    for i in range(2): rows.append([ (f[j-i] if 0<=j-i<=2 else 0) for j in range(4)])
    for i in range(2): rows.append([ (g[j-i] if 0<=j-i<=2 else 0) for j in range(4)])
    M=[r[:] for r in rows]; det=1
    for k in range(4):
        piv=None
        for r in range(k,4):
            if M[r][k]%p: piv=r;break
        if piv is None: return 0
        if piv!=k: M[k],M[piv]=M[piv],M[k]; det=(-det)%p
        det=det*M[k][k]%p
        inv=pow(M[k][k],p-2,p)
        for r in range(k+1,4):
            c=M[r][k]*inv%p
            if c:
                for j in range(k,4): M[r][j]=(M[r][j]-c*M[k][j])%p
    return det

def interpolate(xs,ys,D):
    n=D+1
    Mx=[[pow(xs[i],j,p) for j in range(n)] for i in range(n)]
    b=ys[:n][:]
    for k in range(n):
        piv=None
        for r in range(k,n):
            if Mx[r][k]: piv=r;break
        if piv is None: raise RuntimeError('singular')
        Mx[k],Mx[piv]=Mx[piv],Mx[k]; b[k],b[piv]=b[piv],b[k]
        inv=pow(Mx[k][k],p-2,p)
        for r in range(k+1,n):
            c=Mx[r][k]*inv%p
            if c:
                for j in range(k,n): Mx[r][j]=(Mx[r][j]-c*Mx[k][j])%p
                b[r]=(b[r]-c*b[k])%p
    coef=[0]*n
    for k in reversed(range(n)):
        s=b[k]
        for j in range(k+1,n): s=(s-Mx[k][j]*coef[j])%p
        coef[k]=s*pow(Mx[k][k],p-2,p)%p
    while len(coef)>1 and coef[-1]==0: coef.pop()
    return coef

def solve_modulus(X,Y,e,name,verbose=True):
    F1L,F2L=eqs_for(X,Y,e)
    D=14
    xs=list(range(1,D+2)); ys=[sylv_det(F1L,F2L,t0) for t0 in xs]
    if not any(ys):
        if verbose: print(name,'resultant identically zero (dep)')
        return []
    R=interpolate(xs,ys,D)
    if verbose: print(name,'R deg',len(R)-1)
    xp=upowmod([0,1],p,R)
    g1=gcdp(R, trim(usub(xp,[1])))
    if len(g1)-1==0:
        if verbose: print(name,'no t-roots')
        return []
    ts=roots_of(g1)
    sols=[]
    for t0 in ts:
        def inn(F):
            mx=len(F)-1; out=[0]*(mx+1)
            for dn,P in enumerate(F):
                out[dn]=(out[dn]+sum(c*pow(t0,i,p) for i,c in enumerate(P)))%p
            return trim(out)
        gg=gcdp(inn(F1L),inn(F2L))
        if len(gg)==2:
            n0=(-gg[0]*pow(gg[1],p-2,p))%p
            sols.append((t0,n0))
    return sols

# ---------------- self-test of pipeline ----------------
def f2m(x,y,t,n):
    a,b=x; c,d=y
    return ((a*c+n*b*d)%p, (a*d+b*c+t*b*d)%p)
def f2inv(x,t,n):
    a,b=x
    Nm=(a*a+t*a*b-n*b*b)%p
    iv=pow(Nm,p-2,p)
    return ((a+t*b)%p*iv%p, (-b)%p*iv%p)
random.seed(7)
def rnd_nr():
    while True:
        z=random.randrange(2,10**6)
        if pow((z*z+1)%p,(p-1)//2,p)==p-1: return z, -1
tT,nT = 12345, -(3)  # some model (irreducibility irrelevant for test)
def rnd_pt(t,n):
    while True:
        x0=random.randrange(p); x1=random.randrange(p)
        rhs=f2m(f2m((x0,x1),(x0,x1),t,n),(x0,x1),t,n)
        c2x=(11*0)  # not used
        # pick y random too, we don't need on-curve for pipeline test? We DO: need Y2 - X3 = 11/eps.
        # construct: pick random x,y0,y1; set eps := 11 / (Y2 - X3)
        X=(x0,x1); Y=(random.randrange(p),random.randrange(p))
        X3=f2m(f2m(X,X,t,n),X,t,n); Y2=f2m(Y,Y,t,n)
        d=( (Y2[0]-X3[0])%p, (Y2[1]-X3[1])%p )
        if d==(0,0): continue
        try:
            di=f2inv(d,t,n)
        except Exception:
            continue
        e=( 11*di[0]%p, 11*di[1]%p )
        return X,Y,e
Xs,Ys,es = rnd_pt(tT,nT)
sols=solve_modulus(Xs,Ys,es,'SELFTEST')
print('expected (t,n) =',(tT,nT),'solutions:',sols)

# ---------------- challenge data ----------------
x0,x1 = 100774561144590475569157120930767342387, 218728496724280042701446122970647661523
y0,y1 = 115367896606755692925113233629944781384, 211093354487559124632805793736258741445
A = 50853858759521010453592688907791911225
B = 156893423039651253351316307339945502422
for Xc in ((x1,x0),(x0,x1)):
    for Yc in ((y1,y0),(y0,y1)):
        for e in ((B,A),(A,B)):
            sols=solve_modulus(Xc,Yc,e,f'X={Xc is (x1,x0)} Y={Yc is (y1,y0)} e={e is (B,A)}',verbose=False)
            if sols: print('CHALLENGE SOLUTION Xc=%s Yc=%s e=(B,A)?%s'%(Xc is (x1,x0),Yc is (y1,y0),e is (B,A)), sols)
print('done')

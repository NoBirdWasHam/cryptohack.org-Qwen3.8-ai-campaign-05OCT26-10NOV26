import math, time
from gmpy2 import mpz, isqrt
from Crypto.Util.number import long_to_bytes, inverse

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

def lll(B_in, delta_num=3, delta_den=4, cap=20000):
    n=len(B_in); m=len(B_in[0])
    b=[list(map(mpz,row)) for row in B_in]
    def dot(u,v):
        s=mpz(0)
        for i in range(m): s+=u[i]*v[i]
        return s
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
        if it>cap: break
        if lam[i]!=0:
            mu=(dot(bp[i+1],bp[i])*2+lam[i])//(2*lam[i])
            if mu:
                bp[i+1]=[bp[i+1][c]-mu*bp[i][c] for c in range(m)]
                b[i+1]=[b[i+1][c]-mu*b[i][c] for c in range(m)]
                lam[i+1]=dot(bp[i+1],bp[i+1])
        if lam[i+1]*delta_den >= lam[i]*delta_num:
            i+=1
        else:
            swap(i)
            i = i-1 if i>=1 else 0
    return b, it

def attack(N, e, c, X, Y, m=3, t=1, tag=""):
    A=N+1
    L,monos=build(N,e,X,Y,m,t)
    Lr,it=lll(L)
    # reconstruct
    pols=[]
    for row in Lr:
        t={}
        for cc,ab in enumerate(monos):
            val=row[cc]
            if val==0: continue
            bnd=(X**ab[0])*(Y**ab[1])
            if val % bnd: 
                print("  [%s] reconstruct: not divisible!"%tag,flush=True)
                break
            coef=val//bnd
            if coef: t[ab]=t.get(ab,0)+coef
        else:
            if t: pols.append(t)
    print("  [%s] lattice %dx%d, LLL iters %d, reconstructed %d polys"%(tag,len(L),len(monos),it,len(pols)),flush=True)
    for idx,p in enumerate(pols[:6]):
        print("    P%d: %d terms, maxdeg %d, maxcoef bits %d"%(idx,len(p),max(a+b for a,b in p),max(cc.bit_length() for cc in p.values())))
    # sympy groebner
    from sympy import symbols, Poly as SPoly, ZZ as SZZ, groebner
    sx, sy = symbols('x y')
    spols=[SPoly({ab:int(cc) for ab,cc in p.items()}, sx, sy, domain=SZZ) for p in pols if any(cc for cc in p.values())]
    G=groebner(spols, sx, sy, order='lex')
    print("  [%s] groebner basis: %d polys"%(tag,len(G)),flush=True)
    # univariate root extraction (sympy Poly: check .gens())
    def uroots(p, var):
        out=[]
        try:
            if p.gens!=(var,):
                return out
            for r,mult in p.roots().items():
                if r.is_rational and r.is_integer: out.append(int(r))
        except Exception: pass
        return out
    uy=[]; ux=[]; biv=[]
    for gp in G:
        if gp.is_zero: continue
        if gp.gens==(sy,): uy.append(gp)
        elif gp.gens==(sx,): ux.append(gp)
        else: biv.append(gp)
    print("  [%s] G: univ-y %d, univ-x %d, bivar %d"%(tag,len(uy),len(ux),len(biv)),flush=True)
    for gp in G:
        if not gp.is_zero:
            print("    Gpoly gens=%s total_deg=%d nterms=%d"%(gp.gens,gp.total_degree(),len(gp.monoms())),flush=True)
            print("      expr:", str(gp.as_expr())[:400], flush=True)
    ys=[]; xs=[]
    for gp in uy: ys+=uroots(gp, sy)
    for gp in ux: xs+=uroots(gp, sx)
    # also: for each G, substitute one var and factor
    pairs=set()
    for yv in set(ys):
        for gp in G:
            if gp.is_zero: continue
            sub=gp.subs(sy,yv)
            if sub.is_zero: 
                pairs.add((0,yv)); continue
            for xv in uroots(sub, sx): pairs.add((xv,yv))
    for xv in set(xs):
        for gp in G:
            if gp.is_zero: continue
            sub=gp.subs(sx,xv)
            if sub.is_zero:
                pairs.add((xv,0)); continue
            for yv in uroots(sub, sy): pairs.add((xv,yv))
    # bivariate Groebner poly: try to factor / find integer points via its structure
    # (for Boneh-Durfee the bivar poly is typically linear in x: x = R(y) + c)
    for gp in biv:
        try:
            # treat as poly in x over ZZ[y]
            p_x = SPoly(gp.as_expr(), sx, sy, domain=SZZ)
            # collect terms linear in x
            c1 = p_x.coeff_monomial(sx)   # coefficient of x (poly in y)
            c0 = p_x.coeff_monomial(1)
            if c1 is not None and c1 != 0:
                # x = -c0 / c1 (rational in y) -> for integer y roots of c1, x = -c0/c1
                c1roots = uroots(c1, sy) if c1.gens==(sy,) else []
                for yv in (set(c1roots) | set(ys)):
                    try:
                        den=c1.subs(sy,yv); num=c0.subs(sy,yv)
                        if den!=0 and num % den == 0:
                            pairs.add((-(int(num))//int(den), yv))
                    except Exception: pass
        except Exception: pass
    print("  [%s] candidate pairs: %d"%(tag,len(pairs)),flush=True)
    for xv,yv in pairs:
        z=xv*(A+yv)+1
        if z % e: continue
        try: k=pow(xv,-1,e)
        except Exception: continue
        s=(N+1+k)%e
        phi=N-s+1
        dsc=s*s-4*N
        if dsc<0 or isqrt(dsc)**2!=dsc or (s-isqrt(dsc))%2: continue
        r=isqrt(dsc); p=(s-r)//2; q=(s+r)//2
        if p*q!=N: continue
        print("  [%s] FOUND x0=%d y0=%d | p bits %d q bits %d"%(tag,xv,yv,p.bit_length(),q.bit_length()),flush=True)
        mdec=pow(c, inverse(e,(p-1)*(q-1)), N)
        flag=long_to_bytes(mdec)
        print("  [%s] FLAG: %s"%(tag,flag),flush=True)
        return flag
    return None

def X_from_e(e, delta=0.26):
    bl=e.bit_length()-1
    if bl>53:
        top=(e-(1<<bl))>>(bl-53); ratio=1.0+top/(1<<53); log2e=bl+math.log2(ratio)
    else:
        log2e=math.log2(float(e))
    return mpz(1)<<int(round(log2e*delta))

if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="selftest":
        p=11227048386374621771175649743442169526805922745751610531569607663416378302561807690656370394330458335919244239976798600743588701676542461805061598571009923
        q=7866790440964395011005623971351568677139336343167390105188826934257986271072664643571727955882500173182140478082778193338086048035817634545367411924942763
        N=p*q; phi=(p-1)*(q-1)
        d=186493804207318317888355025415200212277761144340233864189538741099969492009806507
        e=pow(d,-1,phi)
        X=X_from_e(e,0.26); Y=mpz(1)<<((N.bit_length()//2)+1)
        flag=attack(N,e,12345,X,Y,3,1,"selftest")
        print("SELFTEST:", "OK" if flag else "FAIL")
        sys.exit(0)
    v={}
    for line in open("big2_output.txt"):
        if '=' in line:
            a,b=line.split('=',1); v[a.strip()]=b.strip()
    N=int(v['N'],16); e=int(v['e'],16); c=int(v['c'],16)
    print("N bits:",N.bit_length(),"| e bits:",e.bit_length(),flush=True)
    X=X_from_e(e,0.26); Y=mpz(1)<<((N.bit_length()//2)+1)
    print("X bits:",X.bit_length(),"Y bits:",Y.bit_length(),flush=True)
    flag=attack(N,e,c,X,Y,3,1,"big2")
    if flag: open("flag.txt","wb").write(flag)

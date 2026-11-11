"""CSIDH-512 key exchange (challenge 219). SW-form walk over F_p, Galbraith
Thm 25.1.6 Velu (validated in challenge-214). Forward e>0: kernel E[l](F_p).
Backward e<0: anti-rational line {Q: pi(Q)=-Q} over F_p2. Shared = walk(E0,a+b).
Track image of 2-torsion (0,0) through xmaps -> Montgomery A at the end.
Verify by AES-decrypting the given iv/ct."""
import hashlib, random
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ells = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,
        101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,
        191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,
        281,283,293,307,311,313,317,331,337,347,349,353,359,367,373,587]
P = 4
for l in ells: P *= l
P -= 1
IV = bytes.fromhex('daf6cd181775664b099609789fb564c9')
CT = bytes.fromhex('3dd92e255c8e677f4a92226d09f56e2b2f567052ffd4f6f60200018454a83affc2e694c2bf2ad27da38f7f49b6e89928')
a_priv = [-1,-2,-3,-3,-2,-3,-3,0,2,-1,2,-1,-2,-3,1,2,1,2,0,0,1,-1,0,2,-1,0,0,0,1,-1,-3,1,-1,-3,-3,2,2,1,-1,-1,1,0,1,1,1,-2,2,2,-2,-2,0,0,2,0,-1,-3,-2,-2,0,-1,-3,-1,-2,-3,-2,2,1,1,-2,0,1,-1,-3,2]
b_priv = [-1,-1,0,1,2,0,2,-1,-3,1,0,-2,-2,2,-1,-2,-3,-3,-3,2,2,2,-2,-1,1,-2,0,-3,-1,1,-1,-1,-3,-1,-2,1,-1,-2,-3,1,0,-1,1,2,2,0,0,-1,-2,-2,1,-1,1,1,1,1,0,0,0,-3,-2,-1,2,0,-3,-2,1,1,-2,-1,-1,2,0,1]
assert len(a_priv) == len(b_priv) == len(ells)

rng = random.Random(1337)
inv = lambda t: pow(t, P-2, P)

# ---------- F_p2: (u,v) = u + v*i, i^2 = -1 ----------
def a2(x,y): return ((x[0]+y[0])%P, (x[1]+y[1])%P)
def s2(x,y): return ((x[0]-y[0])%P, (x[1]-y[1])%P)
def m2(x,y): return ((x[0]*y[0]-x[1]*y[1])%P, (x[0]*y[1]+x[1]*y[0])%P)
def inv2(x):
    n = pow(x[0]*x[0]+x[1]*x[1], P-2, P)
    return (x[0]*n % P, (-x[1])*n % P)
def d2(x,c): return (x[0]*c%P, x[1]*c%P)
def conj2(x): return (x[0], (-x[1])%P)
def pow2(x,e):
    r=(1,0); b=x
    while e:
        if e&1: r=m2(r,b)
        b=m2(b,b); e>>=1
    return r
def ts2(n):
    if n==(0,0): return (0,0)
    assert pow2(n,(P*P-1)//2)==(1,0), "not a square in F_p2"
    q=P*P-1; s=0
    while q%2==0: q//=2; s+=1
    z=(0,1); k=0
    while pow2(z,(P*P-1)//2)==(1,0):
        k+=1; z=(k%P,(k+1)%P)
    m=s; c=pow2(z,q); t=pow2(n,q); r=pow2(n,(q+1)//2)
    while t!=(1,0):
        i=0; tt=t
        while tt!=(1,0): tt=pow2(tt,2); i+=1
        b=pow2(c,1<<(m-i-1)); m=i; c=pow2(b,2); t=m2(t,c); r=m2(r,b)
    return r

# ---------- EC y^2 = x^3 + a x + b, a,b in F_p, points over F_p2 ----------
def onE(a,b,x,y):
    return m2(y,y)==a2(m2(x,m2(x,x)),a2(m2((a,0),x),(b,0)))
def padd(a,b,P1,P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1,y1=P1; x2,y2=P2
    if x1==x2:
        if y1==y2:
            if y2==(0,0): return None
            lam=m2(a2(d2(m2(x1,x1),3),(a,0)), inv2(d2(y1,2)))
            x3=s2(m2(lam,lam), d2(x1,2)); y3=s2(m2(lam,s2(x1,x3)),y1)
            return (x3,y3)
        return None
    lam=m2(s2(y2,y1), inv2(s2(x2,x1)))
    x3=s2(s2(m2(lam,lam),x1),x2); y3=s2(m2(lam,s2(x1,x3)),y1)
    return (x3,y3)
def pmul(a,b,k,Pt):
    R=None; Q=Pt
    while k:
        if k&1: R=padd(a,b,R,Q)
        Q=padd(a,b,Q,Q); k>>=1
    return R
def negp(Pt):
    if Pt is None: return None
    return (Pt[0], ((-Pt[1][0])%P, (-Pt[1][1])%P))
def frob(Pt):
    if Pt is None: return None
    return (conj2(Pt[0]), conj2(Pt[1]))

def sqrt_p(v):
    if v==0: return 0
    if pow(v,(P-1)//2,P)!=1: return None
    return pow(v,(P+1)//4,P)   # P = 3 mod 4
def randFp2(a,b):
    while True:
        x=(rng.randrange(P), rng.randrange(P))
        rhs=a2(m2(x,m2(x,x)),a2(m2((a,0),x),(b,0)))
        if pow2(rhs,(P*P-1)//2)!=(1,0): continue
        y=ts2(rhs)
        if onE(a,b,x,y): return (x,y)
def randFp(a,b):
    while True:
        x=rng.randrange(P)
        y=sqrt_p((x*x*x+a*x+b)%P)
        if y is not None: return ((x,0),(y,0))

# ---------- Velu (Thm 25.1.6), kernel odd & Galois-stable ----------
def velu(a,b,K):
    reps=[]; seen=set()
    for (x,y) in K:
        key=(x[0],x[1],y[0],y[1]); nk=(x[0],x[1],(-y[0])%P,(-y[1])%P)
        if key in seen or nk in seen: continue
        seen.add(key); reps.append((x,y))
    tS=(0,0); sS=(0,0)
    for (x,y) in reps:
        t=d2(a2(d2(m2(x,x),3),(a,0)),2)
        u=d2(m2(y,y),4)
        tS=a2(tS,t); sS=a2(sS,a2(u,m2(x,t)))
    assert tS[1]==0 and sS[1]==0, "kernel not Galois-stable"
    ap=(a-5*tS[0])%P; bp=(b-7*sS[0])%P
    def xmap(x):
        r=x
        for (xq,yq) in reps:
            d=inv2(s2(x,xq))
            t=d2(a2(d2(m2(xq,xq),3),(a,0)),2)
            u=d2(m2(yq,yq),4)
            r=a2(r, a2(m2(u,m2(d,d)), m2(t,d)))
        return r
    return ap, bp, xmap

def kernel_pts(a,b,Q,l):
    K=[]; R=Q
    for k in range(1,l):
        K.append(R); R=padd(a,b,R,Q)
    return K
def fwd_kernel(a,b,l):
    while True:
        Q=pmul(a,b,(P+1)//l, randFp(a,b))
        if Q is not None: break
    return kernel_pts(a,b,Q,l)
def bwd_kernel(a,b,l):
    while True:
        R=randFp2(a,b)
        S=padd(a,b,R,negp(frob(R)))
        Q=pmul(a,b,(P+1)//l,S)
        if Q is not None and frob(Q)==negp(Q): break
    return kernel_pts(a,b,Q,l)

def walk(a,b,priv,track=None):
    """walk E(SW a,b) by exponent vector; track = x-coord (F_p2) of 2-torsion image."""
    for l,e in zip(ells,priv):
        for _ in range(abs(e)):
            K = fwd_kernel(a,b,l) if e>0 else bwd_kernel(a,b,l)
            a,b,xm = velu(a,b,K)
            if track is not None: track = xm(track)
    return a,b,track

def mont_A(a,v):
    """y^2 = x^3 + 3v x^2 + (3v^2+a) x (root shifted to 0) -> A = 3v/u2, u2 = 3v^2+a."""
    c = (3*v*v + a) % P
    s = sqrt_p(c)
    out=[]
    if s is not None:
        out.append((3*v*inv(s))%P)
    return out

def decrypt(A):
    key = hashlib.sha256(str(A).encode()).digest()
    try:
        pt = unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(CT), 16)
        if pt.startswith(b"crypto"): return pt.decode()
    except Exception: pass
    return None

def jinv(a,b):
    d = (4*pow(a,3,P)+27*b*b)%P
    return 6912*pow(a,3,P)*pow(d,P-2,P)%P if d else None
def ylift(a,b,x):
    rhs=a2(m2(x,m2(x,x)),a2(m2((a,0),x),(b,0)))
    if x[1]==0 and rhs[1]==0:
        y=sqrt_p(rhs[0])
        if y is not None: return (y,0)
    return ts2(rhs)

if __name__ == "__main__":
    import sys
    a0=1; b0=0                           # E0: y^2 = x^3 + x  (Sage [1,0])
    v0=0                                 # 2-torsion (0,0)
    mode = sys.argv[1] if len(sys.argv)>1 else "test"
    if mode=="test":
        a,b = a0,b0
        K=fwd_kernel(a,b,3); a1,b1,xm=velu(a,b,K)
        K=bwd_kernel(a1,b1,3); a2_,b2_,_=velu(a1,b1,K)
        print("roundtrip +1,-1 l=3 (j):", jinv(a2_,b2_)==jinv(a0,b0), flush=True)
        K=bwd_kernel(a0,b0,3); ax,bx,_=velu(a0,b0,K)
        K=fwd_kernel(ax,bx,3); ay,by,_=velu(ax,bx,K)
        print("roundtrip -1,+1 l=3 (j):", jinv(ay,by)==jinv(a0,b0), flush=True)
        a=a0;b=b0
        K=fwd_kernel(a,b,3); a,b,_=velu(a,b,K)
        K=fwd_kernel(a,b,5); a,b,_=velu(a,b,K)
        r1=(a,b)
        a=a0;b=b0
        K=fwd_kernel(a,b,5); a,b,_=velu(a,b,K)
        K=fwd_kernel(a,b,3); a,b,_=velu(a,b,K)
        print("commute 3,5 (j):", jinv(*r1)==jinv(a,b), flush=True)
        # xmap kills a kernel point (image -> infinity) and is a homomorphism on x-coords
        K=fwd_kernel(a0,b0,3); a1,b1,xm=velu(a0,b0,K)
        P1=randFp(a0,b0); P2=randFp(a0,b0)
        lhs=xm(padd(a0,b0,P1,P2)[0])
        y1=ylift(a1,b1,xm(P1[0])); y2=ylift(a1,b1,xm(P2[0]))
        ok=False
        for e1 in (1,-1):
            for e2 in (1,-1):
                Q1=(xm(P1[0]), d2(y1,e1)); Q2=(xm(P2[0]), d2(y2,e2))
                if padd(a1,b1,Q1,Q2)[0]==lhs: ok=True
        print("xmap homomorphism:", ok, flush=True)
    elif mode=="full":
        EA = walk(a0,b0,a_priv, track=(0,0))   # track image of 2-torsion (0,0)
        EB = walk(a0,b0,b_priv, track=(0,0))
        print("EA:", EA[0], EA[1], flush=True)
        print("EB:", EB[0], EB[1], flush=True)
        sh1 = walk(EA[0],EA[1],b_priv, track=EA[2])
        sh2 = walk(EB[0],EB[1],a_priv, track=EB[2])
        print("shared j match:", jinv(sh1[0],sh1[1])==jinv(sh2[0],sh2[1]), flush=True)
        a,b,v = sh1
        cands = mont_A(a, v[0]) if v is not None else []
        for A in set(cands + [(-c)%P for c in cands]):
            r = decrypt(A)
            if r: print("FLAG:", r, flush=True); break
        else:
            print("no decrypt; A cands were:", cands, flush=True)

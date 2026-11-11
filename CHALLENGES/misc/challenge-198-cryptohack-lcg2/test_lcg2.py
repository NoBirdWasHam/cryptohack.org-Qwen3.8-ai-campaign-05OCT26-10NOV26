import random, sympy as sp
a=0x1337deadbeef; b=0xb; N=48; K=8; L=N-K; mod=2**N
def top(x): return x>>(N-K)
def f(x): return (a*x+b)%mod
def finv(x): return ((x-b)*pow(a,-1,mod))%mod

def recover_first(h, a, b, m=8):
    # h[i]=top(x_{i+1}) for i=0..m-1 ; find x_1 (first state).
    # e_i = low40(x_i).  a e_i - e_{i+1} + 2^48 k_i = C_i ; C_i=(h[i+1]-a h[i])*2^L - b
    C=[(h[i+1]-a*h[i])*(2**L)-b for i in range(m-1)]
    # e_i = a^{i-1} e_1 - E_i + 2^48 K_i ; E_1=0, E_i=a E_{i-1}+C_{i-1}
    E=[0]*(m+1)
    for i in range(2,m+1):
        E[i]=a*E[i-1]+C[i-2]
    # M (m x m): cols [e_1, K_2..K_m]; row i: M[i,0]=a^{i-1}; M[i,i-1]=2^N (i>=2)
    M=sp.zeros(m,m)
    for i in range(m):
        M[i,0]=pow(a,i)
        if i>=1:
            M[i,i-1]=2**N
    Ev=sp.Matrix([E[i+1] for i in range(m)])     # E_1..E_m
    center=sp.Matrix([2**(L-1)]*m)
    t=Ev+center
    # CVP: find w s.t. M w close to t
    Bred=(M.T.lll()).T
    w=(Bred.T*Bred).inv()*(Bred.T*t)
    w0=[int(round(float(w[i]))) for i in range(m)]
    best=None
    import itertools
    for dc in itertools.product(range(-6,7),repeat=m):
        ww=[w0[i]+dc[i] for i in range(m)]
        p=Bred*sp.Matrix(ww)
        evec=p-Ev
        if all(0<=evec[i]<2**L for i in range(m)):
            val=sum((evec[i]-2**(L-1))**2 for i in range(m))
            if best is None or val<best[0]:
                best=(val,evec)
    if best is None: return None
    e1=int(best[1][0])
    x1=(h[0]*(2**L)+e1)%mod
    # verify
    x=x1
    for i in range(m):
        if top(x)!=h[i]: return None
        x=f(x)
    return x1

def simulate():
    # build a full 48-byte get_a_challenge stream from random seeds, return (pt,key,iv)
    def block(seed):
        x=seed; out=[]
        for _ in range(16):
            x=f(x); out.append(x)
        return out
    seed_v=random.getrandbits(48)
    v=block(seed_v)              # greeting block; we consumed v1..v8, see v9..v16
    w=block(random.getrandbits(48))
    k=block(random.getrandbits(48))
    i=block(random.getrandbits(48))
    pt=[v[j] for j in range(8,16)]+[w[j] for j in range(0,8)]
    key=[w[j] for j in range(8,16)]+[k[j] for j in range(0,8)]
    iv=[k[j] for j in range(8,16)]+[i[j] for j in range(0,8)]
    return (bytes(top(s) for s in pt), bytes(top(s) for s in key), bytes(top(s) for s in iv)), key

ok=0
for trial in range(30):
    (ptb,keyb,ivb), truekey=simulate()
    # key[0:8] from ptb[8:16] (w1..w8) forward 8
    w1=recover_first([ptb[8+i] for i in range(8)],a,b)
    assert w1 is not None, "w1 fail"
    x=w1
    for _ in range(8): x=f(x)   # w9
    key0=bytes(top(f(x) if False else x) for _ in [0])  # placeholder
    # key[0:8] = top(w9..w16): states w9..w16 = advance w1 by 8..15
    key0=bytes([top(f**0(0)) for _ in [0]])  # skip
    xs=w1
    key0=bytearray()
    for s in range(8):
        xs=f(xs)
        key0.append(top(xs))
    # key[8:16] from ivb[0:8] (k9..k16) backward 8
    k9=recover_first([ivb[0+i] for i in range(8)],a,b)
    assert k9 is not None, "k9 fail"
    key8=bytearray()
    xs=k9
    for s in range(8):
        xs=finv(xs)
        key8.insert(0, top(xs))
    reckey=bytes(key0)+bytes(key8)
    if reckey!=truekey:
        print(f"FAIL {trial}\n rec={reckey.hex()}\n true={truekey.hex()}"); break
    ok+=1
print(f"recovered key {ok}/30")

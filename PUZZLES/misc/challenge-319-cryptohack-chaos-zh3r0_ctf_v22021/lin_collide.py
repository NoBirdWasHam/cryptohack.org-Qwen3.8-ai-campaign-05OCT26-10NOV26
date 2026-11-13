# Collision for chaos hash via linearized family:
# restrict each hi-half h to {M-2^k, M} (M=0xffff) so product lo*(M-hi) = lo<<k (GF2-linear).
# Then per config C=(hX,hY,hZ,hU): v(lo) = Lin_C . lo (+ base_C).
# Collision between config A (lo l) and B (lo l'): [LinA LinB] (l,l') = baseA + baseB over GF(2).
import random, json

M32 = 0xffffffff
def rotl(v,b): return ((v<<b)|(v>>(32-b))) & M32
def rotr(v,b): return ((v>>b)|(v<<(32-b))) & M32

def vfull(X,Y,Z,U):
    M=0xffff; o=[0,0,0,0]
    o[0]^=(X&0xffff)*(M-(Y>>16)); o[1]^=(Y&0xffff)*(M-(Z>>16))
    o[2]^=(Z&0xffff)*(M-(U>>16)); o[3]^=(U&0xffff)*(M-(X>>16))
    o[1]^=rotr(X,2); o[2]^=rotl(X,3)
    o[2]^=rotr(Y,3); o[3]^=rotl(Y,4)
    o[0]^=rotl(Z,1);  o[3]^=rotr(Z,4)
    o[0]^=rotr(U,1);  o[1]^=rotl(U,2)
    return [t & M32 for t in o]

def build(hX,hY,hZ,hU):
    X,Y,Z,U = hX<<16, hY<<16, hZ<<16, hU<<16
    base = vfull(X,Y,Z,U)
    cols=[]
    for vi in range(4):
        for bit in range(16):
            vals=[X,Y,Z,U]; vals[vi]^=(1<<bit)
            cols.append([a^b for a,b in zip(vfull(*vals),base)])
    return cols, base  # cols: 64 vectors of 4 words

def rowmat(cols):  # 64 columns(4 words) -> list of 128 rows as 64-bit ints
    return [ sum(((col[r>>5]>>(r&31))&1)<<c for c,col in enumerate(cols)) for r in range(128) ]

def solve(rows, rhs_bits):  # 128 unknowns (rows 128-bit) ; rhs_bits list of 128 bits; returns 128-bit sol or None
    n=128; NU=128
    aug=[rows[i] | (rhs_bits[i]<<NU) for i in range(n)]
    where=[-1]*NU
    r_i=0
    for col in range(NU-1,-1,-1):
        sel=None
        for i in range(r_i,n):
            if (aug[i]>>col)&1: sel=i; break
        if sel is None: continue
        aug[r_i],aug[sel]=aug[sel],aug[r_i]
        for i in range(n):
            if i!=r_i and ((aug[i]>>col)&1): aug[i]^=aug[r_i]
        where[col]=r_i; r_i+=1
    mask=(1<<NU)-1
    for i in range(n):
        if (aug[i]&mask)==0 and (aug[i]>>NU)&1: return None
    sol=0
    for col in range(NU):
        if where[col]!=-1: sol |= ((aug[where[col]]>>NU)&1)<<col
    return sol

M=0xffff
his=[M]+[M-(1<<k) for k in range(16)]
random.seed(4)
best=None; tried=0
for attempt in range(400000):
    A=(random.choice(his),random.choice(his),random.choice(his),random.choice(his))
    B=list(A); B[random.randrange(4)]=random.choice(his)
    B=tuple(B)
    if A==B: continue
    tried+=1
    cA,bA=build(*A); cB,bB=build(*B)
    rows=[ra|(rb<<64) for ra,rb in zip(rowmat(cA),rowmat(cB))]
    rhs=[ (bA[w]^bB[w]) for w in range(4) ]
    bits=[(rhs[w]>>b)&1 for w in range(4) for b in range(32)]
    sol=solve(rows,bits)
    if sol is None: continue
    loA,loB=sol&0xffffffff,(sol>>64)&0xffffffff
    XA,YA,ZA,UA=(A[0]<<16)|(loA&0xffff),(A[1]<<16)|((loA>>16)&0xffff),\
                 (A[2]<<16)|((loA>>32)&0xffff),(A[3]<<16)|((loA>>48)&0xffff)
    XB,YB,ZB,UB=(B[0]<<16)|(loB&0xffff),(B[1]<<16)|((loB>>16)&0xffff),\
                 (B[2]<<16)|((loB>>32)&0xffff),(B[3]<<16)|((loB>>48)&0xffff)
    if (XA,YA,ZA,UA)==(XB,YB,ZB,UB): continue
    if vfull(XA,YA,ZA,UA)==vfull(XB,YB,ZB,UB):
        best=dict(A=map(hex,A).__str__(),cfgA=A,cfgB=B,X=XA,Y=YA,Z=ZA,U=UA,Xp=XB,Yp=YB,Zp=ZB,Up=UB)
        print("FOUND after",tried,"config pairs")
        print(json.dumps({k:(hex(v) if isinstance(v,int) else v) for k,v in best.items() if k not in('A',)}))
        break
print("tried pairs:",tried)

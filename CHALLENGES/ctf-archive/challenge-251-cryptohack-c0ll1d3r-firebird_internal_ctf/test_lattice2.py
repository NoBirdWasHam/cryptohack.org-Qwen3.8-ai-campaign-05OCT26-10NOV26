import time, random, math
from gmpy2 import is_prime
from fpylll import IntegerMatrix, LLL, BKZ, CVP

PREF = b'SECUREHASH_'; TARGET = b'pleasegivemetheflag'
P = int.from_bytes(PREF,'big'); M = int.from_bytes(PREF+TARGET,'big')

def make_p():
    while True:
        p = random.getrandbits(256)
        if is_prime(p): return p

def build(p, L):
    N = p-1
    S = (256**L-1)//255
    T = (M - P*256**L - 109*S) % N
    A = IntegerMatrix(L, L)
    A[0,0] = N
    for i in range(1,L):
        A[i,0] = -(pow(256,i,N)); A[i,i] = 1
    return A, [T]+[0]*(L-1), N

def check(d, N, L):
    if not all(-12<=di<=13 for di in d): return False
    X=bytes(109+d[L-1-j] for j in range(L))
    m=int.from_bytes(PREF+X,'big')
    return (m%N==M%N) and m!=M

def try_babai(p,L,bs=None,tries=1):
    A,target,N = build(p,L)
    t0=time.time(); LLL.reduction(A)
    if bs: BKZ.reduction(A, BKZ.Param(bs))
    t1=time.time()
    best=None
    for t in range(tries):
        if t==0:
            co=[0]*L
        else:
            co=[random.randint(-3,3) for _ in range(L)]
        r=[sum(co[i]*int(A[i,j]) for i in range(L)) for j in range(L)]
        tgt=[target[j]+r[j] for j in range(L)]
        v=list(CVP.babai(A,tgt))
        d=[target[j]-(v[j]-r[j]) for j in range(L)]
        md=max(abs(x) for x in d)
        if best is None or md<best[0]: best=(md,d)
        if check(d,N,L):
            print("babai L=%d bs=%s try=%d: red %.1fs ok=True maxd=%d" % (L,bs,t,t1-t0,md))
            return True
    print("babai L=%d bs=%s: red %.1fs ok=False bestmaxd=%d (tries=%d)" % (L,bs,t1-t0,best[0],tries))
    return False

def try_kannan(p,L,bs=40):
    A,target,N = build(p,L)
    c = 13
    B = IntegerMatrix(L+1, L+1)
    for i in range(L):
        for j in range(L): B[i,j]=A[i,j]
        B[i,L]=0
    for j in range(L): B[L,j]=target[j]
    B[L,L]=c
    t0=time.time(); LLL.reduction(B); BKZ.reduction(B, BKZ.Param(bs))
    t1=time.time()
    for i in range(L+1):
        row=[int(B[i,j]) for j in range(L+1)]
        if abs(row[L])==c:
            d=[x if row[L]==c else -x for x in row[:L]]
            if check(d,N,L):
                print("kannan L=%d bs=%d: red %.1fs FOUND" % (L,bs,t1-t0)); return True
    print("kannan L=%d bs=%d: red %.1fs notfound" % (L,bs,t1-t0)); return False

p = make_p()
print("p bits", p.bit_length())
for L in (58,60,62,64):
    if try_babai(p,L,bs=40,tries=300): break
for L in (58,60,62,64):
    if try_babai(p,L,bs=60,tries=300): break

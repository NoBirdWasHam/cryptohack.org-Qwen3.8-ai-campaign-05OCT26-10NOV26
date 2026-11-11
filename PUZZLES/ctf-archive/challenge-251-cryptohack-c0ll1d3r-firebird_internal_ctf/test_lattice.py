import time, random, math
from gmpy2 import is_prime, invert
from fpylll import IntegerMatrix, LLL, BKZ, CVP

PREF = b'SECUREHASH_'; TARGET = b'pleasegivemetheflag'
P = int.from_bytes(PREF,'big'); M = int.from_bytes(PREF+TARGET,'big')

def make_p():
    while True:
        p = random.getrandbits(256)
        if is_prime(p): return p

def solve_L(p, L, do_bkz=True, bs=40):
    N = p-1
    S = (256**L-1)//255
    T = (M - P*256**L - 109*S) % N
    A = IntegerMatrix(L, L)
    A[0,0] = N
    for i in range(1,L):
        A[i,0] = -(pow(256,i,N)); A[i,i] = 1
    t0=time.time(); LLL.reduction(A); t1=time.time()
    if do_bkz:
        BKZ(bs)(A)
    t2=time.time()
    target=[T]+[0]*(L-1)
    try:
        v=list(CVP.closest_vector(A,target,method="fast")); meth="enum"
    except Exception as e:
        v=list(CVP.babai(A,target)); meth="babai"
    t3=time.time()
    d=[target[i]-v[i] for i in range(L)]
    ok=all(-12<=di<=13 for di in d)
    if ok:
        X=bytes(109+d[L-1-j] for j in range(L))
        m=int.from_bytes(PREF+X,'big')
        ok = (m%N==M%N) and m!=M
    print("L=%d bkz=%s: lll %.1fs bkz %.1fs cvp(%s) %.1fs -> %s" % (L,do_bkz,t1-t0,t2-t1,meth,t3-t2,ok))
    return ok if ok else None

p = make_p()
print("p bits", p.bit_length())
for L in (58,60,62):
    r = solve_L(p,L,do_bkz=False)
    if r: break
for L in (58,60,62):
    r = solve_L(p,L,do_bkz=True,bs=30)
    if r: break

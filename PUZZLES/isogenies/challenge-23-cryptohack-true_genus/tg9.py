# tg9: per-row Frob eigenvalue u on E[9] (G^p = [u]G, u mod 9), via E(Fp6)=(p^3+1)^2.
# Also q8(Delta) vs x mod 4/8. p=1289 testbed.
from collections import defaultdict
import random
p = 1289
rows = []
for ln in open("small3.out"):
    if ln.startswith("ROW"):
        _, x, a4, a6 = ln.split()
        rows.append((int(x) % 36, int(a4) % p, int(a6) % p))

def red(c):
    c = [v % p for v in c]
    while len(c) > 3:
        top = c.pop()
        c[-1] = (c[-1] + top) % p
        c[-2] = (c[-2] + top) % p
    return c
def mul3(a, b):
    r = [0]*5
    for i in range(3):
        for j in range(3): r[i+j] = (r[i+j] + a[i]*b[j]) % p
    return red(r)
def add3(a, b): return [(a[i]+b[i]) % p for i in range(3)]
def sub3(a, b): return [(a[i]-b[i]) % p for i in range(3)]
def neg3(a): return [(-v) % p for v in a]
def pow3(a, e):
    r = [1,0,0]
    while e:
        if e & 1: r = mul3(r, a)
        a = mul3(a, a); e >>= 1
    return r
def inv3(a): return pow3(a, p**3 - 2)

XI = next(v for v in (2,3,5,6,7,10,11) if pow(v, (p-1)//2, p) == p-1)
def mul6(x, y):
    a1, b1 = x; a2, b2 = y
    aa = add3(mul3(a1,a2), [(XI*v)%p for v in mul3(b1,b2)])
    bb = sub3(mul3(add3(a1,b1), add3(a2,b2)), add3(mul3(a1,a2), mul3(b1,b2)))
    return (aa, bb)
def add6(x, y): return (add3(x[0],y[0]), add3(x[1],y[1]))
def sub6(x, y): return (sub3(x[0],y[0]), sub3(x[1],y[1]))
def neg6(x): return (neg3(x[0]), neg3(x[1]))
def inv6(x):
    den = add3(mul3(x[0],x[0]), [(-XI*v)%p for v in mul3(x[1],x[1])])
    di = inv3(den)
    return (mul3(x[0],di), neg3(mul3(x[1],di)))
def pow6(x, e):
    r = ([1,0,0],[0,0,0])
    while e:
        if e & 1: r = mul6(r, x)
        x = mul6(x, x); e >>= 1
    return r
ONE6 = ([1,0,0],[0,0,0]); ZERO6 = ([0,0,0],[0,0,0])
def is0(x): return x == ZERO6
TP = pow3([0,1,0], p)
def frob6(x):
    def ev(c):
        r = [0,0,0]; ti = [1,0,0]
        for ai in c:
            r = [(r[k] + ai*ti[k]) % p for k in range(3)]
            ti = mul3(ti, TP)
        return r
    return (ev(x[0]), neg3(ev(x[1])))
C6 = lambda v: ([v % p, 0, 0], [0,0,0])
def ts6(v):
    q = p**6 - 1; S = 0
    while q % 2 == 0: q //= 2; S += 1
    z = None; t0 = 2
    while z is None:
        c = pow6(C6(t0), q)
        if pow6(c, 2**(S-1)) != ONE6: z = c
        t0 += 1
    m_ = S; c_ = z; t_ = pow6(v, q); r_ = pow6(v, (q+1)//2)
    while t_ != ONE6:
        i_ = 0; tt = t_
        while tt != ONE6:
            tt = mul6(tt,tt); i_ += 1
            if i_ >= m_: return None
        b_ = pow6(c_, 2**(m_-i_-1)); m_ = i_; c_ = mul6(b_,b_); t_ = mul6(t_,c_); r_ = mul6(r_,b_)
    return r_
def padd(P, Q, a4, a6):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if P == Q:
        if is0(y1): return None
        l = mul6(add6(mul6(C6(3), mul6(x1,x1)), C6(a4)), inv6(add6(mul6(C6(2), y1), ZERO6)))
    else:
        dx = sub6(x1, x2); dy = sub6(y1, y2)
        if is0(dx): return None
        l = mul6(dy, inv6(dx))
    x3 = sub6(sub6(mul6(l,l), x1), x2)
    y3 = sub6(mul6(l, sub6(x1, x3)), y1)
    return (x3, y3)
def pmul(k, P, a4, a6):
    R = None
    while k:
        if k & 1: R = padd(R, P, a4, a6)
        P = padd(P, P, a4, a6); k >>= 1
    return R

rng = random.Random(7)
M = (p**3 + 1)**2 // 9
results = {}
for x, a4, a6 in rows:
    done_ = False
    for attempt in range(60):
        xel = ([rng.randrange(p) for _ in range(3)], [rng.randrange(p) for _ in range(3)])
        fel = add6(add6(mul6(mul6(xel,xel),xel), mul6(C6(a4), xel)), C6(a6))
        if pow6(fel, (p**6 - 1)//2) != ONE6: continue
        yel = ts6(fel)
        if yel is None: continue
        P = (xel, yel)
        G = pmul(M, P, a4, a6)
        if G is None or pmul(3, G, a4, a6) is None: continue
        Gp = (frob6(G[0]), frob6(G[1]))
        for uu in (1,2,4,5,7,8):
            if pmul(uu, G, a4, a6) == Gp:
                results[x] = uu; done_ = True; break
        if done_: break
    if not done_: print("MISS", x)

for x in sorted(results):
    print(f"x={x:3d}  u={results[x]}  u%3={results[x]%3}")
tbl3 = defaultdict(set); tbl9 = defaultdict(set)
for x in results:
    tbl3[x % 3].add(results[x]); tbl9[x % 9].add(results[x])
print("u by x mod 3:", {k: sorted(v) for k, v in tbl3.items()})
print("u by x mod 9:", {k: sorted(v) for k, v in tbl9.items()})
tbl4 = defaultdict(set); tbl8 = defaultdict(set)
for x, a4, a6 in rows:
    Dv = (-16*(4*a4**3 + 27*a6**2)) % p
    e8 = pow(Dv, (p-1)//8, p)
    tbl4[x % 4].add(e8); tbl8[x % 8].add(e8)
print("q8(D) by x mod 4:", {k: sorted(v) for k, v in tbl4.items()})
print("q8(D) by x mod 8:", {k: sorted(v) for k, v in tbl8.items()})
print("done XI=", XI)

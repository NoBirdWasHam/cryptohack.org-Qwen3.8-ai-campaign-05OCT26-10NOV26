# MITM claw attack: recover Alice's 2^35 walk from EA alone.
# Forward: binary tree depth F=23 over a mod 2^23 (kernels 2^(34-i)(P2+aQ2)+b*2^34 Q2).
# Backward: 2-isogeny tree depth B=12 from EA (3 roots of x^3+Ax+B via CZ over F_p2).
# Match j; then brute top 12 bits by extending forward; verify j(E35)==j(EA).
import sys, time, random
sys.path.insert(0, ".")
import fp2
from fp2 import *

E0 = ((1, 0), (0, 0))
P2 = ((1761758151759977040301838, 1956194174015565770794336), (203179590296749797202321, 2069089015584979134622338))
Q2 = ((525239361975369850140518, 2307879706216488835068177), (733730165545948547648966, 1834477572646982833868802))
P3 = ((1542032609308508307064948, 2162781291023757368295120), (904285233345649302734471, 1130418491160933565948899))
Q3 = ((1867216057142335172490873, 365294178628988623980343), (1860108401614981479394873, 2141125983272329025279178))
EA = ((63223462935813026254900, 2336060373130772918448023), (525917254309082638166498, 202739861418983960259548))
sB = 495832856
jEA = jinv(*EA)
jkey = lambda j: j[0] | (j[1] << 82)

F = 23; B = 12
EA_ = 35; EB_ = 29
assert F + B == EA_

def walk2_full(a, extra_pts, ea=35):
    # full 2^ea walk with secret a, tracking P2,Q2 and extra points
    E = ((1, 0), (0, 0)); p2, q2 = P2, Q2; pts = list(extra_pts)
    for i in range(ea):
        u = emul(eadd(p2, emul(q2, a, E[0]), E[0]), 2**(ea-1-i), E[0])
        E2, xm, ym = velu2(E, u)
        mp = lambda Pt: None if Pt is None else (xm(Pt[0]), ym(Pt[0], Pt[1]))
        p2, q2 = mp(p2), mp(q2); pts = [mp(x) for x in pts]
        E = E2
    return E, pts

def chain3(E, H, eb=29):
    # kill cyclic <H>, H of order 3^eb
    for k in range(eb):
        Q0 = emul(H, 3**(eb-1-k), E[0])
        E, mp = velu_odd(E, Q0)
        H = mp(H)
    return E

# ---------- forward DFS depth F ----------
def forward_table():
    tbl = {}
    t0 = time.time()
    # state: (E, p2, q2, w=2^34 q2 [ord2], a); per node: u = 2^(34-i)(p2 + a q2)
    def dfs(i, E, p2, q2, w, a):
        if i == F:
            tbl.setdefault(jkey(jinv(*E)), []).append(a)
            return
        r = eadd(p2, emul(q2, a, E[0]), E[0])
        u = emul(r, 2**(EA_-1-i), E[0])   # order 2
        for b in (0, 1):
            T = u if b == 0 else eadd(u, w, E[0])
            if T is None: continue
            E2, xm, ym = velu2(E, T)
            def mp(Pt):
                if Pt is None: return None
                return (xm(Pt[0]), ym(Pt[0], Pt[1]))
            dfs(i+1, E2, mp(p2), mp(q2), mp(w), a | (b << i))
    dfs(0, E0, P2, Q2, emul(Q2, 2**(EA_-1), (1,0)), 0)
    print("forward leaves:", sum(len(v) for v in tbl.values()), "time", round(time.time()-t0,1), flush=True)
    return tbl

# ---------- root finding of cubic over F_p2 ----------
def pmul(f, g, m):
    r = [(0,0)]*(len(f)+len(g)-1)
    for i, fi in enumerate(f):
        if fi == (0,0): continue
        for j, gj in enumerate(g):
            if gj == (0,0): continue
            r[i+j] = fadd(r[i+j], fmul(fi, gj))
    for i in range(len(r)-1, 2, -1):
        if r[i] == (0,0): continue
        c = r[i]
        r[i] = (0,0)
        # x^3 = -A x - B  (m = [B, A, 0, 1]): x^i -> -c*A x^{i-2} - c*B x^{i-3}
        r[i-2] = fsub(r[i-2], fmul(c, m[1]))
        r[i-3] = fsub(r[i-3], fmul(c, m[0]))
    return r[:3]
def ppow(base, e, m):
    r = [(1,0),(0,0),(0,0)]
    while e:
        if e & 1: r = pmul(r, base, m)
        base = pmul(base, base, m); e >>= 1
    return r
def pgcd(f, g):
    def trim(v):
        v = v[:]
        while len(v) > 1 and v[-1] == (0,0): v.pop()
        return v
    f = trim(f); g = trim(g)
    while any(c != (0,0) for c in g):
        f = pmod(f, g)
        f, g = trim(g), trim(f)
    return f
def pmod(f, g):
    f = f[:]
    dg = len(g)-1
    for i in range(len(f)-1, dg-1, -1):
        if f[i] == (0,0): continue
        k = fdiv(f[i], g[dg])
        for j in range(dg+1):
            f[i-dg+j] = fsub(f[i-dg+j], fmul(k, g[j]))
    return f[:dg]
def quad_roots(b2, c2):
    # roots of x^2 + b2 x + c2
    D = fsub(fsq(b2), fmul((4,0), c2))
    s = fsqrt(D)
    r1 = fdiv(fadd(s, fneg(b2)), (2,0)); r2 = fdiv(fsub(fneg(b2), s), (2,0))
    return r1, r2
def fsqrt(z):
    if z == (0,0): return (0,0)
    # q = p^2, q-1 = 2^35 * 3^29 * (p-1)/... just do generic TS
    q1 = p*p - 1
    s_ = 0; d_ = q1
    while d_ % 2 == 0: d_ //= 2; s_ += 1
    rnd = random.Random(999)
    while True:
        zz = (rnd.randrange(p), rnd.randrange(p))
        if zz == (0,0): continue
        if fpow(zz, (p*p-1)//2) == fneg((1,0)):
            nn = zz; break
    x = fpow(z, (d_+1)//2); b = fpow(z, d_); g = fpow(nn, d_); r_ = s_
    while b != (1,0):
        t = b; m_ = 0
        while t != (1,0):
            t = fsq(t); m_ += 1
            if m_ >= r_: raise RuntimeError("sqrt fail")
        gs = fpow(g, 1 << (r_-m_-1))
        x = fmul(x, gs); g = fmul(gs, gs); b = fmul(b, g); r_ = m_
    return x
def is_sq(z):
    return fpow(z, (p*p-1)//2) == (1,0)
def roots3(A, Bc):
    # F_p2-rational roots of x^3 + A x + Bc (1 or 3 of them)
    m = [Bc, A, (0,0), (1,0)]
    f = [Bc, A, (0,0), (1,0)]
    rnd = random.Random(12345)
    r0 = None
    for _ in range(80):
        al = (rnd.randrange(p), rnd.randrange(p))
        base = [al, (1,0),(0,0),(0,0)]
        h = ppow(base, (p*p-1)//2, m)
        h = [fsub(h[0], (1,0)), h[1], h[2]]
        g = pgcd(f, h)
        d = len(g)-1
        if d == 1:
            r0 = fdiv(fneg(g[0]), g[1]); break
        if d == 2:
            b2, c2 = g[1], g[0]
            if g[2] != (1,0):
                n = finv(g[2]); b2 = fmul(b2, n); c2 = fmul(c2, n)
            r0 = b2  # leftover linear factor x - b2
            break
    if r0 is None: raise RuntimeError("no root")
    out = [r0]
    D = fsub(fsub((0,0), fmul((3,0), fsq(r0))), fmul((4,0), A))  # -3 r0^2 - 4A
    if is_sq(D):
        s = fsqrt(D)
        r1 = fdiv(fadd(s, fneg(r0)), (2,0)); r2 = fdiv(fsub(fneg(r0), s), (2,0))
        out += [r1, r2]
    return out

# ---------- backward DFS depth B from EA ----------
def backward(tbl):
    matches = []
    t0 = time.time()
    def dfs(i, E):
        if i == B:
            k = jkey(jinv(*E))
            if k in tbl:
                matches.append((E, list(tbl[k])))
                print("MATCH at", round(time.time()-t0,1), flush=True)
            return
        A, Bc = E
        for v in roots3(A, Bc):
            E2, xm, ym = velu2(E, (v, (0,0)))
            dfs(i+1, E2)
        if i == 2: print("bwd depth3 done", round(time.time()-t0,1), flush=True)
    dfs(0, EA)
    print("backward done, matches:", len(matches), "time", round(time.time()-t0,1), flush=True)
    return matches

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fwd"
    if mode == "fwd":
        tbl = forward_table()
        import pickle
        pickle.dump(tbl, open("fwd_tbl.pkl", "wb"))
        print("saved fwd_tbl.pkl")
    elif mode == "bwd":
        import pickle
        tbl = pickle.load(open("fwd_tbl.pkl", "rb"))
        ms = backward(tbl)
        import json
        json.dump([[list(map(list, m[0])), m[1]] for m in ms], open("matches.json", "w"))
        print("saved matches.json")

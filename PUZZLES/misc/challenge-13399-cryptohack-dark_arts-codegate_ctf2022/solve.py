# Dark Arts (CODEGATE 2022 archive) full solver. Local: python solve.py local ; Live: solve.py live
import sys, os, socket, hashlib, random, time, cmath, math
import numpy as np
from math import log
T2 = int(sys.argv[2]) if len(sys.argv) > 2 else 2500
HOST, PORT = "archive.cryptohack.org", 35802

# ---------- Challenge 2 GLRT tables ----------
_z = cmath.exp(2j*math.pi/35)
def _g(r): return (r % 5 + r % 7) % 5
Mlist = list(range(96, 161))
LP = {}
for m in Mlist:
    v = [0.0]*5
    for r in range(35):
        s = sum(((0.5+0.5*_z**k)**m)*_z**(-k*r) for k in range(35)).real/35
        v[_g(r)] += max(s, 0.0)
    tot = sum(v); LP[m] = [log(5*max(a, 1e-12)/tot) for a in v]
def c2_stat(counts):
    return max(sum(counts[a]*LP[m][a] for a in range(5)) for m in Mlist)
C2_THRESH = -1.0

def digits5(h):
    d = []
    for _ in range(64):
        d.append(h % 5); h //= 5
    return d
def h_chain(x):
    h = hashlib.sha256(str(x).encode()).digest()
    out = []
    for _ in range(16):
        out.append(int.from_bytes(h, "big"))
        h = hashlib.sha256(h).digest()
    return out

# ---------- C3 quadratic linearization over GF(5) (RUN#4-verified, c3_linearize_check.py) ----------
# b=1 queries have S=sum k_j h_j mod5 in {1,3} => S^2+S=2 mod5: one LINEAR equation in the
# 2144 monomials {k_j, k_j^2, k_j k_l (j<l)}. RREF, read k_j off the linear coordinates.
IDX = [[0]*64 for _ in range(64)]
cur = 64
for j in range(64):
    for l in range(j, 64):
        IDX[j][l] = cur; cur += 1
NV = cur  # 2144
INV = np.array([0,1,3,2,4], dtype=np.int16)  # inverse mod5: 2->3, 3->2
_JS = np.array([IDX[j][j] for j in range(64)])
_JC, _LC = np.triu_indices(64, 1)
_IDX_C = np.array([IDX[j][l] for j, l in zip(_JC, _LC)])

def gf5_rref(A):
    # NOTE: must run in int16 — uint8 silently wraps (256 == 1 mod 5, RUN#4 bug class).
    A = A.astype(np.int16)
    m, n = A.shape; r = 0; piv = []
    for c in range(n):
        if r >= m: break
        nz = np.nonzero(A[r:, c])[0]
        if nz.size == 0: continue
        p = r + int(nz[0])
        if p != r: A[[r, p]] = A[[p, r]]
        A[r] = (A[r] * INV[A[r, c]]) % 5
        rows = np.nonzero(A[:, c])[0]
        rows = rows[rows != r]
        if rows.size:
            A[rows] = (A[rows] - np.outer(A[rows, c], A[r])) % 5
        piv.append(c); r += 1
    return piv, r, A

def c3_solve_linearized(askmany, N0=6000, step=6000, maxN=30000):
    # askmany(xs) -> list of b values. Guards: digits 0..3 + parity re-verify on ALL queries.
    rows = []; rhs = []; all_hds = []; all_bs = []
    N = 0; t0 = time.time()
    while N < maxN:
        N_new = N + (N0 if N == 0 else step)
        new_xs = list(range(N+1, N_new+1))
        for x, b in zip(new_xs, askmany(new_xs)):
            hd = np.array(digits5(int.from_bytes(hashlib.sha256(str(x).encode()).digest(), "big")), dtype=np.int16)
            all_hds.append(hd); all_bs.append(int(b))
            if int(b) != 1: continue
            row = np.zeros(NV, dtype=np.int16)
            row[:64] = hd % 5
            row[_JS] = (hd*hd) % 5
            row[_IDX_C] = (2*hd[_JC]*hd[_LC]) % 5
            rows.append(row); rhs.append(2)
        N = N_new
        Aug = np.concatenate([np.array(rows, dtype=np.int16),
                              np.array(rhs, dtype=np.int16)[:, None]], axis=1)
        piv, _, Aug = gf5_rref(Aug)
        rank_coef = sum(1 for c in piv if c < NV)
        print(f"  c3 lin: N={N} b1eq={len(rows)} rank={rank_coef}/{NV} consistent={NV not in piv} ({time.time()-t0:.1f}s)", flush=True)
        if NV not in piv and rank_coef == NV:
            sol = np.zeros(NV, dtype=np.int16)
            for i, c in enumerate(piv):
                if c < NV: sol[c] = Aug[i, -1]
            k = [int(v) for v in sol[:64]]
            if not all(0 <= v <= 3 for v in k):
                print("  c3 guard: digit outside 0..3 — reject", flush=True); return None
            if all((sum(k[i]*int(hd[i]) for i in range(64)) % 5) % 2 == b for hd, b in zip(all_hds, all_bs)):
                return k
            print("  c3 guard: parity re-verify failed — reject", flush=True); return None
    print(f"  c3: rank never reached {NV} after {maxN} queries", flush=True)
    return None

# ---------- lattices ----------
from fpylll import IntegerMatrix, LLL, BKZ
def reduce_(M, block):
    LLL.reduction(M)
    BKZ.reduction(M, BKZ.Param(block_size=block, timeout=100, strategies=BKZ.DEFAULT_STRATEGY))

def solve_c3(D, bs, block=40, wk=2):
    T = len(D); n = 64 + T + 1
    M = IntegerMatrix(64 + T + 1, n)
    for i in range(64):
        M[i, i] = wk
        for t in range(T): M[i, 64+t] = D[t][i]
    for t in range(T): M[64+t, 64+t] = 10
    r = 64 + T; c = int(2.0*(T**0.5)) + 10
    for t in range(T): M[r, 64+t] = bs[t]
    M[r, n-1] = c
    reduce_(M, block)
    cands = []
    for i in range(M.nrows):
        if abs(M[i, n-1]) == c:
            s = 1 if M[i, n-1] > 0 else -1
            k = [(-s)*int(M[i, j]) for j in range(64)]
            if all(0 <= v <= 3 for v in k): cands.append(k)
    return cands

def solve_c4(p, q, H, fs):
    T = len(fs); n = T + 1
    M = IntegerMatrix(T + 17, n)
    for i in range(16):
        for t in range(T): M[i, t] = H[t][i]
    for t in range(T): M[16+t, t] = p
    tgt = [fs[t] - q//2 for t in range(T)]
    c = int((T**0.5) * (q//2)) // 3
    r = T + 16
    for t in range(T): M[r, t] = tgt[t]
    M[r, T] = c
    # RUN#5: LLL ONLY. BKZ.reduction HARD-CRASHES (silent exit-127, no traceback) fpylll
    # 0.6.4 on this host for this input class — reproduced dependent AND squared, with
    # AND without numpy; T=48 survived (RUN#1 luck). Kannan gap at T=80 (~2^40) dwarfs
    # LLL's approximation factor anyway: LLL alone gave 1 hit + exact key 3/3 (c4_triage.py).
    LLL.reduction(M)
    allKp = []
    for i in range(M.nrows):
        row = [int(M[i, j]) for j in range(n)]
        if any(row) and abs(row[T]) == c:
            s = 1 if row[T] > 0 else -1
            allKp.append([tgt[t] - s*row[t] for t in range(T)])
    return allKp, tgt

def solve_lin_mod_p(A, b, p):
    # generalized gaussian elimination over Z/pZ (p possibly composite), backtrack on non-units
    import itertools
    k = len(A[0])
    Ac = [row[:] for row in A]; bc = b[:]
    r = 0; diag = []
    for c in range(k):
        while True:
            nz = [i for i in range(r, len(Ac)) if Ac[i][c] % p]
            if not nz: return None
            Ac[r], Ac[nz[0]] = Ac[nz[0]], Ac[r]; bc[r], bc[nz[0]] = bc[nz[0]], bc[r]
            a = Ac[r][c] % p
            g = math.gcd(a, p)
            if g == 1: break
            # reduce with extended gcd against another row to lower gcd
            improved = False
            for i in range(r+1, len(Ac)):
                if Ac[i][c] % p and math.gcd(Ac[i][c] % p, p) < g:
                    Ac[r], Ac[i] = Ac[i], Ac[r]; bc[r], bc[i] = bc[i], bc[r]; improved = True; break
            if improved: continue
            if g > 1:
                return None
        inv = pow(Ac[r][c], -1, p)
        Ac[r] = [v*inv % p for v in Ac[r]]; bc[r] = bc[r]*inv % p
        for i in range(len(Ac)):
            if i != r and Ac[i][c] % p:
                f = Ac[i][c]
                Ac[i] = [(Ac[i][j]-f*Ac[r][j]) % p for j in range(k)]
                bc[i] = (bc[i]-f*bc[r]) % p
        r += 1
    return bc[:k]

# ---------- attacks given oracles ----------
def c1_decide(ask):
    for i in range(24):
        o = ask(1 << i)
        if o != 0: return 1
    return 0
def c2_decide(askmany, tmax=6000, hi=10.0, lo=-10.0):
    counts = [0]*5; got = 0
    while got < tmax:
        n = min(500, tmax - got)
        for o in askmany(n): counts[o] += 1
        got += n
        s = c2_stat(counts)
        if s >= hi: return 0
        if s <= lo: return 1
    return 0 if c2_stat(counts) > -1 else 1
def c3_attack(ask, N=6000):
    # RUN#5: quadratic linearization over GF(5) (RUN#4 verified 5/5; replaces dead box_solve).
    return c3_solve_linearized(lambda xs: [ask(x) for x in xs], N0=N)
def c4_attack(ask, p, q):
    T = 80
    xs = list(range(1, T+1))
    fs = [ask(x) for x in xs]
    H = [h_chain(x) for x in xs]
    def chk(k):
        for t in range(T):
            prod = sum(k[i]*H[t][i] for i in range(16))
            if (prod % p + prod % q) % p != fs[t]: return False
        return True
    allKp, tgt = solve_c4(p, q, H, fs)
    for Kp in allKp:
        for _ in range(30):
            idx = random.sample(range(T), 16)
            sol = solve_lin_mod_p([[H[t][i] for i in range(16)] for t in idx], [Kp[t] for t in idx], p)
            if sol and chk(sol): return sol
    return None

# ---------- local mode ----------
def run_local(iters=1):
    code = open("chal.py").read().split("\nchallenge_generator_1()")[0].replace("signal.alarm(300)", "pass")
    g = {"__name__": "chal_local"}
    g.update(dict(os=os, hashlib=hashlib, signal=__import__("types").SimpleNamespace(alarm=lambda n: None)))
    exec(code, g)
    for it in range(iters):
        t0 = time.time()
        for _ in range(64):
            G1 = g["Generator1"]()
            m = c1_decide(G1.calc)
            if m != G1.mode: print("C1 FAIL round", _, flush=True); return False
        print(f"local C1 ok ({time.time()-t0:.1f}s)", flush=True)
        t0 = time.time()
        fails = 0
        for _ in range(64):
            G2 = g["Generator2"]()
            seen = set()
            def askmany(n, G2=G2):
                out = []
                while len(out) < n:
                    x = random.randrange(1 << 100)
                    if x in seen: continue
                    seen.add(x); out.append(G2.calc(x))
                return out
            m = c2_decide(askmany)
            if m != G2.mode: fails += 1
        print(f"local C2 done, fails={fails}/64 ({time.time()-t0:.1f}s)", flush=True)
        t0 = time.time()
        G3 = g["Generator3"]()
        k3 = c3_attack(G3.func_gen)
        print("local C3:", k3 == G3.key, f"({time.time()-t0:.1f}s)", flush=True)
        if k3 != G3.key: return False
        t0 = time.time()
        G4 = g["Generator4"]()
        k4 = c4_attack(G4.func_gen, G4.p, G4.q)
        print("local C4:", k4 == G4.key, f"({time.time()-t0:.1f}s)", flush=True)
        return k4 == G4.key

# ---------- live mode ----------
def run_live():
    s = socket.create_connection((HOST, PORT), timeout=60)
    f = s.makefile("rwb")
    def rd():
        line = f.readline()
        if not line: raise EOFError("conn closed: "+repr(line))
        return line.decode().strip()
    def wr(x): f.write((str(x)+"\n").encode()); f.flush()
    try:
        print("banner:", rd(), flush=True)
        # challenge 1: 64 rounds
        for rnum in range(64):
            buf = b"".join((b"0\n"+str(1 << i).encode()+b"\n") for i in range(24))
            f.write(buf); f.flush()
            outs = [int(rd()) for _ in range(24)]
            mode = 0 if all(o == 0 for o in outs) else 1
            wr(1); wr(mode)
        print("C1 done", flush=True)
        # challenge 2: read "Challenge 2"? no banner inside loops; banners printed before each generator
        # note: "Challenge 2" banner appears as first unread line now:
        print("banner:", rd(), flush=True)
        B = 500
        seen = set()
        for rnum in range(64):
            def askmany(n):
                out = []
                while len(out) < n:
                    xs = []
                    for _ in range(n - len(out)):
                        x = random.randrange(1 << 100)
                        if x in seen: continue
                        seen.add(x); xs.append(x)
                    buf = b"".join((b"0\n" + str(x).encode() + b"\n") for x in xs)
                    f.write(buf); f.flush()
                    for _ in range(len(xs)): out.append(int(rd()))
                return out
            mode = c2_decide(askmany)
            wr(1); wr(mode)
        print("C2 done", flush=True)
        print("banner:", rd(), flush=True)
        # challenge 3: quadratic linearization over GF(5) (RUN#4-verified)
        def askmany3(xs):
            buf = b"".join((b"0\n"+str(x).encode()+b"\n") for x in xs)
            f.write(buf); f.flush()
            return [int(rd()) for _ in xs]
        k3 = c3_solve_linearized(askmany3)
        if not k3: print("C3 FAILED", flush=True); return None
        wr(1)
        for d in k3: wr(d)
        print("C3 key sent", flush=True)
        print("banner:", rd(), flush=True)
        p = int(rd()); q = int(rd())
        print("C4 banner+p+q read", flush=True)
        T4 = 80
        buf = b"".join((b"0\n"+str(x).encode()+b"\n") for x in range(1, T4+1))
        f.write(buf); f.flush()
        fs = [int(rd()) for _ in range(T4)]
        H = [h_chain(x) for x in range(1, T4+1)]
        k4 = None
        allKp = []
        try:
            allKp, tgt = solve_c4(p, q, H, fs)
        except Exception as e:
            print("c4 err", e, flush=True)
        for Kp in allKp:
            for _ in range(40):
                idx = random.sample(range(T4), 16)
                sol = solve_lin_mod_p([[H[t][i] for i in range(16)] for t in idx], [Kp[t] for t in idx], p)
                if sol and all((sum(sol[i]*H[t][i] for i in range(16)) % p + sum(sol[i]*H[t][i] for i in range(16)) % q) % p == fs[t] for t in range(T4)):
                    k4 = sol; break
            if k4: break
        if not k4: print("C4 FAILED", flush=True); return None
        wr(1)
        for d in k4: wr(d)
        flag = rd()
        print("FLAG:", flag, flush=True)
        open("flag_dark_arts-codegate_ctf2022.txt", "w").write(flag)
        return flag
    finally:
        s.close()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    if mode == "local":
        run_local()
    else:
        run_live()

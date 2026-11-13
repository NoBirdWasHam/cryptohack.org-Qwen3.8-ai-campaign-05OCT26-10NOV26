# C4 BKZ crash triage: param V = lll80 | bkz20 | bkz40plain | bkz40to | bkz40rand | bkz40T48
import os, hashlib, types, time, sys, random
import numpy as np
code = open("chal.py").read().split("\nchallenge_generator_1()")[0].replace("signal.alarm(300)", "pass")
g = {"__name__": "chal_local"}
g.update(dict(os=os, hashlib=hashlib, signal=types.SimpleNamespace(alarm=lambda n: None)))
exec(code, g)
from fpylll import IntegerMatrix, LLL, BKZ
import solve  # reuse verified solve_lin_mod_p

def build(T):
    G4 = g["Generator4"]()
    p, q = G4.p, G4.q
    n = T + 1
    xs = list(range(1, T+1))
    fs = [G4.func_gen(x) for x in xs]
    H = [solve.h_chain(x) for x in xs]
    M = IntegerMatrix(T + 17, n)
    for i in range(16):
        for t in range(T): M[i, t] = H[t][i]
    for t in range(T): M[16+t, t] = p
    tgt = [fs[t] - q//2 for t in range(T)]
    c = int((T**0.5) * (q//2)) // 3
    r = T + 16
    for t in range(T): M[r, t] = tgt[t]
    M[r, T] = c
    return M, n, c, tgt, G4, H, fs

def square(M, n):
    LLL.reduction(M)
    rows = [[int(M[i, j]) for j in range(n)] for i in range(M.nrows)]
    nz = [row for row in rows if any(row)]
    M2 = IntegerMatrix(len(nz), n)
    for i, row in enumerate(nz):
        for j, v in enumerate(row): M2[i, j] = v
    print(f"squared: {len(nz)}x{n}", flush=True)
    return M2

def verify(M2, n, c, tgt, G4, H, fs, T):
    found = None; hits = 0
    for i in range(M2.nrows):
        if abs(int(M2[i, n-1])) == c:
            hits += 1
            s = 1 if int(M2[i, n-1]) > 0 else -1
            Kp = [tgt[t] - s*int(M2[i, t]) for t in range(T)]
            for _ in range(30):
                idx = random.sample(range(T), 16)
                sol = solve.solve_lin_mod_p([[H[t][i] for i in range(16)] for t in idx], [Kp[t] for t in idx], G4.p)
                if sol and all((sum(sol[i2]*H[t][i2] for i2 in range(16)) % G4.p + sum(sol[i2]*H[t][i2] for i2 in range(16)) % G4.q) % G4.p == fs[t] for t in range(T)):
                    found = sol; break
            if found: break
    print("hits:", hits, "keymatch:", found == list(G4.key), flush=True)

V = sys.argv[1]
if V == "bkz40rand":
    rng = np.random.default_rng(7)
    M = IntegerMatrix(81, 81)
    for i in range(81):
        for j in range(81): M[i, j] = int(rng.integers(1, 1 << 250))
    print("random 81x81 250-bit", flush=True)
    LLL.reduction(M); print("LLL done", flush=True)
    BKZ.reduction(M, BKZ.Param(block_size=40, timeout=100, strategies=BKZ.DEFAULT_STRATEGY))
    print("BKZ40RAND OK", flush=True)
elif V == "bkz40T48":
    M, n, c, tgt, G4, H, fs = build(48)
    M2 = square(M, n)
    t0 = time.time()
    BKZ.reduction(M2, BKZ.Param(block_size=40, timeout=100, strategies=BKZ.DEFAULT_STRATEGY))
    print("BKZ40T48 reduction OK", time.time()-t0, flush=True)
    verify(M2, n, c, tgt, G4, H, fs, 48)
else:
    M, n, c, tgt, G4, H, fs = build(80)
    M2 = square(M, n)
    t0 = time.time()
    if V == "lll80":
        pass  # M2 already LLL-reduced from square()
    elif V == "bkz20":
        BKZ.reduction(M2, BKZ.Param(block_size=20, timeout=100, strategies=BKZ.DEFAULT_STRATEGY))
    elif V == "bkz40plain":
        BKZ.reduction(M2, BKZ.Param(block_size=40))
    elif V == "bkz40to":
        BKZ.reduction(M2, BKZ.Param(block_size=40, timeout=100))
    print(V, "reduction done", time.time()-t0, flush=True)
    verify(M2, n, c, tgt, G4, H, fs, 80)

# Local validation: chal prefix (classes only), then tests for C1 trick, C2 stats, C4 lattice.
import sys, random, math
SRC = "chal.py"
code = open(SRC).read().split("\nchallenge_generator_1()")[0].replace("signal.alarm(300)", "pass")
g = {"__name__": "chal_local"}
import os, hashlib, types
sig_stub = types.SimpleNamespace(alarm=lambda n: None)
g.update(dict(os=os, hashlib=hashlib, signal=sig_stub))
exec(code, g)

# ---------- C1: weight-1 inputs always give 0 ----------
G1 = g["Generator1"]
ok = True
for _ in range(200):
    G = G1()
    for i in range(30):
        if G.func_gen(1 << i) != 0:
            ok = False
print("C1 weight1->0 always:", ok)

# ---------- C2: exact per-m distributions of f=(prod%5+prod%7)%5 ----------
from math import comb
def pc_of_m(m):
    w = [0]*35
    for k in range(m+1):
        w[k % 35] += comb(m, k)
    den = 2**m
    pc = [0.0]*5
    for r in range(35):
        pc[(r % 5 + r % 7) % 5] += w[r]/den
    return pc
PC = {m: pc_of_m(m) for m in range(257)}
LOGPC = {m: [math.log(max(p, 1e-300)) for p in pc] for m, pc in PC.items()}
LOG5 = math.log(5)
# prior over m
PRIOR = [comb(256, m)/2**256 for m in range(257)]
LP = [math.log(PRIOR[m]) for m in range(257)]

def max_llr(counts):
    N = sum(counts)
    best = -1e18
    for m in range(100, 158):
        s = LP[m]
        for c in range(5):
            if counts[c]:
                s += counts[c]*LOGPC[m][c]
        if s > best: best = s
    return best + N*LOG5   # mixture~max(257 models); conservative

random.seed(1)
import numpy as np
def sim(N, trials=400):
    l0, l1 = [], []
    for _ in range(trials):
        m = sum(random.randint(0,1) for _ in range(256))
        counts = [0]*5
        if random.random() < 0.5:
            p = PC[m]
            for v in np.random.choice(5, size=N, p=p): counts[v]+=1
            l0.append(max_llr(counts))
        else:
            for v in np.random.choice(5, size=N): counts[v]+=1
            l1.append(max_llr(counts))
    return l0, l1
for N in (2000, 4000):
    l0, l1 = sim(N)
    l0.sort(); l1.sort()
    # threshold: mode0 if maxllr > TH
    for TH in (10, 15, 20):
        err0 = sum(1 for x in l0 if x <= TH)/len(l0)
        err1 = sum(1 for x in l1 if x > TH)/len(l1)
        print(f"N={N} TH={TH} P(mode0 misread)={err0:.3f} P(mode1 misread)={err1:.3f}")
    print(f"  l0 min={l0[0]:.1f} q5={l0[len(l0)//20]:.1f}  l1 p95={l1[int(len(l1)*0.95)]:.1f} max={l1[-1]:.1f}")

# ---------- C4: lattice CVP ----------
G4 = g["Generator4"]
import numpy as np
fails = 0
import c4lib
for trial in range(2):
    G = G4()
    p, q = G.p, G.q
    n = 80
    xs = list(range(1, n+1))
    fs = [G.func_gen(x) for x in xs]
    checks = {x: G.func_gen(x) for x in range(n+1, n+6)}
    r = c4lib.solve_c4_from_data(p, q, xs, fs, n, checks)
    ok = r == G.key
    fails += (not ok)
    print(f"C4 trial {trial}: {'OK' if ok else 'FAIL '+str(r)[:60]}")
print("C4 all ok:", fails == 0)

import sys, os, hashlib, types, random, time
code = open("chal.py").read().split("\nchallenge_generator_1()")[0].replace("signal.alarm(300)", "pass")
g = {"__name__": "chal_local"}
g.update(dict(os=os, hashlib=hashlib, signal=__import__("types").SimpleNamespace(alarm=lambda n: None)))
exec(code, g)
from fpylll import IntegerMatrix, LLL, BKZ
def digits5(x):
    h = int.from_bytes(hashlib.sha256(str(x).encode()).digest(), "big")
    d = []
    for _ in range(64): d.append(h % 5); h //= 5
    return d
def attack(T, block, wk, cfac, seed):
    random.seed(seed)
    g3 = g["Generator3"]()
    key = g3.key
    xs = list(range(1, T+1)); bs = [g3.func_gen(x) for x in xs]; D = [digits5(x) for x in xs]
    n = 64 + T + 1
    M = IntegerMatrix(64+T+1, n)
    for i in range(64):
        M[i, i] = wk
        for t in range(T): M[i, 64+t] = D[t][i]
    for t in range(T): M[64+t, 64+t] = 10
    r = 64+T; c = int(cfac*(T**0.5)) + 30
    for t in range(T): M[r, 64+t] = bs[t]
    M[r, n-1] = c
    t0 = time.time()
    LLL.reduction(M)
    BKZ.reduction(M, BKZ.Param(block_size=block, strategies=BKZ.DEFAULT_STRATEGY, timeout=240))
    found = None
    for i in range(M.nrows):
        if abs(M[i, n-1]) == c:
            s = 1 if M[i, n-1] > 0 else -1
            k = [(-s)*int(M[i, j]) for j in range(64)]
            if all(0 <= v <= 3 for v in k):
                if all((sum(k[i]*d[i] for i in range(64)) % 5) % 2 == bs[t] for t, d in enumerate(D)):
                    found = k; break
    print(f"T={T} block={block} wk={wk} cfac={cfac} seed={seed}: {'SOLVED' if found else 'FAIL'} ({time.time()-t0:.0f}s)", flush=True)
    return found
attack(256, 60, 2, 3.0, 1)
attack(256, 80, 2, 3.0, 2)

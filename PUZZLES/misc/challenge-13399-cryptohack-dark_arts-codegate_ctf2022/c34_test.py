# Test lattice solvability of Challenge 3 (Kannan CVP, offset-set) and Challenge 4 (mod-p CVP).
import os, hashlib, types, random, sys, time
code = open("chal.py").read().split("\nchallenge_generator_1()")[0].replace("signal.alarm(300)", "pass")
G = {"__name__": "chal_local"}
G.update(dict(os=os, hashlib=hashlib, signal=types.SimpleNamespace(alarm=lambda n: None)))
exec(code, G)
from fpylll import IntegerMatrix, LLL, BKZ

def run_bkz(M, block=40, timeout=None):
    LLL.reduction(M)
    p = BKZ.Param(block_size=block, strategies=BKZ.DEFAULT_STRATEGY)
    if timeout: p.timeout = timeout
    BKZ.reduction(M, p)

# ---------- Challenge 3 ----------
def test_c3(T=300, block=40, wk=2, seed=0):
    random.seed(seed)
    g3 = G["Generator3"]()
    key = g3.key
    def out(x): return g3.func_gen(x)
    def digits(x):
        h = int.from_bytes(hashlib.sha256(str(x).encode()).digest(), "big")
        d=[]
        for _ in range(64):
            d.append(h%5); h//=5
        return d
    xs = list(range(1, T+1))
    bs = [out(x) for x in xs]
    D = [digits(x) for x in xs]
    n = 64 + T + 1
    M = IntegerMatrix(64 + T + 1, n)
    for i in range(64):
        M[i, i] = wk
        for t in range(T): M[i, 64+t] = D[t][i]
    for t in range(T):
        M[64+t, 64+t] = 10
    r = 64 + T
    M[r, n-1] = 0
    tgt = [0]*64 + [b for b in bs]
    c = int(2.0*(T**0.5)) + 10
    for j in range(n-1): M[r, j] = tgt[j]
    M[r, n-1] = c
    t0=time.time()
    run_bkz(M, block=block)
    for i in range(M.nrows):
        if abs(M[i, n-1]) == c:
            s = 1 if M[i, n-1] > 0 else -1
            cand = [(-s)*M[i, j] // wk if False else 0 for j in range(64)]
            # error vector = target - point (if s=+1) -> k coords of (point-target) = -s*M[i,i]
            cand = [(-s)*int(M[i, j]) for j in range(64)]
            ok = all(0 <= v <= 3 for v in cand)
            if ok and cand == list(key):
                print(f"C3 T={T} block={block} seed={seed}: SOLVED in {time.time()-t0:.1f}s", flush=True)
                return True
    print(f"C3 T={T} block={block} seed={seed}: NOT found ({time.time()-t0:.1f}s)", flush=True)
    return False

# ---------- Challenge 4 ----------
def h_chain(x):
    h = hashlib.sha256(str(x).encode()).digest()
    out = []
    for _ in range(16):
        out.append(int.from_bytes(h, "big"))
        h = hashlib.sha256(h).digest()
    return out

def gauss_mod_p(A, b, p):
    A = [[x % p for x in row] for row in A]; b = [x % p for x in b]
    k = len(A[0]); r = 0
    piv = []
    for c in range(k):
        sel = next((i for i in range(r, len(A)) if A[i][c] % p), None)
        if sel is None: return None
        A[r], A[sel] = A[sel], A[r]; b[r], b[sel] = b[sel], b[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [v*inv % p for v in A[r]]; b[r] = b[r]*inv % p
        for i in range(len(A)):
            if i != r and A[i][c] % p:
                f = A[i][c]
                A[i] = [(A[i][j]-f*A[r][j]) % p for j in range(k)]
                b[i] = (b[i]-f*b[r]) % p
        piv.append(c); r += 1
        if r == k: break
    return b[:k] if len(piv)==k else None

def test_c4(T=48, block=40, seed=0):
    random.seed(seed)
    g4 = G["Generator4"]()
    p, q = g4.p, g4.q
    xs = list(range(1, T+1))
    fs = [g4.func_gen(x) for x in xs]
    H = [h_chain(x) for x in xs]
    n = T + 16 + 1
    M = IntegerMatrix(T + 17, T + 1)
    for i in range(16):
        for t in range(T): M[i, t] = H[t][i]
    for t in range(T): M[16+t, t] = p
    tgt = [fs[t] - q//2 for t in range(T)]
    c = int((T**0.5) * (q // 2)) // 3
    r = T + 16
    for t in range(T): M[r, t] = tgt[t]
    M[r, T] = c
    t0=time.time()
    run_bkz(M, block=block)
    Kp = {}
    for i in range(M.nrows):
        if abs(M[i, T]) == c:
            s = 1 if M[i, T] > 0 else -1
            for t in range(T):
                Kp[t] = tgt[t] - s*int(M[i, t])
    print(f"C4 T={T} seed={seed}: recovered {len(Kp)} coords ({time.time()-t0:.1f}s)", flush=True)
    if len(Kp) < 16: print("C4: not enough coords", flush=True); return False
    idx = sorted(Kp)[:16]
    A = [[H[t][i] for i in range(16)] for t in idx]
    b = [Kp[t] for t in idx]
    sol = gauss_mod_p(A, b, p)
    ok = sol == list(g4.key)
    print("C4 key match:", ok, flush=True)
    return ok

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv)>1 else "both"
    if which in ("c4","both"):
        test_c4(48, 40, 0)
    if which in ("c3","both"):
        test_c3(300, 40, 2, 0)

# Staged BKZ with float_type='mpfr' (the only precision-safe mode in this wheel;
# 'd'/'dpe' crash ~60-120 s into enumeration at dim 1024). Checkpoint + scan per slice.
import sys, time, threading, gzip, os, re, ast
from fpylll import IntegerMatrix, BKZ
d = 1024; n, q = 512, 127
T0 = time.time()
def log(*a): print(round(time.time() - T0), *a, flush=True)
def hb():
    while True:
        time.sleep(300); log("heartbeat alive")
threading.Thread(target=hb, daemon=True).start()

txt = open("output.txt").read()
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))

def cm(a, b):
    o = [0]*n
    nz = [(j, bj) for j, bj in enumerate(b) if bj]
    for i, ai in enumerate(a):
        if ai:
            for j, bj in nz: o[(i+j) % n] += ai*bj
    return o

def gf2_solve_unit(fbits, B):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c-i) % n] & 1: bits |= 1 << i
        rows.append([bits, B[c] & 1])
    piv = {}
    for r in rows:
        while r[0]:
            col = (r[0] & -r[0]).bit_length() - 1
            if col in piv:
                r[0] ^= piv[col][0]; r[1] ^= piv[col][1]
            else:
                piv[col] = r; break
        if not r[0] and r[1]: return None
    x = 0
    for col in range(n-1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        v = t
        rest = bits & ~(1 << col)
        while rest:
            c2 = (rest & -rest).bit_length() - 1
            v ^= (x >> c2) & 1
            rest &= rest - 1
        if v: x |= 1 << col
    return x

def try_f(fvec, gvec, tag):
    if sum(abs(c) for c in fvec) + 2*sum(abs(c) for c in gvec) >= q: return False
    if sum(1 for c in fvec if c) % 2 == 0: return False
    A = [x % q for x in cm(fvec, ct)]
    B = [a & 1 for a in A]
    x = gf2_solve_unit([abs(c) & 1 for c in fvec], B)
    if x is None: return False
    flag = x.to_bytes(n // 8, "big").lstrip(b"\x00")
    log(tag, "->", flag[:90])
    if flag.startswith(b"NNS{") and flag.endswith(b"}"):
        open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
        print("FLAG:", flag.decode(), flush=True)
        sys.exit(0)
    return False

def try_vec(v, tag):
    f0, g0 = v[:n], v[n:]
    try_f(f0, g0, tag)
    try_f([-c for c in f0], [-c for c in g0], tag + " neg")
    try_f(g0, f0, tag + " sw")
    try_f([-c for c in g0], [-c for c in f0], tag + " swneg")

def min_norm(M):
    return min(sum(M[i, j]**2 for j in range(d)) for i in range(d))

def ck(tag): return "M_s" + tag + ".txt.gz"
def checkpoint(M, tag):
    tmp = ck(tag) + ".tmp"
    with gzip.open(tmp, "wt") as f:
        for i in range(d):
            f.write(" ".join(str(M[i, j]) for j in range(d)) + "\n")
    if os.path.exists(ck(tag)): os.remove(ck(tag))
    os.rename(tmp, ck(tag))
    log("checkpointed", tag)
def load_ck(tag):
    name = ck(tag)
    if not os.path.exists(name):
        name = "M_" + tag + ".txt.gz"   # solve7-style checkpoint (M_lll.txt.gz)
    M = IntegerMatrix(d, d)
    with gzip.open(name, "rt") as f:
        for i, line in enumerate(f):
            for j, tok in enumerate(line.split()):
                M[i, j] = int(tok)
    log("resumed", tag)
    return M
def scan(tag, M):
    at = 0
    mn = None
    for i in range(d):
        v = [int(M[i, j]) for j in range(d)]
        s = sum(c*c for c in v)
        if mn is None or s < mn: mn = s
        if s > 200: continue
        at += 1
        try_vec(v, f"{tag} r{i} n2={s}")
    log("scan", tag, "tried", at, "min norm2", mn)

M = None
def run():
    global M
    M = load_ck("lll")
    scan("lll", M)
    for k in (20, 25, 30, 40):
        if os.path.exists(ck(str(k))):
            M = load_ck(str(k))
        tstage = time.time()
        slice_no = 0
        while time.time() - tstage < 5400 and slice_no < 6:
            slice_no += 1
            log("stage", k, "slice", slice_no, "start; min norm2", min_norm(M))
            BKZ.reduction(M, BKZ.EasyParam(k, max_time=900), float_type="mpfr", precision=200)
            log("stage", k, "slice", slice_no, "returned; min norm2", min_norm(M))
            checkpoint(M, str(k))
            scan("k" + str(k), M)
        log("stage", k, "done")
    log("NO FLAG")

ERR = []
def guarded():
    try:
        run()
    except BaseException:
        import traceback
        print(traceback.format_exc(), flush=True)
        ERR.append(1)
threading.stack_size(3 << 26)  # 192 MB
th = threading.Thread(target=guarded)
th.start()
th.join()
sys.exit(1 if ERR else 0)

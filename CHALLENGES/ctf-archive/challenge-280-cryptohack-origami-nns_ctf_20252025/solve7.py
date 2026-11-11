# BKZ on 1024-dim NTRU lattice; 192MB-stack thread; per-block-size stages with
# gzip checkpoints + resume. Usage: python solve7.py [k]  (single stage k, or full chain if none)
# Fix vs solve6: fpylll 0.6.4 has no list-of-lists IntegerMatrix ctor -> build manually.
import re, ast, sys, time, threading, gzip, os
from fpylll import IntegerMatrix, LLL, BKZ

t0 = time.time()
n, q = 512, 127
txt = open("output.txt").read()
pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))
d = 2 * n

def log(*a):
    print(round(time.time() - t0), *a, flush=True)

def hb():
    while True:
        time.sleep(180)
        log("heartbeat alive")
threading.Thread(target=hb, daemon=True).start()

# --- decryptor (validated in selftest.py / solve5.py) ---
def cyclic_mul(a, b):
    out = [0] * n
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    out[(i + j) % n] += ai * bj
    return out

def gf2_solve_unit(fbits, B):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c - i) % n] & 1: bits |= 1 << i
        rows.append([bits, B[c] & 1])
    piv = {}
    for r in rows:
        while r[0]:
            col = (r[0] & -r[0]).bit_length() - 1
            if col in piv:
                r[0] ^= piv[col][0]; r[1] ^= piv[col][1]
            else:
                piv[col] = r; break
        if not r[0] and r[1]:
            return None
    x = 0
    for col in range(n - 1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        val = t
        rest = bits & ~(1 << col)
        while rest:
            c = (rest & -rest).bit_length() - 1
            val ^= (x >> c) & 1
            rest &= rest - 1
        if val: x |= 1 << col
    return x

def try_f(fvec, gvec, tag):
    if sum(abs(c) for c in fvec) + 2 * sum(abs(c) for c in gvec) >= q: return False
    if sum(1 for c in fvec if c) % 2 == 0: return False
    fc = cyclic_mul(fvec, ct)
    A = [x % q for x in fc]
    B = [a & 1 for a in A]
    x = gf2_solve_unit([abs(c) & 1 for c in fvec], B)
    if x is None: return False
    flag = x.to_bytes(n // 8, "big").lstrip(b"\x00")
    print(tag, "->", flag[:90], flush=True)
    if flag.startswith(b"NNS{") and flag.endswith(b"}"):
        open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
        print("FLAG:", flag.decode(), flush=True)
        sys.exit(0)
    return False

def try_vec(v, tag):
    # true secret is 0/1 (source.sage random_poly uses +1 only); BKZ row may be
    # (f|g), (-f|-g), (g|f) or (-g|-f) — try all four sign/order variants.
    f0 = v[:n]; g0 = v[n:]
    try_f(f0, g0, tag)
    try_f([-c for c in f0], [-c for c in g0], tag + " neg")
    try_f(g0, f0, tag + " swap")
    try_f([-c for c in g0], [-c for c in f0], tag + " swapneg")

def scan(tag, M):
    attempted = 0
    for i in range(d):
        v = [int(M[i, j]) for j in range(d)]
        s = sum(c * c for c in v)
        if s > 200:      # target norm2 = 70; skip hopeless rows fast
            continue
        attempted += 1
        try_vec(v, tag + " row%d n2=%d" % (i, s))
    log("scan", tag, "attempted", attempted, "short rows")

def min_norm(M):
    mn = None
    for i in range(d):
        s = sum(M[i, j] ** 2 for j in range(d))
        if mn is None or s < mn: mn = s
    return mn

def ck_name(tag):
    return "M_" + tag + ".txt.gz"

def checkpoint(M, tag):
    tmp = ck_name(tag) + ".tmp"
    with gzip.open(tmp, "wt") as f:
        for i in range(d):
            f.write(" ".join(str(M[i, j]) for j in range(d)) + "\n")
    if os.path.exists(ck_name(tag)):
        os.remove(ck_name(tag))
    os.rename(tmp, ck_name(tag))
    log("checkpointed", tag)

def load_ck(tag):
    M = IntegerMatrix(d, d)
    with gzip.open(ck_name(tag), "rt") as f:
        for i, line in enumerate(f):
            for j, tok in enumerate(line.split()):
                M[i, j] = int(tok)
    log("resumed from checkpoint", tag)
    return M

def build_matrix():
    M = IntegerMatrix(d, d)          # 0.6.4 has no list-of-lists ctor
    for i in range(n):
        M[i, i] = 1
        for j in range(n):
            M[i, j + n] = pk[(j - i) % n]
    for i in range(n):
        M[i + n, i + n] = q
    return M

def stage_run(M, k, prev_tag):
    if os.path.exists(ck_name(str(k))):
        log("stage", k, "already checkpointed, loading")
        return load_ck(str(k))
    if prev_tag and prev_tag != "lll":
        log("note: continuing from", prev_tag, "into BKZ", k)
    p = BKZ.EasyParam(k, max_time=2400)   # 40-min cap/stage; max_time is ctor-only (fpylll 0.6.4)
    BKZ.reduction(M, p)
    log("BKZ", k, "done; min row norm2 =", min_norm(M))
    checkpoint(M, str(k))
    scan("k" + str(k), M)
    return M

def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage is not None:
        prev = None
        for t in ("40", "30", "25", "20", "lll"):
            if os.path.exists(ck_name(t)): prev = t; break
        if prev:
            M = load_ck(prev)
        else:
            M = build_matrix(); log("built")
            LLL.reduction(M); log("LLL done; min row norm2 =", min_norm(M))
            checkpoint(M, "lll"); scan("lll", M)
        stage_run(M, int(stage), prev)
        return

    if os.path.exists(ck_name("lll")):
        M = load_ck("lll")
    else:
        M = build_matrix(); log("built")
        LLL.reduction(M); log("LLL done; min row norm2 =", min_norm(M))
        checkpoint(M, "lll"); scan("lll", M)
    for k in (20, 25, 30, 40):
        M = stage_run(M, k, None)
    log("no flag yet")

ERR = []
def guarded():
    try:
        main()
    except BaseException as e:
        ERR.append(e)
        raise

threading.stack_size(3 << 26)  # 192 MB
th = threading.Thread(target=guarded)
th.start()
th.join()
log("main thread exited")
sys.exit(1 if ERR else 0)

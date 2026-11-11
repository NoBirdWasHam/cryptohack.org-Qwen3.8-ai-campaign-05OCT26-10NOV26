# BKZ on 1024-dim NTRU lattice with 1GB thread stack; staged LLL->BKZ with scans + checkpoints.
import re, ast, sys, time, threading, gzip
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
        time.sleep(120)
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
    try_f(v[:n], v[n:], tag)          # f-part as f
    try_f(v[n:], v[:n], tag + " swap")  # g-part as f (swap roles)

def min_norm(M):
    mn = None
    for i in range(d):
        s = sum(M[i, j] ** 2 for j in range(d))
        if mn is None or s < mn: mn = s
    return mn

def scan(tag, M):
    for i in range(d):
        v = [M[i, j] for j in range(d)]
        if max(map(abs, v)) > 1: continue
        s1 = sum(1 for c in v if c)
        if s1 > 90: continue
        try_vec(v, tag + " row" + str(i))
        try_vec([-c for c in v], tag + " neg" + str(i))
    log(tag, "scan done; min row norm2 =", min_norm(M))

def checkpoint(M, name):
    with gzip.open(name + ".txt.gz", "wt") as f:
        for i in range(d):
            f.write(" ".join(str(M[i, j]) for j in range(d)) + "\n")
    log("checkpointed", name)

def main():
    rows = []
    for i in range(n):
        rows.append(([1 if i == j else 0 for j in range(n)]) + [pk[(j - i) % n] for j in range(n)])
    for i in range(n):
        rows.append([0] * n + [q if i == j else 0 for j in range(n)])
    M = IntegerMatrix(rows)
    log("built")

    LLL.reduction(M)
    log("LLL done; min row norm2 =", min_norm(M))
    checkpoint(M, "M_lll")
    scan("lll", M)

    for k in (20, 25, 30, 40):
        p = BKZ.EasyParam(k)
        try:
            p.auto_abort_timer = 2400  # cap each stage (s) if supported
        except Exception as e:
            log("auto_abort unsupported:", e)
        BKZ.reduction(M, p)
        log("BKZ", k, "done; min row norm2 =", min_norm(M))
        checkpoint(M, "M_k" + str(k))
        scan("k" + str(k), M)
    log("no flag yet")

threading.stack_size(3 << 26)  # 192 MB = max accepted here (64 MB crashed before)
th = threading.Thread(target=main)
th.start()
th.join()
log("main thread exited")

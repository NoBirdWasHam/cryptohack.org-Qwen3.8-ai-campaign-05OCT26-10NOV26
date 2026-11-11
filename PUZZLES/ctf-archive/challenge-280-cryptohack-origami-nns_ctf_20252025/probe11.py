# probe11: own float64 nearest-plane (Babai) on the LLL basis toward the weight-35
# center c = (35/512)*ones. If (f,g) is found: exact mod-q membership + parity decrypt.
import sys, time, gzip, re, ast
import numpy as np
t0 = time.time()
def log(*a): print(round(time.time()-t0, 1), *a, flush=True)

txt = open("output.txt").read()
pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))
n, q, d = 512, 127, 1024

def cm(a, b):
    o = [0]*n
    nz = [(j, bj) for j, bj in enumerate(b) if bj]
    for i, ai in enumerate(a):
        if ai:
            for j, bj in nz: o[(i+j) % n] += ai*bj
    return [x % q for x in o]

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
    f0, g0 = list(v[:n]), list(v[n:])
    try_f(f0, g0, tag)
    try_f([-c for c in f0], [-c for c in g0], tag + " neg")
    try_f(g0, f0, tag + " sw")
    try_f([-c for c in g0], [-c for c in f0], tag + " swneg")

pkL = [int(x) % q for x in pk]
def member(v, tag):
    a = [int(x) % q for x in v[:n]]
    b = [int(x) % q for x in v[n:]]
    o1 = cm(a, pkL) == b
    o2 = cm(b, pkL) == a
    log(tag, "membership b==a*h:", o1, " a==b*h:", o2)
    return o1 or o2

# ---- load basis ----
A_int = np.zeros((d, d), dtype=np.int64)
with gzip.open("M_lll.txt.gz", "rt") as f:
    for i, line in enumerate(f):
        A_int[i, :] = np.fromiter(map(int, line.split()), dtype=np.int64)
log("loaded", A_int.shape, "max|e|", int(np.abs(A_int).max()))

Bf = A_int.astype(np.float64)
bs = Bf.copy()
r = np.einsum("ij,ij->i", bs, bs)
mu = np.zeros((d, d))
for i in range(d):
    for j in range(i):
        m = Bf[i] @ bs[j] / r[j]
        mu[i, j] = m
        if m != 0.0:
            bs[i] -= m * bs[j]
    r[i] = bs[i] @ bs[i]
log("GS done: min||b*||2 =", r.min(), " max||b*||2 =", r.max(),
    " #levels<260:", int((r < 260).sum()), " #levels<66:", int((r < 66).sum()))

def nearest_plane(order):
    t = np.full(d, 35.0/512.0)
    cvec = np.zeros(d, dtype=np.int64)
    rng = range(d-1, -1, -1) if order == "rev" else range(d)
    for i in rng:
        ci = round(float(t @ bs[i] / r[i]))
        if ci:
            t -= ci * Bf[i]
            cvec += ci * A_int[i]
    resid2 = float(t @ t)
    return cvec, resid2

for order in ("rev", "fwd"):
    cvec, rd = nearest_plane(order)
    d2 = float(np.sum((cvec.astype(np.float64) - 35.0/512.0)**2))
    log(order, "resid2 =", round(rd, 3), " dist2(to center) =", round(d2, 2))
    if rd < 200:
        vv = [int(x) for x in cvec]
        member(vv, order)
        try_vec(vv, order)
log("PROBE11 DONE")

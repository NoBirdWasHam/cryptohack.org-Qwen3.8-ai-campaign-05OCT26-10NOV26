# scan_cli.py BASISFILE : scan reduced basis rows for (f,g), then Babai center-CVP,
# validate by mod-q membership, decrypt via p=2 no-wrap parity trick.
import sys, time, re, ast
import numpy as np
t0 = time.time()
def log(*a): print(round(time.time()-t0, 1), *a, flush=True)

path = sys.argv[1]
txt = open("output.txt").read()
pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))
n, q = 512, 127

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
def member(v):
    a = [int(x) % q for x in v[:n]]
    b = [int(x) % q for x in v[n:]]
    return cm(a, pkL) == b or cm(b, pkL) == a

raw = open(path).read()
import re as _re
_groups = _re.findall(r"\[([^\[\]]+)\]", raw)
rows = []
for chunk in _groups:
    toks = chunk.split()
    if toks:
        rows.append([int(t) for t in toks])
log("parsed rows", len(rows), "x", len(rows[0]) if rows else 0)
assert all(len(r) == 2*n for r in rows)

mn = None; tried = 0
for i, r in enumerate(rows):
    s2 = sum(c*c for c in r)
    if mn is None or s2 < mn: mn = s2
    if s2 > 400: continue
    tried += 1
    log("row", i, "norm2", s2, "member", member(r))
    try_vec(r, f"row{i}")
log("row scan done: min norm2", mn, "tried", tried)

A_int = np.array(rows, dtype=np.int64)
d = len(rows)
Bf = A_int.astype(np.float64)
bs = Bf.copy()
r = np.einsum("ij,ij->i", bs, bs)
for i in range(d):
    for j in range(i):
        m = Bf[i] @ bs[j] / r[j]
        if m != 0.0:
            bs[i] -= m * bs[j]
    r[i] = bs[i] @ bs[i]
log("GS: min||b*||2 =", round(r.min(), 3), " max =", round(r.max(), 1))

def nearest_plane(order):
    t = np.full(d, 35.0/512.0)
    cvec = np.zeros(d, dtype=np.int64)
    rng = range(d-1, -1, -1) if order == "rev" else range(d)
    for i in rng:
        ci = round(float(t @ bs[i] / r[i]))
        if ci:
            t -= ci * Bf[i]
            cvec += ci * A_int[i]
    return cvec, float(t @ t)

for order in ("rev", "fwd"):
    cvec, rd = nearest_plane(order)
    log("NP", order, "resid2 =", round(rd, 2))
    if rd < 300:
        vv = [int(x) for x in cvec]
        log("NP", order, "member", member(vv))
        try_vec(vv, f"NP-{order}")
log("SCAN_CLI DONE")

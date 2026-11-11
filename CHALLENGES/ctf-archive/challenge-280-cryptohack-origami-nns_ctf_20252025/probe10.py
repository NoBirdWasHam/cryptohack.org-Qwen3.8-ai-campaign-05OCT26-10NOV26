# Probe: is the (f,g) secret recoverable from the LLL basis by CVP-to-center (Babai)?
# f,g in {0,1}^512 weight 35 each => dist((f,g), center) = sqrt(65.2) ~ 8.07 << GH ~87.
import sys, time, gzip, re, ast
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
    f0, g0 = v[:n], v[n:]
    try_f(f0, g0, tag)
    try_f([-c for c in f0], [-c for c in g0], tag + " neg")
    try_f(g0, f0, tag + " sw")
    try_f([-c for c in g0], [-c for c in f0], tag + " swneg")

def member(v, tag):
    a, b = v[:n], v[n:]
    o1 = cm(a, pk) == [x % q for x in b]
    o2 = cm(b, pk) == [x % q for x in a]
    log(tag, "membership a*h==b:", o1, " b*h==a:", o2)
    return o1 or o2

from fpylll import IntegerMatrix
from fpylll.fplll.gso import MatGSO
from fpylll.fplll.svpcvp import babai

M = IntegerMatrix(d, d)
with gzip.open("M_lll.txt.gz", "rt") as f:
    for i, line in enumerate(f):
        for j, tok in enumerate(line.split()):
            M[i, j] = int(tok)
mx = 0; mn = None
for i in range(d):
    s = 0
    for j in range(d):
        e = abs(int(M[i, j]))
        if e > mx: mx = e
        s += int(M[i, j])**2
    if mn is None or s < mn: mn = s
log("loaded M_lll; max|entry| =", mx, "min row norm2 =", mn)

# GSO profile (dtype default); watch get_r returns SQUARED norms
log("gso start")
g = MatGSO(M)
log("MatGSO constructed")
rmin = None; rmax = None; nbelow = 0
for i in range(d):
    r = g.get_r(i, i)
    if rmin is None or r < rmin: rmin = r
    if rmax is None or r > rmax: rmax = r
    if r < 260: nbelow += 1
    if i % 256 == 255: log("  profile i=", i)
log("GSO profile: min||b*||2 =", round(float(rmin),2), " max||b*||2 =", round(float(rmax),2), " #levels<260:", nbelow)

# Babai nearest plane on 512*M toward 35*ones == CVP to weight-35 center
log("B2 scale start")
B2 = IntegerMatrix(d, d)
for i in range(d):
    for j in range(d):
        B2[i, j] = 512 * int(M[i, j])
target = [35] * d
log("babai start")
try:
    w = babai(B2, target)
    v = [int(x) for x in w]
except BaseException as e:
    log("babai ERR", type(e).__name__, str(e)[:200]); v = None
if v is not None:
    dd = sum((x - 35)**2 for x in v) / (512.0*512.0)
    log("babai dist2(to center) =", round(dd, 2))
    vv = [x // 512 for x in v]
    if all(x % 512 == 0 for x in v):
        member(vv, "babai v")
        try_vec(vv, "babai")
    else:
        log("babai result not divisible by 512 (still lattice pt of 512M? sanity):", sum(1 for x in v if x % 512))
log("PROBE10 DONE")

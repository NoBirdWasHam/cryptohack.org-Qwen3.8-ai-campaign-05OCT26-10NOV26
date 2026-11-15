# probe_fpy_t280.py — fpylll in-process BKZ probe at beta 64 on the planted toy64
# lattice (dim 128) + Kannan-embed variant; escal. branch (3) feasibility gate.
import sys, re, time, random
from fpylll import IntegerMatrix, BKZ, LLL

MODE = sys.argv[1] if len(sys.argv) > 1 else "bkz64"
path = "toy64.fplll"
txt = open(path).read()
groups = re.findall(r"\[([^\[\]]+)\]", txt)
rows = [[int(t) for t in g.split()] for g in groups if g.split()]
d, w = len(rows), len(rows[0])
print("toy basis", d, "x", w, flush=True)

def build(mat):
    m = IntegerMatrix(d, w)
    for i, r in enumerate(mat):
        for j, v in enumerate(r):
            m[i, j] = v
    return m

if MODE == "embed64":
    # Kannan embedding of the scan_cli hint target t=(35/512)... scaled: toy w=5
    # planted f,g have weight 5/64; use t = ones/13-ish -> scaled int lattice x13
    S = 13
    t = [5 * (1 if i % 13 == 0 else 0) for i in range(0, 1)]  # placeholder
    t = [S * 5 // 64 + 1] * w  # hint: uniform small target
    big = IntegerMatrix(d + 1, w + 1)
    for i in range(d):
        for j in range(w):
            big[i, j] = rows[i][j] * S
    for j in range(w):
        big[d, j] = t[j]
    big[d, w] = 1
    m = big
    d += 1
else:
    m = build(rows)

beta = int(sys.argv[2]) if len(sys.argv) > 2 else 64
t0 = time.time()
try:
    BKZ.reduction(m, BKZ.EasyParam(beta, max_time=90.0))
    print("SURVIVED", MODE, "beta", beta, "dim", d, "in", round(time.time() - t0, 1), "s", flush=True)
    # min row norm
    best = None
    md = m.dense_matrix()
    import math
    for i in range(min(d, 8)):
        n2 = sum(int(x) * int(x) for x in md[i])
        print("row", i, "norm2", n2, flush=True)
except Exception as e:
    print("EXC", type(e).__name__, str(e)[:200], flush=True)
    sys.exit(3)

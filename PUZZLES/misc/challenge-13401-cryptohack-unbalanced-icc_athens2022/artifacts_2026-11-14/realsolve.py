"""Real solver: ICC Athens 2022 'unbalanced' — Durfee-Nguyen trivariate Coppersmith.

ed = 1 + k*phi, p||N 256-bit, q 768-bit, d 300-bit, e ~ N.
f(x,y,z) = 2 + x*(A - y - z), A = N+1  (yz -> N);  root (2k, p, q), f(root) = 2ed = 0 mod e.
DN00 shifts g_{k,i,b}, h_{k,j} with m=8, t=5, a=1 -> det condition margin +46 bits/dim.
"""
import sys, time, math, pickle
import variants as V
from fpylll import IntegerMatrix, LLL

M, T, A_SHIFT = 8, 5, 1
BOUNDS = (301, 256, 768)  # x=2k, y=p, z=q


def load_params():
    txt = open("output.txt").read()
    N = int(txt.split("N = ")[1].split("\n")[0], 16)
    e = int(txt.split("e = ")[1].split("\n")[0], 16)
    c = int(txt.split("c = ")[1].split("\n")[0], 16)
    return N, e, c


def reduce_lattice(N, e, cache="rows.pkl"):
    t0 = time.time()
    polys = V.build_polys(N, e, m=M, t=T, a=A_SHIFT, C=2)
    mons, W, B = V.make_lattice(polys, BOUNDS)
    print(f"lattice {B.nrows}x{len(mons)}; entries <= {max(abs(B[r,0]) for r in range(B.nrows)).bit_length()} bits", flush=True)
    LLL.reduction(B, delta=0.99)
    print(f"LLL done in {time.time()-t0:.0f}s", flush=True)
    Em = e ** M
    em2 = Em * Em
    rows = []
    w = len(mons)
    for r in range(B.nrows):
        poly = {}
        for j, mo in enumerate(mons):
            v = int(B[r, j])
            if v:
                assert v % W[j] == 0, "divisibility broken"
                poly[mo] = v // W[j]
        if not poly or all(v % Em == 0 for v in poly.values()):
            continue
        n2 = sum(int(B[r, j]) ** 2 for j in range(len(mons)))
        rows.append((n2, poly))
    rows.sort(key=lambda x: x[0])
    hg = [p for n2, p in rows if n2 * w < em2]
    print(f"nontrivial rows: {len(rows)}; strict-HG passing: {len(hg)}", flush=True)
    with open(cache, "wb") as f:
        pickle.dump({"hg": hg, "rows": rows, "ebits": math.log2(e)}, f)
    return hg, rows


if __name__ == "__main__":
    N, e, c = load_params()
    hg, rows = reduce_lattice(N, e)
    if len(hg) < 2:
        print("too few HG rows; take shortest nontrivial rows")
        sel = [p for _, p in rows[:6]]
    else:
        sel = hg[:6]
    print(f"selected {len(sel)} vanishing polys, support sizes {[len(p) for p in sel]}", flush=True)
    with open("selected.pkl", "wb") as f:
        pickle.dump({"sel": sel, "N": N, "e": e, "c": c}, f)
    print("saved selected.pkl", flush=True)

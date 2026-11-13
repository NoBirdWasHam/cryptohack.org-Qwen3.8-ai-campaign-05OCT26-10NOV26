# t280_fold_mk.py — build + LLL the two folded dim-512 lattices, log GS profiles.
import sys, time, json
sys.path.insert(0, ".")
import numpy as np
from fpylll import IntegerMatrix, GSO
from fpylll.fplll.lll import lll_reduction
from t280_fold import load_real, make_folds, build_lattice, member

h, ct = load_real()
hp, hm = make_folds(h)
m, q = 256, 127

def to_intmat(M):
    d = M.shape[0]; B = IntegerMatrix(d, d)
    for i in range(d):
        for j in range(d): B[i, j] = int(M[i, j])
    return B

def write_fplll(B, path):
    with open(path, "w") as fp:
        fp.write("[")
        for i in range(B.nrows):
            fp.write("[ " + " ".join(str(int(B[i, j])) for j in range(B.ncols)) + " ]")
        fp.write(" ]\n")

def profile(B, name):
    d = B.nrows
    A = np.array([[int(B[i, j]) for j in range(B.ncols)] for i in range(d)], dtype=np.longdouble)
    # classical Gram-Schmidt in 80-bit extended; NOTE float64 Gram of this lattice is
    # numerically singular (lam_min < 0 at -1e-9), so ld is the minimum safe backend here.
    l2 = []
    for i in range(d):
        bi = A[i].copy()
        for j in range(i):
            bi = bi - (A[i] @ V[j] / r[j]) * V[j]
        rj = bi @ bi
        r[i] = rj
        V[i] = bi
        l2.append(float(np.log2(max(rj, np.longdouble(1e-4000))) / 2))
    prof = {"lattice": name, "d": d, "log2_gs_norm": l2}
    mn = min(sum(int(B[i, j]) ** 2 for j in range(B.ncols)) for i in range(d))
    prof["min_row_norm2"] = int(mn)
    steps = [(i, round(l2[i] - l2[i + 1], 3)) for i in range(d - 1) if l2[i] - l2[i + 1] > 0.5]
    prof["steps"] = steps
    prof["gs_min_log2"] = round(min(l2), 3); prof["gs_max_log2"] = round(max(l2), 3)
    return prof

r = {}; V = {}

out = []
for name, hf, eps in (("plus", hp, +1), ("minus", hm, -1)):
    Hlat = build_lattice(hf, m, q, eps)
    B = to_intmat(Hlat)
    t0 = time.time(); lll_reduction(B); tt = time.time() - t0
    prof = profile(B, name)
    write_fplll(B, f"t280_f{name[0]}_cur.fplll")
    print(name, f"LLL {tt:.1f}s", "min norm2", prof["min_row_norm2"],
          "gs log2 range", prof["gs_min_log2"], "-", prof["gs_max_log2"], flush=True)
    print(name, "steps (pos, log2drop):", prof["steps"][:10], flush=True)
    out.append(prof)
json.dump(out, open("t280_fold_profiles.json", "w"))
print("wrote t280_fp_cur.fplll t280_fm_cur.fplll t280_fold_profiles.json")

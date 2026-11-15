# t280_ctl_mk.py — plant REAL-SHAPE toy (n=512,q=127,df=dg=35) and build the SAME
# fold lattices as the real pipeline (level-1 plus/minus dim512, level-2 ++/+- dim256,
# level-3 +++/++- dim128), LLL-seed them exactly like t280_fold*_mk.py, write .fplll
# files + truth JSON for the control runner.
import sys, time, json
sys.path.insert(0, ".")
import numpy as np
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from t280_fold import ringmul, conv512, build_lattice, member

n, q, df, dg, dr = 512, 127, 35, 35, 22
rng = np.random.default_rng(280222)

def sparse(N, d):
    v = np.zeros(N, dtype=np.int64); v[rng.choice(N, d, replace=False)] = 1; return v

def circ_solve_fg(f, g):
    Mx = np.zeros((n, n + 1), dtype=np.int64)
    idx = (np.arange(n)[:, None] - np.arange(n)[None, :]) % n
    Mx[:, :n] = f[idx] % q
    Mx[:, n] = g % q
    where = [-1] * n; row = 0
    for col in range(n):
        cand = np.nonzero(Mx[row:, col] % q)[0]
        if len(cand) == 0: continue
        sel = row + int(cand[0])
        if sel != row: Mx[[row, sel]] = Mx[[sel, row]]
        inv = pow(int(Mx[row, col]), q - 2, q)
        Mx[row] = (Mx[row] * inv) % q
        colv = Mx[:, col].copy(); colv[row] = 0
        nz = np.nonzero(colv)[0]
        if len(nz): Mx[nz] = (Mx[nz] - np.outer(colv[nz], Mx[row])) % q
        where[col] = row; row += 1
    if row < n: return None
    h = np.zeros(n, dtype=np.int64)
    for col in range(n):
        if where[col] != -1: h[col] = Mx[where[col], n]
    return h

t0 = time.time()
while True:
    f = sparse(n, df); g = sparse(n, dg)
    if int(f.sum()) % 2 == 0: continue
    h = circ_solve_fg(f, g)
    if h is None: continue
    if not np.array_equal(conv512(f, h) % q, g): continue
    break
FLAG = (b"NNS{CTL_LADDER_TOY_" + b"0" * 100)[:63] + b"}"
val = int.from_bytes(FLAG, "big")
mvec = np.array([(val >> i) & 1 for i in range(n)], dtype=np.int64)
r = sparse(n, dr)
ct = (2 * conv512(h, r) + mvec) % q
print(f"planted ok {time.time()-t0:.1f}s", flush=True)

m = 256; m2 = 128; m3 = 64
hp = (h[:m] + h[m:]) % q;  hm = (h[:m] - h[m:]) % q
hpp = (hp[:m2] + hp[m2:]) % q; hpm = (hp[:m2] - hp[m2:]) % q
hppp = (hpp[:m3] + hpp[m3:]) % q; hppm = (hpp[:m3] - hpp[m3:]) % q

fp = (f[:m] + f[m:]) % q
fpp = (fp[:m2] + fp[m2:]) % q
fppp = (fpp[:m3] + fpp[m3:]) % q; fppm = (fpp[:m3] - fpp[m3:]) % q
gp = (g[:m] + g[m:]) % q
gpp = (gp[:m2] + gp[m2:]) % q
gppp = (gpp[:m3] + gpp[m3:]) % q; gppm = (gpp[:m3] - gpp[m3:]) % q

def centered(v):
    w = np.array(v, dtype=np.int64) % q
    return w - q * (w > 63)

truth = {"h": h.tolist(), "ct": ct.tolist(), "f": f.tolist(), "g": g.tolist(),
         "flag": FLAG.decode(),
         "fp": fp.tolist(), "fm": centered(f[:m] - f[m:]).tolist(),
         "gp": gp.tolist(), "gm": centered(g[:m] - g[m:]).tolist(),
         "fpp": fpp.tolist(), "fpm": centered(fp[:m2] - fp[m2:]).tolist(),
         "gpp": gpp.tolist(), "gpm": centered(gp[:m2] - gp[m2:]).tolist(),
         "fppp": fppp.tolist(), "fppm": centered(fpp[:m3] - fpp[m3:]).tolist(),
         "gppp": gppp.tolist(), "gppm": centered(gpp[:m3] - gpp[m3:]).tolist()}
json.dump(truth, open("t280_ctl_truth.json", "w"))
print("planted norms2: f+++", int((fppp**2).sum()), "f++- absmax", int(np.abs(truth["fppm"]).max()),
      "++ row2", int((np.array(truth["fppp"]**2).sum() + (gppp**2).sum()) + sum(x*x for x in truth["gppp"]) + 0) if False else "", flush=True)

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

specs = [("ctlp", hp, m, +1), ("ctlm", hm, m, -1),
         ("ctlpp", hpp, m2, +1), ("ctlpm", hpm, m2, -1),
         ("ctlppp", hppp, m3, +1), ("ctlppm", hppm, m3, -1)]
for name, hf, mm, eps in specs:
    Lat = build_lattice(hf, mm, q, eps)
    B = to_intmat(Lat)
    t1 = time.time(); lll_reduction(B)
    mn = min(sum(int(B[i, j])**2 for j in range(B.ncols)) for i in range(B.nrows))
    write_fplll(B, f"t280_ctl_{name}.fplll")
    print(name, f"dim {2*mm} LLL {time.time()-t1:.1f}s minnorm2 {mn}", flush=True)
print("CTL_MK DONE")

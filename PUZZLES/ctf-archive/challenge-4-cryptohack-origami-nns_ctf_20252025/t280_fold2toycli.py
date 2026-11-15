# t280_fold2toycli.py — validate LEVEL-2 pipeline (scan->glue->overlap-bits->decrypt)
# on a planted toy scheme n=256, doubled folds dim-128 lattices, via fplll CLI.
import sys, os, time, subprocess, random
sys.path.insert(0, ".")
import numpy as np
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from t280_fold import build_lattice, ringmul, member

FPLLL = "~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
SDEF = "~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
os.environ["PATH"] = "~/tools/msys64/ucrt64/bin;" + os.environ["PATH"]

n, q, df, dg, dr, m, m2 = 256, 127, 9, 9, 4, 128, 64   # halves: m=128, quarters m2=64
rng = random.Random(2026)
def sparse(N, d):
    v = np.zeros(N, dtype=np.int64); v[rng.sample(range(N), d)] = 1; return v

def conv(a, b, N):
    out = np.zeros(N, dtype=np.int64); a = np.asarray(a, np.int64); b = np.asarray(b, np.int64)
    for i in range(N):
        if a[i]:
            out[(np.arange(N) + i) % N] += a[i] * b
    return out

def to_intmat(M):
    d = M.shape[0]; B = IntegerMatrix(d, d)
    for i in range(d):
        for j in range(d): B[i, j] = int(M[i, j])
    return B

def write_fplll(M, path):
    with open(path, "w") as fp:
        fp.write("[")
        for row in M:
            fp.write("[ " + " ".join(str(int(x)) for x in row) + " ]")
        fp.write(" ]\n")

_tr = 0
while True:
    _tr += 1
    if _tr % 20 == 1: print("seed trial", _tr, flush=True)
    f = sparse(n, df); g = sparse(n, dg)
    # f unit mod 2 and mod q: use parity weight check + inverse exists check later
    if sum(int(x) for x in f) % 2 == 0: continue
    h = None
    try:
        # solve circ(f) @ h = g mod 127 with numpy Gauss over F_127
        ff = np.array(f, dtype=np.int64)
        Mx = np.zeros((n, n), dtype=np.int64)
        idx = (np.arange(n)[:, None] - np.arange(n)[None, :]) % n
        np.add.at(Mx, (np.repeat(np.arange(n), n), idx.ravel()), np.tile(ff, n))
        Mx %= q
        M = np.concatenate([Mx, (np.array(g, dtype=np.int64) % q)[:, None]], axis=1)
        where = [-1] * n; row = 0
        for col in range(n):
            cand = np.nonzero(M[row:, col] % q)[0]
            if len(cand) == 0: continue
            sel = row + int(cand[0])
            M[[row, sel]] = M[[sel, row]]
            inv = pow(int(M[row, col]), q - 2, q)
            M[row] = (M[row] * inv) % q
            colvals = M[:, col].copy()
            colvals[row] = 0
            nz = np.nonzero(colvals % q)[0]
            if len(nz):
                M[nz] = (M[nz] - np.outer(colvals[nz] % q, M[row])) % q
            where[col] = row; row += 1
        if row < n: continue  # f not invertible mod q
        hv = np.zeros(n, dtype=np.int64)
        for col in range(n):
            if where[col] != -1: hv[col] = M[where[col], n]
        if int(hv.sum()) == 0: continue
        h = hv
    except Exception:
        continue
    gg = conv(f, h, n) % q
    if not np.array_equal(gg, np.array(g) % q): continue
    break

flag_bytes = b"NNS{L2TOY_FOLD2WORKS_0123456789}"
assert len(flag_bytes) == n // 8, len(flag_bytes)
mvec = np.unpackbits(np.frombuffer(flag_bytes, np.uint8))[:n].astype(np.int64)
r = sparse(n, dr)
ct = (2 * conv(h, r, n) + mvec) % q
print("planted ok", flush=True)

def fold2_all(vec):
    v0, v1 = vec[:m], vec[m:]
    fp_ = (v0 + v1) % q                       # ring y^m-1 (m=128)
    a = (fp_[:m2] + fp_[m2:]) % q             # y^m2-1  (++)
    b = (fp_[:m2] - fp_[m2:]) % q             # y^m2+1  (+-)
    fm_ = (v0 - v1) % q                       # (not used in this toy scan path)
    return fp_, a, b, fm_

# h folds: h is in R_q; h+ = h0+h1 etc (same fold on h)
h0, h1 = h[:m], h[m:]
hp = (h0 + h1) % q
hpp = (hp[:m2] + hp[m2:]) % q
hpm = (hp[:m2] - hp[m2:]) % q

fp_, app, bmp, fm_ = fold2_all(f)
gp_, agp, bgp, gm_ = fold2_all(g)
print("planted f++ norm2", int((app**2).sum()), "f+- norm2", int((bmp**2).sum()), flush=True)

def run_cli(inp, outp, beta, tmax=600):
    t0 = time.time()
    with open(inp) as fi, open(outp, "w") as fo, open(outp + ".err", "w") as fe:
        rc = subprocess.run([FPLLL, "-a", "bkz", "-b", str(beta), "-nolll", "-f", "dd", "-s", SDEF,
                             "-bkzmaxloops", "2"],
                            stdin=fi, stdout=fo, stderr=fe, timeout=tmax).returncode
    print("cli rc", rc, round(time.time() - t0, 1), flush=True)
    return rc

import re
res = {}
for name, hf, eps, pat in (("pp", hpp, +1, "pp"), ("pm", hpm, -1, "pm")):
    Lat = build_lattice(hf, m2, q, eps)
    B = to_intmat(Lat); lll_reduction(B)
    write_fplll([[int(B[i, j]) for j in range(B.ncols)] for i in range(B.nrows)], f"toy2_{name}.fplll")
    run_cli(f"toy2_{name}.fplll", f"toy2_{name}_out.fplll", 50)
    rows = [[int(t) for t in ch.split()] for ch in re.findall(r"\[([^\[\]]+)\]", open(f"toy2_{name}_out.fplll").read()) if ch.split()]
    res[pat] = np.array(rows, dtype=np.int64)
    print(name, "minnorm2", min(int(np.dot(r, r)) for r in rows), flush=True)

def scan(rows, hf, eps, strict):
    out = []
    for v in rows:
        s2 = int(np.dot(v, v))
        if s2 > 120: continue
        u, w = v[:m2], v[m2:]
        for s in (1, -1):
            uu, ww = s * u, s * w
            if strict:
                okk = uu.min() >= 0 and uu.max() <= 2 and ww.min() >= 0 and ww.max() <= 2 \
                      and int(uu.sum()) == df and int(ww.sum()) == df
            else:
                okk = np.abs(uu).max() <= 1 and np.abs(ww).max() <= 1 \
                      and 3 <= sum(int(abs(x)) for x in uu) <= df and 3 <= sum(int(abs(x)) for x in ww) <= df
            if okk and member(s * v, hf, m2, q, eps):
                out.append((uu, ww))
    return out

cpp = scan(res["pp"], hpp, +1, True)
cpm = scan(res["pm"], hpm, -1, False)
print("cands", len(cpp), len(cpm), flush=True)
ok = False
for (a, ag) in cpp:
    for (b, bg) in cpm:
        if np.any(np.abs(a - b) > 2) or np.any((a + b) % 2): continue
        f0p = (a + b) // 2; f1p = (a - b) // 2
        if np.any((f0p < 0) | (f0p > 1)) or np.any((f1p < 0) | (f1p > 1)): continue
        if int(f0p.sum()) + int(f1p.sum()) != df: continue
        if np.any((ag + bg) % 2): continue
        g0p = (ag + bg) // 2; g1p = (ag - bg) // 2
        if np.any((g0p < 0) | (g0p > 1)) or np.any((g1p < 0) | (g1p > 1)): continue
        fp2 = np.concatenate([f0p, f1p]); gp2 = np.concatenate([g0p, g1p])
        if int(gp2.sum()) != dg: continue
        if not np.all(ringmul(fp2, hp, m, +1) % q == gp2 % q): continue
        print("GLUED f+ valid", flush=True)
        # overlap bits + decrypt (mirror t280_finish logic at toy scale)
        A2 = np.flatnonzero(fp2 == 1)
        K = len(A2)
        fvec = np.zeros(n, dtype=np.int64)
        for i in range(m):
            if fp2[i] == 2: fvec[i] = 1; fvec[m + i] = 1
            elif fp2[i] == 1: fvec[i] = 1
        rowsd = np.zeros((K, n), dtype=np.int64)
        for t, i in enumerate(A2):
            r1 = np.zeros(n); idx = (np.arange(n) + i) % n; r1[idx] = h
            r2 = np.zeros(n); idx2 = (np.arange(n) + m + i) % n; r2[idx2] = h
            rowsd[t] = (r2 - r1) % q
        base_g = conv(fvec, h, n) % q
        found = None
        for P in range(1 << K):
            bits = np.array([(P >> t) & 1 for t in range(K)], dtype=np.int64)
            G = (base_g + bits @ rowsd) % q
            if np.all((G == 0) | (G == 1)) and int(G.sum()) == dg:
                found = P; break
        if found is None:
            print("finish: no consistent f in 2^K (K=%d)" % K); continue
        fv = fvec.copy()
        for t in range(K):
            if (found >> t) & 1: fv[A2[t]] = 0; fv[m + A2[t]] = 1
        # decrypt using validated library path (gf2 unit solve on conv(f,ct))
        from t280_fold import gf2_solve_unit, conv512
        A = [xx % q for xx in conv512([int(z) for z in fv], [int(z) % q for z in ct], n)]
        B2 = [a & 1 for a in A]
        xb = gf2_solve_unit([int(z) & 1 for z in fv], B2, n)
        got = int(xb).to_bytes(n // 8, "big") if xb is not None else b""
        print("decrypted:", got, flush=True)
        if got.startswith(b"NNS{"):
            print("TOY2 FULL SUCCESS", flush=True); ok = True
        break
    if ok: break
print("TOY2 RESULT:", "OK" if ok else "FAIL", flush=True)

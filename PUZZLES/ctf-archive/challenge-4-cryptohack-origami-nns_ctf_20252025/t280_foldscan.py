# t280_foldscan.py — scan folded bases, glue ± parts, parity-decrypt.
# usage: python t280_foldscan.py            (uses t280_fp_cur.fplll / t280_fm_cur.fplll)
import sys, time, re, ast, json
sys.path.insert(0, ".")
import numpy as np
from t280_fold import load_real, make_folds, member, glue_and_decrypt

t0 = time.time()
def log(*a): print(round(time.time() - t0, 1), *a, flush=True)

n, q, m, df = 512, 127, 256, 35
h, ct = load_real()
hp, hm = make_folds(h)

def parse(path):
    raw = open(path).read()
    groups = re.findall(r"\[([^\[\]]+)\]", raw)
    rows = []
    for ch in groups:
        toks = ch.split()
        if toks: rows.append([int(t) for t in toks])
    assert all(len(r) == 2 * m for r in rows), (path, len(rows[0]) if rows else 0)
    return np.array(rows, dtype=np.int64)

def scan_plus(rows):
    cands = []
    for i in range(rows.shape[0]):
        v = rows[i]; s2 = int(v @ v)
        if s2 > 200: continue
        u, w = v[:m], v[m:]
        for s in (1, -1):
            uu, ww = s * u, s * w
            if uu.min() >= 0 and uu.max() <= 2 and ww.min() >= 0 and ww.max() <= 2 \
               and int(uu.sum()) == df and int(ww.sum()) == df:
                if member(s * v, hp, m, q, +1):
                    log(f"plus row{i} norm2={s2} PATTERN")
                    if not any(np.array_equal(c, uu) for c in cands): cands.append(uu)
    return cands

def scan_minus(rows):
    cands = []
    for i in range(rows.shape[0]):
        v = rows[i]; s2 = int(v @ v)
        if s2 > 200: continue
        u, w = v[:m], v[m:]
        for s in (1, -1):
            uu, ww = s * u, s * w
            if np.abs(uu).max() <= 1 and np.abs(ww).max() <= 1 \
               and 20 <= sum(int(abs(x)) for x in uu) <= df and 20 <= sum(int(abs(x)) for x in ww) <= df:
                if member(s * v, hm, m, q, -1):
                    log(f"minus row{i} norm2={s2} PATTERN")
                    if not any(np.array_equal(c, uu) for c in cands): cands.append(uu)
    return cands

pfile = sys.argv[1] if len(sys.argv) > 1 else "t280_fp_cur.fplll"
mfile = sys.argv[2] if len(sys.argv) > 2 else "t280_fm_cur.fplll"
Rp = parse(pfile); Rm = parse(mfile)
log("rows", Rp.shape, Rm.shape,
    "min norm2:", int(min(int(r @ r) for r in Rp)), int(min(int(r @ r) for r in Rm)))
cp = scan_plus(Rp)
cmm = scan_minus(Rm)
log("candidates:", len(cp), len(cmm))
if cp and cmm:
    done = False
    for a in cp[:6]:
        for b in cmm[:6]:
            fv, gv, flag = glue_and_decrypt(a, b, h, ct, m=m, q=q, n=n, log=log)
            if flag:
                open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
                open("FLAG_FOUND.txt", "w").write(flag.decode())
                log("FLAG:", flag.decode())
                done = True; break
        if done: break
    if not done: log("glue candidates present but no valid decrypt")
log("FOLDSCAN DONE")

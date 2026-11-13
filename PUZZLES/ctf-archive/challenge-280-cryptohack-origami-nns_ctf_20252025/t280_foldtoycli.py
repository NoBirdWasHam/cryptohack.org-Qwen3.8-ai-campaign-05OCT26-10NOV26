# t280_foldtoycli.py — toy end-to-end: plant n=256 NTRU, fold to dim-256 lattices,
# reduce with fplll CLI (dd), scan+glue+parity-decrypt, compare planted flag.
import sys, time, subprocess, os
sys.path.insert(0, ".")
import numpy as np, random
from t280_fold import ringmul, conv512, build_lattice, member, glue_and_decrypt

FPLLL = "~/tools/crypto-ctf/fplll-build/prefix3/bin/fplll.exe"
os.environ["PATH"] = "~/tools/msys64/ucrt64/bin;" + os.environ["PATH"]

rng = random.Random(99)
n, q, df, dg, dr, m = 256, 127, 9, 9, 4, 128
def rand01(d):
    v = np.zeros(n, dtype=np.int64); v[rng.sample(range(n), d)] = 1; return v
def cm(a, b): return conv512(a, b, n) % q
while True:
    f = rand01(df); g = rand01(dg)
    Tm = np.zeros((n, n), dtype=np.int64)
    for r_ in range(n):
        for i in range(n): Tm[r_, i] = f[(r_ - i) % n]
    M2 = np.concatenate([Tm % q, (g % q).reshape(n, 1)], axis=1)
    sing = False
    for col in range(n):
        piv = next((rr for rr in range(col, n) if M2[rr, col] % q), None)
        if piv is None: sing = True; break
        M2[[col, piv]] = M2[[piv, col]]
        inv = pow(int(M2[col, col]), -1, q)
        M2[col] = M2[col] * inv % q
        for rr in range(n):
            if rr != col and M2[rr, col] % q: M2[rr] = (M2[rr] - M2[rr, col] * M2[col]) % q
    if sing: continue
    h = M2[:, n]
    if np.all((cm(f, h) - g) % q == 0): break
flag_bytes = b"NNS{TOYCLI_FOLD_WORKS_012345678}"
assert len(flag_bytes) == n // 8, len(flag_bytes)
val = int.from_bytes(flag_bytes, "big")
mm = np.array([(val >> i) & 1 for i in range(n)], dtype=np.int64)
ct = (2 * cm(h, rng2 := rand01(dr)) + mm) % q
print("planted. true folded plus norm2:",
      int(((f[:m]+f[m:])**2).sum() + ((g[:m]+g[m:])**2).sum()))

h0, h1 = h[:m], h[m:]; hp = (h0 + h1) % q; hm = (h0 - h1) % q

def write_fplll(Mp, path):
    with open(path, "w") as fp:
        fp.write("[")
        for r_ in Mp:
            fp.write("[ " + " ".join(str(int(x)) for x in r_) + " ]")
        fp.write(" ]\n")

def run_cli(inp, outp, beta, tmax=600):
    t0 = time.time()
    sdef = "~/tools/crypto-ctf/fplll-build/prefix3/share/fplll/strategies/default.json"
    with open(inp) as fi, open(outp, "w") as fo, open(outp + ".err", "w") as fe:
        rc = subprocess.run([FPLLL, "-a", "bkz", "-b", str(beta), "-nolll", "-f", "dd", "-s", sdef],
                            stdin=fi, stdout=fo, stderr=fe, timeout=tmax).returncode
    print("cli rc", rc, round(time.time() - t0, 1), flush=True)
    return rc

import re
def parse(path):
    raw = open(path).read()
    groups = re.findall(r"\[([^\[\]]+)\]", raw)
    return np.array([[int(t) for t in ch.split()] for ch in groups if ch.split()], dtype=np.int64)

def scan_plus(rows):
    out = []
    for i in range(rows.shape[0]):
        v = rows[i]
        if int(v @ v) > 8 * (df + dg): continue
        for s in (1, -1):
            uu, ww = s * v[:m], s * v[m:]
            if uu.min() >= 0 and uu.max() <= 2 and ww.min() >= 0 and ww.max() <= 2 \
               and int(uu.sum()) == df and int(ww.sum()) == dg and member(s * v, hp, m, q, +1):
                out.append(uu)
    return out

def scan_minus(rows):
    out = []
    for i in range(rows.shape[0]):
        v = rows[i]
        if int(v @ v) > 8 * (df + dg): continue
        for s in (1, -1):
            uu, ww = s * v[:m], s * v[m:]
            if np.abs(uu).max() <= 1 and np.abs(ww).max() <= 1 \
               and sum(int(abs(x)) for x in uu) <= df and sum(int(abs(x)) for x in ww) <= dg \
               and member(s * v, hm, m, q, -1):
                out.append(uu)
    return out

Hp = build_lattice(hp, m, q, +1); Hm = build_lattice(hm, m, q, -1)
write_fplll(Hp, "toycli_p.fplll"); write_fplll(Hm, "toycli_m.fplll")
run_cli("toycli_p.fplll", "toycli_p_out.fplll", 45)
run_cli("toycli_m.fplll", "toycli_m_out.fplll", 45)
Rp = parse("toycli_p_out.fplll"); Rm = parse("toycli_m_out.fplll")
print("min norms:", int(min(int(r @ r) for r in Rp)), int(min(int(r @ r) for r in Rm)))
cp, cmm = scan_plus(Rp), scan_minus(Rm)
print("cands:", len(cp), len(cmm))
flag = None
done = False
for a in cp[:6]:
    for b in cmm[:6]:
        fv, gv, flag = glue_and_decrypt(a, b, h, ct, m=m, q=q, n=n, log=print)
        if flag: done = True; break
    if done: break
print("toy decrypted:", flag)
print("TOY CLI FOLD:", "FULL SUCCESS" if flag == flag_bytes else "FAILED")

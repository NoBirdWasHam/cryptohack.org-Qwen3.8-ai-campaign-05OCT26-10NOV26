# Full-size planted NTRU: n=512, q=127, df=dg=35. Plant (f,g), build the same
# lattice, CLI BKZ (FT from env) per stage in the chain, scan for the planted pair.
import subprocess, sys, time, os, re, ast, random
import numpy as np
t0 = time.time()
def log(*a): print(round(time.time()-t0, 1), *a, flush=True)

FT = os.environ.get("FT", "mpfr")
PREC = os.environ.get("PREC", "200")
FPLLL = r"~/tools/crypto-ctf/fplll-build/prefix2/bin/fplll.exe"
if not os.path.exists(r"~/tools/msys64/ucrt64/bin/libwinpthread-1.dll"):
    pass
os.environ["PATH"] = r"~/tools/msys64/ucrt64/bin;" + os.environ["PATH"]

n, q = 512, 127
rng = random.Random(4242)

def T(v):
    Mm = np.zeros((n, n), dtype=np.int64)
    for m in range(n):
        for i in range(n):
            Mm[m, i] = v[(m-i) % n]
    return Mm

def solve_modq(Amat, bvec):
    M2 = np.concatenate([Amat % q, (bvec % q).reshape(n, 1)], axis=1).astype(np.int64)
    for col in range(n):
        piv = next((rr for rr in range(col, n) if M2[rr, col] % q), None)
        if piv is None: return None
        M2[[col, piv]] = M2[[piv, col]]
        inv = pow(int(M2[col, col]), -1, q)
        M2[col] = (M2[col] * inv) % q
        colv = M2[:, col].copy()
        for rr in range(n):
            if rr != col and colv[rr]:
                M2[rr] = (M2[rr] - colv[rr] * M2[col]) % q
    return M2[:, n]

def rand01(d):
    v = np.zeros(n, dtype=np.int64)
    v[rng.sample(range(n), d)] = 1
    return v

f = g = h = None
while f is None:
    ft = rand01(35); gt = rand01(35)
    hh = solve_modq(T(ft), gt)
    if hh is not None:
        f, g, h = ft, gt, hh
log("planted f,g; wt", int(f.sum()), int(g.sum()))
with open("toy512_truth.json", "w") as fp:
    import json; json.dump({"f": f.tolist(), "g": g.tolist()}, fp)

d = 2*n
rows = []
for i in range(n):
    e = np.zeros(n, dtype=np.int64); e[i] = 1
    s = np.zeros(n, dtype=np.int64)
    for m in range(n): s[m] = h[(m-i) % n]
    rows.append(np.concatenate([e, s]))
for i in range(n):
    e = np.zeros(n, dtype=np.int64); e[i] = q
    rows.append(np.concatenate([np.zeros(n, dtype=np.int64), e]))
cur = "toy512_cur.fplll"
with open(cur, "w") as fp:
    fp.write("[")
    for r_ in rows:
        fp.write("[ " + " ".join(str(int(x)) for x in r_) + " ]")
    fp.write(" ]\n")
log("wrote", cur, os.path.getsize(cur))

def parse(out):
    rws = []
    for chunk in out.replace("\n", " ").strip().split("] ["):
        chunk = chunk.strip().lstrip("[").rstrip("]").replace("]", " ")
        toks = chunk.split()
        if toks: rws.append([int(t) for t in toks])
    return rws

planted = [int(x) for x in f] + [int(x) for x in g]
for stage in (20, 25, 30):
    t1 = time.time()
    p = subprocess.run([FPLLL, "-a", "bkz", "-b", str(stage), "-nolll", "-f", FT,
                        "-p", PREC, "-bkzmaxtime", "1500", "-bkzdumpgso",
                        f"gso512_{stage}.json"],
                       input=open(cur).read(), capture_output=True, text=True, timeout=4000)
    log("stage", stage, "rc", p.returncode, round(time.time()-t1, 1), "s",
        p.stderr[:120] if p.returncode else "")
    if p.returncode != 0 or not p.stdout.strip():
        log("STAGE-FAIL"); sys.exit(2)
    open(cur, "w").write(p.stdout)
    rws = parse(p.stdout)
    mn = min(sum(c*c for c in r) for r in rws)
    found = any(r == planted or [-x for x in r] == planted for r in rws)
    log("stage", stage, "min row norm2", mn, "PLANTED FOUND:", found, flush=True)
    if found:
        print("TOY512_SOLVED")
        break
log("TOY512 DONE")

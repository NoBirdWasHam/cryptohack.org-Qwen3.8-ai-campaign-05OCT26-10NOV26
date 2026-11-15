# Pipeline: M_lll checkpoint -> fplll CLI staged BKZ -> scan rows -> parity decrypt.
# Native ucrt fplll has gmp+mpfr; dodges the fpylll-wheel float64-only crash.
import subprocess, sys, time, os, re, ast
os.chdir(os.path.dirname(os.path.abspath(__file__)))
FPLLL = r"C:\msys64\ucrt64\bin\fplll.exe"
n, q = 512, 127
d = 2 * n
T0 = time.time()
def log(*a): print(round(time.time() - T0), *a, flush=True)

txt = open("output.txt").read()
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))

def cm(a, b):
    o = [0] * n
    nz = [(j, bj) for j, bj in enumerate(b) if bj]
    for i, ai in enumerate(a):
        if ai:
            for j, bj in nz:
                o[(i + j) % n] += ai * bj
    return o

def gf2_solve_unit(fbits, B):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c - i) % n] & 1: bits |= 1 << i
        rows.append([bits, B[c] & 1])
    piv = {}
    for r in rows:
        while r[0]:
            col = (r[0] & -r[0]).bit_length() - 1
            if col in piv:
                r[0] ^= piv[col][0]; r[1] ^= piv[col][1]
            else:
                piv[col] = r; break
        if not r[0] and r[1]:
            return None
    x = 0
    for col in range(n - 1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        val = t
        rest = bits & ~(1 << col)
        while rest:
            c = (rest & -rest).bit_length() - 1
            val ^= (x >> c) & 1
            rest &= rest - 1
        if val: x |= 1 << col
    return x

def try_f(fvec, gvec, tag):
    if sum(abs(c) for c in fvec) + 2 * sum(abs(c) for c in gvec) >= q: return False
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

def scan(tag, rows):
    at = 0
    for i, v in enumerate(rows):
        s = sum(c * c for c in v)
        if s > 200: continue
        at += 1
        f0, g0 = v[:n], v[n:]
        try_f(f0, g0, f"{tag} r{i} n2={s}")
        try_f([-c for c in f0], [-c for c in g0], f"{tag} r{i} neg")
        try_f(g0, f0, f"{tag} r{i} sw")
        try_f([-c for c in g0], [-c for c in f0], f"{tag} r{i} swneg")
    log("scan", tag, "tried", at, "rows; min norm2",
        min(sum(c * c for c in v) for v in rows))

def read_lat(path):
    rows = []
    with open(path) as f:
        f.readline()  # dim line
        for line in f:
            t = line.split()
            if len(t) == d:
                rows.append([int(x) for x in t])
    assert len(rows) == d, (path, len(rows))
    return rows

def write_lat(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(f"{d} {d}\n")
        for v in rows:
            f.write(" ".join(map(str, v)) + "\n")
    os.replace(tmp, path)

# seed from checkpoint
if not os.path.exists("cur.txt"):
    import gzip
    with gzip.open("M_lll.txt.gz", "rt") as g, open("cur.txt.tmp", "w") as f:
        f.write(f"{d} {d}\n")
        for line in g:
            f.write(line)
    os.replace("cur.txt.tmp", "cur.txt")
    log("exported checkpoint -> cur.txt")

scan("lll", read_lat("cur.txt"))
for k in (20, 25, 30, 40):
    out = f"red{k}.txt"
    if not os.path.exists(out):
        log("fplll -b", k, "start")
        t0 = time.time()
        r = subprocess.run([FPLLL, "-b", str(k), "-t", "1500", "-c", "0.99", "cur.txt"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            log("fplll k", k, "FAILED rc=", r.returncode, r.stderr[:200])
            continue
        with open(out + ".tmp", "w") as f: f.write(r.stdout)
        os.replace(out + ".tmp", out)
        log("fplll k", k, "done", round(time.time() - t0), "s")
    rows = read_lat(out)
    scan("k" + str(k), rows)
    write_lat("cur.txt", rows)
log("NO FLAG YET")

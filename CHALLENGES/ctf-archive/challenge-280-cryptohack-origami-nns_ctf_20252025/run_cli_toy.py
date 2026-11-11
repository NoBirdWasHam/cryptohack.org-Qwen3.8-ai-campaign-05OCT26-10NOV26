# Engine ladder gate: run fplll CLI on the toy NTRU lattice, check planted (f,g) found.
import subprocess, json, sys, time
FPLLL = r"~/tools/crypto-ctf/fplll-build/prefix2/bin/fplll.exe"
truth = json.load(open("toy64_truth.json"))
planted = truth["f"] + truth["g"]
lat = open("toy64.fplll").read()

def parse(out):
    rows = []
    for chunk in out.replace("\n", " ").split("] ["):
        chunk = chunk.strip().lstrip("[").rstrip("]").replace("]", " ")
        toks = chunk.split()
        if toks:
            try:
                rows.append([int(t) for t in toks])
            except ValueError:
                print("PARSE-TOK-ERR", toks[:8]); return None
    return rows

for name, extra in [
    ("default", []),
    ("dd", ["-f", "dd"]),
    ("mpfr200", ["-f", "mpfr", "-p", "200"]),
    ("longdouble", ["-f", "longdouble"]),
]:
    t0 = time.time()
    p = subprocess.run([FPLLL, "-a", "bkz", "-b", "20", "-bkzmaxtime", "60"] + extra,
                       input=lat, capture_output=True, text=True, timeout=180)
    rows = parse(p.stdout)
    found = None
    if rows:
        for r in rows:
            if len(r) == len(planted):
                if r == planted: found = "+"
                elif [-x for x in r] == planted: found = "-"
    print(name, "rc", p.returncode, "rows", None if rows is None else len(rows),
          "FOUND", found, round(time.time()-t0, 1), "s", flush=True)
    if p.returncode != 0:
        print("  stderr:", p.stderr[:200], flush=True)

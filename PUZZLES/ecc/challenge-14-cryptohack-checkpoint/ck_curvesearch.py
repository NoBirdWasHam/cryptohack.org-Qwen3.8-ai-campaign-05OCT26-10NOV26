"""Find twist curves y^2=x^3+ax+b' (P-256 a) with smooth order part.
Python generates b candidates; PARI does ellcard (SEA) + factor(n, 10^6);
Python builds smooth part m (primes<=10^6, cap 2^21, need >=2^19).
Output: ck_curves.json list of {b, n, m, fac}."""
import subprocess, json, random, sys

P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
A = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
GP = "~/tools/gp64.exe"
NCAND = int(sys.argv[1]) if len(sys.argv) > 1 else 60
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1

rng = random.Random(SEED)
cands = [rng.randrange(1, P) for _ in range(NCAND)]
bs_list = ",".join(str(b) for b in cands)

# gp pitfalls: top-level multi-statement for-bodies need if(1, ...) idiom; LF-only file.
gp = f"""default(parisizemax, 1<<31);
p = {P};
a = {A};
bs = [{bs_list}];
for(i=1, #bs, if(1, E = ellinit([0,0,0,Mod(a,p),Mod(bs[i],p)]); n = ellcard(E); c = factor(n, 10^6); s = Str("@", bs[i], " ", n); for(j=1, matsize(c)[1], s = Str(s, " ", c[j,1], ":", c[j,2])); print(s);));
"""
open("csearch.gp", "w", newline="\n").write(gp.replace("\r", ""))
r = subprocess.run([GP, "-f", "-q", "csearch.gp"], capture_output=True, text=True, timeout=1700)
out = r.stdout.replace("\\\n", "")
toks = out.split()
recs = []
cur = None
for t in toks:
    if t.startswith("@"):
        if cur and len(cur) >= 2:
            recs.append((int(cur[0]), int(cur[1]), cur[2:]))
        cur = [t[1:]] if len(t) > 1 else []
    elif cur is not None:
        cur.append(t)
if cur and len(cur) >= 2:
    recs.append((int(cur[0]), int(cur[1]), cur[2:]))
recs = [(b, n, [tuple(map(int, pe.split(":"))) for pe in fac if ":" in pe]) for b, n, fac in recs]
print("curves parsed:", len(recs), "stderr:", r.stderr[:200])

CAP = 1 << 21
good = []
for b, n, fac in recs:
    m = 1; used = []
    for l, e in sorted(fac, key=lambda x: -x[0].bit_length()):
        if l >= P: continue
        pe = l ** e
        while pe > 1 and m * pe > CAP:
            pe //= l
        if pe > 1 and m * pe <= CAP:
            m *= pe; used.append((l, pe))
    if m >= 1 << 19:
        good.append({"b": b, "n": n, "m": m, "fac": used})
        print(f"b={b%10**8}... m bits={m.bit_length()} nbits={n.bit_length()}")
try:
    prev = json.load(open("ck_curves.json"))
except Exception:
    prev = []
seen = {(g["b"], g["m"]) for g in prev}
prev += [g for g in good if (g["b"], g["m"]) not in seen]
json.dump(prev, open("ck_curves.json", "w"))
print("total good curves:", len(prev))

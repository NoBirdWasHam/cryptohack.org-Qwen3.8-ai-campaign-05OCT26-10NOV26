# LIVE: full banner + factor n via mixed-query gcd clustering
import socket, sys, random, re, json, itertools
from math import gcd

HOST, PORT = "archive.cryptohack.org", 56048

class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=30)
        self.f = self.s.makefile("rwb")
    def line(self):
        b = self.f.readline()
        if not b: raise EOFError("closed")
        return b.decode(errors="replace").rstrip("\r\n")
    def banner_full(self):
        out = []
        for _ in range(4):
            out.append(self.line())
        import select
        rd, _, _ = select.select([self.s], [], [], 2)
        out.append("EXTRA" if rd else "no-extra")
        return out
    def query(self, r, s, t):
        self.f.write(f"{r},{s},{t}\n".encode()); self.f.flush()
        while True:
            ln = self.line()
            if "Something wrong" in ln: return None
            m = re.match(r".*?r = (-?\d+)", ln)
            if m:
                rp = int(m.group(1))
                sp = int(re.search(r"s = (-?\d+)", self.line()).group(1))
                tp = int(re.search(r"t = (-?\d+)", self.line()).group(1))
                return rp, sp, tp

random.seed()
c = Conn()
bn = c.banner_full()
print("BANNER LINES:", [l[:80] for l in bn], flush=True)
print("banner line4 full:", bn[3][:200], flush=True)
ef = {}
for k, l in zip(("r", "s", "t"), bn[1:4]):
    ef[k] = int(re.search(rf"{k} = (-?\d+)", l).group(1))
print("flag enc r bits:", ef["r"].bit_length(), "s:", ef["s"], "t:", ef["t"], flush=True)

pairs = []
tries = 0
while len(pairs) < 14 and tries < 200:
    tries += 1
    r = random.randrange(2**1000, 2**1020)  # safely < n for either key size
    res = c.query(r, 1, 1)
    if res is None: continue
    rp, sp, tp = res
    if rp == r: continue  # clean query, no info beyond QR-both
    pairs.append((r, rp))

print(f"got {len(pairs)} diffs in {tries} queries", flush=True)
facs = {}
for (i, a), (j, b) in itertools.combinations(enumerate(pairs), 2):
    g = gcd(abs(a[1]-a[0]), abs(b[1]-b[0]))
    if g > 10**30:
        facs[g] = facs.get(g, 0) + 1
top = sorted(facs.items(), key=lambda kv: -kv[1])[:10]
for g, cnt in top:
    print("cluster", g.bit_length(), "bits, count", cnt, flush=True)
json.dump({"banner_s": ef["s"], "banner_t": ef["t"], "banner_r": str(ef["r"]),
           "pairs": [[str(a), str(b)] for a, b in pairs],
           "clusters": [[str(g), c] for g, c in top]}, open("live1.json", "w"))
print("saved live1.json", flush=True)

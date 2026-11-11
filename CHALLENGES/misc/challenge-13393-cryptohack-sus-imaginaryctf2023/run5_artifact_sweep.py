# Artifact sweep: mine ALL captured big integers in cryptohack_org tree,
# pairwise-gcd vs sus n (shared p/q/r reuse fingerprint). Also planted-toy validation.
import os, re, sys, math
from gmpy2 import gcd

ROOT = r"~/Practice_runs/cryptohack_org"
NUM = re.compile(rb"\d{80,}")  # >= ~26 decimal digits *? keep >=80 digits (266+ bits)

def load_sus():
    ns = {}
    exec(open(os.path.join(ROOT, "challenge-13393-cryptohack-sus-imaginaryctf2023", "output.txt")).read(), ns)
    return ns["n"], ns["e"], ns["c"]

def harvest():
    pool = {}
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.lower().endswith((".txt", ".json", ".html", ".log", ".md", ".gp", ".py", ".csv")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(p) > 40 * 1024 * 1024:
                    continue
                with open(p, "rb") as f:
                    data = f.read()
            except Exception:
                continue
            for m in NUM.finditer(data):
                s = m.group()
                # strip leading zeros; require odd & > 2^200 (candidate RSA-grade ints)
                try:
                    v = int(s)
                except Exception:
                    continue
                if 200 <= v.bit_length() <= 20000 and v & 1:
                    pool.setdefault(v, set()).add(os.path.relpath(p, ROOT))
    return pool

def main():
    n, e, c = load_sus()
    pool = harvest()
    print("pool size:", len(pool), "files scanned walk done")
    hits = []
    for v, srcs in pool.items():
        if v == n:
            continue
        g = gcd(n, v)
        if 1 < g < n:
            hits.append((g, v, sorted(srcs)[:3]))
            print("!!! SHARED FACTOR gcd=", g.bit_length(), "b from", sorted(srcs)[:3])
    print("gcd-sweep done. hits:", len(hits))
    # also gcd(c, pool) sanity and n vs n family dedupe
    dup = sum(1 for v in pool if v == n)
    print("copies of n in pool:", dup)

# planted-artifact validation of machinery (toy: rehost reused r)
def toy():
    import random
    rnd = random.Random(42)
    def bp(bits):
        while True:
            x = rnd.getrandbits(bits) | (1 << (bits - 1)) | 1
            if pow(2, x // 2, x) != 0 and isprob(x):
                return x
    def isprob(x):
        if x % 2 == 0: return x == 2
        d = x - 1; s = 0
        while d % 2 == 0: d //= 2; s += 1
        for a in (2, 3, 5, 7, 11):
            y = pow(a, d, x)
            if y in (1, x - 1): continue
            for _ in range(s - 1):
                y = y * y % x
                if y == x - 1: break
            else: return False
        return True
    p1 = bp(80); q1 = p1*p1+p1+1
    while not isprob(q1): p1 = bp(80); q1 = p1*p1+p1+1
    r1 = bp(240)
    n1 = p1*q1*r1
    # rehost instance: shared r (artifact!), fresh p',q'
    p2 = bp(80); q2 = p2*p2+p2+1
    while not isprob(q2): p2 = bp(80); q2 = p2*p2+p2+1
    n2 = p2*q2*r1
    g = gcd(n1, n2)
    print("TOY planted shared-r: gcd bitlen", g.bit_length(), "== r?", g == r1)
    # biased-generation fingerprint toy: p with fixed top 20 bits -> detectable via interval pin? just show gcd machinery works.
    assert g == r1

toy()
main()

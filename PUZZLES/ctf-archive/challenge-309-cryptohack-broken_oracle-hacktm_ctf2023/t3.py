
import sys, random, itertools
sys.path.insert(0, ".")
import server, gmpy2
from Crypto.Util.number import bytes_to_long, long_to_bytes
from math import gcd

random.seed(7)
pub, priv = server.genkey(512)
n, c = pub.n, pub.c
flag = b"flag{test_flag_local}"
while len(flag) < 120: flag += b"\x00"
m = bytes_to_long(flag)
encf = server.encrypt(m, pub)

random.seed(99)
diffs = []
for _ in range(40):
    if len(diffs) >= 8: break
    r = random.randrange(1, n)
    for s in (1, -1):
        try:
            mm = server.decrypt(server.Enc(r, s, 1), pub, priv)
            e2 = server.encrypt(mm, pub)
            diffs.append((r, e2.r, s)); break
        except Exception: pass

for i,(r,rp,s) in enumerate(diffs):
    dd = rp - r
    print(i, "gcd(d,n)=", gcd(abs(dd), n) == n and "n" or (gcd(abs(dd),n) in (priv.p,priv.q) and ("p" if gcd(abs(dd),n)==priv.p else "q") else gcd(abs(dd),n)))
# cluster: same-side pairs share a prime
cand = {}
for (i,a),(j,b) in itertools.combinations(enumerate(diffs),2):
    g = gcd(abs(a[1]-a[0]), abs(b[1]-b[0]))
    if g > 10**6:
        cand.setdefault(g, []).append((i,j))
for g, prs in cand.items():
    print("cluster gcd bits", g.bit_length(), "divides n?", n % g == 0, prs)
    if n % g == 0 and g not in (1,n):
        fac = g if n//g > g else n//g
        # actually g may be exactly p or q
        for f in (g, n//g):
            if gmpy2.is_prime(f):
                other = n//f
                enc = encf
                mps = server.solve_quad(enc.r, c, f); mqs = server.solve_quad(enc.r, c, other)
                ms=[]
                for mp in mps:
                    for mq in mqs:
                        m2 = server.crt(mp, f, mq, other)
                        if gmpy2.jacobi(m2, n) == enc.s: ms.append(m2)
                rec = max(ms) if enc.t==1 else min(ms)
                print("try f bits", f.bit_length(), "->", long_to_bytes(rec)[:40])

# FULL SOLVE: factor via gcd clusters, recover c via t-pair sum/product formula, decrypt flag
import sys, random, re, socket
from math import gcd
sys.path.insert(0, ".")

def solve_quad(r, c, p):
    def mod(poly):
        if poly[2] == 0: return poly
        poly[1] = (poly[1] + poly[2]*r) % p
        poly[0] = (poly[0] - poly[2]*c) % p
        poly[2] = 0
        return poly
    def prod(a, b):
        return mod([a[0]*b[0] % p, (a[1]*b[0]+a[0]*b[1]) % p, a[1]*b[1] % p])
    exp = (p-1)//2
    res, cur = [1,0,0], [0,1,0]
    while True:
        if exp % 2: res = prod(res, cur)
        exp //= 2
        if exp == 0: break
        cur = prod(cur, cur)
    a1 = (-(res[0]-1) * pow(res[1], -1, p)) % p
    return (a1, (r - a1) % p)

def crt(r1, n1, r2, n2):
    g, x, y = gmpy2.gcdext(n1, n2)
    assert g == 1
    return int((n1*x*r2 + n2*y*r1) % (n1*n2))

import gmpy2
from Crypto.Util.number import long_to_bytes

def decrypt_full(rf, sf, tf, c, p, q):
    n = p*q
    mps, mqs = solve_quad(rf, c, p), solve_quad(rf, c, q)
    ms = []
    for mp in mps:
        for mq in mqs:
            m = crt(mp, p, mq, q)
            if gmpy2.jacobi(m, n) == sf: ms.append(m)
    assert len(ms) == 2, ms
    m1, m2 = sorted(ms)
    return m1 if tf == 0 else m2

def c_from_pair(r, rp0, rp1, prime):
    S = (rp0 + rp1) % prime
    P = (rp0 * rp1) % prime
    d = (S - r) % prime
    den = (S - 2*r) % prime
    if d == 0 or den == 0: return None
    num = (P - r*d) % prime
    return num * r % prime * d % prime * pow(den*den % prime, -1, prime) % prime

class Conn:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=60)
        self.f = self.s.makefile("rwb")
    def line(self):
        b = self.f.readline()
        if not b: raise EOFError("closed")
        return b.decode(errors="replace").rstrip("\r\n")
    def banner(self):
        out = [self.line() for _ in range(4)]
        ef = {}
        for k, l in zip(("r","s","t"), out[1:4]):
            ef[k] = int(re.search(rf"{k} = (-?\d+)", l).group(1))
        return ef
    def query(self, r, s, t):
        self.f.write(f"{r},{s},{t}\n".encode()); self.f.flush()
        while True:
            ln = self.line()
            if "Something wrong" in ln: return None
            m = re.match(r".*?r = (-?\d+)", ln)
            if m:
                rp = int(m.group(1))
                int(re.search(r"s = (-?\d+)", self.line()).group(1))
                int(re.search(r"t = (-?\d+)", self.line()).group(1))
                return rp

def run_local():
    import server
    random.seed(42)
    pub, priv = server.genkey(512)
    n, c = pub.n, pub.c
    flag = b"crypto{local_test_flag_123}"
    while len(flag) < 255: flag += b"\x99"
    m = int.from_bytes(flag, "big")
    encf = server.encrypt(m, pub)
    pairs, facs = [], {}
    tries = 0
    while len(pairs) < 10 and tries < 100:
        tries += 1
        r = random.randrange(2**500, 2**510)
        rp = _Q(pub)(r, 1, 1) if False else _query_local(pub, priv, r, 1, 1)
        if rp is None or rp == r: continue
        pairs.append((r, rp))
    def _query_local(pub, priv, r, s, t):
        try:
            mm = server.decrypt(server.Enc(r, s, t), pub, priv)
            return server.encrypt(mm, pub).r
        except Exception:
            return None
    for (i,a),(j,b) in itertools.combinations(enumerate(pairs),2):
        g = gcd(abs(a[1]-a[0]), abs(b[1]-b[0]))
        if g > 2**300: facs[g] = facs.get(g,0)+1
    import itertools
    cl = sorted(facs.items(), key=lambda kv:-kv[1])
    p = cl[0][0]; q = n//p
    print("local factors ok:", p==priv.p or p==priv.q)
    return pub, priv

def run_live(host, port):
    random.seed()
    cn = Conn(host, port)
    ef = cn.banner()
    print("flag enc:", ef["s"], ef["t"], "r bits", ef["r"].bit_length(), flush=True)
    pairs, facs = [], {}
    tries = 0
    while len(pairs) < 12 and tries < 150:
        tries += 1
        r = random.randrange(2**1000, 2**1020)
        rp = cn.query(r, 1, 1)
        if rp is None or rp == r: continue
        pairs.append((r, rp))
    import itertools
    for (i,a),(j,b) in itertools.combinations(enumerate(pairs),2):
        g = gcd(abs(a[1]-a[0]), abs(b[1]-b[0]))
        if g > 2**600: facs[g] = facs.get(g,0)+1
    cl = sorted(facs.items(), key=lambda kv:-kv[1])
    print("clusters:", [(g.bit_length(), cnt) for g,cnt in cl[:5]], flush=True)
    p = cl[0][0]
    # ensure p divides an exact factorization: use two distinct clusters or n=p*q
    q = cl[1][0] if len(cl) > 1 and cl[1][0] != p else None
    # better: p*q should make all diffs consistent; verify gcd(p,q)==1
    if q is None or gcd(p, q) != 1:
        print("factor cluster problem"); return
    print("p bits", p.bit_length(), "q bits", q.bit_length(), flush=True)
    cp = cq = None
    tries = 0
    while (cp is None or cq is None) and tries < 120:
        tries += 1
        r = random.randrange(2**1000, 2**1020)
        r0 = cn.query(r, 1, 0); r1 = cn.query(r, 1, 1)
        if r0 is None or r1 is None: continue
        if r0 == r1: continue
        fp = c_from_pair(r, r0, r1, p)
        fq = c_from_pair(r, r0, r1, q)
        if fp is not None:
            if cp is None: cp = fp; print("c mod p found, tries", tries, flush=True)
            elif fp != cp: cp = None; print("p mismatch retry", flush=True)
        if fq is not None:
            if cq is None: cq = fq; print("c mod q found, tries", tries, flush=True)
            elif fq != cq: cq = None; print("q mismatch retry", flush=True)
        # allow either order: if p-side gave cq first, keep consistent
    print("cp bits", cp.bit_length(), "cq bits", cq.bit_length(), flush=True)
    c = crt(cp, p, cq, q)
    print("jacobi(c,p)", gmpy2.jacobi(c, p), "jacobi(c,q)", gmpy2.jacobi(c, q), flush=True)
    m = decrypt_full(ef["r"], ef["s"], ef["t"], c, p, q)
    bts = long_to_bytes(m)
    print("DECRYPTED:", bts[:120], flush=True)
    mm = re.search(rb"crypto\{[^}]*\}", bts)
    print("FLAG:", mm.group(0).decode() if mm else "NOT FOUND", flush=True)
    open("live2_out.txt", "w").write(str(bts))

if __name__ == "__main__":
    import itertools
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        run_live("archive.cryptohack.org", 56048)
    else:
        print("run with 'live' arg")

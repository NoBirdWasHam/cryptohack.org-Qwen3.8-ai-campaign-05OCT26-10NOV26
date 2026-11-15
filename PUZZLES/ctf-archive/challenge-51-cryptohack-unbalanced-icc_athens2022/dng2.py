# Durfee-Nguyen EXACT (Asiacrypt 2000): polynomials reduced mod (yz - N) BEFORE vectorizing.
# primary: h_{m,j} = y^{a+j} f^m, j=0..t
# helpers: g_{k,i,b} = e^{m-k} x^i y^a z^b f^k (k<m, 1<=i<=m-k, b in {0,1})
#          h_{k,j}  = e^{m-k} y^{a+j} f^k (k<m, j=0..t)
# dim = (m+1)(m+t+1).  Root (k,p,q) of f=1+x(N+1-y-z) mod e, yz=N.
import sys, math, random, re
import gmpy2
from fpylll import IntegerMatrix, LLL

def pmul(p, q):
    r = {}
    for k1, v1 in p.items():
        for k2, v2 in q.items():
            k = (k1[0]+k2[0], k1[1]+k2[1], k1[2]+k2[2])
            r[k] = r.get(k, 0) + v1*v2
    return {k: v for k, v in r.items() if v}

def ppow(f, s):
    r = {(0,0,0): 1}
    for _ in range(s):
        r = pmul(r, f)
    return r

def reduce_yz(poly, N):
    out = {}
    for (u, v, w), c in poly.items():
        if v > 0 and w > 0:
            if v >= w:
                key = (u, v-w, 0); mult = N**w
            else:
                key = (u, 0, w-v); mult = N**v
        else:
            key = (u, v, w); mult = 1
        val = c*mult
        if val:
            out[key] = out.get(key, 0) + val
    return {k: v for k, v in out.items() if v}

def build_rows(N, e, m, t, a):
    A = N+1
    f = {(0,0,0): 1, (1,0,0): A, (1,1,0): -1, (1,0,1): -1}
    fp = {s: ppow(f, s) for s in range(m+1)}
    rows = []  # (poly, factor)
    for j in range(t+1):  # primary h_{m,j}
        rows.append((mon_pow_yz(fp[m], 0, a+j, 1)))
    for k in range(m):
        for i in range(1, m-k+1):
            for b in (0, 1):
                rows.append(mon_pow_yz(fp[k], i, a, b, e**(m-k)))
        for j in range(t+1):
            rows.append(mon_pow_yz(fp[k], 0, a+j, 0, e**(m-k)))
    return rows

def mon_pow_yz(fpoly, i, jj, b, factor=1):
    return reduce_yz({(u+i, v+jj, w+b): c*factor for (u,v,w), c in fpoly.items()}, 1) if factor == 1 else _red2(fpoly, i, jj, b, factor)

def _red2(fpoly, i, jj, b, factor):
    p = {(u+i, v+jj, w+b): c*factor for (u,v,w), c in fpoly.items()}
    return p  # reduction applied later with N

def build(N, e, m, t, a, X, Y, Z):
    A = N+1
    f = {(0,0,0): 1, (1,0,0): A, (1,1,0): -1, (1,0,1): -1}
    fp = {s: ppow(f, s) for s in range(m+1)}
    rows = []
    for j in range(t+1):
        rows.append(reduce_yz({(u, v+a+j, w): c for (u,v,w), c in fp[m].items()}, N))
    for k in range(m):
        for i in range(1, m-k+1):
            for b in (0, 1):
                rows.append(reduce_yz({(u+i, v+a, w+b): c*e**(m-k) for (u,v,w), c in fp[k].items()}, N))
        for j in range(t+1):
            rows.append(reduce_yz({(u, v+a+j, w): c*e**(m-k) for (u,v,w), c in fp[k].items()}, N))
    mons = sorted({k for p in rows for k in p})
    n = len(rows)
    M = IntegerMatrix(n, len(mons))
    for r, p in enumerate(rows):
        for ci, (u, v, w) in enumerate(mons):
            c = p.get((u, v, w), 0)
            if c:
                M[r, ci] = c * (X**u) * (Y**v) * (Z**w)
    return M, mons

def attack(N, e, m=5, t=2, a=None, verbose=True):
    if a is None: a = max(1, m//2)
    X = 1 << 300; Y = 1 << 256; Z = 1 << 768
    M, mons = build(N, e, m, t, a, X, Y, Z)
    LLL.reduction(M, delta=0.99)
    eb = e.bit_length()
    hbound = m*eb - 0.5*math.log2(max(len(mons), 2))
    cands = []
    for r in range(M.nrows):
        row = [int(M[r, c]) for c in range(M.ncols)]
        if all(v == 0 for v in row): continue
        nrm = max(abs(v).bit_length() for v in row if v)
        if nrm >= hbound + 2: continue
        poly = {}
        ok = True
        for ci, v in enumerate(row):
            if v:
                u, wa, wc = mons[ci]
                wgt = (X**u)*(Y**wa)*(Z**wc)
                if v % wgt: ok = False; break
                poly[(u, wa, wc)] = v // wgt
        if not ok: continue
        yform = all(wa >= wc for (u, wa, wc) in poly if wc)
        zform = all(wc >= wa for (u, wa, wc) in poly if wa)
        cands.append((nrm, poly, yform, zform))
    cands.sort(key=lambda z: z[0])
    if verbose:
        print(f"[m={m},t={t},a={a}] rows={M.nrows} mons={len(mons)} hbound={hbound:.1f} cands={len(cands)} nmin={cands[0][0] if cands else None}", flush=True)
    def to_uni(poly, yform):
        H = {}
        for (u, wa, wc), c in poly.items():
            if yform:
                key = (u, wa-wc); mult = N**wc
            else:
                key = (u, wc-wa); mult = N**wa
            H[key] = H.get(key, 0) + c*mult
        return {k: v for k, v in H.items() if v}
    unis = [(nrm, to_uni(p, yf), 'y' if yf else 'z') for (nrm, p, yf, zf) in cands if (yf or zf)]
    # direct gcd from constant terms of x-free candidates
    for nrm, h, form in unis:
        if max((u for u, v in h), default=0) == 0:
            c0 = h.get((0, 0), 0)
            if c0:
                g = int(gmpy2.gcd(N, abs(c0)))
                if 1 < g < N and N % g == 0:
                    if verbose: print(f"p|q from x-free const ({form}): {g.bit_length()}b")
                    return g
    from resultant_lib import resultant_x
    for i in range(len(unis)):
        for j in range(i+1, len(unis)):
            if unis[i][2] != unis[j][2]: continue
            h1, h2 = unis[i][1], unis[j][1]
            if h1 == h2: continue
            try:
                r = resultant_x(h1, h2)
            except Exception as ex:
                if verbose: print("res fail", repr(ex)[:80])
                continue
            if not r: continue
            for tag, val in (("c0", r.get(0, 0)), ("eval1", sum(r.values()))):
                if val:
                    g = int(gmpy2.gcd(N, abs(val)))
                    if 1 < g < N and N % g == 0:
                        if verbose: print(f"factor via gcd(res {tag}) {g.bit_length()}b pair {i},{j} form {unis[i][2]}")
                        return g
    return None

def synth(tries=None):
    random.seed(20261101)
    def rprime(bits):
        return int(gmpy2.next_prime(random.getrandbits(bits) | (1 << (bits-1)) | 1))
    p, q = rprime(256), rprime(768)
    N = p*q
    phi = (p-1)*(q-1)
    while True:
        d = rprime(300)
        if d > N**0.292: break
    e = int(pow(d, -1, phi))
    print("synth instance made", flush=True)
    if tries is None:
        tries = [(m, t, a) for m in (2,3,4,5) for t in (1,2,3) for a in (1,2,3)]
    for (m, t, a) in tries:
        try:
            g = attack(N, e, m=m, t=t, a=a)
        except Exception as ex:
            print("fail", m, t, a, repr(ex)[:100]); continue
        if g and N % g == 0:
            print(f"SYNTH OK m={m} t={t} a={a} exact={g == p}")
            return (m, t, a)
    print("SYNTH ALL FAIL")
    return None

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "real"
    if mode == "synth":
        r = synth()
        print("RESULT", r)
    else:
        txt = open("output.txt").read()
        N = int(re.search(r"N = 0x([0-9a-f]+)", txt).group(1), 16)
        e = int(re.search(r"e = 0x([0-9a-f]+)", txt).group(1), 16)
        c = int(re.search(r"c = 0x([0-9a-f]+)", txt).group(1), 16)
        g = None
        for (m, t, a) in [(3,1,2),(3,2,2),(4,2,2),(4,3,2),(5,2,2),(5,3,3),(5,4,3),(6,3,3),(6,4,3)]:
            try:
                g = attack(N, e, m=m, t=t, a=a)
            except Exception as ex:
                print("err", m, t, a, repr(ex)[:120], flush=True); continue
            if g: break
        if g:
            p, q = (g, N//g) if g < N//g else (N//g, g)
            phi = (p-1)*(q-1)
            d = int(pow(e, -1, phi))
            from Crypto.Util.number import long_to_bytes
            flag = long_to_bytes(pow(c, d, N))
            print("FLAG:", flag.decode(errors="replace"), flush=True)
            open("flag_found.txt", "w").write(flag.decode(errors="replace"))
        else:
            print("FAILED")

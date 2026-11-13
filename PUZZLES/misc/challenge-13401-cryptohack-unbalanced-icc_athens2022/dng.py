# Durfee-Nguyen trivariate Coppersmith (Asiacrypt 2000) — unbalanced RSA small-d.
# eq: f(x,y,z)=1+x((N+1)-y-z) = 0 mod e, root (k,p,q); special: y*z=N.
# Lattice (as described in Sun-Yang PKC'05 survey of DNG):
#   G: e^{m-s} x^i y^a z^b f^s, s=0..m-1, i=1..m-s, b in {0,1}
#   H: e^{m-s} y^{a+j} f^s,      s=0..m,   j=1..t
#   C: e^m
# a=m keeps y-deg >= z-deg so z -> N/y substitution stays polynomial.
# Vanishing polys -> H(x,y); resultant in x -> H(y) vanishes at p -> p | const term -> p = gcd(N, c0).
import sys, random
from math import isqrt
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

def mon_shift(p, dx, dy, dz, c):
    return {(a+dx, b+dy, c2+dz): v*c for (a,b,c2), v in p.items()}

def build(N, e, m, t, X, Y, Z, a=None):
    if a is None: a = m
    A = N+1
    f = {(0,0,0): 1, (1,0,0): A, (1,1,0): -1, (1,0,1): -1}
    fp = {s: ppow(f, s) for s in range(m+1)}
    efs = []
    for s in range(m):
        for i in range(1, m-s+1):
            for b in (0, 1):
                efs.append(mon_shift(fp[s], i, a, b, e**(m-s)))
    for s in range(m+1):
        for j in range(1, t+1):
            efs.append(mon_shift(fp[s], 0, a+j, 0, e**(m-s)))
    efs.append({(0,0,0): e**m})
    mons = sorted({k for p in efs for k in p})
    n = len(efs)
    M = IntegerMatrix(n, len(mons))
    for r, p in enumerate(efs):
        for cidx, (al, be, ga) in enumerate(mons):
            v = p.get((al, be, ga), 0)
            if v:
                M[r, cidx] = v * (X**al) * (Y**be) * (Z**ga)
    return M, mons, efs

def unscale(vec, mons):
    return None  # done inline (need X,Y,Z); see subs

def to_h(poly, mons, N, X, Y, Z):
    # P(x,y,z) -> H(x,y) with z=N/y ; returns {(alpha, deg): coeff} or None if z-deg > y-deg anywhere
    H = {}
    for (al, be, ga), v in poly.items():
        if be < ga:
            return None
        k = (al, be-ga)
        H[k] = H.get(k, 0) + v * (N**ga)
    return H

def resultant_x(h1, h2):
    # h: {(xdeg, ydeg): c} -> poly in x over Z[y]; Sylvester determinant via Bareiss on Z[y]
    def coeffs(h, dx):
        d = {}
        for (a, b), v in h.items():
            if a == dx: d[b] = v
        return d
    d1 = max((a for a, b in h1), default=0); d2 = max((a for a, b in h2), default=0)
    if d1 + d2 == 0:
        return {}
    m1 = max((b for a, b in h1), default=0); m2 = max((b for a, b in h2), default=0)
    M = d1 + d2
    # polys in y
    c1 = [coeffs(h1, i) for i in range(d1+1)]
    c2 = [coeffs(h2, i) for i in range(d2+1)]
    # Sylvester matrix entries = y-polys (dict deg->coeff); do poly arithmetic
    def padd(p, q):
        r = dict(p)
        for k, v in q.items():
            r[k] = r.get(k, 0) + v
        return {k: v for k, v in r.items() if v}
    def pmul1(p, q):
        r = {}
        for k1, v1 in p.items():
            for k2, v2 in q.items():
                r[k1+k2] = r.get(k1+k2, 0) + v1*v2
        return {k: v for k, v in r.items() if v}
    n = M
    rows = []
    for i in range(d2):
        row = [{}]*n
        for j in range(d1+1):
            row[i+j] = c1[j]
        rows.append(row)
    for i in range(d1):
        row = [{}]*n
        for j in range(d2+1):
            row[i+j] = c2[j]
        rows.append(row)
    # determinant over Z[y] via Laplace? use fraction-free Bareiss on y-poly ring
    import copy
    A = copy.deepcopy(rows)
    sign = 1
    prev = {0: 1}
    for k in range(n-1):
        # find pivot
        piv = None
        for r in range(k, n):
            if A[r][k]:
                piv = r; break
        if piv is None:
            return {0: 0}
        if piv != k:
            A[k], A[piv] = A[piv], A[k]; sign = -sign
        p = A[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                num = padd(pmul1(A[i][j], p), {0:0})
                for _ in [0]: pass
                num = pmul1(A[i][j], p)
                sub = pmul1(A[i][k], A[k][j])
                num = {kk: num.get(kk,0)-sub.get(kk,0) for kk in set(num)|set(sub)}
                num = {kk: v for kk, v in num.items() if v}
                if prev != {0: 1}:
                    # exact division by prev
                    dq, dr = [], []
                    # poly div num / prev
                    dn = sorted(num, reverse=True); dd = sorted(prev, reverse=True)
                    q = {}
                    rmap = dict(num)
                    while rmap and max(rmap) >= dd[0]:
                        hn = max(rmap); hd = max(prev)
                        if hn < hd: break
                        co = rmap[hn] // prev[hd]
                        sh = hn-hd
                        q[sh] = q.get(sh, 0) + co
                        for kd, vd in prev.items():
                            rmap[kd+sh] = rmap.get(kd+sh, 0) - co*vd
                        rmap = {k2: v2 for k2, v2 in rmap.items() if v2}
                    if rmap:
                        raise ZeroDivisionError("non-exact Bareiss")
                    num = q
                A[i][j] = num
        prev = p
    det = A[n-1][n-1] if A[n-1][n-1] else {}
    if sign < 0:
        det = {k: -v for k, v in det.items()}
    return det

def attack(N, e, m=2, t=3, a=None, verbose=True):
    X = 1 << 300; Y = 1 << 256; Z = 1 << 768
    M, mons, efs = build(N, e, m, t, X, Y, Z, a=a)
    LLL.reduction(M, delta=0.99)
    eb = e.bit_length()
    import math
    hbound = m*eb - 0.5*math.log2(max(len(mons), 2))  # bits: e^m/sqrt(w)
    hpolys = []
    for r in range(M.nrows):
        row = [M[r, c] for c in range(M.ncols)]
        if all(v == 0 for v in row):
            continue
        nrm = max(abs(v).bit_length() for v in row if v)
        if nrm >= hbound + 2:
            continue
        poly = {}
        okp = True
        for cidx, v in enumerate(row):
            if v:
                al, be, ga = mons[cidx]
                w = (X**al)*(Y**be)*(Z**ga)
                if v % w:
                    okp = False; break
                poly[(al, be, ga)] = v // w
        if not okp:
            continue
        h = to_h(poly, mons, N, X, Y, Z)
        if h and (max((al for al, b in h), default=0) >= 1 or len(h) > 1):
            hpolys.append((nrm, h))
    hpolys.sort(key=lambda z: z[0])
    if verbose:
        print(f"[m={m},t={t},a={a}] rows={M.nrows} mons={len(mons)} hbound={hbound:.1f} cands={len(hpolys)} norms={[h[0] for h in hpolys[:6]]}", flush=True)
    for nrm, h in hpolys:
        if max((al for al, b in h), default=0) == 0:
            c0 = h.get((0, 0), 0)
            if c0:
                g = int(gmpy2.gcd(N, abs(c0)))
                if 1 < g < N and N % g == 0:
                    if verbose: print(f"p from x-free vanishing const: {g.bit_length()}b")
                    return g
    for i in range(len(hpolys)):
        for j in range(i+1, len(hpolys)):
            h1, h2 = hpolys[i][1], hpolys[j][1]
            if h1 == h2:
                continue
            try:
                r = resultant_x(h1, h2)
            except Exception as ex:
                if verbose: print("resultant fail", repr(ex)[:100])
                continue
            if not r:
                continue
            for tag, val in (("c0", r.get(0, 0)), ("res(1)", sum(v for k, v in r.items()))):
                if val:
                    g = int(gmpy2.gcd(N, abs(val)))
                    if 1 < g < N and N % g == 0:
                        if verbose: print(f"p = gcd(N, {tag}) -> {g.bit_length()} bits [pair {i},{j} norms {hpolys[i][0]},{hpolys[j][0]}]")
                        return g
    return None

def synth_test(tries=((2,3,None),(3,4,None),(3,6,None),(4,6,None))):
    random.seed(20261101)
    def rprime(bits):
        x = random.getrandbits(bits) | (1 << (bits-1)) | 1
        return int(gmpy2.next_prime(x))
    p, q = rprime(256), rprime(768)
    N = p*q
    phi = (p-1)*(q-1)
    while True:
        d = rprime(300)
        if d > N**0.292: break
    e = int(pow(d, -1, phi))
    for (m, t, a) in tries:
        pr = attack(N, e, m=m, t=t, a=a)
        if pr and N % pr == 0:
            print(f"SYNTH OK m={m},t={t},a={a}: p recovered exactly = {pr == p}")
            return True
        print(f"SYNTH fail m={m},t={t},a={a} — escalating", flush=True)
    return False

if __name__ == "__main__":
    if sys.argv[1] == "synth":
        ok = synth_test()
        print("SYNTH RESULT:", ok)
        sys.exit(0 if ok else 1)
    import re
    txt = open("output.txt").read()
    N = int(re.search(r"N = 0x([0-9a-f]+)", txt).group(1), 16)
    e = int(re.search(r"e = 0x([0-9a-f]+)", txt).group(1), 16)
    c = int(re.search(r"c = 0x([0-9a-f]+)", txt).group(1), 16)
    print("bits:", N.bit_length(), e.bit_length(), c.bit_length())
    p = None
    for (m, t) in [(2,3),(3,4),(3,6),(4,6),(4,8)]:
        p = attack(N, e, m=m, t=t)
        if p: break
    if p:
        q = N // p
        phi = (p-1)*(q-1)
        d = int(pow(e, -1, phi))
        from Crypto.Util.number import long_to_bytes
        flag = long_to_bytes(pow(c, d, N))
        print("FLAG:", flag.decode(errors="replace"))
        open("flag_found.txt", "w").write(flag.decode(errors="replace"))
    else:
        print("FAILED")

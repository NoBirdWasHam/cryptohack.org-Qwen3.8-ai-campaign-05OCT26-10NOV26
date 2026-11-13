# RUN#3 first-principles DNG: work in reduced ring via F(x,y) = y*f(x,y,N/y)
#   F = y + (N+1)xy - x*y^2 - N*x ;  F(k,p) = p*f(k,p,q) = p*e*d == 0 mod e
# Rows: e^(m-s) * x^i y^j F^s , s=1..m, pivot monomial x^(i+s) y^(j+2s) (coeff (-1)^s monic)
# Row scaled diagonal bits: (m-s)*L + (i+s)*xb + (j+2s)*yb ; fits if slack = s*(L-xb-2yb) - i*xb - j*yb > 0
# det = prod diagonals if pivots distinct -> mean slack > ~log2(n)/2 => HG vanishing vectors.
import sys, math, random, re
import gmpy2
from fpylll import IntegerMatrix, LLL
from flint import fmpz_mat, fmpz

def pmul(p, q):
    r = {}
    for k1, v1 in p.items():
        for k2, v2 in q.items():
            k = (k1[0]+k2[0], k1[1]+k2[1])
            r[k] = r.get(k, 0) + v1*v2
    return {k: v for k, v in r.items() if v}

def Fpoly(N):
    return {(0,1): 1, (1,1): N+1, (1,2): -1, (1,0): -N}

def region_rows(N, e, m, xb, yb=256):
    L = math.log2(float(e))
    F_ = Fpoly(N)
    fp = {0: {(0,0): 1}}
    for s in range(1, m+1):
        fp[s] = pmul(fp[s-1], F_)
    cands = []
    for s in range(1, m+1):
        es = e**(m-s)
        for i in range(0, m+1):
            for j in range(0, 2*m+2):
                slack = s*(L - xb - 2*yb) - i*xb - j*yb
                if slack <= 0: continue
                poly = {}
                for (u,v), c in fp[s].items():
                    key = (u+i, v+j)
                    poly[key] = poly.get(key, 0) + c*es
                poly = {k: v for k, v in poly.items() if v}
                pivot = (i+s, j+2*s)
                diag = (m-s)*L + (i+s)*xb + (j+2*s)*yb
                cands.append((pivot, diag, s, i, j, poly))
    # resolve pivot collisions: keep min diag
    best = {}
    for piv, diag, s, i, j, poly in cands:
        if piv not in best or diag < best[piv][0]:
            best[piv] = (diag, s, i, j, poly)
    rows = sorted(best.values(), key=lambda r: r[0])
    return rows, fp

def build_matrix(rows, xb, yb):
    X = 1 << xb; Y = 1 << yb
    mons = sorted({k for (_, _, _, _, poly) in rows for k in poly},
                  key=lambda t: t[0]*xb + t[1]*yb)
    idx = {mm: ci for ci, mm in enumerate(mons)}
    n = len(rows)
    M = IntegerMatrix(n, len(mons))
    for r, (diag, s, i, j, poly) in enumerate(rows):
        for (u, v), c in poly.items():
            M[r, idx[(u, v)]] = c * (X**u) * (Y**v)
    return M, mons

def bl(x):
    x = abs(int(x))
    if x == 0: return 0
    b = x.bit_length()
    return b - 1 + math.log2(float(x >> (b-53)) / (1 << 53)) if b > 53 else math.log2(float(x))

def pivot_minor_det(M, rows, mons):
    """det of square submatrix on pivot columns (rows ordered by diag asc). Exact if triangular."""
    idx = {mm: ci for ci, mm in enumerate(mons)}
    order = sorted(range(len(rows)), key=lambda r: rows[r][0])
    pcols = [idx[(rows[r][2]+rows[r][1], rows[r][3]+2*rows[r][1])] for r in order]
    B = fmpz_mat(len(order), len(order),
                 [int(M[r, c]) for r in order for c in pcols])
    prod_diag = 1
    tri = True
    for a in range(len(order)):
        prod_diag *= abs(int(B[a, a]))
        for c in range(a):
            if int(B[a, c]) != 0:
                tri = False
    return int(B.det()), prod_diag, tri

def attack(N, e, m=3, xb=300, yb=256, verbose=True, kp=None):
    rows, _ = region_rows(N, e, m, xb, yb)
    M, mons = build_matrix(rows, xb, yb)
    n = M.nrows
    detv, prod_diag, tri = pivot_minor_det(M, rows, mons)
    L = math.log2(float(e))
    detb = bl(detv) / n
    margin = m*L - detb - 0.5*math.log2(n)
    if verbose:
        print(f"[m={m} xb={xb}] rows={n} mons={M.ncols} tri={tri} det^(1/n)={detb:.1f} proddiag^(1/n)={bl(prod_diag)/n:.1f} bound={m*L:.1f} margin={margin:.1f}", flush=True)
    if margin <= 0:
        return None
    LLL.reduction(M, delta=0.99)
    X = 1 << xb; Y = 1 << yb
    hbound = m*L - 0.5*math.log2(M.ncols)
    polys = []
    for r in range(n):
        rowv = [int(M[r, c]) for c in range(M.ncols)]
        if all(v == 0 for v in rowv): continue
        l2 = 0.5*bl(sum(v*v for v in rowv))
        if l2 >= hbound: continue
        poly = {}
        ok = True
        for ci, v in enumerate(rowv):
            if v:
                (u, vdeg) = mons[ci]
                wgt = (X**u)*(Y**vdeg)
                if v % wgt: ok = False; break
                poly[(u, vdeg)] = v // wgt
        if not ok: continue
        if kp is not None:
            k_, p_ = kp
            val = sum(c*(k_**u)*(p_**vdeg) for (u, vdeg), c in poly.items())
            if val != 0:
                if verbose: print(f"  row {r}: l2={l2:.0f} NONVANISH {bl(val):.0f}b", flush=True)
                continue
        polys.append((l2, poly))
    polys.sort(key=lambda z: z[0])
    if verbose: print(f"  vanishing polys below HG: {len(polys)}", flush=True)
    if len(polys) < 2:
        if verbose and polys: print("  first l2:", f"{polys[0][0]:.1f}", flush=True)
        return None
    from resultant_lib import resultant_x
    for i in range(min(len(polys), 8)):
        for j in range(i+1, min(len(polys), 8)):
            h1, h2 = polys[i][1], polys[j][1]
            if h1 == h2: continue
            try:
                r_ = resultant_x(h1, h2)
            except Exception as ex:
                if verbose: print("res fail", repr(ex)[:90], flush=True)
                continue
            if not r_: continue
            for tag in (0, 1):
                val = r_.get(0, 0) if tag == 0 else sum(r_.values())
                if val:
                    g = int(gmpy2.gcd(N, abs(val)))
                    if 1 < g < N and N % g == 0:
                        if verbose: print(f"  FACTOR via pair({i},{j}) {tag}: {g.bit_length()}b", flush=True)
                        return g
    return None

def synth(dbits=192, seed=20261101, ms=(3,4,5)):
    random.seed(seed)
    def rprime(bits):
        return int(gmpy2.next_prime(random.getrandbits(bits) | (1 << (bits-1)) | 1))
    p, q = rprime(256), rprime(768)
    N = p*q
    phi = (p-1)*(q-1)
    while True:
        d = rprime(dbits)
        if d > N**0.292 or dbits != 300: break
    e = int(pow(d, -1, phi))
    k_ = (d*e - 1)//phi
    print(f"synth d={dbits}b k={k_.bit_length()}b made", flush=True)
    for m in ms:
        try:
            g = attack(N, e, m=m, xb=dbits, kp=(k_, p))
        except Exception as ex:
            print("fail", m, repr(ex)[:120], flush=True); continue
        if g and N % g == 0:
            print(f"SYNTH d={dbits} OK m={m} exact={g in (p,q)}")
            return m
    print(f"SYNTH d={dbits} ALL FAIL")
    return None

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "gate192"
    if mode == "gate192":
        synth(dbits=192)
    elif mode == "synth300":
        synth(dbits=300)
    else:
        txt = open("output.txt").read()
        N = int(re.search(r"N = 0x([0-9a-f]+)", txt).group(1), 16)
        e = int(re.search(r"e = 0x([0-9a-f]+)", txt).group(1), 16)
        c = int(re.search(r"c = 0x([0-9a-f]+)", txt).group(1), 16)
        g = None
        for m in (3, 4, 5, 6):
            g = attack(N, e, m=m, xb=300)
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

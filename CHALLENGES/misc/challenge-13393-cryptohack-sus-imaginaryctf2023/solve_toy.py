# Bivariate Coppersmith (integer root) on f(x,y)=(x^2+x+1)y - n, root (p,r).
# Toy instance with same bit-ratios as real: p 60b, q~120b, r 180b => N 360b.
import sys, random
from fpylll import IntegerMatrix, LLL

def make_tooy():
    from Crypto.Util.number import getPrime, isPrime
    while True:
        p = getPrime(60)
        q = p*p + p + 1
        if isPrime(q): break
    while True:
        r = getPrime(180)
        if r != p and r != q: break
    return p, q, r

def region(name, m):
    rows = []
    for k in range(m+1):
        M = m - k
        pts = []
        if name == "triangle":   # i + 2j <= 2M
            for j in range(M+1):
                for i in range(2*M - 2*j + 1):
                    pts.append((i,j))
        elif name == "box":      # i<=M, j<=M
            for i in range(M+1):
                for j in range(M+1):
                    pts.append((i,j))
        elif name == "tri1":     # i + 2j <= M
            for j in range(M//2+1):
                for i in range(M - 2*j + 1):
                    pts.append((i,j))
        for (i,j) in pts: rows.append((k,i,j))
    return rows

def build_and_solve(N, X, Y, root, m, name):
    gens = region(name, m)
    t = len(gens)
    # polynomial monomials: f^k * x^i * y^j has x-deg <= 2k+i, y-deg <= k+j
    def f_coeffs(k, i, j, scale):
        # (x^2+x+1)^k * x^i * y^j * N^(m-k)
        Ns = pow(N, m-k)
        base = [1]  # coeffs of (x^2+x+1)^0 in x
        poly = [1,1,1]
        acc = {0: 1}
        for _ in range(k):
            na = {}
            for a,ca in acc.items():
                for e,cb in enumerate(poly):
                    na[a+e] = na.get(a+e,0) + ca*cb
            acc = na
        return [(a+i, j, ca*Ns) for a,ca in acc.items()]
    # collect monomial universe
    mons = set()
    rowdicts = []
    for (k,i,j) in gens:
        d = {}
        for (a,b,c) in f_coeffs(k,i,j,1):
            d[(a,b)] = c
            mons.add((a,b))
        rowdicts.append(d)
    mons = sorted(mons)
    idx = {mm:ii for ii,mm in enumerate(mons)}
    t = len(rowdicts); ncols = len(mons)
    if t > ncols:
        return None, "too many rows"
    A = IntegerMatrix(t, ncols)
    for ri,d in enumerate(rowdicts):
        for (a,b),c in d.items():
            A[ri, idx[(a,b)]] = c * pow(X,a) * pow(Y,b)
    LLL.reduction(A)
    # try top vectors: build g(x,y), check g(root)==0 over Z
    (px, ry) = root
    good = []
    for ri in range(min(t, 60)):
        coeffs = {}
        ok = True
        for ci in range(ncols):
            v = int(A[ri,ci])
            if v:
                (a,b) = mons[ci]
                s = pow(X,a)*pow(Y,b)
                if v % s: ok = False; break
                coeffs[(a,b)] = v // s
        if not ok: continue
        # value check with exact unscaled coeffs
        val = sum(c * pow(px,a) * pow(ry,b) for (a,b),c in coeffs.items() if c)
        nnz = sum(1 for c in coeffs.values() if c)
        good.append((ri, val==0, nnz))
        if val == 0 and nnz > 1:
            # not a multiple of f? test division by (x^2+x+1)y-N over rationals: just report
            pass
    return (A, mons, gens), good

if __name__ == "__main__":
    random.seed(1)
    p,q,r = make_tooy()
    N = p*q*r
    X, Y = 2**60, 2**180
    print("toy N bits", N.bit_length(), "p,q,r", p.bit_length(), q.bit_length(), r.bit_length(), flush=True)
    for name in ("triangle","box","tri1"):
        for m in (2,3,4):
            res = build_and_solve(N, X, Y, (p,r), m, name)
            if res[0] is None:
                print(name, m, res[1]); continue
            A, mons, gens = res[0]
            zs = res[1]
            nzero = sum(1 for (_,v,nz) in zs if v and nz>1)
            print(name, m, "t=",len(gens), "zero-at-root(nonzero poly) among top60:", nzero, flush=True)

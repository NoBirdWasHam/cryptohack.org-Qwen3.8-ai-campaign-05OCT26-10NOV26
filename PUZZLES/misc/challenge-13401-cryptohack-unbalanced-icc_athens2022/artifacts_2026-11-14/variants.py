"""Durfee-Nguyen ASIACRYPT 2000 trivariate Coppersmith lattice (YZ->N), tunable (m,t,a)."""
from fpylll import IntegerMatrix, LLL


def reduce_yz(poly, N):
    out = {}
    for (a, b, c), v in poly.items():
        d = min(b, c)
        m = (a, b - d, c - d)
        out[m] = out.get(m, 0) + v * (N ** d)
    return out

def mul_poly(p1, p2, N):
    out = {}
    for m1, v1 in p1.items():
        for m2, v2 in p2.items():
            m = (m1[0] + m2[0], m1[1] + m2[1], m1[2] + m2[2])
            out[m] = out.get(m, 0) + v1 * v2
    return reduce_yz(out, N)

def mul_monomial(poly, mm, N):
    out = {}
    for m, v in poly.items():
        nm = (m[0] + mm[0], m[1] + mm[1], m[2] + mm[2])
        out[nm] = out.get(nm, 0) + v
    return reduce_yz(out, N)

def poly_pow(base, exp, N):
    acc = {(0, 0, 0): 1}
    for _ in range(exp):
        acc = mul_poly(acc, base, N)
    return acc


def build_polys(N, e, m, t, a=0, C=2):
    """DN00: g_{k,i,b}=e^(m-k) x^i y^a z^b f^k (k<m, 1<=i<=m-k, b=0,1);
              h_{k,j}=e^(m-k) y^(a+j) f^k (k<=m, 0<=j<=t).
       f = C + x*(A - y - z), A=N+1; root (2k0, p, q) when C=2."""
    A = N + 1
    f = reduce_yz({(0, 0, 0): C, (1, 0, 0): A, (1, 1, 0): -1, (1, 0, 1): -1}, N)
    fpow = [{(0, 0, 0): 1}]
    for kk in range(1, m + 1):
        fpow.append(mul_poly(fpow[-1], f, N))
    polys = []
    for kk in range(m):
        for i in range(1, m - kk + 1):
            for b in (0, 1):
                g = mul_monomial(fpow[kk], (i, a, b), N)
                polys.append({mo: v * e ** (m - kk) for mo, v in g.items()})
    for kk in range(m + 1):
        for j in range(t + 1):
            g = mul_monomial(fpow[kk], (0, a + j, 0), N)
            polys.append({mo: v * e ** (m - kk) for mo, v in g.items()})
    return polys


def make_lattice(polys, bounds_bits):
    bx, by, bz = bounds_bits
    mons = sorted({mo for p in polys for mo in p},
                  key=lambda mo: (mo[0] + mo[1] + mo[2], mo[1], mo[2]))
    W = [2 ** (bx * mo[0] + by * mo[1] + bz * mo[2]) for mo in mons]
    idx = {mo: j for j, mo in enumerate(mons)}
    B = IntegerMatrix(len(polys), len(mons))
    for r, p in enumerate(polys):
        for mo, v in p.items():
            B[r, idx[mo]] = v * W[idx[mo]]
    return mons, W, B


def eval_poly(poly, x0, y0, z0, N):
    p = reduce_yz(poly, N)
    s = 0
    for (a, b, c), v in p.items():
        s += v * (x0 ** a) * (y0 ** b) * (z0 ** c)
    return s

# Region-optimized shifted-power lattice. det via exact Bareiss on Gram (cheap dims).
# objective: det^(1/n) + penalty*n  vs bound = m*log2(e) - 0.5*log2(ncols)
import math, re, sys, json
import sympy
from fractions import Fraction
from fpylll import IntegerMatrix, LLL
from reallat import make_f
from purelat import ppow

t = open('output.txt').read()
N = int(re.search(r'N = (0x[0-9a-f]+)', t).group(1), 16)
e = int(re.search(r'e = (0x[0-9a-f]+)', t).group(1), 16)

def build_gen(f, M, X, Y, A):
    # A: dict t -> list of (a,b)
    polys = []
    for tt in sorted(A):
        g = {k: v*(M**tt) for k, v in ppow(f, max(A)-tt).items()}
        for (a, b) in A[tt]:
            polys.append({(i+a, j+b): cc for (i,j), cc in g.items() if cc})
    cols = sorted({k for p in polys for k in p})
    ci = {k: i for i, k in enumerate(cols)}
    B = IntegerMatrix(len(polys), len(cols))
    for r, p in enumerate(polys):
        for (i,j), v in p.items():
            B[r, ci[(i,j)]] = int(v) * (X**i) * (Y**j)
    return B, cols

def det_bits_over_n(B):
    nz = [r for r in range(B.nrows) if any(int(B[r,j]) for j in range(B.ncols))]
    if len(nz) != B.ncols:
        return None, len(nz)
    G = sympy.Matrix([[sum(int(B[i,a2])*int(B[j,a2]) for a2 in range(B.ncols)) for j in nz] for i in nz])
    dg = int(G.det())
    if dg == 0: return None, len(nz)
    return math.log2(abs(dg)) / len(nz), len(nz)

def tri(theta, X=300.0, Y=254.0):
    out = []
    a = 0
    while True:
        wa = theta - X*a
        if wa < -1e-9 and a > 0: break
        b = 0
        while X*a + Y*b <= theta + 1e-9:
            out.append((a, b)); b += 1
        a += 1
    return out

def evaluate(name, m, th0, th1, Xb=300.0, Yb=254.0, gb=0, do_LLL=True):
    if gb:
        import windowsolve as W
        base = 1 << 255; step = 1 << (255-gb)
        f = W.make_f2(N, base+1, step//2); Y = step//2
    else:
        f = make_f(N); Y = 1 << 254
    X = 1 << 300
    A = {tt: tri(th0 + th1*tt, Xb, Yb) for tt in range(m+1)}
    B, cols = build_gen(f, e, X, Y, A)
    if B.ncols > 90 or B.nrows > 220:
        print(name, 'skip dims', B.nrows, B.ncols, flush=True); return None
    LLL.reduction(B, delta=0.99)
    nz = [r for r in range(B.nrows) if any(int(B[r,j]) for j in range(B.ncols))]
    if len(nz) < 6:
        print(name, 'tiny rank', flush=True); return None
    G = sympy.Matrix([[sum(int(B[i,a2])*int(B[j,a2]) for a2 in range(B.ncols)) for j in nz] for i in nz])
    dg = int(G.det())
    if dg == 0:
        print(name, 'gram zero', flush=True); return None
    n = len(nz)
    d1 = math.log2(abs(dg)) / n
    mn = min(math.log2(sum(int(B[rr,j])**2 for j in range(B.ncols)))/2 for rr in nz)
    bound = m*math.log2(e) - 0.5*math.log2(n)
    print(f'{name}: {B.nrows}x{B.ncols} r={n} det1n={d1:.0f} minLLL={mn:.0f} bound={bound:.0f} margin={bound-mn:.0f} gauss-min={d1+math.sqrt(n/math.e/math.pi):.0f}', flush=True)
    return (name, d1, mn, bound)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if mode == 'scan':
        for m in (2, 3):
            for th0 in (300, 554, 808, 1062):
                for th1 in (300, 554, 808, 1300):
                    evaluate(f'm{m} t0={th0} t1={th1}', m, th0, th1)
    elif mode == 'scan2':  # refined around sweet spot with gb=2
        for m in (2, 3):
            for th0 in (554, 808):
                for th1 in (808, 1062, 1300, 1560):
                    evaluate(f'gb2 m{m} t0={th0} t1={th1}', m, th0, th1, gb=2)

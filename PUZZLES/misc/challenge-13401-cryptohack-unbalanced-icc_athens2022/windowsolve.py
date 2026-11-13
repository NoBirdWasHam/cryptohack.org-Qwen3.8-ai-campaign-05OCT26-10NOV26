# Guess top g bits of p; windowed shifted lattice; LLL; extract vanishing rows -> p | N.
# p in [2^255 + gtop*2^(255-g), 2^255 + (gtop+1)*2^(255-g)): p = 2^255 + gtop*2^(255-g) + 2*(2^(254-g))*w' + ...
# parametrize: p = C_g + 2^(255-gb) ... let's do: p = 2^255 + T + 2*2^(254-gb)*w'' where T = top-value offset
import math, re, sys, pickle
from fractions import Fraction
import sympy
from fpylll import IntegerMatrix, LLL
from extract2 import extract
from reallat import build, rows_of

t = open('output.txt').read()
N = int(re.search(r'N = (0x[0-9a-f]+)', t).group(1), 16)
e = int(re.search(r'e = (0x[0-9a-f]+)', t).group(1), 16)
c = int(re.search(r'c = (0x[0-9a-f]+)', t).group(1), 16)

def make_f2(N, C, S):
    # p = C + 2*w',  w' in [0, S)
    u, w = sympy.symbols('u w')
    P = C + 2*w
    Gx = sympy.expand(u*(P-1)*(N-P) + P)
    f = {}
    for mon, co in Gx.as_coefficients_dict().items():
        du = int(sympy.degree(mon, u)) if mon != 1 else 0
        dw = int(sympy.degree(mon, w)) if mon != 1 else 0
        if mon == 1: du = dw = 0
        f[(du, dw)] = int(f.get((du, dw), 0)) + int(co)
    return f

def attempt(C, S, m=2, cc=2):
    f = make_f2(N, C, S)
    X, Y = 1 << 300, S
    B, cols = build(f, e, X, Y, m=m, c=cc)
    LLL.reduction(B, delta=0.999)
    norms = []
    for r in range(B.nrows):
        s = sum(int(B[r, jj])**2 for jj in range(B.ncols))
        if s:
            norms.append((s.bit_length()/2.0, r))
    norms.sort()
    bound = (e**m).bit_length() - 1 - 0.5*math.log2(B.ncols)
    rows = rows_of(B, cols, X, Y)
    good = []
    for b2, r in norms:
        if b2 >= bound: break
        row = {}
        for ci,(i,j) in enumerate(cols):
            v = int(B[r, ci])
            if v: row[(i,j)] = Fraction(v, (X**i)*(Y**j))
        good.append(row)
    return good, norms[0][0] if norms else 9e9, bound

def verify_p(p):
    if p < 2 or p >= N or N % p: return None
    q = N // p
    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    m = pow(c, d, N)
    try:
        from Crypto.Util.number import long_to_bytes
        b = long_to_bytes(m)
        if b.startswith(b'crypto') or b.startswith(b'flag'):
            return (p, d, b)
        return (p, d, b[:40])
    except Exception:
        return (p, d, b'')

if __name__ == '__main__':
    gb = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    base = 1 << 255
    step = 1 << (255 - gb)          # window width in p
    Sw = 1 << (254 - gb)            # w' bound: p = base + gtop*step + 1 + 2*w'?? p odd:
    # p odd: p = base + gtop*step + 1 + 2*z, z in [0, step/2): since base even, step even.
    for gtop in range(1 << gb):
        C = base + gtop*step + 1
        S = step // 2
        try:
            good, mn, bound = attempt(C, S)
        except Exception as ex:
            print(gtop, 'ERR', ex, flush=True)
            continue
        print(f'gtop={gtop} min={mn:.1f} bound={bound:.1f} under={len(good)}', flush=True)
        if len(good) >= 2:
            ells = []
            v = 2**61
            while len(ells) < 6:
                v = sympy.nextprime(v + 31)
                ells.append(int(v))
            ps = None
            import itertools
            for a, b in itertools.combinations(range(min(len(good), 8)), 2):
                try:
                    ps = extract([good[a], good[b]], 1 << 300, S, N, ells)
                except Exception:
                    ps = None
                if ps:
                    break
            print('  candidates:', ps, flush=True)
            if ps:
                for p_ in ps:
                    r = verify_p(p_)
                    if r and r[2] and (r[2].startswith(b'crypto')):
                        print('FLAG:', r[2], flush=True)
                        open('flag_unbalanced-icc_athens2022.txt', 'wb').write(r[2])
                        sys.exit(0)
                    elif r:
                        print('  factored but flag decode:', r[2][:30], flush=True)

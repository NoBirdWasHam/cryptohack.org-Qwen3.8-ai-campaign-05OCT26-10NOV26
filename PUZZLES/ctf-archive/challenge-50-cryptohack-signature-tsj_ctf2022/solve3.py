# v3 correct geometry: lattice L = { (M a + q u, -a) : a in Z^256, u in Z^6 } subset Z^{262}.
# det L = q^6, dim 262, GH ~ 230. Since M d = v mod q for the true bit-vector d,
# the true solution shows as lattice vector (0,0,0,0,0,0, -d) with norm ~ sqrt(128) ~ 11.
# => uSVP: reduce, scan rows with first-6 coords zero and last-256 coords in {0,-1}.
import sys, time, os
from solve import q, N, G, ec_mul, load, build_system, try_candidate, decrypt

CACHE = 'b262.dump'

def build_matrix(M, v):
    from fpylll import IntegerMatrix
    dim = N + 7
    B = IntegerMatrix(dim, dim)
    for i in range(6):
        B[i, i] = q
    for j in range(N):
        for i in range(6):
            B[6 + j, i] = M[i][j] % q
        B[6 + j, 6 + j] = -1
    for i in range(6):
        B[N + 6, i] = v[i] % q   # Kannan target row (v, 0, T=1)
    B[N + 6, N + 6] = 1
    return B

def scan(Bmat, Z, R, tag):
    hits = 0
    dim = N + 7
    for r in range(dim):
        if abs(int(Bmat[r, dim - 1])) != 1:
            continue
        if any(int(Bmat[r, i]) for i in range(6)):
            continue
        sgn = 1 if int(Bmat[r, dim - 1]) > 0 else -1
        row = [sgn * int(Bmat[r, j]) for j in range(6, 6 + N)]
        if any(t not in (0, 1) for t in row):
            continue
        hits += 1
        d = try_candidate(row, Z, R)
        if d is not None:
            print(f'{tag}: row {r} -> recovered d = {d}', flush=True)
            return d
    print(f'{tag}: scan done, {hits} zero-head binary rows', flush=True)
    return None

def save_mat(B, path):
    with open(path, 'w') as f:
        for r in range(B.nrows):
            f.write(','.join(str(int(B[r, c])) for c in range(B.ncols)) + '\n')

def load_mat(path):
    from fpylll import IntegerMatrix
    rows = [list(map(int, ln.split(','))) for ln in open(path)]
    B = IntegerMatrix(len(rows), len(rows[0]))
    for i, row in enumerate(rows):
        for j, t in enumerate(row):
            B[i, j] = t
    return B

def main():
    Z, R, S, ct = load('output.txt')
    assert len(Z) == 6
    from fpylll import LLL, BKZ
    t0 = time.time()
    M, v = build_system(Z, R, S)
    B = build_matrix(M, v)
    if os.path.exists(CACHE):
        print('loading cached basis', flush=True)
        B = load_mat(CACHE)
    else:
        print('LLL start', flush=True)
        LLL.reduction(B)
        save_mat(B, CACHE)
        print(f'LLL done {time.time()-t0:.0f}s', flush=True)
    d = scan(B, Z, R, 'LLL')
    for beta in (20, 30, 40):
        if d is not None:
            break
        print(f'BKZ{beta} start ({time.time()-t0:.0f}s)', flush=True)
        BKZ.reduction(B, BKZ.Param(beta))
        save_mat(B, CACHE.replace('.dump', f'_bkz{beta}.txt'))
        print(f'BKZ{beta} done ({time.time()-t0:.0f}s)', flush=True)
        d = scan(B, Z, R, f'BKZ{beta}')
    if d is not None:
        print('FLAG D:', d, flush=True)
        decrypt(d, ct)
    else:
        print('V3 FAIL', flush=True)

if __name__ == '__main__':
    main()

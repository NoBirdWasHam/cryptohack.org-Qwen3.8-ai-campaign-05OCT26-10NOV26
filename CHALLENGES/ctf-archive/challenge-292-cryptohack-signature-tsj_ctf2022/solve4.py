# v4: Kannan lattice of solve3 + EXACT radius enumeration (guaranteed to contain
# the true vector (0^6, d, +-1), norm^2 = popcount(d)+1 in [90,170]; enumerate radius^2=300.
import sys, os, time
from solve import q, N, G, ec_mul, load, build_system, try_candidate, decrypt
from solve3 import build_matrix, save_mat, load_mat

CACHE = 'b262v4.txt'

def harvest(B, Z, R):
    from fpylll import GSO, Enumeration
    dim = N + 7
    M = GSO.Mat(B)
    M.update_gso()
    e = Enumeration(M)
    t = time.time()
    out = e.enumerate(0, dim, 300, 0)
    sols = out[0] if isinstance(out, tuple) else out
    print(f'enum: {len(sols)} sols ({time.time()-t:.0f}s)', flush=True)
    for pair in sols:
        norm2, coef = float(pair[0]), pair[1]
        vec = [sum(int(coef[i]) * int(B[i, j]) for i in range(dim)) for j in range(dim)]
        if abs(vec[dim - 1]) != 1:
            continue
        if any(vec[i] for i in range(6)):
            continue
        sgn = 1 if vec[dim - 1] > 0 else -1
        mid = [sgn * t2 for t2 in vec[6:6 + N]]
        if any(t2 not in (0, 1) for t2 in mid):
            continue
        d = try_candidate(mid, Z, R)
        if d is not None:
            print(f'recovered d = {d} (len2={norm2})', flush=True)
            return d
    print(f'no valid vector among {len(sols)} enum solutions', flush=True)
    return None

def main():
    Z, R, S, ct = load('output.txt')
    M, v = build_system(Z, R, S)
    if os.path.exists(CACHE) and os.path.getsize(CACHE) > 1000:
        print('loading cached basis', flush=True)
        B = load_mat(CACHE)
    else:
        from fpylll import LLL
        t = time.time()
        B = build_matrix(M, v)
        print('LLL start', flush=True)
        LLL.reduction(B)
        save_mat(B, CACHE)
        print(f'LLL done {time.time()-t:.0f}s', flush=True)
    d = harvest(B, Z, R)
    if d is not None:
        print('FLAG D:', d, flush=True)
        decrypt(d, ct)
    else:
        print('V4 FAIL', flush=True)

if __name__ == '__main__':
    main()

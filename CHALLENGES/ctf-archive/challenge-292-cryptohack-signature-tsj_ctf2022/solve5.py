# v5: cheap reductions on the v4 lattice (LLL is 39s here!) + row scan after each.
# Ladder: LLL(delta=.999) -> BKZ20 -> BKZ30 -> BKZ40 -> BKZ60, snapshot per stage.
import os, time
from solve import q, N, load, build_system, try_candidate, decrypt
from solve3 import build_matrix, save_mat, load_mat
from solve4 import harvest  # not used for enum (dim cap), kept for reuse
from solve3 import scan

CACHE = 'b262v4.txt'

def main():
    Z, R, S, ct = load('output.txt')
    from fpylll import LLL, BKZ
    t0 = time.time()
    if os.path.exists(CACHE) and os.path.getsize(CACHE) > 1000:
        B = load_mat(CACHE)
        print('loaded basis', flush=True)
    else:
        M, v = build_system(Z, R, S)
        B = build_matrix(M, v)
        LLL.reduction(B)
        save_mat(B, CACHE)
    d = scan(B, Z, R, 'LLL')
    for beta in (20, 30, 40, 60):
        if d is not None:
            break
        print(f'BKZ{beta} start ({time.time()-t0:.0f}s)', flush=True)
        BKZ.reduction(B, BKZ.Param(beta))
        save_mat(B, f'bbkz{beta}.txt')
        print(f'BKZ{beta} done ({time.time()-t0:.0f}s)', flush=True)
        d = scan(B, Z, R, f'BKZ{beta}')
    if d is not None:
        print('FLAG D:', d, flush=True)
        decrypt(d, ct)
    else:
        print('V5 FAIL', flush=True)

if __name__ == '__main__':
    main()

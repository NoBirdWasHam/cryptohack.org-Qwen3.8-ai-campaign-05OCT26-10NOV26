# v2: same linear model as solve.py (d(s-r) - 2s(d&z) = z(1-s) mod q, bits d_j),
# but stronger CVP: Kannan embedding scan + BKZ + exact enumeration.
import sys, ast, time
from hashlib import sha256
from Crypto.Cipher import AES
from solve import q, N, G, ec_mul, load, build_system, particular, kernel_basis, try_candidate, decrypt

def check_x(x, Z, R, maxflip=14):
    bad = [j for j, t in enumerate(x) if t not in (0, 1)]
    if not bad:
        return try_candidate(x, Z, R)
    if len(bad) <= maxflip:
        print(f'  {len(bad)} nonbinary -> {2**len(bad)} flips', flush=True)
        for mask in range(1 << len(bad)):
            y = list(x)
            for b, j in enumerate(bad):
                y[j] = (mask >> b) & 1
            d = try_candidate(y, Z, R)
            if d is not None:
                return d
    else:
        print(f'  {len(bad)} bad > maxflip {maxflip}, skipped', flush=True)
    return None

def from_vec(vec, x0, Z, R, sgn):
    x = [x0[j] + sgn * int(vec[j]) for j in range(N)]
    return check_x(x, Z, R)

def run(Z, R, S, ct, stages):
    from fpylll import IntegerMatrix, LLL, BKZ, CVP
    t0 = time.time()
    M, v = build_system(Z, R, S)
    x0 = particular(M, v)
    if x0 is None:
        print('no particular solution'); return None
    B = kernel_basis(M)  # LLL-reduced already

    def babai_stage(tag, mat):
        print(f'stage {tag} babai', flush=True)
        w = CVP.babai(mat, x0)
        x = [x0[j] - int(w[j]) for j in range(N)]
        return check_x(x, Z, R)

    def kannan_stage(tag, mat, beta=None):
        # embedding: rows [mat | 0] and [x0 | T]; USVP -> x0 - w (last coord -T)
        T = 32
        E = IntegerMatrix(N + 1, N + 1)
        for i in range(N):
            for j in range(N):
                E[i, j] = mat[i, j]
        for j in range(N):
            E[N, j] = x0[j]
        E[N, N] = T
        if beta:
            BKZ.reduction(E, BKZ.Param(beta))
        else:
            LLL.reduction(E)
        print(f'stage {tag} kannan scan ({time.time()-t0:.0f}s)', flush=True)
        for r in range(N + 1):
            last = abs(int(E[r, N]))
            if last != T:
                continue
            sgn = 1 if int(E[r, N]) > 0 else -1
            d = from_vec(E[r], x0, Z, R, sgn)
            if d is not None:
                return d
        return None

    for st in stages:
        print(f'--- {st} ({time.time()-t0:.0f}s) ---', flush=True)
        if st == 'babai':
            d = babai_stage(st, B)
        elif st == 'kannan-LLL':
            d = kannan_stage(st, B)
        elif st.startswith('bkz'):
            beta = int(st[3:].split('-')[0].replace('b', ''))
            BKZ.reduction(B, BKZ.Param(beta))
            d = babai_stage(st, B)
            if d is None and '-' in st:
                d = kannan_stage(st, B)
        elif st == 'enum':
            print('stage exact CVP', flush=True)
            w = CVP.closest_vector(B, x0)
            x = [x0[j] - int(w[j]) for j in range(N)]
            d = check_x(x, Z, R, maxflip=0)
        else:
            d = None
        if d is not None:
            print(f'recovered d at {st} = {d}', flush=True)
            return d
        print(f'{st} failed ({time.time()-t0:.0f}s)', flush=True)
    return None

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'real'
    stages = sys.argv[2].split(',') if len(sys.argv) > 2 else ['babai', 'kannan-LLL', 'bkz20-b', 'bkz30-', 'enum']
    msgs = ["https://www.youtube.com/watch?v=16M9oC-a5bY","https://www.youtube.com/watch?v=QDadz5JZCw8",
            "https://www.youtube.com/watch?v=kyNh7KnsTN0","https://www.youtube.com/watch?v=Lqn42JJxS3I",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ","https://www.youtube.com/watch?v=1Gw_-E784l0"]
    if mode == 'sim':
        import random
        dtrue = random.randrange(1, q)
        Z, R, S = [], [], []
        for m in msgs:
            z = int(sha256(m.encode()).hexdigest(), 16)
            k = dtrue ^ z
            r = ec_mul(G, k)[0]
            s = pow(k % q, -1, q) * (z + r * dtrue) % q
            Z.append(z); R.append(r); S.append(s)
        # model sanity: true bits must satisfy M x = v
        M, v = build_system(Z, R, S)
        bits = [(dtrue >> j) & 1 for j in range(N)]
        ok = all(sum(M[i][j] * bits[j] for j in range(N)) % q == v[i] for i in range(6))
        print('model check on sim d:', ok, flush=True)
        d2 = run(Z, R, S, None, stages)
        print('SIM SUCCESS' if d2 == dtrue else f'SIM FAIL got {d2}', flush=True)
    else:
        Z, R, S, ct = load('output.txt')
        assert len(Z) == 6
        d = run(Z, R, S, ct, stages)
        if d is not None:
            decrypt(d, ct)
        else:
            print('REAL FAIL', flush=True)

if __name__ == '__main__':
    main()

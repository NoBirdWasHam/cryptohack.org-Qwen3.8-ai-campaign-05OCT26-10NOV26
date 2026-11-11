# solve_bp2.py — Gaussian BP for per-block popcount system; locked bits then
# linear algebra (if overdetermined) or small Kannan lattice (if few free bits).
import ast, hashlib, os, sys, time
import numpy as np
np.seterr(all='ignore')

D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()
A = np.array([[(pub[j] >> (511 - k)) & 1 for k in range(512)] for j in range(256)], dtype=np.float64)

def bp(cvec, rounds=8, iters=4000, damp=0.5, seed=0):
    cv = np.array(cvec, float)
    W = A > 0
    lam_p = np.full(512, 4.0)   # prior precision 1/0.25
    lm_p = np.full(512, 2.0)    # prior mean/prec = 0.5*4
    rng = np.random.default_rng(seed)
    for rd in range(rounds):
        mCv = np.where(W, 0.0, np.nan)  # check->var messages (mean, var)
        mu = np.where(W, 0.5, np.nan); vu = np.where(W, 0.25, np.nan)
        best_x = None; best_bad = 1e18
        for it in range(iters):
            # variable beliefs: prior + incoming from checks
            tp = np.full(512, lam_p); tm = np.full(512, lm_p)
            inc_p = np.where(np.isnan(mCv), 0.0, 1.0 / np.where(np.isnan(mCv), 1, mCv))
            inc_m = np.where(np.isnan(mCv), 0.0, mu / np.where(np.isnan(mu), 1, mCv))
            tp = lam_p + (inc_p * W).sum(0); tm = lm_p + (inc_m * W).sum(0)
            bm = tm / tp; bv = 1.0 / tp
            S = (bm[None, :] * A).sum(1); V = (bv[None, :] * A).sum(1)
            # check->var: target t = c - S + bm, var s2 = V - bv
            t = cv[:, None] - S[:, None] + bm[None, :]
            s2 = np.maximum(V[:, None] - bv[None, :], 1e-2)
            new_mu = np.where(W, t, np.nan); new_vu = np.where(W, s2, np.nan)
            if it % 400 == 399:
                xh = (bm > 0.5)
                res = A @ xh - cv
                nbad = int(np.abs(res).sum())
                if nbad < best_bad:
                    best_bad = nbad; best_x = xh.astype(np.int8).copy()
                if it and it % 1200 == 1199:
                    damp2 = min(0.9, damp + 0.1)
                else:
                    damp2 = damp
                mu = damp2 * mu + (1 - damp2) * new_mu
                vu = damp2 * vu + (1 - damp2) * new_vu
                mCv = np.where(np.isnan(mu), np.nan, np.maximum(vu, 1e-2))
                if np.isnan(mu).all(): break
            else:
                mu = damp * mu + (1 - damp) * new_mu
                vu = damp * vu + (1 - damp) * new_vu
                mCv = np.where(np.isnan(mu), np.nan, np.maximum(vu, 1e-2))
        conf = bv
        lock = conf < 0.02
        # anneal priors: lock confident bits
        bm_clip = np.clip(bm, 0, 1)
        lam_p = np.where(lock, 1e4, 4.0)
        lm_p = np.where(lock, (bm_clip > 0.5) * 1e4, 2.0)
        xh = best_x if best_x is not None else (bm > 0.5).astype(np.int8)
        print(f'  rd{rd}: bad={best_bad} locked={int(lock.sum())}', flush=True)
        if best_bad == 0:
            return xh.astype(np.int64), None
    return xh.astype(np.int64), (~lock).astype(np.int64)

def reduce_and_solve(x0, free, cvec):
    cv = np.array(cvec, float)
    fi = np.flatnonzero(free == 0)
    base = A[:, fi] @ x0[fi]
    rf = np.flatnonzero(free == 1)
    Af = A[:, rf]; cr = cv - base
    k = len(rf)
    print('  free bits:', k)
    if k <= 250:
        # solve over rationals via least squares exact (integer): Af y = cr
        from fractions import Fraction
        import sympy as sp
        M = sp.Matrix([[int(Af[i, j]) for j in range(k)] + [int(cr[i])] for i in range(256)])
        sol = M.rref()
        print('  rref done')
        return None
    return None

flag = b''
for bi, c in enumerate(enc):
    t0 = time.time()
    x, free = bp(c)
    if free is None:
        mb = bytes(int(''.join(map(str, x[8*i:8*i+8])), 2) for i in range(64))
        assert all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == c[j] for j in range(256))
        print(f'block {bi}: SOLVED {mb[24:32]} ({time.time()-t0:.0f}s)', flush=True)
        flag += mb[24:32]
    else:
        print(f'block {bi}: BP incomplete, free={int(free.sum())}', flush=True)
        sys.exit(2)
fs = flag.rstrip(b'\x00').decode('latin1')
print('FLAG:', fs)
open(os.path.join(D, 'flag_failproof_revenge-sekaictf202.txt'), 'w').write(fs)

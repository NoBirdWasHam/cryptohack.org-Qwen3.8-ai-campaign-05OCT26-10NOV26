# solve_bp.py — per-block integer-popcount system solved by Gaussian loopy BP + polish.
import ast, hashlib, os, sys, time
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()
A = np.array([[(pub[j] >> (511 - k)) & 1 for k in range(512)] for j in range(256)], dtype=np.float64)
cols = A.sum(axis=0)  # weights per variable (~256)

def bp_block(c, iters=3000, damp=0.5):
    cv = np.array(c, dtype=np.float64)
    W = (A > 0)
    m = np.full_like(A, 0.5); v = np.full_like(A, 0.25)   # var->check messages
    bpri_m = np.full(512, 0.5); bpri_v = np.full(512, 0.25)
    for it in range(iters):
        M = (m * A).sum(axis=1); V = (v * A).sum(axis=1)
        # check->var: constraint sum_{W} x = c
        mu_t = cv[:, None] - (M[:, None] - m * A)          # implied mean per edge
        var_t = np.maximum(V[:, None] - v * A, 1e-3)
        prec_new = 1.0 / var_t - 1.0 / np.maximum(v, 1e-9)
        pm_new = mu_t / var_t - m * 0  # placeholder
        with np.errstate(divide='ignore', invalid='ignore'):
            bp_m = m * A + 0  # per-edge belief mean = prior + incoming; we track per-edge ex terms
        # simpler: recompute edge beliefs via prior + all other checks is O(n^2); use standard trick:
        # edge-belief precision = prior_prec + sum_check prec - edge prec ... need check->var set.
        # Do node-based updates with exclusion via totals:
        # var belief (from prior + all checks):
        tp = 1.0 / bpri_v; tm = bpri_m / bpri_v
        # aggregate check->var totals approximated by summing edge target messages over checks
        ctp = (W * (1.0 / var_t)).sum(axis=0) - 0  # (A already 0/1)
        ctm = (W * (mu_t / var_t)).sum(axis=0)
        bp_mN = (tm + ctp * 0 + ctm) / (tp + ctp)
        bp_vN = 1.0 / (tp + ctp)
        # clamp to [0,1]-ish via clipping moments
        bp_mN = np.clip(bp_mN, -0.2, 1.2)
        bp_vN = np.minimum(bp_vN, 0.30)
        # var->check messages: exclude the check itself
        tpV = tp[None, :] + ctp[None, :]
        tmV = tm[None, :] + ctm[None, :]
        newm = (tmV - (mu_t / var_t)) / np.maximum(tpV - (1.0 / var_t), 1e-6)
        newv = 1.0 / np.maximum(tpV - (1.0 / var_t), 1e-6)
        newm = np.where(W, newm, m); newv = np.where(W, np.minimum(newv, 0.30), v)
        m = damp * m + (1 - damp) * newm; v = damp * v + (1 - damp) * newv
        if it % 300 == 0:
            xh = (bp_mN > 0.5)
            res = np.abs(A @ xh - cv)
            print(f'  it{it}: bad={int((res>0).sum())} sumres={int(res.sum())}', flush=True)
            if res.sum() == 0: break
    xh = np.where(bp_mN > 0.5, 1.0, 0.0)
    return xh, bp_vN

def polish(x, c, iters=200000):
    cv = np.array(c)
    cur = (A @ x - cv)
    for it in range(iters):
        bad = np.flatnonzero(cur != 0)
        if len(bad) == 0: return True
        # greedy single-bit flips reduce sum sq residual
        gain = -(cur[bad] ** 2 * 0)  # compute deltas: flipping var k changes eqs A[:,k]
        best = None
        ks = np.random.choice(512, 64, replace=False)
        for k in ks:
            d = A[:, k].astype(int) * (1 - 2 * int(x[k]))
            newss = int(((cur + d) ** 2).sum() - (cur ** 2).sum())
            if best is None or newss < best[0]: best = (newss, k)
        if best[0] >= 0:
            if it % 2000 == 0 and it: return False
            x[np.random.randint(512)] ^= 1
            cur = (A @ x - cv)
        else:
            x[best[1]] ^= 1
            cur = (A @ x - cv)
    return (cur == 0).all()

flag = b''
rng = np.random.default_rng(1)
for bi, c in enumerate(enc):
    t0 = time.time()
    ok = False
    for attempt in range(6):
        x, bv = bp_block(c, iters=1500, damp=0.6 if attempt else 0.5)
        if polish(x, c):
            ok = True; break
        # retry with prior shifted by BP belief
        if (bv < 0.05).sum() < 20: break
        bpri_saved = (bpri_m.copy(), bpri_v.copy())
        m0b = (x > 0.5).astype(float)
        bpri_m[:] = np.where(bv < 0.08, m0b, 0.5); bpri_v[:] = np.where(bv < 0.08, 0.02, 0.25)
        bpri_m, bpri_v = bpri_saved if False else (bpri_m, bpri_v)
    if not ok:
        print(f'block {bi}: FAILED'); sys.exit(1)
    mb = bytes(int(''.join(map(str, x[8*i:8*i+8])), 2) for i in range(64))
    assert all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == c[j] for j in range(256))
    seg = mb[24:32]
    print(f'block {bi}: {seg}  ({time.time()-t0:.0f}s)', flush=True)
    flag += seg
fs = flag.rstrip(b'\x00').decode('latin1')
print('FLAG:', fs)
open(os.path.join(D, 'flag_failproof_revenge-sekaictf202.txt'), 'w').write(fs)

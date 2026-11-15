# solve5.py — per-block reduced-dim CVP (fpylll closest_vector enumeration / Kannan+BKZ)
import ast, hashlib, os, subprocess, sys, time
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))

def pv(s):
    s = s.strip()
    if s.startswith('Vecsmall('):
        s = s[len('Vecsmall('):]
        if s.endswith(')'): s = s[:-1]
    if s[0] == '[' and s[-1] == ']': s = s[1:-1]
    return [int(x) for x in s.split(',')]

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == '--block':
    bi = int(sys.argv[2])
    from fpylll import IntegerMatrix, CVP
    txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
    secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
    state = hashlib.sha512(secret).digest(); pub = []
    for _ in range(256):
        pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()
    variant = 'b0' if bi == 0 else ('b6' if bi == 6 else 'mid')
    Kf = 'K_mid.txt' if variant == 'mid' else f'K_{variant}.txt'
    mf = f'm0_mid{bi+1}.txt' if variant == 'mid' else f'm0_{variant}.txt'
    K = [pv(l) for l in open(os.path.join(D, Kf)) if l.strip()]
    m0 = pv(open(os.path.join(D, mf)).readline())
    keep = pv(open(os.path.join(D, f'keep_{variant}.txt')).readline())
    n2 = len(keep); d = len(K)
    T = [1 - 2 * x for x in m0]
    flat = []
    for i in range(d): flat += [2 * K[i][j] for j in range(n2)] + [0]
    flat += T + [23]
    M2 = IntegerMatrix.from_iterable(d, n2, [2 * K[i][j] for i in range(d) for j in range(n2)])
    T2 = T
    sol = None
    for meth in ("fast", "proved"):
        try:
            sol = CVP.closest_vector(M2, T2, meth); print('method', meth, 'ok', flush=True); break
        except Exception as e:
            print(meth, 'failed:', str(e)[:80], flush=True)
    if sol is None:
        # Kannan fallback
        from fpylll.fplll.lll import lll_reduction
        from fpylll.fplll.bkz import bkz_reduction
        from fpylll.fplll.bkz_param import BKZParam
        MM = IntegerMatrix.from_iterable(d + 1, n2 + 1, flat)
        Mred = lll_reduction(MM)
        best = None
        for i in range(Mred.nrows):
            if abs(Mred[i, n2]) == 23:
                nm = sum(Mred[i, j] * Mred[i, j] for j in range(n2))
                if best is None or nm < best[0]: best = (nm, i)
        raw = [Mred[best[1], j] for j in range(n2)]; last = Mred[best[1], n2]
        v = [(T[j] + raw[j]) // 2 if last < 0 else (T[j] - raw[j]) // 2 for j in range(n2)]
    else:
        w = [sol[j] for j in range(n2)]
        assert all(x % 2 == 0 for x in w), 'odd closest vector'
        v = [x // 2 for x in w]
    m = [m0[j] + v[j] for j in range(n2)]
    if not all(x in (0, 1) for x in m):
        print('NOT BITS'); sys.exit(1)
    bits = [0] * 512
    if variant == 'b0':
        known = b'crypto{'
        pos = 192
        for ch in known:
            for bit in range(8):
                bits[pos] = (ch >> (7 - bit)) & 1; pos += 1
    for idx, kpos in enumerate(keep):
        bits[kpos - 1] = m[idx]
    mb = bytes(int(''.join(map(str, bits[8 * t:8 * t + 8])), 2) for t in range(64))
    c = enc[bi]
    ok = all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == c[j] for j in range(256))
    print('VERIFIED', ok, 'seg', mb[24:32])
    if ok:
        open(os.path.join(D, f'seg_{bi}.txt'), 'wb').write(mb[24:32])
    sys.exit(0 if ok else 1)

flag = b''
for bi in range(7):
    t0 = time.time()
    r = subprocess.run([sys.executable, '-u', __file__, '--block', str(bi)],
                       capture_output=True, text=True, timeout=900)
    print(f'block {bi} rc={r.returncode} ({time.time()-t0:.0f}s)', r.stdout.strip()[-200:])
    if r.returncode != 0:
        print(r.stderr[-300:]); sys.exit(1)
    flag += open(os.path.join(D, f'seg_{bi}.txt'), 'rb').read()
fs = flag.rstrip(b'\x00').decode('latin1')
print('FLAG:', fs)
open(os.path.join(D, 'flag_failproof_revenge-sekaictf202.txt'), 'w').write(fs)

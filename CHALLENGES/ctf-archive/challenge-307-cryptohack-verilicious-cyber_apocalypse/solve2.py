# Staged variant: escalating BKZ block sizes with per-stage time limit,
# extraction attempt after each stage (true solution is far below GH).
import sys, time
from fpylll import IntegerMatrix, LLL, BKZ

src = open('output.txt').read()
ns = {}
exec(src, ns)
enc = int(ns['enc_flag'], 16)
R = ns['R']

from Crypto.PublicKey import RSA
n = RSA.import_key(open('pubkey.pem').read()).n
e = 65537
N = len(R)
C2 = 1 << 1008
c = (5 * C2) // 2
kappa = C2 // 2
R = [r % n for r in R]
inv = pow(R[0], -1, n)
t0 = time.time()

B = IntegerMatrix(N, N)
for j in range(N):
    B[0, j] = R[j] * inv % n
B[0, 0] = 1
for i in range(1, N):
    B[i, i] = n
LLL.reduction(B, delta=0.99)
print('LLL done', time.time() - t0, flush=True)

E = IntegerMatrix(N + 1, N + 1)
for i in range(N):
    for j in range(N):
        E[i, j] = B[i, j]
for j in range(N):
    E[N, j] = c
E[N, N] = kappa

def try_extract():
    for i in range(N + 1):
        a = int(E[i, N])
        if abs(a) != kappa:
            continue
        sgn = 1 if a > 0 else -1
        err = [int(E[i, j]) * sgn for j in range(N)]
        for mode in (1, -1):
            v = [c + mode * err[j] for j in range(N)]
            if not all(2 * C2 <= x < 3 * C2 for x in v):
                continue
            cand = v[0] * inv % n
            if pow(cand, e, n) == enc:
                return cand
    return None

m = None
for b, tl in [(25, 120), (30, 300), (40, 1200), (50, 2400)]:
    p = BKZ.EasyParam(b)
    try:
        p.max_time = tl
    except Exception:
        pass
    BKZ.reduction(E, p)
    print('BKZ', b, 'done at', time.time() - t0, flush=True)
    m = try_extract()
    print('extract after', b, ':', bool(m), flush=True)
    if m:
        break

if m is None:
    print('FAIL: no solution through BKZ-50')
    raise SystemExit(1)

print('pow check:', pow(m, e, n) == enc)
print('all R consistent:', all(2 * C2 <= (r * m % n) < 3 * C2 for r in R))
em = m.to_bytes(128, 'big')
idx = em.index(b'\x00', 2)
flag = em[idx + 1:].decode(errors='replace')
print('FLAG =', flag)
open('flag_verilicious-cyber_apocalypse.txt', 'w').write(flag)
print('elapsed', time.time() - t0)

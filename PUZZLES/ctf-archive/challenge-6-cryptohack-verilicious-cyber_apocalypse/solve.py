# Verilicious solve: PKCS1 padding-valid multipliers => CVP for padded m.
import time
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

inv = pow(R[0], -1, n)  # if this raises, gcd(R0,n) already factors n
t0 = time.time()

B = IntegerMatrix(N, N)
for j in range(N):
    B[0, j] = R[j] * inv % n
B[0, 0] = 1
for i in range(1, N):
    B[i, i] = n
LLL.reduction(B, delta=0.99)
print('LLL done', time.time() - t0, 'reduced:', LLL.is_reduced(B))

E = IntegerMatrix(N + 1, N + 1)
for i in range(N):
    for j in range(N):
        E[i, j] = B[i, j]
for j in range(N):
    E[N, j] = c
E[N, N] = kappa

BKZ.reduction(E, BKZ.EasyParam(40))
print('BKZ done', time.time() - t0)

best = None
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
        # box is symmetric about c: both v and its mirror pass the box test.
        # Discriminate via RSA: m = v_0 / R_0 must satisfy m^e == enc_flag.
        cand = v[0] * inv % n
        if pow(cand, e, n) == enc:
            best = cand
            break
    if best:
        break

if best is None:
    print('FAIL: solution not surfaced by BKZ-40')
    raise SystemExit(1)

m = best
print('pow check:', pow(m, e, n) == enc)
print('all R consistent:', all(2 * C2 <= (r * m % n) < 3 * C2 for r in R))
if pow(m, e, n) == enc:
    em = m.to_bytes(128, 'big')
    idx = em.index(b'\x00', 2)
    flag = em[idx + 1:].decode(errors='replace')
    print('FLAG =', flag)
    open('flag_verilicious-cyber_apocalypse.txt', 'w').write(flag)
print('elapsed', time.time() - t0)

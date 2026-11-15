# Final method: CVP.closest_vector on the scaling lattice (radius-bounded
# enumeration finds the unique in-box solution instantly).
import time
from fpylll import IntegerMatrix, LLL, CVP

src = open('output.txt').read(); ns={}; exec(src, ns)
enc = int(ns['enc_flag'], 16); R = ns['R']
from Crypto.PublicKey import RSA
n = RSA.import_key(open('pubkey.pem').read()).n
e = 65537
N = len(R)
C2 = 1 << 1008
c = (5*C2)//2
R = [r % n for r in R]
inv = pow(R[0], -1, n)
t0 = time.time()
B = IntegerMatrix(N, N)
for j in range(N): B[0,j] = R[j]*inv % n
B[0,0] = 1
for i in range(1,N): B[i,i] = n
LLL.reduction(B, delta=0.99)
print('LLL done', time.time()-t0, flush=True)
v = [int(x) for x in CVP.closest_vector(B, [c]*N)]
print('CVP done', time.time()-t0, 'box:', all(2*C2 <= x < 3*C2 for x in v), flush=True)
m = v[0]*inv % n
if pow(m, e, n) != enc:
    # mirror ambiguity guard (box symmetric about c): also try 2c-v
    v2 = [2*c - x for x in v]
    m2 = v2[0]*inv % n
    if pow(m2, e, n) == enc:
        m = m2
    else:
        print('FAIL: pow check failed; box:', all(2*C2 <= x < 3*C2 for x in v))
        raise SystemExit(1)
print('pow ok; R-consistent:', all(2*C2 <= (r*m % n) < 3*C2 for r in R))
em = m.to_bytes(128,'big')
idx = em.index(b'\x00', 2)
flag = em[idx+1:].decode(errors='replace')
print('PS len', idx-2)
print('FLAG =', flag)
open('flag_verilicious-cyber_apocalypse.txt','w').write(flag)
print('elapsed', time.time()-t0)

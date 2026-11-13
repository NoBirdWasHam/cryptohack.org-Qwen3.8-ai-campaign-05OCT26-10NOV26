import sys
sys.path.insert(0, ".")
import numpy as np, random
from t280_fold import conv512, ringmul, glue_and_decrypt, member
rng = random.Random(7)
n, q, df, dg, dr, m = 256, 127, 9, 9, 4, 128   # odd df: f unit over F2 (as in the real problem)
def rand01(d):
    v = np.zeros(n, dtype=np.int64); v[rng.sample(range(n), d)] = 1; return v
def cm(a, b): return conv512(a, b, n) % q
while True:
    f = rand01(df); g = rand01(dg)
    Tm = np.zeros((n, n), dtype=np.int64)
    for r_ in range(n):
        for i in range(n): Tm[r_, i] = f[(r_ - i) % n]
    M2 = np.concatenate([Tm % q, (g % q).reshape(n, 1)], axis=1)
    sing = False
    for col in range(n):
        piv = next((rr for rr in range(col, n) if M2[rr, col] % q), None)
        if piv is None: sing = True; break
        M2[[col, piv]] = M2[[piv, col]]
        inv = pow(int(M2[col, col]), -1, q)
        M2[col] = M2[col] * inv % q
        for rr in range(n):
            if rr != col and M2[rr, col] % q: M2[rr] = (M2[rr] - M2[rr, col] * M2[col]) % q
    if sing: continue
    h = M2[:, n]
    if np.all((cm(f, h) - g) % q == 0): break
flag_bytes = b"NNS{GLUE_UNIT_OK_0123456789ABCD}"
assert len(flag_bytes) == n // 8, len(flag_bytes)
val = int.from_bytes(flag_bytes, "big")
mm = np.array([(val >> i) & 1 for i in range(n)], dtype=np.int64)
ct = (2 * cm(h, rand01(dr)) + mm) % q
h0, h1 = h[:m], h[m:]; hp = (h0 + h1) % q; hm = (h0 - h1) % q
f0, f1 = f[:m], f[m:]; g0, g1 = g[:m], g[m:]
fp_true, fm_true = f0 + f1, f0 - f1
print("memberships:", member(np.concatenate([fp_true, (g0+g1)%q]), hp, m, q, +1),
      member(np.concatenate([fm_true % q, (g0-g1) % q]), hm, m, q, -1))
# simulate recovered rows with a rotation offset to exercise alignment search
k0, l0 = 37, 101
cp = np.roll(fp_true, k0); cmm = np.roll(fm_true, l0)
fv, gv, flag = glue_and_decrypt(cp, cmm, h, ct, m=m, q=q, n=n, log=print)
print("glue+decrypt ->", flag)
print("GLUE CHECK:", "PASS" if flag == flag_bytes else "FAIL")

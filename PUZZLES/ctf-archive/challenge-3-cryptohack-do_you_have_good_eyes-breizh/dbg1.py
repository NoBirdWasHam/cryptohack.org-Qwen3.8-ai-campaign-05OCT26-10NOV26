import numpy as np, random, base64, gzip
from dist2 import *
rng = random.Random(7)
A = np.random.randint(0, Q, size=(K, L, N), dtype=np.int64)
s = np.array([[rng.randrange(-2, 3) % Q for _ in range(N)] for _ in range(L)], dtype=np.int64)
e = np.array([[rng.randrange(-2, 3) % Q for _ in range(N)] for _ in range(K)], dtype=np.int64)
Ahh, sh, eh = ntt(A), ntt(s), ntt(e)
th = np.zeros((K, N), dtype=np.int64)
for i in range(K):
    acc = eh[i].copy()
    for j in range(L):
        acc = (acc + Ahh[i][j] * sh[j]) % Q
    th[i] = acc
for m in range(6):
    B = [[int(Ahh[i][j][m]) for j in range(L)] for i in range(K)]
    w, v, n2 = dual_short_pair(B)
    cb = [sum(w[i] * B[i][j] for i in range(K)) % Q for j in range(L)]
    okc = all(cb[j] == v[j] % Q for j in range(L))
    val = modq(sum(w[i] * int(th[i][m]) for i in range(K)))
    shc = [modq(int(sh[j][m])) for j in range(L)]
    ehc = [modq(int(eh[i][m])) for i in range(K)]
    pred = sum(v[j] * shc[j] for j in range(L)) + sum(w[i] * ehc[i] for i in range(K))
    print(m, "congr_ok", okc, "norm", int(n2 ** 0.5), "val", val, "pred", pred,
          "predmod", modq(pred), "shn", int(sum(x * x for x in shc) ** .5),
          "wn", int(sum(x * x for x in w) ** .5))

# t280_gen_mid.py — planted NTRU benchmark instance n=256, q=127, df=dg=10.
# Convention identical to toy512_run.py (rows (e_i|s_i) + (0|q e_i), T(f)h=g).
import numpy as np, json, random, os
rng = random.Random(281107)
n, q, W = 256, 127, 10

def T(v):
    Mm = np.zeros((n, n), dtype=np.int64)
    for m in range(n):
        for i in range(n):
            Mm[m, i] = v[(m - i) % n]
    return Mm

def solve_modq(Amat, bvec):
    M2 = np.concatenate([Amat % q, (bvec % q).reshape(n, 1)], axis=1).astype(np.int64)
    for col in range(n):
        piv = next((rr for rr in range(col, n) if M2[rr, col] % q), None)
        if piv is None: return None
        M2[[col, piv]] = M2[[piv, col]]
        inv = pow(int(M2[col, col]), -1, q)
        M2[col] = (M2[col] * inv) % q
        colv = M2[:, col].copy()
        for rr in range(n):
            if rr != col and colv[rr]:
                M2[rr] = (M2[rr] - colv[rr] * M2[col]) % q
    return M2[:, n]

def rand01(d):
    v = np.zeros(n, dtype=np.int64)
    v[rng.sample(range(n), d)] = 1
    return v

f = g = h = None
while f is None:
    ft = rand01(W); gt = rand01(W)
    hh = solve_modq(T(ft), gt)
    if hh is not None:
        f, g, h = ft, gt, hh
rows = []
for i in range(n):
    e = np.zeros(n, dtype=np.int64); e[i] = 1
    s = np.zeros(n, dtype=np.int64)
    for m in range(n): s[m] = h[(m - i) % n]
    rows.append(np.concatenate([e, s]))
for i in range(n):
    e = np.zeros(n, dtype=np.int64); e[i] = q
    rows.append(np.concatenate([np.zeros(n, dtype=np.int64), e]))
with open("t280_mid256.fplll", "w") as fp:
    fp.write("[")
    for r_ in rows:
        fp.write("[ " + " ".join(str(int(x)) for x in r_) + " ]")
    fp.write(" ]\n")
json.dump({"f": f.tolist(), "g": g.tolist()}, open("t280_mid256_truth.json", "w"))
print("wrote t280_mid256.fplll", os.path.getsize("t280_mid256.fplll"), "planted norm2", 2 * W)

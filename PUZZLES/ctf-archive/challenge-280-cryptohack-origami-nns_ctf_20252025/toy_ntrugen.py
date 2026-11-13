# Toy NTRU instance (n=64,q=127,df=dg=5) -> fplll-format lattice + planted truth.
# Convention: conv(a,h)_m = sum_i a_i h[(m-i) mod n]; lattice {(a,b): b == conv(a,h) mod q}.
import numpy as np, json, random
rng = random.Random(20261103)
n, q = 64, 127

def T(v):  # convolution matrix: T[m, i] = v[(m-i)%n] so (T x)_m = conv(v,x)_m
    Mm = np.zeros((n, n), dtype=np.int64)
    for m in range(n):
        for i in range(n):
            Mm[m, i] = v[(m-i) % n]
    return Mm

def solve_modq(Amat, bvec):
    M2 = np.concatenate([Amat % q, (bvec % q).reshape(n, 1)], axis=1)
    for col in range(n):
        piv = next((rr for rr in range(col, n) if M2[rr, col] % q), None)
        if piv is None: return None
        M2[[col, piv]] = M2[[piv, col]]
        inv = pow(int(M2[col, col]), -1, q)
        M2[col] = M2[col] * inv % q
        for rr in range(n):
            if rr != col and M2[rr, col] % q:
                M2[rr] = (M2[rr] - M2[rr, col] * M2[col]) % q
    return M2[:, n]

def rand01(d):
    v = np.zeros(n, dtype=np.int64)
    v[rng.sample(range(n), d)] = 1
    return v

f = g = h = None
for _ in range(100000):
    ft = rand01(5); gt = rand01(5)
    hh = solve_modq(T(ft), gt)   # f*h = g
    if hh is not None:
        f, g, h = ft, gt, hh
        break
assert f is not None
d = 2 * n
rows = []
for i in range(n):
    e = np.zeros(n, dtype=np.int64); e[i] = 1
    s = np.zeros(n, dtype=np.int64)
    for m in range(n): s[m] = h[(m-i) % n]
    rows.append(np.concatenate([e, s]))
for i in range(n):
    e = np.zeros(n, dtype=np.int64); e[i] = q
    rows.append(np.concatenate([np.zeros(n, dtype=np.int64), e]))
with open("toy64.fplll", "w") as fp:
    fp.write("[")
    for r_ in rows:
        fp.write("[ " + " ".join(str(int(x)) for x in r_) + " ]")
    fp.write(" ]\n")
json.dump({"f": f.tolist(), "g": g.tolist(), "h": h.tolist(), "n": n, "q": q},
          open("toy64_truth.json", "w"))
chk = (T(f) @ h - g) % q
print("toy selfcheck f*h==g mod q:", bool(np.all(chk == 0)), " rows", len(rows))

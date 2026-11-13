# Verify the author's intended C3 linearization (rkm0959.tistory.com/247) against
# a local mimic of Generator3 from chal.py. No network.
import hashlib, time, numpy as np

def digits5(x):
    d = []
    for _ in range(64):
        d.append(x % 5); x //= 5
    return d

# monomial order: [k_j 0..63] [k_j^2 64..127] [k_j k_l, j<l 128..2143]
IDX = [[0]*64 for _ in range(64)]
cur = 64
for j in range(64):
    for l in range(j, 64):
        IDX[j][l] = cur; cur += 1
NV = cur  # 2144

INV = np.array([0,1,3,2,4], dtype=np.uint8)  # inverse mod5: 2->3, 3->2

def gf5_rref(A):
    # A int16 (m,n) values 0..4; returns pivot list, rank; in-place RREF
    A = A.astype(np.int16)
    m, n = A.shape; r = 0; piv = []
    for c in range(n):
        if r >= m: break
        nz = np.nonzero(A[r:, c])[0]
        if nz.size == 0: continue
        p = r + int(nz[0])
        if p != r: A[[r, p]] = A[[p, r]]
        A[r] = (A[r] * INV[A[r, c]]) % 5
        rows = np.nonzero(A[:, c])[0]
        rows = rows[rows != r]
        if rows.size:
            A[rows] = (A[rows] - np.outer(A[rows, c], A[r])) % 5
        piv.append(c); r += 1
    return piv, r, A

def try_key(seed, N):
    rng = np.random.default_rng(seed)
    k = [int(v) for v in rng.integers(0, 4, 64)]
    rows = []; rhs = []
    b_true = []
    for x in range(1, N+1):
        h = int.from_bytes(hashlib.sha256(str(x).encode()).digest(), "big")
        hd = digits5(h)
        b = (sum(k[i]*hd[i] for i in range(64)) % 5) % 2
        b_true.append(b)
        if b != 1: continue
        v = [0]*NV
        for j in range(64):
            v[j] += hd[j]                    # linear term S (coeff 1: S^2 + S = 2)
            v[IDX[j][j]] += hd[j]**2
            for l in range(j+1, 64):
                v[IDX[j][l]] += 2*hd[j]*hd[l]
        rows.append([c % 5 for c in v]); rhs.append(2)
    A = np.array(rows, dtype=np.uint8)
    bb = np.array(rhs, dtype=np.uint8)
    t0 = time.time()
    Aug = np.concatenate([A, bb[:, None]], axis=1)
    piv, rank, Aug = gf5_rref(Aug)
    consistent = not np.any((Aug[:, -1] != 0) & (Aug[:, :-1] == 0).all(axis=1))
    # particular solution: free vars = 0
    sol = np.zeros(NV, dtype=np.uint8)
    for i, c in enumerate(piv):
        if c < NV: sol[c] = Aug[i, -1]
    rank_coef = sum(1 for c in piv if c < NV)
    consistent = (NV not in piv)
    kh = [int(sol[j]) for j in range(64)]
    match = (kh == k)
    inbox = all(0 <= v <= 3 for v in kh)
    print(f"seed={seed} N={N} b1eq={len(rows)} rank={rank_coef}/{NV} consistent={consistent} "
          f"inbox={inbox} key_match={match} ({time.time()-t0:.1f}s)", flush=True)
    return match

for seed, N in [(1, 6000), (2, 6000), (3, 6000), (4, 12000), (5, 20000)]:
    try_key(seed, N)

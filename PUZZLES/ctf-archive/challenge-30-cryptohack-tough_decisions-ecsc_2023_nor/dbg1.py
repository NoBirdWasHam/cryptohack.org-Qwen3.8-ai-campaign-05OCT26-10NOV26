import ast, numpy as np

groups = [ast.literal_eval(l) for l in open("output.txt") if l.strip()]
n = len(groups)
A = np.zeros((n, 6, 16), dtype=np.int8)
B = np.zeros((n, 6), dtype=np.int8)
for i, g in enumerate(groups):
    for j, (a, b) in enumerate(g):
        A[i, j] = [x & 1 for x in a]
        B[i, j] = b & 1

# known prefix bits, LSB-first
prefix = b"crypto{"
pbits = [(c >> i) & 1 for c in prefix for i in range(8)]
npg = len(pbits)  # 56

masks = np.arange(1 << 16, dtype=np.int32)
M = ((masks[:, None] >> np.arange(16)[None, :]) & 1).astype(np.int8)

def group_match(mask):
    dot = (A.reshape(-1, 16) @ mask.reshape(16, 1)) & 1
    return ((dot.reshape(n, 6) == B).all(axis=1))

# real == bit1 hypothesis: real groups must ALL match. Score = number of consistent
# real groups - penalties? Use: real groups must match; fake groups may match (no penalty).
# fit over prefix groups in chunks
best = []
for lo in range(0, 1 << 16, 4096):
    Mc = M[lo:lo + 4096].astype(np.int32)
    d = (A[:npg].reshape(-1, 16) @ Mc.T) & 1  # (336, 4096)
    mt = (d.reshape(npg, 6, -1) == B[:npg, :, None]).all(axis=1)  # (npg,4096) all-6-match
    ones = np.array(pbits, dtype=bool)
    # hypothesis1: bit1 => real => must match. score1 = matches on real - mismatches on real
    good1 = mt[ones].sum(0) - (~mt[ones]).sum(0)
    # hypothesis2: bit0 => real
    good2 = mt[~ones].sum(0) - (~mt[~ones]).sum(0)
    top1 = np.argsort(good1)[-5:][::-1]
    top2 = np.argsort(good2)[-5:][::-1]
    for idx in top1:
        best.append(("h1", lo + int(idx), int(good1[idx])))
    for idx in top2:
        best.append(("h2", lo + int(idx), int(good2[idx])))
best.sort(key=lambda t: -t[2])
for b in best[:12]:
    print(b)

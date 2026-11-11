import ast, itertools, numpy as np

groups = []
with open("output.txt") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        g = ast.literal_eval(line)
        assert len(g) == 6
        groups.append(g)

n = len(groups)
A = np.zeros((n, 6, 16), dtype=np.uint8)
B = np.zeros((n, 6), dtype=np.uint8)
for i, g in enumerate(groups):
    for j, (a, b) in enumerate(g):
        A[i, j] = list(a)
        B[i, j] = b

# parity vectors over GF(2): dot(a,s) mod 2 = parity(a & s_low)
P = (A & 1).astype(np.int8).reshape(-1, 16)  # (n*6,16)
bpar = (B & 1).reshape(-1)

# brute force 2^16 LSB masks
masks = np.arange(1 << 16, dtype=np.int32)
M = ((masks[:, None] >> np.arange(16)[None, :]) & 1).astype(np.int8)  # (65536,16)
dot = P @ M.T  # (n*6, 65536) int8 sums 0..16
match = ((dot & 1) == np.repeat(bpar[:, None], 65536, axis=1)).reshape(n, 6, 65536).all(axis=1)
score = match.sum(axis=0)
best = int(np.argmax(score))
print("best mask:", best, "score", int(score[best]), "/", n, "runner-up:", int(np.sort(score)[-2]))

m = best
# recompute per-group match with chosen mask
def par(a):
    v = 0
    for j, x in enumerate(bytes(a)):
        v |= (x & 1) << j
    return bin(v & m).count("1") & 1
dec_bits = []
for g in groups:
    dec_bits.append(1 if all(par(a) == (b & 1) for a, b in g) else 0)

# bits are LSB-first per byte
out = bytearray()
for i in range(0, len(dec_bits), 8):
    byte = 0
    for k, bit in enumerate(dec_bits[i:i + 8]):
        byte |= bit << k
    out.append(byte)
print("raw decode:", out.decode("latin1"))

# errors only turn true-0 into 1 => true byte is a submask (bitwise subset) of decoded byte.
allowed = set(b"crypto{" + b"}abcdefghijklmnopqrstuvwxyz0123456789_")
bad = [i for i, c in enumerate(out) if c not in allowed]
print("bad positions:", bad)

def fixes(pos):
    byte = out[pos]
    res = []
    bitsset = [k for k in range(8) if (byte >> k) & 1]
    for r in range(0, len(bitsset) + 1):
        for combo in itertools.combinations(bitsset, r):
            nb = byte
            for k in combo:
                nb &= ~(1 << k)
            if nb in allowed:
                res.append((r, nb))
    res.sort()
    return res

cands = [fixes(p) for p in bad]
assert all(len(c) > 0 for c in cands), cands
total = 1
for c in cands:
    total *= len(c)
print("candidate combos:", total)
# choose min total-flips assignment, break ties by readable word heuristics
bestsol = None
import itertools as it
for combo in it.product(*cands):
    cost = sum(c[0] for c in combo)
    if bestsol is None or cost < bestsol[0]:
        bestsol = (cost, [c[1] for c in combo])
fixed = bytearray(out)
for p, v in zip(bad, bestsol[1]):
    fixed[p] = v
print("fixed:", fixed.decode("latin1"))

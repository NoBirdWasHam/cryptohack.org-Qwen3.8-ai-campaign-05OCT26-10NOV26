from spongebob import PBOXES, SBOX, INIT, permute, H, BLOCKSIZE

# 1. rows permutations? duplicates?
for b in range(8):
    r = PBOXES[b]
    print("row", b, "perm", sorted(r) == list(range(18)), "len", len(r))
print("dup rows:", len({tuple(r) for r in PBOXES}))

# 2. SBOX structure: affine test / fixpoints / cycle type
aff = all(SBOX[x ^ y] == (SBOX[x] ^ SBOX[y] ^ SBOX[0]) for x in range(256) for y in range(16))
print("SBOX affine(x,y<16):", aff)
print("fixpoints:", [x for x in range(256) if SBOX[x] == x])
seen = [False]*256; cyc = []
for x in range(256):
    if not seen[x]:
        c = 0; y = x
        while not seen[y]:
            seen[y] = True; y = SBOX[y]; c += 1
        cyc.append(c)
print("cycle lens:", sorted(cyc))

# 3. backward cones: bytes influencing byte j after k permute+SBOX rounds
Q = []
for b in range(8):
    inv = [0]*18
    for i, d in enumerate(PBOXES[b]):
        inv[d] = i
    Q.append(inv)

def backcone(S):
    out = set()
    for j in S:
        for b in range(8):
            out.add(Q[b][j])
    return out

cone = set(range(8, 18))
for k in range(8):
    cone = backcone(cone)
    print("cone size after", k+1, "backrounds:", len(cone), sorted(cone))

cone = set(range(18))
for k in range(8):
    cone = backcone(cone)
print("full->full cone sizes:", len(cone))

# 4. linear span of f(x)^f(0) for first-block map truncated to bytes 8..17
def oneround(m8):
    state = INIT[:]
    for i, c in enumerate(m8):
        state[i] ^= c
    for _ in range(8):
        state = permute(state)
        state = [SBOX[v] for v in state]
    return bytes(state)

import os, random
random.seed(1)
base = oneround(bytes(8))
basis = []
def addvec(v):  # v: int of 80 bits
    for bv in basis:
        v = min(v, v ^ bv)
        if v == 0: return False
    basis.append(v); return True

cnt = 0
for t in range(400):
    x = bytes(random.randrange(256) for _ in range(8))
    y = oneround(x)
    d = int.from_bytes(bytes(a ^ b for a, b in zip(y[8:], base[8:])), "big")
    if addvec(d): cnt += 1
    if cnt == 80: break
print("rank of f(x)^f(0) on bytes8..17 after", t+1, "samples:", cnt)

# 5. full-state span (144 bits)
basis2 = []
def addvec2(v):
    for bv in basis2:
        v = min(v, v ^ bv)
        if v == 0: return False
    basis2.append(v); return True
cnt2 = 0
for t in range(400):
    x = bytes(random.randrange(256) for _ in range(8))
    y = oneround(x)
    d = int.from_bytes(bytes(a ^ b for a, b in zip(y, base)), "big")
    if addvec2(d): cnt2 += 1
print("rank full state:", cnt2, "of 144 after", t+1, "samples")

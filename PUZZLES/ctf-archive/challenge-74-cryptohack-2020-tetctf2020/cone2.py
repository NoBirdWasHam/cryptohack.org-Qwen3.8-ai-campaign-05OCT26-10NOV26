# cone2.py — bit-exact GF(2) analysis: for every reveal pair, how many bits of
# the 2020th output are pinned? Uses full 624*32-bit coordinate masks, verified
# against real CPython random (local, no server).
import random
N = 624
MAGIC = 0x9908b0df
BITS = N * 32

# expr[slot][b] = int bitmask over 624*32 initial bits: bit b of current word
expr = [[0]*32 for _ in range(N)]
for j in range(N):
    for b in range(32):
        expr[j][b] = 1 << (32*j + b)

history = {}  # output index j -> tuple of 32 masks (word s_j at time of output)
for j in range(N):
    history[j] = tuple(expr[j])
for k in range(N, 2020):
    i0, i1, im1 = (k-624) % N, (k-623) % N, (k-1) % N
    e0, e1, em1 = expr[i0], expr[i1], expr[im1]
    new = []
    for b in range(32):
        if b == 31:
            m = e1[31]
        elif b == 30:
            m = e1[30] ^ e0[31]
        else:
            m = e1[b] ^ em1[b+2]
        if (MAGIC >> b) & 1:
            m = m ^ em1[0]
        new.append(m)
    expr[k % N] = new
    history[k] = tuple(new)

def eval_masks(masks, s0):
    v = 0
    for b in range(32):
        bit, mm = 0, masks[b]
        while mm:
            lb = mm & -mm
            idx = lb.bit_length() - 1
            bit ^= (s0[idx >> 5] >> (idx & 31)) & 1
            mm ^= lb
        v |= bit << b
    return v

# verify against CPython's MT19937: outputs 0..2019 of random.Random(seed)
def outputs(seed, n=2020):
    r = random.Random(seed)
    return [r.getrandbits(32) for _ in range(n)]

def untemper(y):
    y &= 0xffffffff
    y ^= y >> 18
    x2 = y
    for _ in range(4):
        x2 = y ^ ((x2 << 15) & 0xefc60000)
    x = x2 & 0xffffffff
    x2 = x
    for _ in range(6):
        x2 = x ^ ((x2 << 7) & 0x9d2c5680)
    x = x2 & 0xffffffff
    x2 = x
    for _ in range(6):
        x2 = x ^ (x2 >> 11)
    return x2 & 0xffffffff

for seed in (1, 2, 3):
    s0 = list(random.Random(seed).getstate()[1][:N])
    outs = outputs(seed)
    assert [untemper(o) for o in outs[:N]] == s0, "untemper/recover mismatch"
    # verify history masks == actual word s_j for j>=624 via real sim
    s = list(s0)
    sim = {}
    for k in range(N, 2020):
        y = (s[(k-624)%N] & 0x80000000) | (s[(k-1)%N] & 0x7fffffff)
        s[k % N] = s[(k-623)%N] ^ (y>>1) ^ (MAGIC if y&1 else 0)
        sim[k] = s[k % N]
    for k in (624, 1396, 2018, 2019):
        # actual word s_k from seed: outputs 0..623 give s0; then sim gives s_k
        assert eval_masks(history[k], s0) == sim[k], (seed, k)
print("history masks verified vs CPython MT19937: OK")

# --- span analysis: candidate reveal indices near the target cone ---
def rowspace_reduce(rows):
    basis = {}
    for r in rows:
        while r:
            p = r.bit_length() - 1
            if p in basis: r ^= basis[p]
            else: basis[p] = r; break
    return basis

def in_span(vec, basis):
    while vec:
        p = vec.bit_length() - 1
        if p not in basis: return False
        vec ^= basis[p]
    return True

T = list(history[2019])  # 32 rows of the target word
Tbasis = rowspace_reduce(T)

cands = sorted(set(list(range(1390, 1402)) + list(range(2012, 2019)) +
                   list(range(766, 780)) + list(range(140, 155)) +
                   list(range(760, 766)) + list(range(2010, 2013))))
best = (0, None)
for ai, a in enumerate(cands):
    Ra = rowspace_reduce(list(history[a]))
    for b in cands[ai+1:]:
        K = rowspace_reduce(list(history[a]) + list(history[b]))
        pin = sum(1 for t in T if in_span(t, K))
        # pinned rows count (rows in T that lie in span K) — conservative per-row
        if pin > best[0]:
            best = (pin, (a, b))
print("best pinned target-bit rows over candidate pairs:", best)

# explicit check of the {1396,2018} claim
K = rowspace_reduce(list(history[1396]) + list(history[2018]))
pin = [b for b, t in enumerate(T) if in_span(t, K)]
print("pair(1396,2018) pinned bit rows:", pin)

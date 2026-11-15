# Exact GF(2) dependency-cone of MT19937 output #2019 (the "2020th number")
# in terms of the 624 initial state words. Determines whether ANY choice of
# 2 revealed outputs can pin any bit of the target (i.e. give > 2^-32 odds).
# Representation: word w's bits tracked as a set of source-word indices
# (bit-level exactness via per-bit GF(2) masks over 624 words).

N = 624
MAGIC = 0x9908b0df

# expr[j] = list of 32 bitmasks (Python int over 624 bits) for current word j
expr = [ [1 << j for _ in range(32)] for j in range(N) ]

def twist(k):
    # s_k = s_{k-623} ^ (y>>1) ^ (MAGIC if y&1 else 0);  y = (s_{k-624}&0x80000000)|(s_{k-1}&0x7fffffff)
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
        if b == 0 or b == 4:  # MAGIC bit set => ^= LSB of s_{k-1}
            if (MAGIC >> b) & 1:
                m = m ^ em1[0]
        new.append(m)
    expr[im1] = new  # k % N == (k-1) is wrong; recompute below
    return new

# careful: s_k overwrites slot k % N
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

def real_s2019(s0):
    s = list(s0)
    for k in range(N, 2020):
        y = (s[(k-624) % N] & 0x80000000) | (s[(k-1) % N] & 0x7fffffff)
        s[k % N] = s[(k-623) % N] ^ (y >> 1) ^ (MAGIC if (y & 1) else 0)
    return s[2019 % N]

target = expr[2019 % N]

# verify symbolic masks against real MT19937 on random states
import random as _r
for t in range(5):
    s0 = [_r.getrandbits(32) for _ in range(N)]
    want = real_s2019(s0)
    got = 0
    for b in range(32):
        bit, mm = 0, target[b]
        while mm:
            lb = mm & -mm
            bit ^= (s0[lb.bit_length()-1] >> b) & 1
            mm ^= lb
        got |= bit << b
    assert got == want, (t, hex(got), hex(want))
print("cone math verified against real MT19937: OK")
for b in range(32):
    m = target[b]
    words = [j for j in range(N) if (m >> j) & 1]
    print(f"bit {b:2d}: depends on {len(words)} initial words: {words}")

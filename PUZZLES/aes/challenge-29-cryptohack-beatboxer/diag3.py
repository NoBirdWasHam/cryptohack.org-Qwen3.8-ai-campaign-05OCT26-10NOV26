src = open("13406_provided.py").read()
ns = {}
exec(src[src.index("class AES"):src.index("class Challenge")], ns)
tb = list(ns["AES"].sbox)

# ---- compute the REAL AES S-box from first principles ----
def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1: p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi: a ^= 0x1b
        b >>= 1
    return p
def ginverse(x):
    if x == 0: return 0
    # x^254 in GF(2^8)
    r = x
    for _ in range(253):
        r = gmul(r, x)
    return r
def real_sbox(x):
    if x == 0: y = 0
    else: y = ginverse(x)
    # affine transform: y XOR rotl(y,1) XOR rotl(y,2) XOR rotl(y,3) XOR rotl(y,4) XOR 0x63
    res = y
    for k in range(1, 5):
        rot = ((y << k) | (y >> (8 - k))) & 0xff
        res ^= rot
    return res ^ 0x63
REAL = [real_sbox(x) for x in range(256)]
# sanity: known values
assert REAL[0] == 0x63, hex(REAL[0])
assert REAL[1] == 0x7c, hex(REAL[1])
assert REAL[0x53] == 0xd1, hex(REAL[0x53])
print("real sbox check passed (S[0]=0x63,S[1]=0x7c,S[0x53]=0xd1)")
print("tb == REAL:", tb == REAL)

# ---- test: tb = p o REAL for a fixed output permutation p? ----
# i.e., exists perm p s.t. tb[x] = p[REAL[x]]
# This holds iff the map REAL[x] -> tb[x] is a function of REAL[x] alone (well-defined).
def is_composition(f, g):
    # exists perm p with f[x] = p[g[x]] for all x  <=>  g[x1]==g[x2] => f[x1]==f[x2]
    m = {}
    for x in range(256):
        if g[x] in m and m[g[x]] != f[x]:
            return False
        m[g[x]] = f[x]
    # also g must be a permutation (it is) so p is a permutation
    return len(set(m.values())) == 256
print("tb = p o REAL (output-conjugate of real):", is_composition(tb, REAL))
print("tb = REAL o p (input-conjugate of real):", is_composition(REAL, tb))

# ---- test affine conjugacy: tb = A o REAL o Ainv with A affine x-> Mx^c ----
# Too many affine maps (GL(8,2) huge). Test a cheap necessary condition:
# differential uniformity. Compute max delta count for tb and for REAL.
def max_diff(sbox):
    best = 0
    from collections import Counter
    for dx in range(1, 256):
        cnt = Counter()
        for x in range(256):
            cnt[sbox[x] ^ sbox[x ^ dx]] += 1
        best = max(best, max(cnt.values()))
    return best
print("max differential uniformity: tb =", max_diff(tb), " REAL =", max_diff(REAL), "(real AES = 4)")

# ---- linear structure: max Walsh for tb ----
def max_linear(sbox):
    best = 0
    for a in range(256):
        for b in range(256):
            # parity of popcount(a & x) vs popcount(b & sbox[x])
            bal = 0
            for x in range(256):
                pa = bin(a & x).count("1") & 1
                pb = bin(b & sbox[x]).count("1") & 1
                bal += (1 if pa == pb else -1)
            best = max(best, abs(bal))
    return best
print("max linear bias (Walsh): tb =", max_linear(tb), " (real AES max = 16? actually 2^? )")
print("  (a linear map would give 256; a secure S-box gives small)")

# ---- is tb a composition of REAL with a fixed XOR? tb[x] = REAL[x] ^ c ----
xs = [tb[x] ^ REAL[x] for x in range(256)]
print("tb = REAL ^ const:", len(set(xs)) == 1)
# ---- is tb[x] = REAL[x] with byte-bit-reversal? ----
def bitrev(x):
    r = 0
    for i in range(8):
        if x & (1 << i): r |= 1 << (7 - i)
    return r
print("tb = bitrev(REAL):", all(tb[x] == bitrev(REAL[x]) for x in range(256)))
print("tb = REAL[bitrev(x)]:", all(tb[x] == REAL[bitrev(x)] for x in range(256)))

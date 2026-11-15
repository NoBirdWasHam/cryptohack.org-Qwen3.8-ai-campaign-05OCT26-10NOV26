import mmh3, random
random.seed(3)
M = 2**32 - 5
def dig(b, i): return mmh3.hash(b, i) % M

# byte-sensitivity at length 256
base = bytes(random.randrange(256) for _ in range(256))
h0 = mmh3.hash(base, 0)
insens = []
for j in (0,1,3,4,60,63,64,67,127,128,129,191,192,250,251,252,253,254,255):
    b2 = bytearray(base); b2[j] ^= 0xFF
    if mmh3.hash(bytes(b2), 0) == h0: insens.append(j)
print("insensitive positions (len256, seed0):", insens)

# all-zeros vs all-ff at 256
print("zeros==ffs:", mmh3.hash(b'\x00'*256,0) == mmh3.hash(b'\xff'*256,0))

# digest collisions among server-style random keys (expect ~0.3 total over all pairs)
# and: do digests ever collide WITH a fixed small set / near-multiples of 2^31?
random.seed(9)
keys = [bytes(random.randrange(256) for _ in range(256)) for _ in range(300)]
D = set()
clash = 0
for r in keys:
    for i in range(47):
        d = dig(r, i)
        if d in D: clash += 1
        D.add(d)
print("sample |S|:", len(D), "expected:", 300*47, "collisions:", clash)

# KEY structural test: for FIXED key K, set of digests = fmix(Phi_K(seed)).
# Check: does digest depend only on (seed) for some special K, e.g. K=zero-blocks?
K = b'\x00'*32
ds = [dig(K,i) for i in range(47)]
print("zero32 distinct digests:", len(set(ds)))
# check affine-in-seed relation: d_i ^ d_0 patterns? print few
print("first 4:", ds[:4])
# length aliasing: same first 32 bytes, different lengths 32/36/64/256?
K36 = K + b'\x00'*4
print("len32==len36 (zeros):", mmh3.hash(K,0)==mmh3.hash(K36,0))
# trailing junk sensitivity for len-256 key with zeros tail
b2 = bytearray(K); # change byte 255
b2[255] = 1
print("byte255 matters:", mmh3.hash(bytes(bytearray(K)),0) != mmh3.hash(bytes(b2),0))

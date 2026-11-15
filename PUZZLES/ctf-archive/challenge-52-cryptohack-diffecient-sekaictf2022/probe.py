import mmh3, random, math, struct

M32 = 0xFFFFFFFF
def rotl(x, r): return ((x << r) | (x >> (32 - r))) & M32

def murmur3_32(data: bytes, seed: int) -> int:
    c1, c2, c3 = 0xCC9E2D51, 0x1B873593, 0xE6546B64
    h = seed & M32
    L = len(data)
    nblocks = L // 4
    for i in range(nblocks):
        k = struct.unpack_from('<I', data, i*4)[0]
        k = (k * c1) & M32; k = rotl(k, 15); k = (k * c2) & M32; k = rotl(k, 13)
        h = (h + k) & M32; h = rotl(h, 3); h = (h*5 + c3) & M32
    tail = data[nblocks*4:]
    k = 0
    if len(tail) >= 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]
        k = (k * c1) & M32; k = rotl(k, 15); k = (k * c2) & M32; h = (h + k) & M32
    h ^= L
    h ^= h >> 16; h = (h * 0x85EBCA6B) & M32
    h ^= h >> 13; h = (h * 0xC2B2AE35) & M32
    h ^= h >> 16
    return h

def to_signed(h):
    return h - (1 << 32) if h >= (1 << 31) else h

# 1) compare pure vs mmh3 on random data/seeds
random.seed(1)
bad = 0
for t in range(300):
    ln = random.choice([0,1,2,3,4,5,31,32,33,64,256,259])
    d = bytes(random.randrange(256) for _ in range(ln))
    s = random.choice([0,1,7,46,12345,2**31-1])
    mine = to_signed(murmur3_32(d, s))
    theirs = mmh3.hash(d, s)
    if mine != theirs:
        bad += 1
        if bad <= 5: print("MISMATCH len", ln, "seed", s, mine, theirs)
print("mismatches:", bad, "/300")

# 2) seeds 0..46 distinct for one data?
b = b'x'*40
ds = [mmh3.hash(b, i) for i in range(47)]
print("seed-distinct:", len(set(ds)) == 47)

# 3) pairwise-digest-collision stats across seeds (look for seed-aliasing bug)
hits = 0; trials = 3000
for t in range(trials):
    d = bytes(random.randrange(256) for _ in range(32))
    dig = [mmh3.hash(d, i) for i in range(47)]
    if len(set(dig)) < 47: hits += 1
print("keys with any two equal digests:", hits, "/", trials)

# 4) trailing-zero sensitivity
a = b"A"*32
print("ztail-equal:", mmh3.hash(a,0) == mmh3.hash(a+b"\x00"*4, 0))
print("prefix-equal:", mmh3.hash(a,0) == mmh3.hash(a+b"B", 0))

# 5) simulated DB init stats (how many keys until security<=768)
def security(i, m=2**32-5, k=47):
    fp = pow(1 - pow(math.e, -k*i/m), k)
    try: return int(1/fp).bit_length()
    except (ZeroDivisionError, OverflowError): return float('inf')
i = 0
while security(i) > 768: i += 1
print("i:", i, "security:", security(i), "raw digests:", 47*i)

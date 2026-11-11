import mmh3, random, struct
M32 = 0xFFFFFFFF
def rotl(x, r): return ((x << r) | (x >> (32 - r))) & M32
def fmix(h):
    h ^= h >> 16; h = (h * 0x85EBCA6B) & M32
    h ^= h >> 13; h = (h * 0xC2B2AE35) & M32
    h ^= h >> 16; return h
def murmur(data, seed, startXor, endXor):
    c1, c2, c3 = 0xCC9E2D51, 0x1B873593, 0xE6546B64
    L = len(data); h = seed & M32
    if startXor: h ^= L
    for i in range(L // 4):
        k = struct.unpack_from('<I', data, i*4)[0]
        k = (k * c1) & M32; k = rotl(k, 15); k = (k * c2) & M32
        h ^= k; h = rotl(h, 13); h = (h*5 + c3) & M32
    tail = data[(L//4)*4:]; k = 0
    if len(tail) >= 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]; k = (k * c1) & M32; k = rotl(k, 15); k = (k * c2) & M32
        h ^= k
    if endXor: h ^= L
    return fmix(h)
def to_signed(h): return h - (1<<32) if h >= (1<<31) else h
random.seed(2)
samples = []
for t in range(120):
    ln = random.choice([0,1,2,3,4,5,31,32,33,64,256,259])
    d = bytes(random.randrange(256) for _ in range(ln))
    s = random.choice([0,1,7,46,12345])
    samples.append((d, s, mmh3.hash(d, s)))
for sx in (0,1):
    for ex in (0,1):
        bad = sum(1 for d,s,ref in samples if to_signed(murmur(d,s,sx,ex)) != ref)
        print(f"startXor={sx} endXor={ex}: mismatches {bad}/{len(samples)}")

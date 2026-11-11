# diffecient: differential tail-collision — find K0 != K1 with IDENTICAL 47-seed
# digest sets. murmur3 x86_32: dig_i(K) = fmix(Phi_K(seed) ^ mix32(tail) ^ len).
# Same 4-byte-aligned prefix P, tails a (3 bytes) / b (2 bytes):
#   D(K1)==D(K0)  iff  mix32(a) ^ mix32(b) == (4n+3)^(4n+2) == 1
# Search a<2^24, b=mix32^-1(mix32(a)^1) < 2^16. Then verify with mmh3.
import time
import mmh3

M = 0xFFFFFFFF
C1, C2 = 0xCC9E2D51, 0x1B873593
INV_C1 = pow(C1, -1, 2**32)
INV_C2 = pow(C2, -1, 2**32)

def mix32(x):
    x = (x * C1) & M
    x = ((x << 15) | (x >> 17)) & M
    return (x * C2) & M

def inv_mix32(y):
    y = (y * INV_C2) & M
    y = ((y >> 15) | (y << 17)) & M
    return (y * INV_C1) & M

# fast numpy scan (small chunks, <=2 threads safe)
import numpy as np
found = None
t0 = time.time()
STEP = 1 << 20
for start in range(0, 1 << 24, STEP):
    a = np.arange(start, start + STEP, dtype=np.int64)
    v = (a * C1) & M
    v = ((v << 15) | (v >> 17)) & M
    v = (v * C2) & M
    b = (v ^ 1) * INV_C2 & M
    b = ((b >> 15) | (b << 17)) & M
    b = (b * INV_C1) & M
    hits = np.nonzero(b < 65536)[0]
    if len(hits):
        i = int(hits[0])
        found = (start + i, int(b[i]))
        break
print("scan time %.1fs" % (time.time() - t0), "found:", found)
assert found

av, bv = found
# sanity with pure python
assert mix32(av) ^ mix32(bv) == 1
assert av < (1 << 24) and bv < (1 << 16)

prefix = b"Ab3!sekai-diffecient-collide-PAD"[:32]
assert len(prefix) == 32
K1 = prefix + av.to_bytes(3, "little")   # admin key, len 35
K0 = prefix + bv.to_bytes(2, "little")   # added key,  len 34
assert K0 != K1

# THE critical check: identical digest sets under the actual library
d0 = [mmh3.hash(K0, i) % (2**32 - 5) for i in range(47)]
d1 = [mmh3.hash(K1, i) % (2**32 - 5) for i in range(47)]
print("digest sets equal:", d0 == d1)
if d0 != d1:
    bad = [i for i in range(47) if d0[i] != d1[i]]
    print("MISMATCH seeds:", bad[:10])
    raise SystemExit(1)

# admin regex replay
import re
for pat in [b".{32,}", b"(?=.*[a-z])", b"(?=.*[A-Z])", br"(?=.*\d)", br"(?=.*\W)"]:
    print("regex", pat, bool(re.match(pat, K1)))

print("K0_HEX", K0.hex())
print("K1_HEX", K1.hex())

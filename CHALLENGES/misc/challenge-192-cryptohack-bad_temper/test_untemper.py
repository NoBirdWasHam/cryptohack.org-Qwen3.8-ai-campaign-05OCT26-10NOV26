import random
def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x00007fff
    x ^= (x << 15) & 0x80000000
    x ^= x >> 18
    return x & 0xffffffff

# Candidate 1: "well-known" formula
def untemper_known(y):
    x = y
    x ^= x >> 18
    x ^= (x << 19) & 0x7fff8000
    x ^= (x << 15) & 0x80000000
    x ^= (x << 7) & 0x00007fff
    x ^= x >> 11
    return x & 0xffffffff

# Candidate 2: bit-accurate general inverses
def inv_rshift_xor(y, s):
    x = y
    m = s
    while m < 32:
        x ^= y >> m
        m *= 2
    return x & 0xffffffff
def inv_lshift_xor(y, s, mask):
    x = [ (y>>i)&1 for i in range(32) ]
    for i in range(s, 32):
        if (mask>>i)&1:
            x[i] ^= x[i-s]
    return sum(x[i]<<i for i in range(32)) & 0xffffffff
def untemper_acc(y):
    x = inv_rshift_xor(y, 18)                 # undo step4 (x ^= x>>18)
    x = inv_lshift_xor(x, 15, 0x80000000)     # undo step3
    x = inv_lshift_xor(x, 7, 0x00007fff)      # undo step2
    x = inv_rshift_xor(x, 11)                 # undo step1 (x ^= x>>11)
    return x

r = random.Random(7)
words = [r.getrandbits(32) for _ in range(2000)]
k1 = all(untemper_known(temper(w))==w for w in words)
k2 = all(untemper_acc(temper(w))==w for w in words)
print("known formula roundtrip:", k1)
print("accurate roundtrip     :", k2)

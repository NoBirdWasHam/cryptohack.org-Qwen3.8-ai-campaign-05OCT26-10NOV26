import random
def inv_rshift_xor(y, s):
    x = y; m = s
    while m < 32:
        x ^= y >> m; m *= 2
    return x & 0xffffffff
def inv_lshift_xor(y, s, mask):
    x = [ (y>>i)&1 for i in range(32) ]
    for i in range(s, 32):
        if (mask>>i)&1:
            x[i] ^= x[i-s]
    return sum(x[i]<<i for i in range(32)) & 0xffffffff
def untemper(y):
    x = inv_rshift_xor(y, 18)
    x = inv_lshift_xor(x, 15, 0x80000000)
    x = inv_lshift_xor(x, 7, 0x00007fff)
    x = inv_rshift_xor(x, 11)
    return x
def twist(mt):
    n=624; mt=mt[:]
    for i in range(n):
        y=(mt[i]&0x80000000)|(mt[(i+1)%n]&0x7fffffff)
        mt[i]=mt[(i+397)%n]^(y>>1)^(0x9908b0df if y&1 else 0)
    return mt

# Verify my twist matches CPython exactly.
r=random.Random(42)
for _ in range(624): r.getrandbits(32)
state_before = r.getstate()[1]   # array just before word #624 is generated
r.getrandbits(32)                  # generate word #624 (index 624) -> triggers twist
state_after = r.getstate()[1]
tw = twist(list(state_before))
match = all(tw[i]==state_after[i] for i in range(624))
print("twist matches CPython:", match)
if not match:
    bad=[i for i in range(624) if tw[i]!=state_after[i]]
    print("num mismatch", len(bad), "first few", bad[:5])
    for i in bad[:3]:
        print(i, hex(tw[i]), hex(state_after[i]))

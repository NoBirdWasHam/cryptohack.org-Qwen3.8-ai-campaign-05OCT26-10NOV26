import random
def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x00007fff
    x ^= (x << 15) & 0x80000000
    x ^= x >> 18
    return x & 0xffffffff

# Find which array index j yields word0 = temper(A[j])
r=random.Random(7)
for _ in range(624): r.getrandbits(32)
st=r.getstate()
A=list(st[1])[:624]
w0=r.getrandbits(32)
# search all j
matches=[j for j in range(624) if temper(A[j])==w0]
print("j with temper(A[j])==word0:", matches)
# also check next word
w1=r.getrandbits(32)
matches1=[j for j in range(624) if temper(A[j])==w1]
print("j for word1:", matches1)

import random, struct
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
def words_of(b): return list(struct.unpack('<8I', b))

C=108
oracle=random.Random(); oracle.seed(b'\x42'*32)
first_seed=oracle.randbytes(32)
calls=[oracle.randbytes(32) for _ in range(C)]
allw=[]
for b in calls: allw+=words_of(b)   # positions 8..871
# ground truth: capture mt0 = state just before 624th word
g=random.Random(); g.seed(b'\x42'*32)
g.randbytes(32)                       # words 0..7
for _ in range(77): g.randbytes(32)   # words 8..623
mt0_true=list(g.getstate()[1])        # pre-twist array at word 624
print("mt0_true[0..7]", [hex(x) for x in mt0_true[:8]])

mt0=[0]*624
for i in range(616): mt0[8+i]=untemper(allw[i])     # positions 8..623
mt2=[untemper(allw[616+i]) for i in range(248)]     # positions 624..871
def yterm(mt0,i): return (mt0[i]&0x80000000)|(mt0[(i+1)%624]&0x7fffffff)
for j in range(8):
    i=227+j; y=yterm(mt0,i)
    mt0[j]=(mt2[i]^(y>>1)^(0x9908b0df if y&1 else 0))&0xffffffff
print("recovered mt0[0..7]", [hex(x) for x in mt0[:8]])
print("match [0..7]:", mt0[:8]==mt0_true[:8])
print("match [8..623]:", mt0[8:624]==mt0_true[8:624])
bad=[i for i in range(8,624) if mt0[i]!=mt0_true[i]]
print("mismatch count in [8..623]:", len(bad), bad[:5])
mt2c=twist(mt0)
bad2=[i for i in range(248) if mt2c[i]!=mt2[i]]
print("mt2 mismatch:", len(bad2), bad2[:5])

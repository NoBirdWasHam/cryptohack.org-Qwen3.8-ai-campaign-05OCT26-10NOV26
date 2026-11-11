import random, struct
def inv_rshift_xor(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&0xffffffff
def inv_lshift_xor(y,s,mask):
    x=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: x[i]^=x[i-s]
    return sum(x[i]<<i for i in range(32))&0xffffffff
def untemper(y):
    x=inv_rshift_xor(y,18)
    x=inv_lshift_xor(x,15,0xefc60000)
    x=inv_lshift_xor(x,7,0x9d2c5680)
    x=inv_rshift_xor(x,11)
    return x
def temper(x):
    x^=x>>11; x^=(x<<7)&0x9d2c5680; x^=(x<<15)&0xefc60000; x^=x>>18
    return x&0xffffffff
def twist(mt):
    n=624;mt=mt[:]
    for i in range(n):
        y=(mt[i]&0x80000000)|(mt[(i+1)%n]&0x7fffffff)
        mt[i]=mt[(i+397)%n]^(y>>1)^(0x9908b0df if y&1 else 0)
    return mt
def words_of(b): return list(struct.unpack('<8I',b))

C=110
oracle=random.Random(); oracle.seed(b'\x42'*32)
first_seed=oracle.randbytes(32)
calls=[oracle.randbytes(32) for _ in range(C)]
obs=[]
for b in calls: obs+=words_of(b)

# TRUE A0: capture after exactly 624 words (pos=624, array=pre-twist)
g=random.Random(); g.seed(b'\x42'*32)
for _ in range(624): g.getrandbits(32)
A0t=list(g.getstate()[1][:624])

# TRUE A1[227..234]: capture after 624+235=859 words (array=A1, pos=235)
g2=random.Random(); g2.seed(b'\x42'*32)
for _ in range(859): g2.getrandbits(32)
A1t=list(g2.getstate()[1][:624])
print("A1 pos check (should be 235):", g2.getstate()[1][624])

# My recovery
A0=[0]*624
for p in range(8,624): A0[p]=untemper(obs[p-8])
A1=[untemper(obs[(624+k)-8]) for k in range(235)]
for k in range(8):
    i=227+k
    yt=(A0[i]&0x80000000)|(A0[(i+1)%624]&0x7fffffff)
    A0[k]=(A1[i]^(yt>>1)^(0x9908b0df if (yt&1) else 0))&0xffffffff

print("\nA0_true[0..7]:", [hex(x) for x in A0t[:8]])
print("A0_rec[0..7]:", [hex(x) for x in A0[:8]])
print("A1_true[227..234]:", [hex(x) for x in A1t[227:235]])
print("A1_rec[227..234]:", [hex(x) for x in A1[227:235]])
print("A1_rec==A1_true[0..234]:", A1[:235]==A1t[:235])
bad1=[k for k in range(235) if A1[k]!=A1t[k]]
print("A1 mismatches:", len(bad1), bad1[:10])
print("A0[8..623] match:", A0[8:]==A0t[8:])

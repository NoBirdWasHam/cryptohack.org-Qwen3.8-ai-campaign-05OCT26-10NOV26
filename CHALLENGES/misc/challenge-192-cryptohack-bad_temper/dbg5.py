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
    x=inv_lshift_xor(x,15,0x80000000)
    x=inv_lshift_xor(x,7,0x00007fff)
    x=inv_rshift_xor(x,11)
    return x
def words_of(b): return list(struct.unpack('<8I',b))

C=110
oracle=random.Random(); oracle.seed(b'\x42'*32)
first_seed=oracle.randbytes(32)
calls=[oracle.randbytes(32) for _ in range(C)]
obs=[]
for b in calls: obs+=words_of(b)   # positions 8..875

# TRUE pre-twist array: fresh oracle, generate 624 words -> pos=624, array=A0
g=random.Random(); g.seed(b'\x42'*32)
g.randbytes(32)                 # words 0..7
for _ in range(77): g.randbytes(32)  # words 8..623 (616 words)
st=g.getstate()
A0_true=list(st[1][:624])       # pre-twist array, pos should be 624
print("pos after 624 words:", st[1][624])
print("len inner:", len(st[1]))

# Recover
A0=[0]*624
for p in range(8,624):
    A0[p]=untemper(obs[p-8])
A1=[untemper(obs[(624+k)-8]) for k in range(235)]
for k in range(8):
    i=227+k
    yt=(A0[i]&0x80000000)|(A0[(i+1)%624]&0x7fffffff)
    A0[k]=(A1[i]^(yt>>1)^(0x9908b0df if (yt&1) else 0))&0xffffffff

bad=[p for p in range(624) if A0[p]!=A0_true[p]]
print("A0 mismatches:", len(bad), "first:", bad[:8])
# check a specific known one: A0[8] should = untemper(word8) = untemper(obs[0])
print("A0[8] recover==true:", A0[8]==A0_true[8])
print("A0[8] recover:", hex(A0[8]), "true:", hex(A0_true[8]))

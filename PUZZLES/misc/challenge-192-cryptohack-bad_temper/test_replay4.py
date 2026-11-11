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
def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x00007fff
    x ^= (x << 15) & 0x80000000
    x ^= x >> 18
    return x & 0xffffffff
def twist(mt):
    n=624; mt=mt[:]
    for i in range(n):
        y=(mt[i]&0x80000000)|(mt[(i+1)%n]&0x7fffffff)
        mt[i]=mt[(i+397)%n]^(y>>1)^(0x9908b0df if y&1 else 0)
    return mt
class MT:
    def __init__(self, init): self.state=list(init); self.pos=0
    def gen(self):
        if self.pos>=624: self.state=twist(self.state); self.pos=0
        y=self.state[self.pos]; self.pos+=1
        return temper(y)
def words_of(b): return list(struct.unpack('<8I', b))
def bytes_of_words(ws): return b''.join(struct.pack('<I', w) for w in ws)

def recover(mt_known, mt2):
    # mt_known: A0 with [8..623] filled (from untemper), A0[0..7]=0
    # mt2: A1[0..247] = twist(A0)[0..247]
    # For i=227..234 (i+397)%624 = i-227 = k: A1[i] = A0[i-227] ^ (yterm(A0,i)>>1) ^ const
    # yterm(A0,i) = (A0[i]&0x80000000)|(A0[(i+1)%624]&0x7fffffff)  -- fully known (i in 227..234)
    A0=mt_known[:]
    for k in range(8):
        i=227+k
        yt=(A0[i]&0x80000000)|(A0[(i+1)%624]&0x7fffffff)
        A0[k]=(mt2[i]^(yt>>1)^(0x9908b0df if (yt&1) else 0))&0xffffffff
    return A0

C=108
oracle=random.Random(); oracle.seed(b'\x42'*32)
first_seed=oracle.randbytes(32)
calls=[oracle.randbytes(32) for _ in range(C)]
allw=[]
for b in calls: allw+=words_of(b)
mt0=[0]*624
for i in range(616): mt0[8+i]=untemper(allw[i])     # A0[8..623]
mt2=[untemper(allw[616+i]) for i in range(248)]     # A1[0..247]
A0=recover(mt0,mt2)
# verify twist
assert twist(A0)[0:248]==mt2, "twist check failed"
print("twist check OK")
mt=MT(A0)
fs=bytes_of_words([mt.gen() for _ in range(8)])
print("first_seed match:", fs==first_seed)
got=bytes_of_words([mt.gen() for _ in range(8*C)])
print("calls match:", got==b''.join(calls))
wallet=bytes_of_words([mt.gen() for _ in range(8)])
real_wallet=oracle.randbytes(32)
print("wallet match:", wallet==real_wallet)
print("wallet hex:", wallet.hex())

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
def words_of(b): return list(struct.unpack('<8I', b))
def bytes_of_words(ws): return b''.join(struct.pack('<I', w) for w in ws)

C=108
oracle=random.Random(); oracle.seed(b'\x42'*32)
first_seed=oracle.randbytes(32)                 # words 0..7
calls=[oracle.randbytes(32) for _ in range(C)]  # words 8..871

allw=[]
for b in calls: allw+=words_of(b)
mt0=[0]*624
for i in range(616): mt0[8+i]=untemper(allw[i])
mt2=[untemper(allw[616+i]) for i in range(248)]
def yterm(mt0,i): return (mt0[i]&0x80000000)|(mt0[(i+1)%624]&0x7fffffff)
for j in range(8):
    i=227+j; y=yterm(mt0,i)
    mt0[j]=(mt2[i]^(y>>1)^(0x9908b0df if y&1 else 0))&0xffffffff

r2=random.Random(); r2.setstate((3, list(mt0), 0))
fs=bytes_of_words([r2.getrandbits(32) for _ in range(8)])
print("first_seed match:", fs==first_seed)
got=bytes_of_words([r2.getrandbits(32) for _ in range(8*C)])
print("calls match:", got==b''.join(calls))
wallet=bytes_of_words([r2.getrandbits(32) for _ in range(8)])
real_wallet=oracle.randbytes(32)
print("wallet match:", wallet==real_wallet)
print("wallet hex:", wallet.hex())
print("first hex :", fs.hex())

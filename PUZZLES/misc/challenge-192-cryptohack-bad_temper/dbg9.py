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
def bytes_of_words(ws): return b''.join(struct.pack('<I',w) for w in ws)

C=110
oracle=random.Random(); oracle.seed(b'\x42'*32)
first_seed=oracle.randbytes(32)
calls=[oracle.randbytes(32) for _ in range(C)]
real_next=oracle.randbytes(32)
obs=[]
for b in calls: obs+=words_of(b)

A0=[0]*624
for p in range(8,624): A0[p]=untemper(obs[p-8])
A1=[untemper(obs[(624+k)-8]) for k in range(235)]
for k in range(8):
    i=227+k
    yt=(A0[i]&0x80000000)|(A0[(i+1)%624]&0x7fffffff)
    A0[k]=(A1[i]^(yt>>1)^(0x9908b0df if (yt&1) else 0))&0xffffffff

# generate full word sequence
def mt_words(A0, count):
    state=list(A0); pos=0; out=[]
    for _ in range(count):
        if pos>=624: state=twist(state); pos=0
        out.append(temper(state[pos])); pos+=1
    return out
gen=mt_words(A0, 8+C*8+8)

# ground truth word sequence: first_seed(0..7) + calls(8..8+8C-1) + next(8+8C..)
truth=[]
truth+=words_of(first_seed)
for b in calls: truth+=words_of(b)
truth+=words_of(real_next)
# compare group by group (each group = 8 words = one randbytes(32))
ngroups=len(truth)//8
mism=[]
for gi in range(ngroups):
    g=gi*8
    if gen[g:g+8]!=truth[g:g+8]:
        mism.append(gi)
print("total groups:",ngroups,"mismatched groups:",len(mism))
print("first 15 mismatched group indices:",mism[:15])
print("groups 0-2 (first_seed+calls0):", "MISMATCH" if 0 in mism else "ok")
# Which word position first diverges?
firstdiv=None
for wi in range(len(truth)):
    if gen[wi]!=truth[wi]:
        firstdiv=wi; break
print("first diverging word index:",firstdiv)
if firstdiv is not None:
    print("  gen :",hex(gen[firstdiv]))
    print("  truth:",hex(truth[firstdiv]))

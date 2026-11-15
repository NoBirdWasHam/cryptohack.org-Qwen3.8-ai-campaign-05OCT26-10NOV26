# Full local validation of the double-untwist attack for bad_temper.
import random, struct
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def inv_f(z):
    b=(z>>31)&1
    return ((z^(MA*b))<<1|b)&0xffffffff
def ir(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&0xffffffff
def il(y,s,mask):
    x=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: x[i]^=x[i-s]
    return sum(x[i]<<i for i in range(32))&0xffffffff
def untemper(y):
    x=ir(y,18); x=il(x,15,0xefc60000); x=il(x,7,0x9d2c5680); return ir(x,11)
def temper(x):
    x^=x>>11; x^=(x<<7)&0x9d2c5680; x^=(x<<15)&0xefc60000; x^=x>>18
    return x&0xffffffff
def my_twist(O):  # CPython in-place twist (verified vs CPython in decisive.py)
    mt=list(O)
    for i in range(624):
        y=(mt[i]&U)|(mt[(i+1)%624]&L)
        mt[i]=mt[(i+397)%624]^f(y)
    return mt

def untwist(N):
    """Given full post-twist array N (=A_next), recover O (=A_cur) where possible.
    Returns list with O[0] possibly wrong in low 31 bits (set to 0 there)."""
    O=[0]*624
    for i in range(228,624):
        y=inv_f(N[i]^N[i-227])
        O[i]|=y&U
        if i<623: O[i+1]|=y&L   # i=623: low part is N[0], not O[0]
    for i in range(0,227):
        y=inv_f(N[i]^O[i+397])
        O[i]|=y&U
        O[i+1]|=y&L
    return O

def words_of(b): return list(struct.unpack('<8I',b))
def pack(ws): return b''.join(struct.pack('<I',w) for w in ws)

def attack(obs_words):
    # obs_words: words at positions 8..1247 (1240 words = 155 blocks)
    assert len(obs_words)==1240
    A2=[untemper(w) for w in obs_words[616:616+624]]   # positions 624..1247
    A1r=untwist(A2)                                     # A1[1..623] correct, A1r[0] garbage low bits
    A0r=untwist(A1r)                                    # A0[1..623] mostly, upper(A0[0]); holes at low(A0[0]), bit31(A0[227]), low31(A0[228])
    A1_0=(A0r[397]^f((A0r[0]&U)|(A0r[1]&L)))&0xffffffff
    first_seed=pack([temper(A1_0)]+[temper(A1r[i]) for i in range(1,8)])
    A3=my_twist(A2)
    next_seed=pack([temper(A3[i]) for i in range(8)])
    return first_seed, next_seed

import os
for trial in range(5):
    secret=os.urandom(32)
    r=random.Random(); r.seed(secret)
    first_seed=r.randbytes(32)
    obs=[]
    while len(obs)<1240: obs+=words_of(r.randbytes(32))
    real_next=r.randbytes(32)
    fs,ns=attack(obs)
    ok1=(fs==first_seed); ok2=(ns==real_next)
    print(f"trial {trial}: first_seed {'OK' if ok1 else 'FAIL'}  next_seed {'OK' if ok2 else 'FAIL'}")
    if not ok1:
        print("  got ",fs.hex()); print("  want",first_seed.hex())
    if not ok2:
        print("  got ",ns.hex()); print("  want",real_next.hex())

# FINAL attack: recover A1[0] via the in-place-twist leak at index 623.
# untwist(A2)->A1[1..623]+upper(A1[0]);  delta = low31(inv_f(A1[623]^A1[396])) = low31(A1[0]).
import random, struct, os
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def inv_f(z):
    b=(z>>31)&1
    return (((z^(MA*b))<<1)|b)&0xffffffff
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
def my_twist(O):
    mt=list(O)
    for i in range(624):
        y=(mt[i]&U)|(mt[(i+1)%624]&L)
        mt[i]=mt[(i+397)%624]^f(y)
    return mt
def untwist_upper_low(N):
    """N fully known post-twist array -> O with O[1..623] exact, upper(O[0]) exact."""
    O=[0]*624
    for i in range(227,624):
        y=inv_f(N[i]^N[i-227]) if i<623 else inv_f(N[623]^N[396])
        O[i]|=y&U
        if i<623: O[i+1]|=y&L
    for i in range(0,227):
        y=inv_f(N[i]^O[i+397])
        O[i]|=y&U
        O[i+1]|=y&L
    return O
def words_of(b): return list(struct.unpack('<8I',b))
def pack(ws): return b''.join(struct.pack('<I',w) for w in ws)

def attack(obs_words):
    assert len(obs_words)==1240
    A2=[untemper(w) for w in obs_words[616:616+624]]
    A1=untwist_upper_low(A2)                 # A1[1..623] exact, A1[0] has correct upper bit
    delta=inv_f(A1[623]^A1[396])&L           # low31 of true A1[0]  (in-place twist leak)
    A1[0]|=delta
    first_seed=pack([temper(A1[i]) for i in range(8)])
    A3=my_twist(A2)
    next_seed=pack([temper(A3[i]) for i in range(8)])
    return first_seed, next_seed

if __name__=="__main__":
    for trial in range(10):
        secret=os.urandom(32)
        r=random.Random(); r.seed(secret)
        first_seed=r.randbytes(32)
        obs=[]
        while len(obs)<1240: obs+=words_of(r.randbytes(32))
        real_next=r.randbytes(32)
        fs,ns=attack(obs)
        print(f"trial {trial}: first_seed {'OK' if fs==first_seed else 'FAIL'}  next_seed {'OK' if ns==real_next else 'FAIL'}")

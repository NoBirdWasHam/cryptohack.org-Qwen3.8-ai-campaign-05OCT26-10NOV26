# Empirically: (1) pos after seed(bytes); (2) does untwist(A2)->A1 recover A1[0..7]?
import random, struct
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def inv_f(z):
    b=(z>>31)&1
    y1=z^(MA*b)          # = y>>1
    y=(y1<<1)|b
    return y&0xffffffff
def untemper(y):
    def ir(y,s):
        x=y;m=s
        while m<32: x^=y>>m; m*=2
        return x&0xffffffff
    def il(y,s,mask):
        x=[(y>>i)&1 for i in range(32)]
        for i in range(s,32):
            if (mask>>i)&1: x[i]^=x[i-s]
        return sum(x[i]<<i for i in range(32))&0xffffffff
    x=ir(y,18); x=il(x,15,0xefc60000); x=il(x,7,0x9d2c5680); return ir(x,11)

def untwist(A2):
    """Given full next-cycle array A2 (post-twist), recover A1 (pre-twist).
    In-place CPython twist: for i<=226: A2[i]=A1[i+397]^f(y_i);
    for 227<=i<=622: A2[i]=A2[i-227]^f(y_i);
    i=623: A2[623]=A2[396]^f(y_623), y_623=(A1[623]&U)|(A2[0]&L).
    y_i=(A1[i]&U)|(A1[i+1]&L) for i<=622."""
    A1=[0]*624
    # i=227..622: f = A2[i]^A2[i-227] -> y_i -> upper(A1[i]), lower31(A1[i+1])
    for i in range(227,623):
        y=inv_f(A2[i]^A2[i-227])
        A1[i]|=y&U
        A1[i+1]|=y&L
    # i=623: f = A2[623]^A2[396] -> upper(A1[623]) (lower part is A2[0], known)
    y=inv_f(A2[623]^A2[396])
    A1[623]|=y&U
    # i=0..226: f = A2[i]^A1[i+397] -> upper(A1[i]), lower31(A1[i+1])
    for i in range(0,227):
        y=inv_f(A2[i]^A1[i+397])
        A1[i]|=y&U
        A1[i+1]|=y&L
    return A1

for trial in range(3):
    r=random.Random(); r.seed(bytes((i*37+11)%256 for i in range(32)))
    pos_after_seed=r.getstate()[1][624]
    first=r.randbytes(32)
    A1_true=list(r.getstate()[1][:624]); p1=r.getstate()[1][624]
    # collect words 8..1247 (A1[8..623] then A2[0..623])
    ws=[]
    while len(ws)<1240:
        ws+=list(struct.unpack('<8I', r.randbytes(32)))
    A2_true=list(r.getstate()[1][:624])  # pos now 1248-624=... after 1240 words pos=8+1240=1248 -> twisted, pos=616? check
    # words: positions 8..1247. After them pos=1248 -> twisted at 624: A2 loaded, words 624..1247 consumed, pos=624? 1248-624=624 -> twisted again! careful
    # Actually after consuming word 1247, pos=1248 -> next call twists. getstate array is still A2.
    A2_obs=[untemper(w) for w in ws[616:616+624]]
    print(f"trial {trial}: pos_after_seed={pos_after_seed} pos_after_first={p1}")
    print("  A2_obs==A2_true:", A2_obs==A2_true)
    A1_rec=untwist(A2_obs)
    diff=[i for i in range(624) if A1_rec[i]!=A1_true[i]]
    print("  untwist mismatches:", diff[:10], "count", len(diff))
    if diff:
        for i in diff[:3]:
            print(f"   A1[{i}] rec={A1_rec[i]:08x} true={A1_true[i]:08x} xor={A1_rec[i]^A1_true[i]:08x}")

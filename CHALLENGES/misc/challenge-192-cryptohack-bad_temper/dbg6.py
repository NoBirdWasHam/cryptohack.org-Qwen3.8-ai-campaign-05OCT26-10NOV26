import random
def inv_rshift_xor(y,s):
    x=y;m=s
    while m<32: x^=y>>m; m*=2
    return x&0xffffffff
def inv_lshift_xor(y,s,mask):
    x=[(y>>i)&1 for i in range(32)]
    for i in range(s,32):
        if (mask>>i)&1: x[i]^=x[i-s]
    return sum(x[i]<<i for i in range(32))&0xffffffff
def temper(x):
    x^=x>>11
    x^=(x<<7)&0x9d2c5680
    x^=(x<<15)&0xefc60000
    x^=x>>18
    return x&0xffffffff
def untemper(y):
    x=y^(y>>18)
    x=inv_lshift_xor(x,15,0xefc60000)
    x=inv_lshift_xor(x,7,0x9d2c5680)
    x=inv_rshift_xor(x,11)
    return x&0xffffffff

# Verify temper matches CPython by checking round-trip AND against actual CPython words.
# Capture CPython raw array and compare temper(A[i]) to the i-th word.
r=random.Random(7)
for _ in range(624): r.getrandbits(32)     # pos wraps to 0, array=post-twist A1
st=r.getstate()
A=list(st[1][:624])
w=r.getrandbits(32)
print("temper(A[0])==word0:", temper(A[0])==w)
# round-trip
rr=random.Random(1)
ws=[rr.getrandbits(32) for _ in range(500)]
rt=all(untemper(temper(w))==w for w in ws)
print("untemper(temper)==id:", rt)
# verify untemper against CPython raw: temper then untemper a raw value
# (can't get raw directly, but round-trip + temper-match is sufficient)

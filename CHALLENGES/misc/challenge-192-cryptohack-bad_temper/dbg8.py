import random
def temper(x):
    x^=x>>11
    x^=(x<<7)&0x9d2c5680
    x^=(x<<15)&0xefc60000
    x^=x>>18
    return x&0xffffffff
def twist(mt):
    n=624;mt=mt[:]
    for i in range(n):
        y=(mt[i]&0x80000000)|(mt[(i+1)%n]&0x7fffffff)
        mt[i]=mt[(i+397)%n]^(y>>1)^(0x9908b0df if y&1 else 0)
    return mt
# word_624 (625th word) = temper_Cpython(twist(A0)[0]); A0 = raw array after 624 words (pos=624)
ok=0; tot=0
for seed in range(5):
    r=random.Random(seed)
    for _ in range(624): r.getrandbits(32)
    A0=list(r.getstate()[1][:624])
    # next word
    w=r.getrandbits(32)
    tot+=1
    if temper(twist(A0)[0])==w: ok+=1
print("temper(twist(A0)[0])==word_624 :", ok,"/",tot)
# also verify the NEXT few words
for seed in [0]:
    r=random.Random(seed)
    for _ in range(624): r.getrandbits(32)
    A0=list(r.getstate()[1][:624])
    A1=twist(A0)
    ok=0
    for k in range(20):
        w=r.getrandbits(32)
        if k<624:
            idx=k if k<1 else k  # after first twist, array is A1, pos goes 0,1,2..
            # but CPython twists again at pos=624; for k<20 we're in A1[0..19]
        if temper(A1[k])==w: ok+=1
    print("first 20 post-twist words match:",ok,"/20")

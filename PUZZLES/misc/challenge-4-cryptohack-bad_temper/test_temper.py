import random
def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x00007fff
    x ^= (x << 15) & 0x80000000
    x ^= x >> 18
    return x & 0xffffffff

# CPython state: capture array at pos 0, then generate words and compare to temper.
r=random.Random(7)
# force pos to 0 by generating 624 words
for _ in range(624): r.getrandbits(32)
st=r.getstate()
print("version",st[0],"pos",st[2],"len",len(st[1]))
arr=list(st[1])
# arr length 625 (624 + pos). The mt array is arr[:624]
A=arr[:624]
w0=r.getrandbits(32)
print("word0 == temper(A[0])?", w0==temper(A[0]))
print("word0",hex(w0),"temper(A0)",hex(temper(A[0])), "A0",hex(A[0]))
# maybe pos is stored differently; try generating a few
ok=0
rr=random.Random(7)
for _ in range(624): rr.getrandbits(32)
Ar=list(rr.getstate()[1])[:624]
for k in range(10):
    w=rr.getrandbits(32)
    if w==temper(Ar[k%624]): ok+=1
print("match count /10:", ok)
# Also check: is it temper(A[pos]) with pos incrementing, or temper(A[0]) after reset?
print("state[2] (pos) after 624:", st[2])

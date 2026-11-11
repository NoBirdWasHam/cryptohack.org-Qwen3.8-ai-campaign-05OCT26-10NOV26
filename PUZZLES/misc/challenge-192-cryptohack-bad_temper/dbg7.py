import random
def temper(x):
    x^=x>>11
    x^=(x<<7)&0x9d2c5680
    x^=(x<<15)&0xefc60000
    x^=x>>18
    return x&0xffffffff

r=random.Random(7)
for _ in range(624): r.getrandbits(32)
st=r.getstate()
inner=st[1]
print("inner len", len(inner), "inner[624]", inner[624])
A=list(inner[:624])
# generate word0
w0=r.getrandbits(32)
hits=[i for i in range(624) if temper(A[i])==w0]
print("A[i] with temper==word0:", hits)
# Maybe the stored array is rotated to pos; pos after 624 words?
# inner[624] is 624 (pos). But CPython may rotate array so that logical index 0 = array[pos].
# Let's check: after pos=624 (i.e., just twisted), logical A[0] should be temper target for word0.
# If array stored rotated: stored[i] = A[(i+624)%624] = A[i]. So stored[0]=A[0].
# Try generating a few words and finding which stored index each comes from.
rr=random.Random(7)
for _ in range(624): rr.getrandbits(32)
inner2=rr.getstate()[1]
A2=list(inner2[:624])
for k in range(3):
    w=rr.getrandbits(32)
    h=[i for i in range(624) if temper(A2[i])==w]
    print(f"word{k} from A2 index:", h)

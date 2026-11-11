import random
def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x00007fff
    x ^= (x << 15) & 0x80000000
    x ^= x >> 18
    return x & 0xffffffff

r=random.Random(7)
for _ in range(624): r.getrandbits(32)   # pos wraps to 0, array = post-twist
st=r.getstate()
print("len(st)", len(st), "type", type(st).__name__)
for i,v in enumerate(st):
    print(" st[%d]:"%i, type(v).__name__, ("len %d"%len(v) if hasattr(v,'__len__') else repr(v)))
S=st[1]
# hypothesis: S[0:624]=mt array, S[624]=pos
pos_hypo=S[624]
A=S[0:624]
w=r.getrandbits(32)
print("pos_hypo",pos_hypo,"temper(A[pos_hypo])==w?", temper(A[pos_hypo])==w, " temper(A[0])==w?", temper(A[0])==w)
# try a few: generate 5 words, track expected
rr=random.Random(7)
for _ in range(624): rr.getrandbits(32)
S2=rr.getstate()[1]
A2=S2[0:624]; pos2=S2[624]
ok=0
for k in range(8):
    w=rr.getrandbits(32)
    if temper(A2[(pos2+k)%624])==w: ok+=1
print("with A=S[0:624], pos=S[624]: matches /8 =", ok)
# alternative: pos stored as st[2]? (it was None) -> no
# alternative: maybe S is the 624 array and pos is separate; test A=S, pos=0
rr2=random.Random(7)
for _ in range(624): rr2.getrandbits(32)
S3=rr2.getstate()[1]
A3=list(S3)
print("len(A3)", len(A3))
# If len 625, maybe A3 = [pos, mt0..mt623]
ok3=0
rr3=random.Random(7)
for _ in range(624): rr3.getrandbits(32)
S4=rr3.getstate()[1]
p=S4[0]; A4=list(S4[1:])
for k in range(8):
    w=rr3.getrandbits(32)
    if temper(A4[(p+k)%624])==w: ok3+=1
print("with A=S[1:], pos=S[0]: matches /8 =", ok3, "pos=",p)

import random
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)

def my_twist(O):   # in-place, write order 0..623
    mt=list(O)
    for i in range(624):
        y=(mt[i]&U)|(mt[(i+1)%624]&L)
        mt[i]=mt[(i+397)%624]^f(y)
    return mt

def canon_twist(O):  # out-of-place standard formula
    N=[0]*624
    for i in range(624):
        y=(O[i]&U)|(O[(i+1)%624]&L)
        N[i]=O[(i+397)%624]^f(y)
    return N

# 1) Find CPython twist point: snapshot array after words 622,623,624,625
r=random.Random(99)
for _ in range(622): r.getrandbits(32)
A622=list(r.getstate()[1][:624]); p622=r.getstate()[1][624]
w623=r.getrandbits(32)
A623=list(r.getstate()[1][:624]); p623=r.getstate()[1][624]
w624=r.getrandbits(32)
A624=list(r.getstate()[1][:624]); p624=r.getstate()[1][624]
w625=r.getrandbits(32)
A625=list(r.getstate()[1][:624]); p625=r.getstate()[1][624]
print("pos after 622,623,624,625 words:", p622, p623, p624, p625)
print("array changed 622->623:", A622!=A623)
print("array changed 623->624:", A623!=A624)
print("array changed 624->625:", A624!=A625)
# The twist happens at the word where the array changes.
# Identify pre-twist array O and post-twist array N.
if A623!=A624:
    O=A623; N=A624; boundary="twist at word 624 (0-idx 623->624)"
elif A624!=A625:
    O=A624; N=A625; boundary="twist at word 625"
else:
    O=A623; N=A624; boundary="?"
print("boundary:", boundary)
# 2) 3-way compare
print("my_twist(O)==N :", my_twist(O)==N)
print("canon_twist(O)==N :", canon_twist(O)==N)
# count differences
dm=sum(1 for i in range(624) if my_twist(O)[i]!=N[i])
dc=sum(1 for i in range(624) if canon_twist(O)[i]!=N[i])
print("my_twist diff count:", dm, " canon diff count:", dc)
# 3) Does my_twist differ from canon_twist at all?
print("my_twist==canon_twist (same function?):", my_twist(O)==canon_twist(O))
# 4) invertibility of the matching one
import random as _r
def is_injective(fn, trials=400):
    seen={}
    for t in range(trials):
        O=[_r.getrandbits(32) for _ in range(624)]
        N=fn(O)
        key=tuple(N)
        if key in seen: return False, seen[t], t
        seen[key]=t
    return True, None, None
m,_,_=is_injective(my_twist)
c,_,_=is_injective(canon_twist)
print("my_twist injective (sample):", m)
print("canon_twist injective (sample):", c)

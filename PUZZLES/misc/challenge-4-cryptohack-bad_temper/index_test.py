import random
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def twist_ip(O, idx):   # in-place, source = O[(i+idx)%624]
    mt=list(O)
    for i in range(624):
        y=(mt[i]&U)|(mt[(i+1)%624]&L)
        mt[i]=mt[(i+idx)%624]^f(y)
    return mt
# Capture CPython's actual twist: array before & after the twist word.
r=random.Random(2024)
for _ in range(624): r.getrandbits(32)
A_before=list(r.getstate()[1][:624]); p_before=r.getstate()[1][624]
w=r.getrandbits(32)   # triggers twist
A_after=list(r.getstate()[1][:624]); p_after=r.getstate()[1][624]
print("p_before",p_before,"p_after",p_after,"(twist happens at word 625, pos 624->1)")
print("A_before==A_after?", A_before==A_after)
# The twist maps A_before -> A_after
for idx in (227,397):
    cand=twist_ip(A_before, idx)
    print(f"in-place idx={idx}: match CPython = {cand==A_after}  (diffs={sum(1 for i in range(624) if cand[i]!=A_after[i])})")
# invertibility test for the matching idx
def injective(O, idx):
    # perturb low bits of A[0]
    for bit in range(32):
        P=list(O); P[0]=O[0]^(1<<bit)
        if twist_ip(P,idx)!=twist_ip(O,idx): return True
    return False
for idx in (227,397):
    print(f"idx={idx} invertible (A[0] low bits affect output):", injective(A_before, idx))

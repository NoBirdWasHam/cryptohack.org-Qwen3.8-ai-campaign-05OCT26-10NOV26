# Collision for spongebob.py: R is a bijection and output = final state.
# For 2-block messages: H(m1||m2)=H(m1'||m2') iff R(INIT^m1)^m2 == R(INIT^m1')^m2'
# since R bijective. Pick m1,m1' distinct, m2 = 0, m2' = s1 ^ s1'.
from spongebob import H, INIT, permute, SBOX, blocks

def R(state):
    for _ in range(8):
        state = permute(state)
        state = [SBOX[b] for b in state]
    return state[:]

def oneround(m):
    state = INIT[:]
    for i, c in enumerate(m):
        state[i] ^= c
    return R(state)

m1 = b"spongebo"
m1p = b"squarepa"
s1 = oneround(m1)
s1p = oneround(m1p)
m2 = bytes(8)
m2p = bytes(x ^ y for x, y in zip(s1, s1p))
a = m1 + m2
b = m1p + m2p
assert a != b
assert H(a) == H(b)
print(a.hex())
print(b.hex())

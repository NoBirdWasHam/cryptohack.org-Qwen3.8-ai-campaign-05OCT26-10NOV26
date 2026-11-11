# Empirically probe CPython's Random().seed(bytes) -> getstate() to pin down
# the init_by_array variant. Strategy: seed with crafted 32-byte keys and
# inspect how the state depends on the key.
import struct, os
from random import Random

def state_of(secret):
    r = Random(); r.seed(secret)
    return list(r.getstate()[1][:624])

def init_genrand(s):
    st = [0]*624
    st[0] = s
    for i in range(1, 624):
        st[i] = (1812433253 * (st[i-1] ^ (st[i-1] >> 30)) + i) & 0xffffffff
    return st

S0 = init_genrand(19650218)
Z = state_of(b"\x00"*32)

# Hypothesis check: does state depend on key at all in expected places?
# Compare state for key with only word0 changed.
A = state_of(struct.pack('<I', 1) + b"\x00"*28)
B = state_of(struct.pack('<I', 2) + b"\x00"*28)
C = state_of(b"\x00"*4 + struct.pack('<I', 1) + b"\x00"*24)
diffA = [i for i in range(624) if A[i] != Z[i]]
diffC = [i for i in range(624) if C[i] != Z[i]]
print("words changed when key word0: 1 vs 0 ->", len(diffA), diffA[:20])
print("A[1]-Z[1] =", (A[1]-Z[1]) & 0xffffffff, " A[1]^Z[1] =", A[1]^Z[1])
print("A[2]-Z[2] =", (A[2]-Z[2]) & 0xffffffff)
print("changed when key word1=1:", len(diffC), diffC[:20])
# check LE vs BE: bytes 01 00 00 00 -> LE word 1, BE word 0x01000000
E = state_of(b"\x01\x00\x00\x00" + b"\x00"*28)
print("bytes 01 00 00 00 == A (LE, word=1)?", E == A)
F = state_of(b"\x00\x00\x00\x01" + b"\x00"*28)
print("bytes 00 00 00 01 == A (BE, word=1)?", F == A)

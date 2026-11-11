#!/usr/bin/env python3
"""Deterministic convention test: compute M1, M3 exactly and print
byte-propagation tables. Block bytes indexed 0..15 with byte 0 = MOST
significant byte (int.from_bytes big-endian, bit 127 = byte0 bit7)."""
from local_oracle import *

def fr(b): return int.from_bytes(b, 'big')

def bytes_active(v):
    # which of the 16 block bytes (0 = MSB) are nonzero in 128-bit int v
    bs = v.to_bytes(16, 'big')
    return tuple(j for j in range(16) if bs[j])

sess = Session(key=b'\x00'*16)   # FIXED key -> deterministic M1,M3
M1 = lin_matrix(lambda v: fr(mix(v.to_bytes(16,'big'), sess.k1)))
M3 = lin_matrix(lambda v: fr(mix(v.to_bytes(16,'big'), sess.k3)))
print("M1 invertible check skipped; columns count:", len(M1), len(M3))

print("\nTable: plaintext bit b -> bytes active in M1*e_b (byte j = big-endian byte j)")
cnt = {}
for b in range(128):
    act = bytes_active(M1[b])
    cnt[len(act)] = cnt.get(len(act), 0) + 1
print("distribution of active-byte-count over 128 columns of M1:", cnt)

# sanity: apply mat_apply to a byte vector
v = fr(b'\x01'+b'\x00'*15)
print("M1 applied to byte0=0x01:", bytes_active(mat_apply(M1, v)))
v = fr(b'\x00'*15+b'\x01')
print("M1 applied to byte15=0x01:", bytes_active(mat_apply(M1, v)))

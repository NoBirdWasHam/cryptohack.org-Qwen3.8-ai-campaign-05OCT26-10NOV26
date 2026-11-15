#!/usr/bin/env python3
"""Debug: with LOCAL server, we KNOW the message. Test byte-15 and byte-14 constructions."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solve
from solve import xor, make_local_client

LC = make_local_client()
c = LC()
msg = c.ch.message.encode("ascii")   # true 32-byte message
P1, P2 = msg[:16], msg[16:]
ct = c.encrypt()
iv, c1, c2 = ct[:16], ct[16:32], ct[32:48]

def frac(ctbytes, n=60):
    return sum(c.unpad_batch([ctbytes]*n, chunk=6))/n

# sanity: original ct should be invalid (hex last byte > 16)
print("orig ct frac_true:", frac(iv+c1+c2))

# byte 15, blk2: true candidate v = P2[15]^1
v = P2[15] ^ 1
d = bytearray(16); d[15] = v
print("byte15 true-cand frac (expect 0.4):", frac(iv+c1+xor(c2,bytes(d))))
d2 = bytearray(16); d2[15] = v ^ 0x55
print("byte15 wrong-cand frac (expect 0.6):", frac(iv+c1+xor(c2,bytes(d2))))

# byte 14, blk2: suffix byte15 -> p=2, candidate v=P2[14]^2
d = bytearray(16); d[15] = P2[15]^2; d[14] = P2[14]^2
print("byte14 true-cand frac (expect 0.4):", frac(iv+c1+xor(c2,bytes(d))))

# byte 15, blk1 via iv: true v = P1[15]^1
m = bytearray(16); m[15] = P1[15]^1
print("blk1 byte15 true-cand frac (expect 0.4):", frac(xor(iv,bytes(m))+c1))

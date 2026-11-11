#!/usr/bin/env python3
"""Measure the LIVE flip rate f = P(result=True | known-invalid padding).
Known-invalid: random 1-block ciphertexts (P(valid) ~ 1/256).
Also times pipelined queries."""
import os, time, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import Client

c = Client()
print("greeting:", c.greeting[:80])
ct = c.encrypt()
print("ct len:", len(ct))

N = 400
garbage = []
for _ in range(N):
    iv = os.urandom(16)
    blk = os.urandom(16)
    garbage.append(iv + blk)

t0 = time.time()
res = c.unpad_batch(garbage, chunk=10)
dt = time.time() - t0
nt = sum(res)
print(f"N={N} true={nt} frac_true={nt/N:.4f}  ({dt/N*1000:.1f} ms/query, total {dt:.1f}s)")
c.close()

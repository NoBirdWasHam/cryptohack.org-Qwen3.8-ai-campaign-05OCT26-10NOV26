#!/usr/bin/env python3
"""Fresh probe: measure P(result=True | known-invalid padding) on the LIVE server.
Known-invalid = random 1-block ciphertexts (P(valid)~1/255). Also time pipelining."""
import os, time, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import Client

c = Client()
print("greeting:", c.greeting[:80])
ct = c.encrypt()
print("ct len:", len(ct), "hex:", ct.hex())

N = 200
garbage = [os.urandom(16) + os.urandom(16) for _ in range(N)]

t0 = time.time()
res = c.unpad_batch(garbage, chunk=6)
dt = time.time() - t0
nt = sum(res)
print(f"N={N} true={nt} frac_true={nt/N:.4f}  ({dt/N*1000:.1f} ms/query, total {dt:.1f}s)")

# second batch to check stability
res2 = c.unpad_batch(garbage, chunk=6)
print(f"batch2 true={sum(res2)} frac={sum(res2)/N:.4f}")
c.close()

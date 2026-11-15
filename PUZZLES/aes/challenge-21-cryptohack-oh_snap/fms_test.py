#!/usr/bin/env python3
"""Local empirical test of the FMS bias: for random keys, condition
'S[i+1] == 0 after KSA round i' -> distribution of (z_i - K[i]) mod 256.
Also measures condition firing rate vs i. This pins the exact vote formula
and tells us how many samples we need per key byte."""
import random, sys
from collections import Counter

def ksa(K):
    S = list(range(256))
    j = 0
    L = len(K)
    # record S[i+1] after round i, for i in 0..254
    after = {}
    for i in range(256):
        j = (j + S[i] + K[i % L]) & 0xFF
        S[i], S[j] = S[j], S[i]
        if i < 255:
            after[i] = S[i+1]
    return S

def prga(S, m):
    S = S[:]
    i = j = 0
    out = bytearray()
    for _ in range(m):
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xFF])
    return bytes(out)

def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    L = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    M = L + 2
    rng = random.Random(1234)
    cond = [0]*L
    votes = [Counter() for _ in range(L)]
    for _ in range(N):
        K = bytes(rng.randrange(256) for _ in range(L))
        S = ksa(K)
        z = prga(S, M)
        # recompute S[i+1]-after-round-i cheaply: rerun ksa recording
        # (do it inline instead: redo loop)
        S2 = list(range(256)); j = 0
        for i in range(L):
            j = (j + S2[i] + K[i % L]) & 0xFF
            S2[i], S2[j] = S2[j], S2[i]
            if S2[i+1] == 0:
                cond[i] += 1
                votes[i][(z[i] - K[i]) & 0xFF] += 1
    for i in range(L):
        if cond[i] == 0:
            print(f"i={i:2d} cond=0")
            continue
        top = votes[i].most_common(3)
        s = " ".join(f"z-K=0x{v:02x}({c/cond[i]*100:.1f}%)" for v, c in top)
        print(f"i={i:2d} cond={cond[i]:6d} ({cond[i]/N*100:5.2f}%)  {s}")

main()

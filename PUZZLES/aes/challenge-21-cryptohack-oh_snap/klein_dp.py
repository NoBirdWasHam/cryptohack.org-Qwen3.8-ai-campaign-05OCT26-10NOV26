#!/usr/bin/env python3
"""Klein sigma attack + top-M-per-state DP path search + keystream verifier.
State = sigma_prev (256 values); keep top-M scored byte-strings per state.
Collects every path that closes with '}' at any length; verifies by RC4."""
import random, sys, math, time, heapq
from collections import Counter
from Crypto.Cipher import ARC4

CHARSET = set(b"abcdefghijklmnopqrstuvwxyz0123456789_{}-.")

def ksa_prefix(N):
    S = list(range(256)); j = 0; jhist = []
    for i in range(len(N)):
        j = (j + S[i] + N[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        jhist.append(j)
    return S, j, jhist

def add_votes(N, z, T, table, w_mp=4):
    S, j, jhist = ksa_prefix(N)
    inv = [0]*256
    for p, v in enumerate(S):
        inv[v] = p
    sigma = 0
    n = len(N)
    for t in range(T):
        l = n + t
        if l >= len(z):
            break
        sigma = (sigma + S[l]) & 0xFF
        tmp = (l - z[l-1]) & 0xFF
        table[t][(inv[tmp] - j - sigma) & 0xFF] += 13
        zl = z[l]
        if zl >= l and all(jh != zl for jh in jhist):
            table[t][(zl - j - sigma) & 0xFF] += w_mp

def dp_search(table, T, known=b"crypto{", M=8, charset=CHARSET):
    sig = 0
    for ch in known:
        sig = (sig + ch) & 0xFF
    # states: dict sigma -> list of (score, bytes)  (min-heap by score, cap M)
    states = {sig: [(0.0, b"")]}
    closed = []  # (score, full_bytes)
    for t in range(len(known), T):
        votes = table[t]
        tot = sum(votes.values()) or 1
        logp = {v: math.log(v_ / tot) for v, v_ in votes.items()}
        newstates = {}
        for sprev, paths in states.items():
            for score, bs in paths:
                for sg, lp in logp.items():
                    b = (sg - sprev) & 0xFF
                    if b in charset:
                        sc = score + lp
                        nb = bs + bytes([b])
                        if b == ord("}"):
                            closed.append((sc, nb))
                        lst = newstates.setdefault(sg, [])
                        lst.append((sc, nb))
        # prune per state
        states = {}
        for sg, lst in newstates.items():
            lst.sort(key=lambda x: -x[0])
            states[sg] = lst[:M]
        if not states:
            break
    closed.sort(key=lambda x: -x[0])
    return closed

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    M = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    flag = sys.argv[4].encode() if len(sys.argv) > 4 else b"[flag value withheld — real-flag strings live only under FLAGS/]"
    f = len(flag)
    TMAX = 48
    m = n + TMAX + 2
    rng = random.Random(7)
    t0 = time.time()
    samples = []
    for _ in range(total):
        N = bytes(rng.randrange(256) for _ in range(n))
        samples.append((N, ARC4.new(N + flag).decrypt(b"\x00" * m)))
    table = [Counter() for _ in range(TMAX)]
    for N, ks in samples:
        add_votes(N, ks, TMAX, table)
    print(f"gen+vote {total} samples in {time.time()-t0:.1f}s (flag len {f})")
    t0 = time.time()
    closed = dp_search(table, TMAX, M=M)
    print(f"dp {time.time()-t0:.1f}s, {len(closed)} closed paths")
    N, ks = samples[-1]
    N2, ks2 = samples[-2]
    for score, bs in closed[:200000]:
        cand = b"crypto{" + bs
        if ARC4.new(N + cand).decrypt(b"\x00" * m) == ks and ARC4.new(N2 + cand).decrypt(b"\x00" * m) == ks2:
            print(f"VERIFIED: {cand!r} score={score:.2f} (rank in closed list: position)")
            return
    print("no verified candidate; top closed:")
    for score, bs in closed[:5]:
        print(f"  {b'[flag value withheld — real-flag strings live only under FLAGS/] score={score:.2f}")

main()

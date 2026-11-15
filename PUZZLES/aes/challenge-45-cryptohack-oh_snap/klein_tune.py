#!/usr/bin/env python3
"""Tune Klein attack: sample count / nonce length / beam-search recovery."""
import random, sys, math, time
from collections import Counter
from Crypto.Cipher import ARC4

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

def beam_search(table, T, known=b"crypto{", K=96, B=4096):
    # sigma values for known prefix
    sig = 0; start = 0
    beams = []  # (score, sigma_prev, bytes)
    # pin known bytes
    pinned = []
    for ch in known:
        sig = (sig + ch) & 0xFF
        pinned.append(sig)
    beams = [(0.0, sig, bytearray(known))]
    for t in range(len(known), T):
        votes = table[t]
        tot = sum(votes.values()) or 1
        cands = [v for v, _ in votes.most_common(K)]
        newb = []
        for score, sprev, bs in beams:
            for sg in cands:
                b = (sg - sprev) & 0xFF
                if 32 <= b <= 126:
                    newb.append((score + math.log(1 + votes[sg]/tot), sg, bs + bytes([b])))
        if not newb:
            return []
        newb.sort(key=lambda x: -x[0])
        # dedupe by sigma_prev keeping best score per sigma_prev? keep diverse:
        beams = newb[:B]
    return beams

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    flag = b"[flag value withheld — real-flag strings live only under FLAGS/]"
    f = len(flag)
    m = n + f + 2
    T = f
    rng = random.Random(7)
    t0 = time.time()
    samples = []
    for _ in range(total):
        N = bytes(rng.randrange(256) for _ in range(n))
        samples.append((N, ARC4.new(N + flag).decrypt(b"\x00" * m)))
    print(f"gen {total} samples in {time.time()-t0:.1f}s")
    for frac in (0.25, 0.5, 1.0):
        cnt = int(total * frac)
        table = [Counter() for _ in range(T)]
        for N, ks in samples[:cnt]:
            add_votes(N, ks, T, table)
        # rank of true sigma
        acc = 0; ranks = []
        for t in range(T):
            acc = (acc + flag[t]) & 0xFF
            ranked = [v for v, _ in table[t].most_common()]
            ranks.append(ranked.index(acc))
        print(f"n={n} samples={cnt}: ranks={ranks}")
        beams = beam_search(table, T)
        found = None
        for score, sg, bs in beams:
            if bs.endswith(b"}"):
                cand = bytes(bs)
                N, ks = samples[-1]
                if ARC4.new(N + cand).decrypt(b"\x00" * m) == ks:
                    found = cand
                    break
        print(f"   beam candidates={len(beams)} verified={'YES: '+found.decode() if found else 'no'}")

main()

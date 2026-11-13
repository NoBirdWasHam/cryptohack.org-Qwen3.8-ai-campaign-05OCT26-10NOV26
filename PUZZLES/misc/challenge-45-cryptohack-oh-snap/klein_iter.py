#!/usr/bin/env python3
"""Iterative Klein attack with known-prefix-in-nonce.
Round k: nonce = R(rlen) || known_prefix. Key = nonce || FLAG.
All KSA rounds up to the first unknown byte are fully simulated ->
that byte gets a full-strength Klein/MP vote; later bytes get telescoped
sigma votes (weaker). Recover, extend prefix, repeat."""
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

def run_round(known, flag, rlen, count, m, rng, w_mp=4):
    """returns table over t=0..T-1 where t indexes FLAG bytes (t>=len(known) unknown)."""
    T = len(flag) - len(known)
    table = [Counter() for _ in range(T)]
    for _ in range(count):
        R = bytes(rng.randrange(256) for _ in range(rlen))
        N = R + known
        ks = ARC4.new(N + flag).decrypt(b"\x00" * m)
        # simulate KSA over nonce AND the known flag copy that follows it
        add_votes(N + known, ks, T, table, w_mp)
    return table

def main():
    rlen = 4
    per_round = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    flag = sys.argv[2].encode() if len(sys.argv) > 2 else b"[flag value withheld — real-flag strings live only under FLAGS/]"
    f = len(flag)
    m = rlen + f + f + 4
    rng = random.Random(11)
    known = b"crypto{"
    total_q = 0
    while len(known) < f:
        T = f - len(known)
        table = run_round(known, flag, rlen, per_round, m, rng)
        total_q += per_round
        # byte at position len(known): sigma_0 vote (t=0) is exactly that byte
        t0 = table[0]
        top = t0.most_common(3)
        best = top[0][0]
        acc = (best) & 0xFF
        ok = (acc == flag[len(known)])
        known += bytes([acc])
        print(f"known={known!r} next={chr(acc)} want={chr(flag[len(known)-1])} {'OK' if ok else 'FAIL'} top={top}")
        if not ok:
            print("MISMATCH -> stopping (would use DP+verifier here)")
            break
    print(f"total queries: {total_q}")

main()

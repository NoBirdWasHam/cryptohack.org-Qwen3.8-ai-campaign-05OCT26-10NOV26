#!/usr/bin/env python3
"""Klein/PTW-style sigma attack prototype for key = nonce || FLAG with a
keystream oracle. Validated locally against a synthetic flag first.

Vote (aircrack-ptw `guesskeybytes`, cross-checked vs wepwolf `klein_cand`):
  state S_t = KSA state after simulating only the n known nonce rounds, j_t = j.
  for t in 0..T-1:  l = n+t
     sigma_t += S_t[l]
     tmp   = (l - z[l-1]) & 0xff
     sinv  = S_t^{-1}[tmp]
     vote for sigma_t (cumulative sum K[n..n+t]) := (sinv - j_t - sigma_t) & 0xff
  Maitra-Paul extra vote for same sigma: (z[l] - j_t - sigma_t) & 0xff
     gated: z[l] >= l and z[l] not in {j after each simulated round}
FLAG[t] = sigma_t - sigma_{t-1}.
"""
import random, sys
from collections import Counter
from Crypto.Cipher import ARC4

def ksa_prefix(N):
    S = list(range(256)); j = 0; jhist = []
    for i in range(len(N)):
        j = (j + S[i] + N[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        jhist.append(j)
    return S, j, jhist

def klein_votes(N, z, T, table, w_mp=4):
    S, j, jhist = ksa_prefix(N)
    inv = [0]*256
    for p, v in enumerate(S):
        inv[v] = p
    sigma = 0
    for t in range(T):
        l = len(N) + t
        sigma = (sigma + S[l]) & 0xFF
        tmp = (l - z[l-1]) & 0xFF
        table[t][(inv[tmp] - j - sigma) & 0xFF] += 13
        if l < len(z):
            zl = z[l]
            if zl >= l and all(jh != zl for jh in jhist):
                table[t][(zl - j - sigma) & 0xFF] += w_mp

def gen_samples(flag, n, m, count, rng):
    out = []
    for _ in range(count):
        N = bytes(rng.randrange(256) for _ in range(n))
        ks = ARC4.new(N + flag).decrypt(b"\x00" * m)
        out.append((N, ks))
    return out

def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    flag = b"[flag value withheld — real-flag strings live only under FLAGS/]"
    f = len(flag)
    m = n + f + 2
    rng = random.Random(42)
    print(f"flag={flag!r} len={f} n={n} samples={count}")
    samples = gen_samples(flag, n, m, count, rng)
    T = f
    table = [Counter() for _ in range(T)]
    for N, ks in samples:
        klein_votes(N, ks, T, table)
    # sigma candidates -> flag bytes
    true_sigma = []
    acc = 0
    for t in range(T):
        acc = (acc + flag[t]) & 0xFF
        true_sigma.append(acc)
    ok = 0
    rec = bytearray()
    prev = 0
    for t in range(T):
        top = table[t].most_common(3)
        best = top[0][0]
        tot = sum(table[t].values())
        rank = [v for v, _ in table[t].most_common()].index(true_sigma[t])
        byte = (best - prev) & 0xFF
        rec.append(byte)
        prev = best
        if byte == flag[t]:
            ok += 1
        print(f"t={t:2d} true_sig={true_sigma[t]:3d} top={[(v,c) for v,c in top]} "
              f"rank_true={rank} byte={chr(byte) if 32<=byte<127 else '?'} want={chr(flag[t])}")
    print(f"recovered: {rec!r}")
    print(f"correct bytes: {ok}/{T}")

main()

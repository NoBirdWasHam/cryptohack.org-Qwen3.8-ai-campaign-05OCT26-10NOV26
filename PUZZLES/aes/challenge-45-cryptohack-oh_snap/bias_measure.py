#!/usr/bin/env python3
"""Measure the t=0 vote bias for the prefix-in-nonce configuration."""
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

flag = sys.argv[2].encode() if len(sys.argv) > 2 else b"[flag value withheld — real-flag strings live only under FLAGS/]"
known = flag[:7]
rlen = 4
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
rng = random.Random(5)
tab = Counter()
m = rlen + 2*len(known) + len(flag) + 4
for _ in range(N):
    R = bytes(rng.randrange(256) for _ in range(rlen))
    Nn = R + known
    ks = ARC4.new(Nn + flag).decrypt(b"\x00" * m)
    N2 = Nn + known
    S, j, jhist = ksa_prefix(N2)
    l = len(N2)
    sigma = S[l]
    tab[(S.index((l - ks[l-1]) & 0xFF) - j - sigma) & 0xFF] += 13
    zl = ks[l]
    if zl >= l and all(jh != zl for jh in jhist):
        tab[(zl - j - sigma) & 0xFF] += 4
true = flag[len(known)]
mc = tab.most_common(5)
mean = sum(tab.values()) / 256
print(f"true byte {chr(true)} count={tab[true]} floor={mean:.0f}")
print("top:", [(chr(v), c) for v, c in mc])

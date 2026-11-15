#!/usr/bin/env python3
"""Search for the real RC4 KSA keystream bias: for random keys, evaluate a family
of candidate conditions (computable from K[0..i]) and report the max bias in
(z_i - K[i]) and (z_i + K[i]) under each condition."""
import random, sys
from collections import Counter

L = 32
M = L + 2
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
rng = random.Random(99)

def full_ksa(K, upto=None):
    S = list(range(256)); j = 0; Ln = len(K)
    for i in range(256 if upto is None else upto):
        j = (j + S[i] + K[i % Ln]) & 0xFF
        S[i], S[j] = S[j], S[i]
    return S, j

def prga(S, m):
    S = S[:]; i = j = 0; out = bytearray()
    for _ in range(m):
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xFF])
    return bytes(out)

# conditions: name -> function(i, state info) -> bool
# state info per i: a=S[i+1] after round i; b=S[i+1] after round i-1;
# jj=j after round i; untouched=pos i+1 never swapped rounds 0..i;
# pf=S[i+1] after FULL ksa with key=K[:i+1]; pfj=j after full ksa K[:i+1]
cond_defs = {
    "a==0":        lambda d: d["a"] == 0,
    "b==0":        lambda d: d["b"] == 0,
    "a==i+1":      lambda d: d["a"] == (d["i"]+1),
    "b==i+1":      lambda d: d["b"] == (d["i"]+1),
    "untouched":   lambda d: d["untouched"],
    "jj==0":       lambda d: d["jj"] == 0,
    "jj==i+1":     lambda d: d["jj"] == (d["i"]+1),
    "jj==i":       lambda d: d["jj"] == d["i"],
    "pf==0":       lambda d: d["pf"] == 0,
    "a==0&untouched_before": lambda d: d["a"] == 0 and d["b"] == (d["i"]+1),
    "b==0&jj!=i+1":lambda d: d["b"] == 0 and d["jj"] != (d["i"]+1),
}
stats = {name: [Counter(), Counter()] for name in cond_defs}  # per name: [z-K dist, z+K dist]
cnt = {name: [0]*L for name in cond_defs}

for _ in range(N):
    K = bytes(rng.randrange(256) for _ in range(L))
    S0, _ = full_ksa(K)
    z = prga(S0, M)
    # per-round records
    S = list(range(256)); j = 0
    touched = [False]*256
    recs = []
    for i in range(L):
        b = S[i+1]
        j = (j + S[i] + K[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        touched[i] = True; touched[j] = True
        a = S[i+1]
        recs.append(dict(i=i, a=a, b=b, jj=j, untouched=not touched[i+1]))
    for i in range(L):
        if i in (1, 2, 3, 5, 8, 13, 20, 31):
            pfS, pfj = full_ksa(K[:i+1])
            recs[i]["pf"] = pfS[i+1]
            recs[i]["pfj"] = pfj
        for name, fn in cond_defs.items():
            if name == "pf==0" and "pf" not in recs[i]:
                continue
            if fn(recs[i]):
                cnt[name][i] += 1
                stats[name][0][(z[i] - K[i]) & 0xFF] += 1
                stats[name][1][(z[i] + K[i]) & 0xFF] += 1

for name in cond_defs:
    tot = sum(cnt[name])
    line = f"{name:22s} tot={tot:7d}"
    for k, lab in ((0, "z-K"), (1, "z+K")):
        c = stats[name][k]
        if tot > 0:
            v, n = c.most_common(1)[0]
            line += f"  {lab}: top 0x{v:02x} {n/tot*100:.2f}% (n={n})"
    print(line)

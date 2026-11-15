"""toomany: reset reseeds the MT19932 with the SAME SEED before every sample,
so the clean a-vector is identical each time; ~half the samples have exactly
one coordinate corrupted (random v). For two corrupted samples at the same
coordinate j: (v1 - v2)*FLAG_j == b1 - b2 (mod 127), e cancels exactly.
"""
import json
from collections import Counter, defaultdict

q = 127
samples = [json.loads(l) for l in open("samples.jsonl")]
N = len(samples)
print("samples:", N)

# 1) clean a = most common a; b_clean values are within +-1
ac = Counter(tuple(s["a"]) for s in samples)
a_clean, cnt = ac.most_common(1)[0]
print("clean a count:", cnt, "of", N)
b_clean = [s["b"] for s in samples if tuple(s["a"]) == a_clean]
print("b_clean values:", Counter(b_clean))
# e_clean unknown in {-1,0,1}; keep all three as reference set
b_ref = set(b_clean)

# 2) group corrupted samples by differing coordinate
groups = defaultdict(list)  # j -> list of (v, b)
bad = 0
for s in samples:
    a = tuple(s["a"])
    if a == a_clean:
        continue
    diffs = [j for j in range(len(a_clean)) if a[j] != a_clean[j]]
    if len(diffs) != 1:
        bad += 1
        continue
    j = diffs[0]
    groups[j].append((a[j], s["b"]))
print("corrupted samples grouped:", sum(len(v) for v in groups.values()), "unparseable:", bad, "coords hit:", sorted(groups))

def inv(x, m=q):
    return pow(x % m, -1, m)

# 3) per coordinate: pairwise exact solve, take mode; single-sample fallback
#    (e is IDENTICAL on every sample because reset reseeds with the same SEED,
#     so a lone corrupted sample gives (b - b_ref)*inv(v - a_j) exactly)
b_ref_val = Counter(b_clean).most_common(1)[0][0]
print("b_ref (clean, deterministic e):", b_ref_val)
FLAG = {}
details = {}
for j in sorted(groups):
    vals = Counter()
    (v1, b1) = groups[j][0]
    for (v2, b2) in groups[j][1:]:
        d = (v1 - v2) % q
        if d == 0:
            continue
        vals[(b1 - b2) * inv(d) % q] += 1
    if len(groups[j]) == 1:
        v, b = groups[j][0]
        d = (v - a_clean[j]) % q
        if d != 0:
            vals[(b - b_ref_val) * inv(d) % q] += 1
            print(f"j={j} single-sample fallback")
    details[j] = vals
    if vals:
        FLAG[j] = vals.most_common(1)[0][0]
    print(f"j={j:2d} n={len(groups[j]):3d} candidates={dict(vals)}")

# 4) known-char sanity check: '[flag value withheld — real-flag strings live only under FLAGS/]' at last
n = len(a_clean)
prefix = b"crypto{"
suffix = b"}"
ok = True
for i, ch in enumerate(prefix):
    if i in FLAG:
        match = FLAG[i] % q == ch % q
        print(f"check j={i} char={chr(ch)!r} recovered={FLAG[i]} -> {'OK' if match else 'MISMATCH'}")
        ok &= match
last = n - 1
if last in FLAG:
    match = FLAG[last] % q == suffix[0] % q
    print(f"check j={last} char='}}' recovered={FLAG[last]} -> {'OK' if match else 'MISMATCH'}")
    ok &= match
print("known-position sanity:", "PASS" if ok else "FAIL")

# 5) assemble; unknown positions: byte = residue (printable ASCII), else residue+127
out = bytearray()
for j in range(n):
    ch = None
    if j < len(prefix):
        ch = prefix[j]
    elif j >= n - len(suffix):
        ch = suffix[j - (n - len(suffix))]
    else:
        r = FLAG.get(j)
        if r is None:
            print("MISSING coord", j)
            ch = 0
        elif 33 <= r <= 126:
            ch = r
        else:
            ch = r + 127
            print(f"j={j} residue {r} not printable -> using {ch}")
    out.append(ch)
flag = bytes(out).decode()
print("FLAG:", flag)

# 6) full verification: every sample must satisfy b == <a, FLAG> + e (mod 127), e in {-1,0,1}
fl = [c for c in out]
fails = 0
for s in samples:
    t = sum(a * f for a, f in zip(s["a"], fl)) % q
    e = (s["b"] - t) % q
    if e not in (0, 1, q - 1):
        fails += 1
print(f"verification: {N - fails}/{N} samples consistent with e in {{-1,0,1}}")

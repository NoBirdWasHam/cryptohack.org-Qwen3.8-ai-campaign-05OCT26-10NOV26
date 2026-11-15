---
record: agent-aar
puzzle: challenge-209-cryptohack-2d_dlog
category: isogenies
url: https://cryptohack.org/challenges/2d_dlog/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/isogenies/challenge-6-cryptohack-2d_dlog/flag.txt"
flag_sha256: bcaa3ce35c033728330ec4b63e689685cc28d22664f773c6a902146b89f29ae7
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 209: DLOG on the Surface (2d_dlog)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack: 2-adic 2D Pohlig–Hellman lifting" [OBSERVED text; evidence tag applies to its source, not each claim]
Since p+1 = 2^127 (a pure 2-power), the whole dlog is one prime power: lift one bit at a
time. Precompute P1 = [2^126]P, Q1 = [2^126]Q (both order 2) and the 4-element candidate
table {O, P1, Q1, P1+Q1}. Maintain A = [a]P + [b]Q; at level k,
D = T − A = 2^k·(a_{k+1}P + b_{k+1}Q), so Dk = [2^{127−k−1}]D lands in the candidate
table, giving bits (a_{k+1}, b_{k+1}). 127 levels × O(127) doublings each — seconds in
pure Python with 128-bit-ish field mul. Exact-verification assert at the end
([a]P + [b]Q == T).

Result:
```
a = 8989068744398147088210219398915291813
b = 6850346275278222392661032070044244531
c = 20317470060808910705949514324772572305
d = 95527147648358416100018697076146379441
```

## reusable-rules
- **Never trust a provided "source" that contradicts the data.** Check digit widths of
  the data against the declared modulus first; a 38-digit coordinate under a 131-digit
  prime is a dead giveaway the files are from different versions.
- **You can recover an unknown F_p from points on y² = x³ + ax + b**: the cross-product
  consistency relations give integer multiples of p; a gcd across 3–6 components isolates
  p (then verify primality + all points on-curve + smooth p+1).
- **2D dlog on a 2-group = 2-adic lifting**, one bit per level with an order-2 candidate
  table — no BSGS needed, and it's exact (assert-verified).
- **Self-test EC arithmetic with the doubling chain itself** (every [2^k]P must stay
  on-curve); it caught the 2-torsion doubling bug that group-law spot tests missed.
- When a flag looks like it's "encrypted with something from the answer", brute the key
  *derivation space* (sha256/md5/concat/to_bytes × CTR/CBC × 16/32) with an
  ASCII-plausibility filter instead of guessing one derivation.

## anti-patterns / limits
- First curve/field assumption (trusting the template) was wrong.
- Doubling at a 2-torsion point (y=0) emitted an off-curve point until a y==0
  guard was added; caught by checking every [2^k]P against the curve.
- PyCryptodome CTR IV-length confusion (nonce=iv[:15] split) — moot, mode was CBC.
- Direct guesses crypto{str(v)} and CTR decryptions failed before the family
  search hit.

## artifacts [OBSERVED]
- code: flag2.py, solve.py
- data/logs: output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
The provided source.sage declares `p = 2^216·3^137 − 1` (131 digits) and
`EllipticCurve(F, [0, 1])`. But every coordinate in output.txt is only ~38 digits —
impossible for uniform F_p elements of a 131-digit prime. The source is a **template**
from another version of the challenge. Consequences:
- `EllipticCurve(F, [0,1])` in Sage = coefficient list **[a4, a6]** (NOT [a1, a2]) → the
  template curve is y² = x³ + 1. The *actual* curve had to be recovered from the points.
- The actual instance: **p = 2^127 − 1, E: y² = x³ + x**.

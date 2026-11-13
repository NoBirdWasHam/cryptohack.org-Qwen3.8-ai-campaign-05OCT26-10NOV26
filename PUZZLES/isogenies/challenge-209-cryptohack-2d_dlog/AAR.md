# AAR — Challenge 209: DLOG on the Surface (2d_dlog)

**Result:** **SOLVED** 2026-10-14 (UTC). Flag
`[flag — recorded in FLAGS/isogenies/challenge-209-cryptohack-2d_dlog/flag.txt]` submitted via
`submit_flag.py 2d_dlog ...` → API 200, score 7105→**7145**, solves 153→**154** (+40 pts).
No solutions page or writeup consulted; pure self-solve.

## What the challenge is
Two 2-primary torsion bases on a supersingular curve over F_{p²}:
(P, Q) and (R, S). Find (a,b,c,d) with R = [a]P + [b]Q, S = [c]P + [d]Q, then decrypt
(iv, ct) to get the flag.

## The trap: the visible source.sage does NOT match the data
The provided source.sage declares `p = 2^216·3^137 − 1` (131 digits) and
`EllipticCurve(F, [0, 1])`. But every coordinate in output.txt is only ~38 digits —
impossible for uniform F_p elements of a 131-digit prime. The source is a **template**
from another version of the challenge. Consequences:
- `EllipticCurve(F, [0,1])` in Sage = coefficient list **[a4, a6]** (NOT [a1, a2]) → the
  template curve is y² = x³ + 1. The *actual* curve had to be recovered from the points.
- The actual instance: **p = 2^127 − 1, E: y² = x³ + x**.

### Recovering p from the points (3-point consistency)
For y² = x³ + ax + b, with N_AB = (y_A² − y_B²) − (x_A³ − x_B³), D_AB = x_A − x_B in
F_{p²} (as plain integer pairs, i² = −1): the same a for all pairs implies
N_PQ·D_PR − N_PR·D_PQ ≡ 0 (mod p) component-wise. Taking the gcd of the six integer
components of three such cross-products M1, M2, M3 gave p = 170141183460469231731687303715884105727
(39 digits, Miller–Rabin prime, p+1 = 2^127 exactly). Fitting a,b from P,Q then put all
four points on y² = x³ + x.

## The attack: 2-adic 2D Pohlig–Hellman lifting
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

## Flag recovery
Neither `crypto{str(v)}` for any of the 8 v ∈ {a,b,c,d, 2^127−a,...} nor the first
~30 AES key seeds with CTR worked. A wider search (flag2.py: ~60 key families × CTR/CBC,
ASCII-plausibility filter) hit on the first pass:
- **AES-256-CBC**, key = **SHA256(str(a) + str(b) + str(c) + str(d))** (plain string
  concat, no separators), iv = the given 16 bytes.
- Plaintext: `[flag — recorded in FLAGS/isogenies/challenge-209-cryptohack-2d_dlog/flag.txt]` +
  PKCS7 (0x0b × 11).

## Errors & fixes (each cost time)
1. **Sage 2-list coefficients = [a4, a6]**, not [a1, a2] — first curve guess wrong.
2. **Template/data mismatch** — coordinates 38 digits vs 131-digit p; fixed by
   recovering p via the 3-point gcd trick instead of trusting the source.
3. **EC doubling at a 2-torsion point (y = 0)**: vertical tangent → 2P = O, but the code
   computed λ with denominator 2y = 0 (f2_div by zero-norm returned (0,0)) and emitted an
   off-curve point (2i, 0). Found by checking on-curve-ness of the doubling chain —
   first bad step was [2^127]P from [2^126]P = (−i, 0). Fix: `if y1 == (0,0): return O`.
4. **PyCryptodome MODE_CTR**: 16-byte IV must be split `nonce=iv[:15], initial_value=iv[15:]`
   (16-byte `initial_value` → "Incorrect length for counter byte string (16, expected 8)";
   `nonce=iv` → "Nonce is too long"). (Turned out moot — the mode was CBC anyway.)
5. **f2_mul(3, x)** — passing a bare int to a pair-based field op; use (3 % p, 0).

## Learning points
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

## Files
`site.md` (statement + files + recovered params), `source.sage`, `output.txt`,
`solve.py` (full pipeline, re-runnable end-to-end), `flag2.py` (key search), `flag.txt`.

## Vulnerability (plain words)

Two compounding weaknesses. (1) The task is exactly the sub-problem behind SIDH
key recovery — writing one 2-power torsion basis (R,S) in terms of another (P,Q)
on a supersingular curve — which is meant to be infeasible; but the chosen field
is p = 2^127 − 1 with #E(F_p) = p+1 = 2^127 exactly, so the entire dlog lives in a
single 2-group where Pohlig–Hellman-style lifting reduces every level to a 2-bit
table lookup. (2) The provided "source.sage" is a stale template from a different
instance, so trusting it is a trap — the real parameters must be read off the data.

## How the answer follows

- Data-vs-source check: output.txt coordinates are ~38 digits while the template
  claims a 131-digit p. Eliminating (a,b) between three points on y² = x³+ax+b
  (cross-products of pairwise slope-consistency relations) yields integers whose
  gcd is p = 2^127 − 1 (prime; p+1 = 2^127); fitting then puts all four points on
  y² = x³ + x.
- 2-adic 2D lifting: precompute P1 = [2^126]P, Q1 = [2^126]Q and the 4-entry
  order-2 table {O, P1, Q1, P1+Q1}. Maintain A = [a]P+[b]Q; the difference
  D = T − A is divisible by 2^k, and Dk = [2^{127−k−1}]D equals exactly one table
  entry, which reveals the next bit-pair (a_{k+1}, b_{k+1}). 127 levels give
  (a,b), likewise (c,d), with final assert [a]P+[b]Q == T.
- Key derivation was a search, plainly stated: ~60 plausible key families ×
  CTR/CBC with an ASCII-plausibility filter; hit = AES-256-CBC with
  key = SHA256(str(a)+str(b)+str(c)+str(d)) → flag.

## Limitations / attempts that failed

- First curve/field assumption (trusting the template) was wrong.
- Doubling at a 2-torsion point (y=0) emitted an off-curve point until a y==0
  guard was added; caught by checking every [2^k]P against the curve.
- PyCryptodome CTR IV-length confusion (nonce=iv[:15] split) — moot, mode was CBC.
- Direct guesses crypto{str(v)} and CTR decryptions failed before the family
  search hit.

## Sources

- Pohlig–Hellman reduction: textbook-level knowledge retrieval (stated plainly);
  the points→p gcd recovery was derived in-run.
- PyCryptodome docs (mode/IV constraints).
- No solutions page or writeup consulted — the AAR records a pure self-solve.

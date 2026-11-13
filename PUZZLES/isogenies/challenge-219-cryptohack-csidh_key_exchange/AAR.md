# AAR — challenge-219: CSIDH Key Exchange (cryptohack.org, 90 pts)

**Status:** SOLVED, submitted live 2026-10-21. 11480 → 11570 (202 solved).
**Flag:** `[flag — recorded in FLAGS/isogenies/challenge-219-cryptohack-csidh_key_exchange/flag.txt]`

## Problem
CSIDH-512: p = 4·∏(75 primes 3..587) − 1, E0: y²=x³+x over F_p, both private exponent
vectors a_priv, b_priv ∈ [−3,3]^75 given. Shared secret = Montgomery coefficient A of
[a+b]E0; flag = AES-CBC-SHA256(str(A)). iv/ct in source.

## Approach
Class-group action is abelian ⇒ shared = walk from E0 with exponents (a+b)[i]:
- **110 signed pointwise ℓ-steps** (Σ|e|), each a single Vélu isogeny over F_p (512-bit).
- Coefficients via Galbraith Thm 25.1.6 short-Weierstrass formulas
  (a4′=a4−5Σt, a6′=a6−7Σ(u+x·t), t=2(3x²+a4), u=4y², ±-pair reps) —
  **validated first on p=419**: 5-step j=13, second step j=98 (prime_power ground truth) ✓.
- Kernel generator: #E = p+1 (supersingular, trace 0, isogenous to E0) and ℓ² ∤ p+1
  ⇒ E(F_p)[ℓ] cyclic: random x → y (p≡3 mod 4 sqrt), Q = [(p+1)/ℓ]P ≠ O.
- Negative exponent: twist by fixed nonsquare d=2, forward step, twist back.
- Final curve (a4,a6): 2-torsion root of x³+ax+b — **p ≡ 2 (mod 3) ⇒ cubing is a
  bijection ⇒ Cardano with cbrt(u)=u^((2p−1)/3)** finds a rational root directly
  (no gp/polrootsmod needed); factor to quadratic for the rest.
- Exactly one root v has 3v²+a4 square ⇒ A = 3v/pow(√(3v²+a4),−1,p) (principal root,
  same convention accepted on 206/209). First candidate decrypted.

## Pitfalls (Observed)
- Python `open(...,"w")` on Windows wrote CRLF into the .gp file → gp echoed `\r` garbage
  and polrootsmod output was unparseable. Fix: avoid gp here entirely (Cardano), or write
  with `newline="\n"`.
- First EC-doubling draft dropped the `+a4` term in the slope — caught by the
  GA==[2^ea]G-style sanity checks, not by a crash. Always assert on-curve/order checks.
- Brute-force helpers from velu_engine.py (point enumeration, root scan) are O(p) —
  fine at p=419, hopeless at 512 bits; replaced with O(ℓ)-per-step code.

## Files
`solve.py` (walk + Cardano + Montgomery + decrypt), `walk_cache.txt` (final a4,a6),
`solve.log` (full run), `flag.txt`.

## Verification
- Formula pre-validation on p=419 ground truth (j=13, 98).
- Kernel order asserted (mul(Q,l)==O) every step; root check asserted for all 2-torsion roots.
- AES decrypt produced valid PKCS#7 + `crypto{...}`; live submit `score_delta: 90`.

## Vulnerability (plain words)

The challenge exposes both CSIDH private exponent vectors a_priv, b_priv
(teaching setup). The mathematical property exploited is CSIDH's own design: the
class-group action is abelian, so the shared curve depends only on the SUM of the
exponent vectors — shared = action of (a+b) on E0 — one combined walk instead of
two independent ones.

## How the answer follows

- Each nonzero exponent = one Vélu step by the pointwise kernel E(F_p)[ℓ]
  (ℓ² ∤ p+1 ⇒ the kernel is cyclic; a generator is a random point times (p+1)/ℓ),
  forward for +e and twist(d=2) → step → untwist for −e — the twist trick is the
  inverse ideal (the conjugate prime) in Cl(−p). Total 110 signed steps (Σ|e|).
- Class-group commutativity ⇒ step order is irrelevant; the final (a4,a6) is the
  shared-secret curve whichever party walks first — this is exactly why [a+b]E0
  reproduces the negotiated key.
- Montgomery A of the final curve: solve x³+a4x+a6 = 0 for 2-torsion roots —
  p ≡ 2 mod 3 makes cubing a bijection, so Cardano works exactly with
  cbrt(u) = u^((2p−1)/3). Exactly one root v has 3v²+a4 square;
  A = 3v / sqrt(3v²+a4) (principal root — the same convention accepted on
  206/209).
- Formulas pre-validated on the p = 419 ground truth (prime_power walk: j=13
  then 98); kernel order asserted at every step; first A decrypted
  (AES-256-CBC, key = SHA256(str(A))) →
  [flag — recorded in FLAGS/isogenies/challenge-219-cryptohack-csidh_key_exchange/flag.txt]; server +90.

## Limitations / attempts that failed

- velu_engine.py's brute-force helpers (O(p) enumeration/root scans) were fine at
  p = 419, hopeless at 512 bits — replaced by O(ℓ)-per-step code.
- Python text-mode writes embedded CRLF in a .gp helper, corrupting polrootsmod
  output; fixed by dropping gp for the cubic (Cardano route).
- First doubling slope omitted +a4 — caught by order/on-curve assertions, not by
  a crash.

## Sources

- Galbraith et al. Thm 25.1.6 Vélu formulas (inherited from prime_power,
  re-validated).
- CSIDH protocol and instance parameters from the challenge's own source.sage.
- No third-party writeups or solution pages consulted (run log).

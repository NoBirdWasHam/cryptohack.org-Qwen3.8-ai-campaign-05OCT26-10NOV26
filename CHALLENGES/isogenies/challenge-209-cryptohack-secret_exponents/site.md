# CSIDH Secret Exponents — CryptoHack / Isogenies (60 pts)

slug: `csidh_secret_exponents` · category: Isogenies · points: 60
Solved: 2026-10-15 · flag: `404` (bare integer, server-verified +60)

## Statement (verbatim from remaining_descs.json)
In the CSIDH key exchange, a private key is a list of integers as long as the number of odd
primes dividing (p+1). This data represents an exponent vector [e_0, e_1, e_2, ..., e_k] which
dictates the path of Alice and Bob's secret isogenies. Before implementing CSIDH let us begin by
computing an isogeny with the secret vector [2,3,4] from the starting curve
E_0 : y² = x³ + x mod 419. The flag for this challenge is the Montgomery coefficient A of the
codomain. Essentially what this challenge is asking you to do is compute an isogeny of degree
n = 3² · 5³ · 7⁴. You will need this code again throughout this section, think about how to
write this efficiently so you can generalise it to other vectors and other characteristics!

## Parameters
- p = 419 (p ≡ 3 mod 4; F_p sqrt via pow(v, (p+1)//4, p)).
- E₀ : y² = x³ + x, j = 1728 (≡ 52 mod 419), #E₀(F_p) = 420 = 2²·3·5·7 (supersingular family).
- Secret vector [2,3,4] over primes [3,5,7] → forward CSIDH steps:
  [3, 3, 5, 5, 5, 7, 7, 7, 7] (9 isogenies, degree 9·125·2401 = 2,702,250).
- At every step #E(F_p) = 420 is preserved (isogenous curves), and for ℓ ∈ {3,5,7} with
  ℓ² ∤ 420 the pointwise ℓ-torsion E(F_p)[ℓ] is cyclic of order ℓ → exactly ONE
  pointwise-rational ℓ-subgroup → the walk is deterministic (any order-ℓ generator gives
  the same Vélu codomain).
- Flag: the Montgomery coefficient A of the final codomain, i.e. the isomorphism
  y² = x³ + a x + b  →  Y² = X³ + A X² + X.

## Answer
Final codomain after the 9-step walk [3,3,5,5,5,7,7,7,7]: **y² = x³ + 196x + 398 mod 419**
(j = 48, #E = 420). Unique 2-torsion root v = 410 with 3v²+a a square →
**A = 3v / √(3v²+a) = 404** → flag `404` (server-verified, +60).

## Montgomery conversion (the answer format)
For y² = x³ + a x + b with a rational 2-torsion x-root v (v³ + a v + b = 0):
1. Shift x = X + v  →  y² = X³ + 3v X² + (3v² + a) X.
2. Scale X = w X′ with w² = 3v² + a  →  Y² = X′³ + (3v / w) X′² + X′.
3. **A = 3v / w**, w = principal sqrt(3v² + a)  (challenge convention: the server-accepted
   206 answer 199 is the principal-root value; A and −A are the same F_p-isomorphism class
   here because −1 is a nonsquare mod 419).

## Engine
`velu_engine.py` — fully self-contained (no PARI, no external libs):
- Vélu x-map point-by-point: x(φ(R)) = x(R) + Σ_{Q∈K\{O}} [x(R+Q) − x(Q)].
- Codomain reconstruction from the image x-coordinates + quotient (coset) group structure:
  three non-collinear image cosets pin a' via F_T(a', b') = A a′² + B a′ − 4 b′ + C = 0;
  uniqueness enforced (ambiguity → hard error, never a silent guess).
- Per-step checks: kernel invariance of the x-map; every image x-value gives square RHS.
- `crosscheck` mode reproduces the prime_power AAR walk data model-by-model (see AAR).

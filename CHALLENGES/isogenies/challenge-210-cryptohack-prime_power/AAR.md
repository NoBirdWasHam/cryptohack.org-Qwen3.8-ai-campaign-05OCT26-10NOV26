# AAR — Challenge 210: Prime Power Isogenies (50 pts, isogenies)

**Date:** 2026-10-14 · **Status:** SOLVED (server-verified) · **Answer:** `27` · **Delta:** +50 (7145 → 7195, 154 → 155 solved)
**Method:** self-solve. Two fully independent implementations (Python Vélu from scratch; PARI/GP `ellisogeny`) agree at every step of both walks. No writeups used.

## Problem

E0: y² = x³ + x over F_419; #E0 = 420; p+1 = 420 = 2²·3·5·7.
1. (observation) Compute the degree 5^9 isogeny (repeated pointwise 5-isogenies). What do you see?
2. (answer) How many 7-isogenies to get back to E0?

## Solution

**Model.** At each step take the *pointwise-rational* l-isogeny: kernel E(F_p)[l].
Since l ∈ {5,7} divides 420 = #E but l² ∤ 420, E(F_p)[l] is cyclic of order l → unique
pointwise kernel → Vélu codomain is deterministic. (Isogenous curves keep #E = 420, so the
property holds at every step.) Vélu formula (Galbraith et al. Thm 25.1.6, short-Weierstrass,
odd kernel): with u(Q)=4yQ², t(Q)=2(3xQ²+a4) summed over ±-pair reps:
A4' = a4 − 5·Σt, A6' = a6 − 7·Σ(u + xQ·t).

**Implementation 1 (Python, `solve.py`).** From-scratch EC arithmetic + Vélu. Formula
validated against the book's worked example (two_isogenies: y²=x³+x / Q(i), kernel (i,0)
→ y²=x³+11x+14i, j=287496 — reproduced exactly).

**Implementation 2 (PARI/GP 2.17.4, `pp_verify27.gp`).** `ellisogeny(E, S[1])` with
S = all pointwise order-l points (brute-force enumeration). Built-in Vélu, independent of
implementation 1.

**Results (both implementations, step-by-step identical):**
- 5-walk j-sequence: 52 → 13 → 98 → 62 → 407 → 407 → 62 → 98 → 13 → **52** (d=9).
  Model at d=9: y² = x³ + 321x; 321 = 66⁴ = 353⁴ mod 419 → **isomorphic to E0**.
  → "what do you see": the degree 5^9 isogeny lands back on the starting curve (9-cycle).
- 7-walk: first return to E0's isomorphism class at **d = 27** (model y² = x³ + 215x;
  215 = 113⁴ = 306⁴ mod 419). No earlier step is isomorphic to E0. j-sequence is palindromic
  around the middle (…407 | 396 396 | 407…).

**Submission:** `submit_flag.py prime_power "27"` → HTTP 200 "Flag submitted"; API user
endpoint confirms score 7145 → 7195 (+50), solved 154 → 155.

## Key findings / pitfalls

1. **j(E0) = 1728 mod 419 (52).** E0 is the mod-419 reduction of the j=1728 curve.
   j-invariants here should be read mod p: "52" *is* 1728. (Nearly caused a wrong
   special-case analysis.)
2. **Two rational l-isogenies per curve, not one.** Over F_{p²}, l-torsion is full
   ((Z/l)² since l² | #E(F_{p²}) = p²+1+2p): each curve has a second, Galois-conjugate,
   non-pointwise rational l-isogeny. The CSIDH walk (and this challenge) uses the
   *pointwise* kernel E(F_p)[l]. Any "unique rational l-isogeny" assumption is only valid
   when l² ∤ #E(F_{p²}).
3. **j-level walks are NOT well-defined.** Two F_p-twins (twists) with the same j can have
   different pointwise l-isogeny codomain j's (observed for j=98: models (239,292)→62 vs
   (67,113)→13). The walk must be followed on actual (a4,a6) models (the Vélu codomain),
   never by reconstructing curves from j. My first PARI attempt did exactly that
   (curve_from_j each step) and produced a wrong 2-cycle; the Python model-level walk is
   the correct one.
4. **Isomorphism test to E0:** (a4',a6') ~ (1,0) ⟺ a6'=0 and a4' a 4th power; for p=419
   the 4th powers are exactly the QRs (gcd(4,418)=2), so a QR test suffices.
5. **PARI 2.17.4 (gp64.exe) parser quirks (confirmed again this session):**
   - `for (i, n, { ... })` brace blocks: "embedded braces (in parser) is not yet implemented".
   - Top-level multi-statement `for` bodies: syntax error; works inside a function body.
   - Multi-line `print(...)` inside a for body: parser breaks; keep each statement on one line.
   - `Str(x) + Str(y)` string concatenation: "forbidden addition t_STR + t_STR" — use
     multi-arg `print`.
   - Working pattern: functions with semicolon-separated single-line for-body statements
     (see `pp_graph.gp`, `pp_verify27.gp`).

## Verification

- Python Vélu vs PARI `ellisogeny`: identical (a4, a6, j) at all 27 + 9 steps.
- Vélu formula cross-checked against the primary source's worked example (exact match).
- Point counts: 419 affine points on E0 (brute force, both implementations).
- Kernels: exactly 4 (l=5) / 6 (l=7) pointwise order-l points at every step (cyclic ✓).
- All chain curves: #E = 420 (isogenous ⇒ same cardinality ✓).
- Server: answer accepted, full 50 points.

## Vulnerability (plain words)

Not an exploit. A supersingular curve over F_p has p+1 rational points — here 420
= 2²·3·5·7, perfectly smooth — so long isogeny walks through the full rational
ℓ-torsion stay entirely inside F_p and are cheap to run. The challenge asks you to
walk and count returns: the answer 27 is the order of the ℓ=7 class-group step —
27 pointwise 7-isogenies is the first time you land back on E0's isomorphism
class (the ℓ=5 observation: a degree-5^9 walk already closes, order 9).

## How the answer follows

- Since ℓ² does not divide 420, every curve on the walk has a cyclic pointwise
  kernel E(F_p)[ℓ] → a unique pointwise Vélu step, deterministic at the (a4,a6)
  model level. (Each curve also has a second, Galois-conjugate rational ℓ-isogeny
  over F_{p²}; confusing the two is the trap, and walks must run on models, not
  j-values: F_p twins with equal j can step to different codomain j's.)
- Vélu (short Weierstrass, Galbraith et al. Thm 25.1.6): A4′ = a4 − 5·Σt,
  A6′ = a6 − 7·Σ(u + xQ·t), with u = 4yQ², t = 2(3xQ²+a4) over ±-pair reps.
- 5-walk closes at degree 5^9: model y² = x³ + 321x with 321 a 4th power mod 419
  → isomorphic to E0; j-sequence 52→13→98→62→407→407→62→98→13→52 is palindromic
  (the dual path retraces). The 7-walk first returns at d = 27 (model
  y² = x³ + 215x, 215 a 4th power). Return test: a6′ = 0 and a4′ a 4th power —
  gcd(4,418) = 2 makes a QR test sufficient.
- Two fully independent implementations (Python Vélu; PARI ellisogeny) agree at
  every step of both walks (27+9 steps); server accepted 27.

## Limitations / attempts that failed

- The first PARI attempt rebuilt the curve from j at each step and produced a
  wrong 2-cycle — proof that j-level walks are not well-defined; discarded.
- j(E0) = 52 is just 1728 mod 419; nearly triggered a false special-case analysis.
- PARI 2.17 parser quirks cost time (brace blocks, multi-statement for-bodies,
  Str+Str concatenation).

## Sources

- Galbraith et al., Thm 25.1.6 (Vélu short-Weierstrass formulas), pre-validated
  against the two_isogenies worked example.
- PARI/GP ellisogeny as the second implementation.
- No third-party writeups or solution pages consulted (AAR: self-solve).

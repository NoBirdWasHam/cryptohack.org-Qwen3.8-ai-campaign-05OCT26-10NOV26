# Five Isogeny CSIDH Twist — CryptoHack / Isogenies (70 pts)

slug: `five_iso_csidh_twist` · category: Isogenies · points: 70
Solved: 2026-10-15 · flag: `261` (bare integer; score_delta +70, 7665→7735)

## Statement (from remaining_descs.json)

In the challenge "CSIDH prime power isogenies" we explored the ℓ-isogeny graphs for the
curves we use in CSIDH and saw that they were cyclic. We were able to compute how many
vertices there were in the graph and effectively walk all the way around until we reached
the starting node again. We also know that given some point of order ℓ on the curve,
there seems to be only one way to walk from each node and that this graph is directed.
This challenge is about how we can effectively (and efficiently) take one step
"backwards" on the graph. This means if the ℓ-isogeny graph has k nodes, instead of
computing k-1 ℓ-isogenies to go backwards we can compute just a single isogeny in the
other direction. To do this, we will need to be able to compute the quadratic twist E^t
of a curve. Look at this curve in Montgomery form. Notice that it is not isomorphic to
E. Compute their j-invariants. Compute their order, are they isogenous? To walk
backwards on the graph we temporarily work on the quadratic twist. Practically, to walk
one step backwards we map E → E^t. From this twisted curve, we compute as normal an
isogeny of degree ℓ using a point of order ℓ on the twisted curve. Then, we untwist the
codomain (by computing a second quadratic twist) to finish the computation. To test your
code, use the solution of "CSIDH prime power isogenies" and compare the result of taking
k-1 "forward" 7-isogenies and a single "backwards" isogeny. Note: if you are computing
x-only isogenies you do not need to explicitly compute the twist, but instead compute
random x-coordinates in F_p. A point is on E when x³ + Ax² + x is a square and E^t when
it is not. From this, we see that checking the squareness of y² is enough to determine
if you will take a step forwards or backwards when this x-only point is used to compute
an isogeny. To compute the flag, walk one step "backwards" on the three-isogeny graph
from the below curve. The flag is the Montgomery coefficient of this curve.
E_0 : y² = x³ + x mod 419. In the CSIDH exponent vector, when an integer is positive we
take e steps from the curve on the ℓ-isogeny graph. When the integer is negative, we
take e steps from the quadratic twist of the curve on the ℓ-isogeny graph.

## Answer
**Flag = 261** (Montgomery coefficient A of y² = x³ + 261 x² + x ≅ the backward-step curve).

## Method
1. **Forward walk (k−1 cross-check, per the statement's own test):** pointwise 3-isogeny
   chain from E_0 (y²=x³+x, #E=420, j=52). The 3-isogeny graph is a **27-cycle** (NOT 3):
   j-seq = [52, 356, 180, 98, 48, 354, 407, 184, 274, 62, 106, 396, 13, 0, 0, 13, 396,
   106, 62, 274, 184, 407, 354, 48, 98, 180, 356, 52] — palindromic, class-return at
   step 27 (model-level return not within 27). So k=27, backward 1 step = forward 26 steps.
2. **Twist algorithm (the statement's method):**
   - E^t = twist(E_0, d=2) (2 nonsquare mod 419): y² = x³ + 4x (b=0 stays 0), #E^t = 420.
   - P = (63, 347) order 3 on E^t; Vélu 3-isogeny E^t → F: y² = x³ + 309x + 326 (j=356).
   - Untwist F (twist again with d=2): G = y² = x³ + d²·309·x + d³·326 = y² = x³ + 398x + 94.
   - j(G) = 356 = j of forward-1-step curve ✓ (palindromic: forward-26 has same class).
3. **Montgomery A of G** (principal-sqrt convention A = 3v/√(3v²+a), the challenge
   convention verified on special_isogenies (199) and csidh_secret_exponents (404)):
   G → **A = 261**, point-mapping verified on all 420 points.

## Verification
- j(G) = 356 matches the forward-26 (≡ forward-1 by palindromicity) class: E_1 =
  y²=x³+182x+64 (PARI-verified isogeny in velu_engine TEST3) has j=356, #E=420 → same
  F_p-isomorphism class as G ✓.
- A(G) = 261, A(E_1) = 158 = −261 mod 419 — the same class's two Montgomery signs,
  consistent with the skill's "A vs −A same class" fact.
- The statement's own test: k−1=26 forward steps ≡ single backward step (both land in
  the j=356 class) ✓.
- Server: score_delta +70.

## Lesson
The "3-isogeny graph" here has k=27 nodes, not 3 — do NOT assume k=ℓ; run the forward
walk to find the class-return. (Observed cycle lengths for p=419, #E=420: ℓ=3 → 27,
ℓ=5 → 9, ℓ=7 → 27.) The ± sign of the Montgomery A is resolved by computing it from
the specific curve model the algorithm produces (G), principal-root convention.

## Evidence
- velu_engine.py (copied from challenge-209; ground-truth TEST1-3 pass)
- solve_twist.py (Methods A/B; Method A's 3-cycle assumption failed the j-check — see AAR)
- walk3.py (full 27-step j-sequence)
- flagA.py (Montgomery A of G and E_1)
- flag.txt

# AAR — five_iso_csidh_twist (CryptoHack Isogenies, 70 pts)

## Result
**SOLVED 2026-10-15.** Flag `261` accepted, score_delta +70 (7665 → 7735; 163 → 164).

## Attack
Backward step on the 3-isogeny graph from E_0: y²=x³+x mod 419, via the quadratic twist:
1. E^t = twist(E_0, d=2): y²=x³+4x (d nonsquare; b=0 stays 0; #E^t=420).
2. P=(63,347) order-3 point on E^t; Vélu 3-isogeny → F: y²=x³+309x+326.
3. Untwist F with d=2 → G: y²=x³+398x+94 (the landed "backward" curve).
4. Montgomery A of G (principal sqrt): A = 261 (420/420 point-mapping verified).
Cross-check: forward 3-walk is a 27-cycle (palindromic j-seq); forward-26 ≡ backward-1,
landing in the same j=356 class as G (E_1 = y²=x³+182x+64, PARI-verified, A=158=−261).

## Verification
- j(G)=j(E_1)=356, #E=420 both → same F_p class ✓
- A(G)=261 vs A(E_1)=158: same-class sign pair ✓ (skill-consistent)
- Server score_delta +70 ✓

## Bug found (self-inflicted, caught immediately)
First attempt assumed the 3-isogeny graph is a 3-cycle (k=ℓ) → "backward 1 = forward 2"
→ A=410. The twist method's j-check (j=356 ≠ 180) refuted it instantly. Lesson: the
ℓ-isogeny graph's cycle length k is NOT ℓ in general (observed p=419: ℓ=3→27, ℓ=5→9,
ℓ=7→27); run the forward walk to find k. The statement's "k−1 forward" test is the
built-in consistency check — use it.

## Flag format
Bare integer (Montgomery A), no wrapper. 1 submission.

## Evidence
velu_engine.py, solve_twist.py, walk3.py, flagA.py, site.md, flag.txt.

## Vulnerability (plain words)

The exercise is the CSIDH "backward step": move to the other neighbour on the
ℓ-isogeny graph (the inverse class-group direction) without searching the graph.
The trick: each curve here has two F_p-rational ℓ-isogenies — the pointwise kernel
E(F_p)[ℓ] and its Galois-conjugate twin — and the quadratic twist swaps those two
kernels. So: twist the curve, take an ordinary forward Vélu step on the twist, and
untwist the result — that composes to exactly one backward step.

## How the answer follows

- E^t = twist(E0, d = 2): y² = x³ + 4x, #E^t = 420, so E^t carries a rational
  order-3 point P = (63,347). Vélu 3-step on the twist gives F: y² = x³ + 309x +
  326; untwisting F by d = 2 gives G: y² = x³ + 398x + 94 — the curve one step
  *behind* E0 on the 3-isogeny graph.
- Answer = Montgomery A of G (principal-sqrt convention): A = 261, verified by a
  420/420 point-mapping check of the isomorphism.
- Built-in consistency check fired: the forward 3-walk from E0 is a 27-cycle, so
  forward-26 ≡ backward-1; the forward-26 curve E1 has j = 356 (same F_p class as
  G, same #E = 420) and A = 158 ≡ −261 mod 419 — the expected same-class sign
  pair. Server accepted 261 (+70).

## Limitations / attempts that failed

- First attempt assumed the 3-isogeny graph cycle length equals ℓ ("backward 1 =
  forward 2", A = 410): refuted instantly by the j-check (356 ≠ 180). Observed
  cycle lengths at p = 419: ℓ = 3 → 27, 5 → 9, 7 → 27. Never assume k = ℓ; run
  the forward walk to find k, and use the statement's k−1-forward test.

## Sources

- Quadratic twist swapping the two Galois-conjugate rational kernels: standard
  supersingular-curve theory (textbook level).
- Earlier server-verified AARs in this corpus (prime_power, secret_exponents) for
  the cycle data and the A sign-pair convention.
- No third-party writeups or solution pages consulted (run log).

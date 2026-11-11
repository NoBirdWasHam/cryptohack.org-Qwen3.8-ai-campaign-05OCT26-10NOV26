# AAR — special_isogenies (CryptoHack Isogenies, 30 pts)

Date: 2026-10-12 · Worker: Hermes · Status: SOLVED (+30, verified by server)

## Result
- Flag `199` (bare) → server delta **+30**, score 6360→6390, solved 134→135.
- Task: Vélu degree-5 isogeny of E₀: y² = x³ + x mod 419 (kernel = the unique
  F_419-rational 5-torsion subgroup ⟨(185,73)⟩); report the Montgomery A of the codomain.

## Method
1. **PARI `ellisogeny`** (per `ctf-isogenies` skill): codomain **y² = x³ + 269x + 82**,
   j = 13, #E′ = 420. (Consistent with the isogeny theorems: #E′/#E = 5 is not required
   for F_p-point counts — the dual isogeny's kernel is fully rational, so #E′ can equal #E;
   the initial "must be 84" intuition was WRONG for F_p-point counts.)
2. **Montgomery conversion** (short-Weierstrass → y²=x³+Ax²+x):
   - rational 2-torsion root v = 23
   - x = X + 23 → y² = X³ + 69X² + 180X
   - scale u⁴ = 180 → u² = √180 = 173
   - **A = 69/173 mod 419 = 199**
3. **Twist disambiguation**: j(A)=13 has two F_419 solutions {199, 220} (twists).
   Applied the explicit isomorphism (X=x−23, X′=X/u², Y′=Y/u³) to all 210 F_419 codomain
   points: **210/210 land on A=199, 1/210 on A=220** → A=199.

## What went wrong (and lessons)
- Spent several rounds doubting the codomain because #E′=420 ≠ 420/5=84. That "contradiction"
  was a misconception: #E(F_p) of the codomain is NOT forced to be #E(F_p)/deg when the dual
  kernel is rational. PARI's map + point-count are self-consistent; trust them.
- Hand-rolled Vélu x′/y′ maps (and my memorized codomain coefficient formulas) kept failing
  point-consistency checks. Per the two_isogenies AAR: **never hand-derive Vélu data — use
  PARI `ellisogeny`**; the only thing that matters is converting its codomain to the required
  model (Montgomery here).
- PARI syntax friction (file-based gp64, `subst` not call-syntax, `poldegree` not `degree`)
  cost time; recorded in `ctf-isogenies`.

## Evidence
- Server: `submit_flag.py special_isogenies 199` → `{"score_delta": 30, "after": {"score": 6390, "solved": 135}}`.
- PARI: `ellisogeny(E,(185,73))` → codomain [0,0,0,269,82] mod 419, j=13.
- Python: isomorphism 210/210 → A=199 (vs 1/210 for twist 220).

## Open items
- prime_power (50), comp_isogenies (60), whats_my_kernel (70), csidh_* (60-90),
  sidh_key_exchange (80), breaking_sidh (250), five_iso_csidh_twist (70).
  PARI `ellisogeny` + Montgomery/short-Weierstrass conversion covers the answer-type ones.
## Vulnerability (plain words)
No vulnerability — an answer-type isogeny computation: E0: y^2 = x^3 + x over F_419 has an F_419-rational point of order 5, so the quotient by its kernel is an explicit degree-5 Vélu isogeny defined over F_419; the requested answer is just the codomain rewritten in Montgomery shape y^2 = x^3 + Ax^2 + x. Everything is constructive because the kernel generator is rational — no extension-field arithmetic.

## How the answer follows
1. Kernel: the unique F_419-rational 5-torsion subgroup <(185,73)>. PARI `ellisogeny(E0,(185,73))` -> codomain y^2 = x^3 + 269x + 82, j = 13, #E'(F_419) = 420. The "#E' must be 420/5 = 84" intuition is a misconception: #E(F_p) is NOT forced to divide by deg when the dual isogeny's kernel is also fully rational — PARI's map and point-count are self-consistent.
2. Convert the codomain to Montgomery: find the rational 2-torsion root v = 23 (23^3 + 269*23 + 82 = 0 mod 419 — re-checked at AAR-upgrade time); translate x = X + 23 -> y^2 = X^3 + 69X^2 + 180X (constant term vanishes exactly, as it must); scale X = u^2 X', Y = u^3 Y' with u^4 = 180 so the X coefficient normalizes to 1: u^2 = sqrt(180) = 173; A = 69/u^2 = 69*173^-1 = **199** mod 419 (re-checked).
3. Twist disambiguation: j = 13 admits two F_419 Montgomery shapes, A in {199, 220} = +/-199 (quadratic twists, isomorphic only over F_419^2). Applying the explicit isomorphism (X = x-23, X' = X/u^2, Y' = Y/u^3) to the recorded 210 F_419 codomain points lands 210/210 on A=199 vs 1/210 on A=220 — the image curve is A=199, not the twist. Answer **199** (bare); server delta +30 confirms.

## Limitations / attempts that failed
- Hand-rolled Vele x'/y' maps and memorized codomain-coefficient formulas repeatedly failed point-consistency checks — lesson banked in the `ctf-isogenies` skill: use PARI `ellisogeny`, never hand-derive Velu data; the only real work is the model conversion.
- Several rounds lost to the #E' = 420 != 84 misconception above.
- PARI syntax friction cost time (file-based gp64, `subst` vs call syntax, `poldegree` not `degree`) — recorded in `ctf-isogenies`.

## Sources
PARI/GP `ellisogeny` (manual); `ctf-isogenies` skill; evidence quoted in the original AAR (server JSON `score_delta:30`, PARI codomain output, 210-point Python check); `solve.py` in this folder. No solutions/writeups consulted.

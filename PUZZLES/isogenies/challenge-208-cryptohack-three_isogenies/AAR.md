# AAR — three_isogenies (CryptoHack Isogenies, 35 pts)

Date: 2026-10-12 · Worker: Hermes · Status: SOLVED (+35, verified by server)

## Result
- Flag `[flag — recorded in FLAGS/isogenies/challenge-208-cryptohack-three_isogenies/flag.txt]` (bare) → server delta **+35**, score 6325→6360, solved 133→134.
- Vélu 3-isogeny of E: y² = x³ + x mod p (p = 2^18·3^13 − 1), kernel ⟨K⟩,
  K = (483728976, 174842350631). Flag = j(E′).

## Method
1. Verified K ∈ E and 3K = O with an independent Python group-law implementation
   ([2]K = (483728976, 243099857880) = −K, consistent).
2. **PARI `ellisogeny`** (per `ctf-isogenies` skill): codomain
   y² = x³ + 417919813652 x + 36118389888 (mod p); j = `ellinit(ph[1])[13]` = [flag — recorded in FLAGS/isogenies/challenge-208-cryptohack-three_isogenies/flag.txt].
3. **Independent Python cross-check** with the standard j-formula
   j = c4³/D, c4 = −48a, D = −16(4a³+27b²): exact match [flag — recorded in FLAGS/isogenies/challenge-208-cryptohack-three_isogenies/flag.txt].

## Notes
- This was fast because the two_isogenies AAR had already established the PARI workflow
  (and that hand-rolled Vélu formulas are unreliable). No fpylll needed.
- For odd-degree kernels PARI takes the generator point directly (the kernel polynomial
  is internal); no need to supply [2]K explicitly.

## Evidence
- Server: `submit_flag.py three_isogenies [flag — recorded in FLAGS/isogenies/challenge-208-cryptohack-three_isogenies/flag.txt]` → `{"score_delta": 35, ...}`.
- PARI: codomain coeffs + j; Python: independent j from same coeffs.

## Vulnerability (plain words)

Not an exploit — a Vélu-formula exercise. Given E: y² = x³ + x mod p
(p = 2^18·3^13 − 1) and a point K of order 3, compute j(E/⟨K⟩). The quotient by a
fixed cyclic kernel is unique and deterministic; the task is only to build the
3-isogeny codomain and read off its j-invariant.

## How the answer follows

- K ∈ E(F_p) and 3K = O were verified with an independent group-law
  implementation ([2]K = −K), so ⟨K⟩ is a valid rational 3-torsion kernel.
- PARI ellisogeny(E, K) returns the codomain
  y² = x³ + 417919813652x + 36118389888; its j, recomputed independently in Python
  as c4³/Δ with c4 = −48a, Δ = −16(4a³+27b²), equals [flag — recorded in FLAGS/isogenies/challenge-208-cryptohack-three_isogenies/flag.txt] — the accepted
  flag. Two independent methods agreeing was the submission gate.

## Limitations / attempts that failed

- Nothing failed on this run (run log); the speed came from banking the
  two_isogenies lessons first: never trust a memorized Vélu codomain formula — let
  PARI produce the codomain and cross-check j with the closed formula.
- Note (knowledge retrieval, stated plainly): the walk itself was delegated to
  PARI's built-in Vélu rather than re-derived from scratch.

## Sources

- PARI/GP ellisogeny (authoritative codomain).
- Standard Vélu / j-formula textbook math.
- No third-party writeups or solution pages consulted (run log).

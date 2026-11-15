# AAR — csidh_secret_exponents (CryptoHack Isogenies, 60 pts)

Date: 2026-10-15 · Worker: Hermes · Status: SOLVED (+60, verified by server, 7405 → 7465, 159 → 160)

## Result
- Flag `404` (bare integer) → server accepted, score_delta +60.
- Task: from E₀ : y² = x³ + x mod 419, compute the CSIDH isogeny for secret vector
  [2,3,4] over primes [3,5,7] (degree 3²·5³·7⁴ = 2,702,250, i.e. 9 forward ℓ-steps
  [3,3,5,5,5,7,7,7,7]); report the Montgomery coefficient A of the codomain.
- Final codomain: **y² = x³ + 196x + 398** (j = 48, #E = 420).
- 2-torsion roots of the final curve: only v = 410 has 3v²+a a square → A = 3v/√(3v²+a) = **404**.

## Walk (Python engine, step-by-step)
```
step 1: l=3 gen=(178,52)  -> (182, 64)  j=356
step 2: l=3 gen=(199,366) -> (292,243)  j=180
step 3: l=5 gen=(308,238) -> (  0,303)  j=  0
step 4: l=5 gen=( 84,125) -> (133,360)  j=356
step 5: l=5 gen=( 27,111) -> ( 85,223)  j=396
step 6: l=7 gen=(233,389) -> (394,188)  j=396
step 7: l=7 gen=(112,106) -> (374,311)  j=407
step 8: l=7 gen=( 84,408) -> (335, 86)  j=356
step 9: l=7 gen=(186,186) -> (196,398)  j= 48   <- final
```

## Method
`velu_engine.py` (in this folder) — fully self-contained Python, no PARI, no external libs:
1. **Vélu x-map point-by-point**: x(φ(R)) = x(R) + Σ_{Q∈K\{O}} [x(R+Q) − x(Q)].
2. **Codomain reconstruction**: image x-coordinates + quotient (coset) group structure;
   three non-collinear image cosets give F_T(a′,b′) = A a′² + B a′ − 4b′ + C = 0;
   two such triples pin (a′,b′); candidates filtered by (all triples) + (every image x-value
   gives square RHS) + uniqueness (ambiguity → hard error).
3. **Per-step checks**: kernel invariance of the x-map (x(φ(R+Q)) = x(φ(R)) ∀Q∈K).
4. **Montgomery conversion**: shift x = X + v (2-torsion root), scale X = wX′ with
   w² = 3v²+a, A = 3v/w with w = principal √(3v²+a) (challenge convention — see below).

## Verification (four independent layers)
1. **challenge-206 ground truth** (server-verified earlier): 5-isogeny from E₀ with kernel
   ⟨(185,73)⟩ → engine gives codomain (269, 82) → A = 199 (the accepted 206 flag). ✓
2. **challenge-210 prime_power AAR** (server-verified, itself 2-implementation cross-checked):
   - 5-walk [5]×9: engine j-sequence [52,13,98,62,407,407,62,98,13,52] and endpoint model
     (321, 0) — EXACT match (model-level, not just j-level).
   - 7-walk [7]×27: endpoint model (215, 0), palindromic j-sequence with j(12)=407,
     j(13)=j(14)=396, j(15)=407 — EXACT match.
3. **PARI `ellisogeny` chain**: full independent 9-step chain (gp64, `chain9.gp` in scratch)
   with the same kernel generators: codomain (a4,a6) identical at EVERY step,
   final (196, 398), j = 48. ✓
4. **Montgomery A = 404**: explicit isomorphism maps all 419 affine points of the final
   curve onto y² = X³ + 404X² + X; j-consistency j_short(196,398) = 48 = j_mont(404)
   (j_mont = 256(A²−3)³/(A²−4)); unique valid 2-torsion root → no A/−A ambiguity.

## What went wrong (and lessons)
- **The "#E′ must be #E/5 = 84" red herring**: the challenge-convention codomain of the
  5-isogeny from E₀ is (269,82) with #E′ = 420 (verified three independent ways), NOT an
  84-point curve. The Vélu x-map image lives on (269,82) as an 84-point subgroup of its
  F_419 group; the challenge's answer key uses (269,82) (server-verified via A=199).
  Do not "fix" a Vélu codomain to satisfy the naive #E′ = #E/deg F_p-point-count expectation.
- **PARI `ellisogeny` point maps are BROKEN** (this gp64 build): the returned map sends
  420 domain points to only 413 distinct images (not a homomorphism) and the "codomain"
  object's point list is unreliable. BUT its **codomain coefficients (ph[1]) are correct**
  — they matched the challenge answer key (269,82) and the Python engine at every one of
  the 9 chain steps. Use PARI for codomain coefficients, never for its point map.
  (The special_isogenies AAR's "trust PARI's map + point-count" lesson is superseded:
  trust only the codomain coefficients.)
- **A vs −A in the Montgomery family**: for p ≡ 3 (mod 4), y²=X³+AX²+X and
  y²=X³−AX²+X are the SAME F_p-isomorphism class (X→−X isomorphism), because −1 is a
  nonsquare and the twist-by-−1 curve is not in the normalized family. So A and −A are
  NOT a twist pair here; "twist disambiguation" between them is meaningless at the
  isomorphism-class level. The challenge's convention for the flag is the **principal-root**
  value: A = 3v/√(3v²+a) with the principal square root (reproduces the accepted 206 flag 199).
- **j_mont formula bug in scratch helper** `isogeny_answers.py`: it used
  j = −256(A²−3)³/(A⁴+4), which is WRONG (only accidentally correct at A=0).
  Correct: **j(y²=X³+AX²+X) = 256(A²−3)³/(A²−4)** (verified: A=199 → 13 = j((269,82));
  A=404 → 48 = j((196,398))).
- **PARI parser friction (again)**: `my(x) = …` inside a for-body → "variable name
  expected"; declare all vars in the function's opening `my(…)` list; single-line for
  bodies; `ellj(ellinit(ph[1]))` fails on the raw ph[1] t_VEC — assign `E2 = ellinit(ph[1])`
  first, then use `E2[13]`.

## Evidence
- `walk.log`: full 9-step walk + final curve + A=404 with 419/419 point-mapping verification.
- `crosscheck.log`: 5-walk and 7-walk model-level exact matches vs prime_power AAR.
- PARI `chain9.gp` output: identical (a4,a6,j) at all 9 steps, final (196,398) j=48.
- Server: `submit_flag.py csidh_secret_exponents 404` →
  `{"ok": true, "score_delta": 60, "before": {"score": 7405, "solved": 159},
     "after": {"score": 7465, "solved": 160}}`.

## Open items (isogeny section, lowest-points-first)
- comp_isogenies (60): composite-degree isogeny by chaining ℓ-steps — velu_engine.csidh_walk
  is exactly this; statement: kernel generator scaled so its multiples cover the composite
  kernel; expect an answer-type flag (j or A).
- whats_my_kernel (70): SIDH public key → recover the kernel (source.sage + output.txt).
- twisted / five_iso_csidh_twist (70): quadratic-twist step "backwards" on the ℓ-isogeny
  graph; needs twist E^t and dual isogeny (or the twist walk trick from prime_power AAR).

## Vulnerability (plain words)

Not a break — an execution exercise in the CSIDH class-group action. Given
E₀: y² = x³ + x mod 419 and the secret exponent vector [2,3,4] over
ℓ in [3,5,7], walk 9 Vélu steps (two 3-steps, three 5-steps, four 7-steps) and
report the Montgomery coefficient A of the resulting curve. The flag therefore
depends both on doing the action correctly and on the challenge's isomorphism
convention (which square root is "principal").

## How the answer follows

- Positive exponents mean repeated Vélu quotients by the pointwise rational
  torsion kernel E(F_p)[ℓ] (cyclic since ℓ² does not divide p+1 = 420); the action
  is abelian, so composing same-ℓ steps in any order is the same.
- A self-contained engine (point-wise Vélu x-map + coset-constraint codomain
  reconstruction, ambiguity → hard error) walks to (a,b) = (196,398), j = 48.
- Montgomery form: shift x = X + v at the unique 2-torsion root v = 410 for which
  3v²+a is a square, then scale X to kill the quadratic term:
  A = 3v/sqrt(3v²+a) with the principal sqrt → A = 404. The A vs −A "ambiguity" is
  not real here (p ≡ 3 mod 4: X ↦ −X is an F_p-isomorphism, same class); the
  convention is what the grader pins, and it reproduces the accepted 206 flag.
- Four independent verifications (206 ground truth; 210's 5-walk and 7-walk model
  match; PARI chain9 identical at every step; 419/419-point isomorphism check),
  plus server-accepted flag 404.

## Limitations / attempts that failed

- The "#E-prime = #E/ℓ" naive F_p point-count expectation is a red herring that
  nearly caused "fixing" a correct Vélu codomain (image = 84-point subgroup of a
  420-point curve).
- This PARI build's ellisogeny point map is broken (non-homomorphic); only its
  codomain coefficients are trustworthy — supersedes an earlier corpus lesson.
- Scratch helper used a wrong j_mont formula; corrected to
  256(A²−3)³/(A²−4).
- PARI parser friction (my() inside for-bodies, ellj on raw ph[1], etc.).

## Sources

- PARI/GP ellisogeny — independent chain, codomain coefficients only.
- In-house ground truth: server-verified challenges 206 (special_isogenies) and
  210 (prime_power) from this same corpus.
- Standard Vélu / Montgomery-conversion math; no third-party writeups or solution
  pages consulted (run log).

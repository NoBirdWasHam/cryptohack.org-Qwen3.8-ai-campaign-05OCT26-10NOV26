# AAR — comp_isogenies (CryptoHack Isogenies, 60 pts)

## Result
**SOLVED 2026-10-15.** Flag `[flag — recorded in FLAGS/isogenies/challenge-9-cryptohack-comp_isogenies/flag.txt]` accepted, score_delta +60 (7605 → 7665; 162 → 163 solved).

## Attack
13-step Vélu isogeny chain over F_{p²} = F_p[i] (p = 417942208511 = 2^18·3^13 − 1), pure Python, no PARI/Sage/fpylll:
1. Verify K ∈ E(F_{p²}), 3^13·K = O (K order 3^13).
2. Q_0 = [3^12]K (order 3); φ_0 = Vélu 3-isogeny with kernel {O, Q_0, −Q_0}.
3. Iterate: K_{k+1} = φ_k(K_k), Q_{k+1} = [3^{11−k}]K_{k+1} (order 3), φ_{k+1} = Vélu 3-isogeny. 13 steps total.
4. j(E_13) from final (a, b) coefficients = 292990704480 + 249510360818·i.

## Verification (verify_comp.py, all passed — see verify.log)
- **V1 kernel-kill**: total map sends K to O; first codomain = F_p-twist of the PARI-verified three_isogenies codomain (same j = [flag — recorded in FLAGS/isogenies/challenge-8-cryptohack-three_isogenies/flag.txt]) — engine anchored to a server-verified value.
- **V2 Frobenius**: j with conjugate kernel = conjugate of j (exact).
- **V3 homomorphism**: total(P+R) = total(P)+total(R) for random P, R ∈ E_0(F_{p²}); all images on E_13.
- Submission confirmed by API (score_delta 60).

## Bugs found & fixed (chronological)
1. **EC doubling used the addition formula** (x3 = λ² − x1 + x2 instead of λ² − 2x1) → 2P off-curve. Fixed in comp_iso.py; caught by on-curve assertion.
2. **`x^((q+1)/4)` sqrt in F_{p²} is invalid** (needs q ≡ 3 mod 4; q = p² ≡ 1 mod 4 always) → infinite loop in random-point sampling. Replaced with proper Tonelli–Shanks (f2_sqrt in comp_iso.py), numerically verified on 200 random elements (98 roots / 102 non-residues, all roots squared back correctly).
3. **TS non-residue search over F_p can never terminate** (z^(p−1) = 1 ⇒ z^((q−1)/2) = 1 for all z ∈ F_p) → must search in F_{p²} (start with i).

## Flag format (7 attempts)
Grader expects Sage `GF(p^2, 'i')` str: **`<imag>*i + <real>`**. Order tried: `249510360818i + 292990704480` ✗, `292990704480+249510360818i` ✗, `292990704480 249510360818` ✗, `292990704480, 249510360818` ✗, `292990704480 + 249510360818i` ✗, `[flag — recorded in FLAGS/isogenies/challenge-9-cryptohack-comp_isogenies/flag.txt]` ✓ (+60), `292990704480 + 249510360818*i` ✗ (already solved).

## Lessons
- For F_{p²}-valued CryptoHack answers, the Sage field-element string (highest-degree term first, explicit `*`) is the serialization.
- Vélu odd-degree isogenies over extension fields work with the same formulas — only the field arithmetic changes; the kernel-kill + Frobenius-symmetry + homomorphism triple is a cheap, strong end-to-end verification when no external engine (PARI) covers F_{p²}.
- When a challenge's statement omits the "flag is …" line, the track convention (j-invariant) still held; the ambiguity was purely serialization.

## Evidence
comp_iso.py, verify_comp.py, verify.log, crosscheck.log, flag.txt, site.md.

## Vulnerability (plain words)

No live-system attack — the lesson is that a cyclic isogeny of composite degree
3^13 need not be computed at once: isogeny theory factors a cyclic kernel into a
chain of prime-degree steps, and the challenge is executing that 13-step chain
over F_{p²} (p = 417942208511 = 2^18·3^13 − 1) and reporting j of the far curve.

## How the answer follows

- ker phi = ⟨K⟩, ord K = 3^13. Set Q0 = [3^12]K (order 3) and quotient; the image
  K1 = phi0(K) still has order 3^12, so repeat: step k quotients by
  ⟨[3^{11−k}]K_k⟩. After 13 Vélu 3-steps the composition kills exactly ⟨K⟩, and
  j(E_13) read from the final (a,b) = 292990704480 + 249510360818·i is the answer.
- Verification replaces an external engine: the total map kills K; the conjugate
  kernel gives the conjugate j (Frobenius symmetry); homomorphism spot-tests on
  E0(F_{p²}); and the first codomain is the F_p-twist of the server-verified
  three_isogenies codomain (same j = [flag — recorded in FLAGS/isogenies/challenge-8-cryptohack-three_isogenies/flag.txt]) — an anchor to ground truth.
- Flag serialization = Sage GF(p²) string form, imag-term-first with explicit
  star: `[flag — recorded in FLAGS/isogenies/challenge-9-cryptohack-comp_isogenies/flag.txt]`.

## Limitations / attempts that failed

- EC doubling used the addition formula (off-curve 2P; caught by on-curve
  assertion).
- The x^((q+1)/4) square root is invalid for q = p² (q ≡ 1 mod 4) → infinite
  loop; replaced by Tonelli–Shanks in F_{p²}.
- Tonelli–Shanks non-residue search over F_p can never terminate (every element
  of F_p is a square in F_{p²}); must search elements of genuinely non-residue
  norm.
- 6 of 7 flag submissions failed on serialization only — the value never changed.

## Sources

- Standard Vélu / cyclic-kernel factorization math; PARI not usable for the
  F_{p²} checks, hence the three-way internal verification.
- No third-party writeups or solution pages consulted (run log).

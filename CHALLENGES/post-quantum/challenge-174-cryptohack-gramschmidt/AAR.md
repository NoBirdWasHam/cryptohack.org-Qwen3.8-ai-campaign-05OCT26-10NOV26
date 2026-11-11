# AAR — Gram Schmidt (challenge-174-cryptohack-gramschmidt)

## 1. Result
**SOLVED** — answer `0.91611` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on 2026-10-12 and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/post-quantum/gramschmidt/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `0.91611`
Answer-type (BARE float, 5 sig figs). Apply Gram-Schmidt to the given basis; report the 2nd component of u4.
- Ran Gram-Schmidt in Python; u4[1] = 0.91611 (5 significant figures). BARE float accepted.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).


## Vulnerability (plain words)
None — implement-the-algorithm drill. The track needs you to own Gram-Schmidt (the orthogonalization that underlies lattice reduction) before reduction shows up, so it asks for one specific output component of your own implementation.

## How the answer follows
Apply the algorithm exactly as quoted in the statement: u₁ = v₁; for i = 2..n, μ_ij = (v_i·u_j)/‖u_j‖² and u_i = v_i − Σ_j μ_ij·u_j — **without normalizing** (the statement warns that library implementations often orthonormalize, which shrinks each u_i to unit length and gives the wrong component values).
With v₁=(4,1,3,−1), v₂=(2,1,−3,4), v₃=(1,0,−2,7), v₄=(6,2,9,−5), exact rational arithmetic gives for the last step the coefficients μ₄₁ = 58/27, μ₄₂ = −659/794, μ₄₃ = 439/4023, and
u₄ = (−1456/4023, **273/298**, 1729/8046, 455/4023).
The requested second component is 273/298 = 0.9161073… → 5 significant figures = **0.91611** (rounding, not truncation, at the 5th significant digit — the statement flags this as a trap). Submitted BARE, accepted 2026-10-12; live-confirmed 2026-10-13.

## Limitations / attempts that failed
- The original solve was "ran Gram-Schmidt in Python" (run log); the script itself was not archived. The exact fractions above were re-derived with rational arithmetic during the 2026-11-01 remediation pass as a comprehension check and reproduce the already-accepted value; the original script's intermediate values are not recorded.
- No failed submission recorded beyond the generic format warnings the statement anticipates (orthonormalized output / wrong rounding).

## Sources
- Statement (site.md) which itself quotes the Gram-Schmidt algorithm from Hoffstein–Pipher–Silverman, *An Introduction to Mathematical Cryptography* — that is the only reference involved. No writeups consulted.

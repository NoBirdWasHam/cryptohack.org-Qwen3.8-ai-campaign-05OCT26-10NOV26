# AAR — Montgomery Curves (challenge-205-cryptohack-b_compute_montgomery)

## 1. Result
**SOLVED** — answer `[flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt]` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on None and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/isogenies/b_compute_montgomery/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `[flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt]`
Answer-type (BARE). E: y^2=x^3+ax+b (a=312589632, b=654443578, p=1912812599); find A of the isomorphic Montgomery curve y^2=x^3+Ax^2+x.
- j(E) = 915617603 (invariant-based). Montgomery j(A) = -64(A^2-3)^3 (derived from b2=4A, b4=2, b6=1, b8=0; sanity A=0 -> 1728 OK).
- Solve (A^2-3)^3 = -j/64: cube root w=1060294165 (PARI polrootsmod(Pol([1,0,0,-w_target],x),p)), t=A^2=3+w, A=+/-sqrt(t).
- Two valid roots (A and -A share the same j): **[flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt]** and 1385156202, both verified j_mont(A)==j(E). Submitted 2026-10-12 (accepted); progress.json did not record the flag — primary value recorded here.
- NOTE: the earlier `isogeny_answers.py` used a WRONG j_mont sign convention AND fed polrootsmod a coefficient list instead of a Pol (PARI error 'incorrect type in factormod (t_VEC)'). Both fixed 2026-10-13.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).
## Vulnerability (plain words)
No vulnerability — an answer-type isomorphism exercise: j classifies elliptic curves up to isomorphism (over the algebraic closure; up to quadratic twist over F_p), and the Montgomery model's j is an explicit rational function of A alone. So "find A such that y^2 = x^3 + Ax^2 + x is isomorphic to the given (a,b) curve" collapses to solving one polynomial equation in A — no basis change must be exhibited.

## How the answer follows
1. Compute j(E) from the invariants: with a=312589632, b=654443578, p=1912812599, j(E) = c4^3/Delta = 915617603 (re-verified mod p at AAR-upgrade time 2026-11-01; harness sanity j(x^3+x)=1728).
2. The challenge's Montgomery model has j_mont(A) = -64(A^2-3)^3 (derived from b2=4A, b4=2, b6=1, b8=0 of its generalized-Weierstrass form — the a3^2 term is what makes b4=2; sanity A=0 -> 1728). Setting j_mont(A) = j(E) gives (A^2-3)^3 = -j/64.
3. Extract a cube root w = 1060294165 of -j/64 (PARI `polrootsmod(Pol([1,0,0,-target],x),p)` — all roots, not just one), set A^2 = 3 + w, take modular square roots -> A in {[flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt], 1385156202}. j_mont depends only on A^2, so both signs are valid (they form the quadratic-twist pair); both pass the end-check j_mont(A) == j(E) (re-confirmed for both at AAR-upgrade time). Submitted [flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt]; accepted bare.

## Limitations / attempts that failed
- First harness pass had two real bugs, both recorded: a WRONG j_mont sign convention, and feeding `polrootsmod` a coefficient list instead of a `Pol` (PARI 'incorrect type in factormod (t_VEC)'). Fixed 2026-10-13; accepted answer comes from the corrected harness.
- First submission used the wrapped format and was rejected (bare required).
- progress.json did not record this answer — the value is recorded here and live-confirmed via the user API only.

## Sources
Own harness `../isogeny_answers.py`; PARI/GP manual (`polrootsmod`); textbook j-invariant / Montgomery-model identities (Silverman/HPS standard material). Statement cached in `challenge_meta.json`. No solutions/writeups consulted.

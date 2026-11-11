# AAR — What's a Lattice? (challenge-176-cryptohack-lattices)

## 1. Result
**SOLVED** — answer `255` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on None and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/post-quantum/lattices/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `255`
Answer-type (BARE). Basis matrix M=[[6,2,-3],[5,1,4],[2,7,1]]; lattice index = |det M|.
- |det| = 255 (computed in `isogeny_answers.py`: abs(int(round(np.linalg.det(M))))). BARE integer accepted.
- (Flag not recorded in progress.json at solve time; value recomputed 2026-10-13, consistent with live solved status.)

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).


## Vulnerability (plain words)
None — definition computation at the point where lattices are first introduced: the volume of a lattice's fundamental domain equals the absolute determinant of any basis matrix.

## How the answer follows
The statement's 2-D example (basis rows (2,5),(3,1) → |det| = 13) establishes the rule vol(F) = |det M|; the instance gives rows v₁=(6,2,−3), v₂=(5,1,4), v₃=(2,7,1). Cofactor expansion of M = [[6,2,−3],[5,1,4],[2,7,1]] along row 1:
6·(1·1 − 4·7) − 2·(5·1 − 4·2) + (−3)·(5·7 − 1·2) = 6·(−27) − 2·(−3) − 3·(33) = −162 + 6 − 99 = **−255** → volume = |−255| = **255**.
Why the determinant *is* the volume: the fundamental domain is the parallelotope spanned by the basis vectors, and |det| is exactly the (signed) volume-scaling factor of that spanning map; changing basis applies a unimodular transformation, whose det is ±1, so |det| is a lattice invariant — every valid basis answers 255.

## Limitations / attempts that failed
- The original solve used floating-point numpy (abs(round(np.linalg.det(M)))) — fine at this size, but the exact integer expansion above (2026-11-01 remediation pass) is the grounding proof; both give 255.
- As already recorded in §3: the answer was not logged in progress.json at solve time; value re-derived 2026-10-13 consistent with the live solved status. Nothing else failed / recorded.

## Sources
- Statement (site.md), including its worked 2-D example that supplies the method. No writeups consulted.

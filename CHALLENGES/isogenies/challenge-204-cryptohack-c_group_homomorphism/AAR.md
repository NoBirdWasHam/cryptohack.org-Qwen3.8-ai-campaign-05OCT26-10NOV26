# AAR — Image Point Arithmetic (challenge-204-cryptohack-c_group_homomorphism)

## 1. Result
**SOLVED** — answer `43636` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on None and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/isogenies/c_group_homomorphism/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `43636`
Answer-type (BARE). Isogeny preserves group structure: P=(48622,27709), Q=(9460,13819) on y^2=x^3+ax+b (p=63079); find x(P+Q).
- Recovered a=56540, b=43233 from the two points (both on-curve), then EC addition: lam=(y2-y1)/(x2-x1), x3=lam^2-a-x1-x2 = **43636** (in `isogeny_answers.py`). BARE integer accepted.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).
## Vulnerability (plain words)
No vulnerability — an answer-type group-law exercise. The challenge's headline is that an isogeny is a group homomorphism (phi(P) + phi(Q) = phi(P+Q)), so x(P+Q) can be computed on the *source* curve without ever computing phi; the mild twist is that the curve parameters a, b are not given and must be recovered from two points that lie on the curve.

## How the answer follows
1. Each given point contributes b = y^2 - x^3 - a*x (mod p); with both P=(48622,27709) and Q=(9460,13819) on y^2 = x^3 + ax + b over p=63079, subtracting the two equations cancels b and solves a linearly: **a = 56540**, hence **b = 43233** (re-verified by substitution at AAR-upgrade time 2026-11-01).
2. Chord-and-tangent: lam = (y2-y1)/(x2-x1) mod p, x3 = lam^2 - a - x1 - x2 = **43636**. Because isogenies preserve the group law, this x(P+Q) is the requested image-side sum's coordinate regardless of the (never-computed) isogeny — the homomorphism property does the commuting for free.
3. Bare integer 43636 accepted 2026-10-12; live-confirmed in the user API. (Re-derived x3 = 43636 during the AAR upgrade — consistent.)

## Limitations / attempts that failed
- First submission used the wrapped flag format and was rejected (bare required). Nothing else recorded in run logs.

## Sources
Own harness `../isogeny_answers.py`; standard EC addition formulas (Silverman/HPS textbook material). Statement cached in `challenge_meta.json`. No solutions/writeups consulted.

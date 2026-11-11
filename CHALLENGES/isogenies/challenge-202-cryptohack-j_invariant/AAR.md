# AAR — The j-invariant (challenge-202-cryptohack-j_invariant)

## 1. Result
**SOLVED** — answer `127` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on None and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/isogenies/j_invariant/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `127`
Answer-type (BARE). y^2=x^3+145x+49 mod 163; compute the j-invariant.
- Invariant-based: c4=-24(2a), D=-8(2a)^3-27(4b)^2, j=c4^3/D mod p -> **127** (sanity j(x^3+x)=1728 verified in `isogeny_answers.py`).
- BARE integer accepted 2026-10-12 (flag not recorded in progress.json; recomputed 2026-10-13, consistent with live status).

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).
## Vulnerability (plain words)
No vulnerability — this is an answer-type computation exercise: evaluate the j-invariant of E: y^2 = x^3 + 145x + 49 over F_163. The whole point of the invariant is that it is computable from the *coefficients alone* — no point arithmetic, no isogeny walk.

## How the answer follows
For short Weierstrass, j = c4^3 / Delta with c4 = -48a and Delta = -16(4a^3 + 27b^2) — equivalently the b-invariant route b4=2a, b6=4b, b8=-a^2b used in the run. Mod 163 with a=145, b=49: c4 = -48*145 = 49, c4^3 = 126, Delta = -16(4*145^3 + 27*49^2) = 78, 78^-1 = 23, so j = 126*23 = **127** (mod 163). (Independently re-checked at AAR-upgrade time 2026-11-01 — reproduces 127.) Sanity harness: the same code returns j(x^3+x) = 1728. Answer-type challenges accept the BARE integer (no crypto{...} wrapper): 127 submitted 2026-10-12, live-confirmed in the user API.

## Limitations / attempts that failed
- First submission used the wrapped flag format and was rejected — bare values are what answer-type challenges require.
- PARI friction (shared harness): `polrootsmod` rejects a bare coefficient list (t_VEC type error); it needs `Pol([...], x)`.

## Sources
Own harness `../isogeny_answers.py` (shared j-invariant code, sanity j(x^3+x)=1728); standard Weierstrass invariant identities (Silverman / HPS textbook material). Statement cached in `challenge_meta.json`. No solutions/writeups consulted.

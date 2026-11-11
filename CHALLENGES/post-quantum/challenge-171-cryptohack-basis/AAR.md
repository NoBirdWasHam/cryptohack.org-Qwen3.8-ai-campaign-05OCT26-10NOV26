# AAR — Size and Basis (challenge-171-cryptohack-basis)

## 1. Result
**SOLVED** — answer `9` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on 2026-10-12 and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/post-quantum/basis/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `9`
Answer-type (BARE number). Given the basis vectors, the lattice size / norm quantity is **9**.
- Computed directly from the statement's vectors; BARE integer accepted.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).


## Vulnerability (plain words)
None — definitions drill (linear independence, basis, orthogonal/orthonormal). The flag question tests one definition: the size (Euclidean norm) of a vector defined as ‖v‖² = v·v.

## How the answer follows
The archived statement gives v = (4, 6, 2, 5) and asks for its size. Applying the statement's own definition:
‖v‖² = 4² + 6² + 2² + 5² = 16 + 36 + 4 + 25 = 81, so ‖v‖ = √81 = **9**.
The number is exact (an integer norm — the instance was chosen so the sqrt lands cleanly), so no rounding ambiguity in the BARE answer. `9` accepted 2026-10-12; live-confirmed 2026-10-13.

## Limitations / attempts that failed
- Single-step computation from the statement's definition; nothing failed and no other attempts recorded in run logs. No script archived for this item.

## Sources
- Statement from challenge_meta.json, quoted in full in site.md. No external reference; no writeups consulted.

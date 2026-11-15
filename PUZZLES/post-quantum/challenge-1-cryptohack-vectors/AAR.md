# AAR — Vectors (challenge-169-cryptohack-vectors)

## 1. Result
**SOLVED** — answer `702` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on 2026-10-12 and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/post-quantum/vectors/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `702`
Answer-type (BARE). Vector-distance revision challenge: compute the distance between the two given points.
- Computed directly; BARE integer accepted. Part of the Lattice intro block (post-quantum), solved 2026-10-12.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).


## Vulnerability (plain words)
None — linear-algebra revision drill at the head of the lattice track. Purpose: make sure you can do scalar multiplication and inner products before lattices are defined in terms of them.

## How the answer follows
The archived statement (site.md) fixes v = (2,6,3), w = (1,0,0), u = (7,7,2) and asks for 3·(2v − w) · 2u (scalar multiples, then the dot product):
1. 2v − w = (4−1, 12−0, 6−0) = (3, 12, 6)
2. 3·(2v − w) = (9, 36, 18);  2u = (14, 14, 4)
3. Dot product = 9·14 + 36·14 + 18·4 = 126 + 504 + 72 = **702**
Each step follows directly from the definitions the statement itself lays out (componentwise addition, scalar multiplication, inner product as the sum of coordinate products). `702` submitted BARE, accepted 2026-10-12; live-confirmed in the user API 2026-10-13.

## Limitations / attempts that failed
- Single-step computation; nothing failed and no other attempts are recorded in run logs. The exact one-liner used at solve time was not archived (no script kept; arithmetic above re-verified from the archived statement during the 2026-11-01 remediation pass).

## Sources
- Statement from challenge_meta.json, quoted in full in site.md. No external reference needed; no writeups consulted.

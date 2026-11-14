---
record: agent-aar
puzzle: challenge-202-cryptohack-j_invariant
category: isogenies
url: https://cryptohack.org/challenges/j_invariant/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/isogenies/challenge-202-cryptohack-j_invariant/flag.txt"
flag_sha256: 743c7850cccfba5e53a9002663ec1ddd1079315a98bdbfdde10e6044f56abefe
skills: []
human_twin: AAR.md
---

# AGENT — The j-invariant (challenge-202-cryptohack-j_invariant)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
No vulnerability — this is an answer-type computation exercise: evaluate the j-invariant of E: y^2 = x^3 + 145x + 49 over F_163. The whole point of the invariant is that it is computable from the *coefficients alone* — no point arithmetic, no isogeny walk.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- First submission used the wrapped flag format and was rejected — bare values are what answer-type challenges require.
- PARI friction (shared harness): `polrootsmod` rejects a bare coefficient list (t_VEC type error); it needs `Pol([...], x)`.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/isogenies/j_invariant/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

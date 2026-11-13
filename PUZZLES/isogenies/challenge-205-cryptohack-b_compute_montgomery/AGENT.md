---
record: agent-aar
puzzle: challenge-205-cryptohack-b_compute_montgomery
category: isogenies
url: https://cryptohack.org/challenges/b_compute_montgomery/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt"
flag_sha256: 4b502dbd2a63a8113c7d71cfce154b230bde76215d06898a9c081ad5cfafe90f
skills: []
human_twin: AAR.md
---

# AGENT — Montgomery Curves (challenge-205-cryptohack-b_compute_montgomery)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
No vulnerability — an answer-type isomorphism exercise: j classifies elliptic curves up to isomorphism (over the algebraic closure; up to quadratic twist over F_p), and the Montgomery model's j is an explicit rational function of A alone. So "find A such that y^2 = x^3 + Ax^2 + x is isomorphic to the given (a,b) curve" collapses to solving one polynomial equation in A — no basis change must be exhibited.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- First harness pass had two real bugs, both recorded: a WRONG j_mont sign convention, and feeding `polrootsmod` a coefficient list instead of a `Pol` (PARI 'incorrect type in factormod (t_VEC)'). Fixed 2026-10-13; accepted answer comes from the corrected harness.
- First submission used the wrapped format and was rejected (bare required).
- progress.json did not record this answer — the value is recorded here and live-confirmed via the user API only.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/isogenies/b_compute_montgomery/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

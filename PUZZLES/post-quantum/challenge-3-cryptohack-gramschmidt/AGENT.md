---
record: agent-aar
puzzle: challenge-3-cryptohack-gramschmidt
category: post-quantum
url: https://cryptohack.org/challenges/gramschmidt/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/post-quantum/challenge-3-cryptohack-gramschmidt/flag.txt"
flag_sha256: 76570843244293eb2eed2e70a8624509a32780e4afd16cf9b288c159f30b2a98
skills: []
human_twin: AAR.md
---

# AGENT — Gram Schmidt (challenge-174-cryptohack-gramschmidt)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
None — implement-the-algorithm drill. The track needs you to own Gram-Schmidt (the orthogonalization that underlies lattice reduction) before reduction shows up, so it asks for one specific output component of your own implementation.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- The original solve was "ran Gram-Schmidt in Python" (run log); the script itself was not archived. The exact fractions above were re-derived with rational arithmetic during the 2026-11-01 remediation pass as a comprehension check and reproduce the already-accepted value; the original script's intermediate values are not recorded.
- No failed submission recorded beyond the generic format warnings the statement anticipates (orthonormalized output / wrong rounding).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/post-quantum/gramschmidt/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

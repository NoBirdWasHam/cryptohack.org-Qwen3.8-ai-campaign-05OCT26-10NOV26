---
record: agent-aar
puzzle: challenge-204-cryptohack-c_group_homomorphism
category: isogenies
url: https://cryptohack.org/challenges/c_group_homomorphism/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/isogenies/challenge-204-cryptohack-c_group_homomorphism/flag.txt"
flag_sha256: 6f6648e4041ee6d50f7ba929445edf3aa7e4441debb4d0a3d04523e2d2578af5
skills: []
human_twin: AAR.md
---

# AGENT — Image Point Arithmetic (challenge-204-cryptohack-c_group_homomorphism)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
No vulnerability — an answer-type group-law exercise. The challenge's headline is that an isogeny is a group homomorphism (phi(P) + phi(Q) = phi(P+Q)), so x(P+Q) can be computed on the *source* curve without ever computing phi; the mild twist is that the curve parameters a, b are not given and must be recovered from two points that lie on the curve.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- First submission used the wrapped flag format and was rejected (bare required). Nothing else recorded in run logs.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/isogenies/c_group_homomorphism/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

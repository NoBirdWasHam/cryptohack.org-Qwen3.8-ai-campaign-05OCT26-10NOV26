---
record: agent-aar
puzzle: challenge-171-cryptohack-basis
category: post-quantum
url: https://cryptohack.org/challenges/basis/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/post-quantum/challenge-2-cryptohack-basis/flag.txt (absent — honest null; see note in FLAGS/INDEX.jsonl)"
flag_sha256: null — flag withheld (note in FLAGS/INDEX.jsonl)
skills: []
human_twin: AAR.md
---

# AGENT — Size and Basis (challenge-171-cryptohack-basis)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
None — definitions drill (linear independence, basis, orthogonal/orthonormal). The flag question tests one definition: the size (Euclidean norm) of a vector defined as ‖v‖² = v·v.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- Single-step computation from the statement's definition; nothing failed and no other attempts recorded in run logs. No script archived for this item.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/post-quantum/basis/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

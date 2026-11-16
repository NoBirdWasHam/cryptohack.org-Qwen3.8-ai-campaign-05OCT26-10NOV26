---
record: agent-aar
puzzle: challenge-1-cryptohack-vectors
category: post-quantum
url: https://cryptohack.org/challenges/vectors/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/post-quantum/challenge-1-cryptohack-vectors/flag.txt"
flag_sha256: 73445aa688fddf09cf8b39ab9ddfc5b006c62e19403dd96825ad2deed8c4a76c
skills: []
human_twin: AAR.md
---

# AGENT — Vectors (challenge-169-cryptohack-vectors)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
None — linear-algebra revision drill at the head of the lattice track. Purpose: make sure you can do scalar multiplication and inner products before lattices are defined in terms of them.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- Single-step computation; nothing failed and no other attempts are recorded in run logs. The exact one-liner used at solve time was not archived (no script kept; arithmetic above re-verified from the archived statement during the 2026-11-01 remediation pass).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/post-quantum/vectors/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

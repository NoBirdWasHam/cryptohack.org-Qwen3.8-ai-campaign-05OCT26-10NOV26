---
record: agent-aar
puzzle: challenge-176-cryptohack-lattices
category: post-quantum
url: https://cryptohack.org/challenges/lattices/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/challenge-176-cryptohack-lattices/challenge-176-cryptohack-lattices/flag.txt"
flag_sha256: ce8bafb38615aeb5d44ebbabe78ec14ac35a5de87bdc5ad5ea82a72656024ce4
skills: []
human_twin: AAR.md
---

# AGENT — What's a Lattice? (challenge-176-cryptohack-lattices)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
None — definition computation at the point where lattices are first introduced: the volume of a lattice's fundamental domain equals the absolute determinant of any basis matrix.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- The original solve used floating-point numpy (abs(round(np.linalg.det(M)))) — fine at this size, but the exact integer expansion above (2026-11-01 remediation pass) is the grounding proof; both give 255.
- As already recorded in §3: the answer was not logged in progress.json at solve time; value re-derived 2026-10-13 consistent with the live solved status. Nothing else failed / recorded.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/post-quantum/lattices/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

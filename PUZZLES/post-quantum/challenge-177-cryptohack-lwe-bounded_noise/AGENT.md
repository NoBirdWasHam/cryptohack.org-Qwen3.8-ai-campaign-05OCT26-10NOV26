---
record: agent-aar
puzzle: challenge-177-cryptohack-lwe-bounded_noise
category: post-quantum
url: https://cryptohack.org/challenges/lwe-bounded_noise/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-177-cryptohack-lwe-bounded_noise/flag.txt"
flag_sha256: eec28fdbfe9f8750f6a8f3e07729ff10e241c3ee6140f3f1b22f0589845fca5a
skills: []
human_twin: AAR.md
---

# AGENT — Bounded Noise (challenge-177-cryptohack-lwe-bounded_noise)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
CVP lattice `[A^T|0; 0 q]` is WRONG for mod-q LWE (the signal A*s mod q is not a lattice point). Algebraic route instead:
1. Pick 25 pivot rows forming an invertible 25x25 subset; parameterize s = s0 + N*e where e is the 25-dim binary error (e_j in {0,1}) and N spans the error space of the remaining rows.
2. One extra row prunes 2^25 candidates to ~1026 (incremental Gray-code evaluation keeps it fast in pure Python).
3. Full verification of all 625 equations; unique candidate -> flag digits.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Failed attempt kept deliberately: the wrong CVP embedding (step 1) — this is the documented dead end.
- Run logs do not record whether additional pruning rows or BKZ-style fixes were tried beyond the single extra row + exhaustive verification.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Server-provided instance `_pq/bounded_noise_output.txt`; working solver `_pq/solve_bn_enum.py` (+ `_pq/_bn_parsed.json`). Theory background: bounded-noise-LWE is standard (Regev-style learning with errors where e is sparse/binary), but no external writeup was consulted.

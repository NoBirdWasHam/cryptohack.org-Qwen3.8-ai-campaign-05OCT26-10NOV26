---
record: agent-aar
puzzle: challenge-179-cryptohack-lwe-nativity
category: post-quantum
url: https://cryptohack.org/challenges/lwe-nativity/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-15-cryptohack-lwe-nativity/flag.txt"
flag_sha256: 92affc20482993ebfe3e92fa5de1dcaaab3db0d2fca4c728cc2d6e4fc71fa65a
skills: []
human_twin: AAR.md
---

# AGENT — Nativity (challenge-179-cryptohack-lwe-nativity)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Decryption computes `sk*c & 1` (parity) and `sk*c = msg + 2*sum(e_j y_j)` -> **the error vanishes mod 2**. Only `s mod 2` is needed: solve `t = s*A (mod 2)` over GF(2) (512x64 elimination) — no lattice at all; the 64 parity bits + per-ciphertext decryption yield the flag bytes.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Run logs do not record any aborted attempt to work over Z/2¹⁶ directly before switching to GF(2) (nor whether one was made); the GF(2) route is the recorded solve.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Server-provided `_pq/public_key.txt`, `_pq/ciphertexts.txt`; own solver `_pq/solve_nat.py`. No external writeup consulted.

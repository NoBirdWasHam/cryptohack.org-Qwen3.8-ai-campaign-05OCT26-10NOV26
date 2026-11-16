---
record: agent-aar
puzzle: challenge-13-cryptohack-lwe-lsb-regev
category: post-quantum
url: https://cryptohack.org/challenges/lwe-lsb-regev/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-13-cryptohack-lwe-lsb-regev/flag.txt"
flag_sha256: 47b4fceead748df248e192da0d4cb187ebd08c154ce5111ef591a0d8f429335d
skills: []
human_twin: AAR.md
---

# AGENT — Noise Free (challenge-175-cryptohack-lwe-lsb-regev)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
64 zero-encryptions -> 64x64 invertible system over GF(65537) (q prime): Gauss-Jordan recovers S exactly; then each flag char: `m = (b - A*S) mod q` (plaintext is a byte, so the mod-q value IS the byte). All chars verified by re-encryption identity.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Run logs do not record how many zero-encryption requests were exchanged before the system was invertible (first-try vs. retry not recorded), nor the exact request count beyond the 64 used.
- Backfill note already in file: folder created after the fact; scripts live in `_pq/`.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Live server interaction only (a.cryptohack.org socket 13411). Solvers: `_pq/13411.py`, `_pq/solve_13411.py`. No external reference or writeup used.
